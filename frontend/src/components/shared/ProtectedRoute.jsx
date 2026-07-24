import { Navigate } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";

// Wrap any page that should require login in this component. If nobody
// is logged in, it silently redirects to /login instead of rendering
// the protected page at all - this is what keeps MainAppPage and
// HistoryPage from ever being reachable by a guest.
export default function ProtectedRoute({ children }) {
  const { currentUser } = useAuth();

  if (!currentUser) {
    return <Navigate to="/login" replace />;
  }

  return children;
}
