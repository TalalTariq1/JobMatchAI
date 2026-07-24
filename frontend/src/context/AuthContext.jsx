import { createContext, useContext, useEffect, useState } from "react";
import {
  createUserWithEmailAndPassword,
  signInWithEmailAndPassword,
  signInWithPopup,
  signOut,
  onAuthStateChanged,
  updateProfile,
} from "firebase/auth";
import { auth, googleProvider } from "../firebase";

// This context is the ONE place that knows "who is logged in right now."
// Any component anywhere in the app can call useAuth() to read the current
// user, or to trigger login/signup/logout, without passing props down
// through every layer manually.
const AuthContext = createContext(null);

export function useAuth() {
  return useContext(AuthContext);
}

export function AuthProvider({ children }) {
  const [currentUser, setCurrentUser] = useState(null);
  // "loading" starts true because, on first page load, Firebase needs a
  // moment to check if there's already a valid saved login. Until it
  // finishes checking, we don't yet know if someone is logged in or not,
  // so we shouldn't render the login page OR the app yet - just wait.
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // onAuthStateChanged fires immediately with the current state, and
    // again any time login/logout happens anywhere in the app.
    const unsubscribe = onAuthStateChanged(auth, (user) => {
      setCurrentUser(user);
      setLoading(false);
    });
    return unsubscribe;
  }, []);

  async function signup(fullName, email, password) {
    const result = await createUserWithEmailAndPassword(auth, email, password);
    // Firebase doesn't ask for a name during signup by default, so we set
    // it as a separate step right after the account is created.
    await updateProfile(result.user, { displayName: fullName });
    return result.user;
  }

  function login(email, password) {
    return signInWithEmailAndPassword(auth, email, password);
  }

  function loginWithGoogle() {
    return signInWithPopup(auth, googleProvider);
  }

  function logout() {
    return signOut(auth);
  }

  // Every backend call that needs to know WHO is calling (like /send-email)
  // needs this fresh token attached as an Authorization header. Tokens
  // expire, so we always ask Firebase for a current one right before use
  // rather than storing one ourselves.
  async function getIdToken() {
    if (!currentUser) return null;
    return currentUser.getIdToken();
  }

  const value = {
    currentUser,
    loading,
    signup,
    login,
    loginWithGoogle,
    logout,
    getIdToken,
  };

  return (
    <AuthContext.Provider value={value}>
      {!loading && children}
    </AuthContext.Provider>
  );
}
