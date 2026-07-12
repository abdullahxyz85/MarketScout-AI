'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Sliders, Play, AlertTriangle, TrendingUp, TrendingDown,
  Minus, ArrowRight, CheckCircle, XCircle, Clock,
  DollarSign, Users, Globe, Cpu, Target, Lightbulb,
} from 'lucide-react';
import { GlassCard, GlassCardContent, GlassCardHeader } from '@/components/ui/glass-card';
import { AnimatedButton } from '@/components/ui/animated-button';
import { loadLastResearch } from '@/lib/research-store';
import { useResearchHistory } from '@/lib/use-research-history';
import { ResearchPicker } from '@/components/dashboard/research-picker';

const SCENARIO_FIELDS = [
  {
    key: 'pricing_strategy',
    label: 'Pricing Strategy',
    icon: DollarSign,
    placeholder: 'e.g. Freemium, $29/seat/mo, Usage-based',
    color: 'from-emerald-500 to-teal-500',
  },
  {
    key: 'target_market',
    label: 'Target Market',
    icon: Target,
    placeholder: 'e.g. Enterprise only, SMBs in Europe',
    color: 'from-violet-500 to-purple-500',
  },
  {
    key: 'geography',
    label: 'Geography',
    icon: Globe,
    placeholder: 'e.g. US-only, EMEA, Southeast Asia',
    color: 'from-blue-500 to-cyan-500',
  },
  {
    key: 'technology_choice',
    label: 'Technology Choice',
    icon: Cpu,
    placeholder: 'e.g. Open-source LLM, proprietary API',
    color: 'from-amber-500 to-orange-500',
  },
  {
    key: 'team_size',
    label: 'Team Size',
    icon: Users,
    placeholder: 'e.g. 3-person founding team, 10 engineers',
    color: 'from-pink-500 to-rose-500',
  },
  {
    key: 'funding_amount',
    label: 'Funding Amount',
    icon: Lightbulb,
    placeholder: 'e.g. Bootstrapped, $500K seed, $5M Series A',
    color: 'from-indigo-500 to-blue-500',
  },
] as const;

type ScenarioKey = typeof SCENARIO_FIELDS[number]['key'];

interface ImpactItem {
  change: string;
  magnitude?: string;
  explanation: string;
  estimated_range?: string;
  estimated_timeline?: string;
  new_risks?: string[];
  mitigated_risks?: string[];
}

interface ScenarioResult {
  scenario_summary?: string;
  impact_analysis?: {
    market_opportunity?: ImpactItem;
    competitive_positioning?: ImpactItem;
    revenue_potential?: ImpactItem;
    risk_profile?: ImpactItem;
    time_to_market?: ImpactItem;
  };
  overall_recommendation?: string;
  key_action_items?: string[];
}

function ChangeIcon({ change }: { change: string }) {
  const positive = ['increase', 'stronger', 'higher', 'faster'];
  const negative = ['decrease', 'weaker', 'lower', 'slower'];
  if (positive.some(k => change?.toLowerCase().includes(k)))
    return <TrendingUp className="w-5 h-5 text-emerald-400" />;
  if (negative.some(k => change?.toLowerCase().includes(k)))
    return <TrendingDown className="w-5 h-5 text-red-400" />;
  return <Minus className="w-5 h-5 text-gray-400" />;
}

function RecommendationBadge({ rec }: { rec?: string }) {
  if (!rec) return null;
  const cfg: Record<string, { color: string; icon: typeof CheckCircle }> = {
    Proceed:                  { color: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/30', icon: CheckCircle },
    'Proceed with Caution':   { color: 'text-amber-400 bg-amber-500/10 border-amber-500/30',     icon: AlertTriangle },
    Avoid:                    { color: 'text-red-400 bg-red-500/10 border-red-500/30',            icon: XCircle },
  };
  const key = Object.keys(cfg).find(k => rec.includes(k)) ?? 'Proceed with Caution';
  const { color, icon: Icon } = cfg[key];
  return (
    <span className={`inline-flex items-center gap-2 px-4 py-2 rounded-full border text-sm font-semibold ${color}`}>
      <Icon className="w-4 h-4" />
      {rec}
    </span>
  );
}

export default function ScenariosPage() {
  const [jobId, setJobId] = useState(() => loadLastResearch()?.jobId ?? '');
  const { history, loading: historyLoading } = useResearchHistory();
  const [scenario, setScenario] = useState<Partial<Record<ScenarioKey, string>>>({});
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<ScenarioResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const filledCount = Object.values(scenario).filter(Boolean).length;

  async function runScenario() {
    if (!jobId.trim() || filledCount === 0) return;
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const res = await fetch(`/api/agents/research/${jobId.trim()}/scenario`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ base_job_id: jobId.trim(), scenario }),
      });
      if (!res.ok) throw new Error(await res.text());
      setResult(await res.json());
    } catch (e: any) {
      setError(e.message ?? 'Simulation failed');
    } finally {
      setLoading(false);
    }
  }

  const impacts = result?.impact_analysis
    ? ([
        ['Market Opportunity',       result.impact_analysis.market_opportunity],
        ['Competitive Positioning',  result.impact_analysis.competitive_positioning],
        ['Revenue Potential',        result.impact_analysis.revenue_potential],
        ['Risk Profile',             result.impact_analysis.risk_profile],
        ['Time to Market',           result.impact_analysis.time_to_market],
      ] as [string, ImpactItem | undefined][]).filter(([, v]) => !!v)
    : [];

  return (
    <div className="min-h-screen p-6 space-y-6">
      {/* Header */}
      <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }}>
        <div className="flex items-center gap-3 mb-1">
          <div className="p-2 rounded-xl bg-gradient-to-br from-violet-500 to-purple-600">
            <Sliders className="w-6 h-6 text-white" />
          </div>
          <h1 className="text-2xl font-bold text-white">Scenario Simulator</h1>
        </div>
        <p className="text-gray-400 ml-14">
          Simulate "what-if" scenarios against a completed research report.
        </p>
      </motion.div>

      <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
        {/* Left — Config */}
        <div className="space-y-5">
          {/* Job ID input */}
          <motion.div initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.1 }}>
            <GlassCard>
              <GlassCardHeader>
                <span className="text-white font-semibold">Base Research Job</span>
              </GlassCardHeader>
              <GlassCardContent className="space-y-3">
                <div>
                  <label className="text-xs text-gray-400 mb-1 block">Pick from your research history</label>
                  <ResearchPicker history={history} loading={historyLoading} onSelect={setJobId} className="py-2.5" />
                </div>
                <div>
                  <label className="text-xs text-gray-400 mb-1 block">Job ID</label>
                  <input
                    value={jobId}
                    onChange={e => setJobId(e.target.value)}
                    placeholder="Paste a completed job ID, or the last one is pre-filled"
                    className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-2.5 text-white text-sm placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-violet-500/50"
                  />
                  {loadLastResearch()?.idea && (
                    <p className="text-xs text-gray-500 mt-1.5">
                      Last research: <span className="text-violet-300">{loadLastResearch()?.idea}</span>
                    </p>
                  )}
                </div>
              </GlassCardContent>
            </GlassCard>
          </motion.div>

          {/* Scenario parameters */}
          <motion.div initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.15 }}>
            <GlassCard>
              <GlassCardHeader>
                <div className="flex items-center justify-between">
                  <span className="text-white font-semibold">Scenario Parameters</span>
                  <span className="text-xs text-gray-400">{filledCount} / {SCENARIO_FIELDS.length} filled</span>
                </div>
              </GlassCardHeader>
              <GlassCardContent className="space-y-4">
                {SCENARIO_FIELDS.map(({ key, label, icon: Icon, placeholder, color }, i) => (
                  <motion.div
                    key={key}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.2 + i * 0.05 }}
                  >
                    <label className="flex items-center gap-2 text-sm text-gray-300 mb-1.5">
                      <span className={`p-1 rounded-md bg-gradient-to-br ${color}`}>
                        <Icon className="w-3.5 h-3.5 text-white" />
                      </span>
                      {label}
                    </label>
                    <input
                      value={scenario[key] ?? ''}
                      onChange={e => setScenario(s => ({ ...s, [key]: e.target.value }))}
                      placeholder={placeholder}
                      className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-2.5 text-white text-sm placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-violet-500/50"
                    />
                  </motion.div>
                ))}
              </GlassCardContent>
            </GlassCard>
          </motion.div>

          <AnimatedButton
            onClick={runScenario}
            disabled={!jobId.trim() || filledCount === 0 || loading}
            className="w-full"
          >
            {loading ? (
              <span className="flex items-center gap-2">
                <svg className="animate-spin w-4 h-4" viewBox="0 0 24 24" fill="none">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z" />
                </svg>
                Running Simulation…
              </span>
            ) : (
              <span className="flex items-center gap-2">
                <Play className="w-4 h-4" /> Run Scenario
              </span>
            )}
          </AnimatedButton>

          {error && (
            <div className="flex items-start gap-2 p-4 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 text-sm">
              <AlertTriangle className="w-4 h-4 mt-0.5 shrink-0" />
              {error}
            </div>
          )}
        </div>

        {/* Right — Results */}
        <div>
          <AnimatePresence mode="wait">
            {!result && !loading && (
              <motion.div
                key="empty"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="h-full flex items-center justify-center"
              >
                <div className="text-center text-gray-500 py-24">
                  <Sliders className="w-12 h-12 mx-auto mb-4 opacity-30" />
                  <p className="text-sm">Fill in at least one scenario parameter<br />and click Run Scenario.</p>
                </div>
              </motion.div>
            )}

            {loading && (
              <motion.div
                key="loading"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="h-full flex items-center justify-center"
              >
                <div className="text-center py-24">
                  <div className="w-12 h-12 rounded-full border-2 border-violet-500/30 border-t-violet-500 animate-spin mx-auto mb-4" />
                  <p className="text-gray-400 text-sm">Simulating scenario…</p>
                </div>
              </motion.div>
            )}

            {result && (
              <motion.div
                key="result"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                className="space-y-4"
              >
                {/* Summary */}
                <GlassCard>
                  <GlassCardHeader>
                    <span className="text-white font-semibold">Scenario Summary</span>
                  </GlassCardHeader>
                  <GlassCardContent className="space-y-3">
                    {result.scenario_summary && (
                      <p className="text-gray-300 text-sm leading-relaxed">{result.scenario_summary}</p>
                    )}
                    {result.overall_recommendation && (
                      <RecommendationBadge rec={result.overall_recommendation} />
                    )}
                  </GlassCardContent>
                </GlassCard>

                {/* Impact grid */}
                {impacts.length > 0 && (
                  <div className="grid grid-cols-1 gap-3">
                    {impacts.map(([label, item], i) => (
                      <motion.div
                        key={label}
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: i * 0.07 }}
                      >
                        <GlassCard>
                          <GlassCardContent className="py-3">
                            <div className="flex items-start justify-between gap-3">
                              <div className="flex items-center gap-2">
                                <ChangeIcon change={item?.change ?? ''} />
                                <span className="text-white text-sm font-medium">{label}</span>
                              </div>
                              {item?.change && (
                                <span className="text-xs px-2 py-0.5 rounded-full bg-white/5 text-gray-300 border border-white/10 capitalize">
                                  {item.change}
                                  {item.magnitude ? ` · ${item.magnitude}` : ''}
                                </span>
                              )}
                            </div>
                            {item?.explanation && (
                              <p className="text-gray-400 text-xs mt-2 leading-relaxed">{item.explanation}</p>
                            )}
                            {item?.estimated_range && (
                              <p className="text-emerald-400 text-xs mt-1">💰 {item.estimated_range}</p>
                            )}
                            {item?.estimated_timeline && (
                              <p className="text-cyan-400 text-xs mt-1 flex items-center gap-1">
                                <Clock className="w-3 h-3" /> {item.estimated_timeline}
                              </p>
                            )}
                          </GlassCardContent>
                        </GlassCard>
                      </motion.div>
                    ))}
                  </div>
                )}

                {/* Action items */}
                {result.key_action_items && result.key_action_items.length > 0 && (
                  <GlassCard>
                    <GlassCardHeader>
                      <span className="text-white font-semibold">Key Action Items</span>
                    </GlassCardHeader>
                    <GlassCardContent>
                      <ul className="space-y-2">
                        {result.key_action_items.map((item, i) => (
                          <li key={i} className="flex items-start gap-2 text-sm text-gray-300">
                            <ArrowRight className="w-4 h-4 text-violet-400 shrink-0 mt-0.5" />
                            {item}
                          </li>
                        ))}
                      </ul>
                    </GlassCardContent>
                  </GlassCard>
                )}
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </div>
  );
}
