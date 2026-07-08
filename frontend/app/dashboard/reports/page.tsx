'use client';

import { useEffect, useMemo, useState } from 'react';
import { motion } from 'framer-motion';
import {
  FileText, Download, Eye, Share2, Star, BarChart3,
  TrendingUp, Search, Clock, Heart, Zap, Filter,
} from 'lucide-react';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, PieChart, Pie, Cell, LineChart,
  Line, AreaChart, Area,
} from 'recharts';
import { GlassCard, GlassCardContent, GlassCardHeader } from '@/components/ui/glass-card';
import { AnimatedButton } from '@/components/ui/animated-button';

type ApiReport = {
  id: string;
  title: string;
  description: string | null;
  industry: string | null;
  score: number;
  pages: number;
  starred: boolean;
  created_at: number;
  chart_data: { trend?: Array<{ score: number }> };
};

const reportIcons = [Heart, BarChart3, TrendingUp, Zap];
const reportColors = [
  'from-rose-500 to-pink-500',
  'from-indigo-500 to-purple-500',
  'from-emerald-500 to-teal-500',
  'from-cyan-500 to-blue-500',
];

const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'];

function timeAgo(epochSeconds: number) {
  const diffMs = Date.now() - epochSeconds * 1000;
  const mins = Math.floor(diffMs / 60000);
  if (mins < 60) return `${mins}m ago`;
  const hours = Math.floor(mins / 60);
  if (hours < 24) return `${hours}h ago`;
  return `${Math.floor(hours / 24)}d ago`;
}

const scoreColor = (s: number) => s >= 90 ? 'text-emerald-400' : s >= 75 ? 'text-indigo-400' : 'text-yellow-400';

const tooltipStyle = {
  contentStyle: { backgroundColor: 'rgba(10,10,20,0.92)', border: '1px solid rgba(99,102,241,0.3)', borderRadius: '12px', fontSize: 12, color: '#fff' },
  labelStyle: { color: '#94a3b8' },
};

export default function ReportsPage() {
  const [search, setSearch] = useState('');
  const [apiReports, setApiReports] = useState<ApiReport[]>([]);
  const [starred, setStarred] = useState<string[]>([]);

  useEffect(() => {
    let cancelled = false;
    fetch('/api/reports/', { credentials: 'include' })
      .then((res) => (res.ok ? res.json() : []))
      .then((data: ApiReport[]) => {
        if (cancelled) return;
        setApiReports(data);
        setStarred(data.filter((r) => r.starred).map((r) => r.id));
      })
      .catch(() => {});
    return () => {
      cancelled = true;
    };
  }, []);

  const reports = useMemo(
    () =>
      apiReports.map((r, i) => {
        const scoreData = r.chart_data?.trend?.length
          ? r.chart_data.trend.slice(-6).map((p) => p.score)
          : Array(6).fill(r.score);
        return {
          id: r.id,
          title: r.title,
          description: r.description ?? '',
          industry: r.industry ?? 'General',
          score: r.score,
          date: timeAgo(r.created_at),
          pages: r.pages,
          starred: r.starred,
          icon: reportIcons[i % reportIcons.length],
          color: reportColors[i % reportColors.length],
          scoreData,
        };
      }),
    [apiReports],
  );

  const industryData = useMemo(() => {
    const byIndustry = new Map<string, { reports: number; total: number }>();
    for (const r of reports) {
      const entry = byIndustry.get(r.industry) ?? { reports: 0, total: 0 };
      entry.reports += 1;
      entry.total += r.score;
      byIndustry.set(r.industry, entry);
    }
    return Array.from(byIndustry.entries()).map(([name, v]) => ({
      name,
      reports: v.reports,
      avgScore: Math.round(v.total / v.reports),
    }));
  }, [reports]);

  const pieData = useMemo(() => {
    const buckets = [
      { name: 'High (90+)', value: 0, color: '#10b981' },
      { name: 'Good (75-89)', value: 0, color: '#6366f1' },
      { name: 'Fair (<75)', value: 0, color: '#f59e0b' },
    ];
    for (const r of reports) {
      if (r.score >= 90) buckets[0].value += 1;
      else if (r.score >= 75) buckets[1].value += 1;
      else buckets[2].value += 1;
    }
    return buckets;
  }, [reports]);

  const activityData = useMemo(
    () => months.map((m) => ({ month: m, reports: 0, avgScore: 0 })),
    [],
  );

  const toggleStar = async (id: string) => {
    const res = await fetch(`/api/reports/${id}/star`, { method: 'POST', credentials: 'include' });
    if (res.ok) {
      setStarred((s) => (s.includes(id) ? s.filter((x) => x !== id) : [...s, id]));
    }
  };

  const filtered = reports.filter((r) => r.title.toLowerCase().includes(search.toLowerCase()));

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
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
                    <Pie data={pieData} cx="50%" cy="50%" innerRadius={42} outerRadius={68} paddingAngle={4} dataKey="value" strokeWidth={0}>
                      {pieData.map((d, i) => <Cell key={i} fill={d.color} opacity={0.85} />)}
                    </Pie>
                    <Tooltip {...tooltipStyle} />
                  </PieChart>
                </ResponsiveContainer>
              </div>
              <div className="space-y-3 flex-shrink-0">
                {pieData.map((d) => (
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
        {filtered.map((r, i) => {
          const sparkData = months.map((m, idx) => ({ m, v: r.scoreData[idx] }));
          return (
            <motion.div key={r.id} initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.09 }}>
              <GlassCard>
                <GlassCardContent>
                  <div className="flex items-start gap-4 mb-4">
                    <div className={`w-13 h-13 w-[52px] h-[52px] rounded-2xl bg-gradient-to-br ${r.color} flex items-center justify-center flex-shrink-0 shadow-lg`}>
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
                        <span>{r.pages}p</span>
                        <span className="px-2 py-0.5 rounded-full bg-white/[0.05] border border-white/[0.08]">{r.industry}</span>
                      </div>
                    </div>
                  </div>

                  {/* Sparkline */}
                  <div className="h-16 mb-3 -mx-1">
                    <ResponsiveContainer width="100%" height="100%">
                      <AreaChart data={sparkData} margin={{ top: 2, right: 2, bottom: 0, left: 2 }}>
                        <defs>
                          <linearGradient id={`sg${r.id}`} x1="0" y1="0" x2="0" y2="1">
                            <stop offset="0%" stopColor="#6366f1" stopOpacity={0.3} />
                            <stop offset="100%" stopColor="#6366f1" stopOpacity={0} />
                          </linearGradient>
                        </defs>
                        <Area type="monotone" dataKey="v" stroke="#6366f1" strokeWidth={1.5} fill={`url(#sg${r.id})`} dot={false} />
                        <Tooltip {...tooltipStyle} formatter={(v: number) => [v, 'Score']} />
                      </AreaChart>
                    </ResponsiveContainer>
                  </div>

                  <div className="flex items-center justify-between pt-3 border-t border-white/[0.06]">
                    <div className="flex gap-2">
                      <motion.button whileHover={{ scale: 1.08 }} className="p-1.5 rounded-lg bg-white/[0.04] border border-white/[0.08] text-white/50 hover:text-white hover:bg-white/[0.08] transition-colors">
                        <Eye className="w-3.5 h-3.5" />
                      </motion.button>
                      <motion.button whileHover={{ scale: 1.08 }} className="p-1.5 rounded-lg bg-white/[0.04] border border-white/[0.08] text-white/50 hover:text-white hover:bg-white/[0.08] transition-colors">
                        <Share2 className="w-3.5 h-3.5" />
                      </motion.button>
                      <motion.button whileHover={{ scale: 1.08 }} onClick={() => toggleStar(r.id)}
                        className={`p-1.5 rounded-lg border transition-colors ${starred.includes(r.id) ? 'bg-yellow-500/10 border-yellow-500/25 text-yellow-400' : 'bg-white/[0.04] border-white/[0.08] text-white/50 hover:text-white'}`}>
                        <Star className="w-3.5 h-3.5" fill={starred.includes(r.id) ? 'currentColor' : 'none'} />
                      </motion.button>
                    </div>
                    <a href={`/api/reports/${r.id}/download`}>
                      <AnimatedButton size="sm"><Download className="w-3.5 h-3.5" />Download</AnimatedButton>
                    </a>
                  </div>
                </GlassCardContent>
              </GlassCard>
            </motion.div>
          );
        })}
      </div>
    </div>
  );
}
