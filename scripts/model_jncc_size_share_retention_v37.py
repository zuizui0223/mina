#!/usr/bin/env python3
"""V37 H1a source-frozen conditional score: baseline size -> later site share.

The original V30 finite-count concentration results are known, but THIS new
size-share score was fixed in contracts/JNCC_SIZE_SHARE_SCORE_V37_FROZEN.md
before opening its values. No island predator, habitat quality, Allee,
immigration or direct movement claim. No raw source child counts committed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from collections import defaultdict, Counter
from pathlib import Path

import numpy as np

import audit_jncc_two_censuses_source_v28 as original
import audit_jncc_comparable_site_panels_v29 as identity
import model_jncc_component_concentration_v30 as v30

ORIGINAL_SHA = identity.ORIGINAL_SHA
FROZEN_CONTRACT = "contracts/JNCC_SIZE_SHARE_SCORE_V37_FROZEN.md"
ALPHA = 0.5
NULL_REPLICATES = 1999
NULL_SEED = 20261027
MIN_PRIMARY_PANELS = 100
MIN_PRIMARY_SPECIES = 8
MIN_PRIMARY_SOURCE_NETWORKS = 30
MIN_PRIMARY_UNITS = 3
MIN_SPECIES_PANELS = 3
EXPECTED_STRUCTURAL_PARENT_PANELS = 1483
EXPECTED_INTEGER_PANELS = 1321
EXPECTED_DECLINING_PANELS = 959
EXPECTED_SPECIES = 17


def baseline_size_score(
    early: list[int] | np.ndarray,
    later: list[int] | np.ndarray,
    alpha: float = ALPHA,
):
    """Return observed new score and exact null allocation/size-contrast vector.

    Negative or noninteger values are source errors, not imputable counts.
    None means no informative contrast (e.g. all baseline sizes identical).
    """
    n0 = np.asarray(early, dtype=np.int64)
    n1 = np.asarray(later, dtype=np.int64)
    if n0.ndim != 1 or n1.ndim != 1 or len(n0) < 3 or len(n0) != len(n1):
        raise ValueError("SOURCE_COMPONENT_COUNT_INVALID")
    if np.any(n0 < 0) or np.any(n1 < 0):
        raise ValueError("NEGATIVE_SOURCE_COUNT")
    total0 = int(n0.sum())
    total1 = int(n1.sum())
    if total0 < 2 or total1 < 2:
        raise ValueError("INVALID_TOTAL")
    if float(alpha) != ALPHA:
        raise ValueError("SMOOTHING_NOT_FROZEN")
    if np.all(n0 == n0[0]):
        return None
    probabilities = (n0.astype(np.float64) + ALPHA) / (total0 + ALPHA*len(n0))
    if not np.isclose(probabilities.sum(), 1.0, rtol=0, atol=1e-12):
        raise ValueError("SMOOTHED_BASELINE_NOT_NORMALIZED")
    size = np.log1p(n0.astype(np.float64))
    mean_size = float(np.dot(probabilities, size))
    centered = size - mean_size
    std = math.sqrt(float(np.dot(probabilities, centered**2)))
    if not std > 0 or not math.isfinite(std):
        raise ValueError("NUMERICAL_SIZE_VARIANCE_INVALID")
    normalized_size = centered / std
    # Exactly zero theoretical null expectation, to floating tolerance.
    baseline_mean = float(np.dot(probabilities, normalized_size))
    normalized_size = normalized_size - baseline_mean
    share_late = n1.astype(np.float64) / total1
    score = float(np.dot(share_late-probabilities, normalized_size))
    return {
        "score": score,
        "pstar": probabilities,
        "size_standardized": normalized_size,
        "later_total": total1,
        "early_total": total0,
        "declining": total1 < total0,
    }


def exact_null_scores(result: dict, rng: np.random.Generator, replicates: int = NULL_REPLICATES):
    """Same standardized β=0 model score recomputed under each null draw."""
    if replicates != NULL_REPLICATES:
        raise ValueError("NULL_REPLICATES_NOT_FROZEN")
    if result is None:
        raise ValueError("NO_INFORMATIVE_SIZE_SIGNAL")
    p = result["pstar"]
    x = result["size_standardized"]
    simulated = rng.multinomial(result["later_total"], p, size=replicates)
    return (simulated.astype(np.float64) / result["later_total"] - p) @ x


def source_intake():
    raw, original_info = original.download_original()
    if original_info["original_sha256"] != ORIGINAL_SHA or hashlib.sha256(raw).hexdigest() != ORIGINAL_SHA:
        raise ValueError("SOURCE_PINNED_JNCC_SHA_MISMATCH")
    source_rows = list(identity.original_rows(raw))
    identity_report = identity.coverage(source_rows)
    if (identity_report["unique_original_two_census_site_species_rows_after_literal_QA"] != 14112
            or identity_report["qualified_species_country_master_unit_panels_with_ge3_sites"] != 1485
            or not identity_report["frozen_eligibility_gate_pass"]):
        raise ValueError("SOURCE_V29_SUPPORT_CHANGED")
    panels, source_qa = v30.extract_structural(source_rows)
    if not source_qa["pre_count_structural_gate_pass"] or len(panels) != EXPECTED_STRUCTURAL_PARENT_PANELS:
        raise ValueError("SOURCE_V30_PARENT_GUARD_CHANGED")

    # Read only the original JNCC count fields L/O *after* source identity gates.
    records = []
    drop_reasons = Counter()
    for key, children in sorted(panels.items()):
        old, new = [], []
        invalid = False
        for _rec, raw_row in children:
            a = v30.exact_count(raw_row.get("L"))
            b = v30.exact_count(raw_row.get("O"))
            if a is None or b is None:
                invalid = True
                break
            old.append(a)
            new.append(b)
        if invalid:
            drop_reasons["source_adjusted_count_not_nonnegative_exact_integer"] += 1
            continue
        if sum(old) < 2 or sum(new) < 2:
            drop_reasons["source_one_epoch_total_lt2"] += 1
            continue
        records.append((key, old, new))
    n_decline = sum(sum(new) < sum(old) for _, old, new in records)
    if (len(records) != EXPECTED_INTEGER_PANELS
        or n_decline != EXPECTED_DECLINING_PANELS
        or len({x[0][0] for x in records}) != EXPECTED_SPECIES):
        raise ValueError("SOURCE_V30_NUMERIC_COHORT_CHANGED")

    return records, {
        "original_SHA256": ORIGINAL_SHA,
        "V29_original_site_species_rows": 14112,
        "structural_parent_panels": len(panels),
        "integer_count_compatible_panels": len(records),
        "declining_total_panels_before_size_variation": n_decline,
        "species_before_size_variation": EXPECTED_SPECIES,
        "source_numeric_exclusion_reasons": dict(drop_reasons),
    }


def species_equal(scores: dict[str, list[float]], minimum: int = MIN_SPECIES_PANELS):
    valid = {name: entries for name, entries in scores.items() if len(entries) >= minimum}
    return float(np.mean([np.mean(v) for v in valid.values()])) if valid else None


def conditional_h1a_analysis(source_records: list, seed: int = NULL_SEED):
    """New endpoint, fixed prior to biological size-share calculation."""
    if seed != NULL_SEED:
        raise ValueError("RANDOM_SEED_NOT_FROZEN")
    rng = np.random.default_rng(seed)
    species_obs = {"declining": defaultdict(list), "all": defaultdict(list)}
    null_sums = {"declining": defaultdict(lambda: np.zeros(NULL_REPLICATES)),
                 "all": defaultdict(lambda: np.zeros(NULL_REPLICATES))}
    null_counts = {"declining": Counter(), "all": Counter()}
    country_obs = []
    info_panels = Counter()
    excluded_equal_sizes = Counter()
    network_ids = set()
    count_units = set()

    for key, old, new in source_records:
        score = baseline_size_score(old, new)
        if score is None:
            excluded_equal_sizes[key[0]] += 1
            continue
        sp, country, master, unit = key
        info_panels["all"] += 1
        network_ids.add((country, master))
        count_units.add(unit)
        if score["declining"]:
            info_panels["declining"] += 1
        # All eligible source panels get the same null; cohort membership is
        # the frozen original N1<N0 comparison, not a score-selected subset.
        z = exact_null_scores(score, rng)
        for cohort in ("all", "declining"):
            if cohort == "declining" and not score["declining"]:
                continue
            species_obs[cohort][sp].append(score["score"])
            null_sums[cohort][sp] += z
            null_counts[cohort][sp] += 1
        country_obs.append((sp, country, master, unit, float(score["score"]), bool(score["declining"])))

    support = {
        "informative_size_panels_all": info_panels["all"],
        "informative_size_panels_declining": info_panels["declining"],
        "excluded_panels_equal_early_component_sizes_by_species": dict(sorted(excluded_equal_sizes.items())),
        "original_country_master_networks_informative_any_trajectory": len(network_ids),
        "original_biological_count_units_informative_any_trajectory": len(count_units),
        "primary_informative_species_ge3_declining_panels": sum(
            len(v) >= MIN_SPECIES_PANELS for v in species_obs["declining"].values()),
        "primary_informative_declining_country_master_networks": len({
            (country, master) for _sp, country, master, _unit, _score, declining
            in country_obs if declining
        }),
        "primary_informative_declining_count_unit_categories": len({
            unit for _sp, _country, _master, unit, _score, declining
            in country_obs if declining
        }),
    }
    pass_gate = (
        support["informative_size_panels_declining"] >= MIN_PRIMARY_PANELS
        and support["primary_informative_species_ge3_declining_panels"] >= MIN_PRIMARY_SPECIES
        and support["primary_informative_declining_country_master_networks"] >= MIN_PRIMARY_SOURCE_NETWORKS
        and support["primary_informative_declining_count_unit_categories"] >= MIN_PRIMARY_UNITS
    )
    support["V37_primary_h1a_information_gate_pass"] = bool(pass_gate)
    if not pass_gate:
        return {"status": "STOP_V37_H1A_INFORMATIVE_SOURCE_GATE", "source_support": support,
                "biological_result_not_promoted": True}

    # Species are the equal-weighted replication tiers; 1999 null draws use
    # the exact same score and averaging procedure as the observed panels.
    summary = {}
    for cohort in ("declining", "all"):
        valid_sp = sorted(
            sp for sp, scores in species_obs[cohort].items()
            if len(scores) >= MIN_SPECIES_PANELS
        )
        obs_by_species = {sp: float(np.mean(species_obs[cohort][sp])) for sp in valid_sp}
        null_matrix = np.stack([null_sums[cohort][sp] / null_counts[cohort][sp]
                                for sp in valid_sp])
        total_null = np.mean(null_matrix, axis=0)
        t = float(np.mean(list(obs_by_species.values())))
        conditional_tail = (1 + int(np.count_nonzero(total_null >= t))) / (NULL_REPLICATES + 1)
        summary[cohort] = {
            "species_equal_mean_score": t,
            "species_positive_mean_count": sum(v>0 for v in obs_by_species.values()),
            "species_positive_mean_fraction": sum(v>0 for v in obs_by_species.values()) / len(obs_by_species),
            "species_sample_count": len(valid_sp),
            "species_data": [{
                "species": sp,
                "eligible_panels": len(species_obs[cohort][sp]),
                "mean_score": obs_by_species[sp],
                "null_mean_score": float(np.mean(null_sums[cohort][sp]/null_counts[cohort][sp])),
            } for sp in valid_sp],
            "conditional_multinomial_null_score_mean": float(np.mean(total_null)),
            "conditional_multinomial_null_score_q05": float(np.quantile(total_null, .05)),
            "conditional_multinomial_null_score_q95": float(np.quantile(total_null, .95)),
            "conditional_multinomial_null_upper_tail": float(conditional_tail),
            "a_priori_directional_descriptive_support": (
                t > 0 and sum(v>0 for v in obs_by_species.values()) >= math.ceil(2*len(valid_sp)/3)
            ),
        }

    # Country/source and species replication diagnostics were predeclared,
    # not chosen based on a favorable result. Never mix all and declines.
    primary = summary["declining"]
    primary["primary_decreasing_panel_counts_by_country"] = dict(sorted(Counter(
        country for _sp, country, _master, _unit, _score, decline
        in country_obs if decline).items()))
    primary["equal_species_score_leave_one_country_out"] = {
        country: species_equal({
            sp: [score for species, ctr, _master, _unit, score, decline in country_obs
                 if decline and species==sp and ctr!=country]
            for sp in species_obs["declining"]
        })
        for country in sorted({country for _sp, country, _master, _unit, _score, decline
                               in country_obs if decline})
    }
    primary["equal_species_score_leave_one_species_out"] = {
        sp: float(np.mean([value for other, value in
                           ((d["species"], d["mean_score"]) for d in primary["species_data"])
                           if other != sp]))
        for sp in sorted(d["species"] for d in primary["species_data"])
    }
    return {
        "status": "JNCC_V37_FIXED_NULL_BASELINE_SIZE_SHARE_SCORE_COMPUTED",
        "source_support": support,
        "primary_declining_parent_result": primary,
        "prespecified_all_trajectory_sensitivity": summary["all"],
        "interpretation_limits": {
            "multinomial_is_arithmetic_not_survey_error_or_recruitment": True,
            "original_census_adjusted_counts_not_independent_animals": True,
            "site_polygon_historical_identity_not_source_verified": True,
            "no_caused_by_social_attraction_or_allee_effect_established": True,
            "no_island_predator_or_habitat_effect_fitted": True,
            "conditional_tail_is_not_unconditional_ecological_p_value": True,
            "H2_predator_refuge_previously_stopped_for_physical_island_sample": True,
            "V30_finite_count_excess_concentration_result_not_changed": True,
        },
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    receipt = {
        "status": "JNCC_V37_SOURCE_OR_ANALYSIS_HOLD",
        "frozen_contract": FROZEN_CONTRACT,
        "frozen_seed": NULL_SEED,
        "conditional_null_replicates": NULL_REPLICATES,
        "source_original_sha256_expected": ORIGINAL_SHA,
        "JNCC_source_raw_site_counts_written_to_repo": False,
    }
    try:
        cohort, original_receipt = source_intake()
        receipt["original_source_cohort_receipt"] = original_receipt
        result = conditional_h1a_analysis(cohort)
        receipt["result"] = result
        receipt["status"] = result["status"]
    except Exception as exc:
        receipt["error"] = type(exc).__name__ + ": " + str(exc)[:900]
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": receipt["status"],
        "original_source_support": receipt.get("original_source_cohort_receipt"),
        "primary_h1a": receipt.get("result",{}).get("primary_declining_parent_result"),
        "prespecified_all_panel": receipt.get("result",{}).get("prespecified_all_trajectory_sensitivity"),
        "error": receipt.get("error"),
    }, ensure_ascii=False))
    if receipt["status"] != "JNCC_V37_FIXED_NULL_BASELINE_SIZE_SHARE_SCORE_COMPUTED":
        raise SystemExit(2)

if __name__ == "__main__":
    main()
