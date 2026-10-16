import AppShell from "@/components/layout/AppShell";
import { useState, useEffect } from "react";
import { api } from "@/lib/api-client";

export default function ResultsPage() {
  const [data, setData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    api.evaluations()
      .then((json) => { setData(Array.isArray(json) ? json : []); setLoading(false); })
      .catch((e: any) => { setError(e.message || String(e)); setLoading(false); });
  }, []);

  return (
    <AppShell>
      <div>
        <h1 style={{ fontSize: 24, fontWeight: 700, color: "#071225" }}>Results</h1>
        <p style={{ color: "#667085" }}>Search/filter results from backend /api/v1/evaluations.</p>
        {loading && <div style={{ padding: 24 }}>Loading from backend…</div>}
        {error && <div style={{ color: "#E5484D", padding: 12, background: "#FFF0F0", borderRadius: 8 }}>{error}</div>}
        {!loading && !error && data.length > 0 && (
          <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 13 }}>
            <thead><tr style={{ borderBottom: "1px solid #E5EAF3" }}><th>Student</th><th>Exam</th><th>Score</th><th>Status</th></tr></thead>
            <tbody>
              {data.map((r: any) => (
                <tr key={r.id || Math.random()} style={{ borderBottom: "1px solid #F5F7FC" }}>
                  <td style={{ padding: 8 }}>{r.student_id || "—"}</td>
                  <td>{r.exam_id || "—"}</td>
                  <td>{r.total_score != null ? `${r.total_score}` : "—"}</td>
                  <td><span style={{ padding: "2px 8px", borderRadius: 999, fontSize: 11, fontWeight: 600, background: r.status === "approved" ? "#E9F8F0" : "#F5F7FC", color: r.status === "approved" ? "#20A66A" : "#667085" }}>{r.status || "pending"}</span></td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
        {!loading && !error && data.length === 0 && <div>Empty — no evaluations found or backend unavailable.</div>}
      </div>
    </AppShell>
  );
}
