'use client';

import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import {
  Compass, Target, TrendingUp, Globe, Cpu, Zap,
  ChevronRight, BarChart3, Lightbulb, Search,
} from 'lucide-react';
import { GlassCard, GlassCardContent, GlassCardHeader } from '@/components/ui/glass-card';
import { AnimatedBadge } from '@/components/ui/animated-badge';
import { AnimatedProgress } from '@/components/ui/animated-progress';
import { EmptyResearchState } from '@/components/dashboard/empty-research-state';
import { loadLastResearch } from '@/lib/research-store';

// ── Helpers ───────────────────────────────────────────────────────────────────
function OpportunityScore({ score }: { score: number }) {
  const s = Math.min(100, Math.max(0, score ?? 0));
  const color = s >= 75 ? 'from-emerald-500 to-teal-500' : s >= 50 ? 'from-indigo-500 to-violet-500' : 'from-amber-500 to-orange-500';
  const textColor = s >= 75 ? 'text-emerald-400' : s >= 50 ? 'text-indigo-400' : 'text-amber-400';
  return (
    <div className="flex items-center gap-4 p-4 rounded-xl bg-white/5 border border-white/10">
      <div className={`w-14 h-14 rounded-2xl bg-gradient-to-br ${color} flex items-center justify-center flex-shrink-0`}>
        <span className="text-white text-lg font-bold">{s}</span>
      </div>
      <div>
        <div className="text-xs text-white/50 mb-1">White Space Opportunity Score</div>
        <div className={`text-2xl font-bold ${textColor}`}>{s}/100</div>
        <AnimatedProgress value={s} variant="glow" className="mt-2 w-48" />
      </div>
    </div>
  );
}

const GAP_CATEGORIES = [
  { key: 'identified_gaps',      label: 'Identified Gaps',         icon: Search,    color: 'from-indigo-500 to-violet-500' },
  { key: 'market_opportunities', label: 'Market Opportunities',    icon: Target,    color: 'from-emerald-500 to-teal-500' },
  { key: 'technical_gaps',       label: 'Technical Gaps',          icon: Cpu,       color: 'from-amber-500 to-orange-500' },
  { key: 'geographic_gaps',      label: 'Geographic Opportunities', icon: Globe,    color: 'from-blue-500 to-cyan-500' },
  { key: 'competitive_gaps',     label: 'Competitive White Spaces', icon: TrendingUp, color: 'from-rose-500 to-pink-500' },
  { key: 'unmet_needs',          label: 'Unmet Customer Needs',    icon: Lightbulb, color: 'from-violet-500 to-purple-500' },
] as const;

// ── Page ───────────────────────────────────────────────────────────────────────
export default function WhiteSpacePage() {
  const [gaps, setGaps] = useState<any>(null);
  const [idea, setIdea] = useState('');
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    const stored = loadLastResearch();
    setGaps(stored?.result?.research_gaps ?? null);
    setIdea(stored?.idea ?? '');
    setLoaded(true);
  }, []);

  if (!loaded) return null;

  if (!gaps) {
    return (
      <div className="space-y-8 max-w-7xl mx-auto">
        <Header />
        <EmptyResearchState
          title="No research yet"
          description="Run a market research analysis to discover white spaces, unmet needs, and unexplored opportunities in your target market."
        />
      </div>
    );
  }

  const opportunityScore: number = gaps.opportunity_score ?? 0;
  const summary: string = gaps.summary ?? gaps.gap_summary ?? '';
  const evidenceQuality: string = gaps.evidence_quality ?? '';

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      <Header />

      {/* Opportunity Score */}
      <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between">
        <OpportunityScore score={opportunityScore} />
        {evidenceQuality && (
          <AnimatedBadge variant={evidenceQuality === 'high' ? 'success' : evidenceQuality === 'medium' ? 'warning' : 'default'}>
            Evidence: {evidenceQuality}
          </AnimatedBadge>
        )}
      </div>

      {/* Summary */}
      {summary && (
        <GlassCard>
          <GlassCardHeader>
            <div className="flex items-center gap-2">
              <Compass className="w-5 h-5 text-indigo-400" />
              <h2 className="text-base font-semibold text-white">White Space Overview</h2>
            </div>
          </GlassCardHeader>
          <GlassCardContent>
            <p className="text-sm text-white/70 leading-relaxed">{summary}</p>
            {idea && (
              <p className="text-xs text-white/35 mt-3 pt-3 border-t border-white/8">
                Analysis for: <span className="text-white/55">{idea}</span>
              </p>
            )}
          </GlassCardContent>
        </GlassCard>
      )}

      {/* Gap Categories */}
      <div className="grid md:grid-cols-2 gap-5">
        {GAP_CATEGORIES.map(({ key, label, icon: Icon, color }) => {
          const items: string[] = Array.isArray(gaps[key]) ? gaps[key] : [];
          if (items.length === 0) return null;
          return (
            <motion.div
              key={key}
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
            >
              <GlassCard>
                <GlassCardHeader>
                  <div className="flex items-center gap-2">
                    <div className={`w-8 h-8 rounded-lg bg-gradient-to-br ${color} flex items-center justify-center`}>
                      <Icon className="w-4 h-4 text-white" />
                    </div>
                    <h3 className="text-sm font-semibold text-white">{label}</h3>
                    <span className="ml-auto text-xs text-white/30">{items.length}</span>
                  </div>
                </GlassCardHeader>
                <GlassCardContent>
                  <ul className="space-y-2">
                    {items.map((item, i) => (
                      <motion.li
                        key={i}
                        initial={{ opacity: 0, x: -6 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: i * 0.04 }}
                        className="flex items-start gap-2 text-sm text-white/65"
                      >
                        <ChevronRight className="w-3.5 h-3.5 text-indigo-400 flex-shrink-0 mt-0.5" />
                        {item}
                      </motion.li>
                    ))}
                  </ul>
                </GlassCardContent>
              </GlassCard>
            </motion.div>
          );
        })}
      </div>

      {/* Raw adjacency gaps if model uses different keys */}
      {(() => {
        const extraKeys = Object.keys(gaps).filter(
          (k) => !['opportunity_score', 'summary', 'gap_summary', 'evidence_quality', 'sources',
            'unsupported_claims', '_validation_warnings', '_hallucination_flags',
            ...GAP_CATEGORIES.map((c) => c.key)].includes(k)
            && Array.isArray(gaps[k]) && (gaps[k] as string[]).length > 0
        );
        if (extraKeys.length === 0) return null;
        return (
          <GlassCard>
            <GlassCardHeader>
              <div className="flex items-center gap-2">
                <Zap className="w-5 h-5 text-amber-400" />
                <h2 className="text-base font-semibold text-white">Additional Insights</h2>
              </div>
            </GlassCardHeader>
            <GlassCardContent>
              {extraKeys.map((k) => (
                <div key={k} className="mb-4">
                  <h3 className="text-xs font-semibold text-white/50 uppercase tracking-wider mb-2">
                    {k.replace(/_/g, ' ')}
                  </h3>
                  <ul className="space-y-1.5">
                    {(gaps[k] as string[]).map((item: string, i: number) => (
                      <li key={i} className="flex items-start gap-2 text-sm text-white/65">
                        <ChevronRight className="w-3.5 h-3.5 text-indigo-400 flex-shrink-0 mt-0.5" />
                        {item}
                      </li>
                    ))}
                  </ul>
                </div>
              ))}
            </GlassCardContent>
          </GlassCard>
        );
      })()}
    </div>
  );
}

function Header() {
  return (
    <div>
      <h1 className="text-2xl font-bold text-white mb-1">
        White Space <span className="bg-gradient-to-r from-emerald-400 to-teal-400 bg-clip-text text-transparent">Discovery</span>
      </h1>
      <p className="text-white/50 text-sm">Unexplored market gaps, unmet needs, and differentiation opportunities.</p>
    </div>
  );
}
