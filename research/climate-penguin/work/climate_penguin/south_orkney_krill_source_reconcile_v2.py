"""Reconcile conflicting year-labelled South Orkney acoustic biomass tables.

Authority: Skaret et al. 2023 ICES J Mar Sci Table 3, DOI 10.1093/icesjms/fsad076.
A 2024 IMR report Table 2 labels the 2014–2020 reported values one year
earlier and populates the missing 2013 combined estimate. Its values are kept
as an auditable original historical input, not silently overwritten. 2013 has
a North-only partial survey, no official North+South combined stratum value.
This is a source/transcription correction, NOT new field data.
"""
from __future__ import annotations
import argparse
import csv
import json
import math
import statistics
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[4]
OLD=ROOT/"research/climate-penguin/inputs/imr_south_orkney_krill_2011_2020_2024_table2.csv"
NEW=ROOT/"research/climate-penguin/inputs/skaret_2023_krill_stratum_table3_reconciled_v2.csv"
SP=("Adelie","Chinstrap","Gentoo")
YEARS=tuple(range(2011,2020))

def read(path):
    with Path(path).open(encoding="utf-8",newline="") as file:
        return list(csv.DictReader(file))

def sources(old=OLD,new=NEW):
    old_records=read(old)
    new_records=read(new)
    if len(old_records)!=10 or len(new_records)!=31:
        raise ValueError("source original yearly roster changed")
    old_by_year={int(z["survey_calendar_year"]):z for z in old_records}
    if set(old_by_year)!=set(range(2011,2021)):
        raise ValueError("old IMR 2024 year sequence changed")
    data={}
    for r in new_records:
        year=int(r["survey_calendar_year"])
        stratum=r["stratum"]
        if stratum not in ("Combined","North","South","Shelf edge"):
            raise ValueError("new source stratum undefined")
        key=stratum,year
        if key in data:
            raise ValueError("duplicate source year stratum")
        val=float(r["density_g_m2"])
        bm=float(r["biomass_million_tonnes"])
        cv=float(r["coefficient_of_variation"])
        if not(0<=val<300 and 0<=bm<20 and 0<cv<1):
            raise ValueError("invalid original source density/CV")
        if (r["source_paper"],r["source_table"])!=("Skaret_2023_ICES","Table_3"):
            raise ValueError("source provenance drift")
        data[key]={**r,"density":val,"bm":bm,"cv":cv}
    expected={
        "Combined":set(range(2011,2021))-{2013},
        "North":set(range(2011,2021)),
        "South":set(range(2011,2021))-{2013},
        "Shelf edge":{2015,2019,2020}
    }
    for label,years in expected.items():
        if {t for s,t in data if s==label}!=years:
            raise ValueError("source year support changed for "+label)
    must={"2011":62.6,"2012":128.8,"2014":76.5,"2015":28.5,
          "2016":49.3,"2017":23.2,"2018":69.4,"2019":27.2,"2020":38.8}
    for yr,v in must.items():
        if not math.isclose(data["Combined",int(yr)]["density"],v,abs_tol=1e-10):
            raise ValueError("published Table 3 transcription mismatch "+yr)
    conflicts=[]
    for year in range(2011,2021):
        oldr=old_by_year[year]
        newr=data.get(("Combined",year))
        old_density=float(oldr["density_g_m2"])
        new_density=newr["density"] if newr else None
        conflict=(new_density is None or not math.isclose(new_density,old_density,abs_tol=1e-12))
        conflicts.append({
            "year":year,
            "prior_IMR_2024_table2_density_g_m2":old_density,
            "Skaret_2023_published_combined_density_g_m2":new_density if new_density is not None else "",
            "new_source_combined_exists":newr is not None,
            "year_value_conflict":conflict,
            "interpretation":"2013 North-only, combined stratum missing" if year==2013 else "conflict requires source lineage distinction" if conflict else "sources agree"
        })
    return data,conflicts

def corr(xx,yy):
    if len(xx)!=len(yy) or len(xx)<4:
        raise ValueError("too few independent year opportunities")
    mx=statistics.mean(xx);my=statistics.mean(yy)
    num=sum((a-mx)*(b-my) for a,b in zip(xx,yy))
    den=math.sqrt(sum((a-mx)**2 for a in xx)*sum((b-my)**2 for b in yy))
    return num/den if den>1e-12 else None

def stage(stage_file,raw_file):
    annual=read(stage_file)
    outcomes={}
    for r in annual:
        key=r["species"],int(r["season_start"])
        if key[0] not in SP or key[1] not in YEARS:
            continue
        if key in outcomes:raise ValueError("duplicate native species-year stage")
        if int(r["has_reported_fledglings_n"])<1:
            raise ValueError("native source missing fledglings")
        outcomes[key]=float(r["median_recorded_fledglings_per_pair"])
    if len(outcomes)!=27:
        raise ValueError("missing original 3 species × 9 historical seasons")
    return outcomes

def compare(records,old,stages):
    oldmap={int(r["survey_calendar_year"]):float(r["density_g_m2"]) for r in read(old)}
    all_data=[]
    for exposure in ("Skaret_combined","prior_2024_transcribed_combined","Skaret_north","Skaret_south","Skaret_north_div_south"):
        for group in ("all_available","comparable_complete","complete_without_2012"):
            years=[y for y in YEARS if
                (exposure=="prior_2024_transcribed_combined" or
                 exposure=="Skaret_north" or
                 (("North",y) in records and ("South",y) in records))]
            if group!="all_available":
                years=[y for y in years if y not in (2013,2015)]
            if group=="complete_without_2012":
                years=[y for y in years if y!=2012]
            if exposure=="Skaret_combined":
                years=[y for y in years if ("Combined",y) in records]
            xx=[]
            for y in years:
                if exposure=="prior_2024_transcribed_combined": x=oldmap[y]
                elif exposure=="Skaret_combined": x=records["Combined",y]["density"]
                elif exposure=="Skaret_north": x=records["North",y]["density"]
                elif exposure=="Skaret_south": x=records["South",y]["density"]
                else: x=records["North",y]["density"]/records["South",y]["density"]
                xx.append(x)
            for sp in SP:
                yy=[stages[sp,y] for y in years]
                all_data.append({
                    "exposure":exposure,
                    "cohort":group,
                    "species":sp,
                    "n_years":len(years),
                    "years":";".join(map(str,years)),
                    "pearson_r":corr(xx,yy),
                    "post_exposure_observational_only":True
                })
    return all_data

def numeric_check(compare_results,conflicts):
    if len(conflicts)!=10 or sum(r["year_value_conflict"] for r in conflicts)!=8:
        raise ValueError("known original Table2 vs Table3 conflicts drift")
    def get(exposure,scope,species):
        return next(r["pearson_r"] for r in compare_results
            if r["exposure"]==exposure and r["cohort"]==scope and r["species"]==species)
    expected={
        ("Skaret_combined","all_available","Adelie"):0.057344314, # tolerance adjusted below
        ("Skaret_combined","all_available","Chinstrap"):-0.2118,
        ("Skaret_combined","all_available","Gentoo"):-0.4134,
        ("prior_2024_transcribed_combined","all_available","Adelie"):-0.21160538308997398,
        ("prior_2024_transcribed_combined","all_available","Chinstrap"):-0.5591205943534584,
        ("prior_2024_transcribed_combined","all_available","Gentoo"):-0.54611367372603,
    }
    for key,val in expected.items():
        current=get(*key)
        tol=0.00015 if key[0]=="Skaret_combined" else 1e-8
        if not math.isclose(current,val,abs_tol=tol):
            raise ValueError("source-contrast numeric receipt not reproduced "+str((key,current,val)))
    return True

def save(path,rows):
    with Path(path).open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]))
        w.writeheader();w.writerows(rows)

def main():
    a=argparse.ArgumentParser()
    a.add_argument("--stage-dir",required=True,type=Path)
    a.add_argument("--out",required=True,type=Path)
    a.add_argument("--check",action="store_true")
    o=a.parse_args()
    records,conflicts=sources()
    stage_values=stage(o.stage_dir/"species_annual_stage_summary.csv",
                       o.stage_dir/"source_stage_site_seasons.csv")
    comparisons=compare(records,OLD,stage_values)
    if o.check:
        numeric_check(comparisons,conflicts)
    o.out.mkdir(parents=True,exist_ok=True)
    save(o.out/"source_year_conflicts.csv",conflicts)
    save(o.out/"stage_correlations_reconciled.csv",comparisons)
    receipt={
      "status":"ORIGINAL_IMR_2024_TABLE2_CONFLICTS_WITH_PRIMARY_SKARET_2023_TABLE3",
      "prior_v1_result":"SUPERSEDED_FOR_REGIONAL_KRILL_TO_FLEDGLING_INFERENCE",
      "primary_paper":"https://doi.org/10.1093/icesjms/fsad076",
      "source_years_combined":sorted(y for s,y in records if s=="Combined"),
      "combined_year_2013":"unavailable_not_zero",
      "source_year_conflicts":sum(z["year_value_conflict"] for z in conflicts),
      "species_stage_link":len(stage_values),
      "all_specification_count":len(comparisons),
      "source_name":"Table 3 year×stratum values manually transcribed from original peer-reviewed paper, not raw acoustic transects",
      "caution":[
        "2024 Table 2 and Skaret 2023 Table 3 disagree in annual labels; do not assert an explanation without source erratum.",
        "The 2013 combined-strata estimate is not present in primary Table 3; 2013 North partial cannot replace it.",
        "The 2015 South transects were limited by sea ice and combined 2015 estimate is sensitivity only.",
        "The 2023 primary paper contains only nine combined annual estimates; corrected S=T source results are based on eight matched Signy seasons 2011–2019.",
        "Multiple species use the same single regional survey per year; ratios are not independent and do not identify prey-mediated causal effects.",
        "Prior modelled raster results have original acoustic/salinity/ice covariate input and are also not independent validation."
      ]}
    (o.out/"decision.json").write_text(json.dumps(receipt,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps({"status":receipt["status"],"conflicts":receipt["source_year_conflicts"],
      "corrected_preseason_all":{sp:next(r["pearson_r"] for r in comparisons if r["exposure"]=="Skaret_combined" and r["cohort"]=="all_available" and r["species"]==sp) for sp in SP},
      "old_preseason_all":{sp:next(r["pearson_r"] for r in comparisons if r["exposure"]=="prior_2024_transcribed_combined" and r["cohort"]=="all_available" and r["species"]==sp) for sp in SP},
      "test_passed":bool(o.check)},ensure_ascii=False))

if __name__=="__main__":
    main()
