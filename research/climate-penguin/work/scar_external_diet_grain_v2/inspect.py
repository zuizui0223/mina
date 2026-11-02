"""Pin SCAR diet source 22/189/398: prey-mass fraction grain and breeding seasons.

2023 SCAR archived source is unchanged; do NOT equate a study-year aggregate
with one stomach. No SIC response before percent mass and season QC.
"""
from __future__ import annotations
import argparse,csv,hashlib,datetime,collections,json,math,importlib.util
from pathlib import Path
HERE=Path(__file__).resolve().parents[1]
P=HERE/"scar_external_diet_v1/audit.py"
spec=importlib.util.spec_from_file_location("scarsource",P)
s=importlib.util.module_from_spec(spec);spec.loader.exec_module(s)
SOURCES={"22":"Cape Shirreff","189":"Gourlay Peninsula (Signy)","398":"Stranger Point"}
def read(path):
    raw=Path(path).read_bytes()
    sha=hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()
    if sha!=s.BLOB:raise ValueError("Source diet blob mismatch")
    return list(csv.DictReader(raw.decode("utf-8-sig").splitlines()))
def season_start(start,end):
    try:
        a=datetime.date.fromisoformat(str(start)[:10]);b=datetime.date.fromisoformat(str(end)[:10])
    except ValueError:return None
    if a>b:raise ValueError("Source date reversed")
    if a.year==b.year:
        if a.month<=4 and b.month<=4:return a.year-1
        if a.month>=11 and b.month>=11:return a.year
        return None
    if b.year==a.year+1 and a.month>=11 and b.month<=4:return a.year
    return None
def mean(vals):return sum(vals)/len(vals)
def save(path,rows,cols):
    with Path(path).open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=cols);w.writeheader()
        for z in rows:w.writerow({k:z.get(k,"") for k in cols})
def run(src,outdir):
    data=read(src)
    sub=[r for r in data if r.get("source_id") in SOURCES and s.species(r)]
    if len(sub)!=119:raise ValueError("Target source row number drift: "+str(len(sub)))
    items=[];groups=collections.defaultdict(list)
    for r in sub:
        yr=season_start(r.get("observation_date_start"),r.get("observation_date_end"))
        label=s.species(r);fraction=s.num(r.get("fraction_diet_by_weight"))
        item=dict(source_id=r["source_id"],source_location=SOURCES[r["source_id"]],
             species=label,season_start=yr,original_calendar_year=s.year(r),
             source_record_date_start=r.get("observation_date_start"),
             source_record_date_end=r.get("observation_date_end"),
             predator_sample_id=r.get("predator_sample_id"),source_sample_count=r.get("predator_sample_count"),
             source_location_label=r.get("location"),prey_name=r.get("prey_name"),
             prey_aggregate_flag=r.get("prey_is_aggregate"),prey_class=s.group(r),
             weight_fraction=fraction,
             source_quality_flag=r.get("quality_flag"),source_is_secondary=r.get("is_secondary_data"),
             source_predator_stage=r.get("predator_breeding_stage"),
             source_record_id=r.get("record_id"))
        items.append(item)
        groups[(r["source_id"],label,yr,str(r.get("predator_sample_id","")))].append(item)
    annual=[]
    for (source_id,label,yr,sample_id),a in sorted(groups.items(),key=lambda kv:str(kv[0])):
        # SCAR trace -999 is *unknown small amount*, not negative diet mass.
        # An aggregate prey group and its constituent species are nested, not additive.
        def group_fraction(taxon):
            rr=[z for z in a if z["prey_class"]==taxon]
            summary=[z for z in rr if str(z["prey_aggregate_flag"]).upper()=="Y"]
            if summary:
                good=[z["weight_fraction"] for z in summary if z["weight_fraction"] is not None and 0<=z["weight_fraction"]<=1]
                return (sum(good) if good and len(good)==len(summary) else None),len(good)
            if any(z["weight_fraction"] is not None and z["weight_fraction"]<0 for z in rr):
                return None,sum(z["weight_fraction"] is not None and 0<=z["weight_fraction"]<=1 for z in rr)
            good=[z["weight_fraction"] for z in rr if z["weight_fraction"] is not None and 0<=z["weight_fraction"]<=1]
            return (sum(good) if good else None),len(good)
        fish,nfish=group_fraction("fish")
        crust,ncrust=group_fraction("crustacean")
        others=[z["weight_fraction"] for z in a if z["prey_class"] is None
                and z["weight_fraction"] is not None and 0<=z["weight_fraction"]<=1]
        denom=fish+crust if fish is not None and crust is not None else None
        ntrace=sum(z["weight_fraction"] == -999 for z in a)
        annual.append(dict(source_id=source_id,source_location=SOURCES[source_id],species=label,
            breeding_season_start=yr,original_calendar_year=min((z["original_calendar_year"] for z in a if z["original_calendar_year"] is not None),default=None),
            sample_id=sample_id,n_rows=len(a),n_fish_rows=nfish,n_crust_rows=ncrust,
            n_other_weight_rows=len(others),n_missing_weight_rows=sum(z["weight_fraction"] is None for z in a),
            n_trace_sentinel_rows=ntrace,
            n_aggregate_prey_rows=sum(str(z["prey_aggregate_flag"]).lower() in ("y","true","1") for z in a),
            fish_fraction_of_all_prey=fish,crust_fraction_of_all_prey=crust,
            fish_plus_crust_fraction=denom,fish_within_fish_plus_crust=(fish/denom if denom and denom>0 else None),
            other_weight_sum=sum(others),total_all_prey_weight=(denom+sum(others) if denom is not None else None),
            n_source_sample_counts=len({z["source_sample_count"] for z in a if s.valid(z["source_sample_count"])}),
            n_quality_not_G=sum(str(z["source_quality_flag"]).upper()!="G" for z in a),
            n_secondary=sum(str(z["source_is_secondary"]).upper() in ("Y","TRUE","1") for z in a)))
    outdir=Path(outdir);outdir.mkdir(parents=True,exist_ok=True)
    save(outdir/"raw_taxon_weight_audit.csv",items,list(items[0]))
    save(outdir/"prey_mass_per_source_sample.csv",annual,list(annual[0]))
    bysrc={}
    for id in SOURCES:
        a=[z for z in annual if z["source_id"]==id]
        bysrc[id]=dict(n_diet_rows=sum(x["n_rows"] for x in a),n_sample_year_species=len(a),
            n_seasons=len({z["breeding_season_start"] for z in a if z["breeding_season_start"] is not None}),
            season_years=sorted({z["breeding_season_start"] for z in a if z["breeding_season_start"] is not None}),
            species=sorted({z["species"] for z in a}),
            n_fish_and_crust_mass=sum(z["fish_within_fish_plus_crust"] is not None for z in a),
            n_fish_crust_total_above_100pct=sum(z["fish_plus_crust_fraction"] is not None and z["fish_plus_crust_fraction"]>1.001 for z in a),
            n_all_prey_total_above_100pct=sum(z["total_all_prey_weight"] is not None and z["total_all_prey_weight"]>1.001 for z in a),
            n_trace_sentinel_rows=sum(z["n_trace_sentinel_rows"] for z in a),
            n_secondary_rows=sum(z["n_secondary"] for z in a),
            n_source_quality_not_G=sum(z["n_quality_not_G"] for z in a))
    result=dict(status="raw_fraction_grain_audit_no_climate_effect",source_sha=s.BLOB,
        source_zenodo=s.COMMIT,n_source_rows=len(sub),n_prey_mass_groups=len(annual),
        sources=bysrc,
        no_go_flags=["SCAR weight fractions can aggregate individuals and are not individual wet grams",
          "Signy source 189 duplicates Lynnes 2004 and cannot independently replicate Signy",
          "Cape Shirreff source 22 has only two breeding seasons",
          "Stranger Point source 398 has Adélie alone; no species-gap test",
          "missing prey weight is NA not zero; mixed prey hierarchy may double count if aggregates included"])
    (outdir/"summary.json").write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps({k:result[k] for k in ("n_source_rows","n_prey_mass_groups","sources")},ensure_ascii=False))
    return result
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--diet",type=Path,required=True);p.add_argument("--out",type=Path,required=True)
    v=p.parse_args();run(v.diet,v.out)
