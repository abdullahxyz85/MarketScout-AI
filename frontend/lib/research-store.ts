const STORAGE_KEY = 'marketscout_last_research';

export interface StoredResearch {
  jobId: string;
  idea?: string;
  industry?: string;
  timestamp: number;
  result: Record<string, unknown>;
}

export function saveLastResearch(jobId: string, result: Record<string, unknown>): void {
  if (typeof window === 'undefined') return;
  try {
    const entry: StoredResearch = {
      jobId,
      idea: (result as any)?.idea ?? '',
      industry: (result as any)?.industry ?? '',
      timestamp: Date.now(),
      result,
    };
    localStorage.setItem(STORAGE_KEY, JSON.stringify(entry));
  } catch {
    // localStorage may be unavailable in some environments
  }
}

export function loadLastResearch(): StoredResearch | null {
  if (typeof window === 'undefined') return null;
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? (JSON.parse(raw) as StoredResearch) : null;
  } catch {
    return null;
  }
}

/** Remove the last research result from localStorage (call on logout). */
export function clearLastResearch(): void {
  if (typeof window === 'undefined') return;
  try {
    localStorage.removeItem(STORAGE_KEY);
  } catch {
    // localStorage may be unavailable
  }
}
