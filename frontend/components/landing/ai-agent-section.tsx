'use client';

import { motion } from 'framer-motion';
import {
  Search,
  Users,
  BarChart3,
  TrendingUp,
  Target,
  Lightbulb,
  ShieldAlert,
  FileText,
  Zap,
  Clock,
} from 'lucide-react';
import { GlassCard, GlassCardContent } from '@/components/ui/glass-card';
import { AnimatedProgress } from '@/components/ui/animated-progress';
import { StatusBadge } from '@/components/ui/animated-badge';

const agents = [
  {
    name: 'Research Agent',
    icon: Search,
    description: 'Gathers and synthesizes data from thousands of sources',
    status: 'running' as const,
    progress: 78,
    estimatedTime: '2 min left',
    color: 'from-indigo-500 to-purple-500',
  },
  {
    name: 'Competitor Agent',
    icon: Users,
    description: 'Analyzes competitor strategies and market positioning',
    status: 'running' as const,
    progress: 92,
    estimatedTime: '30 sec left',
    color: 'from-purple-500 to-pink-500',
  },
  {
    name: 'Market Agent',
    icon: BarChart3,
    description: 'Calculates market size and growth projections',
    status: 'completed' as const,
    progress: 100,
    estimatedTime: 'Completed',
    color: 'from-cyan-500 to-blue-500',
  },
  {
    name: 'Trend Agent',
    icon: TrendingUp,
    description: 'Identifies emerging trends and market shifts',
    status: 'running' as const,
    progress: 45,
    estimatedTime: '4 min left',
    color: 'from-emerald-500 to-teal-500 to-teal-500',
  },
  {
    name: 'SWOT Agent',
    icon: Target,
    description: 'Generates comprehensive SWOT analysis',
    status: 'pending' as const,
    progress: 0,
    estimatedTime: 'Waiting',
    color: 'from-orange-500 to-red-500',
  },
  {
    name: 'Opportunity Agent',
    icon: Lightbulb,
    description: 'Discovers hidden market opportunities',
    status: 'pending' as const,
    progress: 0,
    estimatedTime: 'Waiting',
    color: 'from-yellow-500 to-orange-500',
  },
  {
    name: 'Risk Agent',
    icon: ShieldAlert,
    description: 'Assesses potential risks and challenges',
    status: 'pending' as const,
    progress: 0,
    estimatedTime: 'Waiting',
    color: 'from-red-500 to-rose-500',
  },
  {
    name: 'Report Generator',
    icon: FileText,
    description: 'Compiles findings into a comprehensive report',
    status: 'pending' as const,
    progress: 0,
    estimatedTime: 'Waiting',
    color: 'from-indigo-500 to-blue-500',
  },
];

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { staggerChildren: 0.1 },
  },
};

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0 },
};

export function AIAgentSection() {
  return (
    <section className="py-24 relative">
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
            Specialized AI agents working together to deliver comprehensive market intelligence.
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
