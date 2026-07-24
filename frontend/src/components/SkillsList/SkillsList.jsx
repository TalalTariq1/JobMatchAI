import { motion } from "framer-motion";
import { CheckCircle2, TriangleAlert } from "lucide-react";
import "./SkillsList.css";

// One component handles both "matched" and "missing" skill lists - the
// only difference is color and icon, controlled by the `type` prop.
export default function SkillsList({ title, skills, type }) {
  const isMatched = type === "matched";

  return (
    <div className="card skills-card">
      <h4 className={`skills-title ${isMatched ? "skills-title-matched" : "skills-title-missing"}`}>
        {isMatched ? <CheckCircle2 size={17} /> : <TriangleAlert size={17} />} {title}
      </h4>
      <div className="skills-pill-row">
        {skills.length === 0 && (
          <span className="skills-empty">None</span>
        )}
        {skills.map((skill, index) => (
          <motion.span
            key={skill}
            className={`skills-pill ${isMatched ? "skills-pill-matched" : "skills-pill-missing"}`}
            initial={{ opacity: 0, y: 6 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.04 }}
          >
            {skill}
          </motion.span>
        ))}
      </div>
    </div>
  );
}
