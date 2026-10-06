#!/usr/bin/env python3
"""Exploratory exact-zero recovery-memory screen for penguin breeding components."""
from __future__ import annotations

import argparse
import json
import math
from collections import defaultdict
from pathlib import Path

import numpy as np

from scripts.describe_concentration_dominance import (
    SIGNY_ADELIE_UNITS,
    SIGNY_CHINSTRAP_UNITS,
    SIGNY_YEARS,
    canonical_adelie,
    load_palmer,
    signy_panel,
)
from scripts.audit_signy_replication_support import read_official_zip

PALMER_ISLANDS = ("COR", "HUM", "LIT")


def palmer_full_panels(path: Path):
    rows = load_palmer(path)
    out = {}
    for island in PALMER_ISLANDS:
        local = [r for r in rows if r["island"] == island]
        by_year = defaultdict(dict)
        for r in local:
            by_year[int(r["year"])][str(r["unit"])] = float(r["count"])
        years = sorted(by_year)
        rosters = [set(by_year[y]) for y in years]
        if not rosters or any(r != rosters[0] for r in rosters[1:]):
            raise ValueError(f"{island}: unstable roster")
        if any(b - a != 1 for a, b in zip(years, years[1:])):
            raise ValueError(f"{island}: Palmer calendar gap")
        units = sorted(rosters[0])
        matrix = np.asarray([[by_year[y][u] for y in years] for u in units], dtype=float)
        out[f"ADPE_PALMER_{island}"] = (units, np.asarray(years, dtype=int), matrix)
    return out


def completed_zero_spells(population: str, units, years, matrix):
    totals = matrix.sum(axis=0)
    events = []
    censored = []
    for ui, unit in enumerate(units):
        x = matrix[ui]
        i = 1
        while i < len(years):
            # Loss edge must be calendar-consecutive and positive -> exact zero.
            if years[i] - years[i - 1] == 1 and x[i - 1] > 0 and x[i] == 0:
                loss_pos_i = i - 1
                first_zero_i = i
                k = i
                status = None
                nminus = totals - x
                a_loss = 0.5 * (
                    math.log1p(float(nminus[loss_pos_i])) +
                    math.log1p(float(nminus[first_zero_i]))
                )
                later_zero_states = []
                while True:
                    if k + 1 >= len(years):
                        status = "right_censored"
                        break
                    if years[k + 1] - years[k] != 1:
                        status = "gap_censored"
                        break
                    if x[k + 1] == 0:
                        later_zero_states.append(math.log1p(float(nminus[k + 1])))
                    if x[k + 1] > 0:
                        last_zero_i = k
                        return_i = k + 1
                        a_return = 0.5 * (
                            math.log1p(float(nminus[last_zero_i])) +
                            math.log1p(float(nminus[return_i]))
                        )
                        h = a_return - a_loss
                        events.append({
                            "population": population,
                            "unit": str(unit),
                            "loss_last_positive_year": int(years[loss_pos_i]),
                            "loss_first_zero_year": int(years[first_zero_i]),
                            "return_last_zero_year": int(years[last_zero_i]),
                            "return_first_positive_year": int(years[return_i]),
                            "zero_spell_years": int(return_i - first_zero_i),
                            "a_loss": float(a_loss),
                            "a_return": float(a_return),
                            "H": float(h),
                            "state_ratio_exp_H": float(math.exp(h)),
                            "return_delay_years": int(years[return_i] - years[first_zero_i]),
                            "panel_last_year": int(years[-1]),
                            "max_later_zero_state": (
                                float(max(later_zero_states)) if later_zero_states else None
                            ),
                            "later_zero_state_at_or_above_loss": bool(
                                later_zero_states and max(later_zero_states) >= a_loss
                            ),
                        })
                        i = return_i
                        status = "completed"
                        break
                    k += 1
                if status != "completed":
                    censored.append({
                        "population": population,
                        "unit": str(unit),
                        "loss_last_positive_year": int(years[loss_pos_i]),
                        "loss_first_zero_year": int(years[first_zero_i]),
                        "status": status,
                        "a_loss": float(a_loss),
                        "panel_last_year": int(years[-1]),
                        "max_later_zero_state": (
                            float(max(later_zero_states)) if later_zero_states else None
                        ),
                        "later_zero_state_at_or_above_loss": bool(
                            later_zero_states and max(later_zero_states) >= a_loss
                        ),
                    })
                    i = max(i + 1, k + 1)
                    continue
            i += 1
    return events, censored


def summarize(events, censored):
    completed_units = sorted({(e["population"], e["unit"]) for e in events})
    all_spells = list(events) + list(censored)
    loss_units = sorted({(e["population"], e["unit"]) for e in all_spells})
    completed_pops = sorted({e["population"] for e in events})
    hs = np.asarray([e["H"] for e in events], dtype=float)
    out = {
        "loss_spells_total": int(len(events) + len(censored)),
        "completed_spells": int(len(events)),
        "right_censored_spells": int(sum(c["status"] == "right_censored" for c in censored)),
        "gap_censored_spells": int(sum(c["status"] == "gap_censored" for c in censored)),
        "distinct_components_completed": int(len(completed_units)),
        "population_trajectories_completed": int(len(completed_pops)),
        "completed_populations": completed_pops,
        "distinct_components_with_loss": int(len(loss_units)),
        "ever_reoccupied_component_fraction": (
            float(len(completed_units) / len(loss_units)) if loss_units else None
        ),
        "later_state_match_spells": int(sum(
            bool(e.get("later_zero_state_at_or_above_loss")) for e in all_spells
        )),
    }
    followup = {}
    for horizon in (2, 3, 5, 10):
        eligible = [
            e for e in all_spells
            if int(e["panel_last_year"]) - int(e["loss_first_zero_year"]) >= horizon
        ]
        returned = [
            e for e in eligible
            if e in events and int(e["return_delay_years"]) <= horizon
        ]
        followup[str(horizon)] = {
            "eligible_loss_spells": int(len(eligible)),
            "returned_within_horizon": int(len(returned)),
            "return_fraction": (
                float(len(returned) / len(eligible)) if eligible else None
            ),
        }
    out["return_within_years"] = followup
    if len(hs):
        med = float(np.median(hs))
        out.update({
            "median_H": med,
            "mean_H": float(np.mean(hs)),
            "fraction_H_positive": float(np.mean(hs > 0)),
            "median_state_ratio_exp_H": float(math.exp(med)),
            "min_H": float(np.min(hs)),
            "max_H": float(np.max(hs)),
        })
    else:
        out.update({
            "median_H": None,
            "mean_H": None,
            "fraction_H_positive": None,
            "median_state_ratio_exp_H": None,
            "min_H": None,
            "max_H": None,
        })
    out["adequacy_gate"] = {
        "min_completed_spells": 10,
        "min_distinct_components": 5,
        "min_population_trajectories": 3,
        "passes": bool(
            len(events) >= 10 and
            len(completed_units) >= 5 and
            len(completed_pops) >= 3
        ),
    }
    return out


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--palmer-census", required=True, type=Path)
    p.add_argument("--signy-adelie-zip", required=True, type=Path)
    p.add_argument("--signy-chinstrap-zip", required=True, type=Path)
    p.add_argument("--out", required=True, type=Path)
    a = p.parse_args()

    panels = palmer_full_panels(a.palmer_census)

    ad, _ = read_official_zip(a.signy_adelie_zip)
    u, y, m = signy_panel(ad, units=SIGNY_ADELIE_UNITS, canonicalize=canonical_adelie)
    panels["ADPE_SIGNY"] = (u, y, m)

    ch, _ = read_official_zip(a.signy_chinstrap_zip)
    u, y, m = signy_panel(ch, units=SIGNY_CHINSTRAP_UNITS, canonicalize=None)
    panels["CHPE_SIGNY"] = (u, y, m)

    events, censored = [], []
    population_summaries = {}
    for pop, (units, years, matrix) in panels.items():
        ev, ce = completed_zero_spells(pop, units, years, matrix)
        events.extend(ev)
        censored.extend(ce)
        population_summaries[pop] = {
            "units": len(units),
            "years": len(years),
            "loss_spells": len(ev) + len(ce),
            "completed_spells": len(ev),
            "right_censored_spells": sum(c["status"] == "right_censored" for c in ce),
            "gap_censored_spells": sum(c["status"] == "gap_censored" for c in ce),
        }

    result = {
        "schema_version": 1,
        "analysis_id": "mina-penguin-recovery-memory-screen-v1",
        "status": "exploratory_already_exposed_data_no_inferential_p_values",
        "population_summaries": population_summaries,
        "summary": summarize(events, censored),
        "completed_events": events,
        "censored_events": censored,
        "interpretation_boundary": [
            "Exact-zero observed breeding-component spells only; no low-count threshold is introduced.",
            "H is a descriptive same-component loss-versus-return contrast, not proof of causal hysteresis.",
            "No individual movement, conspecific attraction, or social-information mechanism is identified.",
            "Failure of the adequacy gate cannot be rescued by alternate thresholds, rosters, pooling, or lags."
        ],
    }
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
