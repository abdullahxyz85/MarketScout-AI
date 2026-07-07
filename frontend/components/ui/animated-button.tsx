'use client';

import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';
import { ReactNode } from 'react';

interface AnimatedButtonProps {
  children: ReactNode;
  variant?: 'primary' | 'secondary' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  className?: string;
  onClick?: () => void;
  disabled?: boolean;
}

export function AnimatedButton({
  children,
  variant = 'primary',
  size = 'md',
  className,
  onClick,
  disabled,
}: AnimatedButtonProps) {
  const variants = {
    primary:
      'bg-gradient-to-r from-indigo-600 via-purple-600 to-indigo-600 bg-[length:200%_auto] hover:bg-right text-white shadow-lg shadow-indigo-500/25 hover:shadow-indigo-500/40',
    secondary:
      'bg-white/5 border border-white/10 hover:bg-white/10 hover:border-white/20 text-white backdrop-blur-sm',
    ghost: 'hover:bg-white/5 text-white',
  };

  const sizes = {
    sm: 'px-4 py-2 text-sm',
    md: 'px-6 py-3 text-base',
    lg: 'px-8 py-4 text-lg',
  };

  return (
    <motion.button
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      transition={{ type: 'spring', stiffness: 400, damping: 17 }}
      className={cn(
        'relative rounded-xl font-medium transition-all duration-300 outline-none',
        'focus-visible:ring-2 focus-visible:ring-indigo-500 focus-visible:ring-offset-2 focus-visible:ring-offset-background',
        'disabled:opacity-50 disabled:cursor-not-allowed',
        variants[variant],
        sizes[size],
        className
      )}
      onClick={onClick}
      disabled={disabled}
    >
      <span className="relative z-10 flex items-center justify-center gap-2">{children}</span>
      {variant === 'primary' && (
        <motion.div
          className="absolute inset-0 rounded-xl bg-gradient-to-r from-indigo-600 via-purple-500 to-cyan-500 opacity-0 blur-xl transition-opacity duration-500 group-hover:opacity-50"
          initial={{ opacity: 0 }}
          whileHover={{ opacity: 0.5 }}
        />
      )}
    </motion.button>
  );
}
