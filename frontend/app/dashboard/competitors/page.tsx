"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { Building2, Target, ShieldAlert } from "lucide-react";
import {
  GlassCard,
  GlassCardContent,
  GlassCardHeader,
} from "@/components/ui/glass-card";
import { EmptyResearchState } from "@/components/dashboard/empty-research-state";
import { loadLastResearch } from "@/lib/research-store";

interface Competitor {
  name: string;
  segment: string;
  threat: string;
  marketShare: string;
}

export default function CompetitorsPage() {
  const [competitors, setCompetitors] = useState<Competitor[] | null>(null);

  useEffect(() => {
    const stored = loadLastResearch();
    const real = (stored?.result?.competitors as any)?.competitors;
    if (real?.length) {
      setCompetitors(
        real.map((c: any) => ({
          name: c.name,
          segment: c.description ?? "",
          threat: (c.threat_level ?? "low").replace(/^\w/, (ch: string) => ch.toUpperCase()),
          marketShare: c.market_share ?? "0%",
        }))
      );
    } else {
      setCompetitors([]);
    }
  }, []);

  if (competitors === null) return null;

  if (competitors.length === 0) {
    return (
      <div className="space-y-8 max-w-7xl mx-auto">
        <div>
          <h1 className="text-2xl font-bold text-white mb-1">
            Competitor{" "}
            <span className="bg-gradient-to-r from-indigo-400 to-cyan-400 bg-clip-text text-transparent">
              Landscape
            </span>
          </h1>
          <p className="text-white/45 text-sm">
            Track competitors, market share, and strategic threat levels.
          </p>
        </div>
        <EmptyResearchState
          title="No research yet"
          description="Run a market research analysis to see the competitors it found, their market share, and threat levels."
        />
      </div>
    );
  }

  const highThreatCount = competitors.filter((c) => c.threat.toLowerCase() === "high").length;
  const topShare = Math.max(
    ...competitors.map((c) => parseFloat(c.marketShare.replace("%", "")) || 0)
  );

  const kpis = [
    { label: "Competitors Tracked", value: String(competitors.length), icon: Building2 },
    { label: "High Threat", value: String(highThreatCount), icon: ShieldAlert },
    { label: "Top Share", value: `${topShare}%`, icon: Target },
  ];

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      <div>
        <h1 className="text-2xl font-bold text-white mb-1">
          Competitor{" "}
          <span className="bg-gradient-to-r from-indigo-400 to-cyan-400 bg-clip-text text-transparent">
            Landscape
          </span>
        </h1>
        <p className="text-white/45 text-sm">
          Track competitors, market share, and strategic threat levels.
        </p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        {kpis.map((metric, i) => (
          <motion.div
            key={metric.label}
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.07 }}
          >
            <GlassCard>
              <GlassCardContent>
                <div className="flex items-center justify-between mb-2">
                  <metric.icon className="w-5 h-5 text-indigo-300" />
                </div>
                <div className="text-xl font-bold text-white">
                  {metric.value}
                </div>
                <div className="text-xs text-white/45">{metric.label}</div>
              </GlassCardContent>
            </GlassCard>
          </motion.div>
        ))}
      </div>

      <GlassCard>
        <GlassCardHeader>
          <h3 className="text-base font-semibold text-white">
            Top Competitors
          </h3>
        </GlassCardHeader>
        <GlassCardContent>
          <div className="space-y-3">
            {competitors.map((item, i) => (
              <motion.div
                key={item.name}
                initial={{ opacity: 0, x: 12 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: i * 0.08 }}
                className="flex items-center justify-between rounded-xl border border-white/[0.08] bg-white/[0.03] px-4 py-3"
              >
                <div>
                  <div className="text-sm font-medium text-white">
                    {item.name}
                  </div>
                  <div className="text-xs text-white/45">{item.segment}</div>
                </div>
                <div className="text-right">
                  <div className="text-sm text-white">{item.marketShare}</div>
                  <div
                    className={`text-xs font-medium ${
                      item.threat.toLowerCase() === "high"
                        ? "text-red-400"
                        : item.threat.toLowerCase() === "medium"
                          ? "text-yellow-400"
                          : "text-emerald-400"
                    }`}
                  >
                    Threat: {item.threat}
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </GlassCardContent>
      </GlassCard>
    </div>
  );
}
