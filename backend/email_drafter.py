import os
import json
from dotenv import load_dotenv
from groq import Groq

# Import the other pipeline pieces so this file can be tested standalone,
# the same way test_pipeline.py chains everything together.
from cv_parser import extract_cv_text, analyze_cv_text
from github_fetcher import fetch_github_repos, summarize_github_profile
from jd_parser import parse_job_description
from matcher import match_candidate_to_job

load_dotenv()


def draft_email(cv_json, jd_json, match_result, github_summary=None, recruiter_name=None):
    """
    Generates a specific, evidence-led cold outreach email to a recruiter, grounded
    in the candidate's real matched skills, CV projects, and GitHub profile (from
    matcher.py's match_candidate_to_job output), and signed with contact info pulled
    from the CV.
    """
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

    cv = json.loads(cv_json) if isinstance(cv_json, str) else cv_json
    jd = json.loads(jd_json) if isinstance(jd_json, str) else jd_json
    github_summary = json.loads(github_summary) if isinstance(github_summary, str) else github_summary

    contact = cv.get("contact_info", {})
    education = cv.get("education", {})
    candidate_name = contact.get("name", "")
    projects = cv.get("projects", [])
    # match_result is the dictionary RETURNED BY matcher.py's match_candidate_to_job()
    # e.g. {"match_score": 60.0, "matched_skills": [...], "missing_skills": [...], "recruiter_reasoning": "..."}
    matched_skills = match_result.get("matched_skills", [])
    missing_skills = match_result.get("missing_skills", [])
    match_score = match_result.get("match_score", None)
    # recruiter_reasoning is the matcher's ALREADY-COMPLETED analysis — which specific
    # projects matter, why, and how gaps should be framed. The email should be BUILT
    # FROM this existing analysis, not re-derive its own separate analysis from
    # scratch. This keeps the email and the internal match analysis consistent with
    # each other, and avoids paying for/running a second redundant analysis pass.
    recruiter_reasoning = match_result.get("recruiter_reasoning", "")
    job_title = jd.get("job_title", "the role")

    greeting_name = recruiter_name if recruiter_name else "there"

    prompt = f"""
    You are writing a cold outreach email from a job candidate to a recruiter. This
    is NOT a cover letter template and NOT a vague summary — it must read like someone
    who actually read the job description carefully and is showing precise, concrete
    proof of fit, project by project.

    A technical recruiter analysis has ALREADY BEEN COMPLETED on this candidate for
    this exact job (see RECRUITER ANALYSIS below). That analysis already identified
    which specific projects/repos matter, why they're relevant, and how gaps should
    be framed. Your job is NOT to redo this analysis from scratch — it is to turn
    the strongest, most specific points from that existing analysis into a compelling,
    well-formatted outreach email. Stay consistent with what that analysis concluded;
    do not contradict it or invent a different framing.

    RECRUITER ANALYSIS (already completed — use this as your foundation):
    {recruiter_reasoning if recruiter_reasoning else "No prior analysis provided — analyze the candidate data directly below instead."}

    STRUCTURE (no "Dear..." greeting line, but DO open with a brief human intro - see STEP 0):
    STEP 0 - OPEN LIKE AN ACTUAL PERSON, NOT A SPEC SHEET: Start with one short
    sentence that introduces the candidate as a person before any project talk -
    their name, that they're a student (using the education info provided) or
    their current status, and genuine interest in this specific role/company.
    Example shape only (do not copy wording): "My name is [Name], a Computer
    Science student at [Institution], and I'm excited about the [Job Title]
    opening because [one genuine, specific reason tied to the role]." Keep this
    to ONE sentence - it sets tone, it is not the pitch itself.

    STEP 1 - RANK BEFORE WRITING: Before drafting anything, determine which ONE
    candidate project is MOST relevant to THIS specific JD. Relevance means matching
    the JD's actual required tech stack and core responsibilities - NOT project
    complexity, NOT recency, NOT how impressive it sounds. This ranking must adapt
    fully to whatever the JD asks for: if the JD is a Python/AI/backend role, an
    AI or data pipeline project outranks a simpler frontend project even if the
    frontend project is newer or "bigger." If the JD is a frontend/web role, a
    project built with the JD's exact stack outranks a more complex AI project
    that uses unrelated technology. There is no fixed preferred category - the JD
    alone decides what "most relevant" means each time. Do not default to whichever
    project the candidate data lists first - actively compare each project's tech
    stack against the JD's tech stack and pick the closest match.

    STEP 1b - SOME PROJECTS ARE DUAL-RELEVANT, EMPHASIZE THE MATCHING FACET: several
    candidate projects combine multiple areas (e.g. a project with both a Python/
    FastAPI/LLM backend AND a React/TypeScript frontend). When such a project is
    chosen in Step 1, describe the FACET of it that matches the JD's emphasis, not
    the whole project generically. For a backend/AI-leaning JD, lead with the
    backend/AI/data-processing details of that project. For a frontend/web-leaning
    JD, lead with the frontend/UI/component details of that same project instead.
    Do not describe unrelated facets of the project just because they exist.

    STEP 2 - WRITE THE EMAIL, in this exact priority order (after the Step 0 intro):
    - Open directly with the ONE most relevant project (from Step 1), described
      using the matching facet (from Step 1b) if it's dual-relevant. Name it, state
      the relevant tech stack, and connect it to a specific responsibility from the
      JD. This is the primary focus of the email - roughly 60% of the content.
    - If, and only if, a SECOND project covers a JD requirement the first project
      didn't touch, mention it in 1-2 sentences maximum. Do not add a third CV
      project unless the JD has 3+ clearly distinct requirement areas.
    - GitHub gets exactly ONE short sentence, near the end, not a deep dive. If the
      candidate's GitHub data shows relevant repos not already covered above
      (especially other AI or side projects worth flagging), name 1-2 of them by
      name in that single sentence (e.g. "I've also built a few other AI-focused
      projects on GitHub, including X and Y, if useful context.") - do not explain
      what those repos do in detail, just name them.
    - If there's a relevant missing skill, address it in exactly one confident
      sentence explaining how existing experience transfers - specific about HOW.
    - End with one direct, low-friction call to action (e.g. a 15-minute call this week).

    BANNED PHRASES — do not use any of these or close variants: "could be valuable",
    "might fit", "I believe", "I am confident", "strong foundation", "quick learner",
    "eager to learn", "passionate about", "leverage", "synergy". Replace vague claims
    with specific technical facts.

    LENGTH: This is a real recruiter email, not a portfolio essay. STRICT CAP:
    150-190 words total for the body (slightly higher than a typical cold email
    specifically to make room for the Step 0 human intro sentence - do not use
    that extra room to add more project detail). This is non-negotiable - recruiters
    skim, and a long email gets ignored regardless of how relevant the content is.

    ATS-FRIENDLY FORMATTING - STRICT: Use ONLY plain ASCII punctuation. Plain
    hyphens (-), not en-dashes or em-dashes. Plain straight apostrophes ('), not
    curly/smart apostrophes. Plain straight quotes ("), not curly quotes. No bullet
    points, no markdown, no special Unicode characters of any kind. Write in normal
    conversational sentences a human would actually say out loud, not a dense
    compound-clause listing of technologies separated by semicolons - if a sentence
    has more than 2 technical terms crammed together, split it into two sentences.
    Plain, direct, first-person tone, ATS-friendly (no special formatting, no bullet
    points, no markdown) — confident because of specifics, not adjectives.

    Do NOT include a signature block, contact info, or sign-off name — added separately
    in code.

    CANDIDATE DATA (for reference/detail, in addition to the analysis above):
    Candidate name: {candidate_name or "the candidate"}
    Education: {json.dumps(education, indent=2) if education else "Not provided - omit education detail from the intro if genuinely unavailable, do not invent it"}
    Match score: {match_score}
    Matched skills: {matched_skills}
    Missing skills: {missing_skills}
    Real projects (name + description): {json.dumps(projects, indent=2)}
    GitHub profile (languages/themes/notable repos, if available): {json.dumps(github_summary, indent=2) if github_summary else "Not provided"}

    JOB CONTEXT (read this carefully — your job is to map specific candidate evidence
    to specific parts of this):
    {json.dumps(jd, indent=2)}

    Recruiter's name (use "there" naturally if unknown): {greeting_name}
    """

    body_response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[{"role": "user", "content": prompt}],
    )
    body = body_response.choices[0].message.content.strip()

    subject_prompt = f"""
    Write ONE short, specific email subject line (under 12 words) for a job
    application email. It should reference the role and hint at concrete proof,
    not generic enthusiasm. No quotation marks, no "Subject:" prefix, just the
    subject line text itself.

    Job title: {job_title}
    Top matched skills: {matched_skills[:3]}
    """

    subject_response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[{"role": "user", "content": subject_prompt}],
    )
    subject = subject_response.choices[0].message.content.strip()

    # Build the signature directly from real CV data (never AI-generated),
    # so contact details are always exact, never paraphrased or hallucinated.
    signature_lines = [contact.get("name", "")]
    if contact.get("phone"):
        signature_lines.append(contact["phone"])
    if contact.get("email"):
        signature_lines.append(contact["email"])
    if contact.get("github"):
        signature_lines.append(contact["github"])
    if contact.get("linkedin"):
        signature_lines.append(contact["linkedin"])

    signature = "\n".join(signature_lines)
    full_body = f"{body}\n\n{signature}"

    return {
        "subject": subject,
        "body": full_body,
    }


# --- STANDALONE TEST BLOCK ---
# Mirrors test_pipeline.py: parses a real CV, fetches real GitHub data, parses a
# real JD, runs the matcher, then drafts the email from real pipeline output —
# instead of hardcoded mock data, so this test reflects what actually happens
# end to end.
if __name__ == "__main__":
    cv_filename = "sample_cv.pdf"
    github_username = "TalalTariq1"
    sample_job_text = """
    Iyrix Tech is hiring a Full-Stack Developer Intern (Next.js) who's eager to learn
    how to build with AI tools like Claude Code, Cursor, and Codex.
    """

    if not os.path.exists(cv_filename):
        print(f"Drop a real PDF at '{cv_filename}' in this folder to run this test.")
    else:
        print("[1/4] Parsing CV...")
        raw_cv_text = extract_cv_text(cv_filename)
        cv_json = analyze_cv_text(raw_cv_text)

        print("[2/4] Fetching + summarizing GitHub profile...")
        raw_repos = fetch_github_repos(github_username)
        github_summary = summarize_github_profile(raw_repos)

        print("[3/4] Parsing job description...")
        jd_json = parse_job_description(sample_job_text)

        print("[4/4] Running matcher...")
        match_result = match_candidate_to_job(cv_json, github_summary, jd_json)

        print("\n[5/5] Drafting email...")
        email = draft_email(cv_json, jd_json, match_result, github_summary=github_summary)

        print("\n=================== SUBJECT ===================")
        print(email["subject"])
        print("\n=================== BODY ===================")
        print(email["body"])