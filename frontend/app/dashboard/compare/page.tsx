'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  GitCompare, Play, AlertTriangle, Trophy, Minus,
  TrendingUp, TrendingDown, CheckCircle, ArrowRight,
  BarChart3, Building2, Target, Zap, Shield,
} from 'lucide-react';
import { GlassCard, GlassCardContent, GlassCardHeader } from '@/components/ui/glass-card';
import { AnimatedButton } from '@/components/ui/animated-button';
import { loadLastResearch } from '@/lib/research-store';
import { ResearchHistoryItem, useResearchHistory } from '@/lib/use-research-history';
import { ResearchPicker } from '@/components/dashboard/research-picker';

// ─── Types ────────────────────────────────────────────────────────────────────

interface DimensionRow {
  dimension: string;
  score_a: number;
  score_b: number;
  delta: string;
  winner: string;
}

interface MetaInfo {
  idea: string;
  industry: string;
  overall_score: number;
  innovation_grade: string;
  risk_level: string;
  market_size: string;
  growth_rate: string;
  executive_summary: string;
}

interface IdeaComparison {
  label_a: string;
  label_b: string;
  meta_a: MetaInfo;
  meta_b: MetaInfo;
  dimensions: DimensionRow[];
  overall_score_a: number;
  overall_score_b: number;
  overall_winner: string;
  wins_a: number;
  wins_b: number;
  ties: number;
  advantages_a: string[];
  advantages_b: string[];
  recommendation: string;
}

interface CompetitorItem {
  name: string;
  threat_level: string;
  market_share: string;
  strengths: string[];
  weaknesses: string[];
}

interface CompetitorComparison {
  label_a: string;
  label_b: string;
  saturation_a: number;
  saturation_b: number;
  entry_ease_a: number;
  entry_ease_b: number;
  easier_market: string;
  high_threat_count_a: number;
  high_threat_count_b: number;
  competitors_a: CompetitorItem[];
  competitors_b: CompetitorItem[];
  differentiation_opps_a: string[];
  differentiation_opps_b: string[];
  landscape_a: string;
  landscape_b: string;
  verdict: string;
}

// ─── Helpers ──────────────────────────────────────────────────────────────────

function ScoreBar({ score, color }: { score: number; color: string }) {
  return (
    <div className="flex items-center gap-2 w-full">
      <div className="flex-1 h-1.5 bg-white/10 rounded-full overflow-hidden">
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${score}%` }}
          transition={{ duration: 0.8, ease: 'easeOut' }}
          className={`h-full rounded-full ${color}`}
        />
      </div>
      <span className="text-xs text-gray-300 w-8 text-right">{score}</span>
    </div>
  );
}

function WinnerBadge({ winner, label_a, label_b }: { winner: string; label_a: string; label_b: string }) {
  if (winner === 'tie') return <span className="text-xs text-gray-400">Tie</span>;
  if (winner === label_a) return <span className="text-xs text-violet-300 font-semibold">← A</span>;
  return <span className="text-xs text-cyan-300 font-semibold">B →</span>;
}

function ThreatBadge({ level }: { level: string }) {
  const cfg: Record<string, string> = {
    high:   'bg-red-500/15 text-red-400 border-red-500/30',
    medium: 'bg-amber-500/15 text-amber-400 border-amber-500/30',
    low:    'bg-emerald-500/15 text-emerald-400 border-emerald-500/30',
  };
  return (
    <span className={`text-xs px-2 py-0.5 rounded-full border capitalize ${cfg[level] ?? cfg.medium}`}>
      {level}
    </span>
  );
}

// ─── Job Input Row ─────────────────────────────────────────────────────────────

function JobInputRow({ label, color, value, onChange, history, historyLoading }: {
  label: string; color: string; value: string; onChange: (v: string) => void;
  history: ResearchHistoryItem[]; 
  historyLoading: boolean;
}) {
  return (
    <div className="space-y-2">
      <label className={`text-xs font-semibold ${color} mb-1 block`}>{label}</label>
      <ResearchPicker
        history={history}
        loading={historyLoading}
        onSelect={onChange}
        placeholder="Pick from your research history…"
        className="py-2 text-xs"
      />
      <input
        value={value}
        onChange={e => onChange(e.target.value)}
        placeholder="Paste a completed research job ID"
        className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-2.5 text-white text-sm placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-violet-500/50"
      />
    </div>
  );
}

// ─── Main Page ─────────────────────────────────────────────────────────────────

export default function ComparePage() {
  const lastJobId = loadLastResearch()?.jobId ?? '';
  const { history, loading: historyLoading } = useResearchHistory();

  const [tab, setTab]         = useState<'ideas' | 'competitors'>('ideas');
  const [jobIdA, setJobIdA]   = useState(lastJobId);
  const [jobIdB, setJobIdB]   = useState('');
  const [labelA, setLabelA]   = useState('Idea A');
  const [labelB, setLabelB]   = useState('Idea B');
  const [loading, setLoading] = useState(false);
  const [error, setError]     = useState<string | null>(null);
  const [ideaResult, setIdeaResult]         = useState<IdeaComparison | null>(null);
  const [competitorResult, setCompetitorResult] = useState<CompetitorComparison | null>(null);

  async function runCompare() {
    if (!jobIdA.trim() || !jobIdB.trim()) return;
    setLoading(true);
    setError(null);
    setIdeaResult(null);
    setCompetitorResult(null);
    try {
      const params = new URLSearchParams({
        job_id_a: jobIdA.trim(),
        job_id_b: jobIdB.trim(),
        label_a: labelA || 'Idea A',
        label_b: labelB || 'Idea B',
      });
      const [ideasRes, compRes] = await Promise.all([
        fetch(`/api/agents/compare/ideas?${params}`),
        fetch(`/api/agents/compare/competitors?${params}`),
      ]);
      if (!ideasRes.ok) throw new Error(await ideasRes.text());
      if (!compRes.ok)  throw new Error(await compRes.text());
      setIdeaResult(await ideasRes.json());
      setCompetitorResult(await compRes.json());
    } catch (e: any) {
      setError(e.message ?? 'Comparison failed');
    } finally {
      setLoading(false);
    }
  }

  const hasResult = ideaResult || competitorResult;

  return (
    <div className="min-h-screen p-6 space-y-6">
      {/* Header */}
      <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }}>
        <div className="flex items-center gap-3 mb-1">
          <div className="p-2 rounded-xl bg-gradient-to-br from-cyan-500 to-blue-600">
            <GitCompare className="w-6 h-6 text-white" />
          </div>
          <h1 className="text-2xl font-bold text-white">Compare Ideas</h1>
        </div>
        <p className="text-gray-400 ml-14">
          Side-by-side comparison of two research jobs — ideas and competitive landscapes.
        </p>
      </motion.div>

      {/* Inputs */}
      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
        <GlassCard>
          <GlassCardHeader>
            <span className="text-white font-semibold">Select Two Research Jobs</span>
          </GlassCardHeader>
          <GlassCardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-3">
                <JobInputRow label="Idea A — Job ID" color="text-violet-300" value={jobIdA} onChange={setJobIdA} history={history} historyLoading={historyLoading} />
                <div>
                  <label className="text-xs text-gray-400 mb-1 block">Label (optional)</label>
                  <input
                    value={labelA}
                    onChange={e => setLabelA(e.target.value)}
                    placeholder="e.g. AI Invoice Tool"
                    className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-2 text-white text-sm placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-violet-500/50"
                  />
                </div>
              </div>
              <div className="space-y-3">
                <JobInputRow label="Idea B — Job ID" color="text-cyan-300" value={jobIdB} onChange={setJobIdB} history={history} historyLoading={historyLoading} />
                <div>
                  <label className="text-xs text-gray-400 mb-1 block">Label (optional)</label>
                  <input
                    value={labelB}
                    onChange={e => setLabelB(e.target.value)}
                    placeholder="e.g. HR Automation SaaS"
                    className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-2 text-white text-sm placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-violet-500/50"
                  />
                </div>
              </div>
            </div>

            <AnimatedButton
              onClick={runCompare}
              disabled={!jobIdA.trim() || !jobIdB.trim() || loading}
              className="w-full"
            >
              {loading ? (
                <span className="flex items-center gap-2">
                  <svg className="animate-spin w-4 h-4" viewBox="0 0 24 24" fill="none">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z" />
                  </svg>
                  Comparing…
                </span>
              ) : (
                <span className="flex items-center gap-2">
                  <Play className="w-4 h-4" /> Compare Both Jobs
                </span>
              )}
            </AnimatedButton>

            {error && (
              <div className="flex items-start gap-2 p-4 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 text-sm">
                <AlertTriangle className="w-4 h-4 mt-0.5 shrink-0" /> {error}
              </div>
            )}
          </GlassCardContent>
        </GlassCard>
      </motion.div>

      {/* Results */}
      <AnimatePresence>
        {hasResult && (
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="space-y-5">
            {/* Tabs */}
            <div className="flex gap-2">
              {(['ideas', 'competitors'] as const).map(t => (
                <button
                  key={t}
                  onClick={() => setTab(t)}
                  className={`px-5 py-2 rounded-lg text-sm font-medium transition-all ${
                    tab === t
                      ? 'bg-white/10 text-white border border-white/20'
                      : 'text-gray-400 hover:text-white'
                  }`}
                >
                  {t === 'ideas' ? (
                    <span className="flex items-center gap-1.5"><BarChart3 className="w-4 h-4" /> Ideas</span>
                  ) : (
                    <span className="flex items-center gap-1.5"><Building2 className="w-4 h-4" /> Competitors</span>
                  )}
                </button>
              ))}
            </div>

            {/* Ideas Tab */}
            {tab === 'ideas' && ideaResult && (
              <div className="space-y-5">
                {/* Score overview cards */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {[
                    { meta: ideaResult.meta_a, score: ideaResult.overall_score_a, label: ideaResult.label_a, wins: ideaResult.wins_a, color: 'from-violet-500 to-purple-600', bar: 'bg-violet-500', winner: ideaResult.overall_winner === ideaResult.label_a },
                    { meta: ideaResult.meta_b, score: ideaResult.overall_score_b, label: ideaResult.label_b, wins: ideaResult.wins_b, color: 'from-cyan-500 to-blue-600', bar: 'bg-cyan-500', winner: ideaResult.overall_winner === ideaResult.label_b },
                  ].map(({ meta, score, label, wins, color, bar, winner }) => (
                    <GlassCard key={label} className={winner ? 'ring-1 ring-white/20' : ''}>
                      <GlassCardContent className="pt-4">
                        <div className="flex items-start justify-between mb-3">
                          <div>
                            <p className={`text-xs font-bold bg-gradient-to-r ${color} bg-clip-text text-transparent`}>{label}</p>
                            <p className="text-white font-semibold text-sm mt-0.5 line-clamp-1">{meta.idea}</p>
                            <p className="text-gray-500 text-xs">{meta.industry}</p>
                          </div>
                          {winner && (
                            <span className="flex items-center gap-1 text-xs text-amber-400 bg-amber-500/10 border border-amber-500/20 rounded-full px-2 py-0.5">
                              <Trophy className="w-3 h-3" /> Winner
                            </span>
                          )}
                        </div>
                        <div className="mb-3">
                          <div className="flex justify-between text-xs text-gray-400 mb-1">
                            <span>Overall Score</span>
                            <span className="text-white font-semibold">{score}/100</span>
                          </div>
                          <ScoreBar score={score} color={bar} />
                        </div>
                        <div className="grid grid-cols-3 gap-2 text-xs">
                          <div className="text-center p-1.5 bg-white/5 rounded-lg">
                            <p className="text-gray-400">Grade</p>
                            <p className="text-white font-bold">{meta.innovation_grade}</p>
                          </div>
                          <div className="text-center p-1.5 bg-white/5 rounded-lg">
                            <p className="text-gray-400">Risk</p>
                            <p className="text-white font-bold capitalize">{meta.risk_level}</p>
                          </div>
                          <div className="text-center p-1.5 bg-white/5 rounded-lg">
                            <p className="text-gray-400">Wins</p>
                            <p className="text-white font-bold">{wins}</p>
                          </div>
                        </div>
                      </GlassCardContent>
                    </GlassCard>
                  ))}
                </div>

                {/* Dimension table */}
                <GlassCard>
                  <GlassCardHeader>
                    <span className="text-white font-semibold">Dimension Breakdown</span>
                  </GlassCardHeader>
                  <GlassCardContent>
                    <div className="space-y-3">
                      {ideaResult.dimensions.map((d, i) => (
                        <motion.div
                          key={d.dimension}
                          initial={{ opacity: 0, x: -10 }}
                          animate={{ opacity: 1, x: 0 }}
                          transition={{ delay: i * 0.04 }}
                          className="grid grid-cols-[1fr_60px_60px_50px] items-center gap-3 py-2 border-b border-white/5 last:border-0"
                        >
                          <span className="text-gray-300 text-sm">{d.dimension}</span>
                          <ScoreBar score={d.score_a} color="bg-violet-500" />
                          <ScoreBar score={d.score_b} color="bg-cyan-500" />
                          <WinnerBadge winner={d.winner} label_a={ideaResult.label_a} label_b={ideaResult.label_b} />
                        </motion.div>
                      ))}
                    </div>
                    <div className="flex items-center gap-3 text-xs text-gray-500 mt-4 pt-3 border-t border-white/5">
                      <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-violet-500 inline-block" />{ideaResult.label_a}</span>
                      <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-cyan-500 inline-block" />{ideaResult.label_b}</span>
                    </div>
                  </GlassCardContent>
                </GlassCard>

                {/* Recommendation */}
                {ideaResult.recommendation && (
                  <GlassCard>
                    <GlassCardContent className="py-4">
                      <div className="flex items-start gap-3">
                        <CheckCircle className="w-5 h-5 text-emerald-400 shrink-0 mt-0.5" />
                        <p className="text-gray-300 text-sm leading-relaxed">{ideaResult.recommendation}</p>
                      </div>
                    </GlassCardContent>
                  </GlassCard>
                )}
              </div>
            )}

            {/* Competitors Tab */}
            {tab === 'competitors' && competitorResult && (
              <div className="space-y-5">
                {/* Saturation */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {[
                    { label: competitorResult.label_a, sat: competitorResult.saturation_a, ease: competitorResult.entry_ease_a, ht: competitorResult.high_threat_count_a, winner: competitorResult.easier_market === competitorResult.label_a, bar: 'bg-violet-500' },
                    { label: competitorResult.label_b, sat: competitorResult.saturation_b, ease: competitorResult.entry_ease_b, ht: competitorResult.high_threat_count_b, winner: competitorResult.easier_market === competitorResult.label_b, bar: 'bg-cyan-500' },
                  ].map(({ label, sat, ease, ht, winner, bar }) => (
                    <GlassCard key={label} className={winner ? 'ring-1 ring-white/20' : ''}>
                      <GlassCardContent className="pt-4 space-y-3">
                        <div className="flex items-center justify-between">
                          <span className="text-white font-semibold text-sm">{label}</span>
                          {winner && <span className="text-xs text-emerald-400 flex items-center gap-1"><Target className="w-3 h-3" /> Easier Market</span>}
                        </div>
                        <div>
                          <div className="flex justify-between text-xs text-gray-400 mb-1">
                            <span>Market Saturation</span><span className="text-white">{sat}/100</span>
                          </div>
                          <ScoreBar score={sat} color={sat > 70 ? 'bg-red-500' : sat > 45 ? 'bg-amber-500' : 'bg-emerald-500'} />
                        </div>
                        <div>
                          <div className="flex justify-between text-xs text-gray-400 mb-1">
                            <span>Entry Ease</span><span className="text-white">{ease}/100</span>
                          </div>
                          <ScoreBar score={ease} color={bar} />
                        </div>
                        <p className="text-xs text-gray-400">
                          <span className="text-red-400 font-semibold">{ht}</span> high-threat competitor{ht !== 1 ? 's' : ''}
                        </p>
                      </GlassCardContent>
                    </GlassCard>
                  ))}
                </div>

                {/* Competitor tables */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                  {[
                    { label: competitorResult.label_a, list: competitorResult.competitors_a, diff: competitorResult.differentiation_opps_a, land: competitorResult.landscape_a },
                    { label: competitorResult.label_b, list: competitorResult.competitors_b, diff: competitorResult.differentiation_opps_b, land: competitorResult.landscape_b },
                  ].map(({ label, list, diff, land }) => (
                    <GlassCard key={label}>
                      <GlassCardHeader>
                        <span className="text-white font-semibold text-sm">{label} — Competitors</span>
                      </GlassCardHeader>
                      <GlassCardContent className="space-y-3">
                        {land && <p className="text-gray-400 text-xs leading-relaxed">{land}</p>}
                        {list.map(c => (
                          <div key={c.name} className="p-3 bg-white/5 rounded-lg border border-white/5">
                            <div className="flex items-center justify-between mb-1.5">
                              <span className="text-white text-sm font-medium">{c.name}</span>
                              <div className="flex items-center gap-2">
                                <ThreatBadge level={c.threat_level} />
                                <span className="text-xs text-gray-400">{c.market_share}</span>
                              </div>
                            </div>
                            {c.weaknesses.length > 0 && (
                              <p className="text-xs text-gray-500">
                                <span className="text-amber-400">Gap: </span>{c.weaknesses[0]}
                              </p>
                            )}
                          </div>
                        ))}
                        {diff.length > 0 && (
                          <div className="pt-2 border-t border-white/5">
                            <p className="text-xs text-gray-400 mb-1.5 font-medium">Differentiation Opportunities</p>
                            <ul className="space-y-1">
                              {diff.slice(0, 3).map((d, i) => (
                                <li key={i} className="text-xs text-gray-300 flex items-start gap-1.5">
                                  <Zap className="w-3 h-3 text-violet-400 shrink-0 mt-0.5" />{d}
                                </li>
                              ))}
                            </ul>
                          </div>
                        )}
                      </GlassCardContent>
                    </GlassCard>
                  ))}
                </div>

                {/* Verdict */}
                {competitorResult.verdict && (
                  <GlassCard>
                    <GlassCardContent className="py-4">
                      <div className="flex items-start gap-3">
                        <Shield className="w-5 h-5 text-cyan-400 shrink-0 mt-0.5" />
                        <p className="text-gray-300 text-sm leading-relaxed">{competitorResult.verdict}</p>
                      </div>
                    </GlassCardContent>
                  </GlassCard>
                )}
              </div>
            )}
          </motion.div>
        )}

        {!hasResult && !loading && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="text-center py-20 text-gray-500"
          >
            <GitCompare className="w-12 h-12 mx-auto mb-4 opacity-30" />
            <p className="text-sm">Enter two job IDs above and click Compare.</p>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
