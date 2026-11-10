"""Original ASPA-113 Litchfield breeding-count source reconciliation.

This is a SOURCE IDENTITY, CALENDAR and physical-island hypothesis gate;
no causal warming effect or vegetation change is estimated.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import math
import statistics
from collections import Counter, defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
INPUT=ROOT/"inputs/ASPA113_LITCHFIELD_ADELIE_COUNTS_1991_2012.csv"
COMP=ROOT/"outputs/comparison_audit"
CLIMATE=ROOT/"outputs/climate_penguin"

def read_csv(p):
    with Path(p).open(newline="",encoding="utf-8") as f:
        return list(csv.DictReader(f))

def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def values_by_year(rows):
    seen={}
    for r in rows:
        key=int(r["season_start"])
        assert key not in seen, ("duplicate original season",key)
        assert r["site_id"]=="LITC" and r["species_id"]=="ADPE"
        assert int(r["season_end"])==key+1
        assert r["census_date_status"]=="not_specified_per_year"
        assert not r["census_month"], "Never infer field census month"
        assert r["table_source_note"] in {"3","4","5"}
        seen[key]=int(r["breeding_pairs"])
    assert list(sorted(seen))==list(range(1991,2013))
    assert len(seen)==22
    assert seen[2005]==15 and seen[2006]==4 and seen[2007]==0
    assert all(seen[y]==0 for y in range(2007,2013))
    assert all(seen[y]>0 for y in range(1991,2007))
    return seen

def source_date_priority(path):
    records=read_csv(path)
    non_vic=[r for r in records if r["region"]!="Victoria Land"]
    assert len(non_vic)==181
    unknown=[r for r in non_vic if r["all_months_known"]=="False"]
    assert len(unknown)==120
    by_citation=defaultdict(lambda:{"rows":0,"undated":0,"sites":set(),"regions":set()})
    for r in non_vic:
        for cite in r["citations"].split(";"):
            if not cite:
                continue
            v=by_citation[cite]
            v["rows"]+=1
            v["undated"]+=int(r["all_months_known"]=="False")
            v["sites"].add(r["site_id"])
            v["regions"].add(r["region"])
    ledger=[{"citekey":key,"source_rows":v["rows"],"unknown_month_rows":v["undated"],
             "sites":";".join(sorted(v["sites"])),"regions":";".join(sorted(v["regions"])),
             "source_date_verified":False}
            for key,v in by_citation.items()]
    ledger.sort(key=lambda r:(-r["unknown_month_rows"],-r["source_rows"],r["citekey"]))
    assert len({r["citekey"] for r in ledger})==len(ledger)
    return ledger,{"outside_victoria_rows":len(non_vic),"unresolved_month_rows":len(unknown),
                   "known_month_rows":len(non_vic)-len(unknown)}

def audit(era5=None):
    official=values_by_year(read_csv(INPUT))
    mp=read_csv(COMP/"mapppd_unambiguous_site_seasons.csv")
    old={int(r["season"]):int(float(r["count"])) for r in mp if r["site_id"]=="LITC" and r["species_id"]=="ADPE"
         and r["count"] and 1991<=int(r["season"])<=2012 and int(r["n_counts"])==1}
    concordant=sorted(set(old)&set(official))
    conflicts=[y for y in concordant if old[y]!=official[y]]
    assert len(concordant)==17 and not conflicts
    newly_retained=sorted(set(official)-set(old))
    assert newly_retained==[2006,2009,2010,2011,2012]
    spell=[r for r in read_csv(COMP/"mapppd_zero_episodes.csv") if r["site_id"]=="LITC" and r["species_id"]=="ADPE"]
    assert len(spell)==1 and int(spell[0]["last_positive"])==2005
    assert int(spell[0]["first_observed_zero"])==2007
    plants=[r for r in read_csv(COMP/"vegetation_mapppd_spatial_support.csv") if r["site_id"]=="LITC"]
    assert len(plants)==3
    map500=[r for r in plants if int(r["radius_m"])==500]
    assert len(map500)==1
    assert (int(map500[0]["Vegetation_features"]),int(map500[0]["Lichen_features"]))==(27,59)
    loc=[r for r in read_csv(CLIMATE/"daily_ice_locations.csv") if r["site_id"]=="LITC" and r["cohort"]=="macro_40"]
    assert len(loc)==1 and loc[0]["location_id"]=="loc024"
    priority,support=source_date_priority(CLIMATE/"historical_count_season_timing.csv")
    receipt={"schema":1,"status":"verified_primary_source_count_chronology_not_caused_greening",
        "pdf_url":"https://www.env.go.jp/nature/nankyoku/kankyohogo/database/jyouyaku/aspa/aspa_pdf_en/113.pdf",
        "source_type":"2014 first-party Antarctic Treaty ASPA113 management plan Table 1; pp 5-6",
        "original_count_csv_sha256":sha(INPUT),
        "mapppd_original_snapshot_sha256":sha(COMP/"mapppd_unambiguous_site_seasons.csv"),
        "seasons":22,"positive_seasons":16,"explicit_zero_seasons":6,
        "first_zero_season_start":2007,"last_positive_season_start":2006,
        "published_2006_breeding_pairs":4,
        "mapppd_exact_matches":len(concordant),"mapppd_count_disagreements":len(conflicts),
        "published_only_seasons":newly_retained,"last_positive_mapppd":int(spell[0]["last_positive"]),
        "mapppd_first_zero":int(spell[0]["first_observed_zero"]),
        "survey_month_resolved":False,
        "static_point_buffer_only":{"radius_m":500,"vegetation_map_features":27,"lichen_map_features":59,
          "time_indexed_vegetation":False,"physical_land_polygon_resolved":False},
        "source_priority":support,
        "climate":{"status":"not_queried","reason":"Full ERA5 source artifact optional"},
        "not_inferred":["penguin-induced greening","individual migration","annually surveyed all-patch occupancy",
                        "true climate-attributable population effect","physical rock-capacity increase",
                        "seasonal sea-ice loss before observed counts"]}
    if era5:
        orig=Path(era5)/"era5_monthly_1991_2020.csv"
        m=read_csv(orig)
        assert len(m)==40*30*12
        selected=[r for r in m if r["site_id"]=="LITC"]
        assert len(selected)==360
        grid={(r["returned_grid_latitude"],r["returned_grid_longitude"]) for r in selected}
        assert len(grid)==1
        by_key={(int(r["year"]),int(r["month"])):float(r["air2m_mean_c"])
                for r in selected if r["complete_month"]=="True" and r["air2m_mean_c"]}
        assert len(by_key)==360
        years=[]
        for y in range(1991,2013):
            def t(mm):return statistics.mean(by_key[y,m] for m in mm)
            years.append({"season_start":y,"breeding_pairs_original":official[y],
                "present_count_status":"observed_zero" if official[y]==0 else "observed_positive",
                "ERA5_september_c":t([9]),"ERA5_aug_nov_c":t([8,9,10,11]),
                "ERA5_calendar_annual_c":t(list(range(1,13))),
                "survey_month_certified":False})
        assert len(years)==22
        receipt["climate"]={"status":"ERA5_original_source_retrieved_context_only",
            "source_sha256":sha(orig),"grid_location":list(grid)[0],
            "n_complete_years":len(years),
            "pre_first_zero_september_mean_c":statistics.mean(r["ERA5_september_c"] for r in years if r["season_start"]<=2006),
            "observed_zero_period_september_mean_c":statistics.mean(r["ERA5_september_c"] for r in years if r["season_start"]>=2007),
            "source_calendar_overlap_only":True,
            "causal_or_precensus_exposure":False}
        return receipt,priority,years
    return receipt,priority,None

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--era5-dir",type=Path)
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    args.output.mkdir(parents=True,exist_ok=True)
    r,priority,climate=audit(args.era5_dir)
    (args.output/"LITCHFIELD_ASPA113_SOURCE_RECEIPT.json").write_text(json.dumps(r,indent=2,ensure_ascii=False))
    for name,rows in [("non_victoria_missing_month_citations.csv",priority),
                      ("litchfield_original_count_era5_context.csv",climate)]:
        if not rows:continue
        with (args.output/name).open("w",newline="",encoding="utf-8") as fh:
            w=csv.DictWriter(fh,fieldnames=list(rows[0]))
            w.writeheader();w.writerows(rows)
    print("LITCHFIELD_ASPA113_RECEIPT="+json.dumps(r,ensure_ascii=False),flush=True)

if __name__=="__main__":
    main()
