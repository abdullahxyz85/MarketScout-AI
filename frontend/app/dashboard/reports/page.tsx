'use client';

import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import {
  FileText, Download, Eye, Share2, Star, BarChart3,
  TrendingUp, Search, Clock, Heart, Zap,
} from 'lucide-react';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, PieChart, Pie, Cell,
  AreaChart, Area,
} from 'recharts';
import { GlassCard, GlassCardContent, GlassCardHeader } from '@/components/ui/glass-card';
import { AnimatedButton } from '@/components/ui/animated-button';
import { EmptyResearchState } from '@/components/dashboard/empty-research-state';

const scoreColor = (s: number) => s >= 90 ? 'text-emerald-400' : s >= 75 ? 'text-indigo-400' : 'text-yellow-400';

const tooltipStyle = {
  contentStyle: { backgroundColor: 'rgba(10,10,20,0.92)', border: '1px solid rgba(99,102,241,0.3)', borderRadius: '12px', fontSize: 12, color: '#fff' },
  labelStyle: { color: '#94a3b8' },
};

interface HistoryItem {
  job_id: string;
  idea?: string;
  industry?: string;
  created_at?: string;
  innovation_score?: number;
}

const HISTORY_ICONS = [Heart, BarChart3, TrendingUp, Zap];
const HISTORY_COLORS = [
  'from-rose-500 to-pink-500',
  'from-indigo-500 to-purple-500',
  'from-emerald-500 to-teal-500',
  'from-cyan-500 to-blue-500',
];

function deriveActivityData(history: HistoryItem[]) {
  const buckets = new Map<string, { key: string; label: string; reports: number; scoreSum: number }>();
  for (const h of history) {
    if (!h.created_at) continue;
    const date = new Date(h.created_at);
    const key = `${date.getFullYear()}-${date.getMonth()}`;
    const label = date.toLocaleDateString('en-US', { month: 'short', year: '2-digit' });
    const bucket = buckets.get(key) ?? { key, label, reports: 0, scoreSum: 0 };
    bucket.reports += 1;
    bucket.scoreSum += h.innovation_score ?? 0;
    buckets.set(key, bucket);
  }
  return Array.from(buckets.values())
    .sort((a, b) => a.key.localeCompare(b.key))
    .map((b) => ({ month: b.label, reports: b.reports, avgScore: Math.round(b.scoreSum / b.reports) }));
}

function deriveScoreDistribution(history: HistoryItem[]) {
  let high = 0, good = 0, fair = 0;
  for (const h of history) {
    const s = h.innovation_score ?? 0;
    if (s >= 90) high += 1;
    else if (s >= 75) good += 1;
    else fair += 1;
  }
  return [
    { name: 'High (90+)', value: high, color: '#10b981' },
    { name: 'Good (75-89)', value: good, color: '#6366f1' },
    { name: 'Fair (<75)', value: fair, color: '#f59e0b' },
  ].filter((d) => d.value > 0);
}

function deriveIndustryData(history: HistoryItem[]) {
  const buckets = new Map<string, { industry: string; reports: number; scoreSum: number }>();
  for (const h of history) {
    const industry = h.industry?.trim() || 'General';
    const bucket = buckets.get(industry) ?? { industry, reports: 0, scoreSum: 0 };
    bucket.reports += 1;
    bucket.scoreSum += h.innovation_score ?? 0;
    buckets.set(industry, bucket);
  }
  return Array.from(buckets.values()).map((b) => ({
    name: b.industry,
    reports: b.reports,
    avgScore: Math.round(b.scoreSum / b.reports),
  }));
}

export default function ReportsPage() {
  const [search, setSearch] = useState('');
  const [starred, setStarred] = useState<string[]>([]);
  const [history, setHistory] = useState<HistoryItem[] | null>(null);

  useEffect(() => {
    (async () => {
      try {
        const userRes = await fetch('/api/users/me', { credentials: 'include' });
        if (!userRes.ok) { setHistory([]); return; }
        const user = await userRes.json();
        const userId = user?.id;
        if (!userId) { setHistory([]); return; }
        const res = await fetch(`/api/agents/research/history/${userId}`);
        if (!res.ok) { setHistory([]); return; }
        const data = await res.json();
        setHistory(Array.isArray(data?.history) ? data.history : []);
      } catch {
        setHistory([]);
      }
    })();
  }, []);

  if (history === null) return null;

  if (history.length === 0) {
    return (
      <div className="space-y-8 max-w-7xl mx-auto">
        <div className="flex items-center justify-between flex-wrap gap-4">
          <div>
            <h1 className="text-2xl font-bold text-white mb-0.5">
              Research <span className="bg-gradient-to-r from-indigo-400 to-cyan-400 bg-clip-text text-transparent">Reports</span>
            </h1>
            <p className="text-white/45 text-sm">View, download, and analyse your market intelligence reports</p>
          </div>
        </div>
        <EmptyResearchState
          title="No reports yet"
          description="Run a market research analysis to generate your first report — it'll show up here with its score, industry, and a downloadable PDF."
        />
      </div>
    );
  }

  const reports = history.map((h, i) => ({
    id: h.job_id,
    title: h.idea ?? 'Untitled Research',
    description: h.industry ? `Industry: ${h.industry}` : '',
    industry: h.industry ?? 'General',
    score: h.innovation_score ?? 0,
    date: h.created_at ? new Date(h.created_at).toLocaleString() : '',
    icon: HISTORY_ICONS[i % HISTORY_ICONS.length],
    color: HISTORY_COLORS[i % HISTORY_COLORS.length],
  }));

  const activityData = deriveActivityData(history);
  const scoreDistribution = deriveScoreDistribution(history);
  const industryData = deriveIndustryData(history);
  const filtered = reports.filter((r) => r.title.toLowerCase().includes(search.toLowerCase()));

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      <div className="flex items-center justify-between flex-wrap gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white mb-0.5">
            Research <span className="bg-gradient-to-r from-indigo-400 to-cyan-400 bg-clip-text text-transparent">Reports</span>
          </h1>
          <p className="text-white/45 text-sm">View, download, and analyse your market intelligence reports</p>
        </div>
        <AnimatedButton size="sm"><FileText className="w-4 h-4" />New Research</AnimatedButton>
      </div>

      {/* Analytics charts */}
      <div className="grid lg:grid-cols-3 gap-5">
        {/* Activity line chart */}
        <GlassCard className="lg:col-span-2">
          <GlassCardHeader>
            <h3 className="text-sm font-semibold text-white">Research Activity &amp; Score Trend</h3>
          </GlassCardHeader>
          <GlassCardContent>
            <div className="h-48">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={activityData} margin={{ top: 4, right: 8, bottom: 0, left: -20 }}>
                  <defs>
                    <linearGradient id="aRep" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor="#6366f1" stopOpacity={0.3} />
                      <stop offset="100%" stopColor="#6366f1" stopOpacity={0} />
                    </linearGradient>
                    <linearGradient id="aScore" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor="#10b981" stopOpacity={0.25} />
                      <stop offset="100%" stopColor="#10b981" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                  <XAxis dataKey="month" tick={{ fill: 'rgba(255,255,255,0.35)', fontSize: 10 }} axisLine={false} tickLine={false} />
                  <YAxis tick={{ fill: 'rgba(255,255,255,0.35)', fontSize: 10 }} axisLine={false} tickLine={false} />
                  <Tooltip {...tooltipStyle} />
                  <Area type="monotone" dataKey="reports" stroke="#6366f1" strokeWidth={2} fill="url(#aRep)" name="Reports" />
                  <Area type="monotone" dataKey="avgScore" stroke="#10b981" strokeWidth={1.5} fill="url(#aScore)" name="Avg Score" />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </GlassCardContent>
        </GlassCard>

        {/* Score distribution donut */}
        <GlassCard>
          <GlassCardHeader>
            <h3 className="text-sm font-semibold text-white">Score Distribution</h3>
          </GlassCardHeader>
          <GlassCardContent>
            <div className="h-48 flex items-center gap-3">
              <div className="flex-1">
                <ResponsiveContainer width="100%" height={160}>
                  <PieChart>
                    <Pie data={scoreDistribution} cx="50%" cy="50%" innerRadius={42} outerRadius={68} paddingAngle={4} dataKey="value" strokeWidth={0}>
                      {scoreDistribution.map((d, i) => <Cell key={i} fill={d.color} opacity={0.85} />)}
                    </Pie>
                    <Tooltip {...tooltipStyle} />
                  </PieChart>
                </ResponsiveContainer>
              </div>
              <div className="space-y-3 flex-shrink-0">
                {scoreDistribution.map((d) => (
                  <div key={d.name} className="flex items-center gap-2">
                    <div className="w-2.5 h-2.5 rounded-full" style={{ background: d.color }} />
                    <div>
                      <div className="text-xs text-white/70">{d.name}</div>
                      <div className="text-sm font-bold text-white">{d.value}</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </GlassCardContent>
        </GlassCard>
      </div>

      {/* Industry bar chart */}
      <GlassCard>
        <GlassCardHeader>
          <h3 className="text-sm font-semibold text-white">Reports by Industry</h3>
        </GlassCardHeader>
        <GlassCardContent>
          <div className="h-44">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={industryData} margin={{ top: 4, right: 8, bottom: 0, left: -20 }}>
                <defs>
                  <linearGradient id="bRep2" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#6366f1" />
                    <stop offset="100%" stopColor="#a855f7" />
                  </linearGradient>
                  <linearGradient id="bScore2" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#10b981" />
                    <stop offset="100%" stopColor="#06b6d4" />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                <XAxis dataKey="name" tick={{ fill: 'rgba(255,255,255,0.4)', fontSize: 11 }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fill: 'rgba(255,255,255,0.4)', fontSize: 11 }} axisLine={false} tickLine={false} />
                <Tooltip {...tooltipStyle} />
                <Bar dataKey="reports" name="Reports" fill="url(#bRep2)" radius={[5, 5, 0, 0]} />
                <Bar dataKey="avgScore" name="Avg Score" fill="url(#bScore2)" radius={[5, 5, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </GlassCardContent>
      </GlassCard>

      {/* Search */}
      <div className="relative max-w-sm">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-white/30" />
        <input value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Search reports..."
          className="pl-9 pr-4 py-2.5 w-full rounded-xl bg-white/[0.04] border border-white/[0.08] text-white text-sm placeholder:text-white/25 focus:outline-none focus:border-indigo-500/50 transition-colors" />
      </div>

      {/* Reports grid */}
      <div className="grid md:grid-cols-2 gap-4">
        {filtered.map((r, i) => (
          <motion.div key={r.id} initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.09 }}>
            <GlassCard>
              <GlassCardContent>
                <div className="flex items-start gap-4 mb-4">
                  <div className={`w-[52px] h-[52px] rounded-2xl bg-gradient-to-br ${r.color} flex items-center justify-center flex-shrink-0 shadow-lg`}>
                    <r.icon className="w-6 h-6 text-white" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-start justify-between">
                      <h3 className="text-sm font-semibold text-white leading-tight pr-2">{r.title}</h3>
                      <div className={`text-xl font-bold flex-shrink-0 ${scoreColor(r.score)}`}>{r.score}</div>
                    </div>
                    <p className="text-xs text-white/45 mt-1 line-clamp-2">{r.description}</p>
                    <div className="flex items-center gap-3 text-xs text-white/35 mt-2">
                      <span className="flex items-center gap-1"><Clock className="w-3 h-3" />{r.date}</span>
                      <span className="px-2 py-0.5 rounded-full bg-white/[0.05] border border-white/[0.08]">{r.industry}</span>
                    </div>
                  </div>
                </div>

                <div className="flex items-center justify-between pt-3 border-t border-white/[0.06]">
                  <div className="flex gap-2">
                    <motion.button whileHover={{ scale: 1.08 }} className="p-1.5 rounded-lg bg-white/[0.04] border border-white/[0.08] text-white/50 hover:text-white hover:bg-white/[0.08] transition-colors">
                      <Eye className="w-3.5 h-3.5" />
                    </motion.button>
                    <motion.button whileHover={{ scale: 1.08 }} className="p-1.5 rounded-lg bg-white/[0.04] border border-white/[0.08] text-white/50 hover:text-white hover:bg-white/[0.08] transition-colors">
                      <Share2 className="w-3.5 h-3.5" />
                    </motion.button>
                    <motion.button whileHover={{ scale: 1.08 }} onClick={() => setStarred(s => s.includes(r.id) ? s.filter(x => x !== r.id) : [...s, r.id])}
                      className={`p-1.5 rounded-lg border transition-colors ${starred.includes(r.id) ? 'bg-yellow-500/10 border-yellow-500/25 text-yellow-400' : 'bg-white/[0.04] border-white/[0.08] text-white/50 hover:text-white'}`}>
                      <Star className="w-3.5 h-3.5" fill={starred.includes(r.id) ? 'currentColor' : 'none'} />
                    </motion.button>
                  </div>
                  <a href={`/api/agents/research/${r.id}/report/pdf`} target="_blank" rel="noopener noreferrer">
                    <AnimatedButton size="sm"><Download className="w-3.5 h-3.5" />Download</AnimatedButton>
                  </a>
                </div>
              </GlassCardContent>
            </GlassCard>
          </motion.div>
        ))}
      </div>
    </div>
  );
}
