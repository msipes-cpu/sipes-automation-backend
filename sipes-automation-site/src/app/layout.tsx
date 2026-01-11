import type { Metadata } from "next";
import { Inter, Space_Grotesk, JetBrains_Mono } from "next/font/google";
import "./globals.css";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter"
});

const spaceGrotesk = Space_Grotesk({
  subsets: ["latin"],
  variable: "--font-space-grotesk"
});

const jetbrainsMono = JetBrains_Mono({
  subsets: ["latin"],
  variable: "--font-jetbrains-mono"
});

export const metadata: Metadata = {
  metadataBase: new URL('https://www.sipesautomation.com'),
  title: {
    default: "Sipes Automation | Add $50k Capacity Without Hiring",
    template: "%s | Sipes Automation",
  },
  description: "We guarantee agencies add $50k+ in monthly capacity in 30 days without hiring new staff. Deployed in 48 hours or we pay you $5,000.",
  keywords: ["Agency Automation", "Marketing Agency Systems", "Lead Gen Automation", "Operations Automation", "Make.com Experts", "Zapier Consultants"],
  openGraph: {
    title: "Sipes Automation | Scale Your Agency Without Hiring",
    description: "Add $50k+ in monthly capacity in 30 days. We build automated systems for high-growth agencies.",
    url: 'https://www.sipesautomation.com',
    siteName: 'Sipes Automation',
    locale: 'en_US',
    type: 'website',
  },
  twitter: {
    card: 'summary_large_image',
    title: "Sipes Automation | Agency Operations Experts",
    description: "Add $50k+ in monthly capacity in 30 days without hiring new staff.",
    creator: '@michaelsipes', // Assuming handle, can be updated
  },
  robots: {
    index: true,
    follow: true,
  },
  icons: {
    icon: '/favicon.ico',
    shortcut: '/favicon.ico',
    apple: '/apple-icon.png',
  },
};

import { PostHogProvider } from "@/providers/PostHogProvider";

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${inter.variable} ${spaceGrotesk.variable} ${jetbrainsMono.variable} antialiased`}
      >
        <PostHogProvider>
          {children}
        </PostHogProvider>
      </body>
    </html>
  );
}
