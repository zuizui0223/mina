"""Assess whether GPS→published-GAM Chinstrap island contrasts survive source QA.

Reuses ORIGINAL BAS 300 TDR/GPS source sensor QA (all tags retained), and the
separately reconstructed 308 native Chinstrap GPS deployments × original Freer
2011-20 GAM model cells. The original source GAM fitted IMR acoustics, ice,
salinity. This is observational instrument-selection robustness, NOT an
independent krill measurement, causal island test or foraging effect.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,math,statistics
from pathlib import Path
import chinstrap_300tag_observability_v1 as qa

GPS_SHA="44cb30e8b3136317578d4e86b1dcf99146fae6ab0e721e35a05d4e5ebc6bdda6"
PAIRS=((2011,"LI"),(2013,"PI"),(2015,"MI"))
TIERS=("all_GPS","TDR_GPS_source_matched","source_QA_primary","source_QA_strict")

def original_gps(file):
    raw=Path(file).read_bytes()
    if hashlib.sha256(raw).hexdigest()!=GPS_SHA:
        raise ValueError("original GPS-island model output content SHA changed")
    rows=list(csv.DictReader(raw.decode("utf-8-sig").splitlines()))
    if len(rows)!=308*4:
        raise ValueError("308 original GPS deployments x four published geographical sensitivity sets changed")
    selected=[]
    for r in rows:
        if (r["minimum_island_center_distance_km"]!="10" or
            r["isolated_speed_spikes_removed"]!="True"):
            continue
        if r["qualifies_source_hourly_support"]=="True":
            for k in ("preseason_native_model_krill_g_m2","same_summer_native_model_krill_g_m2"):
                if not r[k]:raise ValueError("qualified GPS source missing model estimate")
            selected.append(r)
    if len(selected)!=253 or len({r["deployment"] for r in selected})!=253:
        raise ValueError("source GPS-geographic qualification roster changed")
    return selected

def joined(cohort,qa_rows):
    q={x["original_source_id"]:x for x in qa_rows}
    output=[]
    for g in cohort:
        decision=q.get(g["deployment"])
        matched=(decision is not None)
        row={
            "season_start":int(g["season_start"]),
            "island":g["island"],
            "source_GPS_deployment":g["deployment"],
            "original_GPS_qualified_10_150km":True,
            "original_TDR_GPS_source_tag_match":matched,
            "source_QA_primary":decision["primary_source_observability"] if matched else None,
            "source_QA_strict":decision["strict_GPS_sensitivity"] if matched else None,
            "not_source_matched_is_missing_TDR_not_nondiving":not matched,
            "preseason_model_g_m2":float(g["preseason_native_model_krill_g_m2"]),
            "same_summer_model_g_m2":float(g["same_summer_native_model_krill_g_m2"])
        }
        output.append(row)
    return output

def include(row,tier):
    if tier=="all_GPS":return True
    if tier=="TDR_GPS_source_matched":return row["original_TDR_GPS_source_tag_match"]
    if tier=="source_QA_primary":return row["source_QA_primary"] is True
    if tier=="source_QA_strict":return row["source_QA_strict"] is True
    raise ValueError("unexpected tier")

def comparisons(rows):
    output=[]
    for season,other in PAIRS:
        for tier in TIERS:
            for period in ("preseason","same_summer"):
                attr=period+"_model_g_m2"
                a=[r[attr] for r in rows if r["season_start"]==season and r["island"]=="SI" and include(r,tier)]
                b=[r[attr] for r in rows if r["season_start"]==season and r["island"]==other and include(r,tier)]
                if not a or not b:
                    raise ValueError("no paired GPS source opportunity for "+str((season,other,tier)))
                ma,mb=statistics.mean(a),statistics.mean(b)
                output.append({
                    "season_start":season,"comparison_island":other,
                    "reference_island":"SI","source_observability_tier":tier,
                    "published_krill_model_period":period,
                    "n_reference_deployments":len(a),"n_other_deployments":len(b),
                    "SI_source_GPS_model_g_m2":ma,
                    "other_source_GPS_model_g_m2":mb,
                    "ratio_other_div_SI":mb/ma if ma>0 else None,
                    "n_island_pairs_not_independent_year_replicates":1,
                    "all_analyzed_values_are_published_GAM_not_captured_krill":True,
                    "selection_is_post_source_instrument_QA_not_randomized":True
                })
    return output

def verify(rows,records):
    if len(rows)!=253:raise ValueError("GPS qualified total changed")
    counts={
        "matched":sum(r["original_TDR_GPS_source_tag_match"] for r in rows),
        "primary":sum(r["source_QA_primary"] is True for r in rows),
        "strict":sum(r["source_QA_strict"] is True for r in rows)
    }
    if counts!={"matched":247,"primary":175,"strict":47}:
        raise ValueError("original TDR/GPS cohort overlap changed "+str(counts))
    expected={
        (2011,"LI","all_GPS"):2.4401791626507325,
        (2013,"PI","all_GPS"):6.3144099881199685,
        (2015,"MI","all_GPS"):2.747735214032483,
        (2011,"LI","source_QA_primary"):2.329590318243858,
        (2013,"PI","source_QA_primary"):6.849201580257687,
        (2015,"MI","source_QA_primary"):2.7906451009453566,
        (2011,"LI","source_QA_strict"):2.0817661157883505,
        (2013,"PI","source_QA_strict"):8.926260378832072,
        (2015,"MI","source_QA_strict"):3.0015589401041
    }
    for key,val in expected.items():
        season,other,tier=key
        current=next(r for r in records if r["season_start"]==season
                     and r["comparison_island"]==other
                     and r["source_observability_tier"]==tier
                     and r["published_krill_model_period"]=="preseason")
        if not math.isclose(current["ratio_other_div_SI"],val,abs_tol=1e-9,rel_tol=1e-9):
            raise ValueError("source-calculated held original/model field discrepancy "+str(key))
    if len(records)!=3*4*2:
        raise ValueError("missing geographic QA/specification outputs")
    return counts

def save(file,records):
    with Path(file).open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(records[0]))
        w.writeheader();w.writerows(records)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--gps-model",required=True,type=Path)
    p.add_argument("--tdr-qa",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    p.add_argument("--check",action="store_true")
    args=p.parse_args()
    base=original_gps(args.gps_model)
    qa_rows=qa.evaluate(qa.read(args.tdr_qa))
    qcounts,qislands=qa.summary(qa_rows)
    if args.check:qa.verify(qcounts,qislands)
    combined=joined(base,qa_rows)
    values=comparisons(combined)
    counts=verify(combined,values) if args.check else {
        "matched":sum(r["original_TDR_GPS_source_tag_match"] for r in combined),
        "primary":sum(r["source_QA_primary"] is True for r in combined),
        "strict":sum(r["source_QA_strict"] is True for r in combined)
    }
    args.out.mkdir(parents=True,exist_ok=True)
    save(args.out/"source_GPS_TDR_observability_join_253.csv",combined)
    save(args.out/"island_matched_year_robustness_24.csv",values)
    result={
        "status":"PUBLISHED_MODEL_GPS_ISLAND_CONTRAST_ROBUST_TO_POST_SOURCE_QA_SENSITIVITY",
        "original_GPS_source_model_csv_sha256":GPS_SHA,
        "original_BAS_300_sensor_QA_source_sha256":qa.INPUT_SHA,
        "original_GPS_qualified_tags":len(combined),
        "source_QA_matched_and_pass_counts":counts,
        "all_source_300_tag_flags_retained":True,
        "matched_years":[x[0] for x in PAIRS],
        "source_qa_not_external_pressure_or_dive_calibration":True,
        "recorded_independent_island_year_pair_comparisons":3,
        "all_modelled_source_fields_only":True,
        "all_24_fixed_results":values,
        "no_biological_test_or_forecast_approved":True,
        "cautions":[
            "Freer 2025 GAM prey fields are model predictions using original IMR acoustics plus sea ice and salinity.",
            "GPS positions do not confirm foraging, capture, ocean position or penguin survival.",
            "The source sensor QA is post-exposure and can select birds by device deployment quality; not randomized.",
            "2011 Signy n=3 in source-QA cohort; 2013 Signy n=8, and stricter n=3. Small sample sensitivity is important.",
            "Three matched comparisons are at three different other islands and years. Not repeated island effects.",
            "No source 2013 combined acoustic stratum observed; published GAM interpolates environmental/acoustic model predictions.",
            "No 2050/2100 climate-driven future breeding abundance, N_eff or vegetation calculation is validated."
        ]
    }
    (args.out/"decision.json").write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps({"status":result["status"],"source_QA":counts,
         "primary": [{"season":r["season_start"],"other":r["comparison_island"],
                      "n":(r["n_other_deployments"],r["n_reference_deployments"]),
                      "ratio":r["ratio_other_div_SI"]} for r in values
                     if r["published_krill_model_period"]=="preseason"
                     and r["source_observability_tier"]=="source_QA_primary"],
         "verified":bool(args.check)},ensure_ascii=False))
if __name__=="__main__":
    main()
