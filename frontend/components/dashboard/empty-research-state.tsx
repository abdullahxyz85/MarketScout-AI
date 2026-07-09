'use client';

import Link from 'next/link';
import { motion } from 'framer-motion';
import { Sparkles, ArrowRight, LucideIcon } from 'lucide-react';
import { GlassCard, GlassCardContent } from '@/components/ui/glass-card';
import { AnimatedButton } from '@/components/ui/animated-button';

interface EmptyResearchStateProps {
  title: string;
  description: string;
  ctaLabel?: string;
  icon?: LucideIcon;
}

export function EmptyResearchState({
  title,
  description,
  ctaLabel = 'Start New Research',
  icon: Icon = Sparkles,
}: EmptyResearchStateProps) {
  return (
    <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }}>
      <GlassCard>
        <GlassCardContent className="flex flex-col items-center text-center py-16 px-6">
          <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-indigo-500 to-purple-500 flex items-center justify-center mb-5 shadow-lg">
            <Icon className="w-7 h-7 text-white" />
          </div>
          <h3 className="text-lg font-semibold text-white mb-2">{title}</h3>
          <p className="text-white/45 text-sm max-w-md mb-6">{description}</p>
          <Link href="/dashboard/research">
            <AnimatedButton size="sm">
              {ctaLabel}<ArrowRight className="w-4 h-4" />
            </AnimatedButton>
          </Link>
        </GlassCardContent>
      </GlassCard>
    </motion.div>
  );
}
