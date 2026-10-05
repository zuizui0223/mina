#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

RAW_TO_STD = {
    "Subcolony": "subcolony",
    "Site.number": "site_id",
    "Year": "year",
    "Occupancy.status": "occupied",
    "Subcolony.size": "subcolony_size",
}


def prepare(path: Path) -> tuple[pd.DataFrame, dict]:
    raw = pd.read_csv(path)
    missing = [c for c in RAW_TO_STD if c not in raw.columns]
    if missing:
        raise ValueError(f"raw occupancy file missing frozen columns: {missing}")

    x = raw[list(RAW_TO_STD)].rename(columns=RAW_TO_STD).copy()
    n_raw = len(x)
    required_na = x.isna().any(axis=1)
    n_dropped_na = int(required_na.sum())
    x = x.loc[~required_na].copy()

    x["subcolony"] = x["subcolony"].astype(str)
    x["site_id"] = x["site_id"].astype(str)
    x["year"] = pd.to_numeric(x["year"], errors="raise").astype(int)
    x["occupied"] = pd.to_numeric(x["occupied"], errors="raise").astype(int)
    x["subcolony_size"] = pd.to_numeric(x["subcolony_size"], errors="raise").astype(float)

    if not set(x["occupied"].unique()).issubset({0, 1}):
        raise ValueError("Occupancy.status contains values other than 0/1 after NA removal")
    if (x["subcolony_size"] < 0).any():
        raise ValueError("Subcolony.size contains negative values")
    if x.duplicated(["subcolony", "site_id", "year"]).any():
        dup = x.loc[
            x.duplicated(["subcolony", "site_id", "year"], keep=False),
            ["subcolony", "site_id", "year"],
        ].head(20)
        raise ValueError(f"duplicate site-year rows: {dup.to_dict(orient='records')}")

    nsize = (
        x.groupby(["subcolony", "year"], sort=True)["subcolony_size"]
        .nunique(dropna=False)
    )
    bad = nsize[nsize != 1]
    if len(bad):
        raise ValueError(
            "Subcolony.size is not unique within subcolony x year: "
            + repr(list(bad.index[:20]))
        )

    x = x.sort_values(["subcolony", "site_id", "year"]).reset_index(drop=True)
    audit = {
        "schema_version": 1,
        "adapter_id": "mina-guillemot-same-site-input-v1",
        "source_file_expected": "JAE_Bennett_CommonGuillemot_sitequality_occupancy.csv",
        "raw_to_standardized_mapping": RAW_TO_STD,
        "rows_read": int(n_raw),
        "rows_dropped_required_NA": n_dropped_na,
        "rows_standardized": int(len(x)),
        "distinct_subcolonies": int(x["subcolony"].nunique()),
        "distinct_sites": int(x[["subcolony", "site_id"]].drop_duplicates().shape[0]),
        "year_min": int(x["year"].min()) if len(x) else None,
        "year_max": int(x["year"].max()) if len(x) else None,
        "occupancy_values": sorted(int(v) for v in x["occupied"].unique()),
        "biological_effect_opened": False,
        "forbidden_fields_not_used": [
            "Quality",
            "Trend.phase",
            "Trend.slope",
            "Colonisation.phase",
            "Wholecolony.size",
            "Mean.size.scale",
            "Mean.trend.scale",
            "Mean.whole.colony.size.scale",
            "Mean.whole.colony.trend.scale"
        ],
    }
    return x, audit


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True, type=Path)
    p.add_argument("--out-csv", required=True, type=Path)
    p.add_argument("--out-audit-json", required=True, type=Path)
    a = p.parse_args()

    x, audit = prepare(a.input)
    a.out_csv.parent.mkdir(parents=True, exist_ok=True)
    x.to_csv(a.out_csv, index=False)
    a.out_audit_json.write_text(
        json.dumps(audit, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(audit, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
