#!/usr/bin/env python3
"""State-only support gate for the preregistered guillemot recovery test.

This script intentionally does not read Subcolony.size or any other abundance
magnitude. It freezes completed vacancy->reoccupation spells and the structured
non-circular common-offset support before the Stage-C population-state
magnitudes are opened.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import pandas as pd

STATE_RAW_FIELDS = ["Subcolony", "Site.number", "Year", "Occupancy.status"]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read_state_only(path: Path) -> pd.DataFrame:
    # usecols is deliberate: population-size and trend/quality magnitudes are
    # not read into this process before the support gate is frozen.
    try:
        x = pd.read_csv(path, usecols=STATE_RAW_FIELDS)
    except ValueError as exc:
        raise ValueError(
            f"raw occupancy file missing frozen state fields: {STATE_RAW_FIELDS}"
        ) from exc

    x = x.rename(columns={
        "Subcolony": "subcolony",
        "Site.number": "site_id",
        "Year": "year",
        "Occupancy.status": "occupied",
    })
    n_raw = len(x)
    x = x.dropna(subset=["subcolony", "site_id", "year", "occupied"]).copy()
    n_after = len(x)

    x["subcolony"] = x["subcolony"].astype(str)
    x["site_id"] = x["site_id"].astype(str)
    x["year"] = pd.to_numeric(x["year"], errors="raise").astype(int)
    x["occupied"] = pd.to_numeric(x["occupied"], errors="raise").astype(int)

    if not set(x["occupied"].unique()).issubset({0, 1}):
        raise ValueError("Occupancy.status must contain only 0/1 after NA removal")
    if x.duplicated(["subcolony", "site_id", "year"]).any():
        raise ValueError("duplicate subcolony x site_id x year rows")

    x = x.sort_values(["subcolony", "site_id", "year"]).reset_index(drop=True)
    x.attrs["state_rows_read"] = int(n_raw)
    x.attrs["state_rows_retained"] = int(n_after)
    return x


def consecutive_blocks(g: pd.DataFrame):
    years = g["year"].to_numpy()
    if len(years) == 0:
        return
    start = 0
    for i in range(1, len(years)):
        if years[i] != years[i - 1] + 1:
            yield g.iloc[start:i].copy()
            start = i
    yield g.iloc[start:].copy()


def extract_completed_spells(state: pd.DataFrame) -> list[dict]:
    rows: list[dict] = []
    spell_no = 0
    for (subcolony, site_id), g in state.groupby(
        ["subcolony", "site_id"], sort=True
    ):
        for block in consecutive_blocks(g):
            if len(block) < 3:
                continue
            years = block["year"].to_numpy()
            occ = block["occupied"].to_numpy()
            occupied_idx = [i for i, v in enumerate(occ) if int(v) == 1]
            if not occupied_idx:
                continue
            # First colonization and pre-first-use zeroes are excluded.
            i = int(occupied_idx[0])
            while i < len(block) - 2:
                if int(occ[i]) == 1 and int(occ[i + 1]) == 0:
                    j = i + 1
                    while j < len(block) and int(occ[j]) == 0:
                        j += 1
                    if j < len(block) and int(occ[j]) == 1:
                        spell_no += 1
                        rows.append({
                            "spell_id": f"G{spell_no:06d}",
                            "subcolony": str(subcolony),
                            "site_id": str(site_id),
                            "block_start": int(years[0]),
                            "block_end": int(years[-1]),
                            "vacancy_pre_year": int(years[i]),
                            "vacancy_first_year": int(years[i + 1]),
                            "vacancy_last_year": int(years[j - 1]),
                            "reoccupation_year": int(years[j]),
                            "vacancy_duration_years": int(j - i - 1),
                        })
                        i = j
                        continue
                i += 1
    return rows


def add_common_offsets(spells: list[dict]) -> list[dict]:
    if not spells:
        return []
    groups: dict[str, list[dict]] = {}
    for r in spells:
        gid = f"{r['subcolony']}|{r['block_start']}-{r['block_end']}"
        groups.setdefault(gid, []).append(r)

    offsets_by_group: dict[str, list[int]] = {}
    for gid, members in sorted(groups.items()):
        lo = -10**9
        hi = 10**9
        for r in members:
            event_min = min(
                r["vacancy_pre_year"],
                r["vacancy_first_year"],
                r["vacancy_last_year"],
                r["reoccupation_year"],
            )
            event_max = max(
                r["vacancy_pre_year"],
                r["vacancy_first_year"],
                r["vacancy_last_year"],
                r["reoccupation_year"],
            )
            lo = max(lo, int(r["block_start"] - event_min))
            hi = min(hi, int(r["block_end"] - event_max))
        offsets_by_group[gid] = (
            list(range(int(lo), int(hi) + 1)) if lo <= hi else []
        )

    out = []
    for r in spells:
        z = dict(r)
        gid = f"{r['subcolony']}|{r['block_start']}-{r['block_end']}"
        z["shift_group_id"] = gid
        z["common_offset_values"] = offsets_by_group[gid]
        out.append(z)
    return out


def support_summary(spells: list[dict]) -> dict:
    eligible = [
        r for r in spells
        if 0 in r["common_offset_values"] and len(r["common_offset_values"]) >= 3
    ]
    per_sub: dict[str, int] = {}
    for r in eligible:
        per_sub[r["subcolony"]] = per_sub.get(r["subcolony"], 0) + 1

    distinct_sites = len({
        (r["subcolony"], r["site_id"]) for r in eligible
    })
    passed = bool(
        len(eligible) >= 30
        and distinct_sites >= 20
        and len(per_sub) == 5
        and min(per_sub.values(), default=0) >= 3
    )
    return {
        "eligible_completed_spells": int(len(eligible)),
        "distinct_sites_with_spells": int(distinct_sites),
        "subcolonies_with_spells": int(len(per_sub)),
        "spells_per_subcolony": {
            str(k): int(v) for k, v in sorted(per_sub.items())
        },
        "thresholds": {
            "minimum_total_completed_spells": 30,
            "minimum_distinct_sites_with_spells": 20,
            "required_subcolonies_with_spells": 5,
            "minimum_spells_per_subcolony": 3,
            "minimum_common_non_circular_offsets_per_shift_group": 3,
        },
        "passed": passed,
    }


def run(path: Path) -> dict:
    state = read_state_only(path)
    all_spells = add_common_offsets(extract_completed_spells(state))
    eligible = [
        r for r in all_spells
        if 0 in r["common_offset_values"] and len(r["common_offset_values"]) >= 3
    ]
    support = support_summary(all_spells)

    return {
        "schema_version": 1,
        "analysis_id": "mina-guillemot-same-site-support-v1",
        "status": (
            "STAGE_B_SUPPORT_PASSED"
            if support["passed"]
            else "STAGE_B_SUPPORT_FAILED"
        ),
        "source": {
            "raw_file_sha256": sha256_file(path),
            "state_fields_read": list(STATE_RAW_FIELDS),
            "magnitude_fields_read": [],
            "state_rows_read": int(state.attrs["state_rows_read"]),
            "state_rows_retained": int(state.attrs["state_rows_retained"]),
        },
        "support": support,
        "completed_spells": eligible,
        "decision": {
            "stage_C_magnitude_opening_authorized": bool(support["passed"])
        },
        "magnitude_boundary": {
            "Subcolony.size_read": False,
            "H_computed": False,
            "A_vacancy_computed": False,
            "A_reoccupation_computed": False,
            "population_state_magnitudes_exposed": False,
        },
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True, type=Path)
    p.add_argument("--out", required=True, type=Path)
    a = p.parse_args()

    result = run(a.input)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "status": result["status"],
        "support": result["support"],
        "magnitude_boundary": result["magnitude_boundary"],
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
