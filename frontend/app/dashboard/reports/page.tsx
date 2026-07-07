'use client';

import { useState } from 'react';
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

const reports = [
  { id: 1, title: 'Healthcare AI Market Analysis', description: 'Comprehensive analysis of the AI-powered healthcare market in North America', industry: 'Healthcare', score: 94, date: '2 hours ago', pages: 24, starred: true, icon: Heart, color: 'from-rose-500 to-pink-500', scoreData: [72, 78, 82, 88, 91, 94] },
  { id: 2, title: 'EdTech Competitive Landscape', description: 'Deep dive into the online education market including 18 competitors', industry: 'EdTech', score: 87, date: '5 hours ago', pages: 18, starred: false, icon: BarChart3, color: 'from-indigo-500 to-purple-500', scoreData: [60, 65, 70, 75, 82, 87] },
  { id: 3, title: 'FinTech Startup Opportunity', description: 'Market sizing and opportunity assessment for B2B payments startup', industry: 'FinTech', score: 76, date: '1 day ago', pages: 21, starred: true, icon: TrendingUp, color: 'from-emerald-500 to-teal-500', scoreData: [55, 58, 62, 68, 73, 76] },
  { id: 4, title: 'SaaS Productivity Tools Market', description: 'Analysis of the enterprise productivity SaaS market for 2024', industry: 'SaaS', score: 81, date: '2 days ago', pages: 16, starred: false, icon: Zap, color: 'from-cyan-500 to-blue-500', scoreData: [58, 62, 67, 72, 78, 81] },
];

const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'];

const industryData = [
  { name: 'Healthcare', reports: 4, avgScore: 91 },
  { name: 'FinTech', reports: 3, avgScore: 78 },
  { name: 'EdTech', reports: 2, avgScore: 85 },
  { name: 'SaaS', reports: 3, avgScore: 82 },
];

const pieData = [
  { name: 'High (90+)', value: 3, color: '#10b981' },
  { name: 'Good (75-89)', value: 7, color: '#6366f1' },
  { name: 'Fair (<75)', value: 2, color: '#f59e0b' },
];

const activityData = months.map((m, i) => ({ month: m, reports: [1, 2, 2, 3, 2, 4][i], avgScore: [72, 76, 79, 83, 85, 87][i] }));

const scoreColor = (s: number) => s >= 90 ? 'text-emerald-400' : s >= 75 ? 'text-indigo-400' : 'text-yellow-400';

const tooltipStyle = {
  contentStyle: { backgroundColor: 'rgba(10,10,20,0.92)', border: '1px solid rgba(99,102,241,0.3)', borderRadius: '12px', fontSize: 12, color: '#fff' },
  labelStyle: { color: '#94a3b8' },
};

export default function ReportsPage() {
  const [search, setSearch] = useState('');
  const [starred, setStarred] = useState<number[]>([1, 3]);

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
                      <motion.button whileHover={{ scale: 1.08 }} onClick={() => setStarred(s => s.includes(r.id) ? s.filter(x => x !== r.id) : [...s, r.id])}
                        className={`p-1.5 rounded-lg border transition-colors ${starred.includes(r.id) ? 'bg-yellow-500/10 border-yellow-500/25 text-yellow-400' : 'bg-white/[0.04] border-white/[0.08] text-white/50 hover:text-white'}`}>
                        <Star className="w-3.5 h-3.5" fill={starred.includes(r.id) ? 'currentColor' : 'none'} />
                      </motion.button>
                    </div>
                    <AnimatedButton size="sm"><Download className="w-3.5 h-3.5" />Download</AnimatedButton>
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
