"""Canonical Ross Island state and first-breeding choice construction.

This module intentionally does not read the real USAP-DC CSV. It operates on
canonical dictionaries whose field meanings are already frozen from public
README metadata. A raw CSV loader remains prohibited until the exact-header
gate is manually unlocked.
"""
from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from typing import Iterable, Mapping

import numpy as np

ROSS_COLONIES = ("CROZ", "ROYD", "BIRD")
STUDY_COLONIES = ("CROZ", "ROYD", "BIRD", "BEAU")
BREEDING_CODES = {1, 2, 8}
INTERPRETABLE_CHICK_CODES = {0, 1, 2, 8}
ALLOWED_REPRO_CODES = {0, 1, 2, 8, 9}


def season_start_year_from_date(value: str) -> int:
    """Map documented Nov-Jan observation dates to austral season start year."""
    try:
        observed = datetime.strptime(str(value).strip(), "%m/%d/%Y").date()
    except ValueError as exc:
        raise ValueError(f"invalid documented Ross date: {value!r}") from exc
    if observed.month in (11, 12):
        return observed.year
    if observed.month == 1:
        return observed.year - 1
    raise ValueError(
        f"off-window Ross observation month {observed.month}; "
        "primary contract permits Nov-Jan only"
    )


def cohort_start_year_from_season(value: str | int) -> int:
    text = str(value).strip()
    if len(text) != 4 or not text.isdigit():
        raise ValueError(f"invalid four-digit banding season: {value!r}")
    yy = int(text[:2])
    zz = int(text[2:])
    start = 1900 + yy if yy >= 90 else 2000 + yy
    if zz != (start + 1) % 100:
        raise ValueError(f"non-consecutive banding season: {value!r}")
    return start


def _as_int(value: object, name: str) -> int:
    if isinstance(value, bool):
        raise ValueError(f"{name} cannot be boolean")
    try:
        number = int(str(value).strip())
    except (TypeError, ValueError) as exc:
        raise ValueError(f"invalid {name}: {value!r}") from exc
    return number


def match_band_inventory(
    band: int | str,
    inventory_rows: Iterable[Mapping[str, object]],
) -> dict[str, object] | None:
    """Resolve one band to exactly one documented inclusive Low-High interval."""
    target = _as_int(band, "Band")
    matches: list[dict[str, object]] = []
    for row in inventory_rows:
        low = _as_int(row["Low"], "Low")
        high = _as_int(row["High"], "High")
        if low > high:
            raise ValueError(f"invalid band interval {low}>{high}")
        if low <= target <= high:
            colony = str(row["Colony"]).strip().upper()
            if colony not in STUDY_COLONIES:
                raise ValueError(f"unknown natal colony {colony!r}")
            season = cohort_start_year_from_season(row["Season"])
            matches.append(
                {
                    "band": target,
                    "natal_colony": colony,
                    "cohort_start_year": season,
                    "interval_low": low,
                    "interval_high": high,
                }
            )
    if not matches:
        return None
    if len(matches) != 1:
        unique = {
            (m["natal_colony"], m["cohort_start_year"])
            for m in matches
        }
        raise ValueError(
            f"band {target} matches {len(matches)} inventory intervals: "
            f"{sorted(unique)!r}"
        )
    return matches[0]


def _repro_code(value: object, field: str) -> int:
    code = _as_int(value, field)
    if code not in ALLOWED_REPRO_CODES:
        raise ValueError(f"unsupported {field} code {code}")
    return code


def _breeder_evidence(row: Mapping[str, object]) -> bool:
    eggs = _repro_code(row["Eggs"], "Eggs")
    chicks = _repro_code(row["Chicks"], "Chicks")
    return eggs in BREEDING_CODES or chicks in BREEDING_CODES


def _chick_presence(rows: Iterable[Mapping[str, object]]) -> int | None:
    interpretable: list[int] = []
    for row in rows:
        code = _repro_code(row["Chicks"], "Chicks")
        if code in INTERPRETABLE_CHICK_CODES:
            interpretable.append(code)
    if not interpretable:
        return None
    return int(any(code in BREEDING_CODES for code in interpretable))


def annualize_resights(
    observations: Iterable[Mapping[str, object]],
    inventory_rows: Iterable[Mapping[str, object]],
) -> list[dict[str, object]]:
    """Collapse canonical raw observations to one state record per band-season."""
    inventory = [dict(row) for row in inventory_rows]
    grouped: dict[tuple[int, int], list[dict[str, object]]] = defaultdict(list)

    for raw in observations:
        band = _as_int(raw["Band"], "Band")
        colony = str(raw["Colony"]).strip().upper()
        if colony not in STUDY_COLONIES:
            raise ValueError(f"unsupported colony code {colony!r}")
        season = season_start_year_from_date(str(raw["Date"]))
        row = {
            "Band": band,
            "Date": str(raw["Date"]).strip(),
            "Colony": colony,
            "Eggs": _repro_code(raw["Eggs"], "Eggs"),
            "Chicks": _repro_code(raw["Chicks"], "Chicks"),
            "season": season,
        }
        grouped[(band, season)].append(row)

    by_band: dict[int, list[dict[str, object]]] = defaultdict(list)
    provisional: list[dict[str, object]] = []

    for (band, season), rows in sorted(grouped.items()):
        natal = match_band_inventory(band, inventory)
        age = None if natal is None else season - int(natal["cohort_start_year"])
        if age is not None and age < 0:
            raise ValueError(f"band {band} observed before natal cohort season")

        visited_ross_set = {
            str(r["Colony"]) for r in rows if str(r["Colony"]) in ROSS_COLONIES
        }
        visited_ross = [c for c in ROSS_COLONIES if c in visited_ross_set]
        visited_all_set = {str(r["Colony"]) for r in rows}
        visited_all = [c for c in STUDY_COLONIES if c in visited_all_set]
        br_colonies = sorted(
            {
                str(r["Colony"])
                for r in rows
                if _breeder_evidence(r)
            }
        )
        breeding_colony = br_colonies[0] if len(br_colonies) == 1 else None
        chick_presence = (
            _chick_presence(
                r for r in rows if str(r["Colony"]) == breeding_colony
            )
            if breeding_colony is not None
            else None
        )
        record = {
            "band": band,
            "season": season,
            "age": age,
            "natal_colony": None if natal is None else natal["natal_colony"],
            "cohort_start_year": (
                None if natal is None else natal["cohort_start_year"]
            ),
            "visited_ross_colonies": visited_ross,
            "visited_study_colonies": visited_all,
            "breeding_evidence_colonies": br_colonies,
            "breeding_colony": breeding_colony,
            "breeder_chick_presence": chick_presence,
            "n_raw_resights": len(rows),
            "state": None,
        }
        provisional.append(record)
        by_band[band].append(record)

    for band, records in by_band.items():
        breeding_seasons = [
            int(r["season"])
            for r in records
            if len(r["breeding_evidence_colonies"]) >= 1
        ]
        first_breeding = min(breeding_seasons) if breeding_seasons else None
        for record in records:
            season = int(record["season"])
            br_colonies = record["breeding_evidence_colonies"]
            age = record["age"]

            if len(br_colonies) == 1:
                record["state"] = "BR"
            elif len(br_colonies) > 1:
                record["state"] = "AMBIG_BR"
            elif first_breeding is not None and season > first_breeding:
                record["state"] = "NB"
            elif (
                (first_breeding is None or season < first_breeding)
                and age is not None
                and int(age) >= 2
                and bool(record["visited_ross_colonies"])
            ):
                record["state"] = "PB"
            else:
                record["state"] = "OBS_OTHER"

            record["first_breeding_season_any_study_colony"] = first_breeding

    return sorted(provisional, key=lambda r: (int(r["band"]), int(r["season"])))


def banded_breeder_performance(
    annual_states: Iterable[Mapping[str, object]],
    *,
    minimum_eligible_breeders: int = 20,
) -> tuple[dict[int, dict[str, float]], dict[str, object]]:
    """Build frozen prior-year banded-breeder chick-presence index."""
    groups: dict[tuple[int, str], list[int]] = defaultdict(list)
    for row in annual_states:
        if row["state"] != "BR":
            continue
        colony = row.get("breeding_colony")
        if colony not in ROSS_COLONIES:
            continue
        presence = row.get("breeder_chick_presence")
        if presence not in (0, 1):
            continue
        groups[(int(row["season"]), str(colony))].append(int(presence))

    raw: dict[int, dict[str, float]] = defaultdict(dict)
    n_breeders: dict[int, dict[str, int]] = defaultdict(dict)
    for (season, colony), values in groups.items():
        n_breeders[season][colony] = len(values)
        if len(values) >= minimum_eligible_breeders:
            raw[season][colony] = float(np.mean(values))

    standardized: dict[int, dict[str, float]] = {}
    dropped: dict[int, str] = {}
    years = sorted(set(n_breeders) | set(raw))
    for year in years:
        if set(raw.get(year, {})) != set(ROSS_COLONIES):
            dropped[year] = "not_all_three_colonies_meet_minimum_breeders"
            continue
        values = np.asarray([raw[year][c] for c in ROSS_COLONIES], dtype=float)
        sd = float(np.std(values, ddof=1))
        if sd <= 0:
            dropped[year] = "zero_between_colony_performance_variance"
            continue
        z = (values - float(np.mean(values))) / sd
        standardized[year] = {
            colony: float(value)
            for colony, value in zip(ROSS_COLONIES, z)
        }

    audit = {
        "minimum_eligible_breeders": minimum_eligible_breeders,
        "n_breeders": {
            str(year): {c: int(n) for c, n in sorted(local.items())}
            for year, local in sorted(n_breeders.items())
        },
        "eligible_performance_years": sorted(standardized),
        "n_eligible_performance_years": len(standardized),
        "dropped_years": {str(y): reason for y, reason in sorted(dropped.items())},
    }
    return standardized, audit


def first_breeding_choice_events(
    annual_states: Iterable[Mapping[str, object]],
) -> list[dict[str, object]]:
    """Construct eligible event skeletons before adding performance/size values."""
    by_band: dict[int, list[dict[str, object]]] = defaultdict(list)
    for row in annual_states:
        by_band[int(row["band"])].append(dict(row))

    events: list[dict[str, object]] = []
    for band, records in sorted(by_band.items()):
        records.sort(key=lambda r: int(r["season"]))
        breeding = [
            r for r in records
            if r["state"] in {"BR", "AMBIG_BR"}
        ]
        if not breeding:
            continue
        first = min(breeding, key=lambda r: int(r["season"]))
        if first["state"] != "BR":
            continue
        chosen = first.get("breeding_colony")
        if chosen not in ROSS_COLONIES:
            continue
        natal = first.get("natal_colony")
        cohort = first.get("cohort_start_year")
        if natal is None or cohort is None:
            continue

        y = int(first["season"])
        lookback = {y - 2, y - 1}
        candidate = sorted(
            {
                colony
                for r in records
                if int(r["season"]) in lookback and r["state"] == "PB"
                for colony in r["visited_ross_colonies"]
            },
            key=lambda c: ROSS_COLONIES.index(c),
        )
        if len(candidate) < 2:
            continue
        if chosen not in candidate:
            continue

        events.append(
            {
                "event_id": f"{band}:{y}",
                "band": band,
                "first_breeding_season": y,
                "performance_year": y - 1,
                "chosen_colony": chosen,
                "candidate_colonies": candidate,
                "natal_colony": natal,
                "cohort_start_year": int(cohort),
                "age_at_first_breeding": y - int(cohort),
            }
        )
    return events


def build_choice_rows(
    events: Iterable[Mapping[str, object]],
    performance_by_year: Mapping[int, Mapping[str, float]],
    colony_size_by_year: Mapping[int, Mapping[str, float]],
) -> tuple[list[dict[str, object]], dict[str, object]]:
    """Attach frozen prior-year performance and size to candidate options."""
    rows: list[dict[str, object]] = []
    excluded: dict[str, str] = {}
    for event in events:
        event_id = str(event["event_id"])
        pyear = int(event["performance_year"])
        candidates = list(event["candidate_colonies"])
        performance = performance_by_year.get(pyear)
        sizes = colony_size_by_year.get(pyear)
        if performance is None:
            excluded[event_id] = "missing_three_colony_performance_year"
            continue
        if sizes is None:
            excluded[event_id] = "missing_colony_size_year"
            continue
        if any(c not in performance for c in candidates):
            excluded[event_id] = "missing_candidate_performance"
            continue
        if any(c not in sizes for c in candidates):
            excluded[event_id] = "missing_candidate_colony_size"
            continue

        for colony in candidates:
            size = float(sizes[colony])
            if not np.isfinite(size) or size < 0:
                raise ValueError(
                    f"invalid colony size for {event_id}/{colony}: {size}"
                )
            rows.append(
                {
                    "event_id": event_id,
                    "first_breeding_season": int(event["first_breeding_season"]),
                    "performance_year": pyear,
                    "candidate_colony": colony,
                    "chosen": int(colony == event["chosen_colony"]),
                    "performance_state": float(performance[colony]),
                    "natal_colony_indicator": int(
                        colony == event["natal_colony"]
                    ),
                    "log1p_colony_size": float(np.log1p(size)),
                }
            )

    return rows, {
        "input_events": len(list(events)) if not isinstance(events, list) else len(events),
        "retained_events": len({r["event_id"] for r in rows}),
        "retained_option_rows": len(rows),
        "excluded_events": excluded,
    }
