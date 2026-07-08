"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import Link from "next/link";
import {
  BarChart3,
  TrendingUp,
  Building2,
  Activity,
  Download,
  RefreshCw,
  Zap,
  Clock,
  Users,
  Target,
  ShieldAlert,
  Lightbulb,
  ChevronRight,
  ArrowUpRight,
  ArrowDownRight,
  FileText,
  HeartPulse,
  ShieldCheck,
  Microscope,
} from "lucide-react";
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
  RadarChart,
  Radar,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  PieChart,
  Pie,
  Cell,
  LineChart,
  Line,
  Legend,
} from "recharts";
import {
  GlassCard,
  GlassCardContent,
  GlassCardHeader,
} from "@/components/ui/glass-card";
import { AnimatedProgress } from "@/components/ui/animated-progress";
import { AnimatedBadge, StatusBadge } from "@/components/ui/animated-badge";
import { AnimatedButton } from "@/components/ui/animated-button";

/* ── Data ── */
const trendData = [
  { month: "Jan", score: 65, opportunity: 48, risk: 35 },
  { month: "Feb", score: 72, opportunity: 55, risk: 32 },
  { month: "Mar", score: 68, opportunity: 52, risk: 38 },
  { month: "Apr", score: 85, opportunity: 67, risk: 28 },
  { month: "May", score: 90, opportunity: 72, risk: 24 },
  { month: "Jun", score: 94, opportunity: 78, risk: 20 },
];

const barData = [
  { sector: "Healthcare", funding: 42, growth: 28 },
  { sector: "FinTech", funding: 38, growth: 22 },
  { sector: "EdTech", funding: 24, growth: 18 },
  { sector: "SaaS", funding: 55, growth: 35 },
  { sector: "CleanTech", funding: 18, growth: 42 },
];

const pieData = [
  { name: "TechCorp AI", value: 28, color: "#6366f1" },
  { name: "DataGenius", value: 22, color: "#a855f7" },
  { name: "InsightLab", value: 15, color: "#06b6d4" },
  { name: "MarketMind", value: 12, color: "#10b981" },
  { name: "Others", value: 23, color: "#f59e0b" },
];

const radarData = [
  { metric: "Research", you: 94, avg: 62 },
  { metric: "Speed", you: 88, avg: 54 },
  { metric: "Accuracy", you: 91, avg: 67 },
  { metric: "Coverage", you: 85, avg: 58 },
  { metric: "Reports", you: 79, avg: 48 },
  { metric: "Insights", you: 96, avg: 61 },
];

const competitors = [
  {
    name: "TechCorp AI",
    marketShare: 28,
    threat: "high",
    trend: "up",
    revenue: "$45M",
  },
  {
    name: "DataGenius",
    marketShare: 22,
    threat: "medium",
    trend: "down",
    revenue: "$22M",
  },
  {
    name: "InsightLab",
    marketShare: 15,
    threat: "low",
    trend: "stable",
    revenue: "$8M",
  },
  {
    name: "MarketMind",
    marketShare: 12,
    threat: "low",
    trend: "up",
    revenue: "$15M",
  },
  {
    name: "DeepAnalytix",
    marketShare: 8,
    threat: "low",
    trend: "stable",
    revenue: "$5M",
  },
];

const agents: Array<{
  name: string;
  status: "running" | "completed" | "pending" | "failed";
  progress: number;
}> = [
  { name: "Research Agent", status: "completed", progress: 100 },
  { name: "Competitor Agent", status: "running", progress: 78 },
  { name: "Market Agent", status: "completed", progress: 100 },
  { name: "Trend Agent", status: "running", progress: 45 },
  { name: "SWOT Agent", status: "pending", progress: 0 },
  { name: "Risk Agent", status: "pending", progress: 0 },
];

const recentResearch = [
  { title: "Healthcare AI Market Analysis", date: "2 hours ago", score: 94 },
  { title: "EdTech Competitive Landscape", date: "5 hours ago", score: 87 },
  { title: "FinTech Startup Opportunity", date: "1 day ago", score: 76 },
];

const swotData = {
  strengths: [
    "Strong AI capabilities",
    "Healthcare expertise",
    "Fast processing",
    "Scalable architecture",
  ],
  weaknesses: ["New market entrant", "Limited brand awareness"],
  opportunities: [
    "Growing AI market",
    "Healthcare sector growth",
    "API ecosystem",
    "Enterprise demand",
  ],
  threats: [
    "Established competitors",
    "Data privacy regulations",
    "Economic uncertainty",
  ],
};

/* ── Recharts shared styles ── */
const tooltipStyle = {
  contentStyle: {
    backgroundColor: "rgba(10,10,20,0.92)",
    border: "1px solid rgba(99,102,241,0.3)",
    borderRadius: "12px",
    fontSize: 12,
    color: "#fff",
  },
  labelStyle: { color: "#94a3b8" },
};

const axisStyle = {
  stroke: "rgba(255,255,255,0.2)",
  fontSize: 11,
  fill: "rgba(255,255,255,0.4)",
};

export default function DashboardPage() {
  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between flex-wrap gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white mb-0.5">
            Welcome back,{" "}
            <span className="bg-gradient-to-r from-indigo-400 to-cyan-400 bg-clip-text text-transparent">
              John
            </span>
          </h1>
          <p className="text-white/45 text-sm">
            Here&apos;s your market intelligence overview for today
          </p>
        </div>
        <div className="flex gap-3">
          <AnimatedButton variant="secondary" size="sm">
            <RefreshCw className="w-4 h-4" />
            Refresh
          </AnimatedButton>
          <AnimatedButton size="sm">
            <Download className="w-4 h-4" />
            Export Report
          </AnimatedButton>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          {
            icon: BarChart3,
            label: "Market Score",
            value: "94.2",
            change: "+12.4%",
            trend: "up",
            color: "from-emerald-500 to-teal-500",
            bg: "rgba(16,185,129,0.08)",
          },
          {
            icon: TrendingUp,
            label: "Opportunity Score",
            value: "87.8",
            change: "+8.2%",
            trend: "up",
            color: "from-indigo-500 to-purple-500",
            bg: "rgba(99,102,241,0.08)",
          },
          {
            icon: Building2,
            label: "Competitors Found",
            value: "24",
            change: "+3 new",
            trend: "up",
            color: "from-purple-500 to-pink-500",
            bg: "rgba(168,85,247,0.08)",
          },
          {
            icon: Activity,
            label: "Funding Activity",
            value: "$2.1B",
            change: "High",
            trend: "up",
            color: "from-cyan-500 to-blue-500",
            bg: "rgba(6,182,212,0.08)",
          },
        ].map((m, i) => (
          <motion.div
            key={m.label}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.08 }}
          >
            <GlassCard className="h-full">
              <GlassCardContent>
                <div className="flex items-start justify-between mb-3">
                  <div
                    className={`w-10 h-10 rounded-xl bg-gradient-to-br ${m.color} flex items-center justify-center shadow-lg`}
                  >
                    <m.icon className="w-5 h-5 text-white" />
                  </div>
                  <span
                    className={`text-xs flex items-center gap-0.5 ${m.trend === "up" ? "text-emerald-400" : "text-red-400"}`}
                  >
                    <ArrowUpRight className="w-3 h-3" />
                    {m.change}
                  </span>
                </div>
                <div className="text-2xl font-bold text-white mb-0.5">
                  {m.value}
                </div>
                <div className="text-xs text-white/45">{m.label}</div>
                {/* Mini sparkline */}
                <div className="mt-3 h-8">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={trendData}>
                      <Line
                        type="monotone"
                        dataKey="score"
                        stroke={
                          m.color.includes("emerald")
                            ? "#10b981"
                            : m.color.includes("indigo")
                              ? "#6366f1"
                              : m.color.includes("purple")
                                ? "#a855f7"
                                : "#06b6d4"
                        }
                        strokeWidth={1.5}
                        dot={false}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </GlassCardContent>
            </GlassCard>
          </motion.div>
        ))}
      </div>

      <GlassCard className="overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-r from-emerald-500/10 via-cyan-500/8 to-transparent" />
        <GlassCardContent className="relative flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
          <div className="space-y-2 max-w-2xl">
            <div className="inline-flex items-center gap-2 text-xs font-medium px-3 py-1 rounded-full border border-emerald-500/25 bg-emerald-500/10 text-emerald-300">
              <HeartPulse className="w-3.5 h-3.5" /> Healthcare Mode
            </div>
            <div>
              <h2 className="text-lg font-semibold text-white">
                Healthcare-specific intelligence pipeline
              </h2>
              <p className="text-sm text-white/50 mt-1">
                Switch into clinical, regulatory, and provider analysis for
                hospital, pharma, and medtech ideas.
              </p>
            </div>
            <div className="flex flex-wrap gap-2 text-xs text-white/55">
              <span className="px-2.5 py-1 rounded-full bg-white/[0.05] border border-white/[0.08]">
                HIPAA checks
              </span>
              <span className="px-2.5 py-1 rounded-full bg-white/[0.05] border border-white/[0.08]">
                FDA pathway scan
              </span>
              <span className="px-2.5 py-1 rounded-full bg-white/[0.05] border border-white/[0.08]">
                Clinical evidence
              </span>
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

      {/* Row 1: Area chart + Agents */}
      <div className="grid lg:grid-cols-3 gap-5">
        <GlassCard className="lg:col-span-2">
          <GlassCardHeader>
            <div className="flex items-center justify-between flex-wrap gap-3">
              <h3 className="text-base font-semibold text-white">
                Market Score Trend
              </h3>
              <div className="flex gap-4 text-xs">
                {[
                  ["#6366f1", "Market Score"],
                  ["#10b981", "Opportunity"],
                  ["#f43f5e", "Risk Index"],
                ].map(([c, l]) => (
                  <span key={l} className="flex items-center gap-1.5">
                    <span
                      className="w-2.5 h-2.5 rounded-full"
                      style={{ background: c }}
                    />
                    <span className="text-white/50">{l}</span>
                  </span>
                ))}
              </div>
            </div>
          </GlassCardHeader>
          <GlassCardContent>
            <div className="h-60">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart
                  data={trendData}
                  margin={{ top: 4, right: 8, bottom: 0, left: -20 }}
                >
                  <defs>
                    <linearGradient id="gScore" x1="0" y1="0" x2="0" y2="1">
                      <stop
                        offset="0%"
                        stopColor="#6366f1"
                        stopOpacity={0.35}
                      />
                      <stop offset="100%" stopColor="#6366f1" stopOpacity={0} />
                    </linearGradient>
                    <linearGradient id="gOpp" x1="0" y1="0" x2="0" y2="1">
                      <stop
                        offset="0%"
                        stopColor="#10b981"
                        stopOpacity={0.25}
                      />
                      <stop offset="100%" stopColor="#10b981" stopOpacity={0} />
                    </linearGradient>
                    <linearGradient id="gRisk" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor="#f43f5e" stopOpacity={0.2} />
                      <stop offset="100%" stopColor="#f43f5e" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid
                    strokeDasharray="3 3"
                    stroke="rgba(255,255,255,0.05)"
                  />
                  <XAxis
                    dataKey="month"
                    {...axisStyle}
                    tick={{ fill: "rgba(255,255,255,0.35)", fontSize: 11 }}
                    axisLine={false}
                    tickLine={false}
                  />
                  <YAxis
                    {...axisStyle}
                    tick={{ fill: "rgba(255,255,255,0.35)", fontSize: 11 }}
                    axisLine={false}
                    tickLine={false}
                  />
                  <Tooltip {...tooltipStyle} />
                  <Area
                    type="monotone"
                    dataKey="score"
                    stroke="#6366f1"
                    strokeWidth={2}
                    fill="url(#gScore)"
                    name="Market Score"
                  />
                  <Area
                    type="monotone"
                    dataKey="opportunity"
                    stroke="#10b981"
                    strokeWidth={2}
                    fill="url(#gOpp)"
                    name="Opportunity"
                  />
                  <Area
                    type="monotone"
                    dataKey="risk"
                    stroke="#f43f5e"
                    strokeWidth={1.5}
                    fill="url(#gRisk)"
                    name="Risk Index"
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </GlassCardContent>
        </GlassCard>

        <GlassCard>
          <GlassCardHeader>
            <div className="flex items-center justify-between">
              <h3 className="text-base font-semibold text-white">AI Agents</h3>
              <AnimatedBadge variant="success">4 Active</AnimatedBadge>
            </div>
          </GlassCardHeader>
          <GlassCardContent className="space-y-2.5">
            {agents.map((a, i) => (
              <motion.div
                key={a.name}
                initial={{ opacity: 0, x: 16 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: i * 0.08 }}
                className="p-2.5 rounded-xl bg-white/[0.04] border border-white/[0.07]"
              >
                <div className="flex items-center justify-between mb-1.5">
                  <span className="text-xs font-medium text-white">
                    {a.name}
                  </span>
                  <StatusBadge status={a.status} />
                </div>
                <AnimatedProgress value={a.progress} />
                <div className="text-xs text-white/30 mt-1">
                  {a.progress}% complete
                </div>
              </motion.div>
            ))}
          </GlassCardContent>
        </GlassCard>
      </div>

      {/* Row 2: Bar chart + Donut */}
      <div className="grid lg:grid-cols-2 gap-5">
        <GlassCard>
          <GlassCardHeader>
            <h3 className="text-base font-semibold text-white">
              Funding &amp; Growth by Sector
            </h3>
          </GlassCardHeader>
          <GlassCardContent>
            <div className="h-56">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart
                  data={barData}
                  margin={{ top: 4, right: 8, bottom: 0, left: -20 }}
                >
                  <defs>
                    <linearGradient id="bFund" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor="#6366f1" />
                      <stop offset="100%" stopColor="#a855f7" />
                    </linearGradient>
                    <linearGradient id="bGrow" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor="#06b6d4" />
                      <stop offset="100%" stopColor="#0ea5e9" />
                    </linearGradient>
                  </defs>
                  <CartesianGrid
                    strokeDasharray="3 3"
                    stroke="rgba(255,255,255,0.05)"
                  />
                  <XAxis
                    dataKey="sector"
                    tick={{ fill: "rgba(255,255,255,0.35)", fontSize: 10 }}
                    axisLine={false}
                    tickLine={false}
                  />
                  <YAxis
                    tick={{ fill: "rgba(255,255,255,0.35)", fontSize: 10 }}
                    axisLine={false}
                    tickLine={false}
                  />
                  <Tooltip {...tooltipStyle} />
                  <Legend
                    wrapperStyle={{
                      fontSize: 11,
                      color: "rgba(255,255,255,0.5)",
                    }}
                  />
                  <Bar
                    dataKey="funding"
                    name="Funding ($M)"
                    fill="url(#bFund)"
                    radius={[5, 5, 0, 0]}
                  />
                  <Bar
                    dataKey="growth"
                    name="Growth (%)"
                    fill="url(#bGrow)"
                    radius={[5, 5, 0, 0]}
                  />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </GlassCardContent>
        </GlassCard>

        <GlassCard>
          <GlassCardHeader>
            <h3 className="text-base font-semibold text-white">
              Market Share Distribution
            </h3>
          </GlassCardHeader>
          <GlassCardContent>
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
                      {pieData.map((entry, i) => (
                        <Cell key={i} fill={entry.color} opacity={0.85} />
                      ))}
                    </Pie>
                    <Tooltip
                      {...tooltipStyle}
                      formatter={(v: number) => [`${v}%`, "Market Share"]}
                    />
                  </PieChart>
                </ResponsiveContainer>
              </div>
              <div className="space-y-2.5 flex-shrink-0">
                {pieData.map((d) => (
                  <div key={d.name} className="flex items-center gap-2">
                    <div
                      className="w-2.5 h-2.5 rounded-full flex-shrink-0"
                      style={{ background: d.color }}
                    />
                    <div>
                      <div className="text-xs font-medium text-white/80">
                        {d.name}
                      </div>
                      <div className="text-xs text-white/40">{d.value}%</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </GlassCardContent>
        </GlassCard>
      </div>

      {/* Row 3: Radar + Competitor table */}
      <div className="grid lg:grid-cols-5 gap-5">
        <GlassCard className="lg:col-span-2">
          <GlassCardHeader>
            <h3 className="text-base font-semibold text-white">
              AI Capability Radar
            </h3>
          </GlassCardHeader>
          <GlassCardContent>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <RadarChart
                  data={radarData}
                  margin={{ top: 0, right: 20, bottom: 0, left: 20 }}
                >
                  <PolarGrid stroke="rgba(255,255,255,0.08)" />
                  <PolarAngleAxis
                    dataKey="metric"
                    tick={{ fill: "rgba(255,255,255,0.45)", fontSize: 11 }}
                  />
                  <PolarRadiusAxis
                    angle={30}
                    domain={[0, 100]}
                    tick={false}
                    axisLine={false}
                  />
                  <Radar
                    name="You"
                    dataKey="you"
                    stroke="#6366f1"
                    fill="#6366f1"
                    fillOpacity={0.25}
                    strokeWidth={2}
                  />
                  <Radar
                    name="Avg Competitor"
                    dataKey="avg"
                    stroke="#a855f7"
                    fill="#a855f7"
                    fillOpacity={0.1}
                    strokeWidth={1.5}
                    strokeDasharray="4 3"
                  />
                  <Legend
                    wrapperStyle={{
                      fontSize: 11,
                      color: "rgba(255,255,255,0.5)",
                    }}
                  />
                  <Tooltip {...tooltipStyle} />
                </RadarChart>
              </ResponsiveContainer>
            </div>
          </GlassCardContent>
        </GlassCard>

        <GlassCard className="lg:col-span-3">
          <GlassCardHeader>
            <h3 className="text-base font-semibold text-white">
              Top Competitors
            </h3>
          </GlassCardHeader>
          <GlassCardContent>
            <table className="w-full">
              <thead>
                <tr className="text-left text-white/35 text-xs border-b border-white/[0.06]">
                  <th className="pb-2.5 font-medium">Company</th>
                  <th className="pb-2.5 font-medium">Share</th>
                  <th className="pb-2.5 font-medium">Revenue</th>
                  <th className="pb-2.5 font-medium">Threat</th>
                  <th className="pb-2.5 font-medium">Trend</th>
                </tr>
              </thead>
              <tbody>
                {competitors.map((c, i) => (
                  <motion.tr
                    key={c.name}
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: i * 0.07 }}
                    className="border-b border-white/[0.04] hover:bg-white/[0.03] transition-colors"
                  >
                    <td className="py-2.5">
                      <div className="flex items-center gap-2.5">
                        <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-white text-xs font-bold flex-shrink-0">
                          {i + 1}
                        </div>
                        <span className="text-white text-sm font-medium">
                          {c.name}
                        </span>
                      </div>
                    </td>
                    <td className="py-2.5">
                      <div className="flex items-center gap-1.5">
                        <div className="w-16 h-1.5 rounded-full bg-white/10">
                          <motion.div
                            className="h-full rounded-full bg-gradient-to-r from-indigo-500 to-purple-500"
                            initial={{ width: 0 }}
                            animate={{ width: `${c.marketShare * 3}%` }}
                            transition={{ delay: 0.3, duration: 0.6 }}
                          />
                        </div>
                        <span className="text-white/50 text-xs">
                          {c.marketShare}%
                        </span>
                      </div>
                    </td>
                    <td className="py-2.5 text-white/60 text-xs">
                      {c.revenue}
                    </td>
                    <td className="py-2.5">
                      <span
                        className={`px-2 py-0.5 rounded-full text-xs font-medium ${c.threat === "high" ? "bg-red-500/15 text-red-400" : c.threat === "medium" ? "bg-yellow-500/15 text-yellow-400" : "bg-emerald-500/15 text-emerald-400"}`}
                      >
                        {c.threat}
                      </span>
                    </td>
                    <td className="py-2.5">
                      <span
                        className={`text-xs flex items-center gap-0.5 ${c.trend === "up" ? "text-emerald-400" : c.trend === "down" ? "text-red-400" : "text-white/40"}`}
                      >
                        {c.trend === "up" && (
                          <ArrowUpRight className="w-3.5 h-3.5" />
                        )}
                        {c.trend === "down" && (
                          <ArrowDownRight className="w-3.5 h-3.5" />
                        )}
                        {c.trend === "stable" && "—"}
                        {c.trend}
                      </span>
                    </td>
                  </motion.tr>
                ))}
              </tbody>
            </table>
          </GlassCardContent>
        </GlassCard>
      </div>

      {/* Row 4: SWOT + Recent research + Quick actions */}
      <div className="grid lg:grid-cols-3 gap-5">
        <GlassCard>
          <GlassCardHeader>
            <div className="flex items-center gap-2">
              <Target className="w-4 h-4 text-indigo-400" />
              <h3 className="text-base font-semibold text-white">
                SWOT Analysis
              </h3>
            </div>
          </GlassCardHeader>
          <GlassCardContent>
            <div className="grid grid-cols-2 gap-2.5">
              {[
                {
                  label: "Strengths",
                  data: swotData.strengths,
                  color: "text-emerald-400",
                  bg: "bg-emerald-500/10 border-emerald-500/20",
                },
                {
                  label: "Weaknesses",
                  data: swotData.weaknesses,
                  color: "text-red-400",
                  bg: "bg-red-500/10 border-red-500/20",
                },
                {
                  label: "Opportunities",
                  data: swotData.opportunities,
                  color: "text-indigo-400",
                  bg: "bg-indigo-500/10 border-indigo-500/20",
                },
                {
                  label: "Threats",
                  data: swotData.threats,
                  color: "text-orange-400",
                  bg: "bg-orange-500/10 border-orange-500/20",
                },
              ].map((q) => (
                <div key={q.label} className={`p-3 rounded-xl border ${q.bg}`}>
                  <div className={`text-xs font-semibold mb-2 ${q.color}`}>
                    {q.label} ({q.data.length})
                  </div>
                  <ul className="space-y-1">
                    {q.data.slice(0, 2).map((t) => (
                      <li
                        key={t}
                        className="text-xs text-white/50 flex items-start gap-1"
                      >
                        <ChevronRight className="w-3 h-3 mt-0.5 flex-shrink-0 text-white/25" />
                        {t}
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
            <div className="flex items-center justify-between">
              <h3 className="text-base font-semibold text-white">
                Recent Research
              </h3>
              <AnimatedButton variant="ghost" size="sm">
                View All
              </AnimatedButton>
            </div>
          </GlassCardHeader>
          <GlassCardContent className="space-y-2.5">
            {recentResearch.map((r, i) => (
              <motion.div
                key={r.title}
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.08 }}
                className="flex items-center justify-between p-3 rounded-xl bg-white/[0.04] border border-white/[0.07] hover:bg-white/[0.07] transition-colors cursor-pointer"
              >
                <div className="flex items-center gap-3 min-w-0">
                  <div className="w-9 h-9 rounded-lg bg-indigo-500/15 border border-indigo-500/25 flex items-center justify-center flex-shrink-0">
                    <FileText className="w-4 h-4 text-indigo-400" />
                  </div>
                  <div className="min-w-0">
                    <div className="text-xs font-medium text-white truncate">
                      {r.title}
                    </div>
                    <div className="text-xs text-white/35 flex items-center gap-1 mt-0.5">
                      <Clock className="w-3 h-3" />
                      {r.date}
                    </div>
                  </div>
                </div>
                <div className="text-right flex-shrink-0 ml-2">
                  <div className="text-lg font-bold bg-gradient-to-r from-indigo-400 to-cyan-400 bg-clip-text text-transparent">
                    {r.score}
                  </div>
                  <div className="text-xs text-white/35">score</div>
                </div>
              </motion.div>
            ))}
          </GlassCardContent>
        </GlassCard>

        <GlassCard>
          <GlassCardHeader>
            <h3 className="text-base font-semibold text-white">
              Quick Actions
            </h3>
          </GlassCardHeader>
          <GlassCardContent>
            <div className="grid grid-cols-2 gap-2.5">
              {[
                {
                  icon: Zap,
                  label: "New Research",
                  desc: "Start now",
                  color: "from-indigo-500 to-purple-500",
                },
                {
                  icon: Users,
                  label: "Add Competitor",
                  desc: "Track rival",
                  color: "from-purple-500 to-pink-500",
                },
                {
                  icon: Lightbulb,
                  label: "Find Gaps",
                  desc: "AI search",
                  color: "from-emerald-500 to-teal-500",
                },
                {
                  icon: ShieldAlert,
                  label: "Risk Scan",
                  desc: "Analyze risks",
                  color: "from-orange-500 to-red-500",
                },
              ].map((a) => (
                <motion.button
                  key={a.label}
                  whileHover={{ scale: 1.03, y: -2 }}
                  whileTap={{ scale: 0.97 }}
                  className="p-3.5 rounded-xl bg-white/[0.04] border border-white/[0.07] hover:bg-white/[0.08] hover:border-white/[0.14] transition-all text-left"
                >
                  <div
                    className={`w-9 h-9 rounded-lg bg-gradient-to-br ${a.color} flex items-center justify-center mb-2.5 shadow-lg`}
                  >
                    <a.icon className="w-4 h-4 text-white" />
                  </div>
                  <div className="text-xs font-semibold text-white">
                    {a.label}
                  </div>
                  <div className="text-xs text-white/35">{a.desc}</div>
                </motion.button>
              ))}
            </div>
          </GlassCardContent>
        </GlassCard>
      </div>
    </div>
  );
}
