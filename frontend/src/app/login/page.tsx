"use client";
import { useState } from "react";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("Demo: login requires backend /api/v1/auth/login (not fully wired). Use any demo credentials to proceed.");
  };

  return (
    <div style={{ minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center", background: "#F5F7FC", fontFamily: "system-ui, sans-serif" }}>
      <div style={{ background: "#fff", padding: 32, borderRadius: 16, border: "1px solid #E5EAF3", boxShadow: "0 4px 20px rgba(7,18,37,0.06)", width: 360, maxWidth: "90vw" }}>
        <h1 style={{ fontSize: 22, fontWeight: 700, color: "#071225", marginBottom: 4 }}>EvalAI</h1>
        <p style={{ fontSize: 13, color: "#667085", marginBottom: 20 }}>Sign in to continue evaluation.</p>
        <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: 12 }}>
          <input aria-label="Email" type="email" placeholder="Faculty email" value={email} onChange={e => setEmail(e.target.value)} style={{ padding: 10, borderRadius: 8, border: "1px solid #E5EAF3", fontSize: 14 }} />
          <input aria-label="Password" type="password" placeholder="Password" value={password} onChange={e => setPassword(e.target.value)} style={{ padding: 10, borderRadius: 8, border: "1px solid #E5EAF3", fontSize: 14 }} />
          <button type="submit" style={{ padding: 10, borderRadius: 8, border: "none", background: "linear-gradient(135deg,#3B66F5,#7C4DFF)", color: "#fff", fontWeight: 600, cursor: "pointer" }}>Sign In</button>
        </form>
        {error && <div style={{ marginTop: 12, fontSize: 12, color: "#E5484D" }}>{error}</div>}
        <div style={{ marginTop: 16, fontSize: 11, color: "#98A2B3" }}>Demo mode — backend /api/v1/auth/login not fully implemented.</div>
      </div>
    </div>
  );
}
