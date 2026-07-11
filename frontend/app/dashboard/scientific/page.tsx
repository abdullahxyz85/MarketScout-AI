'use client';

import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import {
  FlaskConical, ScrollText, Shield, Lightbulb, ExternalLink,
  BookOpen, Award, AlertTriangle, CheckCircle2, BarChart3,
} from 'lucide-react';
import { GlassCard, GlassCardContent, GlassCardHeader } from '@/components/ui/glass-card';
import { AnimatedBadge } from '@/components/ui/animated-badge';
import { AnimatedProgress } from '@/components/ui/animated-progress';
import { EmptyResearchState } from '@/components/dashboard/empty-research-state';
import { loadLastResearch } from '@/lib/research-store';

// ── Types ──────────────────────────────────────────────────────────────────────
interface Paper {
  title?: string;
  authors?: string | string[];
  year?: string | number;
  journal?: string;
  url?: string;
  summary?: string;
  relevance?: string;
}

interface PatentItem {
  title?: string;
  holder?: string;
  number?: string;
  year?: string | number;
  relevance?: string;
  risk_level?: string;
}

// ── Helpers ───────────────────────────────────────────────────────────────────
function MaturityBadge({ maturity }: { maturity: string }) {
  const m = (maturity ?? '').toLowerCase();
  const cfg =
    m.includes('mature') ? { label: 'Mature', cls: 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30' } :
    m.includes('emerging') ? { label: 'Emerging', cls: 'bg-amber-500/20 text-amber-300 border-amber-500/30' } :
    m.includes('early') ? { label: 'Early Stage', cls: 'bg-indigo-500/20 text-indigo-300 border-indigo-500/30' } :
    { label: maturity || 'Unknown', cls: 'bg-white/10 text-white/50 border-white/20' };
  return (
    <span className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full border text-xs font-medium ${cfg.cls}`}>
      {cfg.label}
    </span>
  );
}

function RiskPill({ level }: { level: string }) {
  const l = (level ?? '').toLowerCase();
  const cls =
    l === 'high' ? 'bg-red-500/20 text-red-300 border-red-500/30' :
    l === 'medium' ? 'bg-amber-500/20 text-amber-300 border-amber-500/30' :
    'bg-emerald-500/20 text-emerald-300 border-emerald-500/30';
  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded-full border text-xs font-medium capitalize ${cls}`}>
      {l || 'low'} risk
    </span>
  );
}

// ── Page ───────────────────────────────────────────────────────────────────────
export default function ScientificPatentPage() {
  const [scientific, setScientific] = useState<any>(null);
  const [patents, setPatents] = useState<any>(null);
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    const stored = loadLastResearch();
    setScientific(stored?.result?.scientific ?? null);
    setPatents(stored?.result?.patents ?? null);
    setLoaded(true);
  }, []);

  if (!loaded) return null;

  if (!scientific && !patents) {
    return (
      <div className="space-y-8 max-w-7xl mx-auto">
        <Header />
        <EmptyResearchState
          title="No research yet"
          description="Run a market research analysis to see scientific papers, research maturity, and patent landscape here."
        />
      </div>
    );
  }

  const papers: Paper[] = scientific?.relevant_papers ?? [];
  const keyFindings: string[] = scientific?.key_findings ?? [];
  const maturity: string = scientific?.research_maturity ?? '';
  const scientificSummary: string = scientific?.summary ?? '';

  const patentItems: PatentItem[] = patents?.key_patents ?? [];
  const fto: string = patents?.freedom_to_operate ?? '';
  const ipLandscape: string = patents?.ip_landscape ?? '';
  const patentCount: number = patents?.patent_count ?? patentItems.length;
  const patentRisk: string = patents?.risk_level ?? 'low';

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      <Header />

      {/* KPI Row */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          { label: 'Papers Found', value: String(papers.length), icon: BookOpen, color: 'from-indigo-500 to-violet-500' },
          { label: 'Research Maturity', value: maturity || 'N/A', icon: BarChart3, color: 'from-emerald-500 to-teal-500' },
          { label: 'Patents Identified', value: String(patentCount), icon: Award, color: 'from-amber-500 to-orange-500' },
          { label: 'IP Risk', value: (patentRisk || 'low').charAt(0).toUpperCase() + (patentRisk || 'low').slice(1), icon: Shield, color: 'from-rose-500 to-pink-500' },
        ].map((kpi, i) => (
          <motion.div key={kpi.label} initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.07 }}>
            <GlassCard>
              <GlassCardContent className="py-5">
                <div className={`w-9 h-9 rounded-lg bg-gradient-to-br ${kpi.color} flex items-center justify-center mb-3`}>
                  <kpi.icon className="w-4 h-4 text-white" />
                </div>
                <div className="text-lg font-bold text-white truncate">{kpi.value}</div>
                <div className="text-xs text-white/45">{kpi.label}</div>
              </GlassCardContent>
            </GlassCard>
          </motion.div>
        ))}
      </div>

      {/* ── SCIENTIFIC SECTION ── */}
      {scientific && (
        <>
          {/* Summary + Maturity */}
          <GlassCard>
            <GlassCardHeader>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <FlaskConical className="w-5 h-5 text-indigo-400" />
                  <h2 className="text-base font-semibold text-white">Scientific Research Overview</h2>
                </div>
                {maturity && <MaturityBadge maturity={maturity} />}
              </div>
            </GlassCardHeader>
            <GlassCardContent className="space-y-4">
              {scientificSummary && (
                <p className="text-sm text-white/70 leading-relaxed">{scientificSummary}</p>
              )}
              {keyFindings.length > 0 && (
                <div>
                  <h3 className="text-xs font-semibold text-white/50 uppercase tracking-wider mb-3">Key Findings</h3>
                  <ul className="space-y-2">
                    {keyFindings.map((f, i) => (
                      <li key={i} className="flex items-start gap-2 text-sm text-white/70">
                        <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0 mt-0.5" />
                        {f}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </GlassCardContent>
          </GlassCard>

          {/* Relevant Papers */}
          {papers.length > 0 && (
            <GlassCard>
              <GlassCardHeader>
                <div className="flex items-center gap-2">
                  <ScrollText className="w-5 h-5 text-violet-400" />
                  <h2 className="text-base font-semibold text-white">Relevant Papers</h2>
                  <span className="ml-auto text-xs text-white/30">{papers.length} found</span>
                </div>
              </GlassCardHeader>
              <GlassCardContent>
                <div className="space-y-4">
                  {papers.map((p, i) => (
                    <motion.div
                      key={i}
                      initial={{ opacity: 0, x: -8 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: i * 0.04 }}
                      className="p-4 rounded-xl bg-white/5 border border-white/8 hover:border-indigo-500/30 transition-colors"
                    >
                      <div className="flex items-start justify-between gap-3 mb-2">
                        <h3 className="text-sm font-medium text-white leading-snug">{p.title ?? 'Untitled'}</h3>
                        {p.url && (
                          <a href={p.url} target="_blank" rel="noopener noreferrer"
                            className="p-1 rounded-lg hover:bg-white/10 text-white/40 hover:text-indigo-300 transition-colors flex-shrink-0">
                            <ExternalLink className="w-3.5 h-3.5" />
                          </a>
                        )}
                      </div>
                      <div className="flex flex-wrap gap-2 text-xs text-white/40 mb-2">
                        {p.authors && <span>{Array.isArray(p.authors) ? p.authors.join(', ') : p.authors}</span>}
                        {p.year && <span>· {p.year}</span>}
                        {p.journal && <span>· {p.journal}</span>}
                      </div>
                      {p.summary && <p className="text-xs text-white/55 leading-relaxed">{p.summary}</p>}
                      {p.relevance && (
                        <div className="mt-2 flex items-center gap-1.5 text-xs text-indigo-300">
                          <Lightbulb className="w-3 h-3" />
                          {p.relevance}
                        </div>
                      )}
                    </motion.div>
                  ))}
                </div>
              </GlassCardContent>
            </GlassCard>
          )}
        </>
      )}

      {/* ── PATENT SECTION ── */}
      {patents && (
        <>
          {/* IP Landscape */}
          <GlassCard>
            <GlassCardHeader>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Shield className="w-5 h-5 text-amber-400" />
                  <h2 className="text-base font-semibold text-white">Patent & IP Landscape</h2>
                </div>
                <RiskPill level={patentRisk} />
              </div>
            </GlassCardHeader>
            <GlassCardContent className="space-y-4">
              {ipLandscape && (
                <div>
                  <h3 className="text-xs font-semibold text-white/50 uppercase tracking-wider mb-2">IP Landscape</h3>
                  <p className="text-sm text-white/70 leading-relaxed">{ipLandscape}</p>
                </div>
              )}
              {fto && (
                <div className="p-4 rounded-xl bg-amber-500/5 border border-amber-500/20">
                  <h3 className="text-xs font-semibold text-amber-400 uppercase tracking-wider mb-1.5">Freedom to Operate</h3>
                  <p className="text-sm text-white/70 leading-relaxed">{fto}</p>
                </div>
              )}
            </GlassCardContent>
          </GlassCard>

          {/* Key Patents */}
          {patentItems.length > 0 && (
            <GlassCard>
              <GlassCardHeader>
                <div className="flex items-center gap-2">
                  <Award className="w-5 h-5 text-amber-400" />
                  <h2 className="text-base font-semibold text-white">Key Patents</h2>
                  <span className="ml-auto text-xs text-white/30">{patentCount} identified</span>
                </div>
              </GlassCardHeader>
              <GlassCardContent>
                <div className="space-y-3">
                  {patentItems.map((p, i) => (
                    <motion.div
                      key={i}
                      initial={{ opacity: 0, x: -8 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: i * 0.05 }}
                      className="flex items-start gap-4 p-4 rounded-xl bg-white/5 border border-white/8"
                    >
                      <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-amber-500 to-orange-500 flex items-center justify-center flex-shrink-0 text-xs font-bold text-white">
                        {i + 1}
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-start justify-between gap-2">
                          <h3 className="text-sm font-medium text-white">{p.title ?? 'Untitled Patent'}</h3>
                          {p.risk_level && <RiskPill level={p.risk_level} />}
                        </div>
                        <div className="flex flex-wrap gap-3 text-xs text-white/40 mt-1">
                          {p.holder && <span>Holder: {p.holder}</span>}
                          {p.number && <span>#{p.number}</span>}
                          {p.year && <span>{p.year}</span>}
                        </div>
                        {p.relevance && <p className="text-xs text-white/55 mt-1.5">{p.relevance}</p>}
                      </div>
                    </motion.div>
                  ))}
                </div>
              </GlassCardContent>
            </GlassCard>
          )}
        </>
      )}
    </div>
  );
}

function Header() {
  return (
    <div>
      <h1 className="text-2xl font-bold text-white mb-1">
        Scientific &amp; <span className="bg-gradient-to-r from-violet-400 to-indigo-400 bg-clip-text text-transparent">Patents</span>
      </h1>
      <p className="text-white/50 text-sm">Research papers, scientific maturity, and intellectual property landscape.</p>
    </div>
  );
}
