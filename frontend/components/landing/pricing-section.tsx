'use client';

import { motion } from 'framer-motion';
import { Check, Sparkles, Zap, Building2 } from 'lucide-react';
import { AnimatedButton } from '@/components/ui/animated-button';

const plans = [
  {
    name: 'Starter',
    icon: Sparkles,
    price: 29,
    description: 'Perfect for individual entrepreneurs',
    features: [
      '5 Research Reports/month',
      'Basic Competitor Analysis',
      'Market Sizing',
      'PDF Export',
      'Email Support',
    ],
    popular: false,
  },
  {
    name: 'Professional',
    icon: Zap,
    price: 99,
    description: 'For serious founders and small teams',
    features: [
      'Unlimited Research Reports',
      'Advanced Competitor Analysis',
      'Full SWOT Analysis',
      'Healthcare Mode',
      'Priority AI Processing',
      'API Access',
      'Custom Reports',
      'Priority Support',
    ],
    popular: true,
  },
  {
    name: 'Enterprise',
    icon: Building2,
    price: null,
    description: 'For large teams and organizations',
    features: [
      'Everything in Professional',
      'Custom AI Agent Training',
      'White-label Reports',
      'Dedicated Account Manager',
      'SLA Guarantee',
      'On-premise Deployment',
      'Custom Integrations',
      '24/7 Support',
    ],
    popular: false,
  },
];

export function PricingSection() {
  return (
    <section id="pricing" className="py-24 relative">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-16"
        >
          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-white mb-4">
            Simple, <span className="text-gradient">Transparent</span> Pricing
          </h2>
          <p className="text-lg text-white/60 max-w-2xl mx-auto">
            Choose the plan that fits your needs. All plans include our core AI agents.
          </p>
        </motion.div>

        <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
          {plans.map((plan, index) => (
            <motion.div
              key={plan.name}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: index * 0.1 }}
              className={`relative ${plan.popular ? 'md:-mt-4 md:mb-4' : ''}`}
            >
              {plan.popular && (
                <div className="absolute -top-4 left-1/2 transform -translate-x-1/2 z-10">
                  <motion.div
                    className="px-4 py-1 rounded-full bg-gradient-to-r from-indigo-500 to-purple-500 text-white text-sm font-medium shadow-lg"
                    animate={{
                      boxShadow: [
                        '0 0 20px rgba(99, 102, 241, 0.4)',
                        '0 0 30px rgba(99, 102, 241, 0.6)',
                        '0 0 20px rgba(99, 102, 241, 0.4)',
                      ],
                    }}
                    transition={{ duration: 2, repeat: Infinity }}
                  >
                    Most Popular
                  </motion.div>
                </div>
              )}

              <motion.div
                whileHover={{ y: -8 }}
                className={`relative h-full rounded-3xl p-6 backdrop-blur-xl transition-all duration-500 ${
                  plan.popular
                    ? 'bg-gradient-to-br from-indigo-500/20 via-purple-500/20 to-cyan-500/20 border-2 border-indigo-500/50 shadow-glow-lg'
                    : 'bg-gradient-to-br from-white/[0.08] to-white/[0.02] border border-white/10 hover:border-white/20'
                }`}
              >
                <div className="text-center mb-6">
                  <div
                    className={`w-14 h-14 mx-auto mb-4 rounded-xl ${
                      plan.popular
                        ? 'bg-gradient-to-br from-indigo-500 to-purple-500'
                        : 'bg-white/10'
                    } flex items-center justify-center`}
                  >
                    <plan.icon className="w-7 h-7 text-white" />
                  </div>
                  <h3 className="text-xl font-bold text-white mb-1">{plan.name}</h3>
                  <p className="text-sm text-white/50">{plan.description}</p>
                </div>

                <div className="text-center mb-6">
                  {plan.price !== null ? (
                    <div className="flex items-baseline justify-center">
                      <span className="text-white/60 text-lg">$</span>
                      <span className={`text-5xl font-bold ${plan.popular ? 'text-gradient' : 'text-white'}`}>
                        {plan.price}
                      </span>
                      <span className="text-white/60 text-lg">/mo</span>
                    </div>
                  ) : (
                    <div className="text-3xl font-bold text-white">Custom</div>
                  )}
                </div>

                <ul className="space-y-3 mb-8">
                  {plan.features.map((feature) => (
                    <li key={feature} className="flex items-start gap-3">
                      <div className="w-5 h-5 rounded-full bg-gradient-to-br from-emerald-500 to-teal-500 flex items-center justify-center flex-shrink-0 mt-0.5">
                        <Check className="w-3 h-3 text-white" />
                      </div>
                      <span className="text-sm text-white/70">{feature}</span>
                    </li>
                  ))}
                </ul>

                <AnimatedButton
                  variant={plan.popular ? 'primary' : 'secondary'}
                  className="w-full"
                >
                  {plan.price === null ? 'Contact Sales' : 'Get Started'}
                </AnimatedButton>
              </motion.div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
