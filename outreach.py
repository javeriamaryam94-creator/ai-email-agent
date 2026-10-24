import sys
print("DEBUG: Python runtime started successfully!", flush=True)

import os
import json
import datetime
import traceback
import google.generativeai as genai

print("DEBUG: Imports completed.", flush=True)

# 1. Configure Gemini API Key
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY environment variable is missing!")

genai.configure(api_key=api_key)
print("DEBUG: Gemini configured successfully.", flush=True)

# Prospect Database with Buyer Intent & Tracking States
prospects = [
    {
        "company": "Global Spice & Minerals Inc.",
        "contact_name": "Sarah Jenkins",
        "email": "sarah.jenkins@example-importer.com",
        "market": "North America",
        "buyer_interest": "Looking for food-grade Himalayan pink salt crystals and organic turmeric in bulk.",
        "status": "Pending Initial Outreach",
        "follow_up_count": 0
    },
    {
        "company": "EuroFood Trade GmbH",
        "contact_name": "Lukas Weber",
        "email": "lukas.weber@example-trade.de",
        "market": "Europe",
        "buyer_interest": "Sourcing ethically harvested gourmet salt slabs and chemical-free spices.",
        "status": "Pending Initial Outreach",
        "follow_up_count": 0
    }
]


def generate_pitch(prospect):
    """Generates an executive B2B pitch with built-in error handling."""
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        prompt = f"""
        You are the Head of International Trade at Indus Export Hub, a premier direct exporter of Himalayan Pink Salt and Organic Spices from Pakistan.
        Write a professional, compelling B2B cold outreach email to a prospective buyer.

        Buyer Details:
        - Company: {prospect['company']}
        - Contact Name: {prospect['contact_name']}
        - Market: {prospect['market']}
        - Requirements: {prospect['buyer_interest']}

        Our Direct Contact Info:
        - Phone/WhatsApp: +92 3136125836
        - Official Trade Email: heshi.pvt@gmail.com

        Keep the tone executive, highlight direct-from-source pricing and flexible container shipments. Sign off as Indus Export Hub Team.
        """
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"⚠️ API warning for {prospect['company']}: {e}. Using professional fallback template.")
        return f"""Dear {prospect['contact_name']},

We hope this email finds you well at {prospect['company']}.

As a leading direct exporter of premium Himalayan Pink Salt and organic spices from Pakistan through Indus Export Hub, we specialize in meeting high-volume import demands with rigorous quality assurance and competitive source pricing.

We would love to discuss how we can support your upcoming supply requirements in {prospect['market']}. You can reach us directly via WhatsApp at +92 3136125836 or reply to this email at heshi.pvt@gmail.com.

Best regards,
Indus Export Hub Team
"""


def run_campaign():
    print("🚀 Starting Indus Export Hub Autonomous Email & Tracking System...", flush=True)
    campaign_results = []

    for prospect in prospects:
        print(f"🔄 Processing outreach for {prospect['company']}...", flush=True)
        email_body = generate_pitch(prospect)

        prospect["status"] = "Initial Pitch Drafted"
        prospect["last_contact"] = str(datetime.date.today())
        prospect["follow_up_count"] += 1

        campaign_results.append({
            "company": prospect["company"],
            "contact_name": prospect["contact_name"],
            "recipient": prospect["email"],
            "status": prospect["status"],
            "last_contact": prospect["last_contact"],
            "follow_up_count": prospect["follow_up_count"],
            "email_content": email_body
        })
        print(f"✅ Successfully processed {prospect['company']}.\n", flush=True)

    output_file = "campaign_results.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(campaign_results, f, indent=4)

    print(f"📁 Campaign tracking state saved successfully to {output_file}", flush=True)


if __name__ == "__main__":
    run_campaign()
