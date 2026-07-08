"use client";

import { motion } from "framer-motion";
import {
  HeartPulse,
  ShieldCheck,
  Building2,
  Activity,
  Stethoscope,
  Microscope,
  FileCheck2,
  FlaskConical,
} from "lucide-react";
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  RadarChart,
  Radar,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
} from "recharts";
import {
  GlassCard,
  GlassCardContent,
  GlassCardHeader,
} from "@/components/ui/glass-card";
import { AnimatedBadge } from "@/components/ui/animated-badge";
import { AnimatedProgress } from "@/components/ui/animated-progress";
import { AnimatedButton } from "@/components/ui/animated-button";

const healthcareTrend = [
  { month: "Jan", demand: 48, regulatory: 62, adoption: 40 },
  { month: "Feb", demand: 54, regulatory: 66, adoption: 44 },
  { month: "Mar", demand: 60, regulatory: 69, adoption: 51 },
  { month: "Apr", demand: 67, regulatory: 73, adoption: 58 },
  { month: "May", demand: 73, regulatory: 78, adoption: 64 },
  { month: "Jun", demand: 81, regulatory: 82, adoption: 71 },
];

const readiness = [
  { metric: "Clinical Need", score: 88 },
  { metric: "Regulatory Fit", score: 74 },
  { metric: "Provider Adoption", score: 79 },
  { metric: "Reimbursement", score: 63 },
  { metric: "Data Security", score: 92 },
  { metric: "Pilot Feasibility", score: 84 },
];

const watchlist = [
  {
    name: "MediFlow AI",
    focus: "Hospital operations",
    stage: "Series B",
    threat: "Medium",
  },
  {
    name: "ClinicSense",
    focus: "Primary care optimization",
    stage: "Series A",
    threat: "Low",
  },
  {
    name: "TriageNova",
    focus: "AI triage support",
    stage: "Growth",
    threat: "High",
  },
];

const tooltipStyle = {
  contentStyle: {
    backgroundColor: "rgba(8, 12, 18, 0.92)",
    border: "1px solid rgba(16,185,129,0.35)",
    borderRadius: "12px",
    fontSize: 12,
    color: "#fff",
  },
  labelStyle: { color: "#9ca3af" },
};

export default function HealthcareModePage() {
  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div>
          <h1 className="text-2xl font-bold text-white mb-1">
            Healthcare{" "}
            <span className="bg-gradient-to-r from-emerald-400 to-cyan-400 bg-clip-text text-transparent">
              Mode
            </span>
          </h1>
          <p className="text-white/50 text-sm">
            Clinical, regulatory, and hospital-focused market intelligence.
          </p>
        </div>
        <AnimatedBadge variant="success">
          Specialized Pipeline Active
        </AnimatedBadge>
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          { label: "TAM (Healthcare)", value: "$847B", icon: Building2 },
          { label: "Clinical Demand", value: "81", icon: HeartPulse },
          { label: "Regulatory Readiness", value: "74", icon: ShieldCheck },
          { label: "Provider Adoption", value: "+18%", icon: Stethoscope },
        ].map((metric, i) => (
          <motion.div
            key={metric.label}
            initial={{ opacity: 0, y: 14 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.07 }}
          >
            <GlassCard>
              <GlassCardContent>
                <div className="flex items-center justify-between mb-2">
                  <metric.icon className="w-5 h-5 text-emerald-300" />
                  <span className="text-xs text-white/40">Live</span>
                </div>
                <div className="text-2xl font-bold text-white">
                  {metric.value}
                </div>
                <div className="text-xs text-white/50">{metric.label}</div>
              </GlassCardContent>
            </GlassCard>
          </motion.div>
        ))}
      </div>

      <div className="grid lg:grid-cols-3 gap-5">
        <GlassCard className="lg:col-span-2">
          <GlassCardHeader>
            <h3 className="text-base font-semibold text-white">
              Healthcare Demand, Regulatory and Adoption Trend
            </h3>
          </GlassCardHeader>
          <GlassCardContent>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart
                  data={healthcareTrend}
                  margin={{ top: 4, right: 8, bottom: 0, left: -20 }}
                >
                  <defs>
                    <linearGradient id="hcDemand" x1="0" y1="0" x2="0" y2="1">
                      <stop
                        offset="0%"
                        stopColor="#10b981"
                        stopOpacity={0.35}
                      />
                      <stop offset="100%" stopColor="#10b981" stopOpacity={0} />
                    </linearGradient>
                    <linearGradient id="hcReg" x1="0" y1="0" x2="0" y2="1">
                      <stop
                        offset="0%"
                        stopColor="#22d3ee"
                        stopOpacity={0.28}
                      />
                      <stop offset="100%" stopColor="#22d3ee" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid
                    strokeDasharray="3 3"
                    stroke="rgba(255,255,255,0.05)"
                  />
                  <XAxis
                    dataKey="month"
                    tick={{ fill: "rgba(255,255,255,0.35)", fontSize: 11 }}
                    axisLine={false}
                    tickLine={false}
                  />
                  <YAxis
                    tick={{ fill: "rgba(255,255,255,0.35)", fontSize: 11 }}
                    axisLine={false}
                    tickLine={false}
                  />
                  <Tooltip {...tooltipStyle} />
                  <Area
                    type="monotone"
                    dataKey="demand"
                    name="Clinical Demand"
                    stroke="#10b981"
                    strokeWidth={2}
                    fill="url(#hcDemand)"
                  />
                  <Area
                    type="monotone"
                    dataKey="regulatory"
                    name="Regulatory Readiness"
                    stroke="#22d3ee"
                    strokeWidth={2}
                    fill="url(#hcReg)"
                  />
                  <Area
                    type="monotone"
                    dataKey="adoption"
                    name="Provider Adoption"
                    stroke="#6366f1"
                    strokeWidth={1.5}
                    fill="transparent"
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </GlassCardContent>
        </GlassCard>

        <GlassCard>
          <GlassCardHeader>
            <h3 className="text-base font-semibold text-white">
              Readiness Radar
            </h3>
          </GlassCardHeader>
          <GlassCardContent>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <RadarChart data={readiness}>
                  <PolarGrid stroke="rgba(255,255,255,0.12)" />
                  <PolarAngleAxis
                    dataKey="metric"
                    tick={{ fill: "rgba(255,255,255,0.55)", fontSize: 10 }}
                  />
                  <PolarRadiusAxis
                    angle={30}
                    domain={[0, 100]}
                    tick={{ fill: "rgba(255,255,255,0.25)", fontSize: 9 }}
                  />
                  <Radar
                    name="Readiness"
                    dataKey="score"
                    stroke="#10b981"
                    fill="#10b981"
                    fillOpacity={0.24}
                  />
                </RadarChart>
              </ResponsiveContainer>
            </div>
          </GlassCardContent>
        </GlassCard>
      </div>

      <div className="grid lg:grid-cols-2 gap-5">
        <GlassCard>
          <GlassCardHeader>
            <h3 className="text-base font-semibold text-white">
              Regulatory Checklist
            </h3>
          </GlassCardHeader>
          <GlassCardContent className="space-y-3">
            {[
              {
                label: "HIPAA Compliance Mapping",
                progress: 92,
                icon: FileCheck2,
              },
              {
                label: "FDA Pathway Assessment",
                progress: 74,
                icon: FlaskConical,
              },
              {
                label: "Clinical Validation Plan",
                progress: 68,
                icon: Activity,
              },
            ].map((item) => (
              <div
                key={item.label}
                className="rounded-xl border border-white/[0.08] bg-white/[0.03] p-3"
              >
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2 text-sm text-white">
                    <item.icon className="w-4 h-4 text-emerald-300" />
                    <span>{item.label}</span>
                  </div>
                  <span className="text-xs text-white/50">
                    {item.progress}%
                  </span>
                </div>
                <AnimatedProgress value={item.progress} />
              </div>
            ))}
            <AnimatedButton size="sm">
              Generate Healthcare Summary
            </AnimatedButton>
          </GlassCardContent>
        </GlassCard>

        <GlassCard>
          <GlassCardHeader>
            <h3 className="text-base font-semibold text-white">
              Healthcare Competitor Watchlist
            </h3>
          </GlassCardHeader>
          <GlassCardContent className="space-y-3">
            {watchlist.map((c, i) => (
              <motion.div
                key={c.name}
                initial={{ opacity: 0, x: 16 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: i * 0.06 }}
                className="rounded-xl border border-white/[0.08] bg-white/[0.03] px-4 py-3 flex items-center justify-between"
              >
                <div>
                  <div className="text-sm font-semibold text-white">
                    {c.name}
                  </div>
                  <div className="text-xs text-white/50">
                    {c.focus} • {c.stage}
                  </div>
                </div>
                <span className="text-xs px-2.5 py-1 rounded-full border border-white/15 text-white/75">
                  Threat: {c.threat}
                </span>
              </motion.div>
            ))}
          </GlassCardContent>
        </GlassCard>
      </div>
    </div>
  );
}
