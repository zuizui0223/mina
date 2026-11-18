"""Audit original MAPPPD nest-count calendar months for all three penguin species.
Read exact frozen macro interval panel and original MAPPPD RData. Do not impute months.
"""
import argparse, hashlib, json
from pathlib import Path
import pandas as pd
import numpy as np
import pyreadr
OBS_SHA="b569def7d9a121bcca4bf78f4a4918af16f07e252ac65578ccc7636f3242afbd"
AFTER_SEPT={10,11,12,1,2,3,4,5,6}
def norm(x): return str(x).strip().lower().replace("_"," ")
def num(x): return f"{float(x):.6f}"
def main():
    p=argparse.ArgumentParser()
    for flag in ("rda","intervals","out"):p.add_argument("--"+flag,required=True)
    a=p.parse_args();folder=Path(a.out);folder.mkdir(parents=True,exist_ok=True)
    rda=Path(a.rda)
    if hashlib.sha256(rda.read_bytes()).hexdigest()!=OBS_SHA:raise ValueError("Source RDA SHA drift")
    raw=pyreadr.read_r(str(rda))["penguin_obs"]
    if len(raw)!=5487:raise ValueError("Raw source count drift")
    known=raw.loc[raw.month.notna()&raw.year.notna()&raw.season.notna()]
    if not (known.season.astype(int)==known.year.astype(int)-(known.month.astype(int)<=6).astype(int)).all():
        raise ValueError("Original calendar/season conversion mismatch")
    df=pd.read_csv(a.intervals)
    if len(df)!=216 or df.site_id.nunique()!=26 or set(df.species_id)!={"ADPE","GEPE","CHPE"}:
        raise ValueError("Macro interval source cohort drift")
    raw=raw.loc[raw.type.eq("nests")&raw.species_id.isin(["ADPE","GEPE","CHPE"])].copy()
    raw["method"]=raw.vantage.map(norm)
    raw["count_numeric"]=pd.to_numeric(raw["count"],errors="coerce")
    raw=raw[raw.count_numeric.notna()&raw.season.notna()].copy()
    matches={}
    for o in raw.itertuples(index=False):
        key=(str(o.site_id),str(o.species_id),int(o.season),str(o.method),num(o.count_numeric))
        matches.setdefault(key,[]).append(o)
    observed={}
    for row in df.itertuples(index=False):
        for phase in ("start","end"):
            site,sp,season,method=row.site_id,row.species_id,int(getattr(row,phase+"_year")),norm(row.method)
            count=float(getattr(row,"n_"+phase))
            key=(str(site),str(sp),season,method,num(count))
            if key in observed:continue
            candidates=matches.get(key,[])
            months=[int(o.month) for o in candidates if pd.notna(o.month)]
            all_known=bool(candidates) and len(months)==len(candidates)
            observed[key]=dict(site_id=site,species_id=sp,season=season,
                method=method,nest_count=count,raw_source_matches=len(candidates),
                months_known=all_known,after_september=all_known and all(m in AFTER_SEPT for m in months),
                after_november=all_known and all(m in {12,1,2,3,4,5,6} for m in months),
                months=";".join(map(str,sorted(set(months)))))
    ev=pd.DataFrame(list(observed.values()))
    if len(ev)<200:raise ValueError("Too few source events")
    if not ev.raw_source_matches.gt(0).all():
        print("SOURCE_MATCH_FAILURE "+ev.loc[ev.raw_source_matches.eq(0)].to_string(index=False),flush=True)
        raise ValueError("Some interval nests not traceable to matching raw count+method")
    # Existing original ADPE-only calendar product provides an independent source crosswalk.
    prev=pd.read_csv("research/climate-penguin/outputs/climate_penguin/historical_count_season_timing.csv")
    pv=prev.set_index(["site_id","species_id","season","method"])
    compared=0
    for o in ev.loc[ev.species_id.eq("ADPE")].itertuples(index=False):
        key=(o.site_id,o.species_id,int(o.season),o.method)
        if key not in pv.index:continue
        prior=pv.loc[key]
        compared+=1
        if bool(prior.all_months_known)!=bool(o.months_known) or bool(prior.all_after_september)!=bool(o.after_september):
            raise ValueError("Frozen ADPE calendar support disagreement "+str(key))
    if compared<80:raise ValueError("Insufficient ADPE cross-source calendar verification")
    r=[]
    for o in df.itertuples(index=False):
        first=(str(o.site_id),str(o.species_id),int(o.start_year),norm(o.method),num(o.n_start))
        last=(str(o.site_id),str(o.species_id),int(o.end_year),norm(o.method),num(o.n_end))
        a,b=observed[first],observed[last]
        r.append(dict(site_id=o.site_id,species_id=o.species_id,region=o.region,
            start_year=int(o.start_year),end_year=int(o.end_year),method=norm(o.method),
            both_months_known=bool(a["months_known"] and b["months_known"]),
            both_after_september=bool(a["after_september"] and b["after_september"]),
            both_after_november=bool(a["after_november"] and b["after_november"]),
            first_months=a["months"],last_months=b["months"]))
    intervals=pd.DataFrame(r)
    prev_adelie=int(intervals.loc[intervals.species_id.eq("ADPE"),"both_after_september"].sum())
    if prev_adelie!=31:raise ValueError(f"ADPE original 31 source calendar intervals drifted: {prev_adelie}")
    ev.to_csv(folder/"original_nest_event_months.csv",index=False)
    intervals.to_csv(folder/"216_original_interval_calendar.csv",index=False)
    summary=intervals.groupby("species_id").agg(intervals=("site_id","size"),
      sites=("site_id","nunique"),both_known=("both_months_known","sum"),
      both_after_september=("both_after_september","sum"),
      both_after_november=("both_after_november","sum")).reset_index()
    result=dict(source_sha256=OBS_SHA,original_observation_rows=5487,
      matched_original_events=len(ev),crossvalidated_ADPE_events=compared,
      original_intervals=len(intervals),by_species=summary.to_dict("records"),
      all_species_known=int(intervals.both_months_known.sum()),
      all_species_after_september=int(intervals.both_after_september.sum()),
      original_ADPE_31_supported_intervals_reproduced=True,
      interpretation="Source counts/date provenance only, no climate effect; missing counts/months not imputed")
    (folder/"calendar_receipt.json").write_text(json.dumps(result,indent=2,default=int)+"\n")
    print("THREE_SPECIES_MONTH_AUDIT_RESULT "+json.dumps(result,default=int),flush=True)
if __name__=="__main__":main()
