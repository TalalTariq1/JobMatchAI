import json
# Import your modules
from cv_parser import extract_cv_text, analyze_cv_text
from github_fetcher import fetch_github_repos, summarize_github_profile
from jd_parser import parse_job_description  # adjust name if yours is slightly different
from matcher import match_candidate_to_job
from email_drafter import draft_email

def run_real_test(cv_filename="sample_cv.pdf", github_username="TalalTariq1", job_text=None):
    print("🚀 Starting Live Pipeline Test...\n")
    
    # 1. PARSE YOUR ACTUAL CV
    # Make sure you have your CV pdf inside the backend folder or provide the correct path!
    print(f"[1/5] Parsing CV: {cv_filename}...")
    try:
        raw_cv_text = extract_cv_text(cv_filename)
        cv_json = analyze_cv_text(raw_cv_text)
        print("✅ CV parsed successfully.")
    except Exception as e:
        print(f"❌ Error parsing CV: {e}")
        return

    # 2. FETCH AND SUMMARIZE YOUR LIVE GITHUB DATA
    print(f"\n[2/5] Fetching live GitHub data for user: {github_username}...")
    try:
        # Get the raw list of repositories from GitHub
        raw_repos = fetch_github_repos(github_username)

        print("📊 Summarizing GitHub profile using LLM...")
        # Pass the list into your secondary function to get the correct dictionary format!
        github_summary = summarize_github_profile(raw_repos)

        print("✅ GitHub profile summarized successfully.")
    except Exception as e:
        print(f"❌ Error fetching/summarizing GitHub data: {e}")
        return
    # 3. USE THE PROVIDED JOB DESCRIPTION, OR FALL BACK TO A DEFAULT SAMPLE
    print("\n[3/5] Parsing Job Description...")
    if job_text is None:
        job_text = """
    MERN Stack Developer Intern

Company: PHPTRAVELS
Job Type: Internship (Paid)
Location: On-site
Duration: 3 Months (Leading to Full-Time Opportunity based on Performance)

About PHPTRAVELS

PHPTRAVELS is a travel technology company providing innovative solutions for travel agencies, tour operators, hotels, and travel businesses worldwide. We are looking for a passionate MERN Stack Developer Intern who is eager to learn, build real-world applications, and grow with our development team.

Responsibilities

Assist in developing web applications using the MERN Stack (MongoDB, Express.js, React.js, Node.js).
Build responsive and user-friendly interfaces using React.js.
Develop and maintain REST APIs with Node.js and Express.js.
Work with MongoDB databases and perform CRUD operations.
Debug, test, and optimize application performance.
Collaborate with designers, developers, and product managers.
Participate in code reviews and team meetings.
Learn and implement modern development best practices.
Requirements

Basic understanding of JavaScript (ES6+).
Familiarity with React.js, Node.js, Express.js, and MongoDB.
Understanding of HTML5, CSS3, and responsive design.
Knowledge of Git/GitHub is a plus.
Understanding of REST APIs.
Strong problem-solving and analytical skills.
Eagerness to learn and work in a collaborative environment.
Final-year students or fresh graduates are encouraged to apply.
Preferred Skills

Experience with Tailwind CSS or Bootstrap.
Basic knowledge of Redux or Context API.
Familiarity with JWT Authentication.
Understanding of deployment and hosting is a plus.
What You'll Gain

Hands-on experience working on live products.
Mentorship from experienced developers.
Exposure to modern development workflows.
Opportunity for a full-time position based on performance.
Professional and collaborative work environment.
Job Type

Paid Internship
On-site
Apply now and start your software development journey with PHPTRAVELS!

Pay: Rs15,000.00 - Rs20,000.00 per month

Work Location: In person
    """
    try:
        jd_json = parse_job_description(job_text)
        print("✅ Job Description parsed successfully.")
    except Exception as e:
        print(f"❌ Error parsing Job Description: {e}")
        return

    # 4. RUN THE MATCHER CORE
    print("\n[4/5] Orchestrating Matcher Engine...")
    try:
        analysis_result = match_candidate_to_job(cv_json, github_summary, jd_json)
        
        print("\n=================== LIVE PIPELINE OUTPUT ===================")
        print(f"Calculated Score: {analysis_result['match_score']}%")
        print(f"Matched Stack:    {analysis_result['matched_skills']}")
        print(f"Missing Stack:    {analysis_result['missing_skills']}")
        print("------------------------------------------------------------")
        print("AI Generated Recruiter Reasoning:")
        print(analysis_result['recruiter_reasoning'])
        print("============================================================")
        
    except Exception as e:
        print(f"❌ Error during matching phase: {e}")
        return

    # 5. DRAFT THE OUTREACH EMAIL
    print("\n[5/5] Drafting outreach email...")
    try:
        email = draft_email(cv_json, jd_json, analysis_result, github_summary=github_summary)

        print("\n=================== DRAFTED EMAIL ===================")
        print(f"Subject: {email['subject']}")
        print("\nBody:")
        print(email['body'])
        print("=======================================================")

    except Exception as e:
        print(f"❌ Error during email drafting: {e}")

if __name__ == "__main__":
    # Default run — uses sample_cv.pdf, TalalTariq1, and the built-in sample JD.
    run_real_test()

    # To test with a DIFFERENT job description, CV, or GitHub username, call it
    # with your own values instead, e.g.:
    #
    # run_real_test(
    #     cv_filename="my_other_cv.pdf",
    #     github_username="someoneelse",
    #     job_text="Paste a different job description here...",
    # )