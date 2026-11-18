"""IMR source-reported regional acoustic krill biomass ↔ BAS Signy reproductive stage.

Data lineage: annual acoustic estimates *transcribed from published Table 2* in
the Norwegian Institute of Marine Research 2024 expedition report. Not new raw
acoustic observations. Preseason year t acoustic survey (Jan-Feb t) is prior to
the 2011-2019 BAS breeding season t (fledgling stage Jan-Feb t+1).
Concurrent Jan-Feb t+1 is a secondary, not necessarily preceding, comparison.
This is exploratory post-exposure evidence; does not estimate krill availability
to Signy breeders or a climate-to-count causal transfer.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import math
import statistics
from collections import Counter
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
SOURCE = ROOT / "research/climate-penguin/inputs/imr_south_orkney_krill_2011_2020_2024_table2.csv"
SPECIES = ("Adelie", "Chinstrap", "Gentoo")
YEARS = tuple(range(2011, 2020))
PUBLISHER = "https://www.hi.no/hi/nettrapporter/toktrapport-en-2024-14"
PAPER = "https://doi.org/10.1093/icesjms/fsad076"

def rows(path):
    with Path(path).open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def acoustic(path=SOURCE):
    data=rows(path)
    if len(data)!=10 or {int(r["survey_calendar_year"]) for r in data}!=set(range(2011,2021)):
        raise ValueError("original published yearly survey coverage changed")
    out={}
    for r in data:
        year=int(r["survey_calendar_year"])
        if year in out:
            raise ValueError("duplicate acoustic year")
        if r["source_report"]!="IMR_2024" or r["source_table"]!="Table_2_overall_stratum":
            raise ValueError("different source or survey stratum")
        density=float(r["density_g_m2"])
        biomass=float(r["biomass_million_tonnes"])
        cv=float(r["coefficient_of_variation"])
        freq=int(r["acoustic_khz"])
        if not(0<density<500 and 0<biomass<30 and 0<cv<1 and freq in (38,120)):
            raise ValueError("out of source physical domain")
        if abs(biomass - 0.06*density)>0.08:
            raise ValueError("expected 60000km2 area and published biomass disagree")
        covered=r["survey_coverage"]=="full"
        if r["survey_coverage"] not in ("full","reduced"):
            raise ValueError("unknown survey coverage")
        if covered == (year in (2013,2015)):
            raise ValueError("incomplete coverage mask changed")
        out[year] = {
            "year":year, "density":density,
            "biomass":biomass,"cv":cv,"frequency":freq,
            "full_coverage":covered
        }
    return out

def stagelink(stage_csv, source_stage_csv):
    annual=rows(stage_csv)
    values={}
    for r in annual:
        sp=r["species"]
        if sp not in SPECIES:
            raise ValueError("unexpected reproductive species")
        year=int(r["season_start"])
        if year not in YEARS:
            continue
        val=float(r["median_recorded_fledglings_per_pair"])
        if not math.isfinite(val) or val<0:
            raise ValueError("invalid fledgling stage summary")
        if int(r["has_reported_fledglings_n"])<1:
            raise ValueError("no native fledgling-stage source")
        key=sp,year
        if key in values:
            raise ValueError("duplicate stage summary")
        values[key]=val
    if len(values)!=len(YEARS)*len(SPECIES):
        raise ValueError("missing 3-species 2011-2019 records")
    stage=rows(source_stage_csv)
    sample_counts=Counter()
    for r in stage:
        key=(r["species"],int(r["season_start"]))
        if key not in values or not r.get("recorded_fledglings_per_pair"):
            continue
        d=date.fromisoformat(r["fledgling_count_date"])
        if not (d.year==key[1]+1 and d.month in (1,2,3)):
            raise ValueError("stage year/date correspondence drifted")
        if r["nest_before_fledglings"]!="True":
            raise ValueError("source fledgling stage lacks verified nest-first chronology")
        sample_counts[key]+=1
    if set(sample_counts)!=set(values):
        raise ValueError("stage source lineage incomplete")
    return values,sample_counts

def correlation(x,y):
    if len(x)!=len(y) or len(x)<3:
        raise ValueError("not enough paired years")
    xm=sum(x)/len(x);ym=sum(y)/len(y)
    a=[q-xm for q in x];b=[q-ym for q in y]
    denom=math.sqrt(sum(z*z for z in a)*sum(z*z for z in b))
    return sum(z*w for z,w in zip(a,b))/denom if denom>1e-14 else None

def ranks(seq):
    order=sorted(range(len(seq)),key=lambda i:seq[i])
    out=[0.0]*len(seq)
    k=0
    while k<len(seq):
        j=k+1
        while j<len(seq) and seq[order[j]]==seq[order[k]]:
            j+=1
        for i in range(k,j):
            out[order[i]]=(k+j+1)/2
        k=j
    return out

def analysis(krill,stage,source_counts,offset,subset_label):
    years=[y for y in YEARS if y+offset in krill]
    if subset_label in ("coverage_full","coverage_full_without_2012"):
        years=[y for y in years if krill[y+offset]["full_coverage"]]
    if subset_label=="coverage_full_without_2012":
        years=[y for y in years if y!=2012]
    x=[krill[y+offset]["density"] for y in years]
    results={}
    for sp in SPECIES:
        y=[stage[sp,z] for z in years]
        raw=correlation(x,y)
        rank=correlation(ranks(x),ranks(y))
        loo=[correlation(x[:i]+x[i+1:],y[:i]+y[i+1:]) for i in range(len(x))]
        results[sp]={
            "r":raw,"rank_r":rank,
            "leave_one_year_out_r_min":min(loo),
            "leave_one_year_out_r_max":max(loo),
            "n_source_colony_or_island_stage_rows":sum(source_counts[sp,z] for z in years),
            "n_years":len(years)
        }
    return {
        "acoustic_survey_offset_years":offset,
        "label":subset_label,
        "paired_breeding_years":years,
        "n_independent_calendar_year_opportunities":len(years),
        "observed_unique_survey_years":[y+offset for y in years],
        "survey_years_with_incomplete_source_coverage":[y+offset for y in years if not krill[y+offset]["full_coverage"]],
        "species":results
    }

def run(acoustic_csv,stage_annual_csv,stage_raw_csv):
    krill=acoustic(acoustic_csv)
    stage,src=stagelink(stage_annual_csv,stage_raw_csv)
    all_runs={}
    for label,offset in (("preseason",0),("concurrent_summer",1)):
        all_runs[label]={sub:analysis(krill,stage,src,offset,sub)
                          for sub in ("all","coverage_full","coverage_full_without_2012")}
    year_rows=[]
    for t in YEARS:
        obs={
            "breeding_season_start":t,
            "preseason_survey_year":t,
            "preseason_krill_density_g_m2":krill[t]["density"],
            "preseason_biomass_million_tonnes":krill[t]["biomass"],
            "preseason_survey_cv":krill[t]["cv"],
            "preseason_survey_full":krill[t]["full_coverage"],
            "concurrent_survey_year":t+1,
            "concurrent_krill_density_g_m2":krill[t+1]["density"],
            "concurrent_survey_full":krill[t+1]["full_coverage"],
        }
        for sp in SPECIES:
            obs[sp+"_fledglings_per_pair_native_stage"]=stage[sp,t]
            obs[sp+"_source_stage_units"]=src[sp,t]
        year_rows.append(obs)
    return {
        "status":"POST_EXPOSURE_EXTERNAL_KRILL_SOURCE_EXPLORATORY_NOT_CAUSAL",
        "n_regional_acoustic_surveys":len(krill),
        "n_same_island_breeding_seasons":len(YEARS),
        "species":list(SPECIES),
        "source_type":"Published IMR Table 2 overall-stratum hydroacoustic biomass estimates, not raw acoustic/trawl records",
        "source_url":PUBLISHER,"paper_url":PAPER,
        "acoustic_csv_sha256":hashlib.sha256(Path(acoustic_csv).read_bytes()).hexdigest(),
        "stage_csv_sha256":hashlib.sha256(Path(stage_annual_csv).read_bytes()).hexdigest(),
        "source_stage_csv_sha256":hashlib.sha256(Path(stage_raw_csv).read_bytes()).hexdigest(),
        "comparison":all_runs,"per_year":year_rows,
        "caveats":[
            "One regional krill survey per calendar year is not site-specific krill availability around Signy.",
            "2013 and 2015 coverage restricted by sea ice; inclusion/exclusion shown without choosing positive associations.",
            "Three species have one shared regional survey-year exposure, not three independent ocean replicates.",
            "Survey acoustic frequency varies: 38 vs 120 kHz; detection/comparability and CV matter.",
            "Preseason survey Jan-Feb t is BEFORE breeding season t; local krill field may change by breeding months.",
            "Concurrent survey Jan-Feb t+1 overlaps/succeeds recorded fledgling counts and is not a validated causal predictor.",
            "Annual BAS pre-fledging ratios do not identify recruitment, breeding patch selection, or occupied nesting area.",
            "No model links this ten-year biomass survey causally to sea ice, sea surface salinity, temperature or CMIP6 futures."
        ]
    }

def verify(output):
    expectations={
      "preseason":{
        "all":{"Adelie":-0.21160538308997398,"Chinstrap":-0.5591205943534584,"Gentoo":-0.54611367372603},
        "coverage_full":{"Adelie":-0.3586880600793267,"Chinstrap":-0.7942144981208394,"Gentoo":-0.6633578440970012},
        "coverage_full_without_2012":{"Adelie":0.04433855731546693,"Chinstrap":0.01053320760250549,"Gentoo":0.21428259055756424}
      },
      "concurrent_summer":{
        "all":{"Adelie":0.211766000,"Chinstrap":0.098842000,"Gentoo":0.363102000}
      }
    }
    for label,groups in expectations.items():
        for subset,values in groups.items():
            actual=output["comparison"][label][subset]["species"]
            for sp,value in values.items():
                tol=1e-8 if label=="preseason" else 5e-3
                if not math.isclose(actual[sp]["r"],value,abs_tol=tol):
                    raise ValueError(f"published dataset stage receipt mismatch: {label}/{subset}/{sp}: {actual[sp]['r']} vs {value}")
    assert output["n_regional_acoustic_surveys"]==10
    assert output["n_same_island_breeding_seasons"]==9
    assert output["comparison"]["preseason"]["coverage_full"]["n_independent_calendar_year_opportunities"]==7
    assert output["comparison"]["preseason"]["coverage_full_without_2012"]["n_independent_calendar_year_opportunities"]==6
    return True

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--acoustic-csv",type=Path,default=SOURCE)
    parser.add_argument("--stage-dir",required=True,type=Path)
    parser.add_argument("--out",required=True,type=Path)
    parser.add_argument("--check-receipt",action="store_true")
    a=parser.parse_args()
    result=run(a.acoustic_csv,a.stage_dir/"species_annual_stage_summary.csv",
               a.stage_dir/"source_stage_site_seasons.csv")
    if a.check_receipt:
        verify(result)
    a.out.mkdir(parents=True,exist_ok=True)
    with (a.out/"year_alignment.csv").open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=list(result["per_year"][0]))
        w.writeheader()
        w.writerows(result["per_year"])
    public={k:v for k,v in result.items() if k!="per_year"}
    (a.out/"result.json").write_text(json.dumps(public,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({
        "status":result["status"],
        "preseason":{k:{"years":v["n_independent_calendar_year_opportunities"],
                        "r_by_species":{sp:q["r"] for sp,q in v["species"].items()}}
                     for k,v in result["comparison"]["preseason"].items()},
        "concurrent":{k:{"years":v["n_independent_calendar_year_opportunities"],
                          "r_by_species":{sp:q["r"] for sp,q in v["species"].items()}}
                     for k,v in result["comparison"]["concurrent_summer"].items()},
        "receipt_checked":bool(a.check_receipt)},ensure_ascii=False))

if __name__=="__main__":
    main()
