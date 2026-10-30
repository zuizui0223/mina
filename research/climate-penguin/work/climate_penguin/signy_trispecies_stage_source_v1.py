"""Source-verified three-species Signy annual nesting and chick-stage intake.

Official BAS/RAMADDA public ZIP trees only, with previous Adélie/chinstrap
source pins. This is a new observational source audit, not a forecast or
climate mechanism. Raw original records stay in workflow scratch.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))
from scripts.audit_signy_replication_support import read_official_zip, season_start

SOURCE = {
    "Adelie": {
        "doi": "10.5285/daf2c4fd-c1e3-4e65-851f-d11f02c5b69d",
        "entry_id": "daf2c4fd-c1e3-4e65-851f-d11f02c5b69d",
        "prior_csv_sha256": "585f87928ed64d8982ef5bd86d8a785c38df65c39223d88ec17425854c786d62"
    },
    "Chinstrap": {
        "doi": "10.5285/d0633a9b-8c56-4ae5-88bf-6ec6ba9017b9",
        "entry_id": "d0633a9b-8c56-4ae5-88bf-6ec6ba9017b9",
        "prior_csv_sha256": "e50e98719ba5eedc6f5e617e0c7aa404ebfba15bc22a51e93e78cd4443bf787b"
    },
    "Gentoo": {
        "doi": "10.5285/883c6b40-024e-41e8-9c3e-2668a44b5751",
        "entry_id": "883c6b40-024e-41e8-9c3e-2668a44b5751",
        "prior_csv_sha256": None
    }
}
UNKNOWN = {"", "na", "nan", "none", "unknown", "n/a"}
ROOT = Path(__file__).resolve().parents[4]
DEFAULT_OUT = ROOT/"research/climate-penguin/outputs/signy_trispecies_stage_source_v1"


def number(value):
    if value is None or str(value).strip().lower() in UNKNOWN:
        return None
    try:
        v = float(str(value).replace(",", "").strip())
    except (ValueError,TypeError):
        return None
    return v if math.isfinite(v) and v>=0 else None


def column(df, names, required=True):
    available = {re.sub(r"[^a-z0-9]+","",str(k).lower()): str(k) for k in df.columns}
    for name in names:
        v = available.get(re.sub(r"[^a-z0-9]+","",name.lower()))
        if v:
            return v
    if required:
        raise ValueError(f"Missing source column {names}; available={list(df.columns)}")
    return None


def source_extract(species, zip_path):
    frame, source_meta = read_official_zip(zip_path)
    sha = source_meta["selected_csv_sha256"]
    previous = SOURCE[species]["prior_csv_sha256"]
    if previous and sha!=previous:
        raise ValueError(f"Source CSV SHA drift for {species}: {sha}")
    fields = {
        "season":column(frame,["SEASON", "BREEDING_SEASON"]),
        "colony":column(frame,["COLONY", "COLONY_ID"],species!="Gentoo"),
        "pairs":column(frame,["TOTAL_NUMBER_OF_PAIRS", "BREEDING_PAIRS"]),
        "chicks":column(frame,["TOTAL_NUMBER_OF_CHICKS", "CHICKS_EXPECTED_TO_FLEDGE"]),
        "fledglings":column(frame,["TOTAL_NUMBER_OF_FLEDGLINGS", "FLEDGLINGS"],False),
        "nest_date":column(frame,["DATE_PAIR_COUNT", "DATE_NEST_COUNT"],False),
        "chick_date":column(frame,["DATE_CHICK_COUNT","DATE_FLEDGE_COUNT"],False),
        "fledgling_date":column(frame,["DATE_FLEDGLING_COUNT","DATE_FLEDGLING"],False),
        "comments":column(frame,["COMMENTS","COMMENT"],False),
    }
    import pandas as pd
    extracted = []
    audit = Counter()
    seen = set()
    for idx, obj in frame.iterrows():
        year = season_start(str(obj[fields["season"]]))
        if year is None:
            audit["unparsed_season"] += 1
            continue
        if not 1996<=year<=2019:
            continue
        colony = (str(obj[fields["colony"]]).strip()
                  if fields["colony"] else "SIGNY_SOURCE_AGGREGATE")
        if colony.lower() in UNKNOWN:
            audit["unknown_colony"] += 1
            continue
        key = (year, colony)
        if key in seen:
            raise ValueError(f"duplicate literal colony-season for {species}: {key}")
        seen.add(key)
        pairs, chicks = number(obj[fields["pairs"]]), number(obj[fields["chicks"]])
        fledglings = number(obj[fields["fledglings"]]) if fields["fledglings"] else None
        comments = str(obj[fields["comments"]]).strip() if fields["comments"] and pd.notna(obj[fields["comments"]]) else ""
        def iso(key):
            if not fields[key] or pd.isna(obj[fields[key]]):
                return ""
            raw_date = str(obj[fields[key]]).strip()
            dt = pd.to_datetime(raw_date,dayfirst=not bool(re.match(r"^\d{4}-\d\d-\d\d$",raw_date)),errors="coerce")
            return dt.date().isoformat() if pd.notna(dt) else ""
        nd, cd, fd = iso("nest_date"), iso("chick_date"), iso("fledgling_date")
        ordered = bool(nd and cd and nd<cd)
        valid = pairs is not None and pairs>0 and chicks is not None
        if pairs==0:
            audit["zero_breeding_pairs_no_division"] += 1
        if pairs is None:
            audit["missing_pairs"] += 1
        if chicks is None:
            audit["missing_chicks"] += 1
        if fields["fledglings"] and fledglings is None:
            audit["missing_fledglings"] += 1
        if pairs and fledglings is not None:
            audit["valid_pair_fledgling_rows"] += 1
            if nd and fd and nd<fd:
                audit["ordered_pair_fledgling_rows"] += 1
        if valid:
            audit["valid_pair_chick_rows"] += 1
            if ordered:
                audit["strict_nest_before_chicks"] += 1
            if chicks/pairs>2:
                audit["ratio_above_2"] += 1
        extracted.append({
            "species":species,"season_start":year,"colony":colony,
            "pairs":pairs,"chicks":chicks,"fledglings":fledglings,
            "recorded_fledglings_per_pair":fledglings/pairs if pairs and fledglings is not None else None,
            "source_spatial_unit":"island_aggregate_no_colony_field" if not fields["colony"] else "source_colony",
            "reported_chicks_per_pair":chicks/pairs if valid else None,
            "source_row_index":int(idx),
            "nest_count_date":nd,"chick_count_date":cd,"fledgling_count_date":fd,
            "nest_before_chicks":ordered,
            "nest_before_fledglings":bool(nd and fd and nd<fd),
            "comments":comments,
            "source_csv_sha256":sha
        })
    audit["source_csv_rows"] = len(frame)
    audit["in_window_rows"] = len(extracted)
    audit["in_window_seasons"] = len({r["season_start"] for r in extracted})
    audit["in_window_literal_colonies"] = len({r["colony"] for r in extracted})
    audit["valid_seasons"] = len({r["season_start"] for r in extracted if r["reported_chicks_per_pair"] is not None})
    audit["strict_seasons"] = len({r["season_start"] for r in extracted if r["reported_chicks_per_pair"] is not None and r["nest_before_chicks"]})
    return extracted, dict(audit), {
        "source_url":f"https://doi.org/{SOURCE[species]['doi']}",
        "csv_name":source_meta["selected_csv"],
        "selected_csv_sha256":sha,
        "zip_sha256":hashlib.sha256(Path(zip_path).read_bytes()).hexdigest(),
        "schema_fields":fields
    }


def summarize(rows):
    valid = [r for r in rows if r["reported_chicks_per_pair"] is not None]
    by_species_year = defaultdict(list)
    for r in valid:
        by_species_year[(r["species"],r["season_start"])].append(r)
    annual = []
    for (species,year), group in sorted(by_species_year.items()):
        ordered = [r for r in group if r["nest_before_chicks"]]
        ann = dict(
            species=species,season_start=year,
            observed_colonies=len(group),
            strict_date_colonies=len(ordered),
            median_recorded_chicks_per_pair=statistics.median(
                r["reported_chicks_per_pair"] for r in group
            ),
            ratio_of_recorded_chick_to_pair_sums=(
                sum(r["chicks"] for r in group)/sum(r["pairs"] for r in group)
            ),
            strict_median_recorded_chicks_per_pair=(
                statistics.median(r["reported_chicks_per_pair"] for r in ordered) if ordered else None
            ),
            distinct_literal_colonies=len({r["colony"] for r in group}),
            source_country="Signy, South Orkney Islands",
            is_total_island_population=False,
            original_spatial_unit=group[0]["source_spatial_unit"],
            has_reported_fledglings_n=sum(r["recorded_fledglings_per_pair"] is not None for r in group),
            median_recorded_fledglings_per_pair=(
                statistics.median(r["recorded_fledglings_per_pair"] for r in group if r["recorded_fledglings_per_pair"] is not None)
                if any(r["recorded_fledglings_per_pair"] is not None for r in group) else None
            ),
            no_spatial_independence_claim=True,
            stage_to_individual_survival_verified=False
        )
        if ann["distinct_literal_colonies"]!=len(group):
            raise ValueError("duplicate within species-year source")
        annual.append(ann)
    species = sorted({r["species"] for r in rows})
    complete_years=sorted(set.intersection(*[
        {r["season_start"] for r in annual if r["species"]==species} for species in species
    ])) if len(species)==3 else []
    return annual,complete_years


def run(source_dir,output_dir):
    collected,source_audit,sources=[],{},{}
    for species in SOURCE:
        path=Path(source_dir)/(species.lower()+".zip")
        if not path.exists():
            raise ValueError("missing publisher-original zip: "+str(path))
        rows,audit,metadata=source_extract(species,path)
        collected.extend(rows)
        source_audit[species]=audit
        sources[species]=metadata
    annual,complete_years=summarize(collected)
    output_dir=Path(output_dir)
    output_dir.mkdir(parents=True,exist_ok=True)
    def save_csv(path,rows):
        if not rows:
            return
        with (output_dir/path).open("w",newline="",encoding="utf-8") as file:
            writer=csv.DictWriter(file,fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
    save_csv("source_stage_site_seasons.csv",collected)
    save_csv("species_annual_stage_summary.csv",annual)
    gate=dict(
        status="SOURCE_OBSERVATIONAL_STAGE_ONLY_NO_CAUSAL_MODEL",
        scientific_question="Can original same-island three-species pair/chick stages be harmonized before environmental transfer?",
        raw_source=sources,
        source_audit=source_audit,
        annual_rows=len(annual),
        common_species_seasons=complete_years,
        common_species_season_count=len(complete_years),
        raw_stage_rows=len(collected),
        valid_stage_rows=sum(r["reported_chicks_per_pair"] is not None for r in collected),
        limitations=[
            "Source units differ by species: Gentoo is island aggregate without a colony field, whereas Adelie/Chinstrap have source colony labels.",
            "Adelie/Chinstrap source-colony ratios are not a whole-island success rate.",
            "CEMP chick stages are not individual survival or recruitment, and reported counts may have different scope and survey timing.",
            "Colony labels with composite units can change meaning; do not treat as immutable polygons or sum overlapping labels.",
            "All species share one island and annual marine environment; source colony count is not an independent climate replicate.",
            "No annual salinity, krill, sea ice, or vegetation effect is estimated in this source-only audit.",
            "The separate MAPPPD v9 counts are not independent biological replication of BAS studies.",
        ]
    )
    (output_dir/"source_gate.json").write_text(json.dumps(gate,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps({k:gate[k] for k in ("source_audit","common_species_season_count","annual_rows","raw_stage_rows","valid_stage_rows")},ensure_ascii=False))
    return gate


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--source-dir",required=True,type=Path)
    parser.add_argument("--out",type=Path,default=DEFAULT_OUT)
    opts=parser.parse_args()
    run(opts.source_dir,opts.out)

if __name__=="__main__":
    main()
