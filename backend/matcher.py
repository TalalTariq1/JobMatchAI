import os
import json
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

def calculate_skills_overlap(cv_skills, github_languages, jd_skills, jd_tech_stack):
    """
    Calculates a deterministic match score, while filtering out generic soft skills
    to avoid artificial scoring penalties.
    """
    # 1. Define a blocklist of generic soft skills we want to ignore
    SOFT_SKILLS_BLOCKLIST = {
        "communication", "problem-solving", "problem solving", "english fluency", 
        "fluent english", "team player", "leadership", "time management", 
        "analytical skills", "creativity", "interpersonal skills", "flexibility"
    }

    # 1b. Synonym map: generic JD terms -> specific things a candidate might list,
    # PLUS "either/or" alternative pairs from job descriptions (e.g. a JD saying
    # "Redux or Context API" means having EITHER one should satisfy the requirement,
    # not count as two separate requirements where one is missing).
    GENERIC_SKILL_SYNONYMS = {
        "databases": {"mongodb", "postgresql", "postgres", "mysql", "sqlite",
                      "chromadb", "firestore", "redis", "database"},
        "llms": {"groq", "llama", "gpt", "openai", "chromadb", "rag",
                 "claude", "gemini", "llm"},
        "apis": {"rest apis", "api integration", "fastapi", "graphql", "api"},
        # Common frontend "either/or" alternative pairs:
        "redux": {"redux", "context api"},
        "context api": {"redux", "context api"},
        "bootstrap": {"bootstrap", "tailwind css", "tailwind"},
        "tailwind css": {"bootstrap", "tailwind css", "tailwind"},
        # Word-order variants that plain substring matching misses:
        "responsive web design": {"responsive design", "responsive web design"},
        "responsive design": {"responsive design", "responsive web design"},
        # Broad categories that show up constantly in JDs, phrased generically:
        "database design": {"mongodb", "mongoose", "database", "databases",
                             "sql", "postgresql", "mysql", "schema"},
        "web development": {"react", "react.js", "frontend development",
                             "backend development", "full stack development",
                             "node.js", "express.js", "html", "css", "javascript"},
        "software development": {"full stack development", "backend development",
                                  "frontend development", "git", "github"},
        "software engineering": {"full stack development", "backend development",
                                  "frontend development", "git", "github"},
    }

    # 2. Combine all raw items from the JD
    raw_required = jd_skills + jd_tech_stack
    
    # 3. Clean them up, but ONLY keep them if they are NOT in the soft skills blocklist
    required_skills = set()
    for item in raw_required:
        cleaned_item = item.lower().strip()
        if cleaned_item not in SOFT_SKILLS_BLOCKLIST and cleaned_item != "":
            required_skills.add(cleaned_item)
    
    # 4. Combine all candidate skills from CV and GitHub languages
    candidate_pool = set(skill.lower().strip() for skill in cv_skills)
    if github_languages:
        candidate_pool.update(lang.lower().strip() for lang in github_languages)
        
    if not required_skills:
        return 100.0, [], []

    # 5. Separate into matched and missing lists
    matched_skills = []
    missing_skills = []
    
    for req in required_skills:
        # Direct text overlap (e.g. JD says "node.js", CV says "node.js")
        direct_match = any(req in cand or cand in req for cand in candidate_pool)

        # Synonym/alternative check: if this JD term is a known generic category
        # OR part of a known "either/or" alternative pair, see if the candidate
        # has ANY of the accepted equivalents anywhere in their skill pool.
        synonym_match = False
        if req in GENERIC_SKILL_SYNONYMS:
            known_specifics = GENERIC_SKILL_SYNONYMS[req]
            synonym_match = any(
                specific in cand or cand in specific
                for cand in candidate_pool
                for specific in known_specifics
            )

        if direct_match or synonym_match:
            matched_skills.append(req.title())
        else:
            missing_skills.append(req.title())
            
    # 6. Calculate mathematical score percentage based on hard technical requirements
    score = (len(matched_skills) / len(required_skills)) * 100
    
    return round(score, 1), matched_skills, missing_skills


def reconcile_missing_skills(missing_skills, cv_skills, cv_projects, github_summary):
    """
    The deterministic matcher above only catches matches it has EXACT text
    or a pre-written synonym for - which means it will always eventually
    miss some generic JD phrasing (e.g. "Database Design" when the CV says
    "MongoDB", or "Web Development" when the CV clearly shows web projects).
    Rather than endlessly growing a hardcoded synonym dictionary forever,
    this function does a single LLM pass that reviews ONLY the leftover
    missing items against the candidate's full real profile, and moves
    over anything that's a genuine false negative - a generic requirement
    that IS actually demonstrated, just phrased differently.

    Returns (updated_matched_additions, still_missing) - the caller merges
    updated_matched_additions into the matched list.
    """
    if not missing_skills:
        return [], []

    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

    prompt = f"""
    A deterministic keyword matcher flagged these job requirements as "missing"
    from a candidate's profile: {missing_skills}

    Review the candidate's ACTUAL skills, projects, and GitHub data below.
    Some of these "missing" items are often generic/high-level phrasings
    (e.g. "Database Design", "Web Development", "Software Engineering") that
    ARE genuinely demonstrated by specific evidence, just not in the exact
    same words. Others are genuinely absent and should stay missing.

    Be honest and conservative: only move an item to "actually_covered" if
    there is clear, specific evidence for it. If in doubt, leave it missing.

    Candidate skills: {cv_skills}
    Candidate projects: {json.dumps(cv_projects, indent=2)}
    Candidate GitHub data: {json.dumps(github_summary, indent=2) if github_summary else "Not provided"}

    Return ONLY a JSON object:
    {{
        "actually_covered": ["exact item text from the missing list that IS covered"],
        "still_missing": ["exact item text from the missing list that is genuinely absent"]
    }}
    """

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
    )
    result = json.loads(response.choices[0].message.content)
    return result.get("actually_covered", []), result.get("still_missing", missing_skills)


def generate_match_reasoning(matched_skills, missing_skills, score, cv_projects, github_summary=None, company_context=None):
    """
    Passes the hand-calculated math results, CV projects, GitHub summary, and
    company/domain context to the LLM to generate an honest, contextual
    explanation of the candidate's fit. CV projects and GitHub data are kept as
    two separate, clearly labeled sections so the model treats them as equally
    important evidence.
    """
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

    github_summary = github_summary or {}
    github_section = f"""
    Top languages: {github_summary.get("top_languages", [])}
    Project themes: {github_summary.get("project_themes", [])}
    Notable repos: {json.dumps(github_summary.get("notable_projects", []), indent=2)}
    """

    company_line = ""
    if company_context:
        company_line = f"\n    COMPANY/DOMAIN CONTEXT: {company_context}\n    If any candidate project matches this company's specific business domain (not just tech stack), call that out explicitly as a strong signal — domain relevance matters as much as tech stack overlap.\n"

    prompt = f"""
    You are an elite, technically rigorous Engineering Director and Lead Technical Recruiter conducting a candidate portfolio evaluation.
    Your objective is to provide an exhaustive, multi-paragraph match assessment based strictly on the candidate data payload provided below.

    CRITICAL EXECUTION WARNING: 
    Do NOT write generic placeholder text such as "the candidate has built relevant systems," "the candidate's projects prove their fit," or "their background matches well." 
    You MUST actively read the text data inside the payload, extract the specific project names, repo data, exact libraries, databases, and architectural workflows present, and cite them directly in your reasoning paragraphs. If your response reads like a generic HR template, the system has failed.

    The matching algorithm has calculated an exact skill alignment score of {score}%.
    {company_line}
    =========================================
    CANDIDATE DATA PAYLOAD (DYNAMIC):
    =========================================
    - Math Engine Matched Skills: {matched_skills}
    - Math Engine Missing Skills: {missing_skills}

    === CANDIDATE CV PROJECTS ===
    {json.dumps(cv_projects, indent=2)}

    === CANDIDATE LIVE GITHUB PROFILE ===
    {github_section}

    Both the CV projects section and the GitHub profile section above are equally
    important evidence. Your analysis MUST reference specific items from BOTH
    sections, not just the CV projects.

    =========================================
    STRICT CONTENT GENERATION RULES:
    =========================================
    1. EXHAUSTIVE DATA GROUNDING: You must dedicate individual, dense analytical commentary to the technical initiatives discovered in the data payload. Look through the list, capture the actual project names or GitHub indicators, and explicitly match their frameworks, tools, or automation features to show exactly how that background satisfies the needs of the job opening.

    2. COGNITIVE ARCHITECTURAL BRIDGES: Analyze any missing framework gaps (e.g., if the job asks for Next.js or explicit IDE AI assistants like Cursor/Claude Code, and those exact words are not explicitly found in the candidate's skills array). 
       Look at their foundational stack in the payload (such as custom frontend state management, asynchronous backend routing, database indexing, or manual LLM text-generation pipelines). 
       Argue technically how their practical mastery of these core software paradigms proves they possess the engineering maturity to easily scale, transition, and write clear logic or specs inside the target workspace within days. Frame tooling mismatches as simple environment shifts, not engineering competency deficiencies.

    3. STRICT MINIMALISM ON MISSING SKILLS: Do not drag down the evaluation or dwell on what is missing. State the literal tool gaps briefly and move on.

    Output Format Structure:
    ### 🚀 Overall Candidate Technical Match Verdict
    [Write an intense, highly specific engineering summary analyzing the candidate's overall full-stack architecture capabilities, database familiarity, and alignment percentage based strictly on the payload parameters.]

    ### 🛠️ Deep-Dive Project Portfolio Review & Core Strengths
    [Provide a heavy, technically rich breakdown that isolates and analyzes the implementation details, libraries, and design choices of the specific systems found directly inside the candidate's portfolio payload. Explicitly mention the projects by their exact names as parsed from the data.]

    ### 📊 Technical Alignment & Tool Adaptability Bridge
    [Explain how the candidate's hands-on experience with their current stack components, custom API handlers, or AI model implementations directly constructs a conceptual bridge to master the specific tooling, deployment workflows, or developer frameworks requested in the JD.]

    ### 📉 Verified Technical Gaps & Stack Discrepancies
    [Write exactly 1 to 2 brief, straightforward sentences listing the missing standalone tools or technologies from the missing skills array (e.g., specific target frameworks or environment tools). Emphasize instantly that these represent immediate tooling orientation items rather than core engineering blockers.]
    """
    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    
    return response.choices[0].message.content.strip()


def match_candidate_to_job(cv_json, github_summary, jd_json):
    """
    Main orchestrator function that combines data inputs, handles the 
    algorithmic math step, and attaches the LLM reasoning explanation.
    """
    # Parse inputs if they arrive as raw JSON strings
    cv = json.loads(cv_json) if isinstance(cv_json, str) else cv_json
    github = json.loads(github_summary) if isinstance(github_summary, str) else github_summary
    jd = json.loads(jd_json) if isinstance(jd_json, str) else jd_json
    
    # Extract lists safely with fallbacks
    cv_skills = cv.get("skills", [])
    github_langs = github.get("top_languages", [])  # Your elite catch fix! ⚡
    jd_skills = jd.get("key_skills", [])
    jd_tech_stack = jd.get("tech_stack", [])
    cv_projects = cv.get("projects", [])

    # Company/domain context, if the JD parser extracted it (see jd_parser.py update)
    company_context = jd.get("company_context", None)
    
    # Step 1: Run Hand-Written Math
    score, matched, missing = calculate_skills_overlap(cv_skills, github_langs, jd_skills, jd_tech_stack)

    # Step 1b: Reconcile any remaining "missing" items against the candidate's
    # full profile - catches generic JD phrasing (e.g. "Database Design",
    # "Web Development") that the deterministic matcher has no way to know
    # is actually covered, without needing to hardcode every possible phrasing.
    if missing:
        newly_covered, missing = reconcile_missing_skills(missing, cv_skills, cv_projects, github)
        matched = matched + newly_covered
        total_required = len(matched) + len(missing)
        score = round((len(matched) / total_required) * 100, 1) if total_required else 100.0

    # Step 2: Run LLM Reasoning Explanation
    reasoning = generate_match_reasoning(
        matched, missing, score, cv_projects,
        github_summary=github,
        company_context=company_context,
    )
    
    # Step 3: Package final structured engine response
    return {
        "match_score": score,
        "matched_skills": matched,
        "missing_skills": missing,
        "recruiter_reasoning": reasoning
    }


# --- RUNNING THE UPDATED TEST BLOCK ---
if __name__ == "__main__":
    print("Testing Updated Matcher Engine with your GitHub Key Schema...\n")
    
    # Mock data mimicking your actual outputs
    mock_cv = {
        "skills": ["C++", "JavaScript", "TypeScript", "Node.js", "MongoDB", "Git"],
        "projects": [
            {"name": "StayScape", "description": "Hotel booking platform built using Node.js and MongoDB."},
            {"name": "AI Assignment Solver", "description": "Full-stack application utilizing Python and FastAPI."}
        ]
    }
    
    # Using your actual fetcher dictionary structure here
    mock_github = {
        "top_languages": ["C", "OpenSCAD", "C++"]
    }
    
    # A backend job posting that requires C++ and Node but also has gaps (Docker)
    mock_jd = {
        "key_skills": ["Backend development", "Git"],
        "tech_stack": ["C++", "Node.js", "Docker"]
    }
    
    result = match_candidate_to_job(mock_cv, mock_github, mock_jd)
    
    print("=================== ENGINE OUTPUT ===================")
    print(f"Calculated Score: {result['match_score']}%")
    print(f"Matched Stack:    {result['matched_skills']}")
    print(f"Missing Stack:    {result['missing_skills']}")
    print("-----------------------------------------------------")
    print("AI Generated Recruiter Reasoning:")
    print(result['recruiter_reasoning'])
    print("=====================================================")