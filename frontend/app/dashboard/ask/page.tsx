'use client';

import { useEffect, useRef, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  MessageCircle, Send, Bot, User, Loader2,
  Sparkles, RefreshCw, Copy, Check,
} from 'lucide-react';
import { GlassCard, GlassCardContent, GlassCardHeader } from '@/components/ui/glass-card';
import { AnimatedButton } from '@/components/ui/animated-button';
import { EmptyResearchState } from '@/components/dashboard/empty-research-state';
import { loadLastResearch } from '@/lib/research-store';

// ── Types ──────────────────────────────────────────────────────────────────────
interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

// ── Suggested questions ───────────────────────────────────────────────────────
const SUGGESTED = [
  'What is the total addressable market size for this idea?',
  'Who are the top 3 competitors and what are their weaknesses?',
  'What is the biggest risk I should be worried about?',
  'What makes this idea innovative compared to existing solutions?',
  'What is the recommended go-to-market strategy?',
  'What white spaces or unmet needs can this idea address?',
];

// ── Message bubble ─────────────────────────────────────────────────────────────
function MessageBubble({ msg }: { msg: Message }) {
  const [copied, setCopied] = useState(false);
  const isUser = msg.role === 'user';

  const copy = () => {
    navigator.clipboard.writeText(msg.content).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    });
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      className={`flex gap-3 ${isUser ? 'flex-row-reverse' : ''}`}
    >
      {/* Avatar */}
      <div className={`w-8 h-8 rounded-full flex-shrink-0 flex items-center justify-center ${
        isUser
          ? 'bg-gradient-to-br from-indigo-500 to-violet-500'
          : 'bg-gradient-to-br from-emerald-500 to-teal-500'
      }`}>
        {isUser ? <User className="w-4 h-4 text-white" /> : <Bot className="w-4 h-4 text-white" />}
      </div>

      {/* Bubble */}
      <div className={`group relative max-w-[78%] ${isUser ? 'items-end' : 'items-start'} flex flex-col`}>
        <div className={`px-4 py-3 rounded-2xl text-sm leading-relaxed ${
          isUser
            ? 'bg-indigo-500/25 border border-indigo-500/30 text-white rounded-tr-sm'
            : 'bg-white/5 border border-white/10 text-white/80 rounded-tl-sm'
        }`}>
          {msg.content}
        </div>
        <div className={`flex items-center gap-2 mt-1 ${isUser ? 'flex-row-reverse' : ''}`}>
          <span className="text-xs text-white/25">
            {msg.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
          </span>
          {!isUser && (
            <button
              onClick={copy}
              className="opacity-0 group-hover:opacity-100 transition-opacity p-0.5 rounded text-white/30 hover:text-white/60"
            >
              {copied ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
            </button>
          )}
        </div>
      </div>
    </motion.div>
  );
}

// ── Page ───────────────────────────────────────────────────────────────────────
export default function AskResearchPage() {
  const [jobId, setJobId] = useState<string | null>(null);
  const [idea, setIdea] = useState('');
  const [loaded, setLoaded] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    const stored = loadLastResearch();
    setJobId(stored?.jobId ?? null);
    setIdea(stored?.idea ?? '');
    setLoaded(true);
  }, []);

  // Auto-scroll to bottom on new messages
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const send = async (question: string) => {
    if (!jobId || !question.trim() || loading) return;

    const userMsg: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: question.trim(),
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      const res = await fetch(`/api/agents/research/${jobId}/ask`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: question.trim() }),
      });

      if (!res.ok) {
        throw new Error(`Error ${res.status}`);
      }

      const data = await res.json();
      const botMsg: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: data.answer ?? 'Sorry, I could not generate an answer.',
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, botMsg]);
    } catch (err) {
      const errMsg: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please make sure the agent service is running.',
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errMsg]);
    } finally {
      setLoading(false);
      inputRef.current?.focus();
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    send(input);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      send(input);
    }
  };

  const clearChat = () => setMessages([]);

  if (!loaded) return null;

  if (!jobId) {
    return (
      <div className="space-y-8 max-w-4xl mx-auto">
        <Header />
        <EmptyResearchState
          title="No research yet"
          description="Run a market research analysis first, then come back here to ask questions about your results."
        />
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      <div className="flex items-start justify-between gap-4">
        <Header />
        {messages.length > 0 && (
          <button
            onClick={clearChat}
            className="flex items-center gap-1.5 text-xs text-white/40 hover:text-white/70 transition-colors mt-2"
          >
            <RefreshCw className="w-3.5 h-3.5" /> Clear
          </button>
        )}
      </div>

      {/* Research context badge */}
      {idea && (
        <div className="flex items-center gap-2 px-3 py-2 rounded-xl bg-indigo-500/10 border border-indigo-500/20 text-sm text-indigo-300 w-fit">
          <Sparkles className="w-4 h-4 flex-shrink-0" />
          <span className="truncate max-w-xs">Analyzing: <strong>{idea}</strong></span>
        </div>
      )}

      {/* Chat area */}
      <GlassCard>
        <GlassCardContent className="p-0">
          {/* Messages */}
          <div className="h-[420px] overflow-y-auto p-5 space-y-5">
            {messages.length === 0 && (
              <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="h-full flex flex-col items-center justify-center text-center">
                <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-indigo-500/20 to-violet-500/20 border border-indigo-500/20 flex items-center justify-center mb-4">
                  <MessageCircle className="w-7 h-7 text-indigo-400" />
                </div>
                <p className="text-sm text-white/40 mb-1">Ask anything about your research</p>
                <p className="text-xs text-white/25">The AI answers strictly from your pipeline results</p>
              </motion.div>
            )}
            <AnimatePresence>
              {messages.map((msg) => (
                <MessageBubble key={msg.id} msg={msg} />
              ))}
            </AnimatePresence>
            {loading && (
              <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex gap-3">
                <div className="w-8 h-8 rounded-full bg-gradient-to-br from-emerald-500 to-teal-500 flex items-center justify-center flex-shrink-0">
                  <Bot className="w-4 h-4 text-white" />
                </div>
                <div className="px-4 py-3 rounded-2xl rounded-tl-sm bg-white/5 border border-white/10 flex items-center gap-2">
                  <Loader2 className="w-4 h-4 text-white/40 animate-spin" />
                  <span className="text-sm text-white/40">Thinking…</span>
                </div>
              </motion.div>
            )}
            <div ref={bottomRef} />
          </div>

          {/* Input form */}
          <div className="border-t border-white/10 p-4">
            <form onSubmit={handleSubmit} className="flex gap-3 items-end">
              <textarea
                ref={inputRef}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Ask about market size, competitors, risks, strategy…"
                rows={1}
                className="flex-1 px-4 py-2.5 rounded-xl bg-white/5 border border-white/10 text-white text-sm placeholder:text-white/25 focus:outline-none focus:border-indigo-500/60 resize-none leading-relaxed"
                style={{ maxHeight: 120, overflowY: 'auto' }}
              />
              <AnimatedButton
                disabled={!input.trim() || loading}
                size="sm"
                className="flex-shrink-0 h-10"
                onClick={handleSubmit as any}
              >
                <Send className="w-4 h-4" />
              </AnimatedButton>
            </form>
            <p className="text-xs text-white/20 mt-2">Enter to send · Shift+Enter for new line</p>
          </div>
        </GlassCardContent>
      </GlassCard>

      {/* Suggested questions */}
      {messages.length === 0 && (
        <GlassCard>
          <GlassCardHeader>
            <div className="flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-indigo-400" />
              <h2 className="text-sm font-semibold text-white">Suggested Questions</h2>
            </div>
          </GlassCardHeader>
          <GlassCardContent>
            <div className="grid sm:grid-cols-2 gap-2">
              {SUGGESTED.map((q, i) => (
                <motion.button
                  key={i}
                  initial={{ opacity: 0, y: 6 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: i * 0.04 }}
                  onClick={() => send(q)}
                  disabled={loading}
                  className="text-left px-4 py-3 rounded-xl bg-white/5 border border-white/10 text-sm text-white/60 hover:text-white hover:border-indigo-500/40 hover:bg-indigo-500/5 transition-all"
                >
                  {q}
                </motion.button>
              ))}
            </div>
          </GlassCardContent>
        </GlassCard>
      )}
    </div>
  );
}

function Header() {
  return (
    <div>
      <h1 className="text-2xl font-bold text-white mb-1">
        Ask Your <span className="bg-gradient-to-r from-indigo-400 to-violet-400 bg-clip-text text-transparent">Research</span>
      </h1>
      <p className="text-white/50 text-sm">Chat with AI about your market research — grounded answers, no hallucination.</p>
    </div>
  );
}
