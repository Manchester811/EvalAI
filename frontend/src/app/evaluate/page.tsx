"use client";
import { useEffect, useState } from "react";
import AppShell from "@/components/layout/AppShell";
import { ExamSelector } from "@/components/evaluation/ExamSelector";
import { FileDropzone } from "@/components/evaluation/FileDropzone";

export default function EvaluatePage() {
  const [examId, setExamId] = useState<number | "">("");
  const [lastResult, setLastResult] = useState<any>(null);
  const [statusById, setStatusById] = useState<Record<number, string>>({});
  const [fetchError, setFetchError] = useState("");

  useEffect(() => {
    setFetchError("");
  }, [examId]);

  async function pollStatus(id: number) {
    const url = process.env.NEXT_PUBLIC_API_URL;
    const res = await fetch(`${url}/api/v1/answer-sheets/${id}`);
    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(data.detail || res.statusText || "Status fetch failed");
    setStatusById((s) => ({ ...s, [id]: data.status || data.status_label || "unknown" }));
    return data;
  }

  return (
    <AppShell>
      <div>
        <h1 style={{ fontSize: 24, fontWeight: 700, color: "#071225" }}>Evaluate Sheets</h1>
        <p style={{ color: "#667085" }}>Choose an exam, upload answer sheets, track status. OCR is run after upload (pending → processing → completed/needs_review).</p>
        {fetchError && <p role="alert" style={{ color: "#E5484D", padding: 12, background: "#FFF0F0", borderRadius: 8 }}>{fetchError}</p>}
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16, marginTop: 16 }}>
          <div style={{ background: "#fff", padding: 20, borderRadius: 12, border: "1px solid #E5EAF3" }}>
            <ExamSelector value={examId} onChange={setExamId} />
            {!examId && <p style={{ fontSize: 12, color: "#98A2B3", marginTop: 8 }}>Select an exam before uploading.</p>}
          </div>
          <div style={{ background: "#fff", padding: 20, borderRadius: 12, border: "1px solid #E5EAF3" }}>
            <h2 style={{ fontSize: 14, fontWeight: 600, color: "#071225" }}>Document preview / status</h2>
            {lastResult && (
              <div style={{ fontSize: 12, color: "#667085" }}>
                Sheet #{lastResult.sheet_id} — status: {lastResult.status || "pending"} — {lastResult.message}
                <br />
                <button onClick={() => lastResult.sheet_id != null && pollStatus(lastResult.sheet_id)} style={{ marginTop: 8, padding: "6px 12px", borderRadius: 8, border: "1px solid #E5EAF3", cursor: "pointer" }}>Refresh status</button>
                {lastResult.sheet_id != null && statusById[lastResult.sheet_id] && <span style={{ marginLeft: 8, color: "#20A66A" }}>Polled: {statusById[lastResult.sheet_id]}</span>}
              </div>
            )}
            {!lastResult && <p style={{ fontSize: 12, color: "#98A2B3" }}>No uploads yet.</p>}
          </div>
        </div>
        <div style={{ marginTop: 16 }}>
          <FileDropzone examId={examId === "" ? undefined : Number(examId)} onUploaded={(r) => setLastResult(r)} />
        </div>
      </div>
    </AppShell>
  );
}
