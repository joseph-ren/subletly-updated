import sqlite3
import json
from dotenv import load_dotenv
import os
import google.genai as genai
import argparse

# --- Load API key ---
load_dotenv()
API_KEY = os.getenv("API_KEY")

if not API_KEY:
    print("Warning: API_KEY not found in .env — will use synthetic generation fallback")
    API_KEY = None

# --- Configure Gemini (only if API key available) ---
client = genai.Client(api_key=API_KEY) if API_KEY else None

PROMPT = """
Generate realistic student sublet listings across the following major Canadian cities.

Cities (choose locations only from this list):
Toronto, Montreal, Vancouver, Calgary, Edmonton, Ottawa, Winnipeg, Quebec City, Hamilton, Mississauga, Brampton, Surrey, Laval, Halifax, London, Markham, Vaughan, Gatineau, Longueuil, Burnaby

Rules:
- price between 500 and 1200 (CAD)
- realistic student-style titles (mention neighbourhoods or proximity to universities when appropriate)
- amenities chosen from: wifi, parking, pool, gym, pet-friendly
- when appropriate, include accessibility hints in the amenities such as 'walkable', 'near-transit', 'parking' so the backend accessibility heuristics can pick them up

Return ONLY valid JSON: an array of objects like {"title":..., "price":..., "location":..., "amenities": [...]}
"""

# --- CLI / dry-run support ---
parser = argparse.ArgumentParser(description="Generate sample listings (optionally dry-run)")
parser.add_argument("--dry-run", action="store_true", help="Don't call the API or write to the DB; print sanitized listings")
args = parser.parse_args()

SAMPLE_JSON = json.dumps([
    {"title": "Cozy room near campus", "price": 750, "location": "Toronto", "amenities": ["Wi-Fi", "parking", "pets"]},
    {"title": "Spacious sublet downtown", "price": 950, "location": "Vancouver", "amenities": ["internet", "pool"]},
    {"title": "Furnished studio by campus", "price": 1200, "location": "Calgary", "amenities": ["Gym", "pet friendly"]}
], indent=2)

print("Generating listings... (AI if available; otherwise synthetic)")

if args.dry_run:
    print("Dry-run mode: skipping AI call and using sample JSON.")
    ai_text = SAMPLE_JSON
else:
    if client:
        try:
            response = client.models.generate_content(model="gemini-3-flash-preview", contents=PROMPT)
            ai_text = response.text.strip()
            print("AI Response received")
        except Exception as e:
            print("AI call failed — falling back to synthetic sample:", e)
            ai_text = SAMPLE_JSON
    else:
        ai_text = SAMPLE_JSON

# --- Convert AI output to Python list ---
try:
    listings = json.loads(ai_text)
except json.JSONDecodeError:
    print("Gemini returned bad JSON:")
    print(ai_text)
    exit()

# Ensure we work with the expected number of listings from the model
DESIRED_COUNT = 200
if isinstance(listings, list):
    if len(listings) > DESIRED_COUNT:
        print(f"Gemini returned {len(listings)} listings; trimming to {DESIRED_COUNT}.")
        listings = listings[:DESIRED_COUNT]
    elif len(listings) < DESIRED_COUNT:
        print(f"Warning: Gemini returned only {len(listings)} listings; expected {DESIRED_COUNT}.")

# --- sanitize amenities to allowed set ---
ALLOWED_AMENITIES = {"wifi", "parking", "pool", "gym", "pet-friendly"}
# common aliases the model might use
AMENITY_ALIASES = {
    "internet": "wifi",
    "wi-fi": "wifi",
    "wi fi": "wifi",
    "pets": "pet-friendly",
    "pet friendly": "pet-friendly",
    "pet-friendly": "pet-friendly",
}

# ensure we actually have a list
if not isinstance(listings, list):
    print("Expected a JSON array of listings, got:")
    print(type(listings), listings)
    exit(1)
# Allow extra hint tokens to survive sanitization (walkable, near-transit)
EXTRA_HINTS = {"walkable", "near-transit"}

# Cities list (same as prompt)
CITIES = [
    "Toronto", "Montreal", "Vancouver", "Calgary", "Edmonton", "Ottawa", "Winnipeg",
    "Quebec City", "Hamilton", "Mississauga", "Brampton", "Surrey", "Laval", "Halifax",
    "London", "Markham", "Vaughan", "Gatineau", "Longueuil", "Burnaby"
]

# Accessibility combinations to cover (walkable, transit, car_friendly)
ACCESS_COMBOS = [(w, t, c) for w in (False, True) for t in (False, True) for c in (False, True)]

import random

def synthesize_listing(city, combo, idx):
    w, t, cflag = combo
    title = f"Auto-generated room #{idx} in {city}"
    price = random.randint(500, 1200)
    amenities = []
    if cflag:
        amenities.append('parking')
    if w:
        amenities.append('walkable')
    if t:
        amenities.append('near-transit')
    # add a random allowed amenity to diversify
    # choose extra amenity but avoid adding 'parking' if cflag is False
    possible_extras = list(ALLOWED_AMENITIES)
    if not cflag and 'parking' in possible_extras:
        possible_extras.remove('parking')
    extra = random.choice(possible_extras)
    if extra not in amenities:
        amenities.append(extra)
    return {"title": title, "price": price, "location": city, "amenities": amenities}

# First sanitize whatever we got from AI so far, but allow extra hints
for l in listings:
    raw = l.get("amenities") or []
    sanitized = []
    for a in raw:
        a_norm = a.strip().lower()
        a_mapped = AMENITY_ALIASES.get(a_norm, a_norm)
        a_mapped = a_mapped.replace(' ', '-')
        if a_mapped in ALLOWED_AMENITIES or a_mapped in EXTRA_HINTS:
            sanitized.append(a_mapped)
    l["amenities"] = sanitized


# Build a guaranteed-coverage list: one synth per city × access-combo
final_listings = []
idx = 0
for city in CITIES:
    for combo in ACCESS_COMBOS:
        idx += 1
        final_listings.append(synthesize_listing(city, combo, idx))

# Append AI-provided listings if they don't duplicate the same city/combo
def combo_key_from_listing(l):
    a = set(l.get('amenities', []))
    return (l.get('location'), 'walkable' in a, 'near-transit' in a, 'parking' in a)

existing_keys = {combo_key_from_listing(l) for l in final_listings}
for l in listings:
    key = combo_key_from_listing(l)
    if key not in existing_keys:
        idx += 1
        final_listings.append(l)
        existing_keys.add(key)

# Pad with random synthesized listings until DESIRED_COUNT
while len(final_listings) < DESIRED_COUNT:
    idx += 1
    city = random.choice(CITIES)
    combo = random.choice(ACCESS_COMBOS)
    final_listings.append(synthesize_listing(city, combo, idx))

# Trim to desired count
if len(final_listings) > DESIRED_COUNT:
    final_listings = final_listings[:DESIRED_COUNT]

# Replace listings with the final set
listings = final_listings

# Final sanitize pass (ensure only allowed tokens and hints remain)
for l in listings:
    raw = l.get("amenities") or []
    sanitized = []
    for a in raw:
        a_norm = a.strip().lower()
        a_mapped = AMENITY_ALIASES.get(a_norm, a_norm)
        a_mapped = a_mapped.replace(' ', '-')
        if a_mapped in ALLOWED_AMENITIES or a_mapped in EXTRA_HINTS:
            sanitized.append(a_mapped)
    l["amenities"] = sanitized

# After sanitizing all listings, either print (dry-run) or write to DB
if args.dry_run:
    print("Sanitized listings (dry-run):")
    print(json.dumps(listings, indent=2))
else:
    # --- Insert into SQLite DB ---
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    for l in listings:
        amenities_str = ",".join(l["amenities"])
        c.execute(
            "INSERT INTO listings (title, price, location, amenities) VALUES (?, ?, ?, ?)",
            (l["title"], l["price"], l["location"], amenities_str)
        )

    conn.commit()
    conn.close()

    print(f"Inserted {len(listings)} generated listings!")
