"""Retrospective *posterior-output*, NOT true ecological extinction audit.

From the public author's 2009-2018 50-colony state-space model output, count
exact-zero annual posterior means and model-defined adjacent transitions.
A zero in a posterior is neither an independently reviewed breeding absence
nor absence of suitable fast-ice substrate. The source model uses
z_occ[s,t] ~ dbern(prob_occ), no detection or lag-state dependence.

Official inputs: LaRue et al. (2024), DOI: 10.1098/rspb.2023.2067, GitHub
davidiles/EMPE_Global at pinned commit 13f71112da43c1fd082273677757b41c550457ed.

No PDC individual tracking records or 2022-2024 biological records opened.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import urllib.request
from pathlib import Path

SOURCE_COMMIT = "13f71112da43c1fd082273677757b41c550457ed"
SOURCE_BLOB = "133c900c9dfbf2ce23ca403c9a59edecd9b51ace"
SOURCE_REPO = "davidiles/EMPE_Global"
SOURCE_PATH = "analysis/output/model_results/3_Colony_Level/colony_summary.csv"
SOURCE_URL = (
    f"https://raw.githubusercontent.com/{SOURCE_REPO}/{SOURCE_COMMIT}/{SOURCE_PATH}"
)
YEARS = tuple(range(2009, 2019))
EXPECTED_SITES = 50


def git_sha(raw: bytes) -> str:
    return hashlib.sha1(
        b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw
    ).hexdigest()


def read_rows(raw: bytes, strict=True) -> list[dict]:
    if strict and git_sha(raw) != SOURCE_BLOB:
        raise ValueError("PINNED_AUTHOR_POSTERIOR_CSV_SHA_MISMATCH")
    reader = csv.DictReader(io.StringIO(raw.decode("utf-8-sig")))
    fields = {"year", "site_id", "N_mean", "N_q025", "N_q975"}
    if not fields.issubset(reader.fieldnames or []):
        raise ValueError("Missing posterior CSV columns")
    rows = []
    for record in reader:
        rows.append({
            "year": int(record["year"]),
            "site": record["site_id"],
            "mean": float(record["N_mean"]),
            "lower_95": float(record["N_q025"]),
            "upper_95": float(record["N_q975"]),
        })
    if len({(r["year"], r["site"]) for r in rows}) != len(rows):
        raise ValueError("Repeated site/year identity")
    if any(r["mean"] < 0 or r["lower_95"] < 0 or r["upper_95"] < 0
           or r["upper_95"] < r["lower_95"] for r in rows):
        raise ValueError("Invalid nonnegative posterior abundance")
    if strict and (
        len(rows) != 500
        or len({r["site"] for r in rows}) != EXPECTED_SITES
        or tuple(sorted({r["year"] for r in rows})) != YEARS
    ):
        raise ValueError("Unexpected frozen 50 by 10 source support")
    return rows


def audit(rows: list[dict], expected_sites: int=50) -> dict:
    if len({r["site"] for r in rows}) != expected_sites:
        raise ValueError("Unexpected supported site count")
    if len({r["year"] for r in rows}) != 10:
        raise ValueError("Ten annual posterior estimates required")
    grouped = {}
    for r in rows:
        grouped.setdefault(r["site"], []).append(r)
    if any(len(x) != 10 or tuple(sorted(r["year"] for r in x)) != YEARS
           for x in grouped.values()):
        raise ValueError("Incomplete posterior data panel")

    annual = []
    for year in YEARS:
        arr = [r for r in rows if r["year"] == year]
        annual.append({
            "year": year,
            "exact_zero_posterior_mean": sum(r["mean"] == 0 for r in arr),
            "zero_lower_95_bound": sum(r["lower_95"] == 0 for r in arr),
            "zero_upper_95_bound": sum(r["upper_95"] == 0 for r in arr),
        })
    up, down, site_with_zeros = [], [], []
    for site, raw in grouped.items():
        seq = sorted(raw, key=lambda r: r["year"])
        missing = [r["year"] for r in seq if r["mean"] == 0]
        if missing:
            site_with_zeros.append({"site_id": site, "posterior_zero_years": missing})
        for old, new in zip(seq, seq[1:]):
            if old["mean"] == 0 and new["mean"] > 0:
                up.append({"site_id": site, "zero_year": old["year"], "positive_year": new["year"]})
            elif old["mean"] > 0 and new["mean"] == 0:
                down.append({"site_id": site, "positive_year": old["year"], "zero_year": new["year"]})
    def sel(site, year):
        return next(r for r in grouped[site] if r["year"] == year)

    return {
        "source_commit": SOURCE_COMMIT,
        "source_blob_sha": SOURCE_BLOB,
        "source_url": SOURCE_URL,
        "scope": "POSTERIOR_MEANS_AND_CREDIBLE_INTERVALS_NOT_SURVEY_COUNTS",
        "years": [YEARS[0], YEARS[-1]],
        "site_count": len(grouped),
        "posterior_site_years": len(rows),
        "annual_support": annual,
        "posterior_mean_exact_zero_site_years": sum(r["mean"] == 0 for r in rows),
        "lower_95_bound_zero_site_years": sum(r["lower_95"] == 0 for r in rows),
        "nonzero_mean_but_lower_95_zero_site_years": sum(
            r["mean"] > 0 and r["lower_95"] == 0 for r in rows
        ),
        "upper_95_bound_zero_site_years": sum(r["upper_95"] == 0 for r in rows),
        "distinct_sites_with_a_zero_posterior_mean": len(site_with_zeros),
        "sites_with_zero_posterior_years": sorted(site_with_zeros, key=lambda x: x["site_id"]),
        "apparent_mean_zero_to_positive_transitions": len(up),
        "apparent_mean_positive_to_zero_transitions": len(down),
        "apparent_zero_to_positive_events": sorted(up, key=lambda x: (x["site_id"], x["zero_year"])),
        "apparent_positive_to_zero_events": sorted(down, key=lambda x: (x["site_id"], x["positive_year"])),
        "halley_model_2016_posterior_mean": sel("HALY", 2016)["mean"],
        "halley_model_2016_posterior_lower_95": sel("HALY", 2016)["lower_95"],
        "umbeashi_model_2018_posterior_mean": sel("UMBE", 2018)["mean"],
        "known_umbeashi_2021_2022_reappearance_is_prior_publication": True,
        "model_occupancy_z_s_t_iid_shared_p_no_lag_or_detection": True,
        "exact_posterior_zero_is_verified_yearlong_ice_available_absence": False,
        "mean_transition_is_confirmed_emigration_recolonization": False,
        "scientific_effect_fit": False,
        "new_2022_plus_observational_rows_opened": 0,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    if args.input:
        source = args.input.read_bytes()
    else:
        with urllib.request.urlopen(
            urllib.request.Request(
                SOURCE_URL, headers={"User-Agent": "mina-public-posterior-QA"}
            ), timeout=35
        ) as conn:
            source = conn.read(300_000)
    result = audit(read_rows(source))
    serialized = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.out:
        args.out.write_text(serialized, encoding="utf8")
    print(serialized, end="")


if __name__ == "__main__":
    main()
