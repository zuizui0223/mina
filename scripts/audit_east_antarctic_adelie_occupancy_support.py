#!/usr/bin/env python3
"""Outcome-blind structural support audit for the East Antarctic Adelie occupancy dataset."""
from __future__ import annotations

import argparse
import json
import re
import shutil
import tempfile
import zipfile
from pathlib import Path

import pandas as pd


def norm(x: object) -> str:
    return re.sub(r"[^a-z0-9]+", " ", str(x).strip().lower()).strip()


def _header_role_score(values) -> int:
    """Score a prospective header row using schema words only."""
    cells=[norm(v) for v in values if not pd.isna(v) and str(v).strip()]
    roles=0
    roles += int(any("site" in x and any(k in x for k in ("code","id","breeding","geographic")) for x in cells))
    roles += int(any("season" in x or x == "year" for x in cells))
    roles += int(any("occupancy" in x or x in {"presence absence","present absent"} for x in cells))
    roles += int(any("latitude" in x or x == "lat" for x in cells))
    roles += int(any("longitude" in x or x in {"lon","long"} for x in cells))
    return roles*100 + len(cells)


def read_table(path: Path) -> pd.DataFrame | None:
    suffix = path.suffix.lower()
    try:
        if suffix == ".csv":
            for enc in ("utf-8-sig", "utf-8", "latin-1"):
                try:
                    return pd.read_csv(path, encoding=enc)
                except UnicodeDecodeError:
                    continue
            return None
        if suffix in {".xlsx", ".xls"}:
            book=pd.ExcelFile(path)
            candidates=[]
            for sheet in book.sheet_names:
                preview=pd.read_excel(path,sheet_name=sheet,header=None,nrows=50)
                best_row=0
                best_score=-1
                for idx in range(len(preview)):
                    score=_header_role_score(preview.iloc[idx].tolist())
                    if score>best_score:
                        best_score=score
                        best_row=idx
                # Require at least one structural role before preferring a sheet.
                role_count=best_score//100
                if role_count>0:
                    frame=pd.read_excel(path,sheet_name=sheet,header=best_row)
                    frame.attrs["sheet_name"]=str(sheet)
                    frame.attrs["header_row_zero_based"]=int(best_row)
                    candidates.append((role_count,best_score,len(frame),frame))
            if candidates:
                candidates.sort(key=lambda z:(z[0],z[1],z[2]),reverse=True)
                return candidates[0][3]
            return pd.read_excel(path)
    except Exception:
        return None
    return None


def role_columns(columns: list[str]) -> dict[str, list[str]]:
    roles = {"site": [], "season": [], "occupancy": [], "lat": [], "lon": [], "method": []}
    for c in columns:
        n = norm(c)
        if (
            n in {"site", "site id", "site code", "breeding site", "breeding site id", "breeding site code", "geographic site", "geographic site id", "geographic site code"}
            or ("site" in n and ("id" in n or "code" in n))
        ):
            roles["site"].append(c)
        if any(k in n for k in ("season", "year", "date")) or "breeding season" in n:
            roles["season"].append(c)
        if any(k in n for k in ("occupancy", "occupied", "presence", "status", "breeding present")):
            roles["occupancy"].append(c)
        if n in {"latitude", "lat", "centroid latitude"} or "latitude" in n:
            roles["lat"].append(c)
        if n in {"longitude", "lon", "long", "centroid longitude"} or "longitude" in n:
            roles["lon"].append(c)
        if any(k in n for k in ("method", "source", "observer", "reference", "survey")):
            roles["method"].append(c)
    return roles


def distinct_nonmissing(series: pd.Series) -> int:
    vals = series.dropna().astype(str).str.strip()
    vals = vals[vals.ne("")]
    return int(vals.nunique())


def audit_table(path: Path, frame: pd.DataFrame) -> dict:
    cols = [str(c) for c in frame.columns]
    roles = role_columns(cols)
    out = {
        "file": path.name,
        "rows": int(len(frame)),
        "columns": cols,
        "sheet_name": frame.attrs.get("sheet_name"),
        "inferred_header_row_zero_based": frame.attrs.get("header_row_zero_based"),
        "roles": roles,
        "nonmissing_counts": {},
    }
    for role, cs in roles.items():
        out["nonmissing_counts"][role] = {
            c: int(frame[c].notna().sum()) for c in cs if c in frame.columns
        }

    # Support summaries use only identifiers/time metadata, never occupancy values.
    if roles["site"]:
        sc = roles["site"][0]
        out["unique_sites"] = distinct_nonmissing(frame[sc])
        counts = frame[sc].dropna().astype(str).str.strip().value_counts()
        out["sites_with_rows_ge2"] = int((counts >= 2).sum())
        out["sites_with_rows_ge3"] = int((counts >= 3).sum())
        out["sites_with_rows_ge5"] = int((counts >= 5).sum())
    if roles["season"]:
        tc = roles["season"][0]
        out["unique_time_values"] = distinct_nonmissing(frame[tc])
    if roles["site"] and roles["season"]:
        sc, tc = roles["site"][0], roles["season"][0]
        x = frame[[sc, tc]].dropna().copy()
        x[sc] = x[sc].astype(str).str.strip()
        x[tc] = x[tc].astype(str).str.strip()
        site_seasons = x.groupby(sc)[tc].nunique()
        out["sites_with_distinct_times_ge2"] = int((site_seasons >= 2).sum())
        out["sites_with_distinct_times_ge3"] = int((site_seasons >= 3).sum())
        out["sites_with_distinct_times_ge5"] = int((site_seasons >= 5).sum())
        out["duplicate_site_time_rows"] = int(x.duplicated([sc, tc]).sum())
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--package", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    a = ap.parse_args()

    work = Path(tempfile.mkdtemp(prefix="adelie_occ_"))
    extracted = work / "data"
    extracted.mkdir(parents=True, exist_ok=True)

    package_type = "file"
    if zipfile.is_zipfile(a.package):
        package_type = "zip"
        with zipfile.ZipFile(a.package) as z:
            z.extractall(extracted)
            members = z.namelist()
    else:
        members = [a.package.name]
        shutil.copy2(a.package, extracted / a.package.name)

    tables = []
    for path in sorted(extracted.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in {".csv", ".xlsx", ".xls"}:
            continue
        frame = read_table(path)
        if frame is None:
            tables.append({"file": str(path.relative_to(extracted)), "readable": False})
            continue
        result = audit_table(path, frame)
        result["file"] = str(path.relative_to(extracted))
        result["readable"] = True
        tables.append(result)

    # Candidate observation table = strongest schema overlap with site/time/occupancy roles.
    candidates = []
    for t in tables:
        if not t.get("readable"):
            continue
        roles = t.get("roles", {})
        score = (
            4 * bool(roles.get("site"))
            + 4 * bool(roles.get("season"))
            + 5 * bool(roles.get("occupancy"))
            + 2 * bool(roles.get("lat"))
            + 2 * bool(roles.get("lon"))
            + min(int(t.get("rows", 0)), 10000) / 10000
        )
        candidates.append((score, t))
    candidates.sort(key=lambda x: x[0], reverse=True)
    selected = candidates[0][1] if candidates else None

    gate = {
        "stable_site_field": False,
        "time_field": False,
        "occupancy_field": False,
        "coordinates_in_same_table": False,
        "coordinate_table_available": False,
        "sites_with_repeated_observations_ge20": False,
        "distinct_time_values_ge5": False,
        "passes": False,
    }
    if selected:
        roles = selected.get("roles", {})
        gate["stable_site_field"] = bool(roles.get("site"))
        gate["time_field"] = bool(roles.get("season"))
        gate["occupancy_field"] = bool(roles.get("occupancy"))
        gate["coordinates_in_same_table"] = bool(roles.get("lat") and roles.get("lon"))
        gate["sites_with_repeated_observations_ge20"] = (
            int(selected.get("sites_with_distinct_times_ge2", 0)) >= 20
        )
        gate["distinct_time_values_ge5"] = int(selected.get("unique_time_values", 0)) >= 5

    # A separate site table can satisfy the coordinate requirement.
    coordinate_tables = [
        t for t in tables
        if t.get("readable")
        and t.get("roles", {}).get("site")
        and t.get("roles", {}).get("lat")
        and t.get("roles", {}).get("lon")
    ]
    gate["coordinate_table_available"] = bool(coordinate_tables)
    gate["passes"] = bool(
        gate["stable_site_field"]
        and gate["time_field"]
        and gate["occupancy_field"]
        and (gate["coordinates_in_same_table"] or gate["coordinate_table_available"])
        and gate["sites_with_repeated_observations_ge20"]
        and gate["distinct_time_values_ge5"]
    )

    out = {
        "schema_version": 1,
        "analysis_id": "mina-east-antarctic-adelie-occupancy-support-v1",
        "status": "outcome_blind_support_audit",
        "source": {
            "doi": "10.4225/15/57590498D301C",
            "download_endpoint": "https://data.aad.gov.au/eds/4345/download",
            "package_type": package_type,
            "package_members": members,
        },
        "tables": tables,
        "selected_candidate_observation_table": (
            selected.get("file") if selected else None
        ),
        "support_gate": gate,
        "effect_computed": False,
        "occupancy_value_counts_computed": False,
        "interpretation_boundary": [
            "No presence/absence value was summarized, compared, modeled, or plotted.",
            "This receipt establishes structural support only.",
            "A biological transition contract must be frozen before occupancy outcomes are opened."
        ],
    }
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(out, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
