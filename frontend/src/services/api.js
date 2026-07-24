// This file is the ONLY place in the whole app that talks to the backend.
// Every component imports functions from here instead of calling fetch()
// directly. This means: if the backend URL changes, or how we send auth
// tokens changes, there is exactly one file to update, not fifteen.

const BASE_URL = (import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000").replace(/\/$/, "");

// A small shared helper so every function below doesn't repeat the same
// "check if the response failed" logic.
async function handleResponse(response) {
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `Request failed (${response.status})`);
  }
  return response.json();
}

export async function parseCV(file) {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${BASE_URL}/parse-cv`, {
    method: "POST",
    body: formData,
  });
  return handleResponse(response);
}

export async function fetchGithub(username) {
  const response = await fetch(`${BASE_URL}/fetch-github`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username }),
  });
  return handleResponse(response);
}

export async function parseJobDescription(jobText) {
  const response = await fetch(`${BASE_URL}/parse-jd`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ job_text: jobText }),
  });
  return handleResponse(response);
}

export async function matchCandidate(cvJson, githubSummary, jdJson) {
  const response = await fetch(`${BASE_URL}/match`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      cv_json: cvJson,
      github_summary: githubSummary,
      jd_json: jdJson,
    }),
  });
  return handleResponse(response);
}

export async function draftEmail(cvJson, jdJson, matchResult, githubSummary) {
  const response = await fetch(`${BASE_URL}/draft-email`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      cv_json: cvJson,
      jd_json: jdJson,
      match_result: matchResult,
      github_summary: githubSummary,
    }),
  });
  return handleResponse(response);
}

// This one is different from the others: it doesn't return data, it
// navigates the whole browser away to Google's consent screen. See
// GmailConnectButton usage in MainAppPage for how this is used.
export function getConnectGmailUrl(userId) {
  return `${BASE_URL}/connect-gmail?user_id=${encodeURIComponent(userId)}`;
}

// This is the one sensitive action - it actually sends a real email and
// saves history, so it needs a real login token attached. idToken is
// fetched fresh from AuthContext right before calling this.
export async function sendApplicationEmail(payload, idToken) {
  const response = await fetch(`${BASE_URL}/send-email`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${idToken}`,
    },
    body: JSON.stringify(payload),
  });
  return handleResponse(response);
}

// NOTE: the backend does not have a GET /history endpoint yet - this is
// a small, quick addition still needed on the Python side (main.py),
// mirroring the same Depends(verify_user) pattern as /send-email, calling
// history.py's get_user_history(user_id). Wire this up once that exists.
export async function getUserHistory(idToken) {
  const response = await fetch(`${BASE_URL}/history`, {
    method: "GET",
    headers: {
      Authorization: `Bearer ${idToken}`,
    },
  });
  return handleResponse(response);
}

// Checks whether the current user has already connected Gmail, so the UI
// can show a real "Connected" state instead of always showing the button.
export async function checkGmailStatus(idToken) {
  const response = await fetch(`${BASE_URL}/gmail-status`, {
    method: "GET",
    headers: {
      Authorization: `Bearer ${idToken}`,
    },
  });
  return handleResponse(response);
}