#!/usr/bin/env python3
from __future__ import annotations

import argparse
import io
import json
import math
from pathlib import Path

import pandas as pd


def haversine_km(lat1, lon1, lat2, lon2):
    r = 6371.0088
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2-lat1)
    dl = math.radians(lon2-lon1)
    a = math.sin(dphi/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return 2*r*math.asin(math.sqrt(a))


def read_pangaea_table(path: Path) -> pd.DataFrame:
    text = path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()
    header_idx = None
    for i, line in enumerate(lines):
        cols = [c.strip() for c in line.split("\t")]
        low = {c.lower() for c in cols}
        if "latitude" in low and "longitude" in low:
            header_idx = i
            break
    if header_idx is None:
        raise ValueError("could not locate PANGAEA data header")
    data = "\n".join(lines[header_idx:])
    return pd.read_csv(io.StringIO(data), sep="\t")


def choose_column(df: pd.DataFrame, candidates):
    by_lower = {str(c).strip().lower(): c for c in df.columns}
    for c in candidates:
        if c.lower() in by_lower:
            return by_lower[c.lower()]
    raise ValueError(f"none of columns found: {candidates}; have {list(df.columns)}")


def build_reference(tab: Path) -> pd.DataFrame:
    df = read_pangaea_table(tab)
    latc = choose_column(df, ["Latitude"])
    lonc = choose_column(df, ["Longitude"])
    idc = choose_column(df, ["ID (of colony)", "ID", "Identification", "colony_ID"])
    df[latc] = pd.to_numeric(df[latc], errors="coerce")
    df[lonc] = pd.to_numeric(df[lonc], errors="coerce")
    df = df.dropna(subset=[latc, lonc])
    g = (
        df.groupby(idc)
        .agg(
            reference_latitude=(latc, "median"),
            reference_longitude=(lonc, "median"),
            reference_pixel_count=(latc, "size"),
        )
        .reset_index()
        .rename(columns={idc: "reference_colony_id"})
    )
    g["reference_nominal_area_ha"] = g["reference_pixel_count"] * 0.09
    return g


def build_candidates(forcing: Path, atlas: Path) -> pd.DataFrame:
    u = pd.read_csv(forcing)
    a = pd.read_csv(atlas)[["site_id","site_name","region","latitude","longitude"]].drop_duplicates("site_id")
    ad = u.loc[u["species_id"].astype(str).eq("ADPE"), ["site_id"]].drop_duplicates()
    if len(ad) != 44:
        raise ValueError(f"ADPE candidate drift: {len(ad)} != 44")
    out = ad.merge(a, on="site_id", how="left", validate="1:1")
    if out[["latitude","longitude"]].isna().any().any():
        raise ValueError("missing candidate coordinates")
    return out.sort_values("site_id").reset_index(drop=True)


def audit(forcing: Path, atlas: Path, tab: Path, contract_path: Path):
    c = json.loads(contract_path.read_text(encoding="utf-8"))
    cand = build_candidates(forcing, atlas)
    ref = build_reference(tab)

    rows = []
    for _, s in cand.iterrows():
        best = None
        for _, r in ref.iterrows():
            d = haversine_km(
                float(s.latitude), float(s.longitude),
                float(r.reference_latitude), float(r.reference_longitude)
            )
            if best is None or d < best[0]:
                best = (d, r)
        d, r = best
        rows.append({
            **s.to_dict(),
            "nearest_reference_colony_id": str(r.reference_colony_id),
            "nearest_reference_distance_km": float(d),
            "reference_latitude": float(r.reference_latitude),
            "reference_longitude": float(r.reference_longitude),
            "reference_pixel_count": int(r.reference_pixel_count),
            "reference_nominal_area_ha": float(r.reference_nominal_area_ha),
        })
    out = pd.DataFrame(rows)

    counts = {str(k): int((out["nearest_reference_distance_km"] <= float(k)).sum())
              for k in c["distance_audit_km"]}
    primary = float(c["primary_match_radius_km"])
    matched = out[out["nearest_reference_distance_km"] <= primary]
    regions = sorted(matched["region"].dropna().astype(str).unique().tolist())
    gate = (
        len(matched) >= int(c["feasibility_gate"]["minimum_matched_candidate_sites"])
        and len(regions) >= int(c["feasibility_gate"]["minimum_regions_represented"])
    )
    receipt = {
        "schema_version": 1,
        "result_id": "mina-paper2-adelie-guano-reference-overlap-result-v1",
        "contract_id": c["contract_id"],
        "candidate_adelie_sites": int(len(cand)),
        "reference_colonies": int(len(ref)),
        "match_counts_by_radius_km": counts,
        "primary_radius_km": primary,
        "primary_matched_sites": int(len(matched)),
        "primary_regions": regions,
        "feasibility_gate_passed": bool(gate),
        "boundary": [
            "This is spatial reference overlap only.",
            "No new guano classifier has been evaluated.",
            "No penguin abundance magnitude or trend is used."
        ]
    }
    return out, receipt


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--forcing-csv", type=Path, required=True)
    p.add_argument("--atlas-csv", type=Path, required=True)
    p.add_argument("--pangaea-tab", type=Path, required=True)
    p.add_argument("--contract", type=Path, required=True)
    p.add_argument("--out-csv", type=Path, required=True)
    p.add_argument("--out-json", type=Path, required=True)
    a=p.parse_args()
    table, receipt = audit(a.forcing_csv,a.atlas_csv,a.pangaea_tab,a.contract)
    a.out_csv.parent.mkdir(parents=True, exist_ok=True)
    table.to_csv(a.out_csv,index=False)
    a.out_json.write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(receipt,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
