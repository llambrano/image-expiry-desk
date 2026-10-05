#!/usr/bin/env python3
"""
Generate a fully synthetic dataset for the Image Expiry Desk demo.

Everything this script writes is invented: the hotel group ("Northvale Hotel
Group"), its brands, properties, owners, operators, people, asset IDs and URLs.
Asset URLs point at example.com, a domain reserved for documentation.

Outputs
  data/reference/property_master.csv          hotel dimension table
  data/raw/<year>/<YYYY MM DD> - image_expiry_report.xlsx
                                              one file per report run
  data/raw/2025/..._resend.xlsx               a duplicate report, detected and
                                              skipped by the pipeline

The raw reports deliberately contain the same kinds of defects a real DAM
export has, so the cleaning pipeline has something to do:
  * a "Preview" column that is just the text "Click Here"
  * property codes in mixed case, and multi-property bundles ("abc, xyz")
  * brand slugs that drift between spellings
  * literal spaces in some asset URLs
  * assets served from internal / staging hosts
  * property codes that are missing from the master
  * a property that is renamed partway through the history
  * assets already expired on the day the report was issued

Run:  python scripts/generate_synthetic_data.py   (deterministic, seed 7)
"""
from __future__ import annotations
import random, string
from datetime import date, timedelta
from pathlib import Path
import pandas as pd

SEED = 7
rng = random.Random(SEED)

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
REF = ROOT / "data" / "reference"

# --------------------------------------------------------------------------
# Fictional brand architecture
#   name, report slug, drift slug (alternate spelling seen in some reports),
#   category, weight in portfolio, share of properties enrolled in the DAM
#   expiry pipeline (low for select service & all-inclusive on purpose)
# --------------------------------------------------------------------------
BRANDS = [
    ("Northvale Grand",         "grand",     "northvalegrand", "Full Service",   .10, .75),
    ("Northvale Hotels",        "northvale", None,             "Full Service",   .20, .55),
    ("Kestrel Reserve",         "kestrel",   None,             "Luxury",         .05, .80),
    ("Lumen Hotels",            "lumen",     "lumenhotels",    "Lifestyle",      .07, .70),
    ("The Archive Collection",  "archive",   None,             "Lifestyle",      .07, .65),
    ("Vale Place",              "place",     None,             "Select Service", .23, .22),
    ("Vale House",              "house",     None,             "Select Service", .10, .18),
    ("Tidewater Resorts",       "tidewater", "tidewaters",     "All Inclusive",  .12, .08),
    ("Solace Retreats",         "solace",    None,             "Wellness",       .02, .90),
    ("Northvale Vacation Club", "club",      None,             "Timeshare",      .04, .45),
]

DIVISIONS = {
    "Americas": [
        ("United States", ["New York", "Chicago", "Austin", "Denver", "Seattle",
         "Boston", "Atlanta", "Nashville", "Phoenix", "San Diego", "Miami",
         "Orlando", "Dallas", "Houston", "Portland", "Minneapolis", "Charlotte",
         "Savannah", "Santa Fe", "Honolulu", "Scottsdale", "Napa", "Tampa",
         "Baltimore", "Pittsburgh", "Salt Lake City", "Kansas City", "Raleigh",
         "Richmond", "Sacramento", "Anchorage", "Boise", "Louisville",
         "Milwaukee", "Tucson", "Albuquerque", "Omaha", "St. Louis"]),
        ("Canada", ["Toronto", "Vancouver", "Montreal", "Calgary", "Ottawa"]),
        ("Mexico", ["Cancun", "Mexico City", "Los Cabos", "Guadalajara", "Tulum"]),
        ("Brazil", ["Sao Paulo", "Rio de Janeiro"]),
        ("Costa Rica", ["Guanacaste"]), ("Dominican Republic", ["Punta Cana"]),
        ("Jamaica", ["Montego Bay"]), ("Chile", ["Santiago"]),
        ("Colombia", ["Cartagena", "Medellin"]), ("Peru", ["Lima"]),
    ],
    "EMEA": [
        ("United Kingdom", ["London", "Edinburgh", "Manchester"]),
        ("France", ["Paris", "Nice", "Lyon"]), ("Germany", ["Berlin", "Munich", "Hamburg"]),
        ("Spain", ["Madrid", "Barcelona", "Mallorca", "Malaga"]),
        ("Italy", ["Rome", "Milan", "Florence", "Venice"]),
        ("Portugal", ["Lisbon", "Porto"]), ("Netherlands", ["Amsterdam"]),
        ("Switzerland", ["Zurich", "Geneva"]), ("Greece", ["Athens", "Mykonos"]),
        ("United Arab Emirates", ["Dubai", "Abu Dhabi"]), ("Qatar", ["Doha"]),
        ("Saudi Arabia", ["Riyadh", "Jeddah"]), ("Egypt", ["Cairo"]),
        ("Morocco", ["Marrakech"]), ("South Africa", ["Cape Town"]),
        ("Turkey", ["Istanbul"]), ("Ireland", ["Dublin"]),
    ],
    "APAC": [
        ("Japan", ["Tokyo", "Kyoto", "Osaka", "Niseko"]),
        ("China", ["Shanghai", "Beijing", "Shenzhen", "Chengdu", "Hangzhou", "Sanya"]),
        ("India", ["Mumbai", "Delhi", "Bengaluru", "Goa"]),
        ("Australia", ["Sydney", "Melbourne", "Brisbane", "Perth"]),
        ("Singapore", ["Singapore"]), ("Thailand", ["Bangkok", "Phuket"]),
        ("Indonesia", ["Bali", "Jakarta"]), ("Vietnam", ["Da Nang", "Hanoi"]),
        ("South Korea", ["Seoul", "Busan"]), ("New Zealand", ["Auckland", "Queenstown"]),
        ("Philippines", ["Manila"]), ("Malaysia", ["Kuala Lumpur"]),
    ],
}
DIV_WEIGHT = {"Americas": .55, "EMEA": .24, "APAC": .21}

SUFFIX = {"Northvale Grand": "", "Northvale Hotels": "", "Kestrel Reserve": "",
          "Lumen Hotels": "", "The Archive Collection": "",
          "Vale Place": "", "Vale House": "",
          "Tidewater Resorts": " Resort", "Solace Retreats": "", "Northvale Vacation Club": ""}
AREA = ["Downtown", "Airport", "Riverfront", "Harbor", "Old Town", "Midtown",
        "Convention Center", "Beach", "Central", "Uptown", "Waterfront", "North"]
ARCHIVE_NAMES = ["The Linden", "Hotel Marisol", "The Foundry", "Casa Albera",
                 "The Ledger House", "Hotel Wren", "The Cordage", "Villa Serin",
                 "The Printworks", "Hotel Ostara", "The Tannery", "Maison Lyre",
                 "The Signal", "Hotel Juniper", "The Mercer Yard", "Palazzo Fenn"]

# Invented companies - checked to read as obviously fictional.
OPERATORS_3P = ["Aldermoor Hospitality", "Quillfield Hotel Management",
                "Sableridge Hotel Partners", "Tamsin Lodging Co.",
                "Brightwater Operating Group", "Corvel Hospitality",
                "Ninefold Hotel Services", "Larkspur Management Ltd."]
OWNER_PREFIX = ["Harrow", "Ellison", "Meadowbank", "Castellan", "Birchgate",
                "Oriel", "Pemberly", "Thornbury", "Verity", "Wexford", "Calder",
                "Ashgrove", "Redfern", "Sterling Vale", "Kingsmere", "Lowell"]
OWNER_SUFFIX = ["Capital LLC", "Hotel Holdings", "Real Estate Partners",
                "Property Trust", "Investments Ltd.", "Development LLC"]
FIRST = ["Alex", "Jordan", "Priya", "Marcus", "Elena", "Sam", "Nadia", "Chris",
         "Hannah", "Diego", "Mei", "Tomas", "Aisha", "Ryan", "Sofia", "Kenji",
         "Laura", "Omar", "Grace", "Mateo"]
LAST = ["Whitfield", "Okafor", "Lindqvist", "Moreau", "Castillo", "Brennan",
        "Nakamura", "Abernathy", "Sorensen", "Delacroix", "Halvorsen", "Quintero",
        "Fairbanks", "Ivanova", "Pemberton", "Rasmussen"]

ROOM_TYPES = ["Lobby", "King-Guestroom", "Double-Queen", "Suite-Living",
              "Pool", "Exterior-Dusk", "Restaurant", "Bar", "Spa-Treatment",
              "Fitness-Center", "Meeting-Room", "Ballroom", "Rooftop",
              "Bathroom", "View", "Breakfast", "Terrace", "Beach",
              "Wedding-Setup", "Kids-Club", "Lounge", "Courtyard"]
CAMPAIGN = ["Brand-Hero", "Loyalty-Offer", "Summer-Campaign", "Holiday-Campaign",
            "Meetings-Promo", "Wellness-Story", "Family-Getaway", "Dining-Story"]

PROD_HOST = "assets.example.com"
NONPROD = ["assets-int.example.com", "assets-stg.example.com"]


def ascii_code(s: str, n: int) -> str:
    s = "".join(c for c in s.lower() if c.isalpha())
    return (s + "xxxx")[:n]


# --------------------------------------------------------------------------
# 1. property master
# --------------------------------------------------------------------------
def build_master(n: int = 640) -> pd.DataFrame:
    used, rows = set(), []
    fm_people = [f"{rng.choice(FIRST)} {rng.choice(LAST)}" for _ in range(14)]
    fm_people = list(dict.fromkeys(fm_people))
    archive_pool = ARCHIVE_NAMES[:]
    rng.shuffle(archive_pool)
    bw = [b[4] for b in BRANDS]

    while len(rows) < n:
        brand = rng.choices(BRANDS, weights=bw)[0]
        bname, slug, _, cat, _, _ = brand
        div = rng.choices(list(DIV_WEIGHT), weights=list(DIV_WEIGHT.values()))[0]
        country, cities = rng.choice(DIVISIONS[div])
        city = rng.choice(cities)

        if bname == "The Archive Collection" and archive_pool:
            name = f"{archive_pool.pop()} {city}"
        elif bname in ("Vale Place", "Vale House", "Northvale Hotels") and rng.random() < .55:
            name = f"{bname.replace(' Hotels', '')} {city} {rng.choice(AREA)}"
        else:
            name = f"{bname.replace(' Hotels', '')} {city}{SUFFIX[bname]}"
        if any(r["Property Name"] == name for r in rows):
            continue

        base = ascii_code(city, 3) + ascii_code(slug, 2)
        code = base
        while code in used:
            code = ascii_code(city, 2) + "".join(rng.choices(string.ascii_lowercase, k=3))
        used.add(code)

        managed = cat in ("Luxury", "Wellness") or rng.random() < (.35 if cat == "Select Service" else .6)
        division = "Lifestyle" if cat == "Lifestyle" else div
        status = rng.choices(["Open", "Closed", "Pipeline"], weights=[.9, .04, .06])[0]
        keys = {"Select Service": (90, 220), "Luxury": (80, 260), "Wellness": (40, 120),
                "All Inclusive": (250, 700), "Timeshare": (60, 240)}.get(cat, (180, 900))
        rows.append({
            "Property Code": code.upper(),
            "Property Name": name,
            "Brand": bname,
            "Status": status,
            "Category": cat,
            "Property Type": rng.choice(["Resort"] if cat == "All Inclusive" else
                                        ["Business", "Urban", "Urban", "Business", "Resort"]),
            "Keys": rng.randint(*keys),
            "Country": country,
            "Division": f"{division} Division",
            "Ownership Type": rng.choice(["Private Company", "REIT", "Public Company",
                                          "Private Individual", "Institutional Fund"]),
            "Owner": f"{rng.choice(OWNER_PREFIX)} {rng.choice(OWNER_SUFFIX)}",
            "Reporting Relationship": "Managed" if managed else "Franchised",
            "Operator": "Northvale Hotel Group" if managed else rng.choice(OPERATORS_3P),
            "Field Mktg Mgr": rng.choice(fm_people) if rng.random() < .7 else "",
            "_slug": slug, "_enrol": brand[5],
        })
    return pd.DataFrame(rows)


# --------------------------------------------------------------------------
# 2. report calendar - roughly bi-weekly in 2023, then monthly, with a
#    two-month gap in 2024 (a real-world pattern the dashboard calls out)
# --------------------------------------------------------------------------
def report_dates() -> list[date]:
    out, d = [], date(2023, 6, 12)
    while d < date(2023, 12, 31):
        out.append(d); d += timedelta(days=14)
    extra = ["2024-01-08", "2024-01-22", "2024-02-12", "2024-03-18",
             "2024-05-20", "2024-06-24", "2024-07-22", "2024-08-19", "2024-09-23",
             "2024-10-21", "2024-11-18", "2024-12-16",
             "2025-01-21", "2025-02-24", "2025-03-31", "2025-04-28", "2025-06-09",
             "2025-08-25", "2025-10-27", "2025-12-01",
             "2026-01-26", "2026-02-23", "2026-03-30", "2026-04-27", "2026-05-26",
             "2026-06-29", "2026-08-03", "2026-08-31", "2026-09-21"]
    out += [date.fromisoformat(x) for x in extra]
    return out


# --------------------------------------------------------------------------
# 3. assets + licence lifecycle
# --------------------------------------------------------------------------
def asset_id() -> str:
    return "".join(rng.choices(string.ascii_uppercase + string.digits, k=8))


def build_assets(master: pd.DataFrame, start: date, end: date) -> list[dict]:
    enrolled = master[[rng.random() < e for e in master["_enrol"]]]
    enrolled = enrolled[enrolled["Status"] != "Pipeline"]
    assets, used_ids = [], set()
    span = (end - start).days + 200

    def new_id():
        while True:
            a = asset_id()
            if a not in used_ids:
                used_ids.add(a); return a

    for _, p in enrolled.iterrows():
        n = rng.randint(10, 48) if p["Category"] != "Select Service" else rng.randint(4, 16)
        code = p["Property Code"]
        for i in range(n):
            shot = f"{code}-{rng.choice('RWSDX')}{i + 1:03d}-{rng.choice(ROOM_TYPES)}.jpg"
            up = start - timedelta(days=rng.randint(200, 1400))
            assets.append({
                "id": new_id(), "codes": [code.lower()], "slug": p["_slug"],
                "name": p["Property Name"], "file": shot, "uploaded": up,
                "expiry": start + timedelta(days=rng.randint(-20, span)),
            })

    # corporate / brand-level assets: no property attached
    for b in BRANDS:
        for i in range(rng.randint(18, 40)):
            f = f"{b[1].upper()}-{rng.choice(CAMPAIGN)}-{i + 1:02d}.jpg"
            assets.append({"id": new_id(), "codes": [], "slug": b[1], "name": None,
                           "file": f, "uploaded": start - timedelta(days=rng.randint(100, 900)),
                           "expiry": start + timedelta(days=rng.randint(-10, span))})

    # multi-property bundles (same image licensed to 2-3 sister hotels)
    byc = enrolled.groupby("Country")["Property Code"].apply(list)
    for country, codes in byc.items():
        if len(codes) >= 2 and rng.random() < .35:
            pick = rng.sample(codes, k=min(len(codes), rng.choice([2, 3])))
            for i in range(rng.randint(1, 3)):
                assets.append({"id": new_id(), "codes": [c.lower() for c in pick],
                               "slug": "multi", "name": "Multiple Properties",
                               "file": f"{country.replace(' ', '')}-Destination-{i + 1:02d}.jpg",
                               "uploaded": start - timedelta(days=300),
                               "expiry": start + timedelta(days=rng.randint(0, span))})
    return assets


def slug_for(a: dict, master_slug: dict[str, str]) -> str:
    if a["slug"] == "multi":
        slugs = sorted({master_slug.get(c, "northvale") for c in a["codes"]})
        return ",".join(slugs)
    return a["slug"]


def main() -> None:
    master = build_master()
    dates = report_dates()
    assets = build_assets(master, dates[0], dates[-1])

    # properties that later left the system: present in reports, absent
    # from the master (the pipeline logs these to unmatched_property_codes.csv)
    gone = master.sample(n=9, random_state=SEED)
    master_out = master.drop(gone.index)

    # one property renamed partway through (code is the stable key)
    renamed = master_out[master_out["Brand"] == "Northvale Hotels"].iloc[0]
    old_name = renamed["Property Name"].replace("Northvale", "The Carlisle")
    rename_cutover = date(2025, 3, 1)

    brand_slug = dict(zip(master["Property Code"].str.lower(), master["_slug"]))
    drift = {b[1]: b[2] for b in BRANDS if b[2]}

    RAW.mkdir(parents=True, exist_ok=True)
    total = 0
    for i, rd in enumerate(dates):
        rows = []
        for a in assets:
            # an asset shows up from 45 days before expiry; each report it is
            # listed, there is a chance someone renews it (pushes expiry out)
            while a["expiry"] < rd - timedelta(days=25):
                # lapsed and taken down long ago - relicensed later
                a["expiry"] += timedelta(days=rng.choice([365, 730, 1095]))
            lead = (a["expiry"] - rd).days
            if not (-10 <= lead <= 45):
                continue
            if lead < 0 and rng.random() < .75:   # most lapsed assets get pulled
                continue
            if rng.random() < .30:          # renewed before this run
                a["expiry"] += timedelta(days=rng.choice([365, 730, 1095]))
                continue

            codes = a["codes"][:]
            name = a["name"]
            if codes and codes[0] == renamed["Property Code"].lower() and rd < rename_cutover:
                name = old_name
            code_txt = ", ".join(c.upper() if rng.random() < .01 else c for c in codes)
            slug = slug_for(a, brand_slug)
            if slug in drift and rd.year == 2024 and rng.random() < .5:
                slug = drift[slug]

            host = PROD_HOST if rng.random() > .05 else rng.choice(NONPROD)
            fname = a["file"]
            if rng.random() < .004:
                fname = fname.replace("-", " ", 1)
            up = a["uploaded"]
            url = (f"https://{host}/dam/images/{up:%Y/%m/%d}/{fname}/{fname}")

            rows.append({
                "HotelName": name if name else None,
                "PropertyCode(s)": code_txt or None,
                "Preview": "Click Here",
                "Brand": slug,
                "ID": a["id"],
                "Expiration Date": a["expiry"].strftime("%m/%d/%Y"),
                "Full External URL": url,
            })
        df = pd.DataFrame(rows).sample(frac=1, random_state=i)
        out = RAW / str(rd.year) / f"{rd:%Y %m %d} - image_expiry_report.xlsx"
        out.parent.mkdir(parents=True, exist_ok=True)
        df.to_excel(out, index=False)
        total += len(df)
        if rd == date(2025, 1, 21):     # same report resent later - superseded
            dup = RAW / str(rd.year) / f"{rd:%Y %m %d} - image_expiry_report_resend.xlsx"
            dup.parent.mkdir(parents=True, exist_ok=True)
            df.to_excel(dup, index=False)

    REF.mkdir(parents=True, exist_ok=True)
    master_out.drop(columns=["_slug", "_enrol"]).to_csv(REF / "property_master.csv", index=False)
    print(f"master: {len(master_out)} properties  |  reports: {len(dates)}  |  rows: {total}")


if __name__ == "__main__":
    main()
