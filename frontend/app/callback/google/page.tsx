'use client';

import { useEffect, useRef, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { motion } from 'framer-motion';
import { AlertCircle } from 'lucide-react';
import { AnimatedBackground } from '@/components/landing/animated-background';

export default function GoogleCallbackPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [error, setError] = useState<string | null>(null);
  const requestedRef = useRef(false);

  useEffect(() => {
    if (requestedRef.current) return;
    requestedRef.current = true;

    const query = searchParams.toString();

    fetch(`/api/auth/google/callback?${query}`, {
      credentials: 'include',
    })
      .then(async (res) => {
        if (!res.ok) {
          const body = await res.json().catch(() => null);
          throw new Error(body?.detail ?? 'Google authentication failed');
        }
        return res.json();
      })
      .then((data) => {
        router.replace(data.redirect_url ?? '/dashboard');
      })
      .catch((err) => {
        setError(err instanceof Error ? err.message : 'Google authentication failed');
      });
  }, [searchParams, router]);

  return (
    <div className="min-h-screen flex items-center justify-center px-4 relative">
      <AnimatedBackground />
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="relative z-10 text-center"
      >
        {error ? (
          <div className="max-w-sm">
            <AlertCircle className="w-8 h-8 text-red-400 mx-auto mb-3" />
            <p className="text-white/80 text-sm mb-1">Sign in failed</p>
            <p className="text-white/40 text-xs mb-6">{error}</p>
            <a href="/login" className="text-indigo-400 hover:text-indigo-300 text-sm font-medium">
              Back to login
            </a>
          </div>
        ) : (
          <div>
            <div className="w-8 h-8 rounded-full border-2 border-white/20 border-t-indigo-500 animate-spin mx-auto mb-4" />
            <p className="text-white/50 text-sm">Signing you in with Google...</p>
          </div>
        )}
      </motion.div>
    </div>
  );
}
