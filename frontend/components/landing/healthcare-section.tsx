'use client';

import { motion } from 'framer-motion';
import { Heart, Activity, Building, Shield, Microscope, Stethoscope } from 'lucide-react';
import { GlassCard, GlassCardContent } from '@/components/ui/glass-card';

const healthcareFeatures = [
  {
    icon: Building,
    title: 'Hospital Market Analysis',
    description: 'Deep analysis of hospital systems and healthcare providers',
  },
  {
    icon: Microscope,
    title: 'Regulatory Insights',
    description: 'FDA approval pathways and compliance requirements',
  },
  {
    icon: Shield,
    title: 'Risk Assessment',
    description: 'Healthcare-specific risk and liability evaluation',
  },
  {
    icon: Stethoscope,
    title: 'Clinical Intelligence',
    description: 'Clinical workflow and patient outcome analysis',
  },
];

export function HealthcareSection() {
  return (
    <section className="py-24 relative overflow-hidden">
      <div className="absolute inset-0 bg-gradient-to-r from-emerald-500/5 via-cyan-500/5 to-blue-500/5" />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-16"
        >
          <motion.div
            className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-sm mb-6"
            whileHover={{ scale: 1.05 }}
          >
            <Heart className="w-4 h-4" />
            Healthcare Mode
          </motion.div>
          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-white mb-4">
            Specialized Intelligence for <span className="text-gradient">Healthcare Startups</span>
          </h2>
          <p className="text-lg text-white/60 max-w-2xl mx-auto">
            Healthcare startups require specialized analysis. Our dedicated healthcare mode provides
            industry-specific insights, regulatory guidance, and deep market understanding.
          </p>
        </motion.div>

        <div className="grid lg:grid-cols-2 gap-12 items-center">
          <motion.div
            initial={{ opacity: 0, x: -50 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            className="space-y-6"
          >
            {healthcareFeatures.map((feature, index) => (
              <motion.div
                key={feature.title}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.1 }}
              >
                <GlassCard>
                  <GlassCardContent className="flex items-start gap-4">
                    <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-emerald-500 to-teal-500 flex items-center justify-center flex-shrink-0">
                      <feature.icon className="w-6 h-6 text-white" />
                    </div>
                    <div>
                      <h3 className="text-lg font-semibold text-white mb-1">{feature.title}</h3>
                      <p className="text-sm text-white/60">{feature.description}</p>
                    </div>
                  </GlassCardContent>
                </GlassCard>
              </motion.div>
            ))}
          </motion.div>

          <motion.div
            initial={{ opacity: 0, x: 50 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            className="relative"
          >
            <div className="absolute inset-0 bg-gradient-to-r from-emerald-500/20 to-cyan-500/20 rounded-3xl blur-3xl" />

            <div className="relative rounded-3xl overflow-hidden backdrop-blur-xl border border-white/10 bg-gradient-to-br from-white/[0.08] to-white/[0.02] shadow-2xl p-6">
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full bg-emerald-400" />
                  <span className="text-sm text-white/80">Healthcare Dashboard</span>
                </div>
                <Activity className="w-5 h-5 text-emerald-400" />
              </div>

              <div className="grid grid-cols-2 gap-4 mb-6">
                <div className="p-4 rounded-xl bg-white/5 border border-white/10">
                  <div className="text-2xl font-bold text-white">$847B</div>
                  <div className="text-xs text-white/50">Healthcare Market</div>
                </div>
                <div className="p-4 rounded-xl bg-white/5 border border-white/10">
                  <div className="text-2xl font-bold text-emerald-400">+12.3%</div>
                  <div className="text-xs text-white/50">Growth Rate</div>
                </div>
              </div>

              <div className="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/20 mb-4">
                <div className="flex items-center gap-2 mb-2">
                  <Shield className="w-4 h-4 text-emerald-400" />
                  <span className="text-sm font-medium text-white">FDA Pathway</span>
                </div>
                <p className="text-xs text-white/60">
                  510(k) clearance recommended for your device category
                </p>
              </div>

              <div className="space-y-2">
                {['Patient Outcomes', 'Clinical Trials', 'Regulatory Compliance'].map((item) => (
                  <div
                    key={item}
                    className="flex items-center justify-between p-3 rounded-lg bg-white/5 border border-white/10"
                  >
                    <span className="text-sm text-white/80">{item}</span>
                    <div className="w-16 h-1.5 rounded-full bg-white/10">
                      <motion.div
                        className="h-full rounded-full bg-gradient-to-r from-emerald-500 to-cyan-500"
                        initial={{ width: '0%' }}
                        whileInView={{ width: `${Math.random() * 60 + 40}%` }}
                        viewport={{ once: true }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  );
}
