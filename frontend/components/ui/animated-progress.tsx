'use client';

import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';

interface AnimatedProgressProps {
  value: number;
  max?: number;
  className?: string;
  barClassName?: string;
  showLabel?: boolean;
  variant?: 'default' | 'gradient' | 'glow';
}

export function AnimatedProgress({
  value,
  max = 100,
  className,
  barClassName,
  showLabel = false,
  variant = 'gradient',
}: AnimatedProgressProps) {
  const percentage = Math.min(100, Math.max(0, (value / max) * 100));

  const variants = {
    default: 'bg-white/30',
    gradient: 'bg-gradient-to-r from-indigo-500 via-purple-500 to-cyan-500',
    glow: 'bg-gradient-to-r from-indigo-500 via-purple-500 to-cyan-500 shadow-glow',
  };

  return (
    <div className={cn('w-full', className)}>
      <div className="relative h-2 w-full overflow-hidden rounded-full bg-white/10">
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${percentage}%` }}
          transition={{ duration: 0.8, ease: 'easeOut' }}
          className={cn('h-full rounded-full', variants[variant], barClassName)}
        />
        <div className="absolute inset-0 bg-gradient-to-t from-transparent to-white/10" />
      </div>
      {showLabel && (
        <div className="mt-1 text-xs text-muted-foreground text-right">{Math.round(percentage)}%</div>
      )}
    </div>
  );
}
