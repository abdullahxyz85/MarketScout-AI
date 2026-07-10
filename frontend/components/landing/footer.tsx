"use client";

import Link from "next/link";
import { Logo } from "@/components/ui/logo";

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

          <p className="text-sm text-white/40 lg:text-right">
            2026 MarketScout AI. All rights reserved.
          </p>
        </div>
      </div>
    </footer>
  );
}
