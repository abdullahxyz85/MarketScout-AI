'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Search, Sparkles, ArrowRight, Zap, BarChart3, Users, TrendingUp,
  Target, ShieldAlert, FileText, Lightbulb, Clock, BookOpen, Shield,
  DollarSign, Star, CheckCircle, Compass, Activity, AlertCircle,
  Download, RefreshCw,
} from 'lucide-react';
import { GlassCard, GlassCardContent, GlassCardHeader } from '@/components/ui/glass-card';
import { AnimatedButton } from '@/components/ui/animated-button';
import { StatusBadge } from '@/components/ui/animated-badge';
import { AnimatedProgress } from '@/components/ui/animated-progress';
import { saveLastResearch } from '@/lib/research-store';

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

const AGENTS = [
  { name: 'Research Agent',            icon: Search,      color: 'from-indigo-500 to-purple-500' },
  { name: 'Competitor Agent',          icon: Users,       color: 'from-purple-500 to-pink-500' },
  { name: 'Scientific Research Agent', icon: BookOpen,    color: 'from-blue-500 to-cyan-500' },
  { name: 'Patent Intelligence Agent', icon: Shield,      color: 'from-amber-500 to-yellow-500' },
  { name: 'Funding Agent',             icon: DollarSign,  color: 'from-green-500 to-emerald-500' },
  { name: 'Trend Agent',               icon: TrendingUp,  color: 'from-emerald-500 to-teal-500' },
  { name: 'Research Gap Agent',        icon: Lightbulb,   color: 'from-yellow-500 to-orange-500' },
  { name: 'SWOT Agent',                icon: Target,      color: 'from-orange-500 to-red-500' },
  { name: 'Opportunity Agent',         icon: Star,        color: 'from-violet-500 to-purple-500' },
  { name: 'Risk Agent',                icon: ShieldAlert, color: 'from-red-500 to-rose-500' },
  { name: 'Innovation Scoring Agent',  icon: BarChart3,   color: 'from-cyan-500 to-blue-500' },
  { name: 'Validation Agent',          icon: CheckCircle, color: 'from-teal-500 to-green-500' },
  { name: 'Strategy Agent',            icon: Compass,     color: 'from-indigo-500 to-violet-500' },
  { name: 'Report Generator',          icon: FileText,    color: 'from-indigo-500 to-blue-500' },
];

type Stage = 'input' | 'running' | 'done';

interface ResearchResult {
  report?: {
    executive_summary?: string;
    market_score?: number;
    opportunity_score?: number;
    competition_level?: string;
    recommendations?: string[];
    key_metrics?: Record<string, string>;
  };
  innovation_score?: { innovation_score?: number; grade?: string; score_explanation?: string };
  risks?: { overall_risk_level?: string };
}

export default function ResearchPage() {
  const [idea, setIdea] = useState('');
  const [selectedIndustry, setSelectedIndustry] = useState('');
  const [healthcareMode, setHealthcareMode] = useState(false);
  const [stage, setStage] = useState<Stage>('input');
  const [activeAgentIdx, setActiveAgentIdx] = useState(0);
  const [activeAgentName, setActiveAgentName] = useState('');
  const [progress, setProgress] = useState(0);
  const [result, setResult] = useState<ResearchResult | null>(null);
  const [jobId, setJobId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const startResearch = async () => {
    if (!idea.trim()) return;
    setStage('running');
    setProgress(0);
    setActiveAgentIdx(0);
    setActiveAgentName('Research Agent');
    setError(null);
    try {
      const res = await fetch('/api/agents/research/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ idea, industry: selectedIndustry, healthcare_mode: healthcareMode }),
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error((err as any).detail ?? `HTTP ${res.status}`);
      }
      const { job_id } = await res.json();
      setJobId(job_id);
      const evtSource = new EventSource(`/api/agents/research/${job_id}/stream`);
      evtSource.onmessage = (e: MessageEvent) => {
        try {
          const data = JSON.parse(e.data);
          if (data.heartbeat) return;
          if (typeof data.progress === 'number' && data.progress >= 0) setProgress(data.progress);
          if (data.current_agent && data.current_agent !== 'Complete') {
            setActiveAgentName(data.current_agent);
            const idx = AGENTS.findIndex((a) => a.name === data.current_agent);
            if (idx !== -1) setActiveAgentIdx(idx);
          }
          if (data.done) {
            evtSource.close();
            if (data.error) { setError(data.error); setStage('input'); }
            else { const r: ResearchResult = data.result ?? {}; setResult(r); saveLastResearch(job_id, r); setStage('done'); }
          }
        } catch { /* ignore individual parse errors */ }
      };
      evtSource.onerror = () => { evtSource.close(); setError('Connection error. Please check the agent service and try again.'); setStage('input'); };
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      setStage('input');
    }
  };

  const resetForm = () => {
    setStage('input'); setIdea(''); setSelectedIndustry(''); setHealthcareMode(false);
    setProgress(0); setActiveAgentIdx(0); setResult(null); setError(null); setJobId(null);
  };

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
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
                    <span className={`absolute top-0.5 w-4 h-4 rounded-full bg-white transition-transform ${
                      healthcareMode ? 'translate-x-5' : 'translate-x-0.5'
                    }`} />
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
                  <AnimatedButton size="md" onClick={startResearch} disabled={!idea.trim()}>
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
                    <div className="space-y-2">
                      {Object.entries(result.report.key_metrics).map(([k, v]) => (
                        <div key={k} className="flex justify-between text-sm border-b border-white/5 pb-2">
                          <span className="text-white/50 capitalize">{k.replace(/_/g, ' ')}</span>
                          <span className="text-white font-medium">{v as string}</span>
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
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
