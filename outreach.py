
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
