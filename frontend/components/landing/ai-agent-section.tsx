'use client';

import { motion } from 'framer-motion';
import { Clock } from 'lucide-react';
import { GlassCard, GlassCardContent } from '@/components/ui/glass-card';
import { AnimatedProgress } from '@/components/ui/animated-progress';
import { StatusBadge } from '@/components/ui/animated-badge';
import { AGENT_SEQUENCE } from '@/lib/agents';

const DESCRIPTIONS: Record<string, string> = {
  'Research Agent': 'Gathers and synthesizes market data from thousands of sources',
  'Competitor Agent': 'Identifies and profiles key competitors and their market share',
  'Scientific Research Agent': 'Surveys academic research and assesses scientific maturity',
  'Patent Intelligence Agent': 'Maps the patent landscape and freedom-to-operate risks',
  'Funding Agent': 'Tracks funding rounds and investor activity in the space',
  'Trend Agent': 'Detects emerging trends, tech shifts, and regulatory changes',
  'Research Gap Agent': 'Surfaces unexplored opportunities and market blind spots',
  'SWOT Agent': 'Builds a complete strengths, weaknesses, opportunities & threats analysis',
  'Opportunity Agent': 'Scores market gaps and addressable customer segments',
  'Risk Agent': 'Evaluates business, technical, and regulatory risks',
  'Innovation Scoring Agent': 'Computes a composite innovation score from every signal',
  'Validation Agent': "Stress-tests assumptions like a critical devil's advocate",
  'Strategy Agent': 'Crafts a go-to-market and competitive strategy',
  'Report Generator': 'Compiles every finding into one intelligence report',
};

const agents = AGENT_SEQUENCE.map((agent, i) => {
  const status = i < 6 ? ('completed' as const) : i === 6 ? ('running' as const) : ('pending' as const);
  const progress = status === 'completed' ? 100 : status === 'running' ? 55 : 0;
  const estimatedTime = status === 'completed' ? 'Completed' : status === 'running' ? '1 min left' : 'Waiting';
  return {
    name: agent.name,
    icon: agent.icon,
    color: agent.color,
    description: DESCRIPTIONS[agent.name] ?? '',
    status,
    progress,
    estimatedTime,
  };
});

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { staggerChildren: 0.06 },
  },
};

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0 },
};

export function AIAgentSection() {
  return (
    <section id="agents" className="py-24 relative">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-16"
        >
          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-white mb-4">
            Meet Your <span className="text-gradient">AI Agents</span>
          </h2>
          <p className="text-lg text-white/60 max-w-2xl mx-auto">
            14 specialized AI agents working together to deliver comprehensive market intelligence.
          </p>
        </motion.div>

        <motion.div
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          className="grid md:grid-cols-2 lg:grid-cols-4 gap-6"
        >
          {agents.map((agent) => (
            <motion.div key={agent.name} variants={itemVariants}>
              <GlassCard className="h-full">
                <GlassCardContent>
                  <div className="flex items-start justify-between mb-4">
                    <motion.div
                      className={`w-12 h-12 rounded-xl bg-gradient-to-br ${agent.color} flex items-center justify-center shadow-lg`}
                      animate={
                        agent.status === 'running'
                          ? {
                              boxShadow: [
                                '0 0 20px rgba(99, 102, 241, 0.3)',
                                '0 0 30px rgba(99, 102, 241, 0.5)',
                                '0 0 20px rgba(99, 102, 241, 0.3)',
                              ],
                            }
                          : undefined
                      }
                      transition={{ duration: 2, repeat: Infinity }}
                    >
                      <agent.icon className="w-6 h-6 text-white" />
                    </motion.div>
                    <StatusBadge status={agent.status} />
                  </div>

                  <h3 className="text-lg font-semibold text-white mb-2">{agent.name}</h3>
                  <p className="text-sm text-white/60 mb-4 leading-relaxed">{agent.description}</p>

                  <div className="space-y-2">
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-white/50">Progress</span>
                      <span className="text-white font-medium">{agent.progress}%</span>
                    </div>
                    <AnimatedProgress value={agent.progress} />
                    <div className="flex items-center gap-1 text-xs text-white/40">
                      <Clock className="w-3 h-3" />
                      {agent.estimatedTime}
                    </div>
                  </div>
                </GlassCardContent>
              </GlassCard>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  );
}
