'use client';

import { useEffect, useState } from 'react';

export interface ResearchHistoryItem {
  job_id: string;
  idea?: string;
  industry?: string;
  created_at?: string;
  innovation_score?: number;
}

/** Fetches the signed-in user's saved research history for job-ID pickers. */
export function useResearchHistory() {
  const [history, setHistory] = useState<ResearchHistoryItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        const userRes = await fetch('/api/users/me', { credentials: 'include' });
        if (!userRes.ok) return;
        const user = await userRes.json();
        if (!user?.id) return;
        const res = await fetch(`/api/agents/research/history/${user.id}`, { credentials: 'include' });
        if (!res.ok) return;
        const data = await res.json();
        if (Array.isArray(data?.history)) setHistory(data.history);
      } catch {
        // history picker is a convenience — fail silently, manual job ID entry still works
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  return { history, loading };
}
