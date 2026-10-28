"""
Resume Tailor Pro - Main Flask Application (Multi-Profile & Mobile Ready)

Features:
- Multi-profile management (Kiruthiknivas + friends)
- Resume document ingestion (PDF, DOCX, TXT) with AI auto-parsing
- ATS optimization with Anti-AI detection
- Guaranteed 1-page LaTeX compilation
- iCloud sync for Kiruthiknivas + direct download for all profiles
- Mobile-optimized responsive endpoints
"""
import os
import re
import json
import socket
import logging
import shutil
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, jsonify, send_file, Response

from config import (
    BASE_DIR, OUTPUT_DIR, LATEX_TEMPLATE_DIR, HISTORY_FILE,
    GEMINI_API_KEY, OPENAI_API_KEY,
    OLLAMA_BASE_URL, OLLAMA_MODEL,
    FLASK_HOST, FLASK_PORT, FLASK_DEBUG,
)
from ai_provider import generate_tailored_content
from latex_builder import build_latex_source, compile_latex_to_pdf
import profile_manager

# ============================================================
# SETUP
# ============================================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max upload

UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)
profile_manager.init_profiles()


def get_local_ip() -> str:
    """Detect the local machine IP on Wi-Fi/LAN for mobile sharing."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip


# ============================================================
# ROUTES: MAIN & INFO
# ============================================================
@app.route("/")
def index():
    """Serve the main application interface."""
    local_ip = get_local_ip()
    return render_template("index.html", local_ip=local_ip, port=FLASK_PORT)


@app.route("/network-info")
def network_info():
    """Return network IP for mobile device connections."""
    local_ip = get_local_ip()
    return jsonify({
        "local_ip": local_ip,
        "port": FLASK_PORT,
        "mobile_url": f"http://{local_ip}:{FLASK_PORT}",
    })


@app.route("/api-status")
def api_status():
    """Check configured AI providers."""
    return jsonify({
        "gemini": bool(os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY") or GEMINI_API_KEY),
        "openai": bool(os.environ.get("OPENAI_API_KEY") or OPENAI_API_KEY),
        "ollama": True,
    })


# ============================================================
# ROUTES: PROFILES
# ============================================================
@app.route("/profiles", methods=["GET"])
def get_profiles():
    """Get list of all saved candidate profiles."""
    profiles = profile_manager.list_profiles()
    return jsonify(profiles)


@app.route("/profile/<profile_id>", methods=["GET"])
def get_single_profile(profile_id):
    """Get detailed profile data for a specific candidate."""
    profile = profile_manager.get_profile(profile_id)
    if not profile:
        return jsonify({"success": False, "message": "Profile not found"}), 404
    return jsonify(profile)


@app.route("/profile/upload", methods=["POST"])
def upload_profile_resume():
    """Upload a friend's resume (PDF, DOCX, TXT), parse with AI, and create a profile."""
    try:
        if 'resume_file' not in request.files:
            return jsonify({"success": False, "message": "No file uploaded"}), 400

        file = request.files['resume_file']
        if file.filename == '':
            return jsonify({"success": False, "message": "No file selected"}), 400

        filename = secure_filename(file.filename)
        save_path = os.path.join(UPLOAD_DIR, filename)
        file.save(save_path)

        logger.info("Uploaded resume saved to %s", save_path)

        # 1. Extract text from document
        raw_text = profile_manager.extract_text_from_file(save_path, filename)
        if not raw_text.strip():
            return jsonify({"success": False, "message": "Could not extract text from document. Ensure it is not an image-only scan."}), 400

        # 2. Parse using AI
        user_api_key = request.form.get("api_key", "").strip()
        gemini_key = user_api_key if user_api_key.startswith("AIza") or user_api_key.startswith("AQ.") else (os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY") or GEMINI_API_KEY)
        openai_key = user_api_key if user_api_key.startswith("sk-") else (os.environ.get("OPENAI_API_KEY") or OPENAI_API_KEY)

        logger.info("Parsing resume using AI extractor...")
        parsed_profile = profile_manager.parse_resume_text(
            raw_text=raw_text,
            gemini_key=gemini_key,
            openai_key=openai_key,
        )

        # Override name if user entered a custom name
        custom_name = request.form.get("profile_name", "").strip()
        if custom_name:
            parsed_profile["name"] = custom_name
            parsed_profile["owner"]["name"] = custom_name

        # 3. Save profile
        profile_id = profile_manager.save_profile(parsed_profile)
        logger.info("Successfully created new profile: %s (%s)", profile_id, parsed_profile.get("name"))

        return jsonify({
            "success": True,
            "profile_id": profile_id,
            "name": parsed_profile.get("name"),
            "profile": parsed_profile,
            "message": f"Resume for '{parsed_profile.get('name')}' analyzed and added to profiles!",
        })

    except Exception as e:
        logger.exception("Error during profile upload/parsing")
        return jsonify({"success": False, "message": f"Upload failed: {str(e)}"}), 500


@app.route("/profile/delete/<profile_id>", methods=["POST"])
def delete_profile_route(profile_id):
    """Delete a custom profile."""
    if profile_id == "kiruthiknivas":
        return jsonify({"success": False, "message": "Cannot delete default profile."}), 400

    deleted = profile_manager.delete_profile(profile_id)
    if deleted:
        return jsonify({"success": True, "message": "Profile removed successfully."})
    return jsonify({"success": False, "message": "Profile not found."}), 404


# ============================================================
# ROUTES: GENERATION
# ============================================================
@app.route("/generate", methods=["POST"])
def generate():
    """Generate a tailored resume for the selected profile."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "message": "No data received"}), 400

        profile_id = data.get("profile_id", "kiruthiknivas").strip()
        company = data.get("company", "").strip()
        country = data.get("country", "").strip()
        jd = data.get("jd", "").strip()
        ai_provider = data.get("ai_provider", "gemini").strip().lower()

        # Validate inputs
        if not company:
            return jsonify({"success": False, "message": "Company name is required"}), 400
        if not country:
            return jsonify({"success": False, "message": "Country is required"}), 400
        if not jd:
            return jsonify({"success": False, "message": "Job description is required"}), 400

        # Load candidate profile
        profile = profile_manager.get_profile(profile_id)
        if not profile:
            profile = profile_manager.DEFAULT_PROFILE

        owner = profile.get("owner", profile_manager.DEFAULT_PROFILE["owner"])
        original_resume = profile.get("resume_data", profile_manager.DEFAULT_PROFILE["resume_data"])
        sync_icloud = profile.get("sync_icloud", False)

        candidate_name = owner.get("name", "candidate")
        logger.info(
            "Generating resume for '%s' -> %s (%s) using %s",
            candidate_name, company, country, ai_provider,
        )

        # Step 1: Generate tailored content with AI
        user_api_key = data.get("api_key", "").strip()
        gemini_key = user_api_key if ai_provider == "gemini" and user_api_key else (os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY") or GEMINI_API_KEY)
        openai_key = user_api_key if ai_provider in ["openai", "copilot"] and user_api_key else (os.environ.get("OPENAI_API_KEY") or OPENAI_API_KEY)

        logger.info("Step 1: Calling AI provider (%s)...", ai_provider)
        tailored_content = generate_tailored_content(
            ai_provider=ai_provider,
            original_resume=original_resume,
            company=company,
            country=country,
            jd=jd,
            gemini_key=gemini_key,
            openai_key=openai_key,
            ollama_url=OLLAMA_BASE_URL,
            ollama_model=OLLAMA_MODEL,
        )
        logger.info("AI content generated successfully")

        # Step 2: Build LaTeX source
        logger.info("Step 2: Building LaTeX source...")
        latex_source = build_latex_source(
            owner=owner,
            tailored=tailored_content,
            original_resume=original_resume,
        )

        # Step 3: Compile to PDF
        logger.info("Step 3: Compiling LaTeX to PDF...")
        safe_candidate = re.sub(r'[^a-zA-Z0-9]', '_', candidate_name.lower()).strip('_')
        safe_company = re.sub(r'[^a-zA-Z0-9]', '_', company.lower()).strip('_')
        safe_company = re.sub(r'_+', '_', safe_company)
        filename = f"{safe_candidate}_resume_{safe_company}"

        cls_file = os.path.join(LATEX_TEMPLATE_DIR, "resume.cls")
        pdf_path = compile_latex_to_pdf(
            latex_source=latex_source,
            output_dir=OUTPUT_DIR,
            filename=filename,
            cls_file_path=cls_file,
        )

        # Save the .tex source for inspection
        tex_path = os.path.join(OUTPUT_DIR, f"{filename}.tex")
        with open(tex_path, "w", encoding="utf-8") as f:
            f.write(latex_source)

        # Copy to iCloud Resume folder if enabled for this profile
        icloud_saved = False
        if sync_icloud and os.path.exists(profile_manager.ICLOUD_RESUME_DIR):
            try:
                shutil.copy2(pdf_path, os.path.join(profile_manager.ICLOUD_RESUME_DIR, f"{filename}.pdf"))
                logger.info("Synced PDF to iCloud folder: %s", profile_manager.ICLOUD_RESUME_DIR)
                icloud_saved = True
            except Exception as e:
                logger.warning("Could not sync to iCloud: %s", e)

        logger.info("Resume generated: %s", pdf_path)

        # Save to history
        _save_to_history(company, country, ai_provider, filename, pdf_path, candidate_name)

        dest_msg = "Synced to iCloud Drive & local output" if icloud_saved else "Saved to output folder (ready for download)"

        return jsonify({
            "success": True,
            "pdf_path": pdf_path,
            "filename": f"{filename}.pdf",
            "candidate_name": candidate_name,
            "sync_icloud": icloud_saved,
            "message": f"Resume tailored for {company} ({country}) generated successfully! ({dest_msg})",
        })

    except ValueError as e:
        logger.error("Validation error: %s", e)
        return jsonify({"success": False, "message": str(e)}), 400

    except RuntimeError as e:
        logger.error("Runtime error: %s", e)
        return jsonify({"success": False, "message": str(e)}), 500

    except Exception as e:
        logger.exception("Unexpected error during generation")
        return jsonify({
            "success": False,
            "message": f"An unexpected error occurred: {str(e)}",
        }), 500


# ============================================================
# ROUTES: DOWNLOAD & PREVIEW
# ============================================================
@app.route("/download/<filename>")
def download(filename):
    """Download a generated PDF."""
    pdf_path = os.path.join(OUTPUT_DIR, filename)
    if not os.path.exists(pdf_path):
        return jsonify({"success": False, "message": "File not found"}), 404
    return send_file(pdf_path, as_attachment=True, download_name=filename)


@app.route("/view/<filename>")
def view_pdf(filename):
    """Stream PDF inline for in-browser/mobile PDF view."""
    pdf_path = os.path.join(OUTPUT_DIR, filename)
    if not os.path.exists(pdf_path):
        return jsonify({"success": False, "message": "File not found"}), 404
    return send_file(pdf_path, mimetype='application/pdf')


@app.route("/history")
def history():
    """Get generation history."""
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            records = json.load(f)
    else:
        records = []
    return jsonify(records)


# ============================================================
# HELPERS
# ============================================================
def _save_to_history(company, country, provider, filename, pdf_path, candidate_name):
    """Save generation record to history file."""
    records = []
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                records = json.load(f)
        except (json.JSONDecodeError, IOError):
            records = []

    records.insert(0, {
        "candidate": candidate_name,
        "company": company,
        "country": country,
        "ai_provider": provider,
        "filename": f"{filename}.pdf",
        "pdf_path": pdf_path,
        "generated_at": datetime.now().isoformat(),
    })

    records = records[:50]

    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2)


# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    local_ip = get_local_ip()

    print()
    print("=" * 65)
    print("  RESUME TAILOR PRO (Multi-Profile & Mobile Edition)")
    print("  AI-Powered ATS-Optimized Resume Generator")
    print("=" * 65)
    print()
    print(f"  PC Local Access:    http://127.0.0.1:{FLASK_PORT}")
    print(f"  Mobile/iPhone URL:  http://{local_ip}:{FLASK_PORT}")
    print(f"  Output Directory:   {OUTPUT_DIR}")
    print()
    print("  AI Providers:")
    gemini_active = bool(os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY") or GEMINI_API_KEY)
    openai_active = bool(os.environ.get("OPENAI_API_KEY") or OPENAI_API_KEY)
    print(f"    Gemini:  {'[CONFIGURED]' if gemini_active else '[NOT SET]'}")
    print(f"    OpenAI:  {'[CONFIGURED]' if openai_active else '[NOT SET]'}")
    print(f"    Ollama:  Available at {OLLAMA_BASE_URL}")
    print()
    print("  Profiles:")
    for prof in profile_manager.list_profiles():
        def_tag = " (Default - iCloud Sync)" if prof.get("is_default") else ""
        print(f"    - {prof.get('name')}{def_tag}")
    print()
    print("=" * 65)
    print()

    app.run(host=FLASK_HOST, port=FLASK_PORT, debug=FLASK_DEBUG)
