#!/usr/bin/env python3
"""Outcome-blind Gate 0 audit for Gentoo breeding-colony establishment."""
from __future__ import annotations

import argparse
import csv
import json
import math
from collections import defaultdict
from pathlib import Path
from statistics import median

TARGET_SPECIES = "GEPE"
TARGET_TYPE = "nests"
TARGET_CCAMLR = "48.1"
MIN_EVENTS = 8
MIN_AT_RISK = 20


def _num(x):
    if x is None:
        return None
    s = str(x).strip()
    if s in {"", "NA", "NaN", "nan", "None"}:
        return None
    try:
        v = float(s)
    except ValueError:
        return None
    return v if math.isfinite(v) else None


def _intish(x):
    v = _num(x)
    return None if v is None else int(round(v))


def _presence(x):
    s = str(x).strip().lower()
    if s in {"1", "1.0", "true", "t"}:
        return 1
    if s in {"0", "0.0", "false", "f"}:
        return 0
    return None


def read_csv(path: Path):
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def audit(obs_path: Path, sites_path: Path) -> dict:
    obs = read_csv(obs_path)
    sites = read_csv(sites_path)

    site_meta = {}
    for r in sites:
        sid = str(r.get("site_id", "")).strip()
        cc = str(r.get("ccamlr_id", "")).strip()
        if sid and cc == TARGET_CCAMLR:
            site_meta[sid] = {
                "site_name": str(r.get("site_name", "")).strip(),
                "latitude": _num(r.get("latitude")),
                "longitude": _num(r.get("longitude")),
                "region": str(r.get("region", "")).strip(),
            }

    raw = []
    for r in obs:
        sid = str(r.get("site_id", "")).strip()
        if sid not in site_meta:
            continue
        if str(r.get("species_id", "")).strip() != TARGET_SPECIES:
            continue
        if str(r.get("type", "")).strip().lower() != TARGET_TYPE:
            continue
        season = _intish(r.get("season"))
        if season is None:
            continue
        presence = _presence(r.get("presence"))
        count = _num(r.get("count"))
        positive = presence == 1 or (count is not None and count > 0)
        negative = (not positive) and presence == 0
        raw.append({
            "site_id": sid,
            "season": season,
            "positive": positive,
            "negative": negative,
        })

    by_site_season = defaultdict(list)
    for r in raw:
        by_site_season[(r["site_id"], r["season"])].append(r)

    status = defaultdict(dict)
    conflicts = 0
    for (sid, season), rows in by_site_season.items():
        any_pos = any(r["positive"] for r in rows)
        any_neg = any(r["negative"] for r in rows)
        if any_pos and any_neg:
            conflicts += 1
        if any_pos:
            st = 1
        elif any_neg:
            st = 0
        else:
            st = None
        if st is not None:
            status[sid][season] = st

    left_censored = []
    at_risk = []
    events = []
    transient_detections = []

    for sid in sorted(site_meta):
        seq = sorted(status.get(sid, {}).items())
        if not seq:
            continue
        seasons = [y for y, _ in seq]
        vals = [v for _, v in seq]
        if vals[0] == 1:
            left_censored.append(sid)
            continue
        neg_count = sum(v == 0 for v in vals)
        if len(seq) >= 4 and neg_count >= 1:
            at_risk.append(sid)

        event = None
        transient = []
        for i, (year, val) in enumerate(seq):
            if val != 1:
                continue
            prior_neg = sum(1 for _, v in seq[:i] if v == 0)
            if prior_neg < 2:
                transient.append(year)
                continue
            later = seq[i + 1 : i + 4]
            persistent = any(v == 1 for _, v in later)
            if persistent:
                event = {
                    "site_id": sid,
                    "site_name": site_meta[sid]["site_name"],
                    "event_season": year,
                    "prior_explicit_negative_seasons": prior_neg,
                    "n_known_gentoo_nest_seasons": len(seq),
                    "next_three_observed_statuses": [
                        {"season": y, "status": v} for y, v in later
                    ],
                    "transient_positive_seasons_before_event": transient,
                    "latitude": site_meta[sid]["latitude"],
                    "longitude": site_meta[sid]["longitude"],
                    "region": site_meta[sid]["region"],
                }
                break
            transient.append(year)
        if transient:
            transient_detections.append({
                "site_id": sid,
                "positive_seasons_not_used_as_establishment_before_event_or_censoring": transient,
            })
        if event is not None:
            events.append(event)

    # Gate 0 may only ask whether a prior source exists, not calculate source distance.
    all_positive = []
    for sid, seqmap in status.items():
        lat = site_meta.get(sid, {}).get("latitude")
        lon = site_meta.get(sid, {}).get("longitude")
        if lat is None or lon is None:
            continue
        for season, st in seqmap.items():
            if st == 1:
                all_positive.append((sid, season))

    events_without_prior_source = []
    for e in events:
        t = e["event_season"]
        sid = e["site_id"]
        has_source = any(src != sid and yr < t for src, yr in all_positive)
        e["has_prior_established_source_with_coordinates"] = has_source
        if not has_source:
            events_without_prior_source.append(sid)

    gaps = []
    for sid, seqmap in status.items():
        ys = sorted(seqmap)
        gaps.extend(b - a for a, b in zip(ys, ys[1:]))

    passed = (
        len(events) >= MIN_EVENTS
        and len(at_risk) >= MIN_AT_RISK
        and len(events_without_prior_source) == 0
    )

    return {
        "schema_version": 1,
        "audit_id": "mina-gentoo-colonization-network-gate0-audit-v1",
        "contract_id": "mina-gentoo-colonization-network-gate0-v1",
        "source_rows_total": len(obs),
        "ccamlr_48_1_sites": len(site_meta),
        "gepe_nest_rows": len(raw),
        "gepe_nest_site_season_cells": len(by_site_season),
        "same_site_season_positive_negative_conflicts_positive_overrides": conflicts,
        "sites_with_known_gepe_nest_status": len(status),
        "sites_with_any_explicit_negative": sum(any(v == 0 for v in x.values()) for x in status.values()),
        "left_censored_already_positive_sites": len(left_censored),
        "left_censored_site_ids": left_censored,
        "at_risk_sites": len(at_risk),
        "at_risk_site_ids": at_risk,
        "persistent_colonization_events": len(events),
        "events": events,
        "transient_detection_sites": transient_detections,
        "events_without_prior_source": events_without_prior_source,
        "observation_gap_summary_seasons": {
            "n_gaps": len(gaps),
            "median": None if not gaps else float(median(gaps)),
            "max": None if not gaps else int(max(gaps)),
        },
        "gate_thresholds": {
            "minimum_persistent_colonization_events": MIN_EVENTS,
            "minimum_at_risk_sites": MIN_AT_RISK,
            "maximum_events_with_no_prior_source": 0,
        },
        "decision": {
            "gate_passed": passed,
            "distance_effect_may_be_frozen_next": passed,
            "no_geometry_or_distance_effect_computed": True,
        },
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--obs", type=Path, required=True)
    p.add_argument("--sites", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    a = p.parse_args()
    result = audit(a.obs, a.sites)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
