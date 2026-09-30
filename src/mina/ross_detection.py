"""Outcome-blind detection-proxy builder for Ross Island settlement choices.

This module accepts canonical observation records only. It deliberately contains
no USAP-DC CSV loader; exact raw-column parsing remains locked behind the header
gate.
"""
from __future__ import annotations

from collections import defaultdict
from datetime import date
from typing import Iterable, Mapping

import numpy as np

COLONIES = ("CROZ", "ROYD", "BIRD")
COLONY_SET = set(COLONIES)


def season_start_year(observed: date) -> int | None:
    """Map austral breeding-season dates to the season's starting year."""
    if observed.month >= 10:
        return observed.year
    if observed.month <= 3:
        return observed.year - 1
    return None


def _canonical_date(value: object) -> date:
    if isinstance(value, date):
        return value
    raise TypeError("canonical detection records require datetime.date values")


def build_resight_day_proxy(
    observations: Iterable[Mapping[str, object]],
    events: Iterable[Mapping[str, object]],
) -> tuple[dict[str, dict[str, float]], dict[str, str]]:
    """Return event-specific standardized log resight-day proxies."""
    by_season_colony: dict[tuple[int, str], dict[date, set[str]]] = defaultdict(
        lambda: defaultdict(set)
    )
    for row in observations:
        colony = str(row["colony"])
        if colony not in COLONY_SET:
            continue
        observed = _canonical_date(row["date"])
        season = season_start_year(observed)
        if season is None:
            continue
        individual = str(row["individual_id"])
        by_season_colony[(season, colony)][observed].add(individual)

    proxies: dict[str, dict[str, float]] = {}
    dropped: dict[str, str] = {}

    for event in events:
        event_id = str(event["event_id"])
        focal = str(event["individual_id"])
        season = int(event["first_breeding_season"])
        candidate_set = {
            str(c) for c in event.get("candidate_colonies", COLONIES)
        }
        if not candidate_set.issubset(COLONY_SET):
            raise ValueError(f"unknown candidate colony in event {event_id}")
        if season >= 2014 and "BIRD" in candidate_set:
            dropped[event_id] = "bird_candidate_post_2013"
            continue

        counts = np.empty(3, dtype=float)
        complete = True
        for ci, colony in enumerate(COLONIES):
            dates = by_season_colony.get((season, colony), {})
            nonfocal_dates = sum(
                1 for birds in dates.values() if any(b != focal for b in birds)
            )
            if nonfocal_dates <= 0:
                complete = False
                break
            counts[ci] = float(nonfocal_dates)
        if not complete:
            dropped[event_id] = (
                "missing_nonfocal_resight_date_in_one_or_more_colonies"
            )
            continue

        transformed = np.log1p(counts)
        sd = float(np.std(transformed, ddof=1))
        if sd <= 0:
            z = np.zeros_like(transformed)
        else:
            z = (transformed - float(np.mean(transformed))) / sd
        proxies[event_id] = {
            colony: float(z[ci]) for ci, colony in enumerate(COLONIES)
        }

    return proxies, dropped


def build_date_observer_proxy(
    observations: Iterable[Mapping[str, object]],
    events: Iterable[Mapping[str, object]],
) -> tuple[dict[str, dict[str, float]], dict[str, str]]:
    """Sensitivity proxy using distinct date-observer pairs.

    Canonical observation rows must include an observer field. Empty observer
    values are not counted. All rows belonging to the focal individual are
    excluded.
    """
    by_season_colony: dict[
        tuple[int, str], dict[tuple[date, str], set[str]]
    ] = defaultdict(lambda: defaultdict(set))
    for row in observations:
        colony = str(row["colony"])
        if colony not in COLONY_SET:
            continue
        observer = str(row.get("observer", "")).strip()
        if not observer:
            continue
        observed = _canonical_date(row["date"])
        season = season_start_year(observed)
        if season is None:
            continue
        individual = str(row["individual_id"])
        by_season_colony[(season, colony)][(observed, observer)].add(individual)

    proxies: dict[str, dict[str, float]] = {}
    dropped: dict[str, str] = {}
    for event in events:
        event_id = str(event["event_id"])
        focal = str(event["individual_id"])
        season = int(event["first_breeding_season"])
        candidate_set = {
            str(c) for c in event.get("candidate_colonies", COLONIES)
        }
        if season >= 2014 and "BIRD" in candidate_set:
            dropped[event_id] = "bird_candidate_post_2013"
            continue

        counts = np.empty(3, dtype=float)
        complete = True
        for ci, colony in enumerate(COLONIES):
            pairs = by_season_colony.get((season, colony), {})
            nonfocal_pairs = sum(
                1 for birds in pairs.values() if any(b != focal for b in birds)
            )
            if nonfocal_pairs <= 0:
                complete = False
                break
            counts[ci] = float(nonfocal_pairs)
        if not complete:
            dropped[event_id] = (
                "missing_nonfocal_date_observer_pair_in_one_or_more_colonies"
            )
            continue

        transformed = np.log1p(counts)
        sd = float(np.std(transformed, ddof=1))
        if sd <= 0:
            z = np.zeros_like(transformed)
        else:
            z = (transformed - float(np.mean(transformed))) / sd
        proxies[event_id] = {
            colony: float(z[ci]) for ci, colony in enumerate(COLONIES)
        }
    return proxies, dropped
