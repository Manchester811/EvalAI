"use client";
import { useDropzone } from "react-dropzone";
import { useState } from "react";

type FileItem = { file: File; status: "pending" | "uploading" | "done" | "error"; error?: string; progress?: number };

export function FileDropzone({ onUploaded, examId }: { onUploaded: (r: any) => void; examId?: number }) {
  const [items, setItems] = useState<FileItem[]>([]);
  const [globalError, setGlobalError] = useState("");

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop: (accepted, fileRejections) => {
      if (fileRejections.length) {
        const msg = fileRejections.map((r) => r.errors[0]?.message ?? "Rejected").join(", ");
        setGlobalError(msg);
      } else setGlobalError("");
      const next = accepted.map((file) => ({ file, status: "pending" as const }));
      setItems((prev) => [...prev, ...next]);
    },
    accept: { "image/jpeg": [".jpg", ".jpeg"], "image/png": [".png"], "application/pdf": [".pdf"] },
    maxSize: 10 * 1024 * 1024,
  });

  async function upload(idx: number) {
    const item = items[idx];
    if (!item) return;
    setItems((p) => p.map((it, i) => (i === idx ? { ...it, status: "uploading", progress: 30 } : it)));
    try {
      const form = new FormData();
      form.append("file", item.file);
      if (examId != null) form.append("exam_id", String(examId));
      const url = process.env.NEXT_PUBLIC_API_URL;
      const res = await fetch(`${url}/api/v1/answer-sheets`, { method: "POST", body: form });
      const body = await res.text().catch(() => "");
      let json: any = {};
      try { json = JSON.parse(body); } catch { json = { message: body }; }
      if (!res.ok) {
        const msg = json.detail ?? body ?? `Upload failed (${res.status})`;
        setItems((p) => p.map((it, i) => (i === idx ? { ...it, status: "error", error: typeof msg === "string" ? msg : JSON.stringify(msg) } : it)));
        return;
      }
      setItems((p) => p.map((it, i) => (i === idx ? { ...it, status: "done" } : it)));
      onUploaded(json);
    } catch (err: any) {
      setItems((p) => p.map((it, i) => (i === idx ? { ...it, status: "error", error: err.message ?? String(err) } : it)));
    }
  }

  function retry(idx: number) {
    setItems((p) => p.map((it, i) => (i === idx ? { ...it, status: "pending", error: undefined } : it)));
    upload(idx);
  }

  return (
    <div>
      <div
        {...getRootProps()}
        style={{
          border: `2px dashed ${isDragActive ? "#3B66F5" : "#E5EAF3"}`,
          borderRadius: 12,
          padding: 40,
          textAlign: "center",
          background: isDragActive ? "#F3F6FF" : "#F5F7FC",
          cursor: "pointer",
        }}
        aria-label="Upload dropzone"
      >
        <input {...getInputProps()} />
        <p style={{ fontSize: 16, fontWeight: 600, color: "#071225" }}>Upload Answer Sheet</p>
        <p style={{ fontSize: 13, color: "#667085", marginTop: 8 }}>Drag & drop here or click to browse (JPG/PNG/PDF, 10 MB)</p>
        <p style={{ fontSize: 12, color: "#98A2B3", marginTop: 8 }}>Selected file shows below with Upload / Retry controls.</p>
      </div>
      {globalError && <p role="alert" style={{ color: "#E5484D", fontSize: 12, marginTop: 12 }}>{globalError}</p>}
      <ul style={{ listStyle: "none", padding: 0, marginTop: 16 }}>
        {items.map((it, idx) => (
          <li key={it.file.name + idx} style={{ display: "flex", alignItems: "center", gap: 12, padding: 12, border: "1px solid #E5EAF3", borderRadius: 8, marginTop: 8, background: it.status === "error" ? "#FFF0F0" : "#fff" }}>
            <span style={{ fontSize: 12, flex: 1 }}>{it.file.name} ({Math.round(it.file.size / 1024)} KB) — {it.status}</span>
            {it.status === "error" && <span style={{ fontSize: 11, color: "#E5484D", flex: 1 }}>{it.error ?? "Unknown error"}</span>}
            {it.status === "pending" && <button onClick={() => upload(idx)} style={{ padding: "6px 12px", borderRadius: 8, border: "none", background: "linear-gradient(135deg,#3B66F5,#7C4DFF)", color: "#fff", cursor: "pointer" }}>Upload</button>}
            {it.status === "error" && <button onClick={() => retry(idx)} style={{ padding: "6px 12px", borderRadius: 8, border: "1px solid #E5EAF3", cursor: "pointer" }}>Retry</button>}
            {it.status === "done" && <span style={{ fontSize: 11, color: "#20A66A" }}>Done</span>}
          </li>
        ))}
      </ul>
    </div>
  );
}
