'use client';

import { createContext, useCallback, useContext, useRef, useState, ReactNode } from 'react';
import { saveLastResearch } from '@/lib/research-store';

export type Stage = 'input' | 'running' | 'done';

export interface ResearchResult {
  report?: {
    executive_summary?: string;
    market_score?: number;
    opportunity_score?: number;
    competition_level?: string;
    recommendations?: string[];
    key_metrics?: Record<string, string>;
  };
  innovation_score?: { innovation_score?: number; grade?: string; score_explanation?: string };
  risks?: { overall_risk_level?: string };
  knowledge_graph?: { nodes: any[]; links: any[] };
  [key: string]: unknown;
}

interface ResearchContextValue {
  idea: string;
  setIdea: (v: string) => void;
  selectedIndustry: string;
  setSelectedIndustry: (v: string) => void;
  healthcareMode: boolean;
  setHealthcareMode: (v: boolean) => void;
  stage: Stage;
  activeAgentIdx: number;
  activeAgentName: string;
  progress: number;
  result: ResearchResult | null;
  jobId: string | null;
  error: string | null;
  startResearch: (agentNames: string[]) => Promise<void>;
  resetForm: () => void;
}

const ResearchContext = createContext<ResearchContextValue | null>(null);

export function ResearchProvider({ children }: { children: ReactNode }) {
  const [idea, setIdea] = useState('');
  const [selectedIndustry, setSelectedIndustry] = useState('');
  const [healthcareMode, setHealthcareMode] = useState(false);
  const [stage, setStage] = useState<Stage>('input');
  const [activeAgentIdx, setActiveAgentIdx] = useState(0);
  const [activeAgentName, setActiveAgentName] = useState('');
  const [progress, setProgress] = useState(0);
  const [result, setResult] = useState<ResearchResult | null>(null);
  const [jobId, setJobId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const evtSourceRef = useRef<EventSource | null>(null);

  const startResearch = useCallback(async (agentNames: string[]) => {
    if (!idea.trim()) return;
    // Close any previous stream still open
    evtSourceRef.current?.close();
    setStage('running');
    setProgress(0);
    setActiveAgentIdx(0);
    setActiveAgentName(agentNames[0] ?? '');
    setError(null);
    setResult(null);
    try {
      const res = await fetch('/api/agents/research/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        // user_id is derived server-side from the JWT cookie — never sent from client
        body: JSON.stringify({ idea, industry: selectedIndustry, healthcare_mode: healthcareMode }),
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error((err as any).detail ?? `HTTP ${res.status}`);
      }
      const { job_id } = await res.json();
      setJobId(job_id);
      const evtSource = new EventSource(`/api/agents/research/${job_id}/stream`);
      evtSourceRef.current = evtSource;
      evtSource.onmessage = (e: MessageEvent) => {
        try {
          const data = JSON.parse(e.data);
          if (data.heartbeat) return;
          if (typeof data.progress === 'number' && data.progress >= 0) setProgress(data.progress);
          if (data.current_agent && data.current_agent !== 'Complete') {
            setActiveAgentName(data.current_agent);
            const idx = agentNames.findIndex((n) => n === data.current_agent);
            if (idx !== -1) setActiveAgentIdx(idx);
          }
          if (data.done) {
            evtSource.close();
            evtSourceRef.current = null;
            if (data.error) {
              setError(data.error);
              setStage('input');
            } else {
              const r: ResearchResult = data.result ?? {};
              setResult(r);
              saveLastResearch(job_id, r as Record<string, unknown>);
              setStage('done');
            }
          }
        } catch { /* ignore individual parse errors */ }
      };
      evtSource.onerror = () => {
        evtSource.close();
        evtSourceRef.current = null;
        setError('Connection error. Please check the agent service and try again.');
        setStage('input');
      };
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      setStage('input');
    }
  }, [idea, selectedIndustry, healthcareMode]);

  const resetForm = useCallback(() => {
    evtSourceRef.current?.close();
    evtSourceRef.current = null;
    setStage('input');
    setIdea('');
    setSelectedIndustry('');
    setHealthcareMode(false);
    setProgress(0);
    setActiveAgentIdx(0);
    setResult(null);
    setError(null);
    setJobId(null);
  }, []);

  const value: ResearchContextValue = {
    idea, setIdea,
    selectedIndustry, setSelectedIndustry,
    healthcareMode, setHealthcareMode,
    stage, activeAgentIdx, activeAgentName, progress, result, jobId, error,
    startResearch, resetForm,
  };

  return <ResearchContext.Provider value={value}>{children}</ResearchContext.Provider>;
}

export function useResearch() {
  const ctx = useContext(ResearchContext);
  if (!ctx) throw new Error('useResearch must be used within ResearchProvider');
  return ctx;
}
