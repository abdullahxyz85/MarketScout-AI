"use client";

import Link from "next/link";
import { Logo } from "@/components/ui/logo";

const footerLinks: Record<string, string[]> = {};

export function Footer() {
  return (
    <footer className="border-t border-white/10 bg-black/25 backdrop-blur-xl">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-10">
        <div className="flex flex-col gap-6 lg:flex-row lg:items-center lg:justify-between">
          <div className="flex items-center gap-4">
            <Link href="/" className="shrink-0">
              <Logo size={32} />
            </Link>
            <p className="max-w-sm text-sm text-white/50 leading-6">
              Autonomous AI agents transforming startup ideas into actionable
              market intelligence.
            </p>
          </div>

          <div className="flex flex-wrap items-start gap-x-10 gap-y-4">
            {Object.entries(footerLinks).map(([category, links]) => (
              <div key={category} className="min-w-[110px]">
                <h3 className="text-xs font-semibold uppercase tracking-[0.2em] text-white/60 mb-3">
                  {category}
                </h3>
                <ul className="space-y-2">
                  {links.map((link) => (
                    <li key={link}>
                      <Link
                        href="#"
                        className="text-sm text-white/50 hover:text-white transition-colors"
                      >
                        {link}
                      </Link>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>

          <p className="text-sm text-white/40 lg:text-right">
            2026 MarketScout AI. All rights reserved.
          </p>
        </div>
      </div>
    </footer>
  );
}
