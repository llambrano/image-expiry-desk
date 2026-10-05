#!/usr/bin/env python3
"""
Build the Image Expiry Desk dashboard from the cleaned dataset.

    python scripts/generate_synthetic_data.py   # synthetic raw reports
    python pipeline/clean_reports.py            # -> data/clean/*.csv
    python dashboard/build_dashboard.py         # -> docs/index.html

Writes one self-contained HTML file (data inlined as JSON, no server needed),
ready for GitHub Pages. Only the Open Sans web font is fetched externally and
the page falls back to system fonts without it.
"""
from __future__ import annotations
import json, sys
from pathlib import Path
import pandas as pd

ROOT   = Path(__file__).resolve().parent.parent
CLEAN  = ROOT / "data" / "clean" / "expiring_images_clean.csv"
MASTER = ROOT / "data" / "reference" / "property_master.csv"
TPL    = Path(__file__).resolve().parent / "template.html"
OUT    = ROOT / "docs" / "index.html"
IMAGES = "assets/sample-images"          # relative to docs/index.html

# The synthetic asset URLs point at example.com, so "View asset" opens one of
# ten placeholder images instead (scripts/make_sample_images.py), chosen by
# the room type in the filename; anything unmatched is spread evenly by ID.
SCENE_FOR = {
    "Lobby": "lobby", "Lounge": "lobby",
    "King-Guestroom": "guestroom", "Double-Queen": "guestroom", "Bathroom": "guestroom",
    "Suite-Living": "suite",
    "Pool": "pool", "Kids-Club": "pool",
    "Exterior-Dusk": "exterior", "Courtyard": "exterior",
    "Restaurant": "restaurant", "Bar": "restaurant", "Breakfast": "restaurant",
    "Spa-Treatment": "spa", "Fitness-Center": "spa", "Wellness-Story": "spa",
    "Rooftop": "rooftop", "Terrace": "rooftop", "View": "rooftop",
    "Beach": "beach", "Summer-Campaign": "beach", "Family-Getaway": "pool",
    "Meeting-Room": "ballroom", "Ballroom": "ballroom", "Wedding-Setup": "ballroom",
    "Meetings-Promo": "ballroom", "Dining-Story": "restaurant",
}
SCENES = sorted(set(SCENE_FOR.values()))


def sample_image(filename: str, asset_id: str) -> str:
    stem = filename.rsplit(".", 1)[0].replace("%20", "-").replace(" ", "-")
    for key, scene in sorted(SCENE_FOR.items(), key=lambda kv: -len(kv[0])):
        if stem.endswith(key) or f"-{key}-" in stem:
            return f"{IMAGES}/{scene}.png"
    return f"{IMAGES}/{SCENES[sum(map(ord, asset_id)) % len(SCENES)]}.png"


def txt(v, fallback=""):
    return v if isinstance(v, str) else fallback


def build_payload() -> dict:
    d = pd.read_csv(CLEAN, parse_dates=["report_date", "expiration_date"])
    dates = sorted(d["report_date"].unique())
    if len(dates) < 2:
        sys.exit("need at least two reports to compute new vs carried over")
    cur, prev = dates[-1], dates[-2]

    hist = d.groupby("asset_id")["report_date"].nunique()
    prev_ids = set(d.loc[d["report_date"] == prev, "asset_id"])
    x = d[d["report_date"] == cur]

    rows = []
    for _, r in x.iterrows():
        aid = r["asset_id"]
        rows.append({
            "id": aid,
            "h":  txt(r["hotel_name"], "Corporate / brand-level"),
            "sc": txt(r["property_key"]),
            "b":  txt(r["brand"], "Corporate — no brand"),
            "dv": txt(r["division"], "Corporate"),
            "op": txt(r["operator"]), "ow": txt(r["owner"]),
            "fm": txt(r["field_mktg_mgr"]), "c": txt(r["country"]),
            "st": txt(r["hotel_status"]),
            "e":  r["expiration_date"].strftime("%Y-%m-%d"),
            "u":  sample_image(r["asset_url"].split("/")[-1], aid),
            "fn": r["asset_url"].split("/")[-1],
            "prop": bool(r["is_property_level"]),
            "new":  aid not in prev_ids,
            "seen": int(hist[aid]),
        })

    # coverage: open properties in the master that have ever appeared
    m = pd.read_csv(MASTER, dtype=str)
    m["key"] = m["Property Code"].str.lower()
    open_m = m[m["Status"] == "Open"]
    tracked = set(d["property_key"].dropna())
    cov = (open_m.assign(t=open_m["key"].isin(tracked))
                 .groupby("Category")["t"].mean().sort_values())
    least = " and ".join(cov.index[:2])

    meta = {
        "report_date": pd.Timestamp(cur).strftime("%Y-%m-%d"),
        "prior_report": pd.Timestamp(prev).strftime("%Y-%m-%d"),
        "rows": len(x),
        "hotels": int(x.loc[x["is_property_level"], "property_key"].nunique()),
        "corp_rows": int((~x["is_property_level"]).sum()),
        "new_count": sum(1 for r in rows if r["new"]),
        "carried_count": sum(1 for r in rows if not r["new"]),
        "dropped_count": len(prev_ids - set(x["asset_id"])),
        "prior_rows": int((d["report_date"] == prev).sum()),
        "tracked_hotels_all_time": int(open_m["key"].isin(tracked).sum()),
        "open_hotels_master": int(len(open_m)),
        "least_covered": least,
    }
    return {"meta": meta, "rows": rows}


def main() -> int:
    for f in (CLEAN, TPL, MASTER):
        if not f.is_file():
            print(f"missing required file: {f}", file=sys.stderr)
            return 1
    payload = build_payload()
    # escape "</" so the JSON can never close the <script> block early
    data = json.dumps(payload, ensure_ascii=False).replace("</", "<\\/")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(TPL.read_text().replace("__DATA__", data))

    m = payload["meta"]
    print(f"report {m['report_date']} (prior {m['prior_report']})")
    print(f"  {m['rows']} assets across {m['hotels']} properties + {m['corp_rows']} corporate")
    print(f"  {m['new_count']} new, {m['carried_count']} carried over, {m['dropped_count']} dropped off")
    print(f"  coverage {m['tracked_hotels_all_time']}/{m['open_hotels_master']}; least covered: {m['least_covered']}")
    print(f"wrote {OUT.relative_to(ROOT)}  ({OUT.stat().st_size // 1024} KB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
