import { useState } from "react";
import { motion } from "framer-motion";
import { Paperclip, Trash2, Send, Mail } from "lucide-react";
import { sendApplicationEmail } from "../../services/api";
import { useAuth } from "../../context/AuthContext";
import LoadingSpinner from "../shared/LoadingSpinner";
import "./EmailComposer.css";

// Styled to closely mirror Gmail's own compose window: To / Subject /
// body / attachment chip / Send button bottom-left. Subject and body
// start pre-filled from the AI draft but are fully editable text fields.
export default function EmailComposer({
  initialSubject,
  initialBody,
  attachmentFileName,
  attachmentPath,
  jobTitle,
  matchScore,
  matchedSkills,
  missingSkills,
  recruiterReasoning,
  onSent,
}) {
  const { getIdToken } = useAuth();
  const [recipient, setRecipient] = useState("");
  const [subject, setSubject] = useState(initialSubject);
  const [body, setBody] = useState(initialBody);
  const [sending, setSending] = useState(false);
  const [error, setError] = useState("");

  async function handleSend() {
    if (!recipient.trim()) {
      setError("Add a recipient email before sending.");
      return;
    }
    setSending(true);
    setError("");
    try {
      const idToken = await getIdToken();
      const result = await sendApplicationEmail(
        {
          recipient_email: recipient,
          subject,
          body,
          attachment_path: attachmentPath,
          job_title: jobTitle,
          match_score: matchScore,
          matched_skills: matchedSkills,
          missing_skills: missingSkills,
          recruiter_reasoning: recruiterReasoning,
        },
        idToken
      );
      onSent(result);
    } catch (err) {
      setError(err.message || "Could not send this email. Please try again.");
    } finally {
      setSending(false);
    }
  }

  return (
    <motion.div
      className="email-composer"
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      <div className="email-composer-header">
        <Mail size={16} /> <span>New Message</span>
      </div>

      <div className="email-composer-field">
        <label>To</label>
        <input
          type="email"
          value={recipient}
          onChange={(e) => setRecipient(e.target.value)}
          placeholder="recruiter@company.com"
        />
      </div>

      <div className="email-composer-field">
        <label>Subject</label>
        <input
          type="text"
          value={subject}
          onChange={(e) => setSubject(e.target.value)}
        />
      </div>

      <textarea
        className="email-composer-body"
        value={body}
        onChange={(e) => setBody(e.target.value)}
      />

      {attachmentFileName && (
        <div className="email-composer-attachment">
          <Paperclip size={14} /> {attachmentFileName}
        </div>
      )}

      {error && <p className="field-error email-composer-error">{error}</p>}

      <div className="email-composer-footer">
        <button className="email-send-button" onClick={handleSend} disabled={sending}>
          {sending ? "Sending..." : <>Send <Send size={15} /></>}
        </button>
        <span className="email-composer-icon" title="Attach file"><Paperclip size={17} /></span>
        <span className="email-composer-icon email-composer-icon-danger" title="Discard draft"><Trash2 size={17} /></span>
      </div>

      {sending && <LoadingSpinner label="Sending your application..." />}
    </motion.div>
  );
}
