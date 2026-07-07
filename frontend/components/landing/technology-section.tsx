'use client';

import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';

const technologies = [
  { name: 'AMD Cloud', category: 'Infrastructure' },
  { name: 'Fireworks AI', category: 'AI Inference' },
  { name: 'Llama', category: 'LLM' },
  { name: 'Qwen', category: 'LLM' },
  { name: 'Next.js', category: 'Frontend' },
  { name: 'Tailwind', category: 'Styling' },
  { name: 'LangGraph', category: 'Agent Framework' },
  { name: 'Supabase', category: 'Backend' },
  { name: 'Python', category: 'Language' },
  { name: 'FastAPI', category: 'Backend' },
  { name: 'Tavily', category: 'Search API' },
  { name: 'Vector DB', category: 'Storage' },
];

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { staggerChildren: 0.05 },
  },
};

const itemVariants = {
  hidden: { opacity: 0, scale: 0.9 },
  visible: { opacity: 1, scale: 1 },
};

export function TechnologySection() {
  return (
    <section id="technology" className="py-24 relative">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-16"
        >
          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-white mb-4">
            Built on <span className="text-gradient">Cutting-Edge</span> Technology
          </h2>
          <p className="text-lg text-white/60 max-w-2xl mx-auto">
            We leverage the best AI infrastructure and modern development tools to deliver
            unparalleled market intelligence.
          </p>
        </motion.div>

        <motion.div
          variants={containerVariants}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-4"
        >
          {technologies.map((tech) => (
            <motion.div
              key={tech.name}
              variants={itemVariants}
              whileHover={{ y: -4, scale: 1.02 }}
              className="group relative"
            >
              <div className="p-4 rounded-xl bg-gradient-to-br from-white/[0.08] to-white/[0.02] border border-white/10 hover:border-white/20 transition-all duration-300 backdrop-blur-xl h-full">
                <div className="absolute inset-0 rounded-xl bg-gradient-to-br from-indigo-500/5 to-purple-500/5 opacity-0 group-hover:opacity-100 transition-opacity" />

                <div className="relative">
                  <div className="w-12 h-12 mx-auto mb-3 rounded-xl bg-gradient-to-br from-white/10 to-white/5 flex items-center justify-center border border-white/10">
                    <div className="w-6 h-6 rounded bg-gradient-to-br from-indigo-500 to-purple-500" />
                  </div>
                  <div className="text-center">
                    <div className="text-sm font-semibold text-white mb-1">{tech.name}</div>
                    <div className="text-xs text-white/40">{tech.category}</div>
                  </div>
                </div>
              </div>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  );
}

const timelineSteps = [
  { name: 'Research', description: 'Gather market data' },
  { name: 'Analysis', description: 'Process and categorize' },
  { name: 'AI Processing', description: 'Generate insights' },
  { name: 'Report Generation', description: 'Compile report' },
  { name: 'Visualization', description: 'Create dashboards' },
];

export function TimelineSection() {
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
            From Idea to <span className="text-gradient">Intelligence</span> in Minutes
          </h2>
          <p className="text-lg text-white/60 max-w-2xl mx-auto">
            Our AI pipeline transforms your startup idea into actionable insights through a
            streamlined process.
          </p>
        </motion.div>

        <div className="relative">
          <div className="absolute top-1/2 left-0 right-0 h-px bg-gradient-to-r from-indigo-500/30 via-purple-500/50 to-cyan-500/30 transform -translate-y-1/2 hidden md:block" />

          <div className="grid grid-cols-1 md:grid-cols-5 gap-8 relative">
            {timelineSteps.map((step, index) => (
              <motion.div
                key={step.name}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.1 }}
                className="relative text-center"
              >
                <motion.div
                  className="w-16 h-16 mx-auto rounded-2xl bg-gradient-to-br from-indigo-500 via-purple-500 to-cyan-500 flex items-center justify-center text-white font-bold text-xl shadow-glow relative z-10"
                  whileHover={{ scale: 1.1 }}
                  animate={{
                    boxShadow: [
                      '0 0 20px rgba(99, 102, 241, 0.4)',
                      '0 0 40px rgba(99, 102, 241, 0.6)',
                      '0 0 20px rgba(99, 102, 241, 0.4)',
                    ],
                  }}
                  transition={{ duration: 2, repeat: Infinity, delay: index * 0.3 }}
                >
                  {index + 1}
                </motion.div>
                <div className="mt-4">
                  <h3 className="text-lg font-semibold text-white mb-1">{step.name}</h3>
                  <p className="text-sm text-white/50">{step.description}</p>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
