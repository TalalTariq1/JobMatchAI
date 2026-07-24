import { useState } from "react";
import { Briefcase, CheckCircle2, AlertCircle } from "lucide-react";
import { parseJobDescription } from "../../services/api";
import LoadingSpinner from "../shared/LoadingSpinner";
import "./JobDescriptionInput.css";

export default function JobDescriptionInput({ onDataFetched }) {
  const [text, setText] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [parsed, setParsed] = useState(false);

  async function handleBlur() {
    if (!text.trim()) return;
    setLoading(true);
    setError("");
    setParsed(false);
    try {
      const result = await parseJobDescription(text);
      // Same quirk as the CV: the backend hands back a raw JSON string
      // from the LLM, so we parse it once, here.
      const parsedJdData = JSON.parse(result.jd_data);
      onDataFetched(parsedJdData);
      setParsed(true);
    } catch (err) {
      setError(err.message || "Could not parse this job description.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="card">
      <h3 className="card-title">
        <span className="card-icon-badge"><Briefcase size={16} /></span> Job Description
      </h3>
      <p className="card-subtext">
        Paste the full job posting - the AI will pull out the tech stack and key requirements.
      </p>
      <textarea
        className="jd-textarea"
        placeholder="Paste the job requirements here..."
        value={text}
        onChange={(e) => {
          setText(e.target.value);
          setParsed(false);
        }}
        onBlur={handleBlur}
      />
      {loading && <LoadingSpinner label="Analyzing job requirements..." />}
      {error && <p className="field-error"><AlertCircle size={15} /> {error}</p>}
      {parsed && !loading && !error && (
        <p className="field-success"><CheckCircle2 size={15} /> Job description analyzed</p>
      )}
    </div>
  );
}
