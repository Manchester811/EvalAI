// Shared exam selector — exam list from backend
"use client";
import { useEffect, useState } from "react";

export function ExamSelector({ value, onChange }: { value: number | ""; onChange: (v: number | "") => void }) {
  const [exams, setExams] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const url = process.env.NEXT_PUBLIC_API_URL;
    fetch(`${url}/api/v1/exams?limit=100`)
      .then((r) => (r.ok ? r.json() : Promise.reject(`Exam list ${r.status}`)))
      .then((data) => { setExams(Array.isArray(data) ? data : []); setLoading(false); })
      .catch((e) => { setError(e.message || String(e)); setLoading(false); });
  }, []);

  return (
    <div>
      <label htmlFor="exam-select" style={{ fontSize: 13, fontWeight: 600, color: "#101828" }}>Exam</label>
      {loading && <p style={{ fontSize: 12, color: "#667085" }}>Loading exams…</p>}
      {error && <p style={{ fontSize: 12, color: "#E5484D" }}>{error}</p>}
      <select id="exam-select" value={value} onChange={(e) => onChange(e.target.value ? Number(e.target.value) : "")} style={{ display: "block", marginTop: 8, padding: 10, width: "100%", borderRadius: 8, border: "1px solid #E5EAF3" }}>
        <option value="">Select exam</option>
        {exams.map((e) => (
          <option key={e.id ?? e.exam_id} value={e.id ?? e.exam_id}>
            {e.title ?? e.subject ?? `Exam ${e.id ?? e.exam_id}`}
          </option>
        ))}
      </select>
    </div>
  );
}
