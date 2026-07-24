import "./Logo.css";

// A custom SVG mark instead of an emoji - two overlapping shapes forming
// a subtle "match" motif (a document + a check), on a gradient badge.
export default function Logo({ size = "md" }) {
  return (
    <div className={`logo-row logo-${size}`}>
      <span className="logo-badge">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
          <path
            d="M4 4.5C4 3.67 4.67 3 5.5 3H14L20 9V19.5C20 20.33 19.33 21 18.5 21H5.5C4.67 21 4 20.33 4 19.5V4.5Z"
            fill="white"
            fillOpacity="0.25"
          />
          <path
            d="M14 3V8C14 8.55 14.45 9 15 9H20"
            stroke="white"
            strokeWidth="1.6"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
          <path
            d="M8.5 13.5L10.7 15.7L15.5 10.9"
            stroke="white"
            strokeWidth="1.8"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </svg>
      </span>
      <span className="logo-wordmark">JobMatch<span className="logo-wordmark-accent">AI</span></span>
    </div>
  );
}
