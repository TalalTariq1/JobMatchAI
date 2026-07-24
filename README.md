# JobMatch AI

An AI-powered job application assistant that analyzes a candidate's CV and
GitHub profile against a job description, calculates a real skill-match score,
and drafts a personalized, ATS-friendly outreach email — ready to send
directly through the user's own Gmail account.

**Live demo:** https://job-match-ai-lilac.vercel.app

> **Note on Gmail sending:** this app is not yet verified by Google, so live
> Gmail sending is currently limited to approved test accounts under Google's
> OAuth policy for unverified apps. Every other feature (CV parsing, GitHub
> analysis, JD parsing, matching, and email drafting) works for anyone, no
> restrictions. If you'd like to test the full Gmail-sending flow, reach out
> and I'll add your Google account as a test user.

---

## What it does

1. **Paste a GitHub profile** — pulls every public repo and has an LLM
   summarize languages, project themes, and notable work.
2. **Upload a CV (PDF)** — extracts contact info, education, skills, and
   projects into structured data.
3. **Paste a job description** — extracts the job title, required skills,
   and tech stack.
4. **Analyze Match** — a hybrid scoring engine combines deterministic
   keyword/synonym matching with an LLM reconciliation pass (to catch
   generic JD phrasing a keyword matcher alone would miss), producing a
   real percentage score, matched/missing skill lists, and a detailed
   written analysis.
5. **Draft Application Email** — an LLM ranks the candidate's own projects
   by actual relevance to *this specific* job description (not just
   whichever project is listed first), writes a concise, ATS-friendly,
   human-sounding email grounded in that ranking, and includes the CV as
   an attachment.
6. **Send** — sends the email through the user's own connected Gmail
   account via OAuth2, and saves the application + email to a personal
   history log.

---

## Tech Stack

### Frontend
- **React 18 + Vite** (plain JavaScript, no TypeScript)
- **Plain CSS** — no Tailwind, custom design system (CSS variables, shared
  utility classes)
- **React Router** — client-side routing with protected routes
- **Framer Motion** — animated match-score ring, staggered skill pills,
  page transitions
- **lucide-react** — icon set
- **Firebase Auth (client SDK)** — email/password and Google sign-in
- Deployed on **Vercel**

### Backend
- **Python + FastAPI** — REST API, auto-generated interactive docs at `/docs`
- **Groq API** (`openai/gpt-oss-120b`) — CV parsing, GitHub summarization,
  JD parsing, match reasoning, and email drafting
- **pypdf** — CV text extraction
- **GitHub REST API** — public repo data
- **Firebase Admin SDK + Firestore** — user data, application/email history
- **Google OAuth2 (`google-auth-oauthlib`) + Gmail API** — per-user,
  multi-account Gmail sending with automatic token refresh
- Deployed on **Render**

### Matching Engine (the core logic)
- Deterministic skill-overlap scoring with a hand-built synonym/alias layer
  (e.g. recognizing "MongoDB" satisfies a JD asking for "Database Design")
- An LLM reconciliation pass that reviews any still-unmatched requirements
  against the candidate's full profile, catching generic phrasing a plain
  keyword matcher structurally cannot
- Score is fully auditable — every matched/missing skill traces back to a
  specific piece of evidence, not a black-box guess

---

## Architecture

```
frontend/ (React + Vite)
  └── calls → backend/ (FastAPI)
                ├── /parse-cv        → pypdf + Groq
                ├── /fetch-github    → GitHub REST API + Groq
                ├── /parse-jd        → Groq
                ├── /match           → deterministic scoring + Groq reconciliation + Groq reasoning
                ├── /draft-email     → Groq
                ├── /connect-gmail, /oauth2callback → Google OAuth2
                ├── /send-email      → Gmail API (protected: Firebase ID token required)
                └── /history         → Firestore (protected: Firebase ID token required)

Firebase Auth   → who's logged in
Firestore       → per-user application history + Gmail tokens
```

---

## Running locally

**Backend**
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn main:app --reload
```

**Frontend**
```bash
cd frontend
npm install
npm run dev
```

You'll need your own `.env` (backend) with a `GROQ_API_KEY`, your own
Firebase project (`firebase-key.json`), and your own Google Cloud OAuth
credentials (`gmail-web-credentials.json`) — see `.env.example` for the full
list of required variables.

---

## Known limitations / roadmap

- Gmail sending is gated behind Google's unverified-app test-user limit
  until full OAuth verification is completed
- Firestore security rules are currently in test mode (open access) —
  planned hardening before wider public use
- Company-name extraction from job descriptions not yet implemented
