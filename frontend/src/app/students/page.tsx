"use client";
import { useEffect, useState } from "react";
import AppShell from "@/components/layout/AppShell";

export default function StudentsPage() {
  const [students, setStudents] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const base = process.env.NEXT_PUBLIC_API_URL;
    fetch(`${base}/api/v1/students`)
      .then((r) => {
        if (!r.ok) return r.json().then((b) => Promise.reject(b.detail ?? `Students ${r.status}`)).catch(() => Promise.reject(`Students ${r.status}`));
        return r.json();
      })
      .then((data) => {
        setStudents(Array.isArray(data) ? data : data.students ?? []);
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
        <h1 style={{ fontSize: 24, fontWeight: 700, color: "#071225" }}>Students</h1>
        <p style={{ color: "#667085" }}>List from backend /api/v1/students (requires faculty/admin token).</p>
        {loading && <p>Loading…</p>}
        {error && <p role="alert" style={{ color: "#E5484D", padding: 12, background: "#FFF0F0", borderRadius: 8 }}>{error}</p>}
        {!loading && !error && students.length === 0 && <p style={{ color: "#667085" }}>No students yet.</p>}
        {!loading && !error && students.length > 0 && (
          <div style={{ marginTop: 16, display: "grid", gap: 12 }}>
            {students.map((s) => (
              <div key={s.id ?? s.student_number} style={{ background: "#fff", padding: 16, borderRadius: 12, border: "1px solid #E5EAF3" }}>
                <strong>{s.name ?? s.student_number}</strong>
                <p style={{ fontSize: 12, color: "#667085" }}>{s.student_number} — {s.class_or_section ?? "—"}</p>
              </div>
            ))}
          </div>
        )}
      </div>
    </AppShell>
  );
}
