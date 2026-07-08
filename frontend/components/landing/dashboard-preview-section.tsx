"use client";

import { motion } from "framer-motion";
import {
  LayoutDashboard,
  Search,
  Users,
  FileText,
  Settings,
  BarChart3,
  TrendingUp,
  Activity,
  Building2,
  AlertCircle,
  Zap,
  ChevronRight,
} from "lucide-react";
import { AnimatedProgress } from "@/components/ui/animated-progress";
import { AnimatedBadge, StatusBadge } from "@/components/ui/animated-badge";

const sidebarItems = [
  { icon: LayoutDashboard, label: "Dashboard", active: true },
  { icon: Search, label: "Research", active: false },
  { icon: Users, label: "Competitors", active: false },
  { icon: FileText, label: "Reports", active: false },
  { icon: Settings, label: "Settings", active: false },
];

const competitors = [
  { name: "TechCorp AI", marketShare: "28%", threat: "High" as const },
  { name: "DataGenius", marketShare: "22%", threat: "Medium" as const },
  { name: "InsightLab", marketShare: "15%", threat: "Low" as const },
];

export function DashboardPreviewSection() {
  return (
    <section className="py-24 relative">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-16"
        >
          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-white mb-4">
            Powerful <span className="text-gradient">Dashboard</span>
          </h2>
          <p className="text-lg text-white/60 max-w-2xl mx-auto">
            Monitor all your research projects, track agent progress, and access
            insights in real-time.
          </p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 40 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="relative rounded-3xl overflow-hidden backdrop-blur-2xl border border-white/10 bg-gradient-to-br from-white/[0.05] via-white/[0.03] to-transparent shadow-2xl"
        >
          <div className="absolute inset-0 bg-gradient-to-br from-indigo-500/5 via-transparent to-purple-500/5" />

          <div className="grid lg:grid-cols-[240px_1fr]">
            {/* Sidebar */}
            <div className="border-r border-white/10 p-4 space-y-1 hidden lg:block bg-white/[0.015]">
              <div className="px-3 py-2 mb-4">
                <span className="text-lg font-bold text-white">
                  MarketScout
                </span>
              </div>
              {sidebarItems.map((item) => (
                <motion.div
                  key={item.label}
                  whileHover={{ x: 4 }}
                  className={`flex items-center gap-3 px-3 py-2.5 rounded-lg cursor-pointer transition-colors ${
                    item.active
                      ? "bg-white/10 text-white"
                      : "text-white/60 hover:text-white hover:bg-white/5"
                  }`}
                >
                  <item.icon className="w-5 h-5" />
                  <span className="text-sm font-medium">{item.label}</span>
                  {item.active && (
                    <ChevronRight className="w-4 h-4 ml-auto text-indigo-400" />
                  )}
                </motion.div>
              ))}
            </div>

            {/* Main Content */}
            <div className="p-6">
              {/* Top Metrics */}
              <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
                {[
                  {
                    icon: BarChart3,
                    label: "Market Score",
                    value: "94.2",
                    change: "+12%",
                    color: "text-emerald-400",
                  },
                  {
                    icon: TrendingUp,
                    label: "Opportunity",
                    value: "87.8",
                    change: "+8%",
                    color: "text-indigo-400",
                  },
                  {
                    icon: Building2,
                    label: "Competition",
                    value: "Medium",
                    change: "24 found",
                    color: "text-purple-400",
                  },
                  {
                    icon: Activity,
                    label: "Funding Activity",
                    value: "High",
                    change: "$2.1B",
                    color: "text-cyan-400",
                  },
                ].map((metric) => (
                  <motion.div
                    key={metric.label}
                    whileHover={{ y: -2 }}
                    className="p-4 rounded-xl bg-white/[0.035] border border-white/10"
                  >
                    <metric.icon className={`w-5 h-5 ${metric.color} mb-2`} />
                    <div className="text-2xl font-bold text-white">
                      {metric.value}
                    </div>
                    <div className="text-xs text-white/50">{metric.label}</div>
                    <div className={`text-xs mt-1 ${metric.color}`}>
                      {metric.change}
                    </div>
                  </motion.div>
                ))}
              </div>

              <div className="grid lg:grid-cols-2 gap-6">
                {/* Competitor Table */}
                <div className="p-4 rounded-xl bg-white/[0.035] border border-white/10">
                  <h3 className="text-sm font-semibold text-white mb-4">
                    Competitor Analysis
                  </h3>
                  <div className="space-y-3">
                    {competitors.map((comp, i) => (
                      <div
                        key={comp.name}
                        className="flex items-center justify-between p-3 rounded-lg bg-white/5"
                      >
                        <div className="flex items-center gap-3">
                          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-indigo-500 to-purple-500 flex items-center justify-center text-white text-xs font-bold">
                            {i + 1}
                          </div>
                          <div>
                            <div className="text-sm font-medium text-white">
                              {comp.name}
                            </div>
                            <div className="text-xs text-white/50">
                              Market: {comp.marketShare}
                            </div>
                          </div>
                        </div>
                        <StatusBadge
                          status={
                            comp.threat === "High"
                              ? "running"
                              : comp.threat === "Medium"
                                ? "pending"
                                : "completed"
                          }
                        />
                      </div>
                    ))}
                  </div>
                </div>

                {/* SWOT Panel */}
                <div className="p-4 rounded-xl bg-white/[0.035] border border-white/10">
                  <h3 className="text-sm font-semibold text-white mb-4">
                    SWOT Analysis
                  </h3>
                  <div className="grid grid-cols-2 gap-3">
                    {[
                      {
                        label: "Strengths",
                        count: 8,
                        color: "from-emerald-500 to-teal-500",
                      },
                      {
                        label: "Weaknesses",
                        count: 4,
                        color: "from-red-500 to-rose-500",
                      },
                      {
                        label: "Opportunities",
                        count: 12,
                        color: "from-indigo-500 to-blue-500",
                      },
                      {
                        label: "Threats",
                        count: 6,
                        color: "from-orange-500 to-amber-500",
                      },
                    ].map((item) => (
                      <div
                        key={item.label}
                        className="p-3 rounded-lg bg-white/5 border border-white/10"
                      >
                        <div
                          className={`text-xs font-medium mb-2 bg-gradient-to-r ${item.color} bg-clip-text text-transparent`}
                        >
                          {item.label}
                        </div>
                        <div className="text-2xl font-bold text-white">
                          {item.count}
                        </div>
                        <AnimatedProgress
                          value={item.count}
                          max={15}
                          className="mt-2"
                        />
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* Agent Status */}
              <div className="mt-6 p-4 rounded-xl bg-gradient-to-r from-indigo-500/12 via-purple-500/10 to-cyan-500/12 border border-white/10">
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-2">
                    <Zap className="w-5 h-5 text-indigo-400" />
                    <span className="text-sm font-semibold text-white">
                      AI Agents Status
                    </span>
                  </div>
                  <AnimatedBadge variant="success">8 Active</AnimatedBadge>
                </div>
                <div className="flex gap-2 flex-wrap">
                  {[
                    "Research",
                    "Competitor",
                    "Market",
                    "Trend",
                    "SWOT",
                    "Risk",
                  ].map((agent, i) => (
                    <motion.div
                      key={agent}
                      animate={{ opacity: [0.7, 1, 0.7] }}
                      transition={{
                        duration: 2,
                        repeat: Infinity,
                        delay: i * 0.2,
                      }}
                      className="px-3 py-1.5 rounded-full bg-white/10 border border-white/20 text-xs text-white/80"
                    >
                      {agent}
                    </motion.div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  );
}
