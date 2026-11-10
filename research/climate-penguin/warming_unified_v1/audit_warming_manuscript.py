#!/usr/bin/env python3
"""Warming manuscript factual audit against Git-locked original-derived source rows.

Recomputes 9-year cross-axis contrasts and 6-site future climate independently
from archived inputs (not from the authors' summary JSON), then checks that
scientific claim boundaries and numerical values agree with the manuscript.
"""
from __future__ import annotations
import csv
import hashlib
import json
import math
from pathlib import Path

BASE=Path(__file__).resolve().parent
DATA=BASE/"data"
OUT=BASE/"outputs"
MAN=BASE/"MANUSCRIPT_WARMING_UNIFIED_V0_1.md"
SOURCE=OUT/"WARMING_UNIFIED_EVIDENCE.json"
SCENARIOS=(("ssp245","2041-2060"),("ssp245","2081-2100"),
           ("ssp585","2041-2060"),("ssp585","2081-2100"))

def getcsv(path):
    with path.open(newline="",encoding="utf-8") as f:
        return list(csv.DictReader(f))

def require(x,description):
    if not x:raise ValueError("WARMING_MANUSCRIPT_SOURCE_QA: "+description)

def pearson(a,b):
    ma=sum(a)/len(a);mb=sum(b)/len(b)
    numerator=sum((x-ma)*(y-mb) for x,y in zip(a,b))
    denominator=math.sqrt(sum((x-ma)**2 for x in a)*sum((y-mb)**2 for y in b))
    require(denominator>0,"zero variance in separate Pearson calculation")
    return numerator/denominator

def mean(xs):
    require(bool(xs),"mean of empty original source observations")
    return sum(xs)/len(xs)

def main():
    article=MAN.read_text(encoding="utf-8")
    evidence=json.loads(SOURCE.read_text(encoding="utf-8"))
    six=getcsv(DATA/"six_site_original_breeding_ice.csv")
    nine=getcsv(DATA/"signy_same_year_diet_phenology.csv")
    future=getcsv(DATA/"six_site_future_physical.csv")
    require((len(six),len(nine),len(future))==(6,9,24),"original strict cohort row count")
    require(evidence["status"]=="WARMING_SINGLE_PAPER_CROSS_AXIS_OBSERVATIONAL_JOIN_NO_CAUSAL_FORECAST",
            "source support not verified")
    source_sites={x["site_id"] for x in six}
    require(source_sites=={"ARDL","BISC","LION","LLAN","PCHA","PETE"},
            "six strict original sites changed")
    require(len({x["region"] for x in six})==2,"six sites no longer two geographical regions")
    require(all(float(x["first_Adelie"])>float(x["last_Adelie"]) and
                float(x["first_Gentoo"])<float(x["last_Gentoo"]) and
                float(x["log_ratio_slope_decade"])>0 for x in six),
            "original opposite absolute breeding trends and true ratio positive")
    require(sum(float(x["sep_SIC_observed_years_pp_decade"])>0 for x in six)==4,
            "4/6 sampled-year September ice direction")
    require(sum(float(x["aug_nov_SIC_full_1991_2020_pp_decade"])<0 for x in six)==6,
            "6/6 long-series Aug-Nov ice decrease")
    years=[int(x["year"]) for x in nine]
    require(years==list(range(2001,2010)),"nine exact nonselected shared climate years")
    stomachs=sum(int(x["n_stomachs_adelie"])+int(x["n_stomachs_gentoo"]) for x in nine)
    require(stomachs==422,"422 original Adélie/Gentoo stomachs only")
    ice=[float(x["sic_aug_nov_pct"]) for x in nine]
    diet=[float(x["diet_gap_fish_fraction"]) for x in nine]
    hatching=[float(x["hatching_gap_days"]) for x in nine]
    r_fish=pearson(ice,diet)
    r_hatch=pearson(ice,hatching)
    r_paired=pearson(diet,hatching)
    require(abs(r_fish-0.7814247513630724)<1e-10,"new source fish r")
    require(abs(r_hatch+0.06607505241266795)<1e-10,"new source time gap r")
    require(abs(r_paired+0.05180423317763634)<1e-10,"new source cross-axis r")
    for key,observed in (("r_sic_vs_fish_gap",r_fish),
                         ("r_sic_vs_hatching_gap",r_hatch),
                         ("r_fish_gap_vs_hatching_gap",r_paired)):
        require(abs(observed-evidence["same_year_Signy"][key])<1e-12,
                "evidence JSON and independent input calculation disagree "+key)
    require(abs(mean(hatching)-29.2222222222)<1e-9,"shared nine-year mean hatching gap")
    climate=[]
    for scenario,period in SCENARIOS:
        sub=[x for x in future if x["experiment"]==scenario and x["period"]==period]
        require(len(sub)==6 and {x["site_id"] for x in sub}==source_sites,
                "future input year/SSP missing strict site")
        marine=[x for x in sub if x["source_verified_marine"]=="1"]
        require(len(marine)==4 and
            {x["site_id"] for x in marine}=={"ARDL","BISC","LION","LLAN"},
                "future valid marine subset changed")
        require(all(x["SIC_pp_change_mean"]=="" and x["sos_change_native"]==""
                    for x in sub if x["site_id"] in {"PCHA","PETE"}),
                "distant grid ocean value was silently substituted")
        air_mean=mean([float(x["tas_C_change_mean"]) for x in sub])
        sic_mean=mean([float(x["SIC_pp_change_mean"]) for x in marine])
        sos_mean=mean([float(x["sos_change_native"]) for x in marine])
        reported=next(x for x in evidence["future_six_sites"]["scenario_site_equal_means"]
                      if x["experiment"]==scenario and x["period"]==period)
        for k,val in (("mean_tas_C",air_mean),("mean_SIC_pp",sic_mean),
                      ("mean_sos_native",sos_mean)):
            require(abs(reported[k]-val)<1e-12,"source six-site climate "+k)
        require(reported["n_unique_marine_fingerprints"]==2,
                "four sites repeated only two source ocean-grid cells")
        climate.append(dict(scenario=scenario,period=period,tas6=air_mean,sic4=sic_mean,sos4=sos_mean))
    fixed_phrases=[
       "six repeatedly monitored sites","all six","four sites",
       "nine identical breeding seasons","422 original",
       "r = 0.781","r = −0.066","r = −0.052",
       "29.22","+4.35°C","−23.94",
       "not external preregistration","not identify causal warming",
       "not a population projection","not identical",
       "A41 to A39","Youngflesh et al. (2026)","Clewlow et al. (2019)",
       "neither is a complete three-species","PCHA","PETE",
    ]
    missing=[x for x in fixed_phrases if x not in article]
    require(not missing,"missing essential manuscript scope/claims "+str(missing))
    require("772 independent climate" not in article,
            "pseudoreplicated three-species source")
    require("2050 colony forecast" not in article,
            "invalid quantitative future biology")
    result=dict(status="PASS_ORIGINAL_SOURCE_RECOMPUTATION_AND_WARMING_MANUSCRIPT_CLAIMS",
         manuscript="research/climate-penguin/warming_unified_v1/MANUSCRIPT_WARMING_UNIFIED_V0_1.md",
         manuscript_sha256=hashlib.sha256(MAN.read_bytes()).hexdigest(),
         original_evidence_sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
         six_original_sites=sorted(source_sites),independent_regions=2,
         same_climate_years=9,yearly_stomach_memberships=stomachs,
         same_ice_year_correlations=dict(
            fish_ice=r_fish,phenological_gap_ice=r_hatch,fish_vs_phenological_gap=r_paired),
         four_scenarios=climate,
         refused_claims=["climate-caused population replacement","same three species for both niche axes",
             "772 independent ocean-climate trials","numerical future nests, fish diet or hatching days",
             "land vegetation nest-polygon time series"],
         publication_ready=False)
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/"WARMING_MANUSCRIPT_QA.json").write_text(
        json.dumps(result,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps({"status":result["status"],"stomachs":stomachs,
        "shared_years":9,"r_fish":r_fish,"r_hatch":r_hatch,
        "future_ssp585_late_tas":climate[-1]["tas6"]}))

if __name__=="__main__":
    main()
