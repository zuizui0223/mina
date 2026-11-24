"""Count concurrent source support only; do not estimate spatial overlap."""
from __future__ import annotations
import argparse,hashlib,importlib.util,json,re,zipfile
from collections import defaultdict
from pathlib import Path
import pandas as pd
ROOT=Path(__file__).resolve().parents[3]
MD5="168e5b9b5c4ed20bb84dd00145acb0a5"
def hashfile(p,kind):
    h=hashlib.new(kind)
    with open(p,"rb") as f:
        for b in iter(lambda:f.read(4<<20),b""):h.update(b)
    return h.hexdigest()
def field(df,names):
    present=[c for c in names if c in df.columns]
    return present[0] if len(present)==1 else None
def read_seals(path):
    if hashfile(path,"md5")!=MD5:raise ValueError("RAATD archive MD5 drift")
    with zipfile.ZipFile(path) as z:
        names=z.namelist()
        tracks=[n for n in names if Path(n).name=="ANFS_ssm_by_id_predicted.csv"]
        meta=[]
        for n in names:
            if not n.lower().endswith(".csv") or not re.search("meta",n,re.I):continue
            h=pd.read_csv(z.open(n),nrows=0)
            if {"individual_id","abbreviated_name"}<=set(h.columns):meta.append(n)
        if len(tracks)!=1 or len(meta)!=1:raise ValueError("RAATD member ambiguity "+str({"tracks":tracks,"metadata":meta,"csv":[n for n in names if n.endswith(".csv")]}))
        t=pd.read_csv(z.open(tracks[0]),low_memory=False)
        m=pd.read_csv(z.open(meta[0]),low_memory=False)
    need={"individual_id","date","decimal_latitude","decimal_longitude"}
    if not need<=set(t):raise ValueError("RAATD tracking schema changed")
    m=m.loc[m.abbreviated_name.eq("ANFS")].copy()
    if m.individual_id.isna().any() or m.individual_id.duplicated().any():raise ValueError("seal metadata ID missing/duplicate")
    if not set(t.individual_id)<=set(m.individual_id):raise ValueError("unmatched seal track ID")
    if len(t)!=209472 or t.individual_id.nunique()!=313:raise ValueError("ANFS track counts differ from published table")
    # Audit explicit source metadata; no inferred sex or deployment locality.
    fields=dict(sex=field(m,["sex","individual_sex"]),lat=field(m,["deployment_latitude","deployment_lat","deploy_latitude","deploy_lat","latitude_deployment","latitude_deploy"]),lon=field(m,["deployment_longitude","deployment_lon","deploy_longitude","deploy_lon","longitude_deployment","longitude_deploy"]),date=field(m,["deployment_date","deploy_date","deployment_datetime","date_deploy","date_deployment"]))
    t["utc"]=pd.to_datetime(t.date,format="mixed",utc=True,errors="coerce")
    if t.utc.isna().any():raise ValueError("unparsed seal date")
    box=t.decimal_latitude.between(-63,-58)&t.decimal_longitude.between(-48,-42)
    t=t.loc[box&t.utc.dt.year.eq(2016)&t.utc.dt.month.isin([1,2])].copy()
    t["day"]=t.utc.dt.strftime("%Y-%m-%d")
    candidates=m.loc[m.individual_id.isin(t.individual_id)]
    cohort_cols=[c for c in ("individual_id","dataset_identifier","abbreviated_name","sex","age","breeding_stage","keepornot","deployment_location","site","colony",*fields.values()) if c and c in candidates]
    cohort_cols=list(dict.fromkeys(cohort_cols))
    local_ids=set()
    if all(fields.values()):
        ds=pd.to_datetime(m[fields["date"]],format="mixed",errors="coerce",utc=True)
        la=pd.to_numeric(m[fields["lat"]],errors="coerce");lo=pd.to_numeric(m[fields["lon"]],errors="coerce")
        select=m[fields["sex"]].astype(str).str.strip().str.lower().isin(["m","male"])&la.between(-61.5,-60)&lo.between(-47,-44)&ds.dt.year.eq(2016)&ds.dt.month.eq(1)
        local_ids=set(m.loc[select,"individual_id"])
    r={"archive_md5":MD5,"archive_sha256":hashfile(path,"sha256"),"track_member":tracks[0],"metadata_member":meta[0],"metadata_columns":list(m.columns),"mapped_fields":fields,"candidate_cohort_metadata":candidates[cohort_cols].fillna("").astype(str).to_dict("records"),"local_male_ids":sorted(map(str,local_ids)),"all_seal_ids_in_box":int(t.individual_id.nunique())}
    return t,local_ids,r
def penguins(path):
    s=ROOT/"research/climate-penguin/work/climate_penguin/signy_gps_krill_access_v1.py"
    spec=importlib.util.spec_from_file_location("gps",s);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    tracks,receipt=m.read_tracks(path)
    days=defaultdict(set);ids=defaultdict(set)
    for tr in tracks:
        if tr["season"]!=2015:continue
        sp=tr["species"]
        for t,lat,lon,_ in tr["points"]:
            if t.year==2016 and t.month in (1,2) and -63<=lat<=-58 and -48<=lon<=-42:
                days[(sp,t.date().isoformat())].add(tr["deployment"]);ids[sp].add(tr["deployment"])
    return days,receipt,{sp:len(v) for sp,v in ids.items()}
def main():
    p=argparse.ArgumentParser();p.add_argument("--raatd",type=Path,required=True);p.add_argument("--gps",type=Path,required=True);p.add_argument("--out",type=Path,required=True);a=p.parse_args()
    a.out.mkdir(parents=True,exist_ok=True)
    report={"status":"SOURCE_BLOCKED","outcome_model_executed":False,"spatial_overlap_calculated":False}
    try:
        pdays,gps,pi=penguins(a.gps);report.update(gps_receipt=gps,penguin_unique_ids_janfeb_in_box=pi)
        t,local,seal=read_seals(a.raatd);report["seal_receipt"]=seal
        all_days={d:set(g.individual_id) for d,g in t.groupby("day")}
        dates=pd.date_range("2016-01-01","2016-02-29").strftime("%Y-%m-%d")
        daily=[];eligible=[];unique=defaultdict(set)
        for day in dates:
            sd=all_days.get(day,set()); sl=sd&local
            counts={sp:len(pdays.get((sp,day),set())) for sp in ("Adelie","Chinstrap","Gentoo")}
            row={"day":day,**counts,"all_seals":len(sd),"local_male_seals":len(sl)}
            daily.append(row)
            if counts["Adelie"]>=3 and counts["Chinstrap"]>=3 and len(sl)>=3:
                eligible.append(day)
                for sp in ("Adelie","Chinstrap"):unique[sp].update(pdays[sp,day])
                unique["local_male_seals"].update(sl)
        n={sp:len(unique[sp]) for sp in ("Adelie","Chinstrap","local_male_seals")}
        report.update(status="DESIGN_SUPPORT_REVIEW_REQUIRED" if len(eligible)>=5 and min(n.values())>=5 else "NO_GO_FIXED_COMMON_DATE_GATE",eligible_days=eligible,unique_tracks_on_eligible_days=n,daily_support=daily)
    except Exception as e:report["error"]=str(e)
    (a.out/"source_support.json").write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps({k:v for k,v in report.items() if k not in ("seal_receipt","gps_receipt","daily_support")}))
if __name__=="__main__":main()
