# Project: AI Job Application Agent (name TBD — ideas: JobMatch AI, TailorMail, ApplyGenie)

## 1. One-liner
An AI agent that analyzes a user's CV and GitHub against a job description, drafts a
personalized outreach email highlighting the most relevant skills/projects, and sends it
to a recruiter (with human review before sending). Includes a history dashboard of past
applications and emails.

## 2. Why this project
Built as a portfolio/CV piece to demonstrate: LLM API integration, working with external
APIs (GitHub), full-stack build (React + Python backend), and thoughtful UX (human-in-the-loop
before any email is sent). Built with AI coding tools, but with a "understand every core
piece" rule — see Section 7.

## 3. Constraints (important — do not suggest paid tools)
- Zero budget. No paid APIs, no paid hosting, no paid tiers of anything.
- Backend must be Python (not Node/TypeScript).
- Frontend: React + Vite, plain JavaScript (no TypeScript), plain CSS (no Tailwind).
- Auth/DB: Firebase (Auth + Firestore) — chosen over Supabase because Supabase Edge
  Functions are TypeScript/Deno-only, and this project needs Python on the backend.
- NOTE: Firebase Cloud Functions Python support requires the Blaze (pay-as-you-go)
  billing plan to even deploy, though usage stays free under the quota for a project
  this size. If a truly zero-card setup is wanted instead, backend logic should be
  hosted on Render or PythonAnywhere (free tier, no card), with Firebase used only for
  Auth + Firestore. DECISION PENDING — confirm which path before building the backend
  hosting piece.

## 4. Final tech stack
- Frontend: React + Vite (plain JS), CSS Modules for styling
- Auth: Firebase Auth
- Database: Firestore
- Backend logic: Python — either Firebase Cloud Functions (2nd gen, Python, Blaze plan)
  OR FastAPI on Render (free, no card) — see Section 3 decision pending
- LLM: Gemini API (free tier) — NOT Claude API, NOT OpenAI, to keep cost at $0
- GitHub data: GitHub REST API (public data, no auth needed; use a personal access
  token for higher rate limits, still free)
- Email sending: Gmail API (OAuth, free, sends from the user's own Gmail account)
- Hosting: Firebase Hosting (frontend) — or Vercel if backend ends up on Render instead

## 5. Scope

### In scope for v1
- Upload CV (PDF)
- Enter GitHub username
- Paste job description as plain text (no URL scraping — too fragile for v1)
- Analysis: extract structured data from CV + GitHub + JD
- Match output: ranked list of relevant skills/projects with reasoning
- Draft email: LLM-generated, editable by user before sending
- Send email (Gmail API) with CV attached — ONLY after explicit user approval
- History dashboard: list of past applications + the email sent for each, using Firestore

### Explicitly out of scope for v1 (future work / talking points)
- Scraping job postings from URLs
- Automated follow-ups / application status tracking beyond manual history log
- Bulk / multi-recipient sending
- Cover letter generation (different beast — v2 candidate)

## 6. Architecture

```
Frontend (React + Vite, plain JS)
   |
   |  Upload CV, paste JD, enter GitHub username
   v
Backend (Python)
   /parse-cv        -> extract text from PDF -> Gemini -> structured JSON
                        (skills, experience, projects)
   /fetch-github    -> GitHub REST API -> repos, languages, README summaries
   /match           -> CV JSON + GitHub JSON + JD -> Gemini -> ranked matches + reasoning
                        (BUILD THIS ONE BY HAND — see Section 7)
   /draft-email     -> matches + JD + recruiter context -> Gemini -> draft email text
   /send-email      -> Gmail API, attach CV, send only on explicit user confirm
   |
   v
Firestore
   users/{userId}/applications/{applicationId}
       { jobTitle, company, jobDescription, matchedSkills[], matchScore, createdAt }
   users/{userId}/emails/{emailId}
       { applicationId, recruiterEmail, subject, body, status: "draft"|"sent", sentAt }
```

## 7. Learning approach while vibecoding
Goal: end up with a project that looks impressive AND that the builder can explain
line-by-line in an interview. Rules being followed:
1. Design each piece in plain English before asking AI to write code for it.
2. Ask AI for one function/file at a time, not the whole app at once.
3. Read every line before running it; predict what it does first, then check.
4. When something breaks, ask "why did this break" before asking for the fix.
5. The `/match` function (matching/scoring logic) is being built by hand, using AI only
   as a Q&A reference — this is the "smart" part of the app and the one most likely to
   come up in interviews.
6. Keep a build log (see Section 9) — five minutes per session, what was built, what
   broke, why, what was learned.

## 8. Build order
1. Firebase project setup (Auth + Firestore) + decide backend hosting path (Section 3)
2. Vite React scaffold, no Tailwind/TypeScript
3. CV parser: PDF upload -> text extraction -> Gemini -> structured JSON
4. GitHub fetcher: username -> repos/languages/README summaries
5. JD parser: plain text -> structured requirements
6. Matching logic (built by hand) -> ranked matches + reasoning
7. Email draft generator (Gemini)
8. Frontend wizard UI: Upload -> Review Analysis -> Edit Email -> Confirm & Send
9. Gmail send integration with review-before-send gate
10. History dashboard (Firestore-backed): past applications + associated emails
11. Polish: loading states, error handling, empty states

## 9. Build log
(Add an entry each session. Example format below — replace with real entries as you go.)

- [Date] — Built: ___. Broke: ___. Why it broke: ___. Learned: ___.

## 10. Status as of this doc
Nothing built yet. Next immediate step: resolve the Section 3 hosting decision
(Firebase Blaze vs Render split), then scaffold the Firebase project and Vite frontend,
then build the CV parser first.

## 11. Note for any LLM picking this up
The user is building this primarily as a CV/portfolio project to impress recruiters,
while genuinely learning Python/full-stack skills. They are also doing separate freelance
work (data/tech gigs) in parallel. Keep guidance zero-cost, Python-backend, plain
JS/CSS frontend, and continue enforcing the "understand what you build" approach from
Section 7 — do not just dump full working apps without explanation.
