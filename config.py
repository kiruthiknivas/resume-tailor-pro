# Resume Tailor Pro - Configuration
import os

# ============================================================
# PATHS
# ============================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
LATEX_TEMPLATE_DIR = os.path.join(BASE_DIR, "latex_template")
HISTORY_FILE = os.path.join(BASE_DIR, "generation_history.json")

# Load .env file if present
_env_file = os.path.join(BASE_DIR, ".env")
if os.path.exists(_env_file):
    with open(_env_file, "r", encoding="utf-8") as _ef:
        for _line in _ef:
            _line = _line.strip()
            if _line and not _line.startswith("#") and "=" in _line:
                _k, _v = _line.split("=", 1)
                os.environ.setdefault(_k.strip(), _v.strip())

# ============================================================
# AI PROVIDER CONFIGURATION
# ============================================================
# Gemini API (Google) - Primary
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY") or ""

# OpenAI (ChatGPT) - Secondary
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY") or ""

# Ollama (Local) - Tertiary
OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3.1")

# ============================================================
# RESUME OWNER DETAILS (Your original data - never changes)
# ============================================================
RESUME_OWNER = {
    "name": "Kiruthiknivas R",
    "phone": "+91 93845 38776",
    "location": "Chennai, Tamil Nadu",
    "email": "nivaskiruthik@gmail.com",
    "linkedin": "linkedin.com/in/kiruthiknivas/",
    "linkedin_url": "https://www.linkedin.com/in/kiruthiknivas/",
    "website": "kiruthiknivas.github.io",
    "website_url": "https://kiruthiknivas.github.io/",
}

# ============================================================
# ORIGINAL RESUME DATA (Your skills, experience, etc.)
# ============================================================
ORIGINAL_RESUME = {
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
}

# ============================================================
# FLASK CONFIG
# ============================================================
FLASK_HOST = os.environ.get("FLASK_HOST", "0.0.0.0")
FLASK_PORT = int(os.environ.get("PORT", 5000))
FLASK_DEBUG = os.environ.get("FLASK_DEBUG", "False").lower() in ("true", "1")
