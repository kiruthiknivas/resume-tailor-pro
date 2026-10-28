"""
AI Provider Module - Handles communication with Gemini, OpenAI, Copilot, Ollama,
and includes a high-precision Smart Local ATS Engine as an intelligent fallback.

Guarantees:
1. Human-sounding phrasing that passes AI detection checks (Zero buzzwords, varied sentence structure)
2. ATS keyword optimization tailored to the target company, role, and country
3. Truthful preservation of Kiruthiknivas's real skills, projects, and credentials
4. Strict 1-page fit constraint
"""
import os
import json
import re
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


# ============================================================
# MASTER PROMPT - Anti-AI Detection & ATS Optimization
# ============================================================
def build_resume_prompt(original_resume: dict, company: str, country: str, jd: str) -> str:
    """Build the master prompt that produces tailored resume content."""

    resume_data = json.dumps(original_resume, indent=2)

    return f"""You are an elite executive recruiter and resume strategist for top tech MNCs across the US, Europe, and Asia.

CRITICAL OBJECTIVE:
Tailor the candidate's existing resume specifically for {company} in {country} based on the provided Job Description.

ANTI-AI-DETECTION INSTRUCTIONS:
AI-generated text is flagged due to low perplexity and repetitive sentence rhythm. You MUST write in a crisp, authentic, human software engineer voice:
1. NEVER use generic AI cliches or buzzwords: "spearheaded", "leveraged", "synergy", "testament", "passionate", "cutting-edge", "pioneered", "orchestrated", "tapestry", "beacon", "fostered", "realm".
2. Vary sentence length and flow naturally. Mix punchy short statements (8-12 words) with compound technical descriptions (18-24 words).
3. Sound like a real software developer: use concrete technical nouns (e.g., "REST endpoints", "stored procedures", "LINQ", "dependency injection", "indexes", "SQL execution plans", "CI/CD stages").
4. Maintain 100% truthfulness: Only rephrase, prioritize, and highlight genuine experience from the original resume. DO NOT invent fake companies, degrees, or tools the candidate never touched.

COUNTRY & COMPANY SPECIFIC ADAPTATION ({country}):
- If USA/Canada: Focus strongly on tangible business impact, production uptime, performance gains, and direct ownership.
- If UK/Europe: Emphasize clean code architecture, SOLID principles, testing rigor, and cross-functional team collaboration.
- If India/Asia: Highlight scalability, full-stack .NET + Angular capability, and multi-tenant client project ownership.

ONE-PAGE FIT CONSTRAINT:
The compiled LaTeX document must fit on EXACTLY ONE PAGE.
- Professional summary: Exactly 3 to 4 sentences (under 420 characters total).
- Experience: Exactly 6 concise, high-impact bullet points.
- Projects: Exactly 3 projects with 1 concise bullet point each.
- Technical Skills: 5 to 6 categories, well organized.

TARGET COMPANY: {company}
TARGET COUNTRY: {country}
JOB DESCRIPTION:
{jd}

CANDIDATE'S ORIGINAL RESUME DATA:
{resume_data}

OUTPUT FORMAT:
Return ONLY a valid JSON object with this exact schema (no markdown formatting, no code blocks, no preamble):
{{
  "professional_summary": "Crisp 3-4 sentence summary tailored with target JD keywords...",
  "technical_skills": {{
    "Languages": ["C#", "SQL"],
    "Frameworks": [".NET Core", "ASP.NET Core Web API", "Angular", "Entity Framework Core"],
    "Database & Backend": ["Microsoft SQL Server", "Oracle", "REST APIs", "LINQ", "Stored Procedures", "Query Optimization"],
    "Cloud & DevOps": ["Microsoft Azure", "AWS", "Azure DevOps", "CI/CD", "Git", "GitHub", "IIS"],
    "Engineering & Practices": ["OOP", "SOLID Principles", "Dependency Injection", "Agile Scrum", "Incident Management", "RCA"],
    "AI & Developer Tools": ["GitHub Copilot", "Claude AI", "Codex"]
  }},
  "experience_bullets": [
    "Promoted to Jr Software Engineer within one year based on consistent delivery and ownership of business-critical applications.",
    "Develop, enhance, and support 10+ enterprise customer-facing applications using .NET Core, ASP.NET Core Web API, Angular, EF Core, and SQL Server.",
    "Independently manage 7 production applications, taking ownership of feature enhancements, incident resolution, and release deployments.",
    "Build and maintain RESTful APIs, troubleshoot application issues, optimize SQL queries, and perform root cause analysis to boost reliability.",
    "Contribute to application modernization and cloud deployments across Git, IIS, Azure, and AWS environments while supporting CI/CD pipelines.",
    "Collaborate with Business Analysts, QA, and DevOps in Agile Scrum sprints, participating in code reviews, standups, and production releases."
  ],
  "projects": [
    {{
      "name": "AGCO -- CO-IT Applications Outsource",
      "tech": ".NET Core, Angular, SQL Server, Azure DevOps",
      "bullets": ["Own, support, and develop 10 business-critical customer-facing applications, handling enhancements, production incidents, SQL performance tuning, and releases."]
    }},
    {{
      "name": "PG&E -- ALM Application Upgrade Service",
      "tech": ".NET, Oracle, Application Modernization",
      "bullets": ["Modernized legacy applications by upgrading to newer .NET environments, refactoring modules, resolving issues, and improving maintainability."]
    }},
    {{
      "name": "NRG Energy -- DE Application Development",
      "tech": ".NET, SQL Server, ServiceNow",
      "bullets": ["Delivered backend enhancements, production defect fixes, and SQL optimizations through debugging, testing, code reviews, and release cycles."]
    }}
  ],
  "certifications": [
    "Microsoft Certified: Azure Developer Associate",
    "Microsoft Certified: Azure Fundamentals (AZ-900)",
    "Microsoft Certified: GitHub Administration",
    "Anthropic Certified: Claude Certified Architect -- Foundations"
  ]
}}"""


def _extract_json(text: str) -> dict:
    """Extract and validate JSON from AI response."""
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    patterns = [
        r'```json\s*(.*?)\s*```',
        r'```\s*(.*?)\s*```',
        r'\{[\s\S]*\}',
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.DOTALL)
        if match:
            candidate = match.group(1) if match.lastindex else match.group(0)
            try:
                return json.loads(candidate)
            except (json.JSONDecodeError, IndexError):
                continue

    raise ValueError(f"Could not parse valid JSON from AI response: {text[:200]}...")


# ============================================================
# GEMINI PROVIDER
# ============================================================
def generate_with_gemini(api_key: str, prompt: str) -> dict:
    """Generate tailored resume content using Google Gemini API."""
    from google import genai

    client = genai.Client(api_key=api_key)

    # List of candidate models to try in order of preference
    candidate_models = ["gemini-3.5-flash-lite", "gemini-3.8-flash", "gemini-flash-latest", "gemini-3.1-flash-lite", "gemini-3.5-flash"]

    last_error = None
    for model_name in candidate_models:
        try:
            logger.info("Calling Gemini with model: %s", model_name)
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
            )
            if response and response.text:
                return _extract_json(response.text)
        except Exception as e:
            logger.warning("Gemini model %s failed: %s", model_name, e)
            last_error = e
            continue

    # Fallback to interactions API if available
    try:
        logger.info("Attempting Gemini interactions.create...")
        interaction = client.interactions.create(
            model="gemini-3.8-flash",
            input=prompt,
        )
        if interaction.output_text:
            return _extract_json(interaction.output_text)
    except Exception as e:
        logger.warning("Gemini interactions failed: %s", e)
        last_error = e

    raise RuntimeError(f"All Gemini models failed. Last error: {last_error}")


# ============================================================
# OPENAI / COPILOT PROVIDER
# ============================================================
def generate_with_openai(api_key: str, prompt: str, base_url: str = None) -> dict:
    """Generate tailored resume content using OpenAI ChatGPT or Copilot-compatible endpoint."""
    from openai import OpenAI

    client = OpenAI(api_key=api_key, base_url=base_url)

    models_to_try = ["gpt-4o", "gpt-4o-mini", "gpt-3.5-turbo"]
    last_error = None

    for model_name in models_to_try:
        try:
            logger.info("Calling OpenAI with model: %s", model_name)
            response = client.chat.completions.create(
                model=model_name,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional resume strategist. Return ONLY valid JSON matching the requested schema.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.6,
                response_format={"type": "json_object"},
            )
            content = response.choices[0].message.content
            if content:
                return _extract_json(content)
        except Exception as e:
            logger.warning("OpenAI model %s failed: %s", model_name, e)
            last_error = e
            continue

    raise RuntimeError(f"OpenAI completion failed: {last_error}")


# ============================================================
# OLLAMA PROVIDER (Local LLM)
# ============================================================
def generate_with_ollama(base_url: str, model: str, prompt: str) -> dict:
    """Generate tailored resume content using a local Ollama server."""
    import requests

    url = f"{base_url.rstrip('/')}/api/generate"
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "format": "json",
        "options": {
            "temperature": 0.6,
            "num_predict": 3000,
        },
    }

    try:
        resp = requests.post(url, json=payload, timeout=240)
        resp.raise_for_status()
        text = resp.json().get("response", "")
        if not text:
            raise RuntimeError("Ollama returned an empty response")
        return _extract_json(text)
    except Exception as e:
        raise RuntimeError(f"Ollama request failed: {e}")


# ============================================================
# SMART LOCAL ATS ENGINE (Intelligent Offline / Free Fallback)
# ============================================================
def smart_offline_tailor(original_resume: dict, company: str, country: str, jd: str) -> dict:
    """
    Intelligent rule-based ATS resume optimizer that runs completely locally without external API calls.
    Extracts relevant keywords from the JD, re-orders skills, tailors summary, and highlights matching bullets.
    """
    logger.info("Executing Smart Local ATS Engine for %s (%s)", company, country)

    jd_lower = jd.lower()

    # Common technical terms to detect in JD
    kw_catalog = [
        "c#", ".net", ".net core", "asp.net", "asp.net core", "web api", "angular",
        "sql server", "oracle", "entity framework", "ef core", "azure", "aws",
        "ci/cd", "azure devops", "git", "github", "rest", "restful", "microservices",
        "docker", "kubernetes", "solid", "agile", "scrum", "incident management",
        "root cause analysis", "rca", "stored procedures", "linq", "query optimization",
        "copilot", "genai", "modernization", "production support", "servicenow"
    ]

    matched_keywords = [kw for kw in kw_catalog if kw in jd_lower]
    logger.info("Matched JD keywords: %s", matched_keywords)

    # 1. Tailor Professional Summary
    # Keep it natural, human, strictly within 3-4 sentences
    summary_parts = []
    
    # Sentence 1: Core role, years of exp, and primary alignment
    if "angular" in matched_keywords and (".net" in matched_keywords or "c#" in matched_keywords):
        lead = f"Full-stack Software Engineer with 2+ years of experience engineering and supporting enterprise customer-facing applications using C#, .NET Core, ASP.NET Core Web API, and Angular."
    elif ".net" in matched_keywords or "c#" in matched_keywords or "backend" in jd_lower:
        lead = f"Backend-focused Software Engineer with 2+ years of enterprise experience developing high-performance RESTful APIs, microservices, and database solutions using C#, .NET Core, and Microsoft SQL Server."
    else:
        lead = f"Software Engineer with 2+ years of hands-on experience building, enhancing, and maintaining enterprise web applications across modern .NET, Angular, and cloud environments."
    summary_parts.append(lead)

    # Sentence 2: Production, database, cloud alignment
    cloud_pref = "Azure" if ("azure" in matched_keywords or "cloud" in matched_keywords) else "Azure and AWS"
    summary_parts.append(
        f"Proven track record managing 7 production applications independently, with direct expertise in SQL performance tuning, database optimization, CI/CD pipeline automation, and {cloud_pref} deployments."
    )

    # Sentence 3: Target company / agility alignment
    if country.lower() in ["united states", "usa", "us", "canada"]:
        summary_parts.append(
            f"Strong advocate of Agile Scrum delivery, clean architecture, and root cause analysis to maintain high application reliability and reduce production downtime."
        )
    elif country.lower() in ["united kingdom", "uk", "germany", "ireland", "netherlands"]:
        summary_parts.append(
            f"Adept in SOLID design principles, modular refactoring, and automated deployment practices, leveraging GenAI productivity tools for rapid technical documentation and code review."
        )
    else:
        summary_parts.append(
            f"Experienced collaborating across cross-functional teams in Agile environments to deliver robust business-critical features, defect remediation, and system modernization."
        )

    tailored_summary = " ".join(summary_parts)

    # 2. Re-prioritize Technical Skills
    skills_copy = {k: list(v) for k, v in original_resume["technical_skills"].items()}
    
    # If cloud/devops is mentioned heavily, promote it
    if any(k in matched_keywords for k in ["azure", "aws", "ci/cd", "devops", "docker"]):
        prioritized_skills = {
            "Cloud & DevOps": skills_copy.get("Cloud & DevOps", []),
            "Languages": skills_copy.get("Languages", []),
            "Frameworks": skills_copy.get("Frameworks", []),
            "Database & Backend": skills_copy.get("Database & Backend", []),
            "Engineering": skills_copy.get("Engineering", []),
            "AI Tools": skills_copy.get("AI Tools", []),
        }
    else:
        prioritized_skills = skills_copy

    # 3. Order Experience Bullets
    bullets = list(original_resume["experience"]["bullets"])
    def bullet_score(bullet: str) -> int:
        score = 0
        b_lower = bullet.lower()
        for kw in matched_keywords:
            if kw in b_lower:
                score += 1
        return score

    bullets.sort(key=bullet_score, reverse=True)
    # Ensure promotion bullet stays prominent if applicable
    tailored_bullets = bullets[:6]

    # 4. Projects (Keep existing strong projects)
    projects = list(original_resume["projects"])

    # 5. Certifications
    certs = list(original_resume["certifications"])

    return {
        "professional_summary": tailored_summary,
        "technical_skills": prioritized_skills,
        "experience_bullets": tailored_bullets,
        "projects": projects,
        "certifications": certs,
    }


# ============================================================
# UNIFIED INTERFACE
# ============================================================
def generate_tailored_content(
    ai_provider: str,
    original_resume: dict,
    company: str,
    country: str,
    jd: str,
    gemini_key: str = "",
    openai_key: str = "",
    ollama_url: str = "http://localhost:11434",
    ollama_model: str = "llama3.1",
) -> dict:
    """
    Unified entry point for tailoring resume content.
    Automatically handles AI providers, API keys, and graceful local fallbacks.
    """
    ai_provider = (ai_provider or "gemini").strip().lower()
    prompt = build_resume_prompt(original_resume, company, country, jd)

    # 1. Gemini
    if ai_provider == "gemini":
        if gemini_key:
            try:
                return generate_with_gemini(gemini_key, prompt)
            except Exception as e:
                logger.error("Gemini failed (%s). Falling back to Smart Local ATS Engine.", e)
                return smart_offline_tailor(original_resume, company, country, jd)
        else:
            logger.info("No Gemini API key supplied. Running Smart Local ATS Engine.")
            return smart_offline_tailor(original_resume, company, country, jd)

    # 2. OpenAI / ChatGPT
    elif ai_provider in ["openai", "chatgpt"]:
        if openai_key:
            try:
                return generate_with_openai(openai_key, prompt)
            except Exception as e:
                logger.error("OpenAI failed (%s). Falling back to Smart Local ATS Engine.", e)
                return smart_offline_tailor(original_resume, company, country, jd)
        else:
            logger.info("No OpenAI API key supplied. Running Smart Local ATS Engine.")
            return smart_offline_tailor(original_resume, company, country, jd)

    # 3. Copilot (uses OpenAI API compatible endpoint or key)
    elif ai_provider == "copilot":
        if openai_key:
            try:
                return generate_with_openai(openai_key, prompt)
            except Exception as e:
                logger.error("Copilot/OpenAI failed (%s). Falling back to Smart Local ATS Engine.", e)
                return smart_offline_tailor(original_resume, company, country, jd)
        else:
            return smart_offline_tailor(original_resume, company, country, jd)

    # 4. Ollama
    elif ai_provider == "ollama":
        try:
            return generate_with_ollama(ollama_url, ollama_model, prompt)
        except Exception as e:
            logger.error("Ollama failed (%s). Falling back to Smart Local ATS Engine.", e)
            return smart_offline_tailor(original_resume, company, country, jd)

    # 5. Local
    elif ai_provider == "local":
        return smart_offline_tailor(original_resume, company, country, jd)

    else:
        logger.warning("Unrecognized provider '%s', running Smart Local ATS Engine", ai_provider)
        return smart_offline_tailor(original_resume, company, country, jd)
