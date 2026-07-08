"use client";

import { useEffect, useMemo, useState } from "react";
import { motion } from "framer-motion";
import { Building2, Target, TrendingUp, ShieldAlert } from "lucide-react";
import {
  GlassCard,
  GlassCardContent,
  GlassCardHeader,
} from "@/components/ui/glass-card";

type ApiCompetitor = {
  id: string;
  name: string;
  segment: string | null;
  market_share: number | null;
  threat: string | null;
  trend: string | null;
  revenue: string | null;
};

export default function CompetitorsPage() {
  const [apiCompetitors, setApiCompetitors] = useState<ApiCompetitor[]>([]);

  useEffect(() => {
    let cancelled = false;
    fetch("/api/competitors", { credentials: "include" })
      .then((res) => (res.ok ? res.json() : []))
      .then((data: ApiCompetitor[]) => {
        if (!cancelled) setApiCompetitors(data);
      })
      .catch(() => {});
    return () => {
      cancelled = true;
    };
  }, []);

  const competitors = useMemo(
    () =>
      apiCompetitors.map((c) => ({
        name: c.name,
        segment: c.segment ?? "General Market",
        threat: c.threat
          ? c.threat[0].toUpperCase() + c.threat.slice(1)
          : "Medium",
        marketShare: `${c.market_share ?? 0}%`,
      })),
    [apiCompetitors],
  );

  const highThreatCount = apiCompetitors.filter((c) => c.threat === "high").length;
  const topShare = apiCompetitors.reduce((max, c) => Math.max(max, c.market_share ?? 0), 0);

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
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

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          { label: "Competitors Tracked", value: String(apiCompetitors.length), icon: Building2 },
          { label: "High Threat", value: String(highThreatCount), icon: ShieldAlert },
          { label: "Top Share", value: `${topShare}%`, icon: Target },
          { label: "Monthly Movement", value: "—", icon: TrendingUp },
        ].map((metric, i) => (
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
                  <span className="text-xs text-white/40">Live</span>
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
                  <div className="text-xs text-white/45">
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
