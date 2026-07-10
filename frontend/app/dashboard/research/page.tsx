'use client';

import { useCallback, useRef, useState } from 'react';
import dynamic from 'next/dynamic';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Sparkles, ArrowRight, Zap, BarChart3,
  ShieldAlert, FileText, Lightbulb, Clock,
  Compass, Activity, AlertCircle,
  Download, RefreshCw,
} from 'lucide-react';
import { GlassCard, GlassCardContent, GlassCardHeader } from '@/components/ui/glass-card';
import { AnimatedButton } from '@/components/ui/animated-button';
import { StatusBadge } from '@/components/ui/animated-badge';
import { AnimatedProgress } from '@/components/ui/animated-progress';
import { useResearch } from '@/lib/research-context';
import { AGENT_SEQUENCE as AGENTS } from '@/lib/agents';

const industries = [
  'Healthcare',
  'FinTech',
  'EdTech',
  'SaaS',
  'E-commerce',
  'AI/ML',
  'CleanTech',
  'Logistics',
];

const ForceGraph2D = dynamic(() => import('react-force-graph-2d'), { ssr: false });

const NODE_COLORS: Record<string, string> = {
  idea: '#6366f1', competitor: '#ef4444', paper: '#10b981',
  patent: '#f59e0b', funding: '#06b6d4', trend: '#a855f7',
  opportunity: '#84cc16',
};

export default function ResearchPage() {
  const {
    idea, setIdea,
    selectedIndustry, setSelectedIndustry,
    healthcareMode, setHealthcareMode,
    stage, activeAgentIdx, activeAgentName, progress, result, jobId, error,
    startResearch, resetForm,
  } = useResearch();
  const [scenario, setScenario] = useState({
    pricing_strategy: 'subscription',
    target_market: '',
    geography: '',
    technology_choice: '',
    team_size: '',
    funding_amount: '',
  });
  const [scenarioResult, setScenarioResult] = useState<any>(null);
  const [scenarioLoading, setScenarioLoading] = useState(false);

  // react-force-graph-2d sizes its canvas from the container's measured
  // bounding box; inside a flex/grid layout that box can read 0 on the very
  // first paint, leaving the graph invisible. Measuring explicitly and
  // passing width/height as props avoids relying on its own auto-sizing.
  // A callback ref (rather than useRef + useEffect keyed on `stage`) is required
  // here because this container only mounts once AnimatePresence's exit
  // animation for the previous stage finishes — a `stage`-keyed effect fires
  // before that mount happens and would find the ref still null.
  const graphObserverRef = useRef<ResizeObserver | null>(null);
  const [graphSize, setGraphSize] = useState({ width: 0, height: 500 });

  const graphContainerRef = useCallback((el: HTMLDivElement | null) => {
    graphObserverRef.current?.disconnect();
    graphObserverRef.current = null;
    if (!el) return;
    const updateSize = () => setGraphSize({ width: el.clientWidth, height: 500 });
    updateSize();
    const observer = new ResizeObserver(updateSize);
    observer.observe(el);
    graphObserverRef.current = observer;
  }, []);

  const runScenario = async () => {
    if (!jobId) return;
    setScenarioLoading(true);
    try {
      const res = await fetch(`/api/agents/research/${jobId}/scenario`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ scenario }),
      });
      setScenarioResult(await res.json());
    } catch {
      setScenarioResult(null);
    } finally {
      setScenarioLoading(false);
    }
  };

  const handleStart = () => startResearch(AGENTS.map((a) => a.name));

  return (
    <div className="space-y-8 max-w-5xl mx-auto">
      {error && (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}
          className="flex items-center gap-3 p-4 rounded-xl bg-red-500/10 border border-red-500/30 text-red-300 text-sm">
          <AlertCircle className="w-4 h-4 flex-shrink-0" />{error}
        </motion.div>
      )}

      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-white mb-1">
          New <span className="text-gradient">Research</span>
        </h1>
        <p className="text-white/50">Enter your startup idea and our AI agents will analyze the market</p>
      </div>

      <AnimatePresence mode="wait">
        {stage === 'input' && (
          <motion.div
            key="input"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="space-y-6"
          >
            {/* Idea Input */}
            <GlassCard>
              <GlassCardHeader>
                <div className="flex items-center gap-2">
                  <Sparkles className="w-5 h-5 text-indigo-400" />
                  <h2 className="text-lg font-semibold text-white">Describe Your Startup Idea</h2>
                </div>
              </GlassCardHeader>
              <GlassCardContent>
                <textarea
                  value={idea}
                  onChange={(e) => setIdea(e.target.value)}
                  placeholder="e.g. An AI platform that helps hospitals reduce patient wait times by automating triage and resource allocation..."
                  className="w-full h-36 px-4 py-3 rounded-xl bg-white/5 border border-white/10 text-white placeholder:text-white/30 focus:outline-none focus:border-indigo-500/60 resize-none text-sm leading-relaxed transition-colors"
                />
                <div className="mt-4">
                  <label className="text-sm text-white/60 mb-3 block">Select Industry</label>
                  <div className="flex flex-wrap gap-2">
                    {industries.map((ind) => (
                      <motion.button key={ind} whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}
                        onClick={() => setSelectedIndustry(ind === selectedIndustry ? '' : ind)}
                        className={`px-4 py-1.5 rounded-full text-sm font-medium border transition-all ${
                          selectedIndustry === ind
                            ? 'bg-indigo-500/30 border-indigo-500/60 text-indigo-300'
                            : 'bg-white/5 border-white/10 text-white/60 hover:text-white hover:border-white/30'
                        }`}>{ind}</motion.button>
                    ))}
                  </div>
                </div>
                <div className="mt-4 flex items-center gap-3">
                  <button onClick={() => setHealthcareMode(!healthcareMode)}
                    className={`w-10 h-5 rounded-full transition-colors relative flex-shrink-0 ${
                      healthcareMode ? 'bg-indigo-500' : 'bg-white/20'
                    }`}>
                    <motion.div
                      animate={{ x: healthcareMode ? 22 : 2 }}
                      transition={{ type: 'spring', stiffness: 400, damping: 25 }}
                      className="absolute top-0.5 w-4 h-4 rounded-full bg-white"
                    />
                  </button>
                  <span className="text-sm text-white/60">Healthcare Mode <span className="text-white/30">(FDA · clinical · payer analysis)</span></span>
                </div>
              </GlassCardContent>
            </GlassCard>

            {/* Agents Preview */}
            <GlassCard>
              <GlassCardHeader>
                <h2 className="text-lg font-semibold text-white">AI Agents That Will Run</h2>
              </GlassCardHeader>
              <GlassCardContent>
                <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-3">
                  {AGENTS.map((agent, i) => (
                    <motion.div key={agent.name} initial={{ opacity: 0, scale: 0.9 }}
                      animate={{ opacity: 1, scale: 1 }} transition={{ delay: i * 0.04 }}
                      className="flex items-center gap-3 p-3 rounded-xl bg-white/5 border border-white/10">
                      <div className={`w-9 h-9 rounded-lg bg-gradient-to-br ${agent.color} flex items-center justify-center flex-shrink-0`}>
                        <agent.icon className="w-4 h-4 text-white" />
                      </div>
                      <div>
                        <div className="text-xs font-medium text-white">{agent.name}</div>
                        <div className="text-xs text-white/40 flex items-center gap-1"><Clock className="w-3 h-3" />~1-2 min</div>
                      </div>
                    </motion.div>
                  ))}
                </div>
                <div className="mt-4 flex items-center justify-between">
                  <p className="text-sm text-white/40">Total estimated time: ~15 minutes</p>
                  <AnimatedButton size="md" onClick={handleStart} disabled={!idea.trim()}>
                    Start Research <ArrowRight className="w-4 h-4" />
                  </AnimatedButton>
                </div>
              </GlassCardContent>
            </GlassCard>
          </motion.div>
        )}

        {stage === 'running' && (
          <motion.div
            key="running"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="space-y-6"
          >
            <GlassCard>
              <GlassCardContent className="text-center py-8">
                <motion.div
                  className="w-20 h-20 mx-auto rounded-2xl bg-gradient-to-br from-indigo-500 via-purple-500 to-cyan-500 flex items-center justify-center mb-6 shadow-glow"
                  animate={{ rotate: [0, 360] }}
                  transition={{ duration: 3, repeat: Infinity, ease: 'linear' }}
                >
                  <Zap className="w-10 h-10 text-white" />
                </motion.div>
                <h2 className="text-2xl font-bold text-white mb-2">Analyzing Your Idea</h2>
                <p className="text-white/50 mb-2 max-w-md mx-auto text-sm">
                  Our AI agents are working together to generate comprehensive market intelligence.
                </p>
                {activeAgentName && (
                  <p className="text-indigo-300 text-sm mb-4">Running: <span className="font-semibold">{activeAgentName}</span></p>
                )}
                <div className="max-w-md mx-auto mb-6">
                  <div className="flex justify-between text-sm text-white/60 mb-2">
                    <span>Overall Progress</span>
                    <span>{progress}%</span>
                  </div>
                  <AnimatedProgress value={progress} variant="glow" />
                </div>
              </GlassCardContent>
            </GlassCard>

            <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
              {AGENTS.map((agent, i) => {
                const done = i < activeAgentIdx;
                const active = i === activeAgentIdx;
                return (
                  <motion.div
                    key={agent.name}
                    animate={active ? { scale: [1, 1.03, 1] } : {}}
                    transition={{ duration: 1.5, repeat: Infinity }}
                  >
                    <GlassCard className={active ? 'border-indigo-500/40' : ''}>
                      <GlassCardContent className="py-4">
                        <div className={`w-10 h-10 rounded-xl bg-gradient-to-br ${agent.color} flex items-center justify-center mb-3 ${active ? 'shadow-glow' : ''}`}>
                          <agent.icon className="w-5 h-5 text-white" />
                        </div>
                        <div className="text-sm font-medium text-white mb-2">{agent.name}</div>
                        <StatusBadge status={done ? 'completed' : active ? 'running' : 'pending'} />
                      </GlassCardContent>
                    </GlassCard>
                  </motion.div>
                );
              })}
            </div>
          </motion.div>
        )}

        {stage === 'done' && result && (
          <motion.div key="done" initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} className="space-y-6">
            {/* Hero */}
            <GlassCard className="border-emerald-500/30">
              <GlassCardContent className="text-center py-8">
                <motion.div className="w-20 h-20 mx-auto rounded-2xl bg-gradient-to-br from-emerald-500 to-teal-500 flex items-center justify-center mb-6"
                  initial={{ scale: 0 }} animate={{ scale: 1 }} transition={{ type: 'spring', stiffness: 300, damping: 20 }}>
                  <FileText className="w-10 h-10 text-white" />
                </motion.div>
                <h2 className="text-2xl font-bold text-white mb-2">Research Complete!</h2>
                <p className="text-white/50 mb-6 text-sm">
                  Your market intelligence report is ready.
                  {result?.innovation_score?.grade && <span> Innovation Grade: <span className="text-emerald-400 font-bold">{result.innovation_score.grade}</span></span>}
                </p>
                <div className="flex gap-3 justify-center flex-wrap">
                  {jobId && (
                    <a href={`/api/agents/research/${jobId}/report/pdf`} target="_blank" rel="noopener noreferrer">
                      <AnimatedButton size="md"><Download className="w-4 h-4" /> Download PDF</AnimatedButton>
                    </a>
                  )}
                  <AnimatedButton variant="secondary" size="md" onClick={resetForm}>
                    <RefreshCw className="w-4 h-4" /> New Research
                  </AnimatedButton>
                </div>
              </GlassCardContent>
            </GlassCard>
            {/* Score cards */}
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
              {[
                { label: 'Innovation Score', value: `${result?.innovation_score?.innovation_score ?? 0}/100`, color: 'text-indigo-400' },
                { label: 'Market Score',     value: `${result?.report?.market_score ?? 0}/100`,             color: 'text-emerald-400' },
                { label: 'Opportunity',      value: `${result?.report?.opportunity_score ?? 0}/100`,        color: 'text-purple-400' },
                { label: 'Competition',      value: (result?.report?.competition_level ?? 'medium').charAt(0).toUpperCase() + (result?.report?.competition_level ?? 'medium').slice(1), color: 'text-amber-400' },
              ].map((m, i) => (
                <motion.div key={m.label} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.1 }}>
                  <GlassCard><GlassCardContent className="text-center py-5">
                    <div className={`text-2xl font-bold ${m.color} mb-1`}>{m.value}</div>
                    <div className="text-xs text-white/50">{m.label}</div>
                  </GlassCardContent></GlassCard>
                </motion.div>
              ))}
            </div>
            {/* Executive Summary */}
            {result?.report?.executive_summary && (
              <GlassCard>
                <GlassCardHeader><div className="flex items-center gap-2"><Activity className="w-5 h-5 text-indigo-400" /><h3 className="text-base font-semibold text-white">Executive Summary</h3></div></GlassCardHeader>
                <GlassCardContent>
                  <p className="text-white/70 text-sm leading-relaxed">{result.report.executive_summary}</p>
                  {result?.innovation_score?.score_explanation && (
                    <p className="text-white/40 text-xs mt-3 pt-3 border-t border-white/10">{result.innovation_score.score_explanation}</p>
                  )}
                </GlassCardContent>
              </GlassCard>
            )}
            {/* Metrics + Recommendations */}
            <div className="grid md:grid-cols-2 gap-4">
              {result?.report?.key_metrics && Object.keys(result.report.key_metrics).length > 0 && (
                <GlassCard>
                  <GlassCardHeader><div className="flex items-center gap-2"><BarChart3 className="w-5 h-5 text-cyan-400" /><h3 className="text-base font-semibold text-white">Key Metrics</h3></div></GlassCardHeader>
                  <GlassCardContent>
                    <div className="space-y-3">
                      {Object.entries(result.report.key_metrics).map(([k, v]) => (
                        <div key={k} className="flex gap-4 text-sm border-b border-white/5 pb-2">
                          <span className="text-white/50 capitalize w-28 flex-shrink-0">{k.replace(/_/g, ' ')}</span>
                          <span className="text-white font-medium flex-1">{v as string}</span>
                        </div>
                      ))}
                    </div>
                  </GlassCardContent>
                </GlassCard>
              )}
              {(result?.report?.recommendations ?? []).length > 0 && (
                <GlassCard>
                  <GlassCardHeader><div className="flex items-center gap-2"><Lightbulb className="w-5 h-5 text-amber-400" /><h3 className="text-base font-semibold text-white">Recommendations</h3></div></GlassCardHeader>
                  <GlassCardContent>
                    <ul className="space-y-2">
                      {(result.report!.recommendations ?? []).map((rec, i) => (
                        <li key={i} className="flex items-start gap-2 text-sm text-white/70">
                          <span className="w-5 h-5 rounded-full bg-indigo-500/20 text-indigo-300 text-xs flex items-center justify-center flex-shrink-0 mt-0.5">{i + 1}</span>
                          {rec}
                        </li>
                      ))}
                    </ul>
                  </GlassCardContent>
                </GlassCard>
              )}
            </div>
            {/* Risk footer */}
            <div className="flex items-center gap-3 p-4 rounded-xl bg-white/5 border border-white/10">
              <ShieldAlert className="w-5 h-5 flex-shrink-0 text-amber-400" />
              <span className="text-sm text-white/60">Overall Risk Level: </span>
              <span className="text-sm font-semibold capitalize text-amber-400">{result?.risks?.overall_risk_level ?? 'medium'}</span>
            </div>

            {/* Knowledge Graph */}
            {result?.knowledge_graph?.nodes?.length ? (
              <GlassCard>
                <GlassCardHeader>
                  <div className="flex items-center gap-2">
                    <Compass className="w-5 h-5 text-violet-400" />
                    <h3 className="text-base font-semibold text-white">Knowledge Graph</h3>
                  </div>
                </GlassCardHeader>
                <GlassCardContent>
                  <div ref={graphContainerRef} style={{ height: 500, background: '#0f0f1a', borderRadius: 12, overflow: 'hidden' }}>
                    {graphSize.width > 0 && (
                      <ForceGraph2D
                        graphData={result.knowledge_graph}
                        width={graphSize.width}
                        height={graphSize.height}
                        nodeLabel="label"
                        nodeColor={(n: any) => NODE_COLORS[n.type] ?? '#94a3b8'}
                        nodeRelSize={6}
                        linkColor={() => '#334155'}
                        backgroundColor="#0f0f1a"
                      />
                    )}
                  </div>
                </GlassCardContent>
              </GlassCard>
            ) : null}

            {/* What-if Scenario Simulation */}
            <GlassCard>
              <GlassCardHeader>
                <div className="flex items-center gap-2">
                  <Sparkles className="w-5 h-5 text-indigo-400" />
                  <h3 className="text-base font-semibold text-white">What-if Scenario Simulation</h3>
                </div>
              </GlassCardHeader>
              <GlassCardContent className="space-y-4">
                <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-3">
                  <div>
                    <label className="text-xs text-white/50 mb-1 block">Pricing Strategy</label>
                    <select
                      value={scenario.pricing_strategy}
                      onChange={(e) => setScenario((s) => ({ ...s, pricing_strategy: e.target.value }))}
                      className="w-full px-3 py-2 rounded-lg bg-white/5 border border-white/10 text-white text-sm focus:outline-none focus:border-indigo-500/60"
                    >
                      <option value="subscription">Subscription</option>
                      <option value="freemium">Freemium</option>
                      <option value="one-time">One-time purchase</option>
                      <option value="usage-based">Usage-based</option>
                    </select>
                  </div>
                  {[
                    { key: 'target_market', label: 'Target Market' },
                    { key: 'geography', label: 'Geography' },
                    { key: 'technology_choice', label: 'Technology Choice' },
                    { key: 'team_size', label: 'Team Size' },
                    { key: 'funding_amount', label: 'Funding Amount' },
                  ].map((f) => (
                    <div key={f.key}>
                      <label className="text-xs text-white/50 mb-1 block">{f.label}</label>
                      <input
                        value={(scenario as any)[f.key]}
                        onChange={(e) => setScenario((s) => ({ ...s, [f.key]: e.target.value }))}
                        className="w-full px-3 py-2 rounded-lg bg-white/5 border border-white/10 text-white text-sm placeholder:text-white/25 focus:outline-none focus:border-indigo-500/60"
                        placeholder={f.label}
                      />
                    </div>
                  ))}
                </div>
                <AnimatedButton size="sm" onClick={runScenario} disabled={scenarioLoading}>
                  {scenarioLoading ? 'Simulating...' : 'Run Scenario'}
                </AnimatedButton>

                {scenarioResult && (
                  <div className="mt-4 p-4 rounded-xl bg-white/5 border border-white/10 space-y-3">
                    {scenarioResult.overall_recommendation && (
                      <p className="text-sm text-white/80">{scenarioResult.overall_recommendation}</p>
                    )}
                    {Array.isArray(scenarioResult.key_action_items) && scenarioResult.key_action_items.length > 0 && (
                      <ul className="space-y-1.5">
                        {scenarioResult.key_action_items.map((item: string, i: number) => (
                          <li key={i} className="flex items-start gap-2 text-sm text-white/60">
                            <span className="w-5 h-5 rounded-full bg-indigo-500/20 text-indigo-300 text-xs flex items-center justify-center flex-shrink-0 mt-0.5">{i + 1}</span>
                            {item}
                          </li>
                        ))}
                      </ul>
                    )}
                  </div>
                )}
              </GlassCardContent>
            </GlassCard>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
