'use client';

import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';

interface AnimatedBadgeProps {
  children: React.ReactNode;
  variant?: 'default' | 'success' | 'warning' | 'info' | 'gradient';
  className?: string;
}

export function AnimatedBadge({ children, variant = 'default', className }: AnimatedBadgeProps) {
  const variants = {
    default: 'bg-white/10 text-white border-white/20',
    success: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30',
    warning: 'bg-amber-500/20 text-amber-400 border-amber-500/30',
    info: 'bg-cyan-500/20 text-cyan-400 border-cyan-500/30',
    gradient:
      'bg-gradient-to-r from-indigo-500/20 via-purple-500/20 to-cyan-500/20 text-white border-indigo-500/30',
  };

  return (
    <motion.span
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      className={cn(
        'inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium',
        'border backdrop-blur-sm',
        'transition-all duration-200',
        variants[variant],
        className
      )}
    >
      {children}
    </motion.span>
  );
}

export function StatusBadge({
  status,
  className,
}: {
  status: 'running' | 'completed' | 'pending' | 'failed';
  className?: string;
}) {
  const statusConfig = {
    running: { label: 'Running', variant: 'info' as const, pulse: true },
    completed: { label: 'Completed', variant: 'success' as const, pulse: false },
    pending: { label: 'Pending', variant: 'default' as const, pulse: false },
    failed: { label: 'Failed', variant: 'warning' as const, pulse: false },
  };

  const config = statusConfig[status];

  return (
    <AnimatedBadge variant={config.variant} className={className}>
      {config.pulse && (
        <span className="relative flex h-2 w-2">
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-current opacity-75" />
          <span className="relative inline-flex rounded-full h-2 w-2 bg-current" />
        </span>
      )}
      {config.label}
    </AnimatedBadge>
  );
}
