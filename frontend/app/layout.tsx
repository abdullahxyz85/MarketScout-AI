import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  metadataBase: new URL("https://marketscout.ai"),
  title: "MarketScout AI - Autonomous AI Market Intelligence Platform",
  description:
    "Transform any startup idea into a complete market intelligence report using autonomous AI agents. Powered by advanced multi-agent AI systems.",
  keywords: [
    "AI",
    "Market Intelligence",
    "Startup",
    "Research",
    "Analysis",
    "Competitor Analysis",
    "SWOT",
  ],
  authors: [{ name: "MarketScout AI" }],
  creator: "MarketScout AI",
  openGraph: {
    type: "website",
    locale: "en_US",
    url: "https://marketscout.ai",
    title: "MarketScout AI - Autonomous AI Market Intelligence",
    description:
      "Transform any startup idea into a complete market intelligence report using autonomous AI agents.",
    siteName: "MarketScout AI",
    images: [
      {
        url: "https://bolt.new/static/og_default.png",
        width: 1200,
        height: 630,
      },
    ],
  },
  twitter: {
    card: "summary_large_image",
    title: "MarketScout AI - Autonomous AI Market Intelligence",
    description:
      "Transform any startup idea into a complete market intelligence report using autonomous AI agents.",
    images: ["https://bolt.new/static/og_default.png"],
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="font-sans antialiased">
        {children}
      </body>
    </html>
  );
}
