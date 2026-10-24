import os
import json
from google import genai
from google.genai import types

# Initialize the Gemini client using the environment variable injected by GitHub Actions
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

# Sample database of leads
TARGET_LEADS = [
    {
        "name": "John",
        "company": "Global Spice Importers LLC",
        "industry": "Food Distribution & Retail",
        "notes": "Looking for reliable bulk pink salt and organic spices with consistent supply chains."
    },
    {
        "name": "Sarah",
        "company": "Nordic Gourmet Foods",
        "industry": "European Specialty Grocery",
        "notes": "Interested in sustainable sourcing, eco-friendly packaging, and premium pink salt lamps."
    }
]

def generate_custom_outreach(lead):
    """
    Uses Gemini to research, structure, and write a hyper-personalized professional outreach email.
    """
    prompt = f"""
    You are an expert B2B export and technical sales copywriter for a Pakistani salt and spice export venture. 
    Your goal is to write a highly professional, short, and compelling cold outreach email.
    
    Target Recipient Details:
    - Name: {lead['name']}
    - Company: {lead['company']}
    - Industry: {lead['industry']}
    - Specific Context/Notes: {lead['notes']}
    
    Sender Offering:
    - Premium quality pink salt and authentic spice exports from Pakistan, direct sourcing, strict quality control, reliability, and custom private labeling.
    
    Email Best Practices to Follow:
    1. Subject Line: Keep it 3 to 6 words, lowercase or sentence case, specific, natural, and free of hype words.
    2. Opening Line: Make it about *them* and their business/industry challenges, not about us.
    3. Body: Concise (50 to 120 words), focusing on value, reliability, and direct sourcing.
    4. Call to Action (CTA): End with one easy, low-friction question (e.g., "Open to seeing a sample catalog?").
    5. Tone: Professional, respectful, consultative, and warm.
    
    Output Format:
    Return the response strictly in the following format:
    SUBJECT: [Generated Subject Line]
    BODY:
    [Generated Email Body]
    """

    print(f"-> Generating tailored outreach for {lead['name']} at {lead['company']}...")

    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
    )
    
    return response.text

def run_campaign():
    campaign_log = []
    
    print("🚀 Starting Autonomous B2B Outreach Campaign...\n")
    
    for lead in TARGET_LEADS:
        email_content = generate_custom_outreach(lead)
        
        # Save record for tracking / logging
        campaign_log.append({
            "recipient": lead['name'],
            "company": lead['company'],
            "generated_pitch": email_content,
            "status": "Drafted & Ready"
        })
        print(f"Successfully generated pitch for {lead['name']}\n" + "-"*40)

    # Save the run results to a log file
    with open("campaign_results.json", "w") as f:
        json.dump(campaign_log, f, indent=4)
        
    print("✅ Campaign batch complete! Results saved to campaign_results.json")

if __name__ == "__main__":
    run_campaign()
