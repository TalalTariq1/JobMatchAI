import { useState, useEffect, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Mail, CheckCircle2, BarChart3, PenSquare } from "lucide-react";
import { useAuth } from "../../context/AuthContext";
import {
  matchCandidate,
  draftEmail,
  getConnectGmailUrl,
  checkGmailStatus,
} from "../../services/api";
import GitHubProfileInput from "../../components/GitHubProfileInput/GitHubProfileInput";
import CVUpload from "../../components/CVUpload/CVUpload";
import JobDescriptionInput from "../../components/JobDescriptionInput/JobDescriptionInput";
import MatchProgressWheel from "../../components/MatchProgressWheel/MatchProgressWheel";
import SkillsList from "../../components/SkillsList/SkillsList";
import AIDetailedAnalysis from "../../components/AIDetailedAnalysis/AIDetailedAnalysis";
import EmailComposer from "../../components/EmailComposer/EmailComposer";
import LoadingSpinner from "../../components/shared/LoadingSpinner";
import "./MainAppPage.css";

export default function MainAppPage() {
  const { currentUser, getIdToken } = useAuth();

  const [githubData, setGithubData] = useState(null);
  const [cvData, setCvData] = useState(null);
  const [cvFileName, setCvFileName] = useState("");
  const [jdData, setJdData] = useState(null);

  const [matching, setMatching] = useState(false);
  const [matchResult, setMatchResult] = useState(null);
  const [matchError, setMatchError] = useState("");

  const [drafting, setDrafting] = useState(false);
  const [emailData, setEmailData] = useState(null);
  const [draftError, setDraftError] = useState("");

  const [sentConfirmation, setSentConfirmation] = useState(null);

  const [gmailConnected, setGmailConnected] = useState(false);
  const [checkingGmail, setCheckingGmail] = useState(true);

  const canAnalyze = githubData && cvData && jdData && !matching;

  // Checks the real connection status from the backend - not a guess,
  // an actual look at whether a token is saved for this user in Firestore.
  const refreshGmailStatus = useCallback(async () => {
    try {
      const idToken = await getIdToken();
      const status = await checkGmailStatus(idToken);
      setGmailConnected(status.connected);
    } catch (err) {
      setGmailConnected(false);
    } finally {
      setCheckingGmail(false);
    }
  }, [getIdToken]);

  useEffect(() => {
    refreshGmailStatus();

    // Connecting Gmail happens in a separate tab (Google's consent
    // screen), so there's no direct callback into this page when it's
    // done. Re-checking status whenever this tab regains focus is a
    // reliable, simple way to pick up the change once the user comes back.
    window.addEventListener("focus", refreshGmailStatus);
    return () => window.removeEventListener("focus", refreshGmailStatus);
  }, [refreshGmailStatus]);

  async function handleAnalyze() {
    setMatching(true);
    setMatchError("");
    setMatchResult(null);
    setEmailData(null);
    try {
      const result = await matchCandidate(cvData, githubData, jdData);
      setMatchResult(result.match_data);
    } catch (err) {
      setMatchError(err.message || "Could not analyze this match. Please try again.");
    } finally {
      setMatching(false);
    }
  }

  async function handleDraftEmail() {
    setDrafting(true);
    setDraftError("");
    try {
      const result = await draftEmail(cvData, jdData, matchResult, githubData);
      setEmailData(result.email_data);
    } catch (err) {
      setDraftError(err.message || "Could not draft an email. Please try again.");
    } finally {
      setDrafting(false);
    }
  }

  function handleConnectGmail() {
    window.open(getConnectGmailUrl(currentUser.uid), "_blank", "noopener,noreferrer");
  }

  return (
    <div className="main-app-page">
      <div className="gmail-connect-banner card">
        <div className="gmail-connect-banner-icon">
          <Mail size={16} />
        </div>
        <p className="gmail-connect-banner-text">
          <strong>Gmail Integration Notice</strong>
          <br />
          You can explore and test <strong>all features of this application</strong> without any restrictions. The only feature that is currently unavailable to the general public is <strong>sending emails through Gmail</strong>.
          <br />
          <br />
          This limitation exists because the application is currently using <strong>Google OAuth in testing mode</strong> and has <strong>not yet completed Google's verification process</strong>. As a result, only approved <strong>Google OAuth test users</strong> are allowed to connect their Gmail accounts and use the email-sending feature.
          <br />
          <br />
          If you'd like to test the complete Gmail integration and email workflow, please contact me through <strong>GitHub</strong>. I'll be happy to add your Google account as a test user so you can experience the feature exactly as intended.
        </p>
      </div>

      <div className="gmail-connect-card card">
        <div className="gmail-connect-label">
          <Mail size={17} />
          <span>Connect your Gmail to send applications directly from this app.</span>
        </div>
        {checkingGmail ? (
          <span className="gmail-status-checking">Checking...</span>
        ) : gmailConnected ? (
          <span className="gmail-connected-badge">
            <CheckCircle2 size={15} /> Connected
          </span>
        ) : (
          <button className="secondary-button" onClick={handleConnectGmail}>
            Connect Gmail
          </button>
        )}
      </div>

      <GitHubProfileInput onDataFetched={setGithubData} />
      <CVUpload
        onDataFetched={(data, fileName) => {
          setCvData(data);
          setCvFileName(fileName);
        }}
      />
      <JobDescriptionInput onDataFetched={setJdData} />

      <div className="analyze-button-row">
        <button
          className="primary-button analyze-button"
          onClick={handleAnalyze}
          disabled={!canAnalyze}
        >
          <BarChart3 size={17} /> Analyze Match
        </button>
      </div>

      {matching && <LoadingSpinner label="Analyzing your fit for this role..." />}
      {matchError && <p className="field-error">{matchError}</p>}

      <AnimatePresence>
        {matchResult && !matching && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.35 }}
            className="match-results-section"
          >
            <div className="match-results-grid">
              <div className="card">
                <MatchProgressWheel score={matchResult.match_score} />
              </div>
              <SkillsList
                title="Matched Skills"
                skills={matchResult.matched_skills}
                type="matched"
              />
              <SkillsList
                title="Missing Skills"
                skills={matchResult.missing_skills}
                type="missing"
              />
            </div>

            <AIDetailedAnalysis reasoning={matchResult.recruiter_reasoning} />

            {!emailData && (
              <div className="draft-email-button-row">
                <button
                  className="secondary-button draft-email-button"
                  onClick={handleDraftEmail}
                  disabled={drafting}
                >
                  <PenSquare size={16} /> {drafting ? "Drafting..." : "Draft Application Email"}
                </button>
              </div>
            )}
            {draftError && <p className="field-error">{draftError}</p>}
          </motion.div>
        )}
      </AnimatePresence>

      <AnimatePresence>
        {emailData && !sentConfirmation && (
          <EmailComposer
            initialSubject={emailData.subject}
            initialBody={emailData.body}
            attachmentFileName={cvFileName}
            attachmentPath={`temp_${cvFileName}`}
            jobTitle={jdData?.job_title || ""}
            matchScore={matchResult?.match_score}
            matchedSkills={matchResult?.matched_skills || []}
            missingSkills={matchResult?.missing_skills || []}
            recruiterReasoning={matchResult?.recruiter_reasoning || ""}
            onSent={setSentConfirmation}
          />
        )}
      </AnimatePresence>

      {sentConfirmation && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="sent-confirmation card"
        >
          <CheckCircle2 size={18} />
          <p>{sentConfirmation.message}</p>
        </motion.div>
      )}
    </div>
  );
}
