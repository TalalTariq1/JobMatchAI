import { Loader2 } from "lucide-react";
import "./LoadingSpinner.css";

export default function LoadingSpinner({ label = "Loading..." }) {
  return (
    <div className="loading-spinner-wrapper">
      <Loader2 className="loading-spinner-icon" size={22} />
      <span className="loading-spinner-label">{label}</span>
    </div>
  );
}
