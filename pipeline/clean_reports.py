#!/usr/bin/env python3
"""
Image expiry report - cleaning pipeline
=======================================
Reads every image_expiry_report file under data/raw/<year>/, applies a set of
high-confidence fixes, joins the property master, and writes one tidy CSV.

Source files are never modified. Folders beginning with "_" are skipped.

Fixes applied (see the FIXES counters written to cleaning_log.txt):
  1. Preview column dropped        - it is the literal text "Click Here" on
                                     every row; the real value is the cell
                                     hyperlink, which equals Full External URL.
  2. File format sniffed by magic  - the extension is not trusted (exports are
     bytes, not by extension         sometimes legacy .xls renamed to .xlsx).
  3. Duplicate files skipped       - the same report re-sent is detected by
                                     content hash; first one wins.
  4. URLs percent-encoded          - literal spaces in paths break mail clients.
  5. Brand slugs collapsed         - spelling drift (e.g. northvalegrand -> grand).
  6. Property codes lowercased     - codes arrive in mixed case.
  7. Dimensions from the master    - the property code is the stable key; name,
                                     brand, division, operator, etc. come from
                                     the master, so renames resolve themselves.
  8. Derived columns added         - report_date, lead_days, expired_at_issue,
                                     host_env, is_property_level, asset_ext.
  9. Bundles exploded              - one asset licensed to several properties
                                     becomes one row per property.
"""
from __future__ import annotations
import re, sys, hashlib, warnings
from pathlib import Path
from urllib.parse import quote
import pandas as pd

warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data" / "raw"
MASTER = ROOT / "data" / "reference" / "property_master.csv"
OUTDIR = ROOT / "data" / "clean"
OUT = OUTDIR / "expiring_images_clean.csv"
UNMATCHED = OUTDIR / "unmatched_property_codes.csv"
LOG = OUTDIR / "cleaning_log.txt"

MASTER_COLS = {
    "Property Name": "hotel_name", "Brand": "brand", "Status": "hotel_status",
    "Category": "category", "Property Type": "hotel_type", "Keys": "keys",
    "Country": "country", "Division": "division",
    "Ownership Type": "owner_type", "Owner": "owner",
    "Reporting Relationship": "reporting_relationship",
    "Operator": "operator", "Field Mktg Mgr": "field_mktg_mgr",
}

SOURCE_COLS = ["HotelName", "PropertyCode(s)", "Preview", "Brand", "ID",
               "Expiration Date", "Full External URL"]

BRAND_MAP = {"northvalegrand": "grand", "lumenhotels": "lumen",
             "tidewaters": "tidewater"}

PROD_HOST = "assets.example.com"
NONPROD_HOSTS = {"assets-int.example.com": "internal",
                 "assets-stg.example.com": "staging"}

FIXES: dict[str, int] = {}
NOTES: list[str] = []


def bump(key: str, n: int = 1) -> None:
    FIXES[key] = FIXES.get(key, 0) + n


def sniff_engine(path: Path) -> str:
    """Fix 2: trust magic bytes, not the file extension."""
    head = path.open("rb").read(8)
    if head.startswith(b"PK\x03\x04"):
        return "openpyxl"
    if head.startswith(b"\xd0\xcf\x11\xe0"):
        return "xlrd"
    raise ValueError(f"unrecognised format: {path.name}")


def encode_url(u: str) -> str:
    """Fix 4: percent-encode unsafe characters in the path."""
    if not isinstance(u, str) or " " not in u:
        return u
    bump("urls_encoded")
    scheme, _, rest = u.partition("://")
    host, _, path = rest.partition("/")
    return f"{scheme}://{host}/{quote(path)}"


def load_all() -> pd.DataFrame:
    files = sorted(p for p in SRC.glob("*/*.xls*")
                   if not p.parent.name.startswith("_"))
    seen: dict[str, str] = {}
    frames = []
    for f in files:
        engine = sniff_engine(f)
        declared = "openpyxl" if f.suffix.lower() == ".xlsx" else "xlrd"
        if engine != declared:
            bump("extension_mismatch")
            NOTES.append(f"  extension mismatch: {f.name}")
        df = pd.read_excel(f, dtype=str, engine=engine)
        df.columns = [str(c).strip() for c in df.columns]

        missing = set(SOURCE_COLS) - set(df.columns)
        if missing:
            NOTES.append(f"  SCHEMA DRIFT in {f.name}: missing {sorted(missing)}")
            bump("schema_drift")

        sig = hashlib.md5(
            ("|".join(sorted(df["ID"].astype(str))) + str(len(df))).encode()
        ).hexdigest()
        if sig in seen:
            bump("duplicate_files_skipped")
            NOTES.append(f"  duplicate file skipped: {f.name} (identical to {seen[sig]})")
            continue
        seen[sig] = f.name

        m = re.match(r"(\d{4}) (\d{2}) (\d{2})", f.name)
        if not m:
            NOTES.append(f"  UNPARSEABLE FILENAME: {f.name}")
            bump("unparseable_filename")
            continue
        df["report_date"] = f"{m[1]}-{m[2]}-{m[3]}"
        df["source_file"] = f.name
        frames.append(df)

    NOTES.insert(0, f"  files found: {len(files)}   files loaded: {len(frames)}")
    return pd.concat(frames, ignore_index=True)


def _sorted_list(col: pd.Series) -> pd.Series:
    return (col.str.split(",")
               .map(lambda xs: ", ".join(sorted(x.strip() for x in xs))
                    if isinstance(xs, list) else xs))


def clean(d: pd.DataFrame) -> pd.DataFrame:
    if "Preview" in d.columns:                                   # fix 1
        vals = set(d["Preview"].dropna().unique())
        if vals - {"Click Here"}:
            NOTES.append(f"  Preview had unexpected values: {vals}")
        d = d.drop(columns=["Preview"])
        bump("preview_column_dropped")

    d = d.rename(columns={
        "HotelName": "hotel_name", "PropertyCode(s)": "property_code",
        "Brand": "brand", "ID": "asset_id",
        "Expiration Date": "expiration_date", "Full External URL": "asset_url",
    })

    d["report_date"] = pd.to_datetime(d["report_date"])
    d["expiration_date"] = pd.to_datetime(d["expiration_date"],
                                          format="%m/%d/%Y", errors="coerce")
    bad = int(d["expiration_date"].isna().sum())
    if bad:
        NOTES.append(f"  unparseable expiration dates: {bad}")
        bump("unparseable_dates", bad)

    pc = d["property_code"].astype("string").str.strip()          # fix 6
    upper = int((pc.notna() & (pc != pc.str.lower())).sum())
    if upper:
        bump("property_codes_lowercased", upper)
    d["property_code"] = pc.str.lower()
    d["multi_property"] = d["property_code"].str.contains(",", na=False)
    d["property_code"] = _sorted_list(d["property_code"])
    bump("multi_property_rows", int(d["multi_property"].sum()))

    b = d["brand"].astype("string").str.strip().str.lower()        # fix 5
    bump("brand_slugs_collapsed", int(b.isin(BRAND_MAP).sum()))
    d["brand"] = _sorted_list(b.replace(BRAND_MAP))

    d["asset_url"] = d["asset_url"].map(encode_url)                # fix 4

    d["hotel_name_reported"] = d["hotel_name"].astype("string").str.strip()
    d["brand_reported"] = d["brand"]
    d = d.drop(columns=["hotel_name", "brand"])

    d["lead_days"] = (d["expiration_date"] - d["report_date"]).dt.days   # fix 8
    d["expired_at_issue"] = d["lead_days"] < 0
    host = d["asset_url"].str.extract(r"https?://([^/]+)")[0]
    d["host_env"] = host.map(lambda h: NONPROD_HOSTS.get(
        h, "production" if h == PROD_HOST else "unknown"))
    d["is_property_level"] = d["property_code"].notna()
    d["asset_ext"] = d["asset_url"].str.extract(r"\.([A-Za-z0-9]{2,5})$")[0].str.lower()
    bump("rows_nonprod_url", int((d["host_env"] != "production").sum()))
    bump("rows_expired_at_issue", int(d["expired_at_issue"].sum()))
    bump("rows_not_property_level", int((~d["is_property_level"]).sum()))
    return d


def join_master(d: pd.DataFrame) -> pd.DataFrame:
    """One row per (report_date, asset, property)."""
    m = pd.read_csv(MASTER, dtype=str)
    use = {k: v for k, v in MASTER_COLS.items() if k in m.columns}
    if len(use) < len(MASTER_COLS):
        NOTES.append(f"  master missing columns: {sorted(set(MASTER_COLS) - set(use))}")
    m = m[["Property Code"] + list(use)].rename(columns=use)
    m["property_key"] = m.pop("Property Code").str.strip().str.lower()
    m = m.drop_duplicates("property_key")

    d = d.copy()                                                    # fix 9
    d["shared_asset"] = d["multi_property"]
    d["property_key"] = d["property_code"].str.split(",")
    d = d.explode("property_key")
    d["property_key"] = d["property_key"].str.strip().replace("", pd.NA)
    bump("rows_after_bundle_explode", len(d))

    out = d.merge(m, on="property_key", how="left")                # fix 7
    coded = out["property_key"].notna()
    unmatched = coded & out["hotel_name"].isna()
    bump("rows_matched_to_master", int((coded & ~unmatched).sum()))
    bump("rows_unmatched_to_master", int(unmatched.sum()))

    if unmatched.any():
        rep = (out[unmatched].groupby("property_key")
               .agg(rows=("asset_id", "size"),
                    name_in_report=("hotel_name_reported",
                                    lambda s: s.dropna().iloc[0] if s.notna().any() else ""),
                    first_seen=("report_date", "min"),
                    last_seen=("report_date", "max"))
               .sort_values("rows", ascending=False))
        rep.to_csv(UNMATCHED)
        NOTES.append(f"  {len(rep)} property codes not in master "
                     f"({int(unmatched.sum())} rows) -> {UNMATCHED.name}")

    out["hotel_name_source"] = out["hotel_name"].notna().map(
        {True: "master", False: "reported"})
    out.loc[out["hotel_name"].isna(), "hotel_name"] = \
        out.loc[out["hotel_name"].isna(), "hotel_name_reported"]

    cols = (["report_date", "expiration_date", "lead_days", "expired_at_issue",
             "asset_id", "asset_url", "asset_ext", "host_env",
             "property_key", "property_code", "shared_asset", "is_property_level"]
            + list(use.values())
            + ["hotel_name_source", "hotel_name_reported", "brand_reported", "source_file"])
    return out[cols].sort_values(["report_date", "hotel_name", "expiration_date"])


def main() -> int:
    if not SRC.is_dir() or not MASTER.is_file():
        print("missing data - run scripts/generate_synthetic_data.py first", file=sys.stderr)
        return 1
    OUTDIR.mkdir(parents=True, exist_ok=True)
    raw = load_all()
    out = join_master(clean(raw))
    out.to_csv(OUT, index=False)

    lines = ["Image expiry report - cleaning log",
             f"rows in:  {len(raw)}", f"rows out: {len(out)}", "", "counters:"]
    lines += [f"  {k:32} {v}" for k, v in sorted(FIXES.items())]
    lines += ["", "notes:"] + NOTES
    LOG.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\nwrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
