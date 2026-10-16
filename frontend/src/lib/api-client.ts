export const API_BASE = process.env.NEXT_PUBLIC_API_URL || "";

function getBase(): string {
  if (!API_BASE) throw new Error("NEXT_PUBLIC_API_URL not set. Configure in Vercel environment variables before deploying.");
  return API_BASE.replace(/\/$/, "");
}

export async function apiFetch<T>(path: string, opts?: RequestInit): Promise<T> {
  const url = getBase() + path;
  try {
    const res = await fetch(url, { ...opts, signal: AbortSignal.timeout(10000) });
    if (!res.ok) {
      if (res.status === 401) throw new Error("401 Unauthorized — session expired or missing token.");
      if (res.status === 403) throw new Error("403 Forbidden — insufficient role or not resource owner.");
      if (res.status === 404) throw new Error("404 Not found.");
      if (res.status === 413) throw new Error("413 File too large.");
      if (res.status === 422) throw new Error("422 Validation error.");
      if (res.status >= 500) throw new Error(`500 Server error (${res.status}).`);
      throw new Error(`Request failed (${res.status}).`);
    }
    const ct = res.headers.get("content-type") || "";
    if (ct.includes("application/json")) return await res.json() as T;
    return (await res.text()) as unknown as T;
  } catch (e: any) {
    if (e.name === "TimeoutError" || e.name === "DOMException") throw new Error("Request timed out (10s). Check backend URL.");
    if (e.message?.includes("Failed to fetch")) throw new Error("Network error — backend unreachable at NEXT_PUBLIC_API_URL. Check Vercel env var.");
    throw e;
  }
}

export async function checkHealth(): Promise<{ ok: boolean; message: string }> {
  try {
    const res = await fetch(getBase() + "/health", { signal: AbortSignal.timeout(5000) });
    if (!res.ok) return { ok: false, message: `Backend ${res.status}` };
    const data = await res.json();
    return { ok: true, message: data.status || "ok" };
  } catch (e: any) {
    return { ok: false, message: e.message || "Network failure — check NEXT_PUBLIC_API_URL" };
  }
}

export const api = {
  base: () => getBase(),
  health: () => apiFetch<{ status: string }>("/health"),
  evaluations: () => apiFetch<any[]>("/api/v1/evaluations"),
  evaluation: (id: number) => apiFetch<any>(`/api/v1/evaluations/${id}`),
  exams: () => apiFetch<any[]>("/api/v1/exams"),
  sheets: () => apiFetch<any[]>("/api/v1/answer-sheets"),
  upload: (formData: FormData) => apiFetch<any>("/api/v1/answer-sheets", { method: "POST", body: formData }),
};
