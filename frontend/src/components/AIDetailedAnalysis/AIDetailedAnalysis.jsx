import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Sparkles, ChevronDown, Rocket, Wrench, BarChart3, TrendingDown } from "lucide-react";
import "./AIDetailedAnalysis.css";

// The backend's recruiter_reasoning text uses markdown-style sections.
// We normalize it into clean plain text so the UI shows only readable text.
function cleanAnalysisText(raw) {
  if (!raw) return "";

  return raw
    .replace(/\r/g, "")
    .replace(/<[^>]*>/g, "")
    .replace(/\*\*/g, "")
    .replace(/\*/g, "")
    .replace(/`/g, "")
    .replace(/\|/g, "")
    .replace(/•/g, "")
    .replace(/^-{3,}$/gm, "")
    .replace(/^\s*[*+-]\s+/gm, "")
    .replace(/^\s*#+\s*/gm, "")
    .replace(/\s{2,}/g, " ")
    .replace(/\n{2,}/g, "\n\n")
    .trim();
}

function parseSections(rawText) {
  if (!rawText) return [];
  const parts = rawText.split(/###\s+/).filter(Boolean);
  return parts.map((part) => {
    const [rawHeading, ...rest] = part.split("\n");
    const cleanHeading = rawHeading.replace(/^[^\p{L}]+/u, "").trim();
    return {
      heading: cleanHeading,
      body: cleanAnalysisText(rest.join("\n").trim()),
    };
  });
}

function iconForHeading(heading) {
  const lower = heading.toLowerCase();
  if (lower.includes("verdict") || lower.includes("overall")) return Rocket;
  if (lower.includes("deep") || lower.includes("portfolio")) return Wrench;
  if (lower.includes("alignment") || lower.includes("bridge")) return BarChart3;
  if (lower.includes("gap") || lower.includes("discrepanc")) return TrendingDown;
  return Sparkles;
}

export default function AIDetailedAnalysis({ reasoning }) {
  const [expanded, setExpanded] = useState(true);
  const sections = parseSections(reasoning);

  return (
    <div className="card analysis-card">
      <button
        className="analysis-toggle"
        onClick={() => setExpanded((prev) => !prev)}
      >
        <h4 className="analysis-title">
          <Sparkles size={17} /> AI Detailed Analysis
        </h4>
        <ChevronDown
          size={18}
          className={`analysis-chevron ${expanded ? "analysis-chevron-open" : ""}`}
        />
      </button>

      <AnimatePresence initial={false}>
        {expanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.25 }}
            className="analysis-content"
          >
            {sections.map((section) => {
              const SectionIcon = iconForHeading(section.heading);
              return (
                <div key={section.heading} className="analysis-section">
                  <h5 className="analysis-section-heading">
                    <SectionIcon size={15} /> {section.heading}
                  </h5>
                  <div className="analysis-section-body">{section.body}</div>
                </div>
              );
            })}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
