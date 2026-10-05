#!/usr/bin/env python3
from __future__ import annotations

import argparse
import itertools
import json
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd

REQUIRED = ["subcolony", "site_id", "year", "occupied", "subcolony_size"]


def _validate(df: pd.DataFrame) -> pd.DataFrame:
    missing = [c for c in REQUIRED if c not in df.columns]
    if missing:
        raise ValueError(f"missing required standardized fields: {missing}")
    x = df[REQUIRED].copy()
    if x[REQUIRED].isna().any().any():
        raise ValueError("standardized input contains missing values; omit unobserved site-years")
    x["subcolony"] = x["subcolony"].astype(str)
    x["site_id"] = x["site_id"].astype(str)
    x["year"] = pd.to_numeric(x["year"], errors="raise").astype(int)
    x["occupied"] = pd.to_numeric(x["occupied"], errors="raise").astype(int)
    x["subcolony_size"] = pd.to_numeric(x["subcolony_size"], errors="raise").astype(float)
    if not set(x["occupied"].unique()).issubset({0, 1}):
        raise ValueError("occupied must be binary 0/1")
    if (x["subcolony_size"] < 0).any():
        raise ValueError("subcolony_size must be non-negative")
    if x.duplicated(["subcolony", "site_id", "year"]).any():
        raise ValueError("duplicate subcolony x site_id x year rows")
    # The supplied parent count may include sites not represented in the site-level file.
    if (x["subcolony_size"] < x["occupied"]).any():
        raise ValueError("subcolony_size cannot be smaller than focal occupancy")
    return x.sort_values(["subcolony", "site_id", "year"]).reset_index(drop=True)


def _blocks(g: pd.DataFrame):
    years = g["year"].to_numpy()
    if len(years) == 0:
        return
    start = 0
    for i in range(1, len(years)):
        if years[i] != years[i - 1] + 1:
            yield g.iloc[start:i].copy()
            start = i
    yield g.iloc[start:].copy()


def extract_spells(df: pd.DataFrame) -> pd.DataFrame:
    x = _validate(df)
    rows = []
    spell_no = 0
    for (subcolony, site_id), g in x.groupby(["subcolony", "site_id"], sort=True):
        for block in _blocks(g):
            if len(block) < 3:
                continue
            y = block["year"].to_numpy()
            z = block["occupied"].to_numpy()
            # Site history begins at first observed occupation; pre-first-use zeroes
            # never contribute to a completed vacancy/reoccupation spell.
            occupied_idx = np.flatnonzero(z == 1)
            if len(occupied_idx) == 0:
                continue
            first_occ = int(occupied_idx[0])
            i = first_occ
            while i < len(block) - 2:
                if z[i] == 1 and z[i + 1] == 0:
                    j = i + 1
                    while j < len(block) and z[j] == 0:
                        j += 1
                    if j < len(block) and z[j] == 1:
                        spell_no += 1
                        rows.append({
                            "spell_id": f"G{spell_no:06d}",
                            "subcolony": subcolony,
                            "site_id": site_id,
                            "block_start": int(y[0]),
                            "block_end": int(y[-1]),
                            "vacancy_pre_year": int(y[i]),
                            "vacancy_first_year": int(y[i + 1]),
                            "vacancy_last_year": int(y[j - 1]),
                            "reoccupation_year": int(y[j]),
                            "vacancy_duration_years": int(j - i - 1),
                        })
                        i = j
                        continue
                i += 1
    return pd.DataFrame(rows)


def _other_state_lookup(df: pd.DataFrame) -> dict[tuple[str, str, int], float]:
    x = _validate(df)
    return {
        (r.subcolony, r.site_id, int(r.year)): float(r.subcolony_size - r.occupied)
        for r in x.itertuples(index=False)
    }


def _with_offsets(spells: pd.DataFrame) -> pd.DataFrame:
    if spells.empty:
        return spells.assign(group_id=pd.Series(dtype=str), common_offsets=pd.Series(dtype=object))
    s = spells.copy()
    s["group_id"] = (
        s["subcolony"].astype(str)
        + "|"
        + s["block_start"].astype(str)
        + "-"
        + s["block_end"].astype(str)
    )
    group_offsets = {}
    for gid, g in s.groupby("group_id", sort=True):
        lo = -10**9
        hi = 10**9
        for r in g.itertuples(index=False):
            event_min = min(r.vacancy_pre_year, r.vacancy_first_year, r.vacancy_last_year, r.reoccupation_year)
            event_max = max(r.vacancy_pre_year, r.vacancy_first_year, r.vacancy_last_year, r.reoccupation_year)
            lo = max(lo, int(r.block_start - event_min))
            hi = min(hi, int(r.block_end - event_max))
        vals = list(range(int(lo), int(hi) + 1)) if lo <= hi else []
        group_offsets[gid] = vals
    s["common_offsets"] = s["group_id"].map(group_offsets)
    return s


def _h_for_spell(r, lookup, offset: int = 0) -> float:
    key = lambda year: (str(r.subcolony), str(r.site_id), int(year + offset))
    vals = [
        lookup[key(r.vacancy_pre_year)],
        lookup[key(r.vacancy_first_year)],
        lookup[key(r.vacancy_last_year)],
        lookup[key(r.reoccupation_year)],
    ]
    av = 0.5 * (np.log1p(vals[0]) + np.log1p(vals[1]))
    ar = 0.5 * (np.log1p(vals[2]) + np.log1p(vals[3]))
    return float(ar - av)


def _aggregate(spells: pd.DataFrame, h_values: np.ndarray) -> tuple[float, dict[str, float]]:
    z = spells[["subcolony", "site_id"]].copy()
    z["H"] = h_values
    site = z.groupby(["subcolony", "site_id"], as_index=False)["H"].mean()
    sub = site.groupby("subcolony", as_index=False)["H"].mean()
    contrib = {str(r.subcolony): float(r.H) for r in sub.itertuples(index=False)}
    return float(sub["H"].mean()), contrib


def _exact_signflip(contrib: dict[str, float], observed: float) -> float:
    vals = np.array([contrib[k] for k in sorted(contrib)], dtype=float)
    stats = []
    for signs in itertools.product([-1.0, 1.0], repeat=len(vals)):
        stats.append(float(np.mean(vals * np.asarray(signs))))
    return float(np.mean(np.asarray(stats) >= observed - 1e-15))


def _support(spells: pd.DataFrame) -> dict:
    per_sub = spells.groupby("subcolony").size().to_dict() if not spells.empty else {}
    offsets_ok = bool(len(spells)) and bool(spells["common_offsets"].map(lambda v: 0 in v and len(v) >= 3).all())
    return {
        "total_completed_spells": int(len(spells)),
        "distinct_sites_with_spells": int(spells["site_id"].nunique()) if len(spells) else 0,
        "subcolonies_with_spells": int(spells["subcolony"].nunique()) if len(spells) else 0,
        "spells_per_subcolony": {str(k): int(v) for k, v in per_sub.items()},
        "all_common_offsets_valid": offsets_ok,
        "passed": bool(
            len(spells) >= 30
            and spells["site_id"].nunique() >= 20
            and spells["subcolony"].nunique() == 5
            and len(per_sub) == 5
            and min(per_sub.values()) >= 3
            and offsets_ok
        ),
    }


def analyse(df: pd.DataFrame, *, B: int = 9999, seed: int = 20261005, min_vacancy: int = 1) -> dict:
    x = _validate(df)
    spells = _with_offsets(extract_spells(x))
    if min_vacancy > 1 and len(spells):
        spells = spells.loc[spells["vacancy_duration_years"] >= min_vacancy].copy()
    support = _support(spells)
    out = {
        "support": support,
        "min_vacancy_duration_years": int(min_vacancy),
        "decision": {"analysis_available": bool(support["passed"])},
    }
    if not support["passed"]:
        return out

    lookup = _other_state_lookup(x)
    h_obs = np.array([_h_for_spell(r, lookup, 0) for r in spells.itertuples(index=False)])
    T_obs, contrib = _aggregate(spells, h_obs)
    p_sign = _exact_signflip(contrib, T_obs)

    groups = {
        gid: list(vals.iloc[0])
        for gid, vals in spells.groupby("group_id", sort=True)["common_offsets"]
    }
    rng = np.random.default_rng(seed)
    null = np.empty(B, dtype=float)
    rows = list(spells.itertuples(index=False))
    for b in range(B):
        chosen = {gid: int(rng.choice(v)) for gid, v in groups.items()}
        h = np.array([_h_for_spell(r, lookup, chosen[r.group_id]) for r in rows])
        null[b], _ = _aggregate(spells, h)

    delta = float(T_obs - np.median(null))
    p_shift = float((1 + np.sum(null >= T_obs - 1e-15)) / (B + 1))
    supported = bool(T_obs > 0 and p_sign <= 0.05 and delta > 0 and p_shift <= 0.05)

    out.update({
        "T_obs": float(T_obs),
        "subcolony_contributions": contrib,
        "exact_subcolony_signflip_p": float(p_sign),
        "shift_null": {
            "B": int(B),
            "seed": int(seed),
            "median": float(np.median(null)),
            "delta_shift": delta,
            "upper_tail_p": p_shift,
        },
        "decision": {
            "analysis_available": True,
            "same_site_recovery_asymmetry_supported": supported,
            "all_four_confirmatory_conditions": {
                "T_obs_positive": bool(T_obs > 0),
                "subcolony_signflip_p_le_0_05": bool(p_sign <= 0.05),
                "delta_shift_positive": bool(delta > 0),
                "shift_p_le_0_05": bool(p_shift <= 0.05),
            },
        },
    })
    return out


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True, type=Path)
    p.add_argument("--out-json", required=True, type=Path)
    p.add_argument("--out-spells-csv", required=True, type=Path)
    p.add_argument("--B", type=int, default=9999)
    p.add_argument("--seed", type=int, default=20261005)
    a = p.parse_args()

    df = pd.read_csv(a.input)
    primary = analyse(df, B=a.B, seed=a.seed, min_vacancy=1)
    secondary = analyse(df, B=a.B, seed=a.seed, min_vacancy=2)

    spells = _with_offsets(extract_spells(_validate(df)))
    lookup = _other_state_lookup(df)
    if len(spells):
        spells["H_observed"] = [_h_for_spell(r, lookup, 0) for r in spells.itertuples(index=False)]

    result = {
        "schema_version": 1,
        "analysis_id": "mina-guillemot-same-site-recovery-v1",
        "primary": primary,
        "secondary_two_year_vacancy": secondary,
        "claim_boundary": {
            "event": "annual breeding-site vacancy and later reoccupation",
            "not_identified": ["individual return", "causal Allee effect", "causal social attraction", "permanent abandonment"],
        },
    }
    a.out_json.parent.mkdir(parents=True, exist_ok=True)
    a.out_json.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    spells.to_csv(a.out_spells_csv, index=False)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
