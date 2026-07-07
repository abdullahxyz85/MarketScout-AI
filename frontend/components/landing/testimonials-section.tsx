'use client';

import { motion } from 'framer-motion';
import { Star } from 'lucide-react';

const testimonials = [
  {
    quote:
      "MarketScout AI saved us months of research. The insights were incredibly accurate and helped us pivot our strategy at the right time.",
    author: 'Sarah Chen',
    role: 'CEO, HealthTech Startup',
    avatar: 'SC',
  },
  {
    quote:
      "The multi-agent approach is brilliant. Each agent brings complementary insights that would take a team of analysts to produce.",
    author: 'Marcus Williams',
    role: 'Founder, Quantum Labs',
    avatar: 'MW',
  },
  {
    quote:
      "Healthcare mode was a game-changer for us. The regulatory insights alone were worth the subscription.",
    author: 'Dr. Emily Rodriguez',
    role: 'Co-founder, MedTech Innovations',
    avatar: 'ER',
  },
];

export function TestimonialsSection() {
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
            Trusted by <span className="text-gradient">Innovative Founders</span>
          </h2>
          <p className="text-lg text-white/60 max-w-2xl mx-auto">
            See what startup founders and entrepreneurs are saying about MarketScout AI.
          </p>
        </motion.div>

        <div className="grid md:grid-cols-3 gap-6">
          {testimonials.map((testimonial, index) => (
            <motion.div
              key={testimonial.author}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: index * 0.1 }}
            >
              <motion.div
                whileHover={{ y: -4 }}
                className="h-full p-6 rounded-2xl bg-gradient-to-br from-white/[0.08] to-white/[0.02] border border-white/10 backdrop-blur-xl"
              >
                <div className="flex gap-1 mb-4">
                  {[1, 2, 3, 4, 5].map((star) => (
                    <Star
                      key={star}
                      className="w-4 h-4 text-yellow-400 fill-yellow-400"
                    />
                  ))}
                </div>

                <p className="text-white/80 mb-6 leading-relaxed">
                  "{testimonial.quote}"
                </p>

                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-gradient-to-br from-indigo-500 to-purple-500 flex items-center justify-center text-white font-semibold text-sm">
                    {testimonial.avatar}
                  </div>
                  <div>
                    <div className="text-sm font-semibold text-white">
                      {testimonial.author}
                    </div>
                    <div className="text-xs text-white/50">{testimonial.role}</div>
                  </div>
                </div>
              </motion.div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
