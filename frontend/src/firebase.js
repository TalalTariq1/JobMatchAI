// This file's only job is to connect this app to your Firebase project.
// Every other file that needs auth or Firestore imports from here, so
// there is exactly one place this config lives.

import { initializeApp } from "firebase/app";
import { getAuth, GoogleAuthProvider } from "firebase/auth";

const firebaseConfig = {
  apiKey: "AIzaSyDte7JJlwlc810CJuO5knrSG6xSPY9ac28",
  authDomain: "job-agent-90ee9.firebaseapp.com",
  projectId: "job-agent-90ee9",
  storageBucket: "job-agent-90ee9.firebasestorage.app",
  messagingSenderId: "499711331515",
  appId: "1:499711331515:web:361e6d0a0610f48a89ed9e",
};

const app = initializeApp(firebaseConfig);

export const auth = getAuth(app);
export const googleProvider = new GoogleAuthProvider();
