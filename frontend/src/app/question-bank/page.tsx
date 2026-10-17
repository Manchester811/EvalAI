"use client";
import { useEffect, useState } from "react";
import AppShell from "@/components/layout/AppShell";

type Question = { id?: number; question_id?: number; text?: string; max_marks?: number; reference_answer?: string };

export default function QuestionBankPage() {
  const [questions, setQuestions] = useState<Question[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [examId, setExamId] = useState("");
  const [exams, setExams] = useState<any[]>([]);
  const [creating, setCreating] = useState(false);
  const [newText, setNewText] = useState("");
  const [newMarks, setNewMarks] = useState<number | "">("");
  const [newRef, setNewRef] = useState("");

  useEffect(() => {
    const base = process.env.NEXT_PUBLIC_API_URL;
    // Load exams for selector
    fetch(`${base}/api/v1/exams?limit=100`)
      .then((r) => (r.ok ? r.json() : []))
      .then((data) => setExams(Array.isArray(data) ? data : []))
      .catch(() => setExams([]));
  }, []);

  useEffect(() => {
    if (!examId) { setQuestions([]); setLoading(false); return; }
    setLoading(true);
    const base = process.env.NEXT_PUBLIC_API_URL;
    fetch(`${base}/api/v1/exams/${examId}/questions`)
      .then((r) => (r.ok ? r.json() : Promise.reject(`Questions ${r.status}`)))
      .then((data) => {
        const list = Array.isArray(data) ? data : data.questions ?? [];
        setQuestions(list);
        setLoading(false);
      })
      .catch((e) => {
        setError(e.message ?? String(e));
        setLoading(false);
      });
  }, [examId]);

  async function createQuestion() {
    if (!examId) { setError("Select an exam first."); return; }
    if (!newText.trim()) { setError("Question text required."); return; }
    const base = process.env.NEXT_PUBLIC_API_URL;
    try {
      const res = await fetch(`${base}/api/v1/exams/${examId}/questions`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          text: newText,
          max_marks: newMarks === "" ? 5 : Number(newMarks),
          reference_answer: newRef || undefined,
        }),
      });
      const body = await res.json().catch(() => ({}));
      if (!res.ok) throw new Error(body.detail ?? `Create ${res.status}`);
      setQuestions((q) => [...q, body]);
      setNewText("");
      setNewRef("");
      setNewMarks("");
      setCreating(false);
      setError("");
    } catch (e: any) {
      setError(e.message ?? String(e));
    }
  }

  async function deleteQuestion(qId: number) {
    if (!examId) return;
    const base = process.env.NEXT_PUBLIC_API_URL;
    const res = await fetch(`${base}/api/v1/exams/${examId}/questions/${qId}`, { method: "DELETE" });
    if (!res.ok) {
      const body = await res.json().catch(() => ({}));
      setError(body.detail ?? `Delete ${res.status}`);
      return;
    }
    setQuestions((q) => q.filter((x) => (x.id ?? x.question_id) !== qId));
  }

  return (
    <AppShell>
      <div>
        <h1 style={{ fontSize: 24, fontWeight: 700, color: "#071225" }}>Question Bank</h1>
        <p style={{ color: "#667085" }}>View, create, and delete questions with rubric linkage.</p>
        <div style={{ marginTop: 16, display: "flex", gap: 12, alignItems: "center" }}>
          <label htmlFor="qb-exam" style={{ fontSize: 13, fontWeight: 600 }}>Exam</label>
          <select id="qb-exam" value={examId} onChange={(e) => setExamId(e.target.value)} style={{ padding: 10, borderRadius: 8, border: "1px solid #E5EAF3" }}>
            <option value="">Select exam</option>
            {exams.map((e) => (
              <option key={e.id ?? e.exam_id} value={e.id ?? e.exam_id}>{e.title ?? e.subject ?? `Exam ${e.id}`}</option>
            ))}
          </select>
          <button onClick={() => setCreating((v) => !v)} style={{ padding: "8px 16px", borderRadius: 8, border: "1px solid #E5EAF3", cursor: "pointer" }}>{creating ? "Cancel" : "New question"}</button>
        </div>

        {error && <p role="alert" style={{ color: "#E5484D", padding: 12, background: "#FFF0F0", borderRadius: 8 }}>{error}</p>}

        {creating && (
          <div style={{ marginTop: 16, background: "#fff", padding: 20, borderRadius: 12, border: "1px solid #E5EAF3" }}>
            <label htmlFor="qb-text" style={{ fontSize: 13, fontWeight: 600 }}>Question text</label>
            <textarea id="qb-text" value={newText} onChange={(e) => setNewText(e.target.value)} rows={3} style={{ width: "100%", marginTop: 8, padding: 10, borderRadius: 8, border: "1px solid #E5EAF3" }} />
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12, marginTop: 12 }}>
              <div>
                <label htmlFor="qb-marks" style={{ fontSize: 13, fontWeight: 600 }}>Max marks</label>
                <input id="qb-marks" type="number" value={newMarks} onChange={(e) => setNewMarks(e.target.value ? Number(e.target.value) : "")} style={{ display: "block", marginTop: 8, padding: 10, width: "100%", borderRadius: 8, border: "1px solid #E5EAF3" }} />
              </div>
              <div>
                <label htmlFor="qb-ref" style={{ fontSize: 13, fontWeight: 600 }}>Reference answer</label>
                <textarea id="qb-ref" value={newRef} onChange={(e) => setNewRef(e.target.value)} rows={2} style={{ width: "100%", marginTop: 8, padding: 10, borderRadius: 8, border: "1px solid #E5EAF3" }} />
              </div>
            </div>
            <button onClick={createQuestion} style={{ marginTop: 12, padding: "8px 16px", borderRadius: 8, border: "none", background: "linear-gradient(135deg,#3B66F5,#7C4DFF)", color: "#fff", cursor: "pointer" }}>Create</button>
          </div>
        )}

        {loading && examId && <p style={{ marginTop: 16 }}>Loading…</p>}
        {!examId && <p style={{ marginTop: 16, color: "#667085" }}>Select an exam to view questions.</p>}
        {examId && !loading && questions.length === 0 && !error && <p style={{ marginTop: 16, color: "#667085" }}>No questions for this exam.</p>}
        {questions.length > 0 && (
          <div style={{ marginTop: 16, display: "grid", gap: 12 }}>
            {questions.map((q) => (
              <div key={q.id ?? q.question_id} style={{ background: "#fff", padding: 16, borderRadius: 12, border: "1px solid #E5EAF3" }}>
                <strong>{q.text ?? `Question ${q.id ?? q.question_id}`}</strong>
                <p style={{ fontSize: 12, color: "#667085" }}>Max marks: {q.max_marks ?? "—"} — Ref: {q.reference_answer?.slice(0, 80) ?? "—"}</p>
                <button onClick={() => deleteQuestion(q.id ?? (q.question_id as number))} style={{ marginTop: 8, padding: "4px 12px", borderRadius: 8, border: "1px solid #E5EAF3", cursor: "pointer", color: "#E5484D" }}>Delete</button>
              </div>
            ))}
          </div>
        )}
      </div>
    </AppShell>
  );
}
