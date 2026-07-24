import { Link, useNavigate } from "react-router-dom";
import { PenSquare, History, LogOut } from "lucide-react";
import { useAuth } from "../../context/AuthContext";
import Logo from "./Logo";
import "./Navbar.css";

export default function Navbar() {
  const { currentUser, logout } = useAuth();
  const navigate = useNavigate();

  async function handleLogout() {
    await logout();
    navigate("/login");
  }

  const initials = currentUser?.displayName
    ? currentUser.displayName
        .split(" ")
        .map((part) => part[0])
        .join("")
        .slice(0, 2)
        .toUpperCase()
    : "?";

  return (
    <nav className="navbar">
      <Link to="/" className="navbar-logo-link">
        <Logo size="sm" />
      </Link>

      {currentUser && (
        <div className="navbar-links">
          <Link to="/" className="navbar-link">
            <PenSquare size={16} /> Draft Email
          </Link>
          <Link to="/history" className="navbar-link">
            <History size={16} /> My History
          </Link>
        </div>
      )}

      {currentUser && (
        <div className="navbar-user">
          <span className="navbar-user-name">
            {currentUser.displayName || currentUser.email}
          </span>
          <div className="navbar-avatar">{initials}</div>
          <button className="navbar-logout" onClick={handleLogout}>
            <LogOut size={15} /> Logout
          </button>
        </div>
      )}
    </nav>
  );
}
