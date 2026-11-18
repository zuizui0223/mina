"""Evaluate previously frozen climate predictions ONLY on source-verified post-Sept count intervals.
Training uses the ORIGINAL full panel and is not re-fit: this is test-stratum diagnostic.
"""
import argparse,csv,json,math,statistics
from collections import Counter
from pathlib import Path
PREDICTORS=("no_change","species_mean","baseline","SIC","SST_SSS","SIC_SST_SSS")
STRATEGIES=("chronological","chronological_site_out","chronological_marine_cell_out")
def read(path):
    with open(path,encoding="utf-8",newline="") as f:return list(csv.DictReader(f))
def write(path,rows):
    with open(path,"w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def key(row):return str(row["site_id"]),str(row["species_id"]),int(row["end_year"])
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--macro",type=Path,required=True)
    p.add_argument("--calendar",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
    original=read(a.macro/"macro_original_breeding_ocean_intervals.csv")
    month=read(a.calendar/"216_original_interval_calendar.csv")
    pred=read(a.macro/"macro_all_temporal_holdout_predictions.csv")
    if len(original)!=216 or len(month)!=216:raise ValueError("Original 216 source cohort changed")
    if len(set(map(key,original)))!=216 or len(set(map(key,month)))!=216:
        raise ValueError("Duplicate original biological/calendar join keys")
    by_month={key(row):row for row in month}
    if set(map(key,original))!=set(by_month):raise ValueError("Original month audit not aligned to original site×species×year")
    valid={k for k,row in by_month.items() if row["both_after_september"]=="True"}
    if len(valid)!=43 or Counter(k[1] for k in valid)!={"ADPE":31,"CHPE":3,"GEPE":9}:
        raise ValueError("The independently source-audited 43 confirmed month intervals have changed")
    original_index={key(row):row for row in original}
    tagged=[]
    for row in pred:
        k=key(row)
        if k not in by_month:raise ValueError("Prediction has no exact original calendar key "+str(k))
        actual=float(row["target_log_nests_growth"])
        if abs(actual-float(original_index[k]["delta_log_nests"]))>1e-11:
            raise ValueError("Predictions do not match the original paired nest counts")
        row["source_month_gate_confirmed"] = (k in valid)
        row["calendar_known"] = by_month[k]["both_months_known"]
        if k in valid:tagged.append(row)
    for scope in STRATEGIES:
        if len([x for x in pred if x["strategy"]==scope])<150:raise ValueError("Original forecast source incomplete "+scope)
    if not tagged:raise ValueError("No test fold survives calendar gate")
    out=[]
    for scope in STRATEGIES:
        for sp in ("ALL","ADPE","CHPE","GEPE"):
            r=[x for x in tagged if x["strategy"]==scope and (sp=="ALL" or x["species_id"]==sp)]
            if not r:continue
            sites=len(set(x["site_id"] for x in r))
            for name in PREDICTORS:
                errors=[float(x["predict_"+name])-float(x["target_log_nests_growth"]) for x in r]
                out.append({"strategy":scope,"species":sp,"model":name,"intervals":len(r),
                            "sites":sites,"independent_test_site_years":len(set((x["site_id"],x["end_year"]) for x in r)),
                            "MAE":statistics.mean(abs(e) for e in errors),
                            "RMSE":math.sqrt(statistics.mean(e*e for e in errors))})
    write(a.out/"month_verified_test_predictions.csv",tagged)
    write(a.out/"month_verified_holdout_metrics.csv",out)
    summary={
       "status":"completed_original_source_calendar_stratum_hindcast_no_retraining",
       "original_macro_intervals":216,"verified_post_September_original_intervals":43,
       "verified_by_species":{"ADPE":31,"CHPE":3,"GEPE":9},
       "full_training_note":"Frozen forecast models trained on ALL 216 source observations; month flags only restrict the test set. Thus not fully time-verified training.",
       "subset_folds":{scope:{
           "intervals":len([x for x in tagged if x["strategy"]==scope]),
           "unique_sites":len(set(x["site_id"] for x in tagged if x["strategy"]==scope))
       }for scope in STRATEGIES},
       "MAE_overview":{scope:{
          k:next((r["MAE"] for r in out if r["strategy"]==scope and r["species"]=="ALL" and r["model"]==k),None)
          for k in PREDICTORS
       }for scope in STRATEGIES},
       "forecast_permitted":False,
       "basis_for_gate":"Only 43 original intervals are calendar-verified; 12 are non-Adelie, model trained with mostly calendar-unknown intervals; geographical transfer and out-of-sample climate gain must both be demonstrated.",
    }
    (a.out/"month_verified_forecast_check.json").write_text(json.dumps(summary,indent=2)+"\n",encoding="utf-8")
    print("TIME_VERIFIED_SUBSET_RESULT "+json.dumps(summary),flush=True)
if __name__=="__main__": main()
