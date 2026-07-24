import { useState } from "react";
import { GitBranch, CheckCircle2, AlertCircle } from "lucide-react";
import { fetchGithub } from "../../services/api";
import LoadingSpinner from "../shared/LoadingSpinner";
import "./GitHubProfileInput.css";

export default function GitHubProfileInput({ onDataFetched }) {
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [fetched, setFetched] = useState(false);

  function extractUsername(value) {
    const trimmed = value.trim();
    if (trimmed.includes("github.com")) {
      return trimmed.replace(/\/$/, "").split("/").pop();
    }
    return trimmed;
  }

  async function handleFetch() {
    if (!input.trim()) return;
    setLoading(true);
    setError("");
    try {
      const username = extractUsername(input);
      const result = await fetchGithub(username);
      onDataFetched(result.github_data);
      setFetched(true);
    } catch (err) {
      setError(err.message || "Could not fetch this GitHub profile.");
      setFetched(false);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="card">
      <h3 className="card-title">
        <span className="card-icon-badge"><GitBranch size={16} /></span> GitHub Profile
      </h3>
      <p className="card-subtext">
        Paste your GitHub username or profile URL to load your public project data.
      </p>
      <label className="field-label">Profile URL or username</label>
      <div className="github-input-row">
        <input
          type="text"
          className="text-input"
          placeholder="github.com/username"
          value={input}
          onChange={(e) => {
            setInput(e.target.value);
            setFetched(false);
          }}
          onKeyDown={(e) => e.key === "Enter" && handleFetch()}
        />
        <button className="primary-button github-fetch-button" onClick={handleFetch} disabled={loading}>
          Fetch GitHub
        </button>
      </div>
      {loading && <LoadingSpinner label="Fetching GitHub profile..." />}
      {error && <p className="field-error"><AlertCircle size={15} /> {error}</p>}
      {fetched && !loading && (
        <p className="field-success"><CheckCircle2 size={15} /> GitHub profile loaded</p>
      )}
    </div>
  );
}
