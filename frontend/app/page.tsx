'use client';

import { AnimatedBackground } from '@/components/landing/animated-background';
import { Navbar } from '@/components/landing/navbar';
import { HeroSection } from '@/components/landing/hero-section';
import { TrustedBySection } from '@/components/landing/features-section';
import { FeaturesSection } from '@/components/landing/features-section';
import { WorkflowSection } from '@/components/landing/workflow-section';
import { DashboardPreviewSection } from '@/components/landing/dashboard-preview-section';
import { AIAgentSection } from '@/components/landing/ai-agent-section';
import { HealthcareSection } from '@/components/landing/healthcare-section';
import { CTASection } from '@/components/landing/cta-section';
import { Footer } from '@/components/landing/footer';

export default function HomePage() {
  return (
    <main className="relative min-h-screen">
      <AnimatedBackground />
      <Navbar />
      <HeroSection />
      <TrustedBySection />
      <FeaturesSection />
      <WorkflowSection />
      <DashboardPreviewSection />
      <AIAgentSection />
      <HealthcareSection />
      <CTASection />
      <Footer />
    </main>
  );
}
