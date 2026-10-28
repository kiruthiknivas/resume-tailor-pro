"""
Profile Manager Module - Multi-profile support and resume document parsing.
Supports PDF, DOCX, and TXT uploads and extracts structured candidate data using AI.
"""
import os
import re
import json
import logging
import uuid
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

PROFILES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "profiles")
ICLOUD_RESUME_DIR = r"C:\Users\nivas\iCloudDrive\Resume\One page Resume"


# ============================================================
# DEFAULT PROFILE: KIRUTHIKNIVAS R
# ============================================================
DEFAULT_PROFILE = {
    "id": "kiruthiknivas",
    "name": "Kiruthiknivas R",
    "is_default": True,
    "sync_icloud": True,
    "owner": {
        "name": "Kiruthiknivas R",
        "phone": "+91 93845 38776",
        "location": "Chennai, Tamil Nadu",
        "email": "nivaskiruthik@gmail.com",
        "linkedin": "linkedin.com/in/kiruthiknivas/",
        "linkedin_url": "https://www.linkedin.com/in/kiruthiknivas/",
        "website": "kiruthiknivas.github.io",
        "website_url": "https://kiruthiknivas.github.io/",
    },
    "resume_data": {
        "professional_summary": (
            "Software Engineer with 2+ years of experience developing and supporting "
            "enterprise-scale customer-facing applications using C#, .NET Core, ASP.NET Core "
            "Web API, Angular, and Microsoft SQL Server. Experienced in REST API development, "
            "application modernization, production support, SQL performance tuning, Azure/AWS "
            "environments, CI/CD, and release management. Strong understanding of Agile Scrum, "
            "SDLC, incident management, and root cause analysis, with hands-on use of GenAI "
            "tools to improve development productivity and technical documentation."
        ),
        "technical_skills": {
            "Languages": ["C#", "SQL"],
            "Frameworks": [".NET Core", "ASP.NET Core Web API", "Angular", "Entity Framework Core"],
            "Database & Backend": [
                "Microsoft SQL Server", "Oracle", "REST APIs", "LINQ",
                "Stored Procedures", "Query Optimization"
            ],
            "Cloud & DevOps": [
                "Microsoft Azure", "AWS", "Azure DevOps", "CI/CD",
                "Git", "GitHub", "IIS", "Release Management"
            ],
            "Engineering": [
                "OOP", "SOLID Principles", "Dependency Injection",
                "Agile Scrum", "SDLC", "Incident Management", "RCA"
            ],
            "AI Tools": ["GitHub Copilot", "Claude AI", "Codex"],
        },
        "experience": {
            "company": "Cognizant Technology Solutions, Chennai",
            "roles": [
                {"title": "Jr Software Engineer", "period": "Oct 2025 -- Present"},
                {"title": "Programmer Analyst Trainee", "period": "Oct 2024 -- Sep 2025"},
            ],
            "bullets": [
                "Promoted to Jr Software Engineer within one year based on consistent performance and ownership of business-critical applications.",
                "Develop, enhance, and support 10+ enterprise customer-facing applications using .NET Core, ASP.NET Core Web API, Angular, Entity Framework Core, and Microsoft SQL Server.",
                "Independently manage 7 production applications, taking ownership of feature enhancements, incident resolution, production support, deployments, and release activities.",
                "Build and maintain RESTful APIs, troubleshoot application issues, optimize SQL queries, and perform root cause analysis to improve reliability and performance.",
                "Contribute to application modernization and deployments across Git, IIS, Azure, and AWS environments while supporting CI/CD pipelines and release processes.",
                "Collaborate with Business Analysts, QA, DevOps, and client teams in Agile Scrum environments, participating in sprint planning, code reviews, and production releases.",
            ],
        },
        "projects": [
            {
                "name": "AGCO -- CO-IT Applications Outsource",
                "tech": ".NET Core, Angular, SQL Server, Azure DevOps",
                "bullets": [
                    "Own, support, and develop 10 business-critical customer-facing applications, handling enhancements, production incidents, SQL performance issues, deployments, and release activities."
                ],
            },
            {
                "name": "PG\\&E -- ALM Application Upgrade Service",
                "tech": ".NET, Oracle, Application Modernization",
                "bullets": [
                    "Modernized legacy applications by upgrading to newer .NET environments, refactoring modules, resolving issues, and improving maintainability."
                ],
            },
            {
                "name": "NRG Energy -- DE Application Development",
                "tech": ".NET, SQL Server, ServiceNow",
                "bullets": [
                    "Delivered backend enhancements, production defect fixes, and SQL optimizations through debugging, testing, code reviews, and release cycles."
                ],
            },
        ],
        "certifications": [
            "Microsoft Certified: Azure Developer Associate",
            "Microsoft Certified: Azure Fundamentals (AZ-900)",
            "Microsoft Certified: GitHub Administration",
            "Anthropic Certified: Claude Certified Architect -- Foundations",
        ],
        "education": {
            "degree": "Bachelor of Engineering in Computer Science",
            "period": "2020 -- 2024",
            "institution": "Sathyabama Institute of Science and Technology, Chennai",
            "cgpa": "CGPA: 9.08",
        },
    },
}


def init_profiles():
    """Ensure the profiles directory and default profile exist."""
    os.makedirs(PROFILES_DIR, exist_ok=True)
    default_path = os.path.join(PROFILES_DIR, "kiruthiknivas.json")
    if not os.path.exists(default_path):
        with open(default_path, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_PROFILE, f, indent=2)
        logger.info("Initialized default profile: kiruthiknivas.json")


def list_profiles() -> List[Dict[str, Any]]:
    """List all available profiles."""
    init_profiles()
    profiles = []
    for fname in os.listdir(PROFILES_DIR):
        if fname.endswith(".json"):
            fpath = os.path.join(PROFILES_DIR, fname)
            try:
                with open(fpath, "r", encoding="utf-8") as f:
                    p = json.load(f)
                    profiles.append({
                        "id": p.get("id", os.path.splitext(fname)[0]),
                        "name": p.get("name", "Unknown"),
                        "is_default": p.get("is_default", False),
                        "sync_icloud": p.get("sync_icloud", False),
                        "email": p.get("owner", {}).get("email", ""),
                        "location": p.get("owner", {}).get("location", ""),
                    })
            except Exception as e:
                logger.error("Error reading profile %s: %s", fname, e)

    # Sort default first, then alphabetically
    profiles.sort(key=lambda x: (not x.get("is_default", False), x.get("name", "")))
    return profiles


def get_profile(profile_id: str) -> Optional[Dict[str, Any]]:
    """Load a single profile by ID."""
    init_profiles()
    safe_id = re.sub(r'[^a-zA-Z0-9_\-]', '', profile_id)
    fpath = os.path.join(PROFILES_DIR, f"{safe_id}.json")
    if not os.path.exists(fpath):
        # Fallback to default
        fpath = os.path.join(PROFILES_DIR, "kiruthiknivas.json")
        if not os.path.exists(fpath):
            return DEFAULT_PROFILE

    try:
        with open(fpath, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error("Failed to load profile %s: %s", profile_id, e)
        return DEFAULT_PROFILE


def save_profile(profile_data: Dict[str, Any]) -> str:
    """Save or update a profile."""
    init_profiles()
    profile_id = profile_data.get("id")
    if not profile_id:
        name = profile_data.get("name", "candidate")
        safe_name = re.sub(r'[^a-zA-Z0-9]', '_', name.lower()).strip('_')
        profile_id = f"{safe_name}_{uuid.uuid4().hex[:6]}"
        profile_data["id"] = profile_id

    fpath = os.path.join(PROFILES_DIR, f"{profile_id}.json")
    with open(fpath, "w", encoding="utf-8") as f:
        json.dump(profile_data, f, indent=2)

    logger.info("Saved profile: %s", fpath)
    return profile_id


def delete_profile(profile_id: str) -> bool:
    """Delete a custom profile (cannot delete default profile)."""
    if profile_id == "kiruthiknivas":
        return False
    safe_id = re.sub(r'[^a-zA-Z0-9_\-]', '', profile_id)
    fpath = os.path.join(PROFILES_DIR, f"{safe_id}.json")
    if os.path.exists(fpath):
        os.remove(fpath)
        logger.info("Deleted profile: %s", profile_id)
        return True
    return False


# ============================================================
# DOCUMENT TEXT EXTRACTION (PDF, DOCX, TXT)
# ============================================================
def extract_text_from_file(file_path: str, filename: str) -> str:
    """Extract plain text from uploaded PDF, DOCX, or TXT file."""
    ext = os.path.splitext(filename.lower())[1]

    if ext == ".pdf":
        import fitz
        text = []
        doc = fitz.open(file_path)
        for page in doc:
            text.append(page.get_text())
        doc.close()
        return "\n".join(text)

    elif ext in [".docx", ".doc"]:
        import docx
        doc = docx.Document(file_path)
        text = []
        for p in doc.paragraphs:
            if p.text.strip():
                text.append(p.text.strip())
        for table in doc.tables:
            for row in table.rows:
                row_text = [cell.text.strip() for cell in row.cells if cell.text.strip()]
                if row_text:
                    text.append(" | ".join(row_text))
        return "\n".join(text)

    else:
        # Assume plain text / markdown
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            return f.read()


# ============================================================
# AI RESUME PARSER (Raw text -> Structured JSON Profile)
# ============================================================
RESUME_PARSE_PROMPT = """You are an expert HR data extractor. Convert the following resume into a clean, structured JSON profile.
Extract genuine information without hallucinating. If any field is not found, leave it as empty string or list.

OUTPUT FORMAT: Return ONLY a valid JSON object matching this exact schema:
{
  "name": "Candidate Full Name",
  "owner": {
    "name": "Candidate Full Name",
    "phone": "Phone number or empty",
    "location": "City, Country or empty",
    "email": "email@example.com",
    "linkedin": "linkedin.com/in/username or empty",
    "linkedin_url": "https://www.linkedin.com/in/username or empty",
    "website": "github.com/username or portfolio or empty",
    "website_url": "https://github.com/username or empty"
  },
  "resume_data": {
    "professional_summary": "Extracted or synthesized 3-sentence summary of candidate's core background",
    "technical_skills": {
      "Languages": ["Java", "Python"],
      "Frameworks": ["React", "Node.js"],
      "Databases & Tools": ["PostgreSQL", "Docker"]
    },
    "experience": {
      "company": "Most recent or primary company name, City",
      "roles": [
        {"title": "Software Engineer", "period": "2023 -- Present"}
      ],
      "bullets": [
        "First major achievement bullet",
        "Second major achievement bullet",
        "Third major achievement bullet"
      ]
    },
    "projects": [
      {
        "name": "Project Name",
        "tech": "Technologies used",
        "bullets": ["Key accomplishment in this project"]
      }
    ],
    "certifications": [
      "Certification Name"
    ],
    "education": {
      "degree": "Degree Title",
      "period": "Start -- End Year",
      "institution": "University / College Name",
      "cgpa": "GPA / Percentage or empty"
    }
  }
}

RAW RESUME TEXT:
"""


def parse_resume_text(raw_text: str, gemini_key: str = "", openai_key: str = "") -> Dict[str, Any]:
    """Parse raw resume text into structured profile data using Gemini, OpenAI, or rule-based fallback."""
    from ai_provider import _extract_json

    prompt = RESUME_PARSE_PROMPT + raw_text[:8000]

    # Try Gemini if key is provided
    if gemini_key:
        try:
            from google import genai
            client = genai.Client(api_key=gemini_key)
            for m in ["gemini-3.5-flash-lite", "gemini-flash-latest", "gemini-3.8-flash"]:
                try:
                    res = client.models.generate_content(model=m, contents=prompt)
                    if res and res.text:
                        parsed = _extract_json(res.text)
                        parsed["is_default"] = False
                        parsed["sync_icloud"] = False
                        return parsed
                except Exception as inner_e:
                    logger.warning("Gemini parse model %s failed: %s", m, inner_e)
        except Exception as e:
            logger.warning("Gemini resume parsing failed: %s", e)

    # Try OpenAI if key is provided
    if openai_key:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=openai_key)
            res = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            parsed = _extract_json(res.choices[0].message.content)
            parsed["is_default"] = False
            parsed["sync_icloud"] = False
            return parsed
        except Exception as e:
            logger.warning("OpenAI resume parsing failed: %s", e)

    # Fallback to smart rule-based parser
    return _rule_based_resume_parser(raw_text)


def _rule_based_resume_parser(text: str) -> Dict[str, Any]:
    """Deterministic parser to extract contact info, skills, and experience when no LLM is available."""
    lines = [l.strip() for l in text.split("\n") if l.strip()]

    # Extract name (usually first non-empty line)
    name = lines[0] if lines else "Candidate"
    if len(name) > 40:
        name = "Candidate"

    # Extract email
    email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
    email = email_match.group(0) if email_match else ""

    # Extract phone
    phone_match = re.search(r'(\+?\d{1,3}[\s-]?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}', text)
    phone = phone_match.group(0) if phone_match else ""

    # Extract linkedin
    linkedin_match = re.search(r'(?:https?:\/\/)?(?:www\.)?linkedin\.com\/in\/([\w\-]+)', text, re.I)
    linkedin = f"linkedin.com/in/{linkedin_match.group(1)}" if linkedin_match else ""
    linkedin_url = f"https://www.{linkedin}" if linkedin else ""

    # Extract bullets
    bullets = [l.lstrip("•-* ").strip() for l in lines if l.startswith(("•", "-", "*")) or (len(l) > 30 and l[0].isupper())]
    if not bullets:
        bullets = ["Delivered production software features and enhancements in collaboration with team members."]

    return {
        "name": name,
        "is_default": False,
        "sync_icloud": False,
        "owner": {
            "name": name,
            "phone": phone,
            "location": "Remote / Relocation",
            "email": email,
            "linkedin": linkedin,
            "linkedin_url": linkedin_url,
            "website": "",
            "website_url": "",
        },
        "resume_data": {
            "professional_summary": f"Professional software engineer with proven experience in full-lifecycle application delivery, testing, and system enhancements.",
            "technical_skills": {
                "Technical Stack": ["Software Development", "Problem Solving", "Version Control", "Agile Methodologies"],
                "Tools & Systems": ["Git", "CI/CD", "Testing", "APIs"]
            },
            "experience": {
                "company": "Professional Experience",
                "roles": [
                    {"title": "Software Engineer", "period": "Recent"}
                ],
                "bullets": bullets[:6]
            },
            "projects": [
                {
                    "name": "Featured Project",
                    "tech": "Core Technologies",
                    "bullets": ["Delivered key architectural components and user-facing features."]
                }
            ],
            "certifications": [],
            "education": {
                "degree": "Bachelor of Engineering / Science",
                "period": "Graduate",
                "institution": "University / Institution",
                "cgpa": ""
            }
        }
    }
