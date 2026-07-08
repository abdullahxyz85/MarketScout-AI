'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronDown } from 'lucide-react';
import { cn } from '@/lib/utils';

const faqs = [
  {
    question: 'What is MarketScout AI?',
    answer:
      'MarketScout AI is an autonomous multi-agent AI platform that transforms startup ideas into comprehensive market intelligence reports. Our specialized AI agents work together to research competitors, analyze markets, identify trends, assess risks, and generate actionable insights.',
  },
  {
    question: 'How do the AI agents work together?',
    answer:
      'Our multi-agent system employs specialized AI agents that each focus on a specific domain. The Research Agent gathers data, while Competitor, Market, and Trend Agents analyze different aspects. SWOT and Opportunity Agents synthesize findings, and the Report Generator compiles everything into a comprehensive report.',
  },
  {
    question: 'What AI models power MarketScout?',
    answer:
      'We leverage a combination of state-of-the-art AI models including Llama and Qwen, running on Fireworks AI infrastructure with AMD Cloud GPUs. This combination ensures fast, accurate, and reliable intelligence generation.',
  },
  {
    question: 'Can I download the research reports?',
    answer:
      'Yes! All reports can be exported as PDF documents. Professional and Enterprise plans also include API access for automated report generation and integration with your existing tools.',
  },
  {
    question: 'Does it support healthcare startups?',
    answer:
      'Absolutely! Our dedicated Healthcare Mode provides specialized analysis including FDA regulatory pathways, clinical trial intelligence, patient outcome analysis, and healthcare-specific market insights. Its perfect for medtech, healthtech, and biotech startups.',
  },
  {
    question: 'How long does it take to generate a report?',
    answer:
      'A complete market intelligence report typically takes 5-15 minutes depending on complexity. Our AI agents work in parallel to speed up the process while maintaining thorough analysis.',
  },
];

export function FAQSection() {
  const [openIndex, setOpenIndex] = useState<number | null>(0);

  return (
    <section id="faq" className="py-24 relative">
      <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-16"
        >
          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-white mb-4">
            Frequently Asked <span className="text-gradient">Questions</span>
          </h2>
          <p className="text-lg text-white/60">
            Everything you need to know about MarketScout AI.
          </p>
        </motion.div>

        <div className="space-y-4">
          {faqs.map((faq, index) => (
            <motion.div
              key={faq.question}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: index * 0.05 }}
            >
              <motion.button
                onClick={() => setOpenIndex(openIndex === index ? null : index)}
                className={cn(
                  'w-full text-left p-5 rounded-2xl transition-all duration-300',
                  'bg-gradient-to-br from-white/[0.08] to-white/[0.02]',
                  'border border-white/10 hover:border-white/20',
                  'backdrop-blur-xl',
                  openIndex === index && 'bg-white/10 border-indigo-500/30'
                )}
                whileHover={{ y: -2 }}
              >
                <div className="flex items-center justify-between">
                  <span className="text-lg font-medium text-white pr-4">
                    {faq.question}
                  </span>
                  <motion.div
                    animate={{ rotate: openIndex === index ? 180 : 0 }}
                    transition={{ duration: 0.3 }}
                    className="flex-shrink-0"
                  >
                    <ChevronDown className="w-5 h-5 text-white/60" />
                  </motion.div>
                </div>

                <AnimatePresence>
                  {openIndex === index && (
                    <motion.div
                      initial={{ height: 0, opacity: 0 }}
                      animate={{ height: 'auto', opacity: 1 }}
                      exit={{ height: 0, opacity: 0 }}
                      transition={{ duration: 0.3 }}
                      className="overflow-hidden"
                    >
                      <p className="pt-4 text-white/60 leading-relaxed">
                        {faq.answer}
                      </p>
                    </motion.div>
                  )}
                </AnimatePresence>
              </motion.button>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
