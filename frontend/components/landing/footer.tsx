'use client';

import Link from 'next/link';
import { Logo } from '@/components/ui/logo';

const footerLinks = {
  Product: ['Features', 'Pricing', 'Dashboard', 'API'],
};

export function Footer() {
  return (
    <footer className="border-t border-white/10 bg-black/20 backdrop-blur-xl">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-8">
          <div className="col-span-2">
            <Link href="/" className="mb-4">
              <Logo size={32} />
            </Link>
            <p className="text-sm text-white/50 mb-6 max-w-xs">
              Autonomous AI agents transforming startup ideas into actionable market intelligence.
            </p>
          </div>

          {Object.entries(footerLinks).map(([category, links]) => (
            <div key={category}>
              <h3 className="text-sm font-semibold text-white mb-4">{category}</h3>
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

          <p className="col-span-2 md:col-span-1 lg:col-span-3 self-center text-right text-sm text-white/40 whitespace-nowrap">
            2026 MarketScout AI. All rights reserved.
          </p>
        </div>
      </div>
    </footer>
  );
}
