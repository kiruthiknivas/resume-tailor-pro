"""
LaTeX Resume Builder - Generates LaTeX source and compiles to PDF.
Uses the exact same resume.cls template from the original Overleaf resume.
"""
import os
import subprocess
import shutil
import tempfile
import logging
import re
import sys

logger = logging.getLogger(__name__)


def _escape_latex(text: str) -> str:
    """Escape special LaTeX characters in text, preserving intentional LaTeX commands."""
    if not text:
        return ""

    # Don't escape if text already contains LaTeX commands
    if '\\' in text and any(cmd in text for cmd in ['\\textbf', '\\href', '\\quad', '\\begin', '\\end', '\\item', '\\hfill', '\\vspace', '\\&']):
        return text

    # Escape special characters
    replacements = [
        ('&', '\\&'),
        ('%', '\\%'),
        ('$', '\\$'),
        ('#', '\\#'),
        ('_', '\\_'),
        ('{', '\\{'),
        ('}', '\\}'),
        ('~', '\\textasciitilde{}'),
        ('^', '\\textasciicircum{}'),
    ]

    for old, new in replacements:
        text = text.replace(old, new)

    return text


def _escape_skill(text: str) -> str:
    """Escape a skill name for LaTeX, handling C# and & specially."""
    if text == "C#":
        return "C\\#"
    if "&" in text:
        return text.replace("&", "\\&")
    return _escape_latex(text)


def _escape_bullet(text: str) -> str:
    """Escape a bullet point for LaTeX, handling common patterns."""
    if not text:
        return ""
    # Handle C# specifically
    text = text.replace("C#", "C\\#")
    # Handle & but not \&
    text = re.sub(r'(?<!\\)&', r'\\&', text)
    # Handle % but not \%
    text = re.sub(r'(?<!\\)%', r'\\%', text)
    # Handle # but not \# and not C\#
    text = re.sub(r'(?<!\\)(?<!C)#', r'\\#', text)
    # Handle _ but not \_
    text = re.sub(r'(?<!\\)_', r'\\_', text)
    # Handle $ but not \$
    text = re.sub(r'(?<!\\)\$', r'\\$', text)
    return text


def build_latex_source(
    owner: dict,
    tailored: dict,
    original_resume: dict,
) -> str:
    """
    Build the full LaTeX source for the tailored resume.

    Args:
        owner: dict with name, phone, location, email, linkedin, etc.
        tailored: dict from AI with professional_summary, technical_skills, etc.
        original_resume: dict with original data for fallback
    """

    # --- Header ---
    name = owner["name"]
    phone = owner["phone"]
    location = owner["location"]
    email = owner["email"]
    linkedin_url = owner["linkedin_url"]
    linkedin_display = owner["linkedin"]
    website_url = owner["website_url"]
    website_display = owner["website"]

    # --- Professional Summary ---
    summary = tailored.get("professional_summary", original_resume["professional_summary"])
    summary = _escape_bullet(summary)

    # --- Technical Skills ---
    skills = tailored.get("technical_skills", original_resume["technical_skills"])
    skills_lines = []
    for i, (category, skill_list) in enumerate(skills.items()):
        cat_escaped = _escape_skill(category)
        if isinstance(skill_list, list):
            skills_str = ", ".join(_escape_skill(s) for s in skill_list)
        else:
            skills_str = _escape_skill(str(skill_list))
        line_end = " \\\\" if i < len(skills) - 1 else ""
        skills_lines.append(f"{{\\bf {cat_escaped}:}} {skills_str}{line_end}")
    skills_block = "\n".join(skills_lines)

    # --- Experience Bullets (capped at 6 to guarantee 1-page fit) ---
    exp_bullets = list(tailored.get("experience_bullets", original_resume["experience"]["bullets"]))[:6]
    exp_items = "\n".join(f"    \\item {_escape_bullet(b)}" for b in exp_bullets)

    # --- Roles ---
    roles = original_resume["experience"]["roles"]
    roles_rows = "\n".join(
        f"\\textbf{{{r['title']}}} & {r['period']} \\\\"
        for r in roles
    )

    # --- Projects (capped at 3 with 1 bullet each) ---
    projects = list(tailored.get("projects", original_resume["projects"]))[:3]
    project_blocks = []
    for proj in projects:
        proj_name = proj["name"]
        proj_tech = proj.get("tech", "")
        proj_bullets = list(proj.get("bullets", []))[:1]

        # Escape project name - handle \& that's already in original data
        if "\\&" not in proj_name:
            proj_name = proj_name.replace("&", "\\&")

        if proj_tech:
            if "\\&" not in proj_tech:
                proj_tech = proj_tech.replace("&", "\\&")
            header = f"\\textbf{{{proj_name} \\quad | \\quad {proj_tech}}}"
        else:
            header = f"\\textbf{{{proj_name}}}"

        items = "\n".join(f"    \\item {_escape_bullet(b)}" for b in proj_bullets)

        block = f"""
{header}
\\begin{{itemize}}
{items}
\\end{{itemize}}
\\vspace{{2pt}}"""
        project_blocks.append(block)

    projects_block = "\n".join(project_blocks)

    # --- Certifications (top 4 in 2x2 grid) ---
    certs = list(tailored.get("certifications", original_resume["certifications"]))[:4]
    # Build 2-column certification table
    if len(certs) >= 4:
        cert_rows = []
        for i in range(0, len(certs), 2):
            left = _escape_bullet(certs[i]) if i < len(certs) else ""
            right = _escape_bullet(certs[i + 1]) if i + 1 < len(certs) else ""
            sep = " \\\\[-0.1em]" if i + 2 < len(certs) else ""
            cert_rows.append(f"{left} &\n{right}{sep}")
        certs_block = "\n".join(cert_rows)
        certs_section = f"""\\begin{{tabular*}}{{\\textwidth}}{{@{{\\extracolsep{{\\fill}}}}ll}}
{certs_block}
\\end{{tabular*}}"""
    else:
        cert_items = " \\\\\n".join(_escape_bullet(c) for c in certs)
        certs_section = cert_items

    # --- Education ---
    edu = original_resume["education"]

    # --- Full LaTeX Document ---
    latex = f"""\\documentclass{{resume}}

\\usepackage[left=0.4in,top=0.28in,right=0.4in,bottom=0.25in]{{geometry}}
\\usepackage{{enumitem}}
\\setlist[itemize]{{topsep=2pt,itemsep=1.5pt,parsep=0pt,partopsep=0pt,leftmargin=1.5em}}

\\name{{{name}}}

\\address{{{phone} \\quad | \\quad {location}}}
\\address{{
\\href{{mailto:{email}}}{{{email}}}
\\quad | \\quad
\\href{{{linkedin_url}}}{{{linkedin_display}}}
\\quad | \\quad
\\href{{{website_url}}}{{{website_display}}}
}}

\\begin{{document}}

%----------------------------------------------------------------------------------------
% PROFESSIONAL SUMMARY
%----------------------------------------------------------------------------------------

\\begin{{rSection}}{{PROFESSIONAL SUMMARY}}

{summary}

\\end{{rSection}}

%----------------------------------------------------------------------------------------
% TECHNICAL SKILLS
%----------------------------------------------------------------------------------------

\\begin{{rSection}}{{TECHNICAL SKILLS}}

{skills_block}

\\end{{rSection}}

%----------------------------------------------------------------------------------------
% PROFESSIONAL EXPERIENCE
%----------------------------------------------------------------------------------------

\\begin{{rSection}}{{PROFESSIONAL EXPERIENCE}}

\\textbf{{{original_resume["experience"]["company"]}}}

\\begin{{tabular*}}{{\\textwidth}}{{@{{\\extracolsep{{\\fill}}}}lr}}
{roles_rows}
\\end{{tabular*}}

\\begin{{itemize}}
{exp_items}
\\end{{itemize}}

\\end{{rSection}}

%----------------------------------------------------------------------------------------
% KEY PROJECT EXPERIENCE
%----------------------------------------------------------------------------------------

\\begin{{rSection}}{{KEY PROJECT EXPERIENCE}}
{projects_block}

\\end{{rSection}}

%----------------------------------------------------------------------------------------
% CERTIFICATIONS
%----------------------------------------------------------------------------------------

\\begin{{rSection}}{{CERTIFICATIONS}}

{certs_section}

\\end{{rSection}}

%----------------------------------------------------------------------------------------
% EDUCATION
%----------------------------------------------------------------------------------------

\\vspace{{-0.3em}}
\\begin{{rSection}}{{EDUCATION}}
\\begin{{tabular*}}{{\\textwidth}}{{@{{\\extracolsep{{\\fill}}}}lr}}
\\textbf{{{edu["degree"]}}} & \\textbf{{{edu["period"]}}} \\\\
{edu["institution"]} & {edu["cgpa"]}
\\end{{tabular*}}
\\end{{rSection}}

\\enlargethispage{{\\baselineskip}}

\\end{{document}}
"""
    return latex


def compile_latex_to_pdf(
    latex_source: str,
    output_dir: str,
    filename: str,
    cls_file_path: str,
) -> str:
    """
    Compile LaTeX source to PDF using pdflatex.

    Args:
        latex_source: The full LaTeX source string
        output_dir: Directory to save the final PDF
        filename: Output filename (without extension)
        cls_file_path: Path to resume.cls file

    Returns:
        Full path to the generated PDF
    """
    # Create temp directory for compilation
    with tempfile.TemporaryDirectory(prefix="resume_tailor_") as tmpdir:
        # Copy resume.cls to temp dir
        shutil.copy2(cls_file_path, os.path.join(tmpdir, "resume.cls"))

        # Write .tex file
        tex_path = os.path.join(tmpdir, f"{filename}.tex")
        with open(tex_path, "w", encoding="utf-8") as f:
            f.write(latex_source)

        logger.info("Compiling LaTeX in %s", tmpdir)

        # Find pdflatex
        pdflatex_cmd = _find_pdflatex()

        # Prepare compile arguments
        compile_cmd = [pdflatex_cmd, "-interaction=nonstopmode", "-halt-on-error"]
        if sys.platform == "win32":
            compile_cmd.append("--enable-installer")
        compile_cmd.append(f"{filename}.tex")

        # Run pdflatex twice (for references/layout)
        for run_num in range(2):
            try:
                result = subprocess.run(
                    compile_cmd,
                    cwd=tmpdir,
                    capture_output=True,
                    text=True,
                    timeout=120,
                )

                if result.returncode != 0:
                    # Read the log file for better error info
                    log_path = os.path.join(tmpdir, f"{filename}.log")
                    log_content = ""
                    if os.path.exists(log_path):
                        with open(log_path, "r", encoding="utf-8", errors="replace") as lf:
                            log_content = lf.read()

                    # Extract error lines from log
                    error_lines = [
                        line for line in log_content.split("\n")
                        if line.startswith("!") or "Error" in line
                    ]
                    error_summary = "\n".join(error_lines[:10]) if error_lines else result.stderr[:1000]

                    raise RuntimeError(
                        f"pdflatex compilation failed (run {run_num + 1}):\n{error_summary}"
                    )

                logger.info("pdflatex run %d completed successfully", run_num + 1)

            except subprocess.TimeoutExpired:
                raise RuntimeError("pdflatex compilation timed out (120s)")

        # Check PDF was created
        pdf_source = os.path.join(tmpdir, f"{filename}.pdf")
        if not os.path.exists(pdf_source):
            raise RuntimeError("PDF was not generated despite successful compilation")

        # Move PDF to output directory
        os.makedirs(output_dir, exist_ok=True)
        pdf_dest = os.path.join(output_dir, f"{filename}.pdf")
        shutil.copy2(pdf_source, pdf_dest)

        logger.info("PDF saved to %s", pdf_dest)
        return pdf_dest


def _find_pdflatex() -> str:
    """Find the pdflatex executable on the system (PATH or common locations)."""
    # 1. Try PATH first (Standard on Linux/Docker and configured Windows environments)
    pdflatex = shutil.which("pdflatex")
    if pdflatex:
        return pdflatex

    # 2. Check common locations on Windows
    common_paths = [
        # MiKTeX user install
        os.path.expanduser("~\\AppData\\Local\\Programs\\MiKTeX\\miktex\\bin\\x64\\pdflatex.exe"),
        # MiKTeX system install
        "C:\\Program Files\\MiKTeX\\miktex\\bin\\x64\\pdflatex.exe",
        # TeX Live
        "C:\\texlive\\2024\\bin\\windows\\pdflatex.exe",
        "C:\\texlive\\2025\\bin\\windows\\pdflatex.exe",
        "C:\\texlive\\2026\\bin\\windows\\pdflatex.exe",
    ]

    for path in common_paths:
        if os.path.exists(path):
            return path

    raise RuntimeError(
        "pdflatex not found! Please install TeX Live (Linux) or MiKTeX (Windows)."
    )
