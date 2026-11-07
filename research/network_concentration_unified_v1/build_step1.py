#!/usr/bin/env python3
"""Rebuild a two-endpoint network x species macroecology ledger.

Step 1 only: lock metadata-defined endpoints before reading count magnitudes.
This is a NEW harmonization, not a reproduction of previous source effects.
Runs within the existing mina PR206 branch; never edits frozen Paper 1.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import itertools
import json
import math
import re
import sys
import zipfile
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from geographiclib.geodesic import Geodesic

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "research/network_concentration_unified_v1"
DATA = BASE / "data"
OUT = BASE / "outputs"
SRC = ROOT / "research/climate-penguin/outputs"
SCHEMA = json.loads((BASE / "SCHEMA.json").read_text(encoding="utf8"))
MAP_SHA = "fcb622814d9aec674fb34ff5f8acd357f5508cf4bc1c63945e62d0c558fbc3c1"
EMP_SHA = "c887b9e1176b153345073281ebcaf6752ffb361023269afb5bdcfa371ec381ec"
JNCC_SHA = "9edf05b8af0a44c3ca770f390120c4b99bcaae3ae35fd844a82982d6ad8116d4"
PAL_SHA = "b4ef04e2275ea779fc8fe54fa13528dc2052d37dd88a60c811d54c7601f67b16"
SIGNY_SHA = {
    "ADPE": "585f87928ed64d8982ef5bd86d8a785c38df65c39223d88ec17425854c786d62",
    "CHPE": "e50e98719ba5eedc6f5e617e0c7aa404ebfba15bc22a51e93e78cd4443bf787b",
}
SEED_BASE = "20261106"
B = 20000
FOCAL = {"ADPE", "CHPE", "GEPE"}


def sha(value):
    if not isinstance(value, str):
        value = json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(value.encode("utf8")).hexdigest()


def read_source(path, expected=None, required=False):
    if not path.exists():
        if required:
            raise FileNotFoundError(str(path))
        return None
    raw = path.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if expected and digest != expected:
        raise ValueError(f"Frozen source hash mismatch: {path} {digest} != {expected}")
    return raw


def read_csv_bytes(raw):
    import io
    return list(csv.DictReader(io.StringIO(raw.decode("utf-8-sig"), newline="")))


def columns(table):
    return list(SCHEMA["properties"][table]["items"]["required"])


def blank(table):
    return dict.fromkeys(columns(table))


def write_csv(path, table, records):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf8") as f:
        w = csv.DictWriter(f, fieldnames=columns(table))
        w.writeheader()
        for x in records:
            y = dict(x)
            for k, v in y.items():
                if isinstance(v, (dict, list)):
                    y[k] = json.dumps(v, ensure_ascii=False, separators=(",", ":"))
                elif v is None:
                    y[k] = ""
            w.writerow(y)


def read_csv(path):
    return read_csv_bytes(path.read_bytes())


def number(v):
    if v is None or str(v).strip() == "":
        return None
    try:
        x = float(v)
    except (ValueError, TypeError):
        return None
    return x if math.isfinite(x) and x >= 0 else None


def parse_int_count(v):
    x = number(v)
    return int(x) if x is not None and x.is_integer() else None


def fixed_cohort(components):
    return sha(sorted(c["cid"] for c in components)) if components else None


def component(cid, raw0, raw1, y0, y1, lat=None, lon=None, method0=None, method1=None, rawspecies=None, loc0=None, loc1=None, physical=None):
    return dict(cid=cid, raw0=raw0, raw1=raw1, y0=y0, y1=y1,
                lat=lat, lon=lon, method0=method0, method1=method1,
                rawspecies=rawspecies, loc0=loc0, loc1=loc1, physical=physical)


def candidate(dataset, net, species, unit, rule, sourceid, role, typ, scale,
              components=None, y0=None, y1=None, pair_count=0, reason=None, status=None,
              parent=None, lineage=None, estimate="recorded_count", coords="complete_original"):
    cs = sorted(components or [], key=lambda c: c["cid"])
    return dict(kind="network_species", dataset=dataset, network=net, species=species,
                unit=unit, rule=rule, sourceids=[sourceid], role=role, typ=typ, scale=scale,
                components=cs, y0=y0, y1=y1, pair_count=pair_count, reason=reason,
                status=status or ("locked" if cs else "not_estimable"), parent=parent,
                lineage=lineage or sourceid, estimate=estimate, coords=coords)


def pair_candidate(dataset, net, a, b, ua, ub, rule, sourceid, comps=None, y0=None, y1=None, count=0, reason=None):
    return dict(kind="network_species_pairs", dataset=dataset, network=net, a=a, b=b,
                ua=ua, ub=ub, rule=rule, sourceids=[sourceid], role="macro_primary",
                components=sorted(comps or [], key=lambda c: c["cid"]), y0=y0, y1=y1,
                pair_count=count, reason=reason, status="locked" if comps else "not_estimable",
                lineage=sourceid)


def source_meta(rec):
    return rec.get("n_counts") == "1" and rec.get("n_methods") == "1" and rec.get("method") not in ("", "unknown", None)


def build_candidates(root):
    result = []
    loaded = {}
    map_raw = read_source(SRC / "comparison_audit/mapppd_unambiguous_site_seasons.csv", MAP_SHA, True)
    loaded["mapppd_pygoscelis"] = hashlib.sha256(map_raw).hexdigest()
    rows = read_csv_bytes(map_raw)
    groups = defaultdict(lambda: defaultdict(dict))
    for ri, r in enumerate(rows, 2):
        if r["species_id"] not in FOCAL or not r["region"] or not r["site_id"]:
            continue
        key = (r["region"], r["species_id"])
        year = int(r["season"])
        if year in groups[key][r["site_id"]]:
            raise ValueError(f"duplicate MAPPPD site/species/year: {key} {r['site_id']} {year}")
        r["_line"] = ri
        groups[key][r["site_id"]][year] = r

    def shared(records, y0, y1):
        comp = []
        for site, years in records.items():
            p, q = years.get(y0), years.get(y1)
            if not (p and q and source_meta(p) and source_meta(q) and p["method"] == q["method"]):
                continue
            if p["latitude"] != q["latitude"] or p["longitude"] != q["longitude"]:
                continue  # no silently changing component geolocation
            comp.append(component("MAPPPD::"+site, p["count"], q["count"], y0, y1,
                                  p["latitude"], p["longitude"], p["method"], q["method"],
                                  loc0=f"mapppd.csv:{p['_line']}", loc1=f"mapppd.csv:{q['_line']}",
                                  physical="MAPPPD::"+site))
        return comp

    for (region, species), recs in sorted(groups.items()):
        years = sorted({y for bysite in recs.values() for y in bysite})
        possible = [(a, b, shared(recs, a, b)) for a, b in itertools.combinations(years, 2)]
        viable = [(a, b, cs) for a, b, cs in possible if len(cs) >= 3]
        viable.sort(key=lambda p: (p[0], -p[1]))
        selected = viable[0] if viable else (None, None, [])
        y0, y1, comps = selected
        result.append(candidate("MAPPPD", "MAPPPD::"+region, species, "nest",
              "mapppd_earliest_then_latest_available_pair", "mapppd_pygoscelis",
              "macro_primary", "original_source_site", "regional_network", comps,
              y0, y1, len(viable), None if viable else "no_3_same_method_shared_sites",
              lineage="mapppd_pinned_88c73a5_field_count_lineage"))

    for region in sorted({x[0] for x in groups}):
        species = sorted(sp for rg, sp in groups if rg == region)
        for a, b in itertools.combinations(species, 2):
            aa, bb = groups[(region, a)], groups[(region, b)]
            years = sorted({y for years_by_site in aa.values() for y in years_by_site}
                           | {y for years_by_site in bb.values() for y in years_by_site})
            # no abundance values are consulted when selecting pair endpoints
            valid = []
            for y0, y1 in itertools.combinations(years, 2):
                ac = {c["cid"]: c for c in shared(aa, y0, y1)}
                bc = {c["cid"]: c for c in shared(bb, y0, y1)}
                ids = sorted(set(ac) & set(bc))
                if len(ids) >= 3:
                    valid.append((y0, y1, [dict(cid=cid, A=ac[cid], B=bc[cid]) for cid in ids]))
            valid.sort(key=lambda p: (p[0], -p[1]))
            y0, y1, cs = valid[0] if valid else (None, None, [])
            result.append(pair_candidate("MAPPPD", "MAPPPD::"+region, a, b, "nest", "nest",
               "pair_mapppd_earliest_then_latest_shared_available_pair", "mapppd_pygoscelis",
               cs, y0, y1, len(valid), None if cs else "no_3_common_species_site_epoch_units"))

    ross_ids = ["BRDM", "BRDN", "BRDS", "CRZE", "CRZW", "ROYD"]
    recs = {s: groups[("Victoria Land", "ADPE")].get(s, {}) for s in ross_ids}
    cs = shared(recs, 1985, 2024)
    if len(cs) != 6 or any(c["method0"] != "aerial" for c in cs):
        cs = []
    result.append(candidate("Ross_MAPPPD", "ROSS::Ross Island", "ADPE", "nest",
         "fixed_ross_1985_2024", "ross_within_island", "local_resolution",
         "MAPPPD_aerial_sector", "within_island", cs, 1985 if cs else None,
         2024 if cs else None, int(bool(cs)), None if cs else "ross_six_source_sectors_incomplete",
         parent="MAPPPD::Victoria Land", lineage="mapppd_pinned_88c73a5_field_count_lineage"))

    emperor_raw = read_source(SRC / "emperor_ice_land_substrate_v1/author_colony_summary.csv", EMP_SHA, True)
    loaded["emperor_author_index"] = hashlib.sha256(emperor_raw).hexdigest()
    emp = read_csv_bytes(emperor_raw)
    bysec = defaultdict(lambda: defaultdict(dict))
    for ri, r in enumerate(emp, 2):
        y = int(r["year"])
        sec, site = r["ice_reg"], r["site_id"]
        if site in bysec[sec][y]:
            raise ValueError("emperor original duplicated site-year")
        r["_line"] = ri
        bysec[sec][y][site] = r
    for sec, epoch in sorted(bysec.items()):
        ids = sorted(set(epoch.get(2009, {})) & set(epoch.get(2018, {})))
        cs = []
        for site in ids:
            a, b = epoch[2009][site], epoch[2018][site]
            cs.append(component("EMPE_Global::"+site, a["N_mean"], b["N_mean"], 2009, 2018,
                                a["lat"], a["lon"], "model_posterior_mean", "model_posterior_mean",
                                loc0=f"emperor.csv:{a['_line']}", loc1=f"emperor.csv:{b['_line']}"))
        result.append(candidate("EMPE_Global", "EMPE_Global::"+sec, "EMPE", "adult_index",
              "fixed_emperor_2009_2018", "emperor_author_index", "model_index_reference",
              "author_colony_site", "sector_network", cs, 2009, 2018, 1,
              lineage="emperor_author_posterior_summary", estimate="model_posterior_mean"))

    pal_path = root / "build/step1_inputs/palmer.csv"
    pal_raw = read_source(pal_path, PAL_SHA)
    if pal_raw is not None:
        loaded["palmer_within_island"] = hashlib.sha256(pal_raw).hexdigest()
    p_rows = read_csv_bytes(pal_raw) if pal_raw else []
    pal_by = defaultdict(lambda: defaultdict(dict))
    for i, r in enumerate(p_rows, 2):
        if r.get("island_name") not in {"COR", "HUM", "LIT"} or not r.get("colony_code"):
            continue
        if r.get("num_breeding_pairs") in ("", "NaN", "nan", None):
            continue
        try:
            year = int(r["time"][:4])
        except ValueError:
            continue
        pal_by[r["island_name"]][year][r["colony_code"]] = (r, i)
    for island, K in [("COR", 7), ("HUM", 9), ("LIT", 9)]:
        start = pal_by[island].get(1991, {})
        end = pal_by[island].get(2017, {})
        cs = []
        if len(start) == K and set(start) == set(end):
            for name in sorted(start):
                a, i0 = start[name]
                b, i1 = end[name]
                cs.append(component("Palmer_LTER::"+island+"::"+name,
                    a["num_breeding_pairs"], b["num_breeding_pairs"], 1991, 2017,
                    method0="annual_colony_census", method1="annual_colony_census",
                    loc0=f"palmer.csv:{i0}", loc1=f"palmer.csv:{i1}"))
        result.append(candidate("Palmer_LTER", "PALMER::"+island, "ADPE", "breeding_pair",
            "fixed_palmer_1991_2017", "palmer_within_island",
            "local_resolution" if cs else "input_recovery_pending",
            "monitored_colony_code", "within_island", cs, 1991 if cs else None,
            2017 if cs else None, int(bool(cs)),
            None if cs else "palmer_source_unavailable_or_roster_changed",
            status="locked" if cs else "pending_recovery",
            coords="unavailable", lineage="palmer_colony_code_LTER"))

    for species, urlname, labels in [
        ("ADPE", "signy_adelie.zip", ["A1+A60", "A2", "A3", "A4", "A64"]),
        ("CHPE", "signy_chinstrap.zip", ["C15", "C16", "C17", "C18", "C46", "C47", "C79", "C80", "C81"])
    ]:
        zpath = root / "build/step1_inputs" / urlname
        signy = {}
        if zpath.exists():
            with zipfile.ZipFile(zpath) as z:
                matches = [(name, z.read(name)) for name in z.namelist()
                           if name.lower().endswith(".csv") and
                           hashlib.sha256(z.read(name)).hexdigest() == SIGNY_SHA[species]]
            if len(matches) != 1:
                raise ValueError(f"Signy source exact CSV hash not unique: {species} {len(matches)}")
            fname, raw = matches[0]
            loaded["signy_within_island_"+species] = hashlib.sha256(raw).hexdigest()
            import io
            # Source has occasional unquoted commas in the FINAL comments column.
            lines = list(csv.reader(io.StringIO(raw.decode("utf-8-sig", errors="replace"))))
            head = lines[0]
            for ii, values in enumerate(lines[1:], 2):
                if len(values) > len(head):
                    values = values[:len(head)-1] + [",".join(values[len(head)-1:])]
                elif len(values) < len(head):
                    values += [""]*(len(head)-len(values))
                r = dict(zip(head, values))
                rawyear = str(r.get("SEASON", "")).strip()
                match = re.match(r"^(\d{4})[-/]", rawyear)
                if not match:
                    continue
                y = int(match.group(1))
                if y not in (1996, 2019):
                    continue
                label = str(r.get("COLONY", "")).strip().replace(" ", "")
                if species == "ADPE" and label in {"A1", "A60", "A1+A60"}:
                    label = "A1+A60"
                signy.setdefault((y, label), []).append((r.get("TOTAL_NUMBER_OF_PAIRS", ""), ii))
        cs = []
        if all((y, label) in signy for y in (1996, 2019) for label in labels):
            for label in labels:
                a = signy[1996, label]
                b = signy[2019, label]
                # Preserve every literal source cell for the pooled A1+A60 unit.
                def pool(items):
                    ns = [number(v) for v, _ in items]
                    return str(sum(ns)) if all(v is not None for v in ns) else None
                cs.append(component("Signy::"+species+"::"+label,
                    pool(a), pool(b), 1996, 2019, method0="canonical_breeding_pair",
                    method1="canonical_breeding_pair",
                    loc0="signy.csv:"+",".join(str(x[1]) for x in a),
                    loc1="signy.csv:"+",".join(str(x[1]) for x in b)))
        result.append(candidate("BAS_Signy", "SIGNY::Signy Island", species, "breeding_pair",
            "fixed_signy_1996_2019", "signy_within_island",
            "local_resolution" if cs else "input_recovery_pending",
            "canonical_monitored_colony", "within_island", cs,
            1996 if cs else None, 2019 if cs else None, int(bool(cs)),
            None if cs else "signy_source_unavailable_or_canonical_endpoint_incomplete",
            status="locked" if cs else "pending_recovery",
            coords="unavailable", lineage="signy_source_"+species))

    jpath = root / "build/step1_inputs/jncc.xlsx"
    jraw = read_source(jpath, JNCC_SHA)
    if jraw is None:
        result.append(candidate("JNCC", "JNCC::SOURCE_RECOVERY", "PENDING", "unresolved",
            "no_comparable_rule", "jncc_revised_20240708", "input_recovery_pending",
            "original_site_id", "master_site_network", reason="jncc_original_workbook_not_recovered",
            status="pending_recovery", coords="complete_source_start_points", estimate="adjusted_count"))
    else:
        loaded["jncc_revised_20240708"] = hashlib.sha256(jraw).hexdigest()
        sys.path.insert(0, str(root / "build/step1_inputs/jncc_code"))
        import audit_jncc_comparable_site_panels_v29 as v29
        import model_jncc_component_concentration_v30 as v30
        jrows = list(v29.original_rows(jraw))
        v29qa = v29.coverage(jrows)
        if (v29qa["unique_original_two_census_site_species_rows_after_literal_QA"] != 14112
                or v29qa["qualified_species_country_master_unit_panels_with_ge3_sites"] != 1485):
            raise ValueError("JNCC frozen V29 structural gate drift")
        safe, qa = v30.extract_structural(jrows)
        if len(safe) != 1483:
            raise ValueError(f"JNCC V30 original structural panels changed: {len(safe)}")
        jmeta = defaultdict(list)
        for (species, country, master, unit), group in sorted(safe.items()):
            yrs0 = {r["year_2000"] for r, src in group}
            yrs1 = {r["year_recent"] for r, src in group}
            synchronous = len(yrs0)==len(yrs1)==1
            y0, y1 = (next(iter(yrs0)), next(iter(yrs1))) if synchronous else (None, None)
            cs = []
            if synchronous and y1 > y0:
                for r, src in group:
                    id = f"JNCC::{country}::{master}::{r['site_id']}"
                    cs.append(component(id, src.get("L"), src.get("O"), y0, y1,
                        r["lat"], r["lon"], "adjusted_count", "adjusted_count",
                        rawspecies=r["species"],
                        loc0=f"jncc.xlsx:{r['source_sheet']}:{r['source_row']}:L",
                        loc1=f"jncc.xlsx:{r['source_sheet']}:{r['source_row']}:O",
                        physical=id))
            net = f"JNCC::{country}::{master}"
            result.append(candidate("JNCC", net, species, unit, "jncc_v39_exact_years",
                "jncc_revised_20240708", "macro_primary" if cs else "descriptive_only",
                "original_site_id", "master_site_network", cs, y0, y1, int(bool(cs)),
                None if cs else "asynchronous_original_site_census_years",
                status="locked" if cs else "not_estimable",
                coords="complete_source_start_points", estimate="adjusted_count",
                lineage="jncc_country_master_"+country+"_"+master))
            if cs:
                jmeta[net].append((species, unit, y0, y1, {c["cid"]:c for c in cs}))
        for net, members in jmeta.items():
            for (a, ua, ya0, ya1, ac), (b, ub, yb0, yb1, bc) in itertools.combinations(sorted(members), 2):
                if a == b:
                    continue
                ids = sorted(set(ac) & set(bc))
                matched = []
                if (ya0, ya1)==(yb0, yb1) and len(ids) >= 3:
                    # Shared Site.ID and coordinates: original site-based overlap only,
                    # not a proven physical colony-polygon overlap.
                    for cid in ids:
                        ca, cb = ac[cid], bc[cid]
                        if ca["lat"] != cb["lat"] or ca["lon"] != cb["lon"]:
                            continue
                        matched.append(dict(cid=cid, A=ca, B=cb))
                if len(matched) < 3:
                    matched = []
                result.append(pair_candidate("JNCC", net, a, b, ua, ub,
                    "pair_jncc_exact_shared_census_years", "jncc_revised_20240708",
                    matched, ya0 if matched else None, ya1 if matched else None,
                    int(bool(matched)),
                    None if matched else "no_verified_same_site_id_same_year_pair"))

    return result, loaded


def candidate_key(c):
    if c["kind"] == "network_species":
        return [c["dataset"], c["network"], c["species"], c["unit"]]
    return [c["dataset"], c["network"], c["a"], c["b"], c["ua"], c["ub"]]


def candidate_ids(c):
    co = fixed_cohort(c["components"])
    if c["kind"] == "network_species":
        v = [c["dataset"], c["network"], c["species"], c["unit"], co, c["y0"], c["y1"]]
    else:
        v = [c["dataset"], c["network"], c["a"], c["b"], c["ua"], c["ub"], co, c["y0"], c["y1"]]
    return sha(v), co


def registry_record(c, actual_sha, timestamp):
    row, co = candidate_ids(c)
    entry = blank("endpoint_registry")
    entry.update(candidate_id=sha(candidate_key(c)), row_id=row,
                 dataset_id=c["dataset"], network_id=c["network"],
                 species_id=c.get("species"), count_unit=c.get("unit"),
                 endpoint_rule=c["rule"], year0=c["y0"], year1=c["y1"],
                 component_ids=[x["cid"] for x in c["components"]], cohort_id=co,
                 epoch_sync_status="synchronous" if co else
                 ("asynchronous" if c["dataset"] == "JNCC" and c["status"] == "not_estimable"
                  else "unresolved"),
                 candidate_pair_count=c["pair_count"],
                 selection_basis="source_metadata_presence_ID_method_and_exact_census_years_only",
                 selection_status=c["status"],
                 non_estimation_reasons=[] if co else [c["reason"] or "no_supported_pair"],
                 source_ids=c["sourceids"],
                 source_sha256s=[actual_sha[s] for s in c["sourceids"] if s in actual_sha],
                 locked_at_utc=timestamp, analysis_unit=c["kind"],
                 species_a=c.get("a"), species_b=c.get("b"),
                 count_unit_a=c.get("ua"), count_unit_b=c.get("ub"))
    return entry


def extent_and_status(comps, coordinate_label):
    coords = [(float(c["lat"]), float(c["lon"])) for c in comps if
              c.get("lat") not in (None, "") and c.get("lon") not in (None, "") and
              math.isfinite(float(c["lat"])) and math.isfinite(float(c["lon"]))]
    if len(coords) != len(comps) or not coords:
        return None, "unavailable" if coordinate_label=="unavailable" else "incomplete"
    d = max((Geodesic.WGS84.Inverse(a[0],a[1],b[0],b[1])["s12"]
             for a, b in itertools.combinations(coords, 2)), default=0)
    return d/1000.0, coordinate_label


def metric(x):
    x = np.array(x, dtype=float)
    N = float(x.sum())
    return None if N <= 0 else float(N*N/float(x@x))


def null_distribution(a, b, dt, rowid, overlap=False, c=None, d=None):
    seed = int(sha(SEED_BASE+"|"+rowid)[:8],16)
    rng = np.random.default_rng(seed)
    if not overlap:
        x0, x1 = np.asarray(a, dtype=np.int64), np.asarray(b, dtype=np.int64)
        t0, t1 = int(x0.sum()), int(x1.sum())
        pool = (x0+x1)/(t0+t1)
    else:
        x0, x1, y0, y1 = [np.asarray(q, dtype=np.int64) for q in (a,b,c,d)]
        t0, t1, u0, u1 = int(x0.sum()), int(x1.sum()), int(y0.sum()), int(y1.sum())
        pool = (x0+x1)/(t0+t1)
        pool2 = (y0+y1)/(u0+u1)
    simulated = []
    for start in range(0, B, 500):
        n = min(500, B-start)
        s0, s1 = rng.multinomial(t0, pool, size=n), rng.multinomial(t1, pool, size=n)
        if not overlap:
            h0 = np.sum((s0/t0)**2,axis=1)
            h1 = np.sum((s1/t1)**2,axis=1)
            val = (10.0/dt)*np.log(h1/h0)
        else:
            q0, q1 = rng.multinomial(u0, pool2, size=n), rng.multinomial(u1, pool2, size=n)
            o0 = np.minimum(s0/t0,q0/u0).sum(axis=1)
            o1 = np.minimum(s1/t1,q1/u1).sum(axis=1)
            val = (10.0/dt)*(o1-o0)
        simulated.append(val)
    z = np.concatenate(simulated)
    sd = float(z.std(ddof=1))
    return [float(z.mean()),sd,float(np.quantile(z,.025)),
            float(np.quantile(z,.975)),sd/math.sqrt(B)]


def unit_records(c, entry):
    out = []
    co = entry["cohort_id"]
    if not co:
        return out
    for comp in c["components"]:
        for suffix, sub in ([(c.get("a"), comp["A"]), (c.get("b"), comp["B"])]
                            if c["kind"] == "network_species_pairs"
                            else [(c["species"],comp)]):
            for epoch, k in [("early","0"),("late","1")]:
                raw = sub["raw"+k]
                n = number(raw)
                u = blank("unit_endpoints")
                u.update(row_id=entry["row_id"],dataset_id=c["dataset"],
                         network_id=c["network"],species_id=suffix,
                         raw_species_label=sub.get("rawspecies") or suffix,
                         cohort_id=co,component_id=comp["cid"],
                         physical_unit_id=sub.get("physical"),
                         endpoint=epoch,year=entry["year"+k],
                         raw_season_label=str(sub["y"+k]),
                         count_value=n,raw_value=str(raw) if raw is not None else None,
                         count_status=("missing" if raw is None or str(raw).strip()=="" else
                                       "invalid" if n is None else
                                       "observed_zero" if n==0 else "observed_positive"),
                         count_unit=c.get("unit") if c["kind"]=="network_species" else
                                   (c["ua"] if suffix==c["a"] else c["ub"]),
                         estimate_type=c.get("estimate","recorded_count") if
                            c["kind"]=="network_species" else
                            ("adjusted_count" if c["dataset"]=="JNCC" else "recorded_count"),
                         method=sub["method"+k],latitude=(float(sub["lat"])
                            if sub["lat"] not in ("",None) else None),
                         longitude=(float(sub["lon"]) if sub["lon"] not in ("",None) else None),
                         coordinate_semantics=("original_start_point" if c["dataset"]=="JNCC" else
                                               "source_site_anchor" if sub["lat"] not in ("",None) else None),
                         source_id=c["sourceids"][0],source_record_id=None,
                         source_row_locator=sub["loc"+k] or "source_column_no_row_key",
                         lineage_group=c["lineage"],
                         analysis_unit=c["kind"])
                out.append(u)
    return out


def make_network(c, e):
    out = blank("network_species")
    co = e["cohort_id"]
    out.update(row_id=e["row_id"],dataset_id=c["dataset"],network_id=c["network"],
               species_id=c["species"],cohort_id=co,scale_class=c["scale"],
               component_type=c["typ"],parent_network_id=c.get("parent"),
               lineage_group=c["lineage"],year0=e["year0"],year1=e["year1"],
               dt_years=e["year1"]-e["year0"] if co else None,
               epoch_sync_status=e["epoch_sync_status"],K=len(c["components"]) if co else None,
               count_unit=c["unit"],estimate_type=c["estimate"],null_status="not_computed",
               coordinate_status="unavailable",endpoint_status="pending_recovery" if
               c["status"]=="pending_recovery" else "no_comparable_pair",
               analysis_role=c["role"],exclusion_reason=list(e["non_estimation_reasons"]),
               prior_view_status="previous_results_viewed",source_id=c["sourceids"][0])
    if not co:
        out["null_status"]=("input_recovery_pending" if c["status"]=="pending_recovery" else
            "asynchronous_epochs" if c["dataset"]=="JNCC" else "insufficient_components")
        return out
    x0=[number(q["raw0"]) for q in c["components"]]
    x1=[number(q["raw1"]) for q in c["components"]]
    if None in x0 or None in x1:
        out["endpoint_status"]="invalid_values"
        out["null_status"]="noninteger_count"
        out["exclusion_reason"].append("source_count_invalid")
        return out
    N0,N1=sum(x0),sum(x1)
    out.update(occupied0=sum(v>0 for v in x0),occupied1=sum(v>0 for v in x1),
               N0=N0,N1=N1)
    # These denominators require an independent full source network census inventory.
    out["surveyed_components0"]=None
    out["surveyed_components1"]=None
    out["coverage0"]=None
    out["coverage1"]=None
    out["neff0"]=metric(x0)
    out["neff1"]=metric(x1)
    ext,cs=extent_and_status(c["components"],c["coords"])
    out["extent_km"],out["coordinate_status"]=ext,cs
    out["endpoint_status"]=("positive_both" if N0>0 and N1>0 else
                "terminal_zero" if N0>0 else "origin_zero" if N1>0 else "both_zero")
    if N0>0:
        out["abundance_pct_change_interval"]=100*(N1/N0-1)
    if N0>0 and N1>0:
        dt=out["dt_years"]
        G=10.0/dt*math.log(N1/N0)
        out["abundance_log_change_decade"]=G
        out["abundance_pct_change_decade"]=100*math.expm1(G)
        out["concentration_raw_decade"]=-10.0/dt*math.log(out["neff1"]/out["neff0"])
    if c["estimate"]=="model_posterior_mean":
        out["null_status"]="model_joint_uncertainty_unavailable"
        out["exclusion_reason"].append("model_marginal_means_no_joint_count_null")
        return out
    if len(c["components"])<3:
        out["null_status"]="insufficient_components"
    elif N0<=0 or N1<=0:
        out["null_status"]="nonpositive_total"
    elif N0<2 or N1<2:
        out["null_status"]="total_below_two"
    elif any(parse_int_count(v) is None for v in x0+x1):
        out["null_status"]="noninteger_count"
    else:
        (m,sd,q0,q1,se)=null_distribution(x0,x1,dt,e["row_id"])
        out.update(null_mean_decade=m,null_sd_decade=sd,null_q025_decade=q0,
                   null_q975_decade=q1,null_mcse_decade=se,
                   concentration_excess_decade=out["concentration_raw_decade"]-m,
                   null_status="computed")
    return out


def make_pair(c,e):
    out=blank("network_species_pairs")
    co=e["cohort_id"]
    out.update(pair_row_id=e["row_id"],dataset_id=c["dataset"],network_id=c["network"],
               species_a=c["a"],species_b=c["b"],pair_cohort_id=co,
               year0=e["year0"],year1=e["year1"],
               dt_years=e["year1"]-e["year0"] if co else None,
               K_pair=len(c["components"]) if co else None,
               count_unit_a=c["ua"],count_unit_b=c["ub"],
               null_status="not_computed",coordinate_status="unavailable",
               analysis_role="macro_primary" if co else "descriptive_only",
               pair_status="eligible" if co else "insufficient_common_units",
               exclusion_reason=list(e["non_estimation_reasons"]),
               source_ids=c["sourceids"],lineage_group=c["lineage"])
    if not co:
        out["null_status"]="insufficient_components"
        return out
    q=c["components"]
    arrays = [[number(z[k]["raw"+t]) for z in q] for k,t in (("A","0"),("A","1"),("B","0"),("B","1"))]
    if any(None in x for x in arrays):
        out["null_status"]="noninteger_count"
        out["pair_status"]="invalid_values"
        return out
    a0,a1,b0,b1=arrays
    A0,A1,B0,B1=map(sum, arrays)
    out.update(N_a0=A0,N_a1=A1,N_b0=B0,N_b1=B1)
    out["extent_km"],out["coordinate_status"]=extent_and_status(
        [c["A"] for c in q],"complete_source_start_points" if c["dataset"]=="JNCC" else "complete_original")
    if min(A0,A1,B0,B1)<=0:
        out["pair_status"]="nonpositive_total"
        out["null_status"]="nonpositive_total"
        return out
    dt=out["dt_years"]
    Ga=(10/dt)*math.log(A1/A0)
    Gb=(10/dt)*math.log(B1/B0)
    o0=sum(min(x/A0,y/B0) for x,y in zip(a0,b0))
    o1=sum(min(x/A1,y/B1) for x,y in zip(a1,b1))
    out.update(G_a_decade=Ga,G_b_decade=Gb,pair_decline_decade=-(Ga+Gb)/2,
        overlap0=o0,overlap1=o1,overlap_raw_decade=(10/dt)*(o1-o0))
    if len(q)<3:
        out["null_status"]="insufficient_components"
    elif min(A0,A1,B0,B1)<2:
        out["null_status"]="total_below_two"
    elif any(parse_int_count(z) is None for ar in arrays for z in ar):
        out["null_status"]="noninteger_count"
    else:
        m,sd,l,u,se=null_distribution(a0,a1,dt,e["row_id"],True,b0,b1)
        out.update(overlap_excess_decade=out["overlap_raw_decade"]-m,
            null_mean_decade=m,null_sd_decade=sd,null_q025_decade=l,
            null_q975_decade=u,null_mcse_decade=se,null_status="computed")
    return out


def lock_registry(candidates, actualsha, timestamp):
    entries=[registry_record(c,actualsha,timestamp) for c in candidates]
    if len({e["row_id"] for e in entries})!=len(entries):
        raise ValueError("duplicate source/cohort/endpoint row_id")
    DATA.mkdir(parents=True,exist_ok=True)
    blob=(json.dumps(entries,ensure_ascii=False,indent=2)+"\n").encode("utf8")
    (DATA/"endpoint_registry.json").write_bytes(blob)
    (DATA/"endpoint_registry.sha256").write_text(hashlib.sha256(blob).hexdigest()+"\n")
    (DATA/"input_checksums.json").write_text(json.dumps(actualsha,indent=2)+"\n")
    return entries


def check_lock(candidates, sourcehash):
    raw=(DATA/"endpoint_registry.json").read_bytes()
    digest=hashlib.sha256(raw).hexdigest()
    if (DATA/"endpoint_registry.sha256").read_text().strip()!=digest:
        raise ValueError("endpoint registry changed after locking")
    old=json.loads(raw)
    if sourcehash!=json.loads((DATA/"input_checksums.json").read_text()):
        raise ValueError("original data source changed after endpoint lock")
    if len(old)!=len(candidates):
        raise ValueError("candidate number changed after endpoint lock")
    for e,c in zip(old,candidates):
        z=registry_record(c,sourcehash,e["locked_at_utc"])
        if z!=e:
            raise ValueError(f"endpoint selection changed after lock {e['row_id']}")
    return old


def readout(rows,pairs,regs,shas):
    result=Counter((r["dataset_id"],r["null_status"]) for r in rows)
    counts=Counter(r["null_status"] for r in rows)
    pair_counts=Counter(r["null_status"] for r in pairs)
    nmacro=sum(r["analysis_role"]=="macro_primary" and r["null_status"]=="computed" for r in rows)
    lines=[
        "# Step 1 — fixed-endpoint macroecology readout (new derived calculation)",
        "",
        "Source and endpoint lock: SHA256 `"+(DATA/"endpoint_registry.sha256").read_text().strip()+"`.",
        "B = 20,000 two-endpoint independent pooled-share multinomial draws per eligible count row.",
        "This is an arithmetic fixed-share benchmark, NOT an observation-error-calibrated ecological null.",
        "No Step 2–4 trait, SST, species-overlap regression or corrected p-values have been fitted.",
        "",
        f"Main network×species candidate records: **{len(rows)}**; computed count-null: **{counts['computed']}**; among macro-primary: **{nmacro}**.",
        f"Shared physical-site species-pair candidates: **{len(pairs)}**; computed count-null: **{pair_counts['computed']}**.",
        "",
        "## Count-null outcome support by source",
        "",
        "| Source | candidate rows | count-null computed | model/index/pending/nonestimable |",
        "|---|---:|---:|---:|",
    ]
    for s in sorted({r["dataset_id"] for r in rows}):
        rr=[x for x in rows if x["dataset_id"]==s]
        cc=sum(r["null_status"]=="computed" for r in rr)
        lines.append(f"| {s} | {len(rr)} | {cc} | {len(rr)-cc} |")
    lines.extend(["", "## Null noncomputation reasons", ""])
    lines += [f"- {k}: {v}" for k,v in sorted(counts.items())]
    lines.extend(["","## Pair noncomputation reasons",""])
    lines += [f"- {k}: {v}" for k,v in sorted(pair_counts.items())]
    lines.extend(["", "## Source integrity", ""])
    lines += [f"- `{k}`: `{v}`" for k,v in sorted(shas.items())]
    lines.extend(["","## Interpretation and checks", "",
        "- Matched site IDs are not interchangeable with physical islands. The UK JNCC network is a Country×Master-site administrative structure.",
        "- Original parent/child count records are not added as independent study replicates.",
        "- Local-resolution Palmer, Signy and Ross are not added to MAPPPD macro-primary as independent rows.",
        "- Emperor model-mean allocation is descriptive; without joint posterior draws the multinomial count null is not applied.",
        "- A terminal observed zero is retained, but Y is missing; zero totals are never replaced by last-positive census.",
        "- Null quantiles describe simulated counts, not 95% confidence intervals of the observed Y.",
        "- Surveys-per-epoch denominators and coordinate-derived island habitats are unknown unless the actual full original survey roster supports them; never equate the matched cohort with complete abundance coverage.",
        "- Census adjusted counts, source-site boundary shifts, time-span differences and observational effort can still influence results.",
        "- Sources whose originals cannot be byte-verified are retained as explicitly unresolved.",
        "- All results are post-prior-evidence exploratory, not externally preregistered.",
        ""])
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/"STEP1_READOUT.md").write_text("\n".join(lines),encoding="utf8")
    summary=dict(n_rows=len(rows),computed=counts["computed"],macro_primary_computed=nmacro,
                 n_pairs=len(pairs),pairs_computed=pair_counts["computed"],
                 null_status=dict(counts),pair_null_status=dict(pair_counts),
                 n_sources=len({r["source_id"] for r in rows}),registry_sha=(DATA/"endpoint_registry.sha256").read_text().strip())
    (OUT/"STEP1_QA.json").write_text(json.dumps(summary,indent=2)+"\n")
    print(json.dumps(summary,ensure_ascii=False))


def run(phase):
    candidates, shas = build_candidates(ROOT)
    if phase=="registry":
        timestamp=datetime.now(timezone.utc).isoformat(timespec="seconds")
        entries=lock_registry(candidates,shas,timestamp)
        print(json.dumps({"stage":"endpoint_lock","candidates":len(entries),
                          "selected":sum(e["selection_status"]=="locked" for e in entries),
                          "source_hashes":len(shas),
                          "lock_sha256":(DATA/"endpoint_registry.sha256").read_text().strip()}))
        return
    entries=check_lock(candidates,shas)
    units=[]
    for c,e in zip(candidates,entries):
        units.extend(unit_records(c,e))
    write_csv(DATA/"unit_endpoints.csv","unit_endpoints",units)
    if phase=="endpoints":
        print(json.dumps({"stage":"original_endpoint_counts","rows":len(units)}))
        return
    rows=[make_network(c,e) for c,e in zip(candidates,entries) if c["kind"]=="network_species"]
    pairs=[make_pair(c,e) for c,e in zip(candidates,entries) if c["kind"]=="network_species_pairs"]
    # Exact fixed-cohort sums and no duplicate primary source lineage
    for r in rows:
        if r["null_status"]=="computed" and not (r["N0"]>=2 and r["N1"]>=2 and r["K"]>=3):
            raise ValueError("Computed count null violates source/total gate")
        if r["concentration_excess_decade"] is not None:
            if abs(r["concentration_excess_decade"]-
                   (r["concentration_raw_decade"]-r["null_mean_decade"]))>1e-9:
                raise ValueError("Null-centered concentration identity broken")
    write_csv(DATA/"network_species.csv","network_species",rows)
    write_csv(DATA/"network_species_pairs.csv","network_species_pairs",pairs)
    readout(rows,pairs,entries,shas)


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--phase",required=True,choices=["registry","endpoints","outcomes"])
    a=p.parse_args()
    run(a.phase)


if __name__=="__main__":
    main()
