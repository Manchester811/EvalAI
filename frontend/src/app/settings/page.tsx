"use client";
import { useEffect, useState } from "react";
import AppShell from "@/components/layout/AppShell";

export default function SettingsPage() {
  const [user, setUser] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const base = process.env.NEXT_PUBLIC_API_URL;
    fetch(`${base}/api/v1/auth/me`)
      .then((r) => {
        if (!r.ok) return r.json().then((b) => Promise.reject(b.detail ?? `Auth ${r.status}`)).catch(() => Promise.reject(`Auth ${r.status}`));
        return r.json();
      })
      .then((data) => {
        setUser(data);
        setLoading(false);
      })
      .catch((e) => {
        setError(e?.message ?? String(e));
        setLoading(false);
      });
  }, []);

  return (
    <AppShell>
      <div>
        <h1 style={{ fontSize: 24, fontWeight: 700, color: "#071225" }}>Settings</h1>
        <p style={{ color: "#667085" }}>User profile, institution config, supported backend configuration. Secrets never shown.</p>
        {loading ? <p style={{ marginTop: 16 }}>Loading…</p> : null}
        {error && <p role="alert" style={{ color: "#E5484D", padding: 12, background: "#FFF0F0", borderRadius: 8 }}>{error}</p>}
        {user && !loading && (
          <div style={{ marginTop: 16, background: "#fff", padding: 20, borderRadius: 12, border: "1px solid #E5EAF3" }}>
            <strong>Current user</strong>
            <p style={{ fontSize: 12, color: "#667085" }}>{user.email ?? user.username ?? "—"} — {user.role ?? "—"}</p>
            <p style={{ fontSize: 11, color: "#98A2B3" }}>Never expose secret API keys through public screens.</p>
          </div>
        )}
      </div>
    </AppShell>
  );
}
