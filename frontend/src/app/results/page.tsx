import AppShell from "@/components/layout/AppShell";
import { useState, useEffect, useMemo } from "react";
import { api } from "@/lib/api-client";

export default function ResultsPage() {
  const [data, setData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [query, setQuery] = useState("");
  const [filterStatus, setFilterStatus] = useState<"all" | "approved" | "ai_suggested" | "pending">("all");
  const [page, setPage] = useState(1);
  const perPage = 10;

  useEffect(() => {
    api.evaluations()
      .then((json) => { setData(Array.isArray(json) ? json : []); setLoading(false); })
      .catch((e: any) => { setError(e.message || String(e)); setLoading(false); });
  }, []);

  const filtered = useMemo(() => {
    let list = data;
    if (query) {
      const q = query.toLowerCase();
      list = list.filter((r) => (r.student_id + " " + (r.exam_id ?? "") + " " + (r.feedback ?? "")).toLowerCase().includes(q));
    }
    if (filterStatus !== "all") {
      list = list.filter((r) => {
        const s = (r.status || "pending").toLowerCase();
        if (filterStatus === "approved") return s === "approved";
        if (filterStatus === "ai_suggested") return ["ai_suggested", "needs_review", "processing"].includes(s);
        return s === "pending" || s === "processing";
      });
    }
    return list;
  }, [data, query, filterStatus]);

  const totalPages = Math.max(1, Math.ceil(filtered.length / perPage));
  const paginated = filtered.slice((page - 1) * perPage, page * perPage);

  async function handleExport(format: "csv" | "pdf") {
    const url = process.env.NEXT_PUBLIC_API_URL;
    window.open(`${url}/api/v1/exports/evaluations?format=${format}`, "_blank");
  }

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: 16, flexWrap: "wrap" }}>
        <div>
          <h1 style={{ fontSize: 24, fontWeight: 700, color: "#071225" }}>Results</h1>
          <p style={{ color: "#667085" }}>Search, filter, paginate, export from /api/v1/evaluations and /api/v1/exports.</p>
        </div>
        <div style={{ display: "flex", gap: 8 }}>
          <button onClick={() => handleExport("csv")} style={{ padding: "6px 12px", borderRadius: 8, border: "1px solid #E5EAF3", cursor: "pointer", fontSize: 12, fontWeight: 600 }}>CSV</button>
          <button onClick={() => handleExport("pdf")} style={{ padding: "6px 12px", borderRadius: 8, border: "1px solid #E5EAF3", cursor: "pointer", fontSize: 12, fontWeight: 600 }}>PDF</button>
        </div>
      </div>
      <div style={{ display: "flex", gap: 12, marginTop: 16, flexWrap: "wrap" }}>
        <label htmlFor="results-search" style={{ fontSize: 12, fontWeight: 600, color: "#667085" }}>Search</label>
        <input id="results-search" aria-label="Search evaluations" value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Student / exam" style={{ flex: 1, padding: 10, borderRadius: 8, border: "1px solid #E5EAF3" }} />
        <label htmlFor="results-status" style={{ fontSize: 12, fontWeight: 600, color: "#667085" }}>Status</label>
        <select id="results-status" value={filterStatus} onChange={(e) => setFilterStatus(e.target.value as any)} style={{ padding: 10, borderRadius: 8, border: "1px solid #E5EAF3" }}>
          <option value="all">All</option>
          <option value="approved">Approved</option>
          <option value="ai_suggested">AI only</option>
          <option value="pending">Pending</option>
        </select>
      </div>
      {loading && <div style={{ padding: 24 }}>Loading from backend…</div>}
      {error && <div role="alert" style={{ color: "#E5484D", padding: 12, background: "#FFF0F0", borderRadius: 8 }}>{error}</div>}
      {!loading && !error && filtered.length > 0 && (
        <div style={{ marginTop: 16 }}>
          <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 13 }}>
            <thead><tr style={{ borderBottom: "1px solid #E5EAF3" }}><th>Student</th><th>Exam</th><th>Marks</th><th>Approval</th></tr></thead>
            <tbody>
              {paginated.map((r: any) => {
                const score = Array.isArray(r.question_scores) ? r.question_scores.length : 0;
                const approved = r.status === "approved" || r.approved === true;
                return (
                  <tr key={r.id || Math.random()} style={{ borderBottom: "1px solid #F5F7FC" }}>
                    <td style={{ padding: 8 }}>{r.student_id ?? r.student_number ?? "—"}</td>
                    <td>{r.exam_id ?? "—"}</td>
                    <td>{r.total_score != null ? `${r.total_score}` : (r.awarded_marks != null ? `${r.awarded_marks}/${r.max_marks ?? "—"}` : "—")} {score > 0 && <span style={{ fontSize: 11, color: "#98A2B3" }}>({score} qs)</span>}</td>
                    <td><span style={{ padding: "2px 8px", borderRadius: 999, fontSize: 11, fontWeight: 600, background: approved ? "#E9F8F0" : "#FFF6DF", color: approved ? "#20A66A" : "#F2A51A" }}>{approved ? "Faculty approved" : "AI suggested"}</span></td>
                  </tr>
                );
              })}
            </tbody>
          </table>
          <div style={{ display: "flex", gap: 8, justifyContent: "flex-end", marginTop: 12 }}>
            <button disabled={page <= 1} onClick={() => setPage((p) => Math.max(1, p - 1))} style={{ padding: "6px 12px", borderRadius: 8, border: "1px solid #E5EAF3", cursor: page <= 1 ? "not-allowed" : "pointer", opacity: page <= 1 ? 0.5 : 1 }}>Prev</button>
            <span style={{ fontSize: 12, color: "#667085", alignSelf: "center" }}>Page {page} / {totalPages} — {filtered.length} items</span>
            <button disabled={page >= totalPages} onClick={() => setPage((p) => Math.min(totalPages, p + 1))} style={{ padding: "6px 12px", borderRadius: 8, border: "1px solid #E5EAF3", cursor: page >= totalPages ? "not-allowed" : "pointer", opacity: page >= totalPages ? 0.5 : 1 }}>Next</button>
          </div>
        </div>
      )}
      {!loading && !error && filtered.length === 0 && <div style={{ marginTop: 16, color: "#667085" }}>No evaluations found (empty data or backend unavailable). Apply filters or upload sheets.</div>}
    </div>
  );
}
