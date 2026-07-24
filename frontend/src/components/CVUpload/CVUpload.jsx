import { useState, useRef } from "react";
import { FileText, UploadCloud, CheckCircle2, AlertCircle } from "lucide-react";
import { parseCV } from "../../services/api";
import LoadingSpinner from "../shared/LoadingSpinner";
import "./CVUpload.css";

export default function CVUpload({ onDataFetched }) {
  const [fileName, setFileName] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [dragOver, setDragOver] = useState(false);
  const fileInputRef = useRef(null);

  async function handleFile(file) {
    if (!file) return;
    setFileName(file.name);
    setLoading(true);
    setError("");
    try {
      const result = await parseCV(file);
      const parsedCvData = JSON.parse(result.cv_data);
      onDataFetched(parsedCvData, file.name);
    } catch (err) {
      setError(err.message || "Could not parse this CV.");
    } finally {
      setLoading(false);
    }
  }

  function handleDrop(e) {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer.files?.[0];
    handleFile(file);
  }

  return (
    <div className="card">
      <h3 className="card-title">
        <span className="card-icon-badge"><FileText size={16} /></span> Resume Upload
      </h3>
      <p className="card-subtext">
        Upload your PDF resume and the AI will extract your experience and skills.
      </p>
      <div
        className={`cv-dropzone ${dragOver ? "cv-dropzone-active" : ""}`}
        onDragOver={(e) => {
          e.preventDefault();
          setDragOver(true);
        }}
        onDragLeave={() => setDragOver(false)}
        onDrop={handleDrop}
      >
        <input
          type="file"
          accept=".pdf"
          ref={fileInputRef}
          className="cv-hidden-input"
          onChange={(e) => handleFile(e.target.files?.[0])}
        />
        <span className="cv-upload-icon"><UploadCloud size={26} /></span>
        {fileName ? (
          <p>
            Selected: <strong>{fileName}</strong>
          </p>
        ) : (
          <p>Drag CV here, or use the button below</p>
        )}
        <span className="cv-hint">PDF only, up to 10MB</span>
      </div>

      <div className="cv-actions-row">
        <button className="secondary-button" onClick={() => fileInputRef.current?.click()}>
          Choose Resume
        </button>
        {loading && <LoadingSpinner label="Reading and analyzing your CV..." />}
        {error && <p className="field-error"><AlertCircle size={15} /> {error}</p>}
        {fileName && !loading && !error && (
          <p className="field-success"><CheckCircle2 size={15} /> Resume parsed successfully!</p>
        )}
      </div>
    </div>
  );
}
