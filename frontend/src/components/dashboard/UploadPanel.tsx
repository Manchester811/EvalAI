'use client';

import { ChangeEvent, DragEvent, useRef, useState } from 'react';
import { CloudUpload } from 'lucide-react';

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000';
const MAX_FILE_SIZE = 10 * 1024 * 1024;
const ACCEPTED_TYPES = new Set(['image/jpeg', 'image/png', 'application/pdf']);
type UploadMode = 'single' | 'multiple' | 'bulk';
type UploadFailure = { fileName: string; reason: string };

const isRecord = (value: unknown): value is Record<string, unknown> => typeof value === 'object' && value !== null;

const formatErrorDetail = (value: unknown): string | null => {
  if (typeof value === 'string') {
    const detail = value.trim();
    return detail ? detail.slice(0, 300) : null;
  }

  if (Array.isArray(value)) {
    const details = value
      .map((item) => formatErrorDetail(isRecord(item) ? item.msg ?? item.message ?? item.error : item))
      .filter((item): item is string => Boolean(item));
    return details.length ? details.join('; ').slice(0, 300) : null;
  }

  if (isRecord(value)) {
    return formatErrorDetail(value.detail) ?? formatErrorDetail(value.message) ?? formatErrorDetail(value.error);
  }

  return null;
};

const parseJson = (body: string): unknown => {
  if (!body.trim()) return null;
  try {
    return JSON.parse(body) as unknown;
  } catch {
    return null;
  }
};

export default function UploadPanel() {
  const inputRef = useRef<HTMLInputElement>(null);
  const uploadInFlightRef = useRef(false);
  const [mode, setMode] = useState<UploadMode>('single');
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [queueSize, setQueueSize] = useState(0);
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);

  const uploadFile = async (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await fetch(`${API_URL}/api/v1/answer-sheets`, { method: 'POST', body: formData });
    const responseBody = await response.text();
    const payload = parseJson(responseBody);
    if (!response.ok) {
      const detail = formatErrorDetail(payload) ?? (payload === null ? responseBody.trim().slice(0, 300) : '');
      throw new Error(detail || `The server rejected the upload (HTTP ${response.status}).`);
    }
    return payload;
  };

  const uploadFiles = async (files: File[]) => {
    if (uploadInFlightRef.current) return;
    uploadInFlightRef.current = true;
    setError('');
    setMessage('');

    let completed = 0;
    const failures: UploadFailure[] = [];
    try {
      if (!files.length) return;
      if (mode === 'single' && files.length > 1) {
        setError('Single Sheet mode accepts one file at a time. Select one JPG, PNG, or PDF.');
        return;
      }

      const invalidType = files.find((file) => !ACCEPTED_TYPES.has(file.type));
      const oversized = files.find((file) => file.size > MAX_FILE_SIZE);
      if (invalidType) {
        setError(`${invalidType.name} is not a supported file. Choose JPG, PNG, or PDF.`);
        return;
      }
      if (oversized) {
        setError(`${oversized.name} is larger than 10 MB. Choose a smaller file.`);
        return;
      }

      setQueueSize(files.length);
      setIsUploading(true);
      for (const file of files) {
        try {
          await uploadFile(file);
          completed += 1;
          setMessage(`Uploaded ${completed} of ${files.length} ${files.length === 1 ? 'sheet' : 'sheets'}.`);
        } catch (uploadError) {
          failures.push({
            fileName: file.name,
            reason: uploadError instanceof Error ? uploadError.message : 'The server could not accept this file.',
          });
        }
      }

      if (failures.length) {
        if (completed) {
          setMessage(`${completed} of ${files.length} ${files.length === 1 ? 'sheet' : 'sheets'} uploaded and stored successfully.`);
        }
        const failureDetails = failures.map(({ fileName, reason }) => `${fileName}: ${reason}`).join(' ');
        setError(
          failures.length === 1
            ? `${failures[0].fileName} could not be uploaded: ${failures[0].reason}`
            : `${failures.length} files could not be uploaded. ${failureDetails}`,
        );
      } else {
        setMessage(`${files.length} ${files.length === 1 ? 'sheet' : 'sheets'} uploaded and stored successfully.`);
      }
    } catch (uploadError) {
      const reason = uploadError instanceof Error ? uploadError.message : 'The upload could not be completed.';
      if (completed) {
        setMessage(`${completed} of ${files.length} ${files.length === 1 ? 'sheet' : 'sheets'} uploaded successfully.`);
      }
      setError(completed ? `Some uploads could not be completed: ${reason}` : `Upload failed: ${reason}`);
    } finally {
      setIsUploading(false);
      setQueueSize(0);
      uploadInFlightRef.current = false;
      if (inputRef.current) inputRef.current.value = '';
    }
  };

  const selectFile = (event: ChangeEvent<HTMLInputElement>) => {
    void uploadFiles(Array.from(event.target.files ?? []));
  };

  const dropFile = (event: DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    setIsDragging(false);
    if (!uploadInFlightRef.current) void uploadFiles(Array.from(event.dataTransfer.files));
  };

  const description = mode === 'single'
    ? 'Upload one answer sheet.'
    : mode === 'multiple'
      ? 'Upload several answer sheets; each file is stored separately.'
      : 'Upload a batch of answer sheets one file at a time.';

  return (
    <section className="surface-card upload-card" aria-labelledby="upload-title">
      <div className="card-heading">
        <div>
          <h2 id="upload-title">Evaluate Answer Sheets</h2>
          <p id="upload-mode-description" className="sr-only">{description}</p>
        </div>
      </div>

      <div className="upload-tabs" role="group" aria-label="Upload mode">
        {([['single', 'Single Sheet'], ['multiple', 'Multiple Sheets'], ['bulk', 'Bulk Upload']] as const).map(([value, label]) => (
          <button
            key={value}
            className={`upload-tab${mode === value ? ' upload-tab-active' : ''}`}
            type="button"
            aria-pressed={mode === value}
            disabled={isUploading}
            onClick={() => {
              if (uploadInFlightRef.current) return;
              setMode(value);
              setMessage('');
              setError('');
            }}
          >
            {label}
          </button>
        ))}
      </div>

      <div
        className={`upload-dropzone${isDragging ? ' upload-dropzone-dragging' : ''}`}
        onDragEnter={(event) => { event.preventDefault(); if (!uploadInFlightRef.current) setIsDragging(true); }}
        onDragOver={(event) => { event.preventDefault(); if (!uploadInFlightRef.current) event.dataTransfer.dropEffect = 'copy'; }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={dropFile}
        aria-busy={isUploading}
        aria-describedby="upload-helper upload-limits"
      >
        <input
          ref={inputRef}
          id="answer-sheet-file"
          className="sr-only"
          type="file"
          name="answer-sheet-file"
          accept=".jpg,.jpeg,.png,.pdf"
          multiple={mode !== 'single'}
          aria-label="Answer sheet files"
          aria-describedby="upload-mode-description upload-helper upload-limits"
          onChange={selectFile}
          disabled={isUploading}
        />
        <span className="upload-icon"><CloudUpload size={27} strokeWidth={1.9} aria-hidden="true" /></span>
        <span className="upload-title">{isUploading ? 'Uploading…' : 'Upload Answer Sheet'}</span>
        <span id="upload-helper" className="upload-helper">Drag & drop {mode === 'single' ? 'an image or PDF file' : 'your files'} here, or use Choose File</span>
        <span id="upload-limits" className="upload-limits">Supports JPG, PNG, PDF · Max 10&nbsp;MB per file</span>
        <button className="upload-cta" type="button" onClick={() => inputRef.current?.click()} disabled={isUploading}>
          <CloudUpload size={15} aria-hidden="true" /> {isUploading ? 'Uploading…' : 'Choose File'}
        </button>
      </div>
      {queueSize > 0 && <p className="upload-queue" role="status" aria-live="polite">Uploading {queueSize} {queueSize === 1 ? 'sheet' : 'sheets'} one at a time…</p>}
      {error && <p className="upload-error" role="alert">{error}</p>}
      {message && <p className="upload-message" role="status" aria-live="polite">{message}</p>}
    </section>
  );
}
