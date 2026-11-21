#!/usr/bin/env python3
"""SCAR original penguin bulk d15N: source-only species/site/season support gate.

Never estimates any isotope-vs-environment association. Source event counts are
NOT independent prey samples or proven colony identification.
"""
import argparse
import collections
import csv
import datetime as dt
import hashlib
import io
import json
import math
import pathlib
import re
import zipfile

ARCHIVE_MD5 = "5e098c268ce0028704bc4b06300cb0ef"
ARCHIVE_BYTES = 9543574
OLD_SITE_EXPECTED = 88
SPECIES = {
    "pygoscelis adeliae": "Adelie",
    "pygoscelis antarcticus": "Chinstrap",
    "pygoscelis antarctica": "Chinstrap",
    "pygoscelis papua": "Gentoo",
}
EXACT_D15N = {"delta_15n", "delta 15n", "delta15n", "d15n", "δ15n", "δ 15n"}
LABELS = ("taxon_name", "taxon_name_original", "taxon_worms_scientific_name")
TISSUE_FIELDS = ("tissue", "tissue_type", "sample_tissue", "taxon_tissue", "sample_material")
NO_GO = "NO_GO_SCAR_INDEPENDENT_ISOTOPE_POLYNYA_TEST"


def string(x):
    return (x or "").strip()


def to_float(v):
    try:
        q = float(string(v))
        return q if math.isfinite(q) else None
    except (ValueError, TypeError):
        return None


def sample_date(v):
    """Exact ISO day is required; annual summaries cannot stand for sample date."""
    s = string(v)
    if not re.match(r"^\d{4}-\d{2}-\d{2}", s):
        return None
    try:
        return dt.date.fromisoformat(s[:10])
    except ValueError:
        return None


def season(d):
    if d.month in (11, 12):
        return d.year
    if d.month in (1, 2):
        return d.year - 1
    return None


def haversine(lat1, lon1, lat2, lon2):
    r = 6371.0088
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = p2 - p1
    dl = math.radians(((lon2 - lon1 + 180) % 360) - 180)
    a = math.sin(dp / 2)**2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2)**2
    return 2*r*math.asin(min(1, math.sqrt(max(0,a))))


def geo(row):
    w,e,s,n = (to_float(row.get(c)) for c in ("west","east","south","north"))
    if None in (w,e,s,n) or not(-90 <= s <= n <= 90) or not(-180 <= w <= 180 and -180 <= e <= 180):
        return None
    # Ambiguous dateline-spanning rectangles are NOT promoted to precise sites.
    if abs(e-w) > 180:
        return None
    midlon, midlat = (w+e)/2, (s+n)/2
    dx = haversine(midlat,w,midlat,e)
    dy = haversine(s,midlon,n,midlon)
    return midlat,midlon,math.hypot(dx,dy)


def get_headers_and_rows(z, name):
    info = next((i for i in z.infolist() if i.filename == name), None)
    if info is None:
        raise ValueError(f"Publisher member missing: {name}")
    with z.open(info) as f:
        reader = csv.DictReader(io.TextIOWrapper(f, encoding="utf-8-sig", newline=""))
        headers = reader.fieldnames or []
        return list(reader), headers


def load_sources(zip_path):
    raw = pathlib.Path(zip_path).read_bytes()
    sha = hashlib.sha256(raw).hexdigest()
    if len(raw) != ARCHIVE_BYTES or hashlib.md5(raw).hexdigest() != ARCHIVE_MD5:
        raise ValueError("STOP_SOURCE_MISMATCH original publisher ZIP byte count/MD5")
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        bad = z.testzip()
        if bad is not None:
            raise ValueError(f"STOP_SOURCE_CORRUPT first bad ZIP member {bad}")
        data, head = get_headers_and_rows(z, "scar_isotopes_mv.csv")
        sources, source_head = get_headers_and_rows(z, "scar_sources.csv")
        members = [i.filename for i in z.infolist()]
    refs = {string(x.get("source_id")): x for x in sources}
    return data, head, refs, source_head, sha, members


def read_reference(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        data = list(csv.DictReader(f))
    if len(data) != OLD_SITE_EXPECTED:
        raise ValueError(f"STOP_OLD88_SOURCE_GEOGRAPHY expected 88 sites, got {len(data)}")
    out = []
    for x in data:
        la,lo=to_float(x.get("colony_lat")),to_float(x.get("colony_lon"))
        if la is None or lo is None:
            raise ValueError("STOP_SOURCE_MISSING_CENTROID_COORDINATE")
        out.append(dict(id=string(x["site_id"]),region=string(x["source_region"]),lat=la,lon=lo))
    if len(set(x["id"] for x in out)) != OLD_SITE_EXPECTED:
        raise ValueError("STOP_SOURCE_DUPLICATE_OLD_SITE")
    return out


def check_date(row):
    start,end = sample_date(row.get("observation_date_start")),sample_date(row.get("observation_date_end"))
    if start is None or end is None or end < start or (end-start).days > 122:
        return None
    a,b=season(start),season(end)
    if a is None or a != b:
        return None
    return a


def name_and_species(row):
    for field in LABELS:
        label=string(row.get(field)).lower()
        if label in SPECIES:
            return SPECIES[label]
    return None


def audit(zip_path, reference_csv, out_dir):
    out = pathlib.Path(out_dir)
    out.mkdir(parents=True,exist_ok=True)
    data,columns,sources,source_headers,archive_sha,members = load_sources(zip_path)
    old88 = read_reference(reference_csv)
    needed={"source_id","measurement_name","measurement_mean_value","west","east",
            "south","north","observation_date_start","observation_date_end"}
    if not needed.issubset(set(columns)) or not any(x in columns for x in LABELS):
        raise ValueError("STOP_SOURCE_COLUMNS_MISSING "+str(sorted(needed-set(columns))))
    all_target=collections.Counter()
    d15n=collections.Counter()
    causes=collections.Counter()
    measured_names=collections.Counter()
    tissue_counts=collections.Counter()
    provenance=collections.Counter()
    source_links={}
    seen={}
    for r in data:
        species=name_and_species(r)
        if not species:
            continue
        all_target[species]+=1
        meas=string(r.get("measurement_name")).lower()
        measured_names[meas]+=1
        if meas not in EXACT_D15N:
            causes["not_bulk_delta15n_name"]+=1
            continue
        d15n[species]+=1
        if to_float(r.get("measurement_mean_value")) is None:
            causes["delta15n_missing_numeric_mean"]+=1
            continue
        if string(r.get("is_secondary_data")).lower() in ("y","yes","true","1"):
            causes["secondary_source"]+=1
            continue
        if string(r.get("quality_flag")).lower() in ("q","questionable","bad"):
            causes["questionable_quality"]+=1
            continue
        src=string(r.get("source_id"))
        if not src:
            causes["source_id_missing"]+=1
            continue
        location=string(r.get("location"))
        if not location:
            causes["source_locality_missing"]+=1
            continue
        samyear=check_date(r)
        if samyear is None:
            causes["not_exact_single_breeding_season"]+=1
            continue
        xy=geo(r)
        if xy is None:
            causes["missing_or_broad_bbox_geometry"]+=1
            continue
        lat,lon,diam=xy
        if diam > 25 or lat > -55:
            causes["bbox_over25km_or_nonantarctic"]+=1
            continue
        if (2004 <= samyear <= 2010) or (2013 <= samyear <= 2021):
            era="historical2004_2010" if samyear <= 2010 else "modern2013_2021"
        else:
            causes["not_preselected_windows"]+=1
            continue
        # tissue is retained as metadata; NEVER collapse into biological equivalence
        tissue="|".join(f"{f}={string(r.get(f))}" for f in TISSUE_FIELDS if f in columns)
        if not tissue: tissue="TISSUE_NOT_TYPED_IN_SOURCE_SCHEMA"
        tissue_counts[tissue]+=1
        info=sources.get(src,{})
        citation=string(info.get("details"))
        # Exclude previously-used response data as independent evidence.
        if re.search(r"Youngflesh|Michelson",citation,re.I):
            causes["original_or_prior_study_not_independent"]+=1
            continue
        dists=sorted((haversine(lat,lon,s["lat"],s["lon"]),s) for s in old88)
        nearest=dists[0][0]
        within2=sum(km <= 2 for km,_ in dists)
        within10=sum(km <= 10 for km,_ in dists)
        within25=sum(km <= 25 for km,_ in dists)
        # "source location/year" is an upper bound: same study locality
        # from multiple tissues or analytical repeats counts once.
        key=(src,species,location,samyear,era)
        if key not in seen:
            seen[key]={"source_id":src,"species":species,"location":location,
                       "source_season":samyear,"era":era,"source_region":dists[0][1]["region"],
                       "nearest_old_source_site_id":dists[0][1]["id"],
                       "nearest_old_source_site_km":round(nearest,4),
                       "second_old_source_site_km":round(dists[1][0],4),
                       "old_source_sites_within2km":within2,
                       "old_source_sites_within10km":within10,
                       "old_source_sites_within25km":within25,
                       "geometry_precision_km":round(diam,4),
                       "rows":0,
                       "sample_ids":set(),
                       "tissues":set(),
                       "study_citation":citation[:140]}
        row=seen[key]
        row["rows"]+=1
        sample=string(r.get("taxon_sample_id"))
        if sample:row["sample_ids"].add(sample)
        row["tissues"].add(tissue)
        provenance[src]=citation
    # Metadata only; never distribute source isotope responses.
    groups=list(seen.values())
    for q in groups:
        q["n_named_sample_ids"]=len(q.pop("sample_ids"))
        q["tissues"]="; ".join(sorted(q["tissues"]))[:500]
        q["strict_unique_old88_within25km"]=q["old_source_sites_within25km"]==1
    groups.sort(key=lambda x:(x["era"],x["source_region"],x["source_id"],x["location"],x["source_season"]))
    details={}
    for era in ("historical2004_2010","modern2013_2021"):
        allg=[g for g in groups if g["era"]==era]
        positive=[g for g in allg if g["strict_unique_old88_within25km"]]
        details[era]={
            "publisher_study_locality_species_season_upper_bound_all":len(allg),
            "publisher_study_locality_species_season_upper_bound_unique_old88_25km":len(positive),
            "distinct_publisher_source_studies_unique_25km":len(set(x["source_id"] for x in positive)),
            "distinct_source_localities_unique_25km":len(set((x["source_id"],x["location"]) for x in positive)),
            "distinct_nearest_old88_sites_unique_25km":len(set(x["nearest_old_source_site_id"] for x in positive)),
            "distinct_original_regions_unique_25km":len(set(x["source_region"] for x in positive)),
            "distinct_breeding_seasons_unique_25km":len(set(x["source_season"] for x in positive)),
            "proximity_group_count_le2km":sum(x["old_source_sites_within2km"]>=1 for x in allg),
            "proximity_group_count_le10km":sum(x["old_source_sites_within10km"]>=1 for x in allg),
            "proximity_group_count_le25km":sum(x["old_source_sites_within25km"]>=1 for x in allg),
            "count_ambiguous_multiple_old_sites_within25km":sum(x["old_source_sites_within25km"]>1 for x in allg),
        }
    derived_metadata_csv=out/"scar_original_pygoscelis_bulk_d15n_source_support_groups.csv"
    fields=["era","source_id","species","location","source_season","source_region",
            "nearest_old_source_site_id","nearest_old_source_site_km","second_old_source_site_km",
            "old_source_sites_within2km","old_source_sites_within10km","old_source_sites_within25km",
            "strict_unique_old88_within25km","geometry_precision_km","rows",
            "n_named_sample_ids","tissues","study_citation"]
    with open(derived_metadata_csv,"w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=fields,extrasaction="ignore")
        w.writeheader()
        w.writerows(groups)
    complete=details["historical2004_2010"]["publisher_study_locality_species_season_upper_bound_unique_old88_25km"]
    modern=details["modern2013_2021"]["publisher_study_locality_species_season_upper_bound_unique_old88_25km"]
    report={
        "verdict":NO_GO,
        "explanation":"A source locality within 25km is geographic proximity, not verified colony identity; formation/winter exposure timing is still unverified. No effect fit.",
        "provenance":"SCAR Southern Ocean Diet and Energetics Database DOI 10.5281/zenodo.20047874",
        "publisher_zip_md5":ARCHIVE_MD5,
        "publisher_zip_sha256":archive_sha,
        "publisher_zip_bytes":ARCHIVE_BYTES,
        "publisher_members":members,
        "publisher_isotopes_mv_rows_all_taxa":len(data),
        "publisher_scar_sources_rows":len(sources),
        "isotopes_schema":columns,
        "publisher_sources_schema":source_headers,
        "tissue_columns_present":[x for x in TISSUE_FIELDS if x in columns],
        "target_pygoscelis_all_isotope_measurement_rows":dict(all_target),
        "target_pygoscelis_named_bulk_d15n_rows":dict(d15n),
        "target_measurement_names_top25":dict(measured_names.most_common(25)),
        "target_tissues_top25":dict(tissue_counts.most_common(25)),
        "dropped_rows_reasons":dict(causes),
        "source_studies_retained_ids":sorted(provenance),
        "window_support":details,
        "fixed_requirement":">=20 study-location-species-season, >=5 distinct original study/location, >=3 regions, >=4 winters; verified source colony and feather formative period still required",
        "not_publisher_independent_units":"all rows are measurement entries; source groups are only an upper bound to independently sampled ecological observations",
        "not_a_test_of_winter_polynya":True,
        "climate_effect_fitted":False,
        "note":"No causal or dietary mechanism inference from bulk delta15N; Michelson and Youngflesh source not counted independent.",
    }
    (out/"scar_original_pygoscelis_bulk_d15n_source_support_verdict.json").write_text(
        json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8"
    )
    print(json.dumps({
        "status":NO_GO,
        "total_isotope_rows":len(data),
        "all_pygoscelis_isotope_rows":sum(all_target.values()),
        "exact_bulk_d15n_rows":sum(d15n.values()),
        "historical_unique_proximity_groups":complete,
        "modern_unique_proximity_groups":modern,
        "result_file":str(derived_metadata_csv),
        "biology_effect_estimated":False,
        "source_field_names":columns,
        "measurement_names":dict(measured_names.most_common(10)),
        "exclusion_counts":dict(causes),
        "window_support":details,
        "tissue_fields":[x for x in TISSUE_FIELDS if x in columns]
        },indent=2))
    return report


if __name__ == "__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--source-zip",required=True)
    ap.add_argument("--old88-sites",required=True)
    ap.add_argument("--out",required=True)
    args=ap.parse_args()
    audit(args.source_zip,args.old88_sites,args.out)
