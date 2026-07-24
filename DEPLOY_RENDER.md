Render deployment checklist

1) Services to create on Render

- Backend (Python web service)
  - Root directory: `backend`
  - Environment: Python 3 (use the latest supported)
  - Build command: `pip install -r requirements.txt`
  - Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

- Frontend (Static Site)
  - Root directory: `frontend`
  - Build command: `npm install && npm run build`
  - Publish directory: `frontend/dist`

2) Environment variables / secrets to add to Render (Backend service)

- `GROQ_API_KEY` — your Groq API key
- `FIREBASE_SERVICE_ACCOUNT_JSON` — the service account JSON (base64 or raw) or upload file via Render dashboard if supported
- `GMAIL_CREDENTIALS_JSON` — Gmail client secrets JSON (if required)
- Any other keys (e.g. third-party tokens)

Notes:
- Do NOT commit any secrets to GitHub. Use Render's "Environment" or "Secrets" UI to add them.
- If you provide the Firebase JSON as an env var, update `firebase_client.py` to read it from the env var and write the JSON to `firebase-key.json` at startup (or decode base64). This keeps the repo clean.

3) Optional: Add a `render.yaml` manifest to declare both services centrally (Render supports this). If you prefer manual dashboard setup, skip it.

4) After deploying

- Rotate any keys that were previously exposed in commits (Firebase API key, service account, Gmail client secrets, Groq key). Treat them as compromised.
- Monitor logs on Render and fix any missing package/import errors by updating `backend/requirements.txt`.

5) Quick local run (backend):

```bash
cd backend
python -m pip install -r requirements.txt
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

6) Quick local run (frontend):

```bash
cd frontend
npm install
npm run dev
```

If you want, I can:
- add a `render.yaml` manifest for both services,
- update `firebase_client.py` to support reading the service account JSON from an env var (safer for Render), and
- commit these safe changes to the repo.
