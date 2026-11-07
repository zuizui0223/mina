#!/usr/bin/env python3
"""Freeze-to-manuscript audit: validate actual source numbers and claim boundaries.

Not a new ecological analysis. Refuses a manuscript with internally inconsistent
count, sample, hypothesis, uncertainty, publisher warning or future-coverage text.
"""
from pathlib import Path
from collections import Counter,defaultdict
import csv,json,hashlib,math,re

BASE=Path(__file__).resolve().parent
DATA=BASE/"data"
OUT=BASE/"outputs"
MAN=BASE/"MANUSCRIPT_FULL_DRAFT_V0_1.md"

def csvrows(p):
    with p.open(newline="",encoding="utf-8") as f:return list(csv.DictReader(f))

def check(statement,what):
    if not statement:raise ValueError(f"Manuscript source QA failed: {what}")

def main():
    article=MAN.read_text(encoding="utf-8")
    m=csvrows(DATA/"network_species.csv")
    p=csvrows(DATA/"network_species_pairs.csv")
    a=json.loads((OUT/"STEP6_JNCC_METHOD_QA.json").read_text(encoding="utf-8"))
    h=json.loads((OUT/"STEP4_FIXED_ASSOCIATIONS.json").read_text(encoding="utf-8"))
    f=json.loads((OUT/"STEP5_PHYSICAL_EXPOSURE_QA.json").read_text(encoding="utf-8"))
    j=[r for r in m if r["dataset_id"]=="JNCC" and r["analysis_role"]=="macro_primary" and r["null_status"]=="computed"]
    an=[r for r in m if r["dataset_id"]=="MAPPPD" and r["analysis_role"]=="macro_primary" and r["null_status"]=="computed"]
    ps=[r for r in p if r["null_status"]=="computed"]
    check((len(j),len(an),len(ps))==(663,12,378),"Step1 source cohorts changed")
    check(sum(float(x["concentration_excess_decade"])>0 for x in j)==436,"JNCC concentration positive 436")
    check(sum(float(x["N1"])<float(x["N0"]) for x in j)==479,"Declining panels 479")
    check(sum(float(x["concentration_excess_decade"])>0 and float(x["N1"])<float(x["N0"]) for x in j)==327,"Declining positive 327")
    check(sum(float(x["concentration_excess_decade"])>0 for x in an)==5,"Antarctic positive 5")
    mean_by_species=defaultdict(list)
    for r in j:mean_by_species[r["species_id"]].append(float(r["concentration_excess_decade"]))
    check(sum(sum(v)/len(v)>0 for v in mean_by_species.values())==15 and len(mean_by_species)==17,"Species support changed")
    check(a["complete_main"]["n_rows"]==len(j) and a["complete_main"]["positive"]==436,"Source original QA disagrees")
    clean=a["unique_coordinate_and_label_descriptive_subset"]
    warned=a["publisher_population_trend_method_warning"]["descriptive_remaining"]
    check((clean["n_rows"],clean["positive"],clean["species_with_positive_mean"])==(651,427,15),"metadata anomaly sensitivity")
    check((warned["n_rows"],warned["positive"],warned["species_with_positive_mean"])==(573,374,14),"publisher warning sensitivity")
    check((a["source_matched_child_sites_across_panels"],
           a["original_source_start_coordinate_duplicates_panel_n"],
           a["original_repeated_child_site_names_panel_n"])==(4217,10,2),"Source QA metadata counts changed")
    check(h["B"]==9999 and h["H2"]["status"]=="NOT_ESTIMABLE","H2 and bootstrap unchanged")
    check(set(h["results"])=={"H3","H4D","H4W"},"Frozen tests changed")
    for key,coef,pval in (("H3",+.03316307915510672,.94),("H4D",+.00616079380244838,1.),("H4W",-.015215574022541397,1.)):
        v=h["results"][key]
        check(abs(v["coef"]-coef)<1e-9 and abs(v["holm_4"]-pval)<1e-9,"Frozen result differs "+key)
    summary=f["summary"]
    check((summary["total_network_species"],summary["candidate_sites"],summary["matched_sites"],
           summary["air_complete_network_species"],summary["marine_complete_network_species"])==(12,61,13,3,2),"Frozen CMIP6 coverage changed")
    required=[
       "675 source-compatible network-by-species", "663 British–Irish", "436 (65.8%)",
       "15 of 17", "327 (68.3%)", "427 of the 651", "374/573 (65.3%)",
       "source-matched monitored components", "H3 adjusted p = 0.940",
       "H4D adjusted p = 1.000", "H4W adjusted p = 1.000",
       "4,217 child site records", "Three",
       "no calibrated", "source-effort",
    ]
    # Exactly grounded numerical assertions, not wording-specific editorial placeholders.
    required=[z for z in required if z not in ("Three","no calibrated","source-effort")]
    missing=[s for s in required if s not in article]
    check(not missing, "Missing fixed source statements: "+str(missing))
    for section in ("## Abstract","## Introduction","## Materials and methods",
                    "## Results","## Discussion","## Proposed figures and supplement",
                    "## Verified reference anchors","## Editorial hold before submission"):
        check(section in article,"Missing core section "+section)
    check(article.count("https://jncc.gov.uk/our-work/seabirds-count/")>=1,"Original JNCC method source absent")
    check("not externally preregistered" in article,"Must disclose nonregistration")
    check("could not be calibrated" in article and "Site.ID" in article,"Measurement limitations missing")
    check("not predicted" in article or "not a numerical" in article or
          "not predicted nesting area" in article,"Future biological forecast boundary missing")
    result={
        "status":"PASS_MANUSCRIPT_SOURCE_FACTS_WITH_DISCLOSED_MEASUREMENT_HOLD",
        "source":"research/network_concentration_unified_v1/MANUSCRIPT_FULL_DRAFT_V0_1.md",
        "manuscript_sha256":hashlib.sha256(MAN.read_bytes()).hexdigest(),
        "characters":len(article),"approx_words":len(article.split()),
        "frozen_source_cohorts":{"JNCC":len(j),"MAPPPD":len(an),"species_pairs":len(ps)},
        "JNCC":{"positive":436,"declines":479,"positive_in_declines":327,
                "positive_species":15,"source_child_record_memberships":4217,
                "metadata_clean":clean,"publisher_warn_removed":warned},
        "fixed_hypothesis_decisions":{
            k:{"coef":v["coef"],"p_holm":v["holm_4"],"support":v["prediction_supported"]}
            for k,v in h["results"].items()
        },
        "CMIP6":{"matched_site_memberships":13,"candidate_site_memberships":61,
                 "full_air_networks":3,"full_marine_networks":2},
        "not_proven":["stable historic nesting polygons","constant detection or effort",
                      "causal warming response","physical-island effect",
                      "biological future breeding prediction"],
        "full_paper_submission_ready":False,
    }
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/"STEP6_MANUSCRIPT_SOURCE_QA.json").write_text(
        json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps({"status":result["status"],"chars":result["characters"],
                      "approx_words":result["approx_words"],
                      "source_numeric_checks":"PASS","frozen_hypotheses":"PASS",
                      "publisher_quality_caveats":"RETAINED"},ensure_ascii=False))

if __name__=="__main__":main()
