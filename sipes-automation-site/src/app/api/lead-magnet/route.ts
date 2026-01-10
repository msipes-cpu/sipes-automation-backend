import { NextResponse } from "next/server";
import { Resend } from "resend";
import { createClient } from "@supabase/supabase-js";

// Initialize clients (will fail gracefully if keys missing)
const resend = process.env.RESEND_API_KEY ? new Resend(process.env.RESEND_API_KEY) : null;
const supabase = (process.env.NEXT_PUBLIC_SUPABASE_URL && process.env.SUPABASE_SERVICE_ROLE_KEY)
    ? createClient(process.env.NEXT_PUBLIC_SUPABASE_URL, process.env.SUPABASE_SERVICE_ROLE_KEY)
    : null;

export async function POST(req: Request) {
    try {
        const { email } = await req.json();

        if (!email) {
            return NextResponse.json({ error: "Email is required" }, { status: 400 });
        }

        // 1. Save to Supabase (if configured)
        if (supabase) {
            await supabase.from("leads").insert([{ email, source: "lead_magnet_v1" }]);
        }

        // 2. Send Email via Resend (if configured)
        if (resend) {
            await resend.emails.send({
                from: "Sipes Automation <onboarding@mail.sipesautomation.com>",
                to: email,
                subject: "Your $50k Capacity Checklist",
                html: `
          <div style="font-family: sans-serif; max-w: 600px; margin: 0 auto;">
            <h1>Open Your $50k Capacity Checklist 🔓</h1>
            <p>You requested the <strong>50 Ways to Add $50k Capacity</strong> checklist.</p>
            <p>We've compiled it into a secret vault page for you (no PDF download needed).</p>
            <br/>
            <a href="https://sipesautomation.com/resources/50-ways" style="background: #2563EB; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; font-weight: bold;">
              Access The Vault
            </a>
            <br/><br/>
            <p>Don't share this link.</p>
            <p>- Michael Sipes</p>
          </div>
        `
            });
        }

        console.log(`Lead Captured: ${email}`);

        return NextResponse.json({ success: true, message: "Lead captured" });

    } catch (error) {
        console.error("Lead capture error:", error);
        return NextResponse.json({ error: "Internal Server Error" }, { status: 500 });
    }
}
