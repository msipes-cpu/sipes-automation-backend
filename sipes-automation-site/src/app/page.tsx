import { Navbar } from "@/components/Navbar";
import { Hero } from "@/components/Hero";
import { Services } from "@/components/Services";
import { VideoSection } from "@/components/VideoSection";
import { Results } from "@/components/Results";
import { Testimonials } from "@/components/Testimonials";
import { ROICalculator } from "@/components/ROICalculator";
import { FAQ } from "@/components/FAQ";
import { LogoTicker } from "@/components/LogoTicker";
import { Comparison } from "@/components/Comparison";
import { Process } from "@/components/Process";
import { StickyCTA } from "@/components/StickyCTA";
import { CommonAutomations } from "@/components/CommonAutomations";
import { SlideInLeadMagnet } from "@/components/SlideInLeadMagnet";
import { Portfolio } from "@/components/Portfolio";
import { Footer } from "@/components/Footer";

export default function Home() {
  return (
    <main className="bg-white min-h-screen text-zinc-900 selection:bg-blue-100 selection:text-blue-900">
      <Navbar />
      <Hero />
      <LogoTicker />
      <VideoSection />
      <Results />
      <Testimonials />
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
      <Footer />
    </main>
  );
}
