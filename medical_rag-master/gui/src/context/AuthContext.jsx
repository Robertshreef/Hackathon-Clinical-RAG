import { createContext, useContext, useState } from "react";

const AuthContext = createContext(null);

// ── Auth Bypass ───────────────────────────────────────────────────────────────
// No login required — the app starts immediately as "authed".
// The backend also accepts requests without a token (see auth/dependencies.py).

const BYPASS_USER = {
  id: "00000000-0000-0000-0000-000000000001",
  email: "local@clinicalrag.local",
  full_name: "Local User",
  role: "user",
};

export function AuthProvider({ children }) {
  const [user] = useState(BYPASS_USER);
  const [status] = useState("authed");

  // Stub functions — kept so existing components that call them don't crash
  const login = async () => {};
  const register = async () => {};
  const logout = async () => {};

  return (
    <AuthContext.Provider value={{ user, status, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}

