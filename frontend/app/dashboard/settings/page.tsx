'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  User,
  Bell,
  Shield,
  CreditCard,
  Zap,
  Globe,
  Moon,
  Save,
  Check,
  Key,
  Eye,
  EyeOff,
  ChevronRight,
  Trash2,
} from 'lucide-react';
import { GlassCard, GlassCardContent, GlassCardHeader } from '@/components/ui/glass-card';
import { AnimatedButton } from '@/components/ui/animated-button';
import { AnimatedBadge } from '@/components/ui/animated-badge';

const tabs = [
  { id: 'profile', label: 'Profile', icon: User },
  { id: 'notifications', label: 'Notifications', icon: Bell },
  { id: 'security', label: 'Security', icon: Shield },
  { id: 'billing', label: 'Billing', icon: CreditCard },
  { id: 'agents', label: 'AI Agents', icon: Zap },
];

function ProfileTab() {
  const [saved, setSaved] = useState(false);
  const save = () => { setSaved(true); setTimeout(() => setSaved(false), 2000); };
  return (
    <div className="space-y-6">
      <GlassCard>
        <GlassCardHeader>
          <h3 className="text-lg font-semibold text-white">Personal Information</h3>
        </GlassCardHeader>
        <GlassCardContent className="space-y-4">
          <div className="flex items-center gap-4 mb-6">
            <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-indigo-500 to-purple-500 flex items-center justify-center text-white font-bold text-2xl shadow-glow">
              JD
            </div>
            <div>
              <div className="text-white font-semibold">John Doe</div>
              <div className="text-sm text-white/50">john@example.com</div>
              <AnimatedBadge variant="gradient" className="mt-2">Professional Plan</AnimatedBadge>
            </div>
          </div>
          {[
            { label: 'Full Name', value: 'John Doe' },
            { label: 'Email', value: 'john@example.com' },
            { label: 'Company', value: 'My Startup Inc.' },
          ].map((f) => (
            <div key={f.label}>
              <label className="text-sm text-white/60 mb-1.5 block">{f.label}</label>
              <input
                defaultValue={f.value}
                className="w-full px-4 py-2.5 rounded-xl bg-white/5 border border-white/10 text-white text-sm focus:outline-none focus:border-indigo-500/50 transition-colors"
              />
            </div>
          ))}
          <AnimatedButton size="sm" onClick={save}>
            {saved ? <><Check className="w-4 h-4" /> Saved!</> : <><Save className="w-4 h-4" /> Save Changes</>}
          </AnimatedButton>
        </GlassCardContent>
      </GlassCard>
    </div>
  );
}

function NotificationsTab() {
  const [prefs, setPrefs] = useState({
    researchComplete: true,
    weeklyDigest: true,
    competitorUpdates: false,
    systemAlerts: true,
  });
  return (
    <GlassCard>
      <GlassCardHeader>
        <h3 className="text-lg font-semibold text-white">Notification Preferences</h3>
      </GlassCardHeader>
      <GlassCardContent className="space-y-4">
        {Object.entries(prefs).map(([key, val]) => {
          const labels: Record<string, string> = {
            researchComplete: 'Research Complete',
            weeklyDigest: 'Weekly Digest',
            competitorUpdates: 'Competitor Updates',
            systemAlerts: 'System Alerts',
          };
          return (
            <div key={key} className="flex items-center justify-between p-4 rounded-xl bg-white/5 border border-white/10">
              <div>
                <div className="text-sm font-medium text-white">{labels[key]}</div>
                <div className="text-xs text-white/40">Receive notifications when {labels[key].toLowerCase()}</div>
              </div>
              <motion.button
                onClick={() => setPrefs(p => ({ ...p, [key]: !val }))}
                className={`w-12 h-6 rounded-full border transition-all duration-300 relative ${val ? 'bg-indigo-500 border-indigo-500' : 'bg-white/10 border-white/20'}`}
              >
                <motion.div
                  animate={{ x: val ? 24 : 2 }}
                  transition={{ type: 'spring', stiffness: 400, damping: 25 }}
                  className="absolute top-0.5 w-5 h-5 rounded-full bg-white shadow"
                />
              </motion.button>
            </div>
          );
        })}
      </GlassCardContent>
    </GlassCard>
  );
}

function SecurityTab() {
  const [showPass, setShowPass] = useState(false);
  return (
    <div className="space-y-6">
      <GlassCard>
        <GlassCardHeader>
          <h3 className="text-lg font-semibold text-white">Change Password</h3>
        </GlassCardHeader>
        <GlassCardContent className="space-y-4">
          {['Current Password', 'New Password', 'Confirm Password'].map((f) => (
            <div key={f}>
              <label className="text-sm text-white/60 mb-1.5 block">{f}</label>
              <div className="relative">
                <Key className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-white/30" />
                <input
                  type={showPass ? 'text' : 'password'}
                  className="w-full pl-10 pr-10 py-2.5 rounded-xl bg-white/5 border border-white/10 text-white text-sm focus:outline-none focus:border-indigo-500/50"
                />
                <button onClick={() => setShowPass(!showPass)} className="absolute right-3 top-1/2 -translate-y-1/2 text-white/40 hover:text-white">
                  {showPass ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>
          ))}
          <AnimatedButton size="sm"><Save className="w-4 h-4" /> Update Password</AnimatedButton>
        </GlassCardContent>
      </GlassCard>
      <GlassCard>
        <GlassCardHeader>
          <h3 className="text-lg font-semibold text-white">Two-Factor Authentication</h3>
        </GlassCardHeader>
        <GlassCardContent>
          <p className="text-sm text-white/60 mb-4">Add an extra layer of security to your account</p>
          <AnimatedButton variant="secondary" size="sm"><Shield className="w-4 h-4" /> Enable 2FA</AnimatedButton>
        </GlassCardContent>
      </GlassCard>
    </div>
  );
}

function BillingTab() {
  return (
    <div className="space-y-6">
      <GlassCard className="border-indigo-500/30">
        <GlassCardContent>
          <div className="flex items-start justify-between">
            <div>
              <div className="flex items-center gap-3 mb-2">
                <h3 className="text-xl font-bold text-white">Professional Plan</h3>
                <AnimatedBadge variant="success">Active</AnimatedBadge>
              </div>
              <p className="text-white/50 text-sm">Unlimited reports, all AI agents, healthcare mode</p>
              <div className="mt-4 text-3xl font-bold text-gradient">$99<span className="text-lg text-white/50">/mo</span></div>
            </div>
            <AnimatedButton variant="secondary" size="sm">Upgrade</AnimatedButton>
          </div>
        </GlassCardContent>
      </GlassCard>

      <GlassCard>
        <GlassCardHeader><h3 className="text-lg font-semibold text-white">Usage This Month</h3></GlassCardHeader>
        <GlassCardContent className="space-y-4">
          {[
            { label: 'Research Reports', used: 8, max: 'Unlimited' },
            { label: 'AI Agent Runs', used: 64, max: 'Unlimited' },
            { label: 'API Calls', used: 1240, max: 10000 },
          ].map((u) => (
            <div key={u.label}>
              <div className="flex justify-between text-sm mb-1.5">
                <span className="text-white/70">{u.label}</span>
                <span className="text-white/50">{u.used} / {u.max}</span>
              </div>
              {typeof u.max === 'number' && (
                <div className="h-1.5 rounded-full bg-white/10">
                  <div className="h-full rounded-full bg-gradient-to-r from-indigo-500 to-purple-500" style={{ width: `${(u.used / u.max) * 100}%` }} />
                </div>
              )}
            </div>
          ))}
        </GlassCardContent>
      </GlassCard>
    </div>
  );
}

function AgentsTab() {
  const agentSettings = [
    { name: 'Research Agent', enabled: true, depth: 'Deep' },
    { name: 'Competitor Agent', enabled: true, depth: 'Standard' },
    { name: 'Market Agent', enabled: true, depth: 'Deep' },
    { name: 'Trend Agent', enabled: true, depth: 'Standard' },
    { name: 'SWOT Agent', enabled: false, depth: 'Standard' },
    { name: 'Risk Agent', enabled: true, depth: 'Standard' },
  ];

  const [settings, setSettings] = useState(agentSettings);

  return (
    <GlassCard>
      <GlassCardHeader><h3 className="text-lg font-semibold text-white">AI Agent Configuration</h3></GlassCardHeader>
      <GlassCardContent className="space-y-3">
        {settings.map((a, i) => (
          <div key={a.name} className="flex items-center justify-between p-4 rounded-xl bg-white/5 border border-white/10">
            <div className="flex items-center gap-3">
              <Zap className="w-5 h-5 text-indigo-400" />
              <div>
                <div className="text-sm font-medium text-white">{a.name}</div>
                <div className="text-xs text-white/40">Depth: {a.depth}</div>
              </div>
            </div>
            <motion.button
              onClick={() => setSettings(s => s.map((x, j) => j === i ? { ...x, enabled: !x.enabled } : x))}
              className={`w-12 h-6 rounded-full border transition-all duration-300 relative ${a.enabled ? 'bg-indigo-500 border-indigo-500' : 'bg-white/10 border-white/20'}`}
            >
              <motion.div
                animate={{ x: a.enabled ? 24 : 2 }}
                transition={{ type: 'spring', stiffness: 400, damping: 25 }}
                className="absolute top-0.5 w-5 h-5 rounded-full bg-white shadow"
              />
            </motion.button>
          </div>
        ))}
      </GlassCardContent>
    </GlassCard>
  );
}

const tabContent: Record<string, React.ComponentType> = {
  profile: ProfileTab,
  notifications: NotificationsTab,
  security: SecurityTab,
  billing: BillingTab,
  agents: AgentsTab,
};

export default function SettingsPage() {
  const [activeTab, setActiveTab] = useState('profile');
  const Content = tabContent[activeTab];

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      <div>
        <h1 className="text-2xl font-bold text-white mb-1">
          Account <span className="text-gradient">Settings</span>
        </h1>
        <p className="text-white/50">Manage your account, preferences, and AI agents</p>
      </div>

      <div className="grid md:grid-cols-[200px_1fr] gap-6">
        <div className="space-y-1">
          {tabs.map((tab) => (
            <motion.button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              whileHover={{ x: 2 }}
              className={`w-full flex items-center gap-3 px-4 py-2.5 rounded-xl text-sm font-medium transition-all ${
                activeTab === tab.id
                  ? 'bg-indigo-500/20 text-white border border-indigo-500/30'
                  : 'text-white/60 hover:text-white hover:bg-white/5'
              }`}
            >
              <tab.icon className="w-4 h-4 flex-shrink-0" />
              {tab.label}
              {activeTab === tab.id && <ChevronRight className="w-4 h-4 ml-auto text-indigo-400" />}
            </motion.button>
          ))}
        </div>

        <motion.div
          key={activeTab}
          initial={{ opacity: 0, x: 10 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.2 }}
        >
          <Content />
        </motion.div>
      </div>
    </div>
  );
}
