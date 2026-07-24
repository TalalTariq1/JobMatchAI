import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { useAuth } from "../../context/AuthContext";
import { getUserHistory } from "../../services/api";
import LoadingSpinner from "../../components/shared/LoadingSpinner";
import "./HistoryPage.css";

export default function HistoryPage() {
  const { getIdToken } = useAuth();
  const [applications, setApplications] = useState([]);
  const [emails, setEmails] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadHistory() {
      try {
        const idToken = await getIdToken();
        const data = await getUserHistory(idToken);
        setApplications(data.applications || []);
        setEmails(data.emails || []);
      } catch (err) {
        setError("Could not load your history right now.");
      } finally {
        setLoading(false);
      }
    }
    loadHistory();
  }, [getIdToken]);

  function findEmailForApplication(applicationId) {
    return emails.find((email) => email.applicationId === applicationId);
  }

  if (loading) {
    return (
      <div className="history-page">
        <LoadingSpinner label="Loading your application history..." />
      </div>
    );
  }

  return (
    <div className="history-page">
      <h2 className="history-title">My History</h2>

      {error && <p className="field-error">{error}</p>}

      {!error && applications.length === 0 && (
        <p className="history-empty">
          No applications yet - once you send your first application, it'll show up here.
        </p>
      )}

      <div className="history-list">
        {applications.map((application, index) => {
          const linkedEmail = findEmailForApplication(application.id);
          return (
            <motion.div
              key={application.id}
              className="card history-item"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.05 }}
            >
              <div className="history-item-header">
                <h4>{application.jobTitle || "Untitled Role"}</h4>
                <span className="history-score-badge">
                  {application.matchScore}% match
                </span>
              </div>
              <div className="history-skills-row">
                {(application.matchedSkills || []).slice(0, 5).map((skill) => (
                  <span key={skill} className="skills-pill skills-pill-matched">
                    {skill}
                  </span>
                ))}
              </div>
              {linkedEmail && (
                <p className="history-email-subject">
                  Sent: <strong>{linkedEmail.subject}</strong>
                </p>
              )}
            </motion.div>
          );
        })}
      </div>
    </div>
  );
}
