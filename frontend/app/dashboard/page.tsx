'use client';

import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import Link from 'next/link';
import {
  BarChart3, TrendingUp, Building2, Activity, Download,
  RefreshCw, Zap, Clock, Users, Target, ShieldAlert,
  Lightbulb, ChevronRight, FileText, HeartPulse, ShieldCheck,
} from 'lucide-react';
import {
  ResponsiveContainer, PieChart, Pie, Cell, Tooltip,
  RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis,
} from 'recharts';
import { GlassCard, GlassCardContent, GlassCardHeader } from '@/components/ui/glass-card';
import { AnimatedProgress } from '@/components/ui/animated-progress';
import { AnimatedBadge, StatusBadge } from '@/components/ui/animated-badge';
import { AnimatedButton } from '@/components/ui/animated-button';
import { EmptyResearchState } from '@/components/dashboard/empty-research-state';
import { loadLastResearch, saveLastResearch } from '@/lib/research-store';
import { getAgentStatuses } from '@/lib/agents';

/* ── Recharts shared styles ── */
const tooltipStyle = {
  contentStyle: {
    backgroundColor: 'rgba(10,10,20,0.92)',
    border: '1px solid rgba(99,102,241,0.3)',
    borderRadius: '12px',
    fontSize: 12,
    color: '#fff',
  },
  labelStyle: { color: '#94a3b8' },
  itemStyle: { color: '#fff' },
};

const PIE_COLORS = ['#6366f1', '#a855f7', '#06b6d4', '#10b981', '#f59e0b'];

interface HistoryItem {
  job_id: string;
  idea?: string;
  industry?: string;
  created_at?: string;
  innovation_score?: number;
}

export default function DashboardPage() {
  const [firstName, setFirstName] = useState('there');
  const [liveData, setLiveData] = useState<any>(null);
  const [recentResearch, setRecentResearch] = useState<HistoryItem[]>([]);
  const [jobId, setJobId] = useState<string | null>(null);
  const [switchingJobId, setSwitchingJobId] = useState<string | null>(null);

  async function selectResearch(id: string) {
    if (id === jobId || switchingJobId) return;
    setSwitchingJobId(id);
    try {
      const res = await fetch(`/api/agents/research/${id}/result`, { credentials: 'include' });
      if (!res.ok) throw new Error('Failed to load research result');
      const result = await res.json();
      saveLastResearch(id, result);
      setLiveData(result);
      setJobId(id);
      window.scrollTo({ top: 0, behavior: 'smooth' });
    } catch {
      // leave the dashboard showing whatever was previously loaded
    } finally {
      setSwitchingJobId(null);
    }
  }

  useEffect(() => {
    fetch('/api/users/me', { credentials: 'include' })
      .then((res) => (res.ok ? res.json() : null))
      .then((data) => {
        if (data?.display_name) setFirstName(data.display_name.split(' ')[0]);
        if (data?.id) {
          fetch(`/api/agents/research/history/${data.id}`, { credentials: 'include' })
            .then((res) => (res.ok ? res.json() : null))
            .then((hist) => {
              if (Array.isArray(hist?.history)) setRecentResearch(hist.history.slice(0, 3));
            })
            .catch(() => {});
        }
      })
      .catch(() => {});
  }, []);

  useEffect(() => {
    const stored = loadLastResearch();
    if (stored?.result) setLiveData(stored.result);
    if (stored?.jobId) setJobId(stored.jobId);
  }, []);

  const competitors: Array<{ name: string; marketShare: number; threat: string; revenue: string }> =
    liveData?.competitors?.competitors?.map((c: any) => ({
      name: c.name,
      marketShare: parseFloat(String(c.market_share).replace('%', '')) || 0,
      threat: c.threat_level ?? 'low',
      revenue: c.revenue ?? '—',
    })) ?? [];

  const pieData = liveData?.competitors?.competitors?.length
    ? liveData.competitors.competitors.slice(0, 5).map((c: any, i: number) => ({
        name: c.name,
        value: parseFloat(String(c.market_share).replace('%', '')) || 0,
        color: PIE_COLORS[i] ?? '#94a3b8',
      }))
    : [];

  const agentStatuses = liveData ? getAgentStatuses(liveData) : [];

  const innovationScores = liveData?.innovation_score?.scores;
  const radarData = innovationScores ? [
    { metric: 'Novelty', value: innovationScores.novelty ?? 0 },
    { metric: 'Opportunity', value: innovationScores.market_opp ?? 0 },
    { metric: 'Funding', value: innovationScores.funding ?? 0 },
    { metric: 'Research', value: innovationScores.research_maturity ?? 0 },
    { metric: 'IP Space', value: innovationScores.ip_space ?? 0 },
    { metric: 'Competition', value: innovationScores.opportunity_boost ?? 0 },
  ] : [];

  const kpiCards = liveData ? [
    { icon: BarChart3, label: 'Market Score', value: String(liveData?.innovation_score?.innovation_score ?? 0), color: 'from-emerald-500 to-teal-500', bg: 'rgba(16,185,129,0.08)' },
    { icon: TrendingUp, label: 'Opportunity Score', value: String(liveData?.opportunities?.opportunity_score ?? 0), color: 'from-indigo-500 to-purple-500', bg: 'rgba(99,102,241,0.08)' },
    { icon: Building2, label: 'Competitors Found', value: String(liveData?.competitors?.competitors?.length ?? 0), color: 'from-purple-500 to-pink-500', bg: 'rgba(168,85,247,0.08)' },
    { icon: Activity, label: 'Risk Score', value: String(liveData?.risks?.risk_score ?? 0), color: 'from-cyan-500 to-blue-500', bg: 'rgba(6,182,212,0.08)' },
  ] : [];

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between flex-wrap gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white mb-0.5">
            Welcome back, <span className="bg-gradient-to-r from-indigo-400 to-cyan-400 bg-clip-text text-transparent">{firstName}</span>
          </h1>
          <p className="text-white/45 text-sm">Here&apos;s your market intelligence overview for today</p>
        </div>
        <div className="flex gap-3">
          <AnimatedButton variant="secondary" size="sm" onClick={() => window.location.reload()}><RefreshCw className="w-4 h-4" />Refresh</AnimatedButton>
          <AnimatedButton
            size="sm"
            disabled={!jobId}
            onClick={() => {
              if (jobId) window.open(`/api/agents/research/${jobId}/report/pdf`, '_blank', 'noopener,noreferrer');
            }}
          >
            <Download className="w-4 h-4" />Export Report
          </AnimatedButton>
        </div>
      </div>

      {!liveData ? (
        <EmptyResearchState
          title="No research yet"
          description="Run your first market research analysis to see your dashboard populated with real competitors, scores, and insights."
        />
      ) : (
        <>
          {/* KPI Cards */}
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            {kpiCards.map((m, i) => (
              <motion.div key={m.label} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.08 }}>
                <GlassCard className="h-full">
                  <GlassCardContent>
                    <div className="flex items-start justify-between mb-3">
                      <div className={`w-10 h-10 rounded-xl bg-gradient-to-br ${m.color} flex items-center justify-center shadow-lg`}>
                        <m.icon className="w-5 h-5 text-white" />
                      </div>
                    </div>
                    <div className="text-2xl font-bold text-white mb-0.5">{m.value}</div>
                    <div className="text-xs text-white/45">{m.label}</div>
                  </GlassCardContent>
                </GlassCard>
              </motion.div>
            ))}
          </div>

          {/* Row 1: Healthcare Mode */}
          <GlassCard className="overflow-hidden">
            <div className="absolute inset-0 bg-gradient-to-r from-emerald-500/10 via-cyan-500/8 to-transparent" />
            <GlassCardContent className="relative flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
              <div className="space-y-2 max-w-2xl">
                <div className="inline-flex items-center gap-2 text-xs font-medium px-3 py-1 rounded-full border border-emerald-500/25 bg-emerald-500/10 text-emerald-300">
                  <HeartPulse className="w-3.5 h-3.5" /> Healthcare Mode
                </div>
                <div>
                  <h2 className="text-lg font-semibold text-white">Healthcare-specific intelligence pipeline</h2>
                  <p className="text-sm text-white/50 mt-1">
                    Switch into clinical, regulatory, and provider analysis for hospital, pharma, and medtech ideas.
                  </p>
                </div>
                <div className="flex flex-wrap gap-2 text-xs text-white/55">
                  <span className="px-2.5 py-1 rounded-full bg-white/[0.05] border border-white/[0.08]">HIPAA checks</span>
                  <span className="px-2.5 py-1 rounded-full bg-white/[0.05] border border-white/[0.08]">FDA pathway scan</span>
                  <span className="px-2.5 py-1 rounded-full bg-white/[0.05] border border-white/[0.08]">Clinical evidence</span>
                </div>
              </div>
              <div className="flex items-center gap-3 flex-shrink-0">
                <div className="hidden md:flex items-center gap-2 text-xs text-white/50">
                  <ShieldCheck className="w-4 h-4 text-emerald-300" />
                  <span>Specialized Mode Ready</span>
                </div>
                <Link href="/dashboard/healthcare">
                  <AnimatedButton size="sm">
                    Open Healthcare Mode
                    <ChevronRight className="w-4 h-4" />
                  </AnimatedButton>
                </Link>
              </div>
            </GlassCardContent>
          </GlassCard>

          {/* Row 2: AI Agents + Market Share */}
          <div className="grid lg:grid-cols-3 gap-5">
            <GlassCard>
              <GlassCardHeader>
                <div className="flex items-center justify-between">
                  <h3 className="text-base font-semibold text-white">AI Agents</h3>
                  <AnimatedBadge variant="success">{agentStatuses.filter((a) => a.status === 'completed').length} Completed</AnimatedBadge>
                </div>
              </GlassCardHeader>
              <GlassCardContent className="space-y-2.5 max-h-80 overflow-y-auto">
                {agentStatuses.map((a, i) => (
                  <motion.div key={a.name} initial={{ opacity: 0, x: 16 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: i * 0.04 }}
                    className="p-2.5 rounded-xl bg-white/[0.04] border border-white/[0.07]">
                    <div className="flex items-center justify-between mb-1.5">
                      <span className="text-xs font-medium text-white">{a.name}</span>
                      <StatusBadge status={a.status} />
                    </div>
                    <AnimatedProgress value={a.progress} />
                  </motion.div>
                ))}
              </GlassCardContent>
            </GlassCard>

            <GlassCard className="lg:col-span-2">
              <GlassCardHeader>
                <h3 className="text-base font-semibold text-white">Market Share Distribution</h3>
              </GlassCardHeader>
              <GlassCardContent>
                {pieData.length ? (
                  <div className="flex items-center gap-4">
                    <div className="h-56 flex-1">
                      <ResponsiveContainer width="100%" height="100%">
                        <PieChart>
                          <Pie
                            data={pieData}
                            cx="50%"
                            cy="50%"
                            innerRadius={55}
                            outerRadius={90}
                            paddingAngle={3}
                            dataKey="value"
                            strokeWidth={0}
                          >
                            {pieData.map((entry: any, i: number) => (
                              <Cell key={i} fill={entry.color} opacity={0.85} />
                            ))}
                          </Pie>
                          <Tooltip
                            {...tooltipStyle}
                            formatter={(v: number) => [`${v}%`, 'Market Share']}
                          />
                        </PieChart>
                      </ResponsiveContainer>
                    </div>
                    <div className="space-y-2.5 flex-shrink-0">
                      {pieData.map((d: any) => (
                        <div key={d.name} className="flex items-center gap-2">
                          <div className="w-2.5 h-2.5 rounded-full flex-shrink-0" style={{ background: d.color }} />
                          <div>
                            <div className="text-xs font-medium text-white/80">{d.name}</div>
                            <div className="text-xs text-white/40">{d.value}%</div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                ) : (
                  <p className="text-sm text-white/40 py-10 text-center">No competitor data found in the last research run.</p>
                )}
              </GlassCardContent>
            </GlassCard>
          </div>

          {/* Row 3: Radar + Competitor table */}
          <div className="grid lg:grid-cols-5 gap-5">
            <GlassCard className="lg:col-span-2">
              <GlassCardHeader>
                <h3 className="text-base font-semibold text-white">AI Capability Radar</h3>
              </GlassCardHeader>
              <GlassCardContent>
                {radarData.length ? (
                  <div className="h-64">
                    <ResponsiveContainer width="100%" height="100%">
                      <RadarChart data={radarData} margin={{ top: 20, right: 40, bottom: 20, left: 40 }}>
                        <PolarGrid stroke="rgba(255,255,255,0.08)" />
                        <PolarAngleAxis dataKey="metric" tick={{ fill: 'rgba(255,255,255,0.45)', fontSize: 10 }} />
                        <PolarRadiusAxis angle={30} domain={[0, 100]} tick={false} axisLine={false} />
                        <Radar name="Score" dataKey="value" stroke="#6366f1" fill="#6366f1" fillOpacity={0.3} strokeWidth={2} />
                        <Tooltip {...tooltipStyle} />
                      </RadarChart>
                    </ResponsiveContainer>
                  </div>
                ) : (
                  <p className="text-sm text-white/40 py-10 text-center">No innovation score breakdown found in the last research run.</p>
                )}
              </GlassCardContent>
            </GlassCard>

            <GlassCard className="lg:col-span-3">
            <GlassCardHeader>
              <h3 className="text-base font-semibold text-white">Top Competitors</h3>
            </GlassCardHeader>
            <GlassCardContent>
              {competitors.length ? (
                <table className="w-full">
                  <thead>
                    <tr className="text-left text-white/35 text-xs border-b border-white/[0.06]">
                      <th className="pb-2.5 font-medium">Company</th>
                      <th className="pb-2.5 font-medium">Share</th>
                      <th className="pb-2.5 font-medium">Revenue</th>
                      <th className="pb-2.5 font-medium">Threat</th>
                    </tr>
                  </thead>
                  <tbody>
                    {competitors.map((c, i) => (
                      <motion.tr key={c.name} initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: i * 0.07 }}
                        className="border-b border-white/[0.04] hover:bg-white/[0.03] transition-colors">
                        <td className="py-2.5">
                          <div className="flex items-center gap-2.5">
                            <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-white text-xs font-bold flex-shrink-0">{i + 1}</div>
                            <span className="text-white text-sm font-medium">{c.name}</span>
                          </div>
                        </td>
                        <td className="py-2.5">
                          <div className="flex items-center gap-1.5">
                            <div className="w-16 h-1.5 rounded-full bg-white/10">
                              <motion.div className="h-full rounded-full bg-gradient-to-r from-indigo-500 to-purple-500"
                                initial={{ width: 0 }} animate={{ width: `${c.marketShare * 3}%` }} transition={{ delay: 0.3, duration: 0.6 }} />
                            </div>
                            <span className="text-white/50 text-xs">{c.marketShare}%</span>
                          </div>
                        </td>
                        <td className="py-2.5 text-white/60 text-xs">{c.revenue}</td>
                        <td className="py-2.5">
                          <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${c.threat === 'high' ? 'bg-red-500/15 text-red-400' : c.threat === 'medium' ? 'bg-yellow-500/15 text-yellow-400' : 'bg-emerald-500/15 text-emerald-400'}`}>
                            {c.threat}
                          </span>
                        </td>
                      </motion.tr>
                    ))}
                  </tbody>
                </table>
              ) : (
                <p className="text-sm text-white/40 py-6 text-center">No competitor data found in the last research run.</p>
              )}
            </GlassCardContent>
            </GlassCard>
          </div>

          {/* Row 4: SWOT + Quick actions */}
          <div className="grid lg:grid-cols-2 gap-5">
            <GlassCard>
              <GlassCardHeader>
                <div className="flex items-center gap-2">
                  <Target className="w-4 h-4 text-indigo-400" />
                  <h3 className="text-base font-semibold text-white">SWOT Analysis</h3>
                </div>
              </GlassCardHeader>
              <GlassCardContent>
                <div className="grid grid-cols-2 gap-2.5">
                  {[
                    { label: 'Strengths', data: liveData?.swot?.strengths ?? [], color: 'text-emerald-400', bg: 'bg-emerald-500/10 border-emerald-500/20' },
                    { label: 'Weaknesses', data: liveData?.swot?.weaknesses ?? [], color: 'text-red-400', bg: 'bg-red-500/10 border-red-500/20' },
                    { label: 'Opportunities', data: liveData?.swot?.opportunities ?? [], color: 'text-indigo-400', bg: 'bg-indigo-500/10 border-indigo-500/20' },
                    { label: 'Threats', data: liveData?.swot?.threats ?? [], color: 'text-orange-400', bg: 'bg-orange-500/10 border-orange-500/20' },
                  ].map((q) => (
                    <div key={q.label} className={`p-3 rounded-xl border ${q.bg}`}>
                      <div className={`text-xs font-semibold mb-2 ${q.color}`}>{q.label} ({q.data.length})</div>
                      <ul className="space-y-1">
                        {q.data.slice(0, 2).map((t: string) => (
                          <li key={t} className="text-xs text-white/50 flex items-start gap-1">
                            <ChevronRight className="w-3 h-3 mt-0.5 flex-shrink-0 text-white/25" />{t}
                          </li>
                        ))}
                      </ul>
                    </div>
                  ))}
                </div>
              </GlassCardContent>
            </GlassCard>

            <GlassCard>
              <GlassCardHeader>
                <h3 className="text-base font-semibold text-white">Quick Actions</h3>
              </GlassCardHeader>
              <GlassCardContent>
                <div className="grid grid-cols-2 gap-2.5">
                  {[
                    { icon: Zap, label: 'New Research', desc: 'Start now', color: 'from-indigo-500 to-purple-500' },
                    { icon: Users, label: 'Add Competitor', desc: 'Track rival', color: 'from-purple-500 to-pink-500' },
                    { icon: Lightbulb, label: 'Find Gaps', desc: 'AI search', color: 'from-emerald-500 to-teal-500' },
                    { icon: ShieldAlert, label: 'Risk Scan', desc: 'Analyze risks', color: 'from-orange-500 to-red-500' },
                  ].map((a) => (
                    <motion.button key={a.label} whileHover={{ scale: 1.03, y: -2 }} whileTap={{ scale: 0.97 }}
                      className="p-3.5 rounded-xl bg-white/[0.04] border border-white/[0.07] hover:bg-white/[0.08] hover:border-white/[0.14] transition-all text-left">
                      <div className={`w-9 h-9 rounded-lg bg-gradient-to-br ${a.color} flex items-center justify-center mb-2.5 shadow-lg`}>
                        <a.icon className="w-4 h-4 text-white" />
                      </div>
                      <div className="text-xs font-semibold text-white">{a.label}</div>
                      <div className="text-xs text-white/35">{a.desc}</div>
                    </motion.button>
                  ))}
                </div>
              </GlassCardContent>
            </GlassCard>
          </div>
        </>
      )}

      {/* Recent Research — always visible, independent of local "last run" state */}
      <GlassCard>
        <GlassCardHeader>
          <div className="flex items-center justify-between">
            <h3 className="text-base font-semibold text-white">Recent Research</h3>
            <Link href="/dashboard/reports">
              <AnimatedButton variant="ghost" size="sm">View All</AnimatedButton>
            </Link>
          </div>
        </GlassCardHeader>
        <GlassCardContent className="space-y-2.5">
          {recentResearch.length ? recentResearch.map((r, i) => (
            <motion.div key={r.job_id} initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.08 }}
              onClick={() => selectResearch(r.job_id)}
              className={`flex items-center justify-between p-3 rounded-xl border transition-colors cursor-pointer ${
                r.job_id === jobId
                  ? 'bg-indigo-500/10 border-indigo-500/30'
                  : 'bg-white/[0.04] border-white/[0.07] hover:bg-white/[0.07]'
              } ${switchingJobId ? 'pointer-events-none opacity-60' : ''}`}>
              <div className="flex items-center gap-3 min-w-0">
                <div className="w-9 h-9 rounded-lg bg-indigo-500/15 border border-indigo-500/25 flex items-center justify-center flex-shrink-0">
                  {switchingJobId === r.job_id
                    ? <div className="w-3.5 h-3.5 rounded-full border-2 border-indigo-400/30 border-t-indigo-400 animate-spin" />
                    : <FileText className="w-4 h-4 text-indigo-400" />}
                </div>
                <div className="min-w-0">
                  <div className="text-xs font-medium text-white truncate">{r.idea ?? 'Untitled Research'}</div>
                  <div className="text-xs text-white/35 flex items-center gap-1 mt-0.5">
                    <Clock className="w-3 h-3" />{r.created_at ? new Date(r.created_at).toLocaleDateString() : ''}
                  </div>
                </div>
              </div>
              <div className="text-right flex-shrink-0 ml-2">
                <div className="text-lg font-bold bg-gradient-to-r from-indigo-400 to-cyan-400 bg-clip-text text-transparent">{r.innovation_score ?? '—'}</div>
                <div className="text-xs text-white/35">score</div>
              </div>
            </motion.div>
          )) : (
            <p className="text-sm text-white/40 py-6 text-center">No past research runs found.</p>
          )}
        </GlassCardContent>
      </GlassCard>
    </div>
  );
}
