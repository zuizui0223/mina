"""Schema gate for the Ross Island banding/resighting carrier benchmark."""
from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


def _norm(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", value.lower())


FIELD_PATTERNS = {
    "individual_id": (
        "bandnumber", "bandno", "bandid", "bandcode", "individualid",
        "birdid", "metalband", "band",
    ),
    "date_or_season": (
        "resightdate", "observationdate", "obsdate", "date",
        "season", "year", "breedingseason",
    ),
    "location": (
        "breedingcolony", "colony", "site", "location", "place",
        "resightlocation",
    ),
    "breeding_state": (
        "reproductivestate", "breedingstate", "breedingstatus",
        "reprostatus", "status", "neststatus", "nest", "egg", "chick",
    ),
    "effort": (
        "survey effort", "surveyeffort", "search effort", "searcheffort",
        "surveyoccasion", "searchoccasion", "effort",
    ),
    "banding_date": (
        "bandingdate", "banddate", "datebanded", "bandingseason",
        "bandingyear",
    ),
    "age": (
        "ageatbanding", "knownage", "age", "ageclass",
    ),
}


def _candidate_fields(fields: list[str], role: str) -> list[str]:
    patterns = tuple(_norm(x) for x in FIELD_PATTERNS[role])
    scored: list[tuple[int, str]] = []
    for field in fields:
        value = _norm(field)
        score = 0
        for pattern in patterns:
            if value == pattern:
                score = max(score, 100 + len(pattern))
            elif pattern and pattern in value:
                score = max(score, 10 + len(pattern))
        if score:
            scored.append((-score, field))
    return [field for _, field in sorted(scored)]


def inspect_csv(path: str | Path, *, sample_rows: int = 2000) -> dict[str, object]:
    with Path(path).open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        fields = list(reader.fieldnames or [])
        rows = []
        for idx, row in enumerate(reader):
            if idx >= sample_rows:
                break
            rows.append(row)
    if not fields:
        raise ValueError(f"CSV has no header: {path}")
    nonempty = {
        field: sum(
            str(row.get(field, "")).strip() not in {"", "NA", "NaN", "nan"}
            for row in rows
        )
        for field in fields
    }
    return {
        "path": str(path),
        "fields": fields,
        "sample_rows": len(rows),
        "sample_nonempty": nonempty,
        "candidates": {
            role: _candidate_fields(fields, role)
            for role in FIELD_PATTERNS
        },
    }


def _unique_primary(candidates: list[str]) -> str | None:
    return candidates[0] if candidates else None


def audit(
    resighting_path: str | Path,
    banding_path: str | Path | None = None,
) -> dict[str, object]:
    resight = inspect_csv(resighting_path)
    banding = inspect_csv(banding_path) if banding_path is not None else None

    rc = resight["candidates"]
    resight_id = _unique_primary(rc["individual_id"])
    resight_time = _unique_primary(rc["date_or_season"])
    resight_location = _unique_primary(rc["location"])
    resight_state = _unique_primary(rc["breeding_state"])
    resight_effort = _unique_primary(rc["effort"])

    stable_identity_gate = bool(resight_id)
    spatial_transition_gate = bool(
        stable_identity_gate and resight_time and resight_location
    )

    band_id = None
    band_time = None
    band_age = None
    if banding is not None:
        bc = banding["candidates"]
        band_id = _unique_primary(bc["individual_id"])
        band_time = _unique_primary(bc["banding_date"]) or _unique_primary(
            bc["date_or_season"]
        )
        band_age = _unique_primary(bc["age"])

    known_age_gate = bool(
        banding is not None
        and resight_id
        and band_id
        and (band_time or band_age)
    )
    breeding_propensity_gate = bool(
        stable_identity_gate
        and resight_time
        and resight_location
        and resight_state
        and resight_effort
    )

    return {
        "schema_version": 1,
        "analysis_id": "mina-ross-island-carrier-schema-gate-v1",
        "resighting": resight,
        "banding": banding,
        "selected_fields": {
            "resighting_individual_id": resight_id,
            "resighting_time": resight_time,
            "resighting_location": resight_location,
            "resighting_breeding_state": resight_state,
            "resighting_effort": resight_effort,
            "banding_individual_id": band_id,
            "banding_time": band_time,
            "banding_age": band_age,
        },
        "gates": {
            "stable_individual_identity": stable_identity_gate,
            "conditional_location_transition": spatial_transition_gate,
            "known_age_filter": known_age_gate,
            "breeding_propensity_model": breeding_propensity_gate,
        },
        "decision": {
            "can_run_B1_conditional_location_fidelity": spatial_transition_gate,
            "can_run_known_age_primary": known_age_gate,
            "can_unlock_B3_breeding_propensity": breeding_propensity_gate,
        },
        "interpretation_boundary": {
            "missing_resight_is_nonbreeding": False,
            "encounter_gap_is_sabbatical": False,
            "automatic_field_detection_is_final_semantic_validation": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--resighting", required=True, type=Path)
    parser.add_argument("--banding", type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    result = audit(args.resighting, args.banding)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
