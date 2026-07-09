import {
  Search, Users, BookOpen, Shield, DollarSign, TrendingUp, Lightbulb,
  Target, Star, ShieldAlert, BarChart3, CheckCircle, Compass, FileText,
  LucideIcon,
} from 'lucide-react';

/**
 * Single source of truth for the 14-agent pipeline, mirroring
 * agent-service/orchestrator/pipeline.py's AGENT_SEQUENCE (order matters).
 * `errorLabel` is the exact prefix each step uses when pushing a failure into
 * the result's `errors[]` array (see pipeline.py's `_run_step` calls) — it's
 * how a stored result's real per-agent status is derived after the fact.
 */
export interface AgentDef {
  name: string;
  errorLabel: string;
  icon: LucideIcon;
  color: string;
}

export const AGENT_SEQUENCE: AgentDef[] = [
  { name: 'Research Agent', errorLabel: 'ResearchAgent', icon: Search, color: 'from-indigo-500 to-purple-500' },
  { name: 'Competitor Agent', errorLabel: 'CompetitorAgent', icon: Users, color: 'from-purple-500 to-pink-500' },
  { name: 'Scientific Research Agent', errorLabel: 'ScientificAgent', icon: BookOpen, color: 'from-blue-500 to-cyan-500' },
  { name: 'Patent Intelligence Agent', errorLabel: 'PatentAgent', icon: Shield, color: 'from-amber-500 to-yellow-500' },
  { name: 'Funding Agent', errorLabel: 'FundingAgent', icon: DollarSign, color: 'from-green-500 to-emerald-500' },
  { name: 'Trend Agent', errorLabel: 'TrendAgent', icon: TrendingUp, color: 'from-emerald-500 to-teal-500' },
  { name: 'Research Gap Agent', errorLabel: 'ResearchGapAgent', icon: Lightbulb, color: 'from-yellow-500 to-orange-500' },
  { name: 'SWOT Agent', errorLabel: 'SWOTAgent', icon: Target, color: 'from-orange-500 to-red-500' },
  { name: 'Opportunity Agent', errorLabel: 'OpportunityAgent', icon: Star, color: 'from-violet-500 to-purple-500' },
  { name: 'Risk Agent', errorLabel: 'RiskAgent', icon: ShieldAlert, color: 'from-red-500 to-rose-500' },
  { name: 'Innovation Scoring Agent', errorLabel: 'InnovationScoringAgent', icon: BarChart3, color: 'from-cyan-500 to-blue-500' },
  { name: 'Validation Agent', errorLabel: 'ValidationAgent', icon: CheckCircle, color: 'from-teal-500 to-green-500' },
  { name: 'Strategy Agent', errorLabel: 'StrategyAgent', icon: Compass, color: 'from-indigo-500 to-violet-500' },
  { name: 'Report Generator', errorLabel: 'ReportAgent', icon: FileText, color: 'from-indigo-500 to-blue-500' },
];

export interface AgentStatus extends AgentDef {
  status: 'completed' | 'failed';
  progress: number;
}

/**
 * Derives real per-agent status from a completed research result: an agent
 * is 'failed' only if the result's errors[] recorded a failure for it,
 * otherwise it genuinely completed (the pipeline runs every step in order
 * and a saved result means the run reached the end).
 */
export function getAgentStatuses(result: { errors?: unknown } | null | undefined): AgentStatus[] {
  const errors = Array.isArray(result?.errors) ? (result!.errors as string[]) : [];
  return AGENT_SEQUENCE.map((agent) => {
    const failed = errors.some((e) => typeof e === 'string' && e.startsWith(`${agent.errorLabel}:`));
    return { ...agent, status: failed ? 'failed' : 'completed', progress: failed ? 0 : 100 };
  });
}
