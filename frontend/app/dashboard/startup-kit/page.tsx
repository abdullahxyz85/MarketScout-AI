'use client';

import { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  FileText, TrendingUp, Layers, ChevronDown, ChevronUp,
  Target, Users, DollarSign, Rocket, Shield, BarChart3,
  Globe, Clock, Trophy, Lightbulb, Sparkles, Loader2,
  Check, X, Building2, ArrowRight,
} from 'lucide-react';
import { GlassCard, GlassCardContent, GlassCardHeader } from '@/components/ui/glass-card';
import { AnimatedButton } from '@/components/ui/animated-button';
import { AnimatedBadge } from '@/components/ui/animated-badge';
import { EmptyResearchState } from '@/components/dashboard/empty-research-state';
import { loadLastResearch } from '@/lib/research-store';
import { cn } from '@/lib/utils';

// ── Types ──────────────────────────────────────────────────────────────────────

interface BusinessPlan {
  _idea?: string; _industry?: string;
  executive_summary?: string; problem_statement?: string; solution?: string;
  value_proposition?: string; target_market?: string; product?: string;
  business_model?: string; go_to_market?: string; competitive_advantage?: string;
  competition?: string; team_requirements?: string; financial_projections?: string;
  milestones?: string; risks_and_mitigations?: string; success_metrics?: string;
}

interface InvestorMemo {
  _idea?: string; _industry?: string;
  verdict?: 'invest' | 'pass' | 'watch';
  verdict_rationale?: string; one_liner?: string; investment_thesis?: string;
  market_opportunity?: { tam?: string; sam?: string; som?: string };
  business_model?: string;
  traction_signals?: string[]; competitive_moat?: string; key_risks?: string[];
  why_now?: string;
  funding_ask?: { amount?: string; use_of_funds?: string[]; timeline?: string };
  exit_strategy?: string; red_flags?: string[]; green_flags?: string[];
}

interface Slide {
  number?: number; title?: string; headline?: string;
  content?: string[]; visual_suggestion?: string; speaker_notes?: string;
}

interface PitchDeck {
  _idea?: string; _industry?: string;
  deck_title?: string; tagline?: string; key_message?: string;
  slide_count?: number; slides?: Slide[];
}

type TabId = 'business-plan' | 'investor-memo' | 'pitch-deck';

interface TabDef {
  id: TabId;
  label: string;
  icon: React.ElementType;
  desc: string;
  endpoint: string;
}

const TABS: TabDef[] = [
  { id: 'business-plan', label: 'Business Plan', icon: FileText,   endpoint: 'business-plan',  desc: 'Comprehensive 15-section business plan generated from your research' },
  { id: 'investor-memo', label: 'Investor Memo',  icon: TrendingUp, endpoint: 'investor-memo',  desc: 'VC-style investment memo with verdict and market thesis' },
  { id: 'pitch-deck',    label: 'Pitch Deck',     icon: Layers,     endpoint: 'pitch-deck',     desc: '10-slide structured pitch deck with speaker notes' },
];

// ── Generate Prompt Card ───────────────────────────────────────────────────────

function GenerateCard({ tab, onGenerate, loading }: { tab: TabDef; onGenerate: () => void; loading: boolean }) {
  const Icon = tab.icon;
  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      className="flex flex-col items-center justify-center py-16 text-center"
    >
      <div className="w-16 h-16 rounded-2xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center mb-5">
        <Icon className="w-7 h-7 text-indigo-400" />
      </div>
      <h3 className="text-lg font-semibold text-white mb-2">Generate {tab.label}</h3>
      <p className="text-sm text-white/40 mb-7 max-w-sm leading-relaxed">{tab.desc}</p>
      <AnimatedButton onClick={onGenerate} disabled={loading} className="gap-2.5 px-6">
        {loading
          ? <><Loader2 className="w-4 h-4 animate-spin" /> Generating…</>
          : <><Sparkles className="w-4 h-4" /> Generate {tab.label}</>
        }
      </AnimatedButton>
    </motion.div>
  );
}

// ── Business Plan View ─────────────────────────────────────────────────────────

const BP_SECTIONS: { key: keyof BusinessPlan; label: string; Icon: React.ElementType }[] = [
  { key: 'executive_summary',     label: 'Executive Summary',     Icon: FileText },
  { key: 'problem_statement',     label: 'Problem Statement',     Icon: Target },
  { key: 'solution',              label: 'Solution',              Icon: Lightbulb },
  { key: 'value_proposition',     label: 'Value Proposition',     Icon: Sparkles },
  { key: 'target_market',         label: 'Target Market',         Icon: Users },
  { key: 'product',               label: 'Product',               Icon: Rocket },
  { key: 'business_model',        label: 'Business Model',        Icon: BarChart3 },
  { key: 'go_to_market',          label: 'Go-to-Market',          Icon: Globe },
  { key: 'competitive_advantage', label: 'Competitive Advantage', Icon: Trophy },
  { key: 'competition',           label: 'Competition Analysis',  Icon: Building2 },
  { key: 'team_requirements',     label: 'Team Requirements',     Icon: Users },
  { key: 'financial_projections', label: 'Financial Projections', Icon: DollarSign },
  { key: 'milestones',            label: 'Milestones',            Icon: Clock },
  { key: 'risks_and_mitigations', label: 'Risks & Mitigations',   Icon: Shield },
  { key: 'success_metrics',       label: 'Success Metrics',       Icon: Check },
];

function BusinessPlanView({ data }: { data: BusinessPlan }) {
  const [open, setOpen] = useState<Set<string>>(new Set(['executive_summary']));
  const toggle = (key: string) =>
    setOpen(prev => { const n = new Set(prev); n.has(key) ? n.delete(key) : n.add(key); return n; });

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-1.5">
      {BP_SECTIONS.map(({ key, label, Icon }) => {
        const text = data[key];
        if (!text) return null;
        const isOpen = open.has(key);
        return (
          <div key={key} className="rounded-xl border border-white/[0.06] overflow-hidden">
            <button
              onClick={() => toggle(key)}
              className="w-full flex items-center gap-3 px-4 py-3 hover:bg-white/[0.04] transition-colors text-left"
            >
              <div className="w-7 h-7 rounded-lg bg-indigo-500/10 flex items-center justify-center flex-shrink-0">
                <Icon className="w-3.5 h-3.5 text-indigo-400" />
              </div>
              <span className="text-sm font-medium text-white flex-1">{label}</span>
              {isOpen
                ? <ChevronUp className="w-4 h-4 text-white/30 flex-shrink-0" />
                : <ChevronDown className="w-4 h-4 text-white/30 flex-shrink-0" />}
            </button>
            <AnimatePresence initial={false}>
              {isOpen && (
                <motion.div
                  initial={{ height: 0, opacity: 0 }}
                  animate={{ height: 'auto', opacity: 1 }}
                  exit={{ height: 0, opacity: 0 }}
                  transition={{ duration: 0.2 }}
                  className="overflow-hidden"
                >
                  <div className="px-4 pb-4 pt-1 text-sm text-white/65 leading-relaxed border-t border-white/[0.04]">
                    {text}
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        );
      })}
    </motion.div>
  );
}

// ── Investor Memo View ─────────────────────────────────────────────────────────

const VERDICT_CONFIG = {
  invest: { label: 'Invest',       emoji: '✅', color: 'text-emerald-400', border: 'border-emerald-500/30', bg: 'bg-emerald-500/8'  },
  watch:  { label: 'Watch',        emoji: '👀', color: 'text-yellow-400',  border: 'border-yellow-500/30',  bg: 'bg-yellow-500/8'   },
  pass:   { label: 'Pass',         emoji: '❌', color: 'text-red-400',     border: 'border-red-500/30',     bg: 'bg-red-500/8'      },
} as const;

function InvestorMemoView({ data }: { data: InvestorMemo }) {
  const v = data.verdict && data.verdict in VERDICT_CONFIG ? data.verdict : 'watch';
  const vc = VERDICT_CONFIG[v as keyof typeof VERDICT_CONFIG];

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-4">
      {/* Verdict Banner */}
      <div className={cn('rounded-xl border p-5', vc.border, vc.bg)}>
        <div className="flex flex-wrap items-start gap-4">
          <div>
            <p className="text-[10px] text-white/40 uppercase tracking-widest mb-1.5">Verdict</p>
            <p className={cn('text-3xl font-bold tracking-tight', vc.color)}>
              {vc.emoji} {vc.label}
            </p>
          </div>
          {data.one_liner && (
            <p className="text-sm text-white/60 italic border-l border-white/10 pl-4 flex-1 leading-relaxed">
              "{data.one_liner}"
            </p>
          )}
        </div>
        {data.verdict_rationale && (
          <p className="mt-3 text-sm text-white/55 border-t border-white/[0.08] pt-3 leading-relaxed">
            {data.verdict_rationale}
          </p>
        )}
      </div>

      {/* Metrics row */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
        {data.market_opportunity && (
          <GlassCard>
            <GlassCardHeader>
              <span className="text-xs font-semibold text-white/50 uppercase tracking-wide">Market Opportunity</span>
            </GlassCardHeader>
            <GlassCardContent className="space-y-2 pt-2">
              {(['tam', 'sam', 'som'] as const).map(k => data.market_opportunity?.[k] && (
                <div key={k}>
                  <span className="text-[10px] text-white/35 uppercase tracking-wider">{k}</span>
                  <p className="text-sm font-semibold text-white leading-tight">{data.market_opportunity[k]}</p>
                </div>
              ))}
            </GlassCardContent>
          </GlassCard>
        )}
        {data.funding_ask && (
          <GlassCard>
            <GlassCardHeader>
              <span className="text-xs font-semibold text-white/50 uppercase tracking-wide">Funding Ask</span>
            </GlassCardHeader>
            <GlassCardContent className="pt-2">
              {data.funding_ask.amount && (
                <p className="text-xl font-bold text-indigo-400 mb-1">{data.funding_ask.amount}</p>
              )}
              {data.funding_ask.timeline && (
                <p className="text-xs text-white/40 mb-2">{data.funding_ask.timeline}</p>
              )}
              {(data.funding_ask.use_of_funds || []).slice(0, 3).map((u, i) => (
                <p key={i} className="text-xs text-white/55 flex gap-1.5"><ArrowRight className="w-3 h-3 text-indigo-400 mt-0.5 flex-shrink-0" />{u}</p>
              ))}
            </GlassCardContent>
          </GlassCard>
        )}
        {(data.traction_signals || []).length > 0 && (
          <GlassCard>
            <GlassCardHeader>
              <span className="text-xs font-semibold text-white/50 uppercase tracking-wide">Traction Signals</span>
            </GlassCardHeader>
            <GlassCardContent className="pt-2 space-y-1">
              {(data.traction_signals || []).slice(0, 4).map((s, i) => (
                <p key={i} className="text-xs text-white/55 flex gap-1.5">
                  <Check className="w-3 h-3 text-emerald-400 mt-0.5 flex-shrink-0" />{s}
                </p>
              ))}
            </GlassCardContent>
          </GlassCard>
        )}
      </div>

      {/* Thesis + Moat */}
      {(data.investment_thesis || data.competitive_moat) && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {data.investment_thesis && (
            <GlassCard>
              <GlassCardHeader><span className="text-sm font-medium text-white">Investment Thesis</span></GlassCardHeader>
              <GlassCardContent><p className="text-sm text-white/60 leading-relaxed">{data.investment_thesis}</p></GlassCardContent>
            </GlassCard>
          )}
          {data.competitive_moat && (
            <GlassCard>
              <GlassCardHeader><span className="text-sm font-medium text-white">Competitive Moat</span></GlassCardHeader>
              <GlassCardContent><p className="text-sm text-white/60 leading-relaxed">{data.competitive_moat}</p></GlassCardContent>
            </GlassCard>
          )}
        </div>
      )}

      {/* Green / Red Flags */}
      {((data.green_flags || []).length > 0 || (data.red_flags || []).length > 0) && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {(data.green_flags || []).length > 0 && (
            <div className="rounded-xl border border-emerald-500/20 bg-emerald-500/5 p-4">
              <h4 className="text-sm font-semibold text-emerald-400 mb-3 flex items-center gap-2">
                <Check className="w-4 h-4" /> Green Flags
              </h4>
              <ul className="space-y-1.5">
                {(data.green_flags || []).map((f, i) => (
                  <li key={i} className="text-xs text-white/60 flex gap-2 leading-relaxed">
                    <span className="text-emerald-400 mt-0.5 flex-shrink-0">✓</span>{f}
                  </li>
                ))}
              </ul>
            </div>
          )}
          {(data.red_flags || []).length > 0 && (
            <div className="rounded-xl border border-red-500/20 bg-red-500/5 p-4">
              <h4 className="text-sm font-semibold text-red-400 mb-3 flex items-center gap-2">
                <X className="w-4 h-4" /> Red Flags
              </h4>
              <ul className="space-y-1.5">
                {(data.red_flags || []).map((f, i) => (
                  <li key={i} className="text-xs text-white/60 flex gap-2 leading-relaxed">
                    <span className="text-red-400 mt-0.5 flex-shrink-0">✕</span>{f}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {/* Why Now + Exit */}
      {(data.why_now || data.exit_strategy) && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {data.why_now && (
            <GlassCard>
              <GlassCardHeader><span className="text-sm font-medium text-white">Why Now?</span></GlassCardHeader>
              <GlassCardContent><p className="text-sm text-white/60 leading-relaxed">{data.why_now}</p></GlassCardContent>
            </GlassCard>
          )}
          {data.exit_strategy && (
            <GlassCard>
              <GlassCardHeader><span className="text-sm font-medium text-white">Exit Strategy</span></GlassCardHeader>
              <GlassCardContent><p className="text-sm text-white/60 leading-relaxed">{data.exit_strategy}</p></GlassCardContent>
            </GlassCard>
          )}
        </div>
      )}

      {/* Key Risks */}
      {(data.key_risks || []).length > 0 && (
        <GlassCard>
          <GlassCardHeader><span className="text-sm font-medium text-white">Key Risks</span></GlassCardHeader>
          <GlassCardContent>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
              {(data.key_risks || []).map((r, i) => (
                <div key={i} className="flex gap-2 text-xs text-white/55 leading-relaxed">
                  <span className="text-yellow-400 mt-0.5 flex-shrink-0">⚠</span>{r}
                </div>
              ))}
            </div>
          </GlassCardContent>
        </GlassCard>
      )}
    </motion.div>
  );
}

// ── Pitch Deck View ────────────────────────────────────────────────────────────

const SLIDE_GRADIENTS = [
  'from-indigo-500/15 to-purple-500/15 border-indigo-500/25',
  'from-purple-500/15 to-pink-500/15 border-purple-500/25',
  'from-cyan-500/15 to-blue-500/15 border-cyan-500/25',
  'from-emerald-500/15 to-teal-500/15 border-emerald-500/25',
  'from-orange-500/15 to-amber-500/15 border-orange-500/25',
  'from-blue-500/15 to-indigo-500/15 border-blue-500/25',
  'from-pink-500/15 to-rose-500/15 border-pink-500/25',
  'from-teal-500/15 to-cyan-500/15 border-teal-500/25',
  'from-violet-500/15 to-indigo-500/15 border-violet-500/25',
  'from-amber-500/15 to-orange-500/15 border-amber-500/25',
];

function PitchDeckView({ data }: { data: PitchDeck }) {
  const [expanded, setExpanded] = useState<number | null>(null);

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-5">
      {/* Deck header */}
      <div className="text-center space-y-1 pb-1">
        <h3 className="text-xl font-bold text-white">{data.deck_title || 'Pitch Deck'}</h3>
        {data.tagline && <p className="text-sm text-indigo-300">{data.tagline}</p>}
        {data.key_message && (
          <p className="text-xs text-white/40 max-w-lg mx-auto leading-relaxed pt-1">{data.key_message}</p>
        )}
      </div>

      {/* Slide grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        {(data.slides || []).map((slide, i) => {
          const grad = SLIDE_GRADIENTS[i % SLIDE_GRADIENTS.length];
          const isOpen = expanded === i;
          return (
            <motion.div
              key={i}
              onClick={() => setExpanded(isOpen ? null : i)}
              whileHover={{ scale: 1.01 }}
              className={cn(
                'rounded-xl border bg-gradient-to-br p-4 cursor-pointer transition-shadow',
                grad,
                isOpen ? 'ring-1 ring-indigo-500/40' : '',
              )}
            >
              {/* Slide number + title */}
              <div className="flex items-center gap-2.5 mb-2.5">
                <span className="w-6 h-6 rounded-full bg-white/10 text-[10px] font-bold text-white/50 flex items-center justify-center flex-shrink-0">
                  {slide.number || i + 1}
                </span>
                <span className="text-[10px] font-semibold text-white/50 uppercase tracking-widest">
                  {slide.title}
                </span>
              </div>
              {slide.headline && (
                <p className="text-sm font-semibold text-white mb-2 leading-snug">{slide.headline}</p>
              )}
              <ul className="space-y-1">
                {(slide.content || []).slice(0, isOpen ? undefined : 3).map((c, j) => (
                  <li key={j} className="text-xs text-white/55 flex gap-1.5 leading-relaxed">
                    <span className="text-white/25 flex-shrink-0 mt-0.5">•</span>{c}
                  </li>
                ))}
                {!isOpen && (slide.content || []).length > 3 && (
                  <li className="text-[10px] text-white/30 mt-1">+ {(slide.content || []).length - 3} more · click to expand</li>
                )}
              </ul>
              <AnimatePresence>
                {isOpen && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: 'auto' }}
                    exit={{ opacity: 0, height: 0 }}
                    className="overflow-hidden"
                  >
                    {slide.visual_suggestion && (
                      <p className="mt-3 text-[11px] text-cyan-400/70 flex gap-1.5 items-start border-t border-white/[0.06] pt-2.5">
                        <span>🎨</span>{slide.visual_suggestion}
                      </p>
                    )}
                    {slide.speaker_notes && (
                      <p className="mt-2 text-[11px] text-white/35 flex gap-1.5 items-start italic">
                        <span>📝</span>{slide.speaker_notes}
                      </p>
                    )}
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.div>
          );
        })}
      </div>
    </motion.div>
  );
}

// ── Main Page ──────────────────────────────────────────────────────────────────

type DataStore = { 'business-plan': BusinessPlan | null; 'investor-memo': InvestorMemo | null; 'pitch-deck': PitchDeck | null };
type FlagStore = Record<TabId, boolean>;

export default function StartupKitPage() {
  const [jobId, setJobId]     = useState('');
  const [idea, setIdea]       = useState('');
  const [industry, setIndustry] = useState('');
  const [activeTab, setActiveTab] = useState<TabId>('business-plan');
  const [data, setData]   = useState<DataStore>({ 'business-plan': null, 'investor-memo': null, 'pitch-deck': null });
  const [loading, setLoading] = useState<FlagStore>({ 'business-plan': false, 'investor-memo': false, 'pitch-deck': false });
  const [errors,  setErrors]  = useState<Record<TabId, string | null>>({ 'business-plan': null, 'investor-memo': null, 'pitch-deck': null });
  const [checked, setChecked] = useState(false);

  useEffect(() => {
    const stored = loadLastResearch();
    if (stored?.jobId) {
      setJobId(stored.jobId);
      setIdea((stored.result as any)?.idea || (stored.result as any)?._idea || '');
      setIndustry((stored.result as any)?.industry || (stored.result as any)?._industry || '');
    }
    setChecked(true);
  }, []);

  if (!checked) return null;

  if (!jobId) {
    return (
      <div className="space-y-8 max-w-7xl mx-auto">
        <div>
          <h1 className="text-2xl font-bold text-white mb-1">
            Startup <span className="bg-gradient-to-r from-indigo-400 to-purple-400 bg-clip-text text-transparent">Kit</span>
          </h1>
        </div>
        <EmptyResearchState title="No Research Found" description="Run a market research first to generate your Startup Kit." />
      </div>
    );
  }

  const generate = async (tab: TabId) => {
    setLoading(l => ({ ...l, [tab]: true }));
    setErrors(e => ({ ...e, [tab]: null }));
    try {
      const res = await fetch(`/api/agents/research/${jobId}/${tab}`);
      if (!res.ok) {
        const body = await res.json().catch(() => ({}));
        throw new Error(body.detail || `HTTP ${res.status}`);
      }
      const json = await res.json();
      setData(d => ({ ...d, [tab]: json }));
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Generation failed';
      setErrors(e => ({ ...e, [tab]: msg }));
    } finally {
      setLoading(l => ({ ...l, [tab]: false }));
    }
  };

  const currentData = data[activeTab];
  const currentTab  = TABS.find(t => t.id === activeTab)!;

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      {/* Header */}
      <motion.div initial={{ opacity: 0, y: -8 }} animate={{ opacity: 1, y: 0 }}>
        <h1 className="text-2xl font-bold text-white">
          Startup{' '}
          <span className="bg-gradient-to-r from-indigo-400 to-purple-400 bg-clip-text text-transparent">Kit</span>
        </h1>
        <p className="text-sm text-white/40 mt-1">
          AI-generated business assets from your market research
          {idea ? ` · "${idea}"` : ''}
          {industry ? ` · ${industry}` : ''}
        </p>
      </motion.div>

      {/* Tab bar */}
      <div className="flex gap-1 p-1 rounded-xl bg-white/[0.03] border border-white/[0.06] w-fit flex-wrap">
        {TABS.map(tab => {
          const Icon = tab.icon;
          const active = activeTab === tab.id;
          const done   = !!data[tab.id];
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={cn(
                'flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all relative',
                active ? 'bg-indigo-500/20 text-white border border-indigo-500/30' : 'text-white/45 hover:text-white hover:bg-white/[0.05]',
              )}
            >
              <Icon className="w-4 h-4" />
              {tab.label}
              {done && <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 absolute top-1.5 right-1.5" />}
            </button>
          );
        })}
      </div>

      {/* Card area */}
      <GlassCard>
        <GlassCardContent className="p-6 min-h-[420px]">
          <AnimatePresence mode="wait">
            <motion.div
              key={activeTab}
              initial={{ opacity: 0, x: 8 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -8 }}
              transition={{ duration: 0.15 }}
            >
              {/* Error banner */}
              {errors[activeTab] && (
                <div className="mb-5 p-3 rounded-lg bg-red-500/10 border border-red-500/20 text-sm text-red-300">
                  {errors[activeTab]}
                </div>
              )}

              {!currentData ? (
                <GenerateCard tab={currentTab} onGenerate={() => generate(activeTab)} loading={loading[activeTab]} />
              ) : activeTab === 'business-plan' ? (
                <BusinessPlanView data={currentData as BusinessPlan} />
              ) : activeTab === 'investor-memo' ? (
                <InvestorMemoView data={currentData as InvestorMemo} />
              ) : (
                <PitchDeckView data={currentData as PitchDeck} />
              )}
            </motion.div>
          </AnimatePresence>
        </GlassCardContent>
      </GlassCard>
    </div>
  );
}
