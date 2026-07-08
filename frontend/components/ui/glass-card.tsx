'use client';

import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';
import { ReactNode } from 'react';

interface GlassCardProps {
  children: ReactNode;
  className?: string;
  glow?: boolean;
  hover?: boolean;
}

export function GlassCard({ children, className, glow, hover = true }: GlassCardProps) {
  return (
    <motion.div
      whileHover={hover ? { y: -4, scale: 1.01 } : undefined}
      transition={{ type: 'spring', stiffness: 400, damping: 17 }}
      className={cn(
        'relative overflow-hidden rounded-2xl',
        'bg-gradient-to-br from-white/[0.08] to-white/[0.02]',
        'backdrop-blur-xl',
        'border border-white/[0.08]',
        'shadow-xl shadow-black/20',
        glow && 'shadow-glow',
        hover && 'cursor-pointer',
        className
      )}
    >
      <div className="absolute inset-0 bg-gradient-to-br from-indigo-500/5 via-transparent to-purple-500/5 opacity-0 transition-opacity duration-500 hover:opacity-100" />
      <div className="relative z-10">{children}</div>
    </motion.div>
  );
}

export function GlassCardHeader({ children, className }: { children: ReactNode; className?: string }) {
  return <div className={cn('p-6 border-b border-white/5', className)}>{children}</div>;
}

export function GlassCardContent({ children, className }: { children: ReactNode; className?: string }) {
  return <div className={cn('p-6', className)}>{children}</div>;
}

export function GlassCardFooter({ children, className }: { children: ReactNode; className?: string }) {
  return (
    <div className={cn('p-6 pt-0 border-t border-white/5 mt-6 pt-4', className)}>{children}</div>
  );
}
