"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import {
  HeartPulse,
  Building2,
  FileCheck2,
} from "lucide-react";
import {
  GlassCard,
  GlassCardContent,
  GlassCardHeader,
} from "@/components/ui/glass-card";
import { AnimatedBadge } from "@/components/ui/animated-badge";
import { AnimatedButton } from "@/components/ui/animated-button";
import { EmptyResearchState } from "@/components/dashboard/empty-research-state";
import { loadLastResearch } from "@/lib/research-store";

export default function HealthcareModePage() {
  const [liveData, setLiveData] = useState<any>(null);
  const [checked, setChecked] = useState(false);

  useEffect(() => {
    const stored = loadLastResearch();
    setLiveData(stored?.result ?? null);
    setChecked(true);
  }, []);

  if (!checked) return null;

  if (!liveData) {
    return (
      <div className="space-y-6 max-w-7xl mx-auto">
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
        <EmptyResearchState
          title="No research yet"
          description="Run a market research analysis with Healthcare Mode enabled to see clinical trends, regulatory risks, and healthcare-specific competitors here."
        />
      </div>
    );
  }

  if (liveData.healthcare_mode !== true) {
    return (
      <div className="space-y-6 max-w-7xl mx-auto">
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
        <EmptyResearchState
          title="Last research wasn't in Healthcare Mode"
          description="Run a new market research analysis with Healthcare Mode enabled to see clinical trends, regulatory risks, and healthcare-specific competitors here."
        />
      </div>
    );
  }

  const research = liveData.research ?? {};
  const trends = liveData.trends ?? {};
  const risks = liveData.risks ?? {};
  const competitors = liveData.competitors?.competitors ?? [];

  const regulatoryRisks = (risks.risks ?? []).filter((r: any) => r.category === "regulatory");

  const kpis = [
    { label: "TAM (Healthcare)", value: research.market_size_estimate || "—", icon: Building2 },
    { label: "Market Growth Rate", value: trends.market_growth_rate || "—", icon: HeartPulse },
  ];

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

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        {kpis.map((metric, i) => (
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

      <div className="grid lg:grid-cols-2 gap-5">
        <GlassCard>
          <GlassCardHeader>
            <h3 className="text-base font-semibold text-white">
              Healthcare Trends
            </h3>
          </GlassCardHeader>
          <GlassCardContent className="space-y-3">
            {(trends.trends ?? []).length ? (
              (trends.trends ?? []).map((t: any) => (
                <div
                  key={t.name}
                  className="rounded-xl border border-white/[0.08] bg-white/[0.03] p-3"
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-sm font-medium text-white">{t.name}</span>
                    <span className="text-xs px-2 py-0.5 rounded-full border border-white/15 text-white/70">
                      {t.direction} · {t.impact} impact
                    </span>
                  </div>
                  <p className="text-xs text-white/50">{t.description}</p>
                </div>
              ))
            ) : (
              <p className="text-sm text-white/40 py-4 text-center">No trend data found.</p>
            )}
            {(trends.regulatory_trends ?? []).length > 0 && (
              <div className="rounded-xl border border-white/[0.08] bg-white/[0.03] p-3">
                <div className="text-xs font-semibold text-emerald-400 mb-2">Regulatory Trends</div>
                <ul className="space-y-1">
                  {trends.regulatory_trends.map((r: string) => (
                    <li key={r} className="text-xs text-white/50">• {r}</li>
                  ))}
                </ul>
              </div>
            )}
          </GlassCardContent>
        </GlassCard>

        <GlassCard>
          <GlassCardHeader>
            <div className="flex items-center gap-2">
              <FileCheck2 className="w-4 h-4 text-emerald-300" />
              <h3 className="text-base font-semibold text-white">
                Regulatory Risks
              </h3>
            </div>
          </GlassCardHeader>
          <GlassCardContent className="space-y-3">
            {regulatoryRisks.length ? (
              regulatoryRisks.map((r: any) => (
                <div
                  key={r.name}
                  className="rounded-xl border border-white/[0.08] bg-white/[0.03] p-3"
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-sm font-medium text-white">{r.name}</span>
                    <span className={`text-xs px-2 py-0.5 rounded-full ${r.severity === 'high' ? 'bg-red-500/15 text-red-400' : r.severity === 'medium' ? 'bg-yellow-500/15 text-yellow-400' : 'bg-emerald-500/15 text-emerald-400'}`}>
                      {r.severity}
                    </span>
                  </div>
                  <p className="text-xs text-white/50 mb-1">{r.description}</p>
                  <p className="text-xs text-white/35">Mitigation: {r.mitigation}</p>
                </div>
              ))
            ) : (
              <p className="text-sm text-white/40 py-4 text-center">No regulatory risks identified.</p>
            )}
            <AnimatedButton size="sm">
              Generate Healthcare Summary
            </AnimatedButton>
          </GlassCardContent>
        </GlassCard>
      </div>

      <GlassCard>
        <GlassCardHeader>
          <h3 className="text-base font-semibold text-white">
            Healthcare Competitor Watchlist
          </h3>
        </GlassCardHeader>
        <GlassCardContent className="space-y-3">
          {competitors.length ? (
            competitors.map((c: any, i: number) => (
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
                    {c.description}
                  </div>
                </div>
                <span className="text-xs px-2.5 py-1 rounded-full border border-white/15 text-white/75 capitalize">
                  Threat: {c.threat_level ?? "low"}
                </span>
              </motion.div>
            ))
          ) : (
            <p className="text-sm text-white/40 py-4 text-center">No competitors found.</p>
          )}
        </GlassCardContent>
      </GlassCard>
    </div>
  );
}
