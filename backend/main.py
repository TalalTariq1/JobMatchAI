import shutil
from fastapi import FastAPI, UploadFile, File, Header, HTTPException, Depends
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from google_auth_oauthlib.flow import Flow
from firebase_admin import auth

from cv_parser import extract_cv_text, analyze_cv_text
from github_fetcher import fetch_github_repos, summarize_github_profile
from jd_parser import parse_job_description
from matcher import match_candidate_to_job
from email_drafter import draft_email
from email_sender import save_gmail_token, send_email
from history import save_application, save_sent_email, get_user_history
import firebase_client  # just importing this runs firebase_admin.initialize_app once
import os
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Configure CORS and OAuth redirect using environment variables so the
# backend works both locally and in production without changing code.
FRONTEND_ORIGINS = os.environ.get(
    "FRONTEND_ORIGINS",
    "http://localhost:5173,http://127.0.0.1:5173",
)
FRONTEND_ORIGINS_LIST = [o.strip() for o in FRONTEND_ORIGINS.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=FRONTEND_ORIGINS_LIST,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

GMAIL_SCOPES = ["https://www.googleapis.com/auth/gmail.send"]
# Backend base URL is used for OAuth redirect construction. In production
# set BACKEND_BASE_URL to your Render URL (e.g. https://jobmatchai-r9zk.onrender.com)
BACKEND_BASE_URL = os.environ.get("BACKEND_BASE_URL", "http://localhost:8000").rstrip("/")
REDIRECT_URI = f"{BACKEND_BASE_URL}/oauth2callback"


def verify_user(authorization: str = Header(...)):
    """
    This is the FastAPI equivalent of Express middleware. It runs BEFORE
    any endpoint that depends on it. It expects the request to include a
    header like: Authorization: Bearer <idToken>

    It checks that idToken is real and currently valid with Firebase, and
    returns the real, permanent user ID (the 'localId' from your curl test)
    if so. If the token is missing, fake, or expired, it stops the request
    immediately with a 401 error — the actual endpoint code never runs.
    """
    token = authorization.replace("Bearer ", "")
    try:
        decoded_token = auth.verify_id_token(token)
        return decoded_token["uid"]
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired login token")


@app.get("/")
def read_root():
    return {"message": "Job agent backend is running"}


@app.post("/parse-cv")
async def parse_cv(file: UploadFile = File(...)):
    """
    Receives an uploaded CV PDF, saves it temporarily, runs it through
    extract_cv_text and analyze_cv_text, and returns the structured JSON.
    """
    temp_path = f"temp_{file.filename}"
    with open(temp_path, "wb") as temp_file:
        shutil.copyfileobj(file.file, temp_file)

    raw_text = extract_cv_text(temp_path)
    structured_json = analyze_cv_text(raw_text)

    return {"cv_data": structured_json}


class GitHubRequest(BaseModel):
    username: str


@app.post("/fetch-github")
def fetch_github(request: GitHubRequest):
    """
    Receives a GitHub username, fetches their public repos, and returns
    a structured summary (top languages, project themes, notable projects).
    """
    repos = fetch_github_repos(request.username)
    summary = summarize_github_profile(repos)
    return {"github_data": summary}


class JDRequest(BaseModel):
    job_text: str


@app.post("/parse-jd")
def parse_jd(request: JDRequest):
    """
    Receives raw job description text and returns structured requirements
    (job title, key skills, tech stack).
    """
    jd_json = parse_job_description(request.job_text)
    return {"jd_data": jd_json}


class MatchRequest(BaseModel):
    cv_json: dict
    github_summary: dict
    jd_json: dict


@app.post("/match")
def match(request: MatchRequest):
    """
    Receives the CV data, GitHub summary, and JD data, and returns the
    match score, matched/missing skills, and AI-generated reasoning.
    """
    result = match_candidate_to_job(
        request.cv_json,
        request.github_summary,
        request.jd_json,
    )
    return {"match_data": result}


class EmailRequest(BaseModel):
    cv_json: dict
    jd_json: dict
    match_result: dict
    github_summary: dict | None = None


@app.post("/draft-email")
def create_email(request: EmailRequest):
    """
    Receives CV data, JD data, and the match result, and returns a drafted
    outreach email (subject + body).
    """
    email = draft_email(
        request.cv_json,
        request.jd_json,
        request.match_result,
        github_summary=request.github_summary,
    )
    return {"email_data": email}


@app.get("/connect-gmail")
def connect_gmail(user_id: str):
    """
    Starts the Gmail permission flow for a specific user. Redirects their
    browser to Google's real login + consent screen. We attach their
    user_id as the 'state' parameter, so we know whose token we're saving
    once they come back.
    """
    flow = Flow.from_client_secrets_file(
        "gmail-web-credentials.json",
        scopes=GMAIL_SCOPES,
        redirect_uri=REDIRECT_URI,
        autogenerate_code_verifier=False,
    )
    authorization_url, _ = flow.authorization_url(
        access_type="offline",       # "offline" is what gives us a refresh token, not just a short-lived one
        include_granted_scopes="true",
        prompt="consent",            # forces Google to always show the consent screen, ensuring we get a refresh token every time
        state=user_id,
    )
    return RedirectResponse(authorization_url)


@app.get("/oauth2callback")
def oauth2callback(code: str, state: str):
    """
    Google redirects the user's browser back here after they click Allow.
    'code' is a one-time proof we exchange for a real token. 'state' is the
    user_id we attached earlier, now handed back to us unchanged, so we
    know exactly whose token this is.
    """
    flow = Flow.from_client_secrets_file(
        "gmail-web-credentials.json",
        scopes=GMAIL_SCOPES,
        redirect_uri=REDIRECT_URI,
        autogenerate_code_verifier=False,
    )
    flow.fetch_token(code=code)

    user_id = state
    save_gmail_token(user_id, flow.credentials)

    return {"message": f"Gmail successfully connected for user {user_id}!"}


class SendEmailRequest(BaseModel):
    recipient_email: str
    subject: str
    body: str
    attachment_path: str
    job_title: str
    match_score: float
    matched_skills: list[str]
    missing_skills: list[str]
    recruiter_reasoning: str


@app.post("/send-email")
def send_application_email(request: SendEmailRequest, user_id: str = Depends(verify_user)):
    """
    Sends the actual email through the user's connected Gmail account,
    then saves a record of this application and the sent email into
    Firestore, so it shows up in the user's history.

    user_id no longer comes from the request body — it comes from
    Depends(verify_user), which only runs this function at all if the
    request included a real, valid login token. This is what actually
    stops someone from sending email pretending to be a different user.
    """
    send_email(
        user_id=user_id,
        to=request.recipient_email,
        subject=request.subject,
        body_text=request.body,
        attachment_path=request.attachment_path,
    )

    application_id = save_application(user_id, {
        "jobTitle": request.job_title,
        "matchScore": request.match_score,
        "matchedSkills": request.matched_skills,
        "missingSkills": request.missing_skills,
        "recruiterReasoning": request.recruiter_reasoning,
    })

    email_id = save_sent_email(user_id, application_id, {
        "subject": request.subject,
        "body": request.body,
        "status": "sent",
    })

    return {
        "message": "Email sent and saved to history successfully!",
        "application_id": application_id,
        "email_id": email_id,
    }


@app.get("/history")
def get_history(user_id: str = Depends(verify_user)):
    """
    Returns every past application and sent email for the currently
    logged-in user, protected the same way as /send-email - only a real,
    valid login token gets past Depends(verify_user).
    """
    return get_user_history(user_id)


@app.get("/gmail-status")
def gmail_status(user_id: str = Depends(verify_user)):
    """
    Checks whether the currently logged-in user has already connected
    Gmail (i.e. has a saved token in Firestore), without needing to
    actually load or use that token. The frontend calls this to decide
    whether to show 'Connect Gmail' or a 'Connected' confirmation.
    """
    doc = firebase_client.db.collection("users").document(user_id).get()
    connected = doc.exists and bool(doc.to_dict().get("gmailToken"))
    return {"connected": connected}