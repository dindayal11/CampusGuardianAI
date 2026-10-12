
"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import { apiFetch } from "@/lib/api";

export default function Login() {
  const router = useRouter();

  const [identifier, setIdentifier] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function submit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setError("");
    setBusy(true);

    const loginId = identifier.trim();

    try {
      // First try Student / Institute Admin login.
      try {
        await apiFetch("/auth/login", {
          method: "POST",
          body: JSON.stringify({
            user_id: loginId,
            password,
          }),
        });

        router.push("/dashboard");
        return;
      } catch {
        // If regular login fails, try Platform Admin login.
      }

      try {
        await apiFetch("/auth/platform-login", {
          method: "POST",
          body: JSON.stringify({
            email: loginId,
            password,
          }),
        });

        router.push("/dashboard/platform");
      } catch {
        setError("Invalid User ID/email or password.");
      }
    } catch {
      setError("Login failed. Please try again.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="auth-wrap">
      <div className="auth">
        <span className="eyebrow">Secure login</span>

        <h1>Campus Guardian AI</h1>

        <p className="muted">
          Sign in to access your Campus Guardian AI dashboard.
        </p>

        <form onSubmit={submit}>
          <div className="field">
            <label htmlFor="identifier">User ID </label>

            <input
              id="identifier"
              type="text"
              value={identifier}
              onChange={(e) => setIdentifier(e.target.value)}
              autoComplete="username"
              placeholder="Enter your User ID "
              required
            />
          </div>

          <div className="field">
            <label htmlFor="password">Password</label>

            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              autoComplete="current-password"
              placeholder="Enter your password"
              required
            />
          </div>

          {error && (
            <div className="notice" role="alert">
              {error}
            </div>
          )}

          <div className="cta">
            <button
              className="btn primary"
              type="submit"
              disabled={busy}
            >
              {busy ? "Signing in..." : "Login"}
            </button>
          </div>
        </form>
      </div>
    </main>
  );
}
