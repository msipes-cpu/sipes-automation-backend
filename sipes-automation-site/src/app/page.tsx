import { Navbar } from "@/components/Navbar";
import { Hero } from "@/components/Hero";
import { Services } from "@/components/Services";
import { VideoSection } from "@/components/VideoSection";
import { Results } from "@/components/Results";
import { ROICalculator } from "@/components/ROICalculator";
import { FAQ } from "@/components/FAQ";
import { LogoTicker } from "@/components/LogoTicker";
import { Comparison } from "@/components/Comparison";
import { Process } from "@/components/Process";
import { StickyCTA } from "@/components/StickyCTA";
import { CommonAutomations } from "@/components/CommonAutomations";
import { SlideInLeadMagnet } from "@/components/SlideInLeadMagnet";
import { Portfolio } from "@/components/Portfolio";

export default function Home() {
  return (
    <main className="bg-white min-h-screen text-zinc-900 selection:bg-blue-100 selection:text-blue-900">
      <Navbar />
      <Hero />
      <LogoTicker />
      <VideoSection />
      <Results />
      <Portfolio />
      <CommonAutomations />
      <Services />
      <Comparison />
      <Process />
      <ROICalculator />
      <FAQ />
      <StickyCTA />
      <SlideInLeadMagnet />

      {/* Footer */}
      <footer className="py-12 border-t border-zinc-100 text-center text-zinc-500 text-sm bg-zinc-50">
        <div className="max-w-7xl mx-auto px-6 flex flex-col md:flex-row items-center justify-between gap-4">
          <p>© {new Date().getFullYear()} Sipes Automation. All rights reserved.</p>
          <p className="flex items-center gap-2">
            <span>Built in 48 hours.</span>
            <span className="w-1.5 h-1.5 bg-green-500 rounded-full animate-pulse"></span>
          </p>
        </div>
      </footer>
    </main>
  );
}
