'use client';

import { useCallback, useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import {
  ShieldCheck, Star, AlertTriangle, CheckCircle2, XCircle,
  BarChart3, RefreshCw, Globe, FileSearch, Activity,
  TrendingUp, Zap, Info,
} from 'lucide-react';
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell,
} from 'recharts';
import { GlassCard, GlassCardContent, GlassCardHeader } from '@/components/ui/glass-card';
import { AnimatedButton } from '@/components/ui/animated-button';
import { AnimatedBadge } from '@/components/ui/animated-badge';
import { AnimatedProgress } from '@/components/ui/animated-progress';
import { EmptyResearchState } from '@/components/dashboard/empty-research-state';
import { loadLastResearch } from '@/lib/research-store';
import { cn } from '@/lib/utils';

// ── Types ──────────────────────────────────────────────────────────────────────

interface QualityReport {
  pipeline_quality: number;
  hallucination_risk: 'low' | 'medium' | 'high';
  missing_evidence: string[];
  consistency: number;
  overall_grade: string;
  agent_scores: Record<string, number>;
  source_credibility: number;
  warnings: string[];
  summary: string;
}

interface Evidence {
  claim: string;
  agent: string;
  evidence_type: string;
  source_urls: string[];
  strength: 'strong' | 'weak' | 'unknown';
}

interface EvidenceResponse {
  evidences: Evidence[];
  summary: {
    total: number;
    strong_claims: string[];
    weak_claims: string[];
    unknown_claims: string[];
    agents_covered: string[];
  };
  total: number;
}

interface RankedSource {
  url: string;
  stars: number;
  score: number;
  category: string;
  label: string;
}

interface SourcesResponse {
  ranked_sources: RankedSource[];
  top_sources: RankedSource[];
  average_credibility: number;
  total_sources: number;
}

// ── Tooltip style ──────────────────────────────────────────────────────────────

const TOOLTIP = {
  contentStyle: { backgroundColor: 'rgba(10,10,20,0.92)', border: '1px solid rgba(99,102,241,0.3)', borderRadius: '10px', fontSize: 11, color: '#fff' },
  labelStyle: { color: '#94a3b8' },
  itemStyle: { color: '#fff' },
};

// ── Grade badge ────────────────────────────────────────────────────────────────

function GradeBadge({ grade }: { grade: string }) {
  const cfg = {
    A: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/30',
    B: 'text-indigo-400  bg-indigo-500/10  border-indigo-500/30',
    C: 'text-yellow-400  bg-yellow-500/10  border-yellow-500/30',
    D: 'text-orange-400  bg-orange-500/10  border-orange-500/30',
    F: 'text-red-400     bg-red-500/10     border-red-500/30',
  } as Record<string, string>;
  return (
    <div className={cn('w-16 h-16 rounded-2xl border-2 flex items-center justify-center text-3xl font-black', cfg[grade] ?? cfg.F)}>
      {grade}
    </div>
  );
}

// ── Risk pill ──────────────────────────────────────────────────────────────────

function RiskPill({ risk }: { risk: string }) {
  const cfg = {
    low:    { cls: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/25', icon: CheckCircle2  },
    medium: { cls: 'text-yellow-400  bg-yellow-500/10  border-yellow-500/25',  icon: AlertTriangle },
    high:   { cls: 'text-red-400     bg-red-500/10     border-red-500/25',     icon: XCircle       },
  } as const;
  const r = (risk in cfg ? risk : 'high') as keyof typeof cfg;
  const { cls, icon: Icon } = cfg[r];
  return (
    <span className={cn('inline-flex items-center gap-1.5 text-xs font-semibold px-3 py-1 rounded-full border', cls)}>
      <Icon className="w-3.5 h-3.5" />
      {risk.charAt(0).toUpperCase() + risk.slice(1)} Hallucination Risk
    </span>
  );
}

// ── Star row ───────────────────────────────────────────────────────────────────

function StarRow({ stars, max = 5 }: { stars: number; max?: number }) {
  return (
    <span className="flex gap-0.5">
      {Array.from({ length: max }).map((_, i) => (
        <Star key={i} className={cn('w-3 h-3', i < stars ? 'text-yellow-400 fill-yellow-400' : 'text-white/15')} />
      ))}
    </span>
  );
}

// ── Strength badge ─────────────────────────────────────────────────────────────

function StrengthBadge({ strength }: { strength: string }) {
  const cfg = {
    strong:  'text-emerald-400 bg-emerald-500/10',
    weak:    'text-yellow-400  bg-yellow-500/10',
    unknown: 'text-white/40    bg-white/5',
  } as const;
  const s = strength as keyof typeof cfg;
  return (
    <span className={cn('text-[10px] font-semibold px-2 py-0.5 rounded-full capitalize', cfg[s] ?? cfg.unknown)}>
      {strength}
    </span>
  );
}

// ── Section skeleton ──────────────────────────────────────────────────────────

function Skeleton() {
  return (
    <div className="space-y-3 animate-pulse">
      {[1, 2, 3].map(i => (
        <div key={i} className="h-10 rounded-lg bg-white/[0.04]" />
      ))}
    </div>
  );
}

// ── Main Page ──────────────────────────────────────────────────────────────────

export default function QualityPage() {
  const [jobId, setJobId]   = useState('');
  const [quality,  setQuality]  = useState<QualityReport | null>(null);
  const [evidence, setEvidence] = useState<EvidenceResponse | null>(null);
  const [sources,  setSources]  = useState<SourcesResponse | null>(null);
  const [loading,  setLoading]  = useState(false);
  const [error,    setError]    = useState<string | null>(null);
  const [checked,  setChecked]  = useState(false);
  const [agentFilter, setAgentFilter] = useState<string>('all');

  const load = useCallback(async (jid: string) => {
    setLoading(true);
    setError(null);
    try {
      const [qRes, eRes, sRes] = await Promise.all([
        fetch(`/api/agents/research/${jid}/quality-report`),
        fetch(`/api/agents/research/${jid}/evidence`),
        fetch(`/api/agents/research/${jid}/sources`),
      ]);
      if (!qRes.ok) throw new Error(`Quality report: HTTP ${qRes.status}`);
      if (!eRes.ok) throw new Error(`Evidence: HTTP ${eRes.status}`);
      if (!sRes.ok) throw new Error(`Sources: HTTP ${sRes.status}`);
      const [q, e, s] = await Promise.all([qRes.json(), eRes.json(), sRes.json()]);
      setQuality(q);
      setEvidence(e);
      setSources(s);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to load quality data');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    const stored = loadLastResearch();
    if (stored?.jobId) {
      setJobId(stored.jobId);
      load(stored.jobId);
    }
    setChecked(true);
  }, [load]);

  if (!checked) return null;

  if (!jobId) {
    return (
      <div className="space-y-8 max-w-7xl mx-auto">
        <div>
          <h1 className="text-2xl font-bold text-white mb-1">
            Research <span className="bg-gradient-to-r from-indigo-400 to-cyan-400 bg-clip-text text-transparent">Quality</span>
          </h1>
        </div>
        <EmptyResearchState title="No Research Found" description="Run a market research first to view quality metrics." />
      </div>
    );
  }

  // Derived agent scores chart data
  const agentScoreData = quality
    ? Object.entries(quality.agent_scores)
        .map(([k, v]) => ({ agent: k, score: Math.round(v * 100) }))
        .sort((a, b) => b.score - a.score)
    : [];

  // Unique agents for filter
  const agents = evidence
    ? ['all', ...Array.from(new Set(evidence.evidences.map(e => e.agent))).sort()]
    : ['all'];

  const filteredEvidence = evidence
    ? (agentFilter === 'all' ? evidence.evidences : evidence.evidences.filter(e => e.agent === agentFilter))
    : [];

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -8 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-start justify-between gap-4 flex-wrap"
      >
        <div>
          <h1 className="text-2xl font-bold text-white">
            Research{' '}
            <span className="bg-gradient-to-r from-indigo-400 to-cyan-400 bg-clip-text text-transparent">Quality</span>
          </h1>
          <p className="text-sm text-white/40 mt-1">
            Pipeline quality score, evidence grounding, and source credibility
          </p>
        </div>
        <AnimatedButton
          onClick={() => load(jobId)}
          disabled={loading}
          className="gap-2 text-sm"
        >
          <RefreshCw className={cn('w-4 h-4', loading && 'animate-spin')} />
          {loading ? 'Loading…' : 'Refresh'}
        </AnimatedButton>
      </motion.div>

      {/* Error */}
      {error && (
        <div className="p-4 rounded-xl bg-red-500/10 border border-red-500/20 text-sm text-red-300">
          {error}
        </div>
      )}

      {/* ── Section 1: Quality Report ── */}
      <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.05 }}>
        <h2 className="text-xs font-semibold text-white/40 uppercase tracking-widest mb-3 flex items-center gap-2">
          <ShieldCheck className="w-3.5 h-3.5" /> Pipeline Quality Report
        </h2>

        {loading && !quality ? (
          <GlassCard><GlassCardContent className="p-6"><Skeleton /></GlassCardContent></GlassCard>
        ) : quality ? (
          <div className="space-y-4">
            {/* KPI row */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              {[
                { label: 'Pipeline Quality', value: `${Math.round(quality.pipeline_quality * 100)}%`, icon: Activity, color: 'text-indigo-400' },
                { label: 'Source Credibility', value: `${Math.round(quality.source_credibility * 100)}%`, icon: Globe, color: 'text-cyan-400' },
                { label: 'Consistency', value: `${Math.round(quality.consistency * 100)}%`, icon: TrendingUp, color: 'text-emerald-400' },
                { label: 'Missing Agents', value: quality.missing_evidence.length, icon: Zap, color: 'text-yellow-400' },
              ].map(({ label, value, icon: Icon, color }) => (
                <GlassCard key={label}>
                  <GlassCardContent className="p-4">
                    <Icon className={cn('w-4 h-4 mb-2', color)} />
                    <p className="text-xl font-bold text-white">{value}</p>
                    <p className="text-xs text-white/40 mt-0.5">{label}</p>
                  </GlassCardContent>
                </GlassCard>
              ))}
            </div>

            {/* Grade + progress bars + risk */}
            <GlassCard>
              <GlassCardContent className="p-5">
                <div className="flex flex-wrap gap-5 items-start">
                  <div className="flex flex-col items-center gap-2">
                    <GradeBadge grade={quality.overall_grade} />
                    <span className="text-[10px] text-white/40">Overall Grade</span>
                  </div>
                  <div className="flex-1 space-y-3 min-w-[200px]">
                    {[
                      { label: 'Pipeline Quality',  value: quality.pipeline_quality },
                      { label: 'Source Credibility', value: quality.source_credibility },
                      { label: 'Consistency',        value: quality.consistency },
                    ].map(({ label, value }) => (
                      <div key={label}>
                        <div className="flex justify-between text-xs mb-1">
                          <span className="text-white/50">{label}</span>
                          <span className="text-white/70 font-medium">{Math.round(value * 100)}%</span>
                        </div>
                        <AnimatedProgress value={Math.round(value * 100)} className="h-1.5" />
                      </div>
                    ))}
                  </div>
                  <div className="flex flex-col gap-2 pt-1">
                    <RiskPill risk={quality.hallucination_risk} />
                    {quality.missing_evidence.length > 0 && (
                      <div className="flex flex-wrap gap-1 max-w-xs">
                        {quality.missing_evidence.map(m => (
                          <span key={m} className="text-[10px] text-white/40 bg-white/[0.04] border border-white/[0.06] px-2 py-0.5 rounded-full">
                            {m}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                </div>

                {quality.summary && (
                  <p className="mt-4 pt-4 border-t border-white/[0.06] text-sm text-white/50 leading-relaxed">
                    {quality.summary}
                  </p>
                )}
              </GlassCardContent>
            </GlassCard>

            {/* Agent scores chart */}
            {agentScoreData.length > 0 && (
              <GlassCard>
                <GlassCardHeader>
                  <span className="text-sm font-medium text-white flex items-center gap-2">
                    <BarChart3 className="w-4 h-4 text-indigo-400" /> Agent Confidence Scores
                  </span>
                </GlassCardHeader>
                <GlassCardContent className="px-2 pb-4">
                  <ResponsiveContainer width="100%" height={180}>
                    <BarChart data={agentScoreData} margin={{ top: 4, right: 8, left: -24, bottom: 4 }}>
                      <XAxis dataKey="agent" tick={{ fontSize: 10, fill: '#64748b' }} axisLine={false} tickLine={false} />
                      <YAxis domain={[0, 100]} tick={{ fontSize: 10, fill: '#64748b' }} axisLine={false} tickLine={false} />
                      <Tooltip {...TOOLTIP} formatter={(v: number) => [`${v}%`, 'Score']} cursor={{ fill: 'rgba(255,255,255,0.05)' }} />
                      <Bar dataKey="score" radius={[4, 4, 0, 0]} activeBar={{ fillOpacity: 0.7, stroke: 'transparent' }}>
                        {agentScoreData.map((d, i) => (
                          <Cell key={i} fill={d.score >= 80 ? '#10b981' : d.score >= 60 ? '#6366f1' : '#f59e0b'} />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </GlassCardContent>
              </GlassCard>
            )}

            {/* Warnings */}
            {quality.warnings.length > 0 && (
              <GlassCard>
                <GlassCardHeader>
                  <span className="text-sm font-medium text-yellow-400 flex items-center gap-2">
                    <AlertTriangle className="w-4 h-4" /> Warnings ({quality.warnings.length})
                  </span>
                </GlassCardHeader>
                <GlassCardContent>
                  <p className="flex items-start gap-1.5 text-[11px] text-white/35 mb-3 pb-3 border-b border-white/[0.06]">
                    <Info className="w-3.5 h-3.5 flex-shrink-0 mt-0.5" />
                    These are automated checks on this run's own data (missing fields, unparsed LLM output, empty citations) — not app errors. They flag where this report's evidence is thin, so treat them as a trust signal, not a bug report.
                  </p>
                  <ul className="space-y-1.5">
                    {quality.warnings.map((w, i) => (
                      <li key={i} className="text-xs text-white/50 flex gap-2">
                        <span className="text-yellow-400/60 flex-shrink-0 mt-0.5">⚠</span>{w}
                      </li>
                    ))}
                  </ul>
                </GlassCardContent>
              </GlassCard>
            )}
          </div>
        ) : null}
      </motion.div>

      {/* ── Section 2: Evidence Engine ── */}
      <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
        <h2 className="text-xs font-semibold text-white/40 uppercase tracking-widest mb-3 flex items-center gap-2">
          <FileSearch className="w-3.5 h-3.5" /> Evidence Analysis
        </h2>

        {loading && !evidence ? (
          <GlassCard><GlassCardContent className="p-6"><Skeleton /></GlassCardContent></GlassCard>
        ) : evidence ? (
          <div className="space-y-3">
            {/* Summary stats */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              {[
                { label: 'Total Evidence',   value: evidence.total,                           color: 'text-indigo-400' },
                { label: 'Strong Claims',    value: evidence.summary.strong_claims?.length ?? 0,  color: 'text-emerald-400' },
                { label: 'Weak Claims',      value: evidence.summary.weak_claims?.length ?? 0,    color: 'text-yellow-400' },
                { label: 'Agents Covered',   value: evidence.summary.agents_covered?.length ?? 0, color: 'text-cyan-400' },
              ].map(({ label, value, color }) => (
                <GlassCard key={label}>
                  <GlassCardContent className="p-4">
                    <p className={cn('text-2xl font-bold', color)}>{value}</p>
                    <p className="text-xs text-white/40 mt-0.5">{label}</p>
                  </GlassCardContent>
                </GlassCard>
              ))}
            </div>

            {/* Filter + table */}
            <GlassCard>
              <GlassCardHeader className="flex items-center justify-between flex-wrap gap-3">
                <span className="text-sm font-medium text-white">Evidence Claims</span>
                <div className="flex gap-1 flex-wrap">
                  {agents.map(a => (
                    <button
                      key={a}
                      onClick={() => setAgentFilter(a)}
                      className={cn(
                        'text-[10px] px-2.5 py-1 rounded-full border transition-all capitalize',
                        agentFilter === a
                          ? 'bg-indigo-500/20 border-indigo-500/30 text-white'
                          : 'border-white/[0.08] text-white/40 hover:text-white/70 hover:border-white/20',
                      )}
                    >
                      {a}
                    </button>
                  ))}
                </div>
              </GlassCardHeader>
              <GlassCardContent>
                {filteredEvidence.length === 0 ? (
                  <p className="text-sm text-white/30 py-6 text-center">No evidence claims for this filter.</p>
                ) : (
                  <div className="space-y-2 max-h-72 overflow-y-auto pr-1">
                    {filteredEvidence.map((ev, i) => (
                      <div key={i} className="flex items-start gap-3 p-3 rounded-lg bg-white/[0.02] hover:bg-white/[0.04] transition-colors">
                        <StrengthBadge strength={ev.strength} />
                        <div className="flex-1 min-w-0">
                          <p className="text-xs text-white/70 leading-relaxed line-clamp-2">{ev.claim}</p>
                          <div className="flex gap-2 mt-1 flex-wrap">
                            <span className="text-[10px] text-indigo-400/70">{ev.agent}</span>
                            <span className="text-[10px] text-white/25">·</span>
                            <span className="text-[10px] text-white/35 capitalize">{ev.evidence_type}</span>
                            {ev.source_urls.length > 0 && (
                              <>
                                <span className="text-[10px] text-white/25">·</span>
                                <span className="text-[10px] text-white/30">{ev.source_urls.length} source{ev.source_urls.length > 1 ? 's' : ''}</span>
                              </>
                            )}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </GlassCardContent>
            </GlassCard>
          </div>
        ) : null}
      </motion.div>

      {/* ── Section 3: Source Credibility ── */}
      <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.15 }}>
        <h2 className="text-xs font-semibold text-white/40 uppercase tracking-widest mb-3 flex items-center gap-2">
          <Globe className="w-3.5 h-3.5" /> Source Credibility
        </h2>

        {loading && !sources ? (
          <GlassCard><GlassCardContent className="p-6"><Skeleton /></GlassCardContent></GlassCard>
        ) : sources ? (
          <div className="space-y-3">
            {/* Credibility KPIs */}
            <div className="grid grid-cols-3 gap-3">
              {[
                { label: 'Total Sources',      value: sources.total_sources,                        color: 'text-indigo-400' },
                { label: 'Avg Credibility',    value: `${Math.round(sources.average_credibility * 100)}%`, color: 'text-emerald-400' },
                { label: 'Top-Tier Sources',   value: sources.top_sources.filter(s => s.stars >= 4).length, color: 'text-yellow-400' },
              ].map(({ label, value, color }) => (
                <GlassCard key={label}>
                  <GlassCardContent className="p-4">
                    <p className={cn('text-2xl font-bold', color)}>{value}</p>
                    <p className="text-xs text-white/40 mt-0.5">{label}</p>
                  </GlassCardContent>
                </GlassCard>
              ))}
            </div>

            {/* Avg credibility bar */}
            <GlassCard>
              <GlassCardContent className="p-5">
                <div className="flex items-center justify-between text-xs mb-2">
                  <span className="text-white/50">Average source credibility</span>
                  <span className="text-white/70 font-semibold">{Math.round(sources.average_credibility * 100)}%</span>
                </div>
                <AnimatedProgress value={Math.round(sources.average_credibility * 100)} className="h-2" />
                <p className="text-[10px] text-white/30 mt-2 flex items-center gap-1.5">
                  <Info className="w-3 h-3" />
                  Based on domain authority: PubMed/Nature=5★, Reuters/Bloomberg=4★, TechCrunch=3★, LinkedIn=2★, unknown=1★
                </p>
              </GlassCardContent>
            </GlassCard>

            {/* Ranked list */}
            <GlassCard>
              <GlassCardHeader>
                <span className="text-sm font-medium text-white">All Sources — Ranked by Credibility</span>
              </GlassCardHeader>
              <GlassCardContent>
                {sources.ranked_sources.length === 0 ? (
                  <p className="text-sm text-white/30 py-6 text-center">No sources found in research results.</p>
                ) : (
                  <div className="space-y-1.5 max-h-80 overflow-y-auto pr-1">
                    {sources.ranked_sources.map((src, i) => (
                      <div
                        key={i}
                        className="flex items-center gap-3 p-2.5 rounded-lg hover:bg-white/[0.03] transition-colors group"
                      >
                        <StarRow stars={src.stars} />
                        <div className="flex-1 min-w-0">
                          <a
                            href={src.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-xs text-indigo-300/80 hover:text-indigo-300 truncate block group-hover:underline"
                            onClick={e => e.stopPropagation()}
                          >
                            {src.url}
                          </a>
                          <span className="text-[10px] text-white/30 capitalize">{src.category?.replace(/_/g, ' ')}</span>
                        </div>
                        <div className="text-right flex-shrink-0">
                          <p className="text-xs font-semibold text-white/60">{Math.round(src.score * 100)}%</p>
                          <p className="text-[10px] text-white/25">{src.label}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </GlassCardContent>
            </GlassCard>
          </div>
        ) : null}
      </motion.div>

      {/* Bottom padding */}
      <div className="h-4" />
    </div>
  );
}
