from flask import Flask, render_template, request, jsonify
import sqlite3
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def get_db():
    return sqlite3.connect("database.db")

def match_score(user_amenities, listing_amenities):
    return len(set(user_amenities) & set(listing_amenities))


def normalize_amenities_list(amenities):
    """Return a list of normalized amenity strings (lowercased, trimmed, mapped, spaces -> hyphens)."""
    AMENITY_ALIASES = {
        "internet": "wifi",
        "wi-fi": "wifi",
        "wi fi": "wifi",
        "pets": "pet-friendly",
        "pet friendly": "pet-friendly",
        "pet-friendly": "pet-friendly",
    }
    normalized = []
    for a in (amenities or []):
        if not isinstance(a, str):
            continue
        a_norm = a.strip().lower()
        # map common aliases
        a_mapped = AMENITY_ALIASES.get(a_norm, a_norm)
        a_mapped = a_mapped.replace(' ', '-')
        if a_mapped:
            normalized.append(a_mapped)
    return normalized


def compute_matchability(listings, wanted_norm=None, budget=None, access_filters=None):
    """Attach a matchability percentage to each listing in-place and return the list.
    wanted_norm: list of normalized wanted amenities (e.g., ['wifi','gym']) or empty/None
    budget: integer budget (or None)
    Algorithm:
      - amenity_score = matched_count / len(wanted_norm) (0..1). If no wanted_norm, amenity_score = 0.
      - price_score = normalized where lower price => higher score. If budget available, use budget-range; else use min/max in listings.
      - combine: if wanted_norm provided, weights amenity=0.6, price=0.4; else 100% price.
      - Convert to integer percent 0..100 and add as listing['matchability']
    """
    if not listings:
        return listings

    prices = [l.get('price') or 0 for l in listings]
    min_price = min(prices)
    max_price = max(prices)
    # avoid zero division
    eps = 1e-6

    for l in listings:
        price = l.get('price') or 0

        # price score: higher for cheaper options relative to range or budget
        if budget:
            denom = max(eps, (budget - min_price))
            # if budget <= min_price then denom small; use fallback to range
            if denom <= eps and max_price > min_price:
                denom = max_price - min_price
            price_score = 1.0 - max(0.0, (price - min_price) / max(denom, eps))
        else:
            denom = max(eps, (max_price - min_price))
            price_score = 1.0 - ((price - min_price) / denom) if denom > eps else 1.0
        price_score = max(0.0, min(1.0, price_score))

        # amenity score
        amenity_score = 0.0
        matched = 0
        if wanted_norm:
            listing_amenities = normalize_amenities_list(l.get('amenities') or [])
            for w in wanted_norm:
                if w in listing_amenities:
                    matched += 1
            amenity_score = matched / len(wanted_norm) if wanted_norm else 0.0

        # accessibility score: average of selected access_scores (normalized 0..1)
        access_score = 0.0
        if access_filters:
            parts = []
            for f in access_filters:
                if f == 'walkable':
                    parts.append((l.get('walkable_score') or 0) / 100.0)
                elif f == 'transit':
                    parts.append((l.get('transit_score') or 0) / 100.0)
                elif f == 'car_friendly':
                    parts.append((l.get('car_score') or 0) / 100.0)
            if parts:
                access_score = sum(parts) / len(parts)

        # Weighting rules
        # If user requested amenities, keep amenity weight high (0.6). The remaining 0.4
        # is split between price and accessibility when accessibility filters are present.
        if wanted_norm:
            amenity_weight = 0.6
            remaining = 0.4
            if access_filters:
                access_total = remaining * 0.5
                price_weight = remaining - access_total
                access_weight = access_total
            else:
                price_weight = remaining
                access_weight = 0.0
        else:
            # No amenities requested: use price mostly; if access filters selected, include them.
            if access_filters:
                price_weight = 0.6
                access_weight = 0.4
            else:
                price_weight = 1.0
                access_weight = 0.0

        score = (amenity_weight * amenity_score if wanted_norm else 0.0) + (price_weight * price_score) + (access_weight * access_score)

        pct = int(round(max(0.0, min(1.0, score)) * 100))
        l['matchability'] = pct

    return listings


TRANSIT_CITIES = {c.lower() for c in [
    "Toronto", "Montreal", "Vancouver", "Calgary", "Edmonton", "Ottawa", "Winnipeg",
    "Quebec City", "Hamilton", "Mississauga", "Brampton", "Surrey", "Laval", "Halifax",
    "London", "Markham", "Vaughan", "Gatineau", "Longueuil", "Burnaby"
]}

WALKABLE_CITIES = {c.lower() for c in ["Toronto", "Montreal", "Vancouver", "Quebec City", "Ottawa", "Halifax", "Winnipeg"]}


def compute_accessibility_flags(listing):
    """Return (walkable, transit, car_friendly) booleans for a listing dict."""
    amenities = normalize_amenities_list(listing.get('amenities') or [])
    loc = (listing.get('location') or '').strip().lower()
    # boolean flags (existing behavior)
    car_friendly = 'parking' in amenities
    transit_bool = loc in TRANSIT_CITIES
    walkable_bool = loc in WALKABLE_CITIES or 'walkable' in amenities

    # Heuristic numeric scoring (0..100)
    # Walkability: high for known walkable cities, slightly boosted by a 'walkable' amenity
    if loc in WALKABLE_CITIES:
        walk_score = 80
    else:
        walk_score = 35
    if 'walkable' in amenities:
        walk_score = min(100, walk_score + 10)
    if 'parking' in amenities:
        # presence of parking slightly lowers pure walkability
        walk_score = max(0, walk_score - 5)

    # Transit accessibility: high for big transit cities; boosted by transit-related amenities
    if loc in TRANSIT_CITIES:
        transit_score = 80
    else:
        transit_score = 20
    if 'transit' in amenities or 'near-transit' in amenities:
        transit_score = min(100, transit_score + 10)
    if 'bus' in amenities or 'subway' in amenities or 'tram' in amenities:
        transit_score = min(100, transit_score + 5)

    # Car mobility: high when parking is available or in less transit-focused cities
    if 'parking' in amenities:
        car_score = 90
    else:
        # if city has strong transit, car mobility may be less necessary
        car_score = 40 if loc in TRANSIT_CITIES else 70
    if 'garage' in amenities or 'covered-parking' in amenities:
        car_score = min(100, car_score + 5)

    # Normalize and attach
    def clamp01(x):
        return max(0, min(100, int(round(x))))

    listing['walkable'] = bool(walkable_bool)
    listing['transit'] = bool(transit_bool)
    listing['car_friendly'] = bool(car_friendly)
    listing['walkable_score'] = clamp01(walk_score)
    listing['transit_score'] = clamp01(transit_score)
    listing['car_score'] = clamp01(car_score)
    return listing

@app.route("/", methods=["GET", "POST"])
def home():
    results = []

    if request.method == "POST":
        budget = int(request.form["budget"])
        location = request.form["location"].lower()
        amenities = request.form.getlist("amenities")
        # normalize user-provided amenities for matching logic
        user_amenities_norm = [a.strip().lower().replace(' ', '-') for a in amenities if a.strip()]

        conn = get_db()
        c = conn.cursor()

        c.execute("""
            SELECT title, price, location, amenities
            FROM listings
            WHERE price <= ? AND LOWER(location) = ?
        """, (budget, location))

        rows = c.fetchall()
        conn.close()

        listings = []
        for r in rows:
            listings.append({
                "title": r[0],
                "price": r[1],
                "location": r[2],
                "amenities": normalize_amenities_list(r[3].split(",")) if r[3] else []
            })
        # compute accessibility scores/flags for each listing so matchability can use them
        for l in listings:
            compute_accessibility_flags(l)
        # If the user requested any amenities, require listings to include ALL requested amenities (strict AND filter)
        if user_amenities_norm:
            def has_all_wanted(listing):
                listing_amenities = listing.get("amenities") or []
                return all(w in listing_amenities for w in user_amenities_norm)

            filtered = [l for l in listings if has_all_wanted(l)]
            if not filtered:
                results = []
            else:
                # compute matchability and sort by it (include selected access filters from form)
                access_filters = []
                if request.form.get('walkable'):
                    access_filters.append('walkable')
                if request.form.get('transit'):
                    access_filters.append('transit')
                if request.form.get('car_friendly'):
                    access_filters.append('car_friendly')
                compute_matchability(filtered, wanted_norm=user_amenities_norm, budget=budget, access_filters=access_filters)
                results = sorted(filtered, key=lambda l: l.get('matchability', 0), reverse=True)
        else:
            access_filters = []
            if request.form.get('walkable'):
                access_filters.append('walkable')
            if request.form.get('transit'):
                access_filters.append('transit')
            if request.form.get('car_friendly'):
                access_filters.append('car_friendly')
            compute_matchability(listings, wanted_norm=user_amenities_norm, budget=budget, access_filters=access_filters)
            results = sorted(listings, key=lambda l: l.get('matchability', 0), reverse=True)

    return render_template("index.html", results=results)


@app.route("/api/listings", methods=["GET"])
def api_listings():
    # optional query params: budget, location, amenities (comma-separated)
    budget = request.args.get("budget", type=int)
    location = request.args.get("location", default=None, type=str)
    amenities_q = request.args.get("amenities", default=None, type=str)

    params = []
    where = []

    if budget is not None:
        where.append("price <= ?")
        params.append(budget)
    if location:
        where.append("LOWER(location) = ?")
        params.append(location.lower())

    q = "SELECT title, price, location, amenities FROM listings"
    if where:
        q += " WHERE " + " AND ".join(where)

    conn = get_db()
    c = conn.cursor()
    c.execute(q, tuple(params))
    rows = c.fetchall()
    conn.close()

    listings = []
    for r in rows:
        listings.append({
            "title": r[0],
            "price": r[1],
            "location": r[2],
            "amenities": normalize_amenities_list(r[3].split(",")) if r[3] else []
        })

    # compute accessibility flags for each listing
    for l in listings:
        compute_accessibility_flags(l)

    # support additional boolean query params: walkable, transit, car_friendly
    walkable_q = request.args.get('walkable')
    transit_q = request.args.get('transit')
    car_q = request.args.get('car_friendly')

    def parse_bool(v):
        if v is None:
            return None
        return v.lower() in ('1', 'true', 'yes', 'on')

    walkable_filter = parse_bool(walkable_q)
    transit_filter = parse_bool(transit_q)
    car_filter = parse_bool(car_q)

    if walkable_filter is not None:
        listings = [l for l in listings if l.get('walkable') == walkable_filter]
    if transit_filter is not None:
        listings = [l for l in listings if l.get('transit') == transit_filter]
    if car_filter is not None:
        listings = [l for l in listings if l.get('car_friendly') == car_filter]

    # If amenities query present, handle pet-friendly as a strict filter
    wanted_norm = None
    if amenities_q:
        wanted = [a.strip() for a in amenities_q.split(",") if a.strip()]
        wanted_norm = [a.strip().lower().replace(' ', '-') for a in wanted]

        def has_all_wanted_api(listing):
            listing_amenities = listing.get("amenities") or []
            return all(w in listing_amenities for w in wanted_norm)

        filtered = [l for l in listings if has_all_wanted_api(l)]
        if not filtered:
            listings = []
        else:
            listings = filtered

    # Always compute matchability and sort by it before returning
    access_filters = []
    if walkable_filter:
        access_filters.append('walkable')
    if transit_filter:
        access_filters.append('transit')
    if car_filter:
        access_filters.append('car_friendly')

    compute_matchability(listings, wanted_norm=wanted_norm, budget=budget, access_filters=access_filters)
    listings = sorted(listings, key=lambda l: l.get('matchability', 0), reverse=True)

    return jsonify(listings)

if __name__ == "__main__":
    import os
    port = int(os.environ.get('PORT', 5001))
    host = os.environ.get('HOST', '127.0.0.1')
    print(f"Starting Flask app on {host}:{port}")
    app.run(debug=True, host=host, port=port)
