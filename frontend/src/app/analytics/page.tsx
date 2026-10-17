"use client";
import { useEffect, useState } from "react";
import AppShell from "@/components/layout/AppShell";
import { Bar, BarChart, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

export default function AnalyticsPage() {
  const [overview, setOverview] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const base = process.env.NEXT_PUBLIC_API_URL;
    fetch(`${base}/api/v1/analytics/overview`)
      .then((r) => (r.ok ? r.json() : Promise.reject(`Analytics ${r.status}`)))
      .then((data) => {
        setOverview(data);
        setLoading(false);
      })
      .catch((e) => {
        setError(e.message || String(e));
        setLoading(false);
      });
  }, []);

  if (loading) return <AppShell><div>Loading analytics…</div></AppShell>;
  if (error)
    return (
      <AppShell>
        <h1 style={{ fontSize: 24, fontWeight: 700, color: "#071225" }}>Analytics</h1>
        <p role="alert" style={{ color: "#E5484D", padding: 12, background: "#FFF0F0", borderRadius: 8 }}>{error}</p>
        <p style={{ fontSize: 13, color: "#667085" }}>Backend must be running at {process.env.NEXT_PUBLIC_API_URL} and return /api/v1/analytics/overview.</p>
      </AppShell>
    );

  const summaryCards = overview?.summary_cards ?? { total_evaluations: 0, avg_score: 0, completion_rate: 0, questions_assessed: 0 };
  const activity = Array.isArray(overview?.activity) ? overview.activity : [];
  const distribution = Array.isArray(overview?.distribution) ? overview.distribution : [];

  return (
    <AppShell>
      <div>
        <h1 style={{ fontSize: 24, fontWeight: 700, color: "#071225" }}>Analytics</h1>
        <section style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit,minmax(180px,1fr))", gap: 16, marginTop: 16 }}>
          <div style={{ background: "#fff", padding: 16, borderRadius: 12, border: "1px solid #E5EAF3" }}><strong>{summaryCards.total_evaluations}</strong> Total evaluations</div>
          <div style={{ background: "#fff", padding: 16, borderRadius: 12, border: "1px solid #E5EAF3" }}><strong>{summaryCards.avg_score}</strong> Average score</div>
          <div style={{ background: "#fff", padding: 16, borderRadius: 12, border: "1px solid #E5EAF3" }}><strong>{summaryCards.completion_rate}</strong> Completion rate</div>
          <div style={{ background: "#fff", padding: 16, borderRadius: 12, border: "1px solid #E5EAF3" }}><strong>{summaryCards.questions_assessed}</strong> Questions assessed</div>
        </section>
        {activity.length > 0 ? (
          <div style={{ marginTop: 24, background: "#fff", padding: 20, borderRadius: 12, border: "1px solid #E5EAF3" }}>
            <h2 style={{ fontSize: 14, fontWeight: 600, color: "#071225" }}>Activity over time</h2>
            <ResponsiveContainer width="100%" height={180}>
              <LineChart data={activity}>
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Line type="monotone" dataKey="count" stroke="#3B66F5" />
              </LineChart>
            </ResponsiveContainer>
          </div>
        ) : (
          <p style={{ marginTop: 24, color: "#667085" }}>No evaluation activity data yet. Submit evaluations to populate charts.</p>
        )}
        {distribution.length > 0 ? (
          <div style={{ marginTop: 16, background: "#fff", padding: 20, borderRadius: 12, border: "1px solid #E5EAF3" }}>
            <h2 style={{ fontSize: 14, fontWeight: 600, color: "#071225" }}>Score distribution</h2>
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={distribution}>
                <XAxis dataKey="bucket" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="count" fill="#7C4DFF" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        ) : (
          <p style={{ marginTop: 16, color: "#667085" }}>No score distribution data yet.</p>
        )}
      </div>
    </AppShell>
  );
}
