'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import Link from 'next/link';
import { Eye, EyeOff, Mail, Lock, User, ArrowRight, Github, Check } from 'lucide-react';
import { AnimatedBackground } from '@/components/landing/animated-background';
import { Logo } from '@/components/ui/logo';
import { GoogleIcon } from '@/components/ui/google-icon';

const perks = [
  'Unlimited AI market research',
  'Full competitor analysis suite',
  'Healthcare mode included',
  'Instant PDF reports',
];

export default function SignupPage() {
  const [form, setForm] = useState({ name: '', email: '', password: '' });
  const [showPass, setShowPass] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setTimeout(() => setLoading(false), 1500);
  };

  const passwordStrength = form.password.length === 0 ? 0 : form.password.length < 6 ? 1 : form.password.length < 10 ? 2 : 3;
  const strengthLabels = ['', 'Weak', 'Good', 'Strong'];
  const strengthColors = ['', 'bg-red-500', 'bg-yellow-500', 'bg-emerald-500'];

  return (
    <div className="min-h-screen flex items-center justify-center px-4 py-12 relative">
      <AnimatedBackground />

      <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
        <div className="w-[600px] h-96 rounded-full bg-purple-500/15 blur-3xl" />
      </div>

      <div className="w-full max-w-5xl grid lg:grid-cols-2 gap-8 items-center relative z-10">
        {/* Left: Value prop */}
        <motion.div
          initial={{ opacity: 0, x: -40 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.6 }}
          className="hidden lg:block space-y-6"
        >
          <Link href="/" className="inline-flex items-center">
            <Logo size={36} className="[&_[data-slot=wordmark]]:text-2xl" />
          </Link>

          <div>
            <h1 className="text-4xl font-bold text-white leading-tight mb-3">
              Start validating your <span className="text-gradient">startup idea</span> today
            </h1>
            <p className="text-white/50 text-lg">
              Join thousands of founders using AI-powered intelligence to make smarter decisions.
            </p>
          </div>

          <div className="space-y-3">
            {perks.map((perk, i) => (
              <motion.div
                key={perk}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.2 + i * 0.1 }}
                className="flex items-center gap-3"
              >
                <div className="w-6 h-6 rounded-full bg-gradient-to-br from-emerald-500 to-teal-500 flex items-center justify-center flex-shrink-0">
                  <Check className="w-3.5 h-3.5 text-white" />
                </div>
                <span className="text-white/70">{perk}</span>
              </motion.div>
            ))}
          </div>

          <div className="p-4 rounded-2xl bg-white/5 border border-white/10 backdrop-blur-xl">
            <div className="flex items-center gap-3 mb-2">
              <div className="w-10 h-10 rounded-full bg-gradient-to-br from-indigo-500 to-purple-500 flex items-center justify-center text-white font-bold text-sm">
                SC
              </div>
              <div>
                <div className="text-sm font-medium text-white">Sarah Chen</div>
                <div className="text-xs text-white/40">CEO, HealthTech Startup</div>
              </div>
            </div>
            <p className="text-sm text-white/60 italic">
              "MarketScout AI saved us months of research. The insights were incredibly accurate."
            </p>
          </div>
        </motion.div>

        {/* Right: Form */}
        <motion.div
          initial={{ opacity: 0, y: 40, scale: 0.95 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          transition={{ duration: 0.6, delay: 0.1 }}
        >
          <div className="relative rounded-3xl overflow-hidden backdrop-blur-2xl border border-white/10 bg-gradient-to-br from-white/[0.08] to-white/[0.02] shadow-2xl">
            <div className="absolute inset-0 bg-gradient-to-br from-indigo-500/5 via-transparent to-purple-500/5 pointer-events-none" />

            <div className="relative p-8">
              <div className="lg:hidden text-center mb-8">
                <Link href="/" className="inline-flex items-center">
                  <Logo size={30} className="[&_[data-slot=wordmark]]:text-xl" />
                </Link>
              </div>

              <h2 className="text-2xl font-bold text-white mb-1">Create your account</h2>
              <p className="text-white/50 text-sm mb-6">Free to start, no credit card required</p>

              <div className="space-y-3 mb-5">
                <motion.a
                  href="/api/auth/github/login"
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  className="w-full flex items-center justify-center gap-3 py-3 rounded-xl bg-white/5 border border-white/10 text-white/80 hover:bg-white/10 hover:text-white transition-all text-sm font-medium"
                >
                  <Github className="w-5 h-5" />
                  Continue with GitHub
                </motion.a>
                <motion.a
                  href="/api/auth/google/login"
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  className="w-full flex items-center justify-center gap-3 py-3 rounded-xl bg-white/5 border border-white/10 text-white/80 hover:bg-white/10 hover:text-white transition-all text-sm font-medium"
                >
                  <GoogleIcon className="w-5 h-5" />
                  Continue with Google
                </motion.a>
              </div>

              <div className="relative mb-5">
                <div className="absolute inset-0 flex items-center">
                  <div className="w-full border-t border-white/10" />
                </div>
                <div className="relative flex justify-center">
                  <span className="px-3 bg-transparent text-white/40 text-sm">or sign up with email</span>
                </div>
              </div>

              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <label className="text-sm text-white/60 mb-1.5 block">Full Name</label>
                  <div className="relative">
                    <User className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-white/30" />
                    <input
                      type="text"
                      value={form.name}
                      onChange={(e) => setForm(f => ({ ...f, name: e.target.value }))}
                      placeholder="John Doe"
                      className="w-full pl-11 pr-4 py-3 rounded-xl bg-white/5 border border-white/10 text-white placeholder:text-white/25 text-sm focus:outline-none focus:border-indigo-500/60 transition-colors"
                    />
                  </div>
                </div>

                <div>
                  <label className="text-sm text-white/60 mb-1.5 block">Email address</label>
                  <div className="relative">
                    <Mail className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-white/30" />
                    <input
                      type="email"
                      value={form.email}
                      onChange={(e) => setForm(f => ({ ...f, email: e.target.value }))}
                      placeholder="you@example.com"
                      className="w-full pl-11 pr-4 py-3 rounded-xl bg-white/5 border border-white/10 text-white placeholder:text-white/25 text-sm focus:outline-none focus:border-indigo-500/60 transition-colors"
                    />
                  </div>
                </div>

                <div>
                  <label className="text-sm text-white/60 mb-1.5 block">Password</label>
                  <div className="relative">
                    <Lock className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-white/30" />
                    <input
                      type={showPass ? 'text' : 'password'}
                      value={form.password}
                      onChange={(e) => setForm(f => ({ ...f, password: e.target.value }))}
                      placeholder="Min. 8 characters"
                      className="w-full pl-11 pr-11 py-3 rounded-xl bg-white/5 border border-white/10 text-white placeholder:text-white/25 text-sm focus:outline-none focus:border-indigo-500/60 transition-colors"
                    />
                    <button
                      type="button"
                      onClick={() => setShowPass(!showPass)}
                      className="absolute right-3.5 top-1/2 -translate-y-1/2 text-white/30 hover:text-white/70 transition-colors"
                    >
                      {showPass ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                    </button>
                  </div>
                  {form.password.length > 0 && (
                    <div className="mt-2 flex items-center gap-2">
                      <div className="flex gap-1 flex-1">
                        {[1, 2, 3].map((n) => (
                          <div key={n} className={`h-1 flex-1 rounded-full transition-all duration-300 ${n <= passwordStrength ? strengthColors[passwordStrength] : 'bg-white/10'}`} />
                        ))}
                      </div>
                      <span className={`text-xs font-medium ${passwordStrength === 3 ? 'text-emerald-400' : passwordStrength === 2 ? 'text-yellow-400' : 'text-red-400'}`}>
                        {strengthLabels[passwordStrength]}
                      </span>
                    </div>
                  )}
                </div>

                <motion.button
                  type="submit"
                  disabled={loading}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  className="w-full py-3 rounded-xl bg-gradient-to-r from-indigo-600 via-purple-600 to-indigo-600 bg-[length:200%_auto] text-white font-semibold text-sm shadow-lg shadow-indigo-500/25 hover:shadow-indigo-500/40 transition-all flex items-center justify-center gap-2 mt-2"
                >
                  {loading ? (
                    <motion.div
                      className="w-5 h-5 rounded-full border-2 border-white/30 border-t-white"
                      animate={{ rotate: 360 }}
                      transition={{ duration: 0.8, repeat: Infinity, ease: 'linear' }}
                    />
                  ) : (
                    <>Create Account <ArrowRight className="w-4 h-4" /></>
                  )}
                </motion.button>

                <p className="text-xs text-white/30 text-center">
                  By signing up, you agree to our{' '}
                  <Link href="#" className="text-indigo-400 hover:underline">Terms</Link> and{' '}
                  <Link href="#" className="text-indigo-400 hover:underline">Privacy Policy</Link>.
                </p>
              </form>

              <p className="text-center text-sm text-white/40 mt-5">
                Already have an account?{' '}
                <Link href="/login" className="text-indigo-400 hover:text-indigo-300 font-medium transition-colors">
                  Sign in
                </Link>
              </p>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
}
