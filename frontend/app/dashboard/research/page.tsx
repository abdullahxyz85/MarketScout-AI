<<<<<<< HEAD
"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Search,
  Sparkles,
  ArrowRight,
  Zap,
  BarChart3,
  Users,
  TrendingUp,
  Target,
  ShieldAlert,
  FileText,
  Lightbulb,
  Clock,
  HeartPulse,
  ShieldCheck,
  Microscope,
} from "lucide-react";
import {
  GlassCard,
  GlassCardContent,
  GlassCardHeader,
} from "@/components/ui/glass-card";
import { AnimatedButton } from "@/components/ui/animated-button";
import { AnimatedBadge, StatusBadge } from "@/components/ui/animated-badge";
import { AnimatedProgress } from "@/components/ui/animated-progress";

const industries = [
  "Healthcare",
  "FinTech",
  "EdTech",
  "SaaS",
  "E-commerce",
  "AI/ML",
  "CleanTech",
  "Logistics",
];

const agents = [
  {
    name: "Research Agent",
    icon: Search,
    color: "from-indigo-500 to-purple-500",
    time: "~2 min",
  },
  {
    name: "Competitor Agent",
    icon: Users,
    color: "from-purple-500 to-pink-500",
    time: "~3 min",
  },
  {
    name: "Market Agent",
    icon: BarChart3,
    color: "from-cyan-500 to-blue-500",
    time: "~2 min",
  },
  {
    name: "Trend Agent",
    icon: TrendingUp,
    color: "from-emerald-500 to-teal-500",
    time: "~2 min",
  },
  {
    name: "SWOT Agent",
    icon: Target,
    color: "from-orange-500 to-red-500",
    time: "~1 min",
  },
  {
    name: "Opportunity Agent",
    icon: Lightbulb,
    color: "from-yellow-500 to-orange-500",
    time: "~2 min",
  },
  {
    name: "Risk Agent",
    icon: ShieldAlert,
    color: "from-red-500 to-rose-500",
    time: "~1 min",
  },
  {
    name: "Report Generator",
    icon: FileText,
    color: "from-indigo-500 to-blue-500",
    time: "~1 min",
  },
];

type Stage = "input" | "running" | "done";

export default function ResearchPage() {
  const [idea, setIdea] = useState("");
  const [selectedIndustry, setSelectedIndustry] = useState("");
  const [healthcareMode, setHealthcareMode] = useState(false);
  const [careFocus, setCareFocus] = useState("Clinical Workflow");
  const [stage, setStage] = useState<Stage>("input");
  const [activeAgent, setActiveAgent] = useState(0);
  const [progress, setProgress] = useState(0);

  const startResearch = () => {
    if (!idea.trim()) return;
    setStage("running");
    let agentIdx = 0;
    let pct = 0;

    const tick = setInterval(() => {
      pct += 2;
      setProgress(pct);
      if (pct % 14 === 0) {
        agentIdx = Math.min(agentIdx + 1, agents.length - 1);
        setActiveAgent(agentIdx);
      }
      if (pct >= 100) {
        clearInterval(tick);
        setStage("done");
      }
    }, 120);
  };

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
=======
'use client';

import { useEffect, useRef, useState } from 'react';
import dynamic from 'next/dynamic';
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
import { useResearch } from '@/lib/research-context';

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
  const graphContainerRef = useRef<HTMLDivElement>(null);
  const [graphSize, setGraphSize] = useState({ width: 0, height: 500 });

  useEffect(() => {
    const el = graphContainerRef.current;
    if (!el) return;
    const updateSize = () => setGraphSize({ width: el.clientWidth, height: 500 });
    updateSize();
    const observer = new ResizeObserver(updateSize);
    observer.observe(el);
    return () => observer.disconnect();
  }, [stage]);

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
    <div className="space-y-6 max-w-5xl mx-auto">
      {error && (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}
          className="flex items-center gap-3 p-4 rounded-xl bg-red-500/10 border border-red-500/30 text-red-300 text-sm">
          <AlertCircle className="w-4 h-4 flex-shrink-0" />{error}
        </motion.div>
      )}

>>>>>>> add-ai-agent-service
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-white mb-1">
          New <span className="text-gradient">Research</span>
        </h1>
<<<<<<< HEAD
        <p className="text-white/50">
          Enter your startup idea and our AI agents will analyze the market
        </p>
        {healthcareMode && (
          <div className="mt-3 inline-flex items-center gap-2 rounded-full border border-emerald-500/35 bg-emerald-500/15 px-3 py-1 text-xs text-emerald-300">
            <HeartPulse className="w-3.5 h-3.5" /> Healthcare Mode Active
          </div>
        )}
      </div>

      <AnimatePresence mode="wait">
        {stage === "input" && (
=======
        <p className="text-white/50">Enter your startup idea and our AI agents will analyze the market</p>
      </div>

      <AnimatePresence mode="wait">
        {stage === 'input' && (
>>>>>>> add-ai-agent-service
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
<<<<<<< HEAD
                  <h2 className="text-lg font-semibold text-white">
                    Describe Your Startup Idea
                  </h2>
=======
                  <h2 className="text-lg font-semibold text-white">Describe Your Startup Idea</h2>
>>>>>>> add-ai-agent-service
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
<<<<<<< HEAD
                  <label className="text-sm text-white/60 mb-3 block">
                    Select Industry
                  </label>
                  <div className="flex flex-wrap gap-2">
                    {industries.map((ind) => (
                      <motion.button
                        key={ind}
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                        onClick={() => setSelectedIndustry(ind)}
                        className={`px-4 py-1.5 rounded-full text-sm font-medium border transition-all ${
                          selectedIndustry === ind
                            ? "bg-indigo-500/30 border-indigo-500/60 text-indigo-300"
                            : "bg-white/5 border-white/10 text-white/60 hover:text-white hover:border-white/30"
                        }`}
                      >
                        {ind}
                      </motion.button>
                    ))}
                  </div>
                </div>

                <div className="mt-6 rounded-xl border border-emerald-500/25 bg-gradient-to-r from-emerald-500/12 to-cyan-500/10 p-4">
                  <div className="flex items-center justify-between gap-3">
                    <div>
                      <div className="flex items-center gap-2 text-white font-medium text-sm">
                        <HeartPulse className="w-4 h-4 text-emerald-300" />
                        Enable Healthcare Mode
                      </div>
                      <p className="text-xs text-white/60 mt-1">
                        Adds regulatory, clinical, and hospital-provider
                        analysis to the research pipeline.
                      </p>
                    </div>
                    <button
                      onClick={() => setHealthcareMode((prev) => !prev)}
                      className={`w-12 h-6 rounded-full border transition-all duration-300 relative ${healthcareMode ? "bg-emerald-500 border-emerald-500" : "bg-white/10 border-white/20"}`}
                    >
                      <motion.div
                        animate={{ x: healthcareMode ? 24 : 2 }}
                        transition={{
                          type: "spring",
                          stiffness: 400,
                          damping: 25,
                        }}
                        className="absolute top-0.5 w-5 h-5 rounded-full bg-white shadow"
                      />
                    </button>
                  </div>

                  {healthcareMode && (
                    <div className="mt-4 grid sm:grid-cols-2 gap-4">
                      <div>
                        <label className="text-xs text-white/60 mb-2 block">
                          Healthcare Focus
                        </label>
                        <div className="flex flex-wrap gap-2">
                          {[
                            "Clinical Workflow",
                            "Diagnostics",
                            "Digital Therapeutics",
                            "Hospital Ops",
                          ].map((focus) => (
                            <button
                              key={focus}
                              onClick={() => setCareFocus(focus)}
                              className={`px-3 py-1.5 rounded-full text-xs border transition-all ${careFocus === focus ? "bg-emerald-500/25 border-emerald-500/60 text-emerald-200" : "bg-white/6 border-white/15 text-white/65 hover:text-white"}`}
                            >
                              {focus}
                            </button>
                          ))}
                        </div>
                      </div>
                      <div className="space-y-2">
                        <div className="flex items-center gap-2 text-xs text-white/70">
                          <ShieldCheck className="w-3.5 h-3.5 text-emerald-300" />{" "}
                          HIPAA/Regulatory checks enabled
                        </div>
                        <div className="flex items-center gap-2 text-xs text-white/70">
                          <Microscope className="w-3.5 h-3.5 text-cyan-300" />{" "}
                          Clinical evidence signal scanning enabled
                        </div>
                      </div>
                    </div>
                  )}
=======
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
>>>>>>> add-ai-agent-service
                </div>
              </GlassCardContent>
            </GlassCard>

            {/* Agents Preview */}
            <GlassCard>
              <GlassCardHeader>
<<<<<<< HEAD
                <h2 className="text-lg font-semibold text-white">
                  AI Agents That Will Run
                </h2>
              </GlassCardHeader>
              <GlassCardContent>
                <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-3">
                  {agents.map((agent, i) => (
                    <motion.div
                      key={agent.name}
                      initial={{ opacity: 0, scale: 0.9 }}
                      animate={{ opacity: 1, scale: 1 }}
                      transition={{ delay: i * 0.05 }}
                      className="flex items-center gap-3 p-3 rounded-xl bg-white/5 border border-white/10"
                    >
                      <div
                        className={`w-9 h-9 rounded-lg bg-gradient-to-br ${agent.color} flex items-center justify-center flex-shrink-0`}
                      >
                        <agent.icon className="w-4 h-4 text-white" />
                      </div>
                      <div>
                        <div className="text-xs font-medium text-white">
                          {agent.name}
                        </div>
                        <div className="text-xs text-white/40 flex items-center gap-1">
                          <Clock className="w-3 h-3" />
                          {healthcareMode &&
                          (agent.name === "Trend Agent" ||
                            agent.name === "Risk Agent")
                            ? `${agent.time} + medical`
                            : agent.time}
                        </div>
=======
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
>>>>>>> add-ai-agent-service
                      </div>
                    </motion.div>
                  ))}
                </div>
                <div className="mt-4 flex items-center justify-between">
<<<<<<< HEAD
                  <p className="text-sm text-white/40">
                    Total estimated time: ~14 minutes
                  </p>
                  <AnimatedButton
                    size="md"
                    onClick={startResearch}
                    disabled={!idea.trim()}
                  >
=======
                  <p className="text-sm text-white/40">Total estimated time: ~15 minutes</p>
                  <AnimatedButton size="md" onClick={handleStart} disabled={!idea.trim()}>
>>>>>>> add-ai-agent-service
                    Start Research <ArrowRight className="w-4 h-4" />
                  </AnimatedButton>
                </div>
              </GlassCardContent>
            </GlassCard>
          </motion.div>
        )}

<<<<<<< HEAD
        {stage === "running" && (
=======
        {stage === 'running' && (
>>>>>>> add-ai-agent-service
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
<<<<<<< HEAD
                  transition={{ duration: 3, repeat: Infinity, ease: "linear" }}
                >
                  <Zap className="w-10 h-10 text-white" />
                </motion.div>
                <h2 className="text-2xl font-bold text-white mb-2">
                  Analyzing Your Idea
                </h2>
                <p className="text-white/50 mb-6 max-w-md mx-auto text-sm">
                  Our AI agents are working together to generate comprehensive
                  market intelligence.
                </p>
=======
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
>>>>>>> add-ai-agent-service
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
<<<<<<< HEAD
              {agents.map((agent, i) => {
                const done = i < activeAgent;
                const active = i === activeAgent;
=======
              {AGENTS.map((agent, i) => {
                const done = i < activeAgentIdx;
                const active = i === activeAgentIdx;
>>>>>>> add-ai-agent-service
                return (
                  <motion.div
                    key={agent.name}
                    animate={active ? { scale: [1, 1.03, 1] } : {}}
                    transition={{ duration: 1.5, repeat: Infinity }}
                  >
<<<<<<< HEAD
                    <GlassCard className={active ? "border-indigo-500/40" : ""}>
                      <GlassCardContent className="py-4">
                        <div
                          className={`w-10 h-10 rounded-xl bg-gradient-to-br ${agent.color} flex items-center justify-center mb-3 ${active ? "shadow-glow" : ""}`}
                        >
                          <agent.icon className="w-5 h-5 text-white" />
                        </div>
                        <div className="text-sm font-medium text-white mb-2">
                          {agent.name}
                        </div>
                        <StatusBadge
                          status={
                            done ? "completed" : active ? "running" : "pending"
                          }
                        />
=======
                    <GlassCard className={active ? 'border-indigo-500/40' : ''}>
                      <GlassCardContent className="py-4">
                        <div className={`w-10 h-10 rounded-xl bg-gradient-to-br ${agent.color} flex items-center justify-center mb-3 ${active ? 'shadow-glow' : ''}`}>
                          <agent.icon className="w-5 h-5 text-white" />
                        </div>
                        <div className="text-sm font-medium text-white mb-2">{agent.name}</div>
                        <StatusBadge status={done ? 'completed' : active ? 'running' : 'pending'} />
>>>>>>> add-ai-agent-service
                      </GlassCardContent>
                    </GlassCard>
                  </motion.div>
                );
              })}
            </div>
          </motion.div>
        )}

<<<<<<< HEAD
        {stage === "done" && (
          <motion.div
            key="done"
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="space-y-6"
          >
            <GlassCard className="border-emerald-500/30">
              <GlassCardContent className="text-center py-8">
                <motion.div
                  className="w-20 h-20 mx-auto rounded-2xl bg-gradient-to-br from-emerald-500 to-teal-500 flex items-center justify-center mb-6"
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  transition={{ type: "spring", stiffness: 300, damping: 20 }}
                >
                  <FileText className="w-10 h-10 text-white" />
                </motion.div>
                <h2 className="text-2xl font-bold text-white mb-2">
                  Research Complete!
                </h2>
                <p className="text-white/50 mb-6 text-sm">
                  Your market intelligence report is ready. Overall market
                  score:{" "}
                  <span className="text-emerald-400 font-bold">94.2</span>
                  {healthcareMode ? (
                    <span className="text-cyan-300">
                      {" "}
                      with healthcare regulatory insights.
                    </span>
                  ) : null}
                </p>
                <div className="flex gap-3 justify-center flex-wrap">
                  <AnimatedButton size="md">
                    <FileText className="w-4 h-4" /> View Report
                  </AnimatedButton>
                  <AnimatedButton
                    variant="secondary"
                    size="md"
                    onClick={() => {
                      setStage("input");
                      setIdea("");
                      setProgress(0);
                      setActiveAgent(0);
                    }}
                  >
                    Start New Research
=======
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
>>>>>>> add-ai-agent-service
                  </AnimatedButton>
                </div>
              </GlassCardContent>
            </GlassCard>
<<<<<<< HEAD

            <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
              {[
                {
                  label: "Market Score",
                  value: "94.2",
                  color: "text-emerald-400",
                },
                {
                  label: "Opportunity",
                  value: "87.8",
                  color: "text-indigo-400",
                },
                { label: "Competitors", value: "24", color: "text-purple-400" },
                { label: "Risk Level", value: "Low", color: "text-cyan-400" },
              ].map((m, i) => (
                <motion.div
                  key={m.label}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: i * 0.1 }}
                >
                  <GlassCard>
                    <GlassCardContent className="text-center py-4">
                      <div className={`text-3xl font-bold ${m.color} mb-1`}>
                        {m.value}
                      </div>
                      <div className="text-sm text-white/50">{m.label}</div>
                    </GlassCardContent>
                  </GlassCard>
                </motion.div>
              ))}
            </div>
=======
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
>>>>>>> add-ai-agent-service
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
