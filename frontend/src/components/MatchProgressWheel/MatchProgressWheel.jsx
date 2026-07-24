import { useEffect, useState } from "react";
import { motion, animate } from "framer-motion";
import "./MatchProgressWheel.css";

// Draws an SVG ring and animates it (and the number in the center)
// smoothly from 0 up to the real match score, once, when the score
// first appears.
export default function MatchProgressWheel({ score }) {
  const [displayedScore, setDisplayedScore] = useState(0);

  const radius = 70;
  const circumference = 2 * Math.PI * radius;

  useEffect(() => {
    if (score == null) return;
    // animate() here is Framer Motion's imperative helper - it smoothly
    // interpolates a number over time and calls onUpdate every frame,
    // which is exactly what we need for both the ring AND the counting
    // number to move in sync.
    const controls = animate(0, score, {
      duration: 1.4,
      ease: "easeOut",
      onUpdate: (value) => setDisplayedScore(Math.round(value)),
    });
    return () => controls.stop();
  }, [score]);

  const offset = circumference - (displayedScore / 100) * circumference;

  function competitivenessLabel(value) {
    if (value >= 75) return "High";
    if (value >= 45) return "Moderate";
    return "Needs Work";
  }

  return (
    <div className="progress-wheel-wrapper">
      <h4 className="progress-wheel-title">Match Result</h4>
      <svg width="180" height="180" viewBox="0 0 180 180">
        <defs>
          <linearGradient id="matchGradient" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#5B4FE9" />
            <stop offset="100%" stopColor="#8B5CF6" />
          </linearGradient>
        </defs>
        <circle
          cx="90"
          cy="90"
          r={radius}
          fill="none"
          stroke="#EDECFB"
          strokeWidth="14"
        />
        <motion.circle
          cx="90"
          cy="90"
          r={radius}
          fill="none"
          stroke="url(#matchGradient)"
          strokeWidth="14"
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          transform="rotate(-90 90 90)"
        />
        <text
          x="90"
          y="86"
          textAnchor="middle"
          className="progress-wheel-percent"
        >
          {displayedScore}%
        </text>
        <text
          x="90"
          y="106"
          textAnchor="middle"
          className="progress-wheel-label"
        >
          {score >= 75 ? "STRONG MATCH" : score >= 45 ? "PARTIAL MATCH" : "WEAK MATCH"}
        </text>
      </svg>

      <div className="competitiveness-row">
        <span>Competitiveness</span>
        <strong>{competitivenessLabel(score)}</strong>
      </div>
      <div className="competitiveness-bar-track">
        <motion.div
          className="competitiveness-bar-fill"
          initial={{ width: 0 }}
          animate={{ width: `${score}%` }}
          transition={{ duration: 1.4, ease: "easeOut" }}
        />
      </div>
    </div>
  );
}
