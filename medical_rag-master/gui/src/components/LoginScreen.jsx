import { BrainCircuit, Loader2 } from "lucide-react";
import { useState } from "react";
import { useAuth } from "../context/AuthContext";

export default function LoginScreen() {
  const { login, register } = useAuth();
  const [mode, setMode] = useState("login");
  const [form, setForm] = useState({ email: "", password: "", full_name: "" });
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const update = (key) => (e) => setForm((f) => ({ ...f, [key]: e.target.value }));

  const submit = async (e) => {
    e.preventDefault();
    setError("");
    setBusy(true);
    try {
      if (mode === "login") {
        await login(form.email, form.password);
      } else {
        await register(form.email, form.password, form.full_name);
        await login(form.email, form.password);
      }
    } catch (err) {
      setError(err.message || "Something went wrong");
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="min-h-screen w-full bg-navy-900 flex items-center justify-center px-4">
      <div className="w-full max-w-sm animate-rise">
        <div className="flex items-center gap-2.5 justify-center mb-8">
          <div className="w-9 h-9 rounded-xl bg-brand-600 flex items-center justify-center shadow-glow">
            <BrainCircuit className="w-5 h-5 text-white" strokeWidth={1.75} />
          </div>
          <span className="font-display font-semibold text-2xl text-white tracking-tight">
            Agentic Mind
          </span>
        </div>

        <div className="bg-white rounded-2xl shadow-card border border-mist-line p-7">
          <h1 className="font-display font-semibold text-xl text-navy-800 mb-1">
            {mode === "login" ? "Welcome back" : "Create your account"}
          </h1>
          <p className="text-sm text-navy-400 mb-6 font-body">
            {mode === "login"
              ? "Sign in to reach your conversations."
              : "A few details and you're in."}
          </p>

          <form onSubmit={submit} className="space-y-4">
            {mode === "register" && (
              <Field label="Full name">
                <input
                  required
                  value={form.full_name}
                  onChange={update("full_name")}
                  className="input"
                  placeholder="Dr. Ada Lovelace"
                />
              </Field>
            )}
            <Field label="Email">
              <input
                type="email"
                required
                value={form.email}
                onChange={update("email")}
                className="input"
                placeholder="you@example.com"
              />
            </Field>
            <Field label="Password">
              <input
                type="password"
                required
                minLength={8}
                value={form.password}
                onChange={update("password")}
                className="input"
                placeholder="••••••••"
              />
            </Field>

            {error && (
              <p className="text-sm text-rose bg-rose/10 border border-rose/20 rounded-md px-3 py-2">
                {error}
              </p>
            )}

            <button
              type="submit"
              disabled={busy}
              className="w-full flex items-center justify-center gap-2 bg-brand-600 hover:bg-brand-700 disabled:opacity-60 text-white font-body font-medium text-sm rounded-lg py-2.5 transition-colors"
            >
              {busy && <Loader2 className="w-4 h-4 animate-spin" />}
              {mode === "login" ? "Sign in" : "Create account"}
            </button>
          </form>

          <button
            onClick={() => {
              setError("");
              setMode(mode === "login" ? "register" : "login");
            }}
            className="mt-5 text-sm text-navy-400 hover:text-brand-600 transition-colors font-body w-full text-center"
          >
            {mode === "login"
              ? "New here? Create an account"
              : "Already have an account? Sign in"}
          </button>
        </div>
      </div>

      <style>{`
        .input {
          width: 100%;
          border: 1px solid #DCE5F2;
          background: #F5F8FC;
          border-radius: 8px;
          padding: 0.55rem 0.7rem;
          font-size: 0.875rem;
          font-family: 'Inter', sans-serif;
          color: #0F1B3D;
          outline: none;
          transition: border-color .15s, box-shadow .15s;
        }
        .input:focus {
          border-color: #2F6FED;
          box-shadow: 0 0 0 3px rgba(47,111,237,0.12);
          background: white;
        }
      `}</style>
    </div>
  );
}

function Field({ label, children }) {
  return (
    <label className="block">
      <span className="block text-xs font-medium text-navy-400 mb-1.5 font-body uppercase tracking-wide">
        {label}
      </span>
      {children}
    </label>
  );
}
