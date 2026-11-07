"""Observed penguin niche reorganization at two time windows (exploratory).

Strictly source-backed original MAPPPD counts and OSI-SAF nearshore ice.
No claim of identified warming response, competition, or future nest numbers.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]/"outputs"
INPUTS={
    "bio":("comparison_audit/mapppd_unambiguous_site_seasons.csv","fc134e364cf38699fa7611d7dee5fbbbcb370c0a"),
    "pairs":("warming_species_breeding_v1/matched_species_breeding_change.csv","f17b4a21e9e5a045a40f5a4af9019e3bbc011758"),
    "ice":("climate_penguin/macro_monthly_seaice_1991_2020.csv","4fcea71c2d8b1069b6ad143f6522061ed434daf5"),
    "future":("warming_species_breeding_v1/future_climate_coobserved_sites.csv","97ae24e98a0cb5f6b36e275d036cb4b71c953312"),
}
def read_original():
    out={}
    for label,(relative,expected) in INPUTS.items():
        raw=(ROOT/relative).read_bytes()
        sha=hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()
        if sha!=expected:
            raise ValueError("Git blob changed "+label+" "+sha)
        with (ROOT/relative).open(newline="",encoding="utf-8") as f:
            out[label]=list(csv.DictReader(f))
    if tuple(len(out[k]) for k in ("bio","pairs","ice","future"))!=(2999,13,9600,32):
        raise ValueError("Input row count drift")
    return out
def average(a):
    return sum(a)/len(a)
def slope(x,y):
    xm=average(x); ym=average(y); denom=sum((t-xm)**2 for t in x)
    if denom<1e-10:
        raise ValueError("Insufficient temporal variation")
    return sum((t-xm)*(u-ym) for t,u in zip(x,y))/denom
def pearson(rows,a,b):
    if len(rows)<3:return None
    x=[r[a] for r in rows]; y=[r[b] for r in rows]
    ax=average(x); ay=average(y)
    den=math.sqrt(sum((v-ax)**2 for v in x)*sum((v-ay)**2 for v in y))
    return sum((v-ax)*(w-ay) for v,w in zip(x,y))/den if den>1e-10 else None
def writecsv(path,rows):
    if not rows:raise ValueError("Empty output")
    with path.open("w",newline="",encoding="utf-8") as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]))
        writer.writeheader();writer.writerows(rows)
def run(outdir):
    source=read_original()
    bio={(r["site_id"],r["species_id"],int(r["season"]),r["method"]):r for r in source["bio"]}
    if len(bio)!=2999:raise ValueError("Duplicate original biological rows")
    ice={(r["site_id"],int(r["year"]),int(r["month"])):float(r["sic_mean"]) for r in source["ice"]
         if r["complete_month"]=="True" and r["inner_km"]=="0"}
    if len(ice)!=4800:raise ValueError("Incomplete satellite source")
    sites=[];years=[];intervals=[]
    for pair in source["pairs"]:
        if pair["compared_species"]!="GEPE" or pair["gate"]!="1":continue
        if pair["method_compared"]!=pair["method_reference"]:raise ValueError("Count method mismatch")
        sy=[int(t) for t in pair["common_years"].split(";")]
        rows=[]
        for year in sy:
            a=bio.get((pair["site_id"],"ADPE",year,pair["method_reference"]))
            g=bio.get((pair["site_id"],"GEPE",year,pair["method_compared"]))
            if a is None or g is None or a["count"]=="" or g["count"]=="":
                raise ValueError("Unmatched original count")
            an=float(a["count"]); gn=float(g["count"])
            if not math.isfinite(an+gn) or min(an,gn)<0:raise ValueError("Invalid nest counts")
            s=[ice[(pair["site_id"],year,m)] for m in (8,9,10,11)]
            rows.append(dict(site_id=pair["site_id"],region=pair["region"],year=year,
                adelie_n=an,gentoo_n=gn,log_adelie=math.log(an) if an>0 else None,
                log_gentoo=math.log(gn) if gn>0 else None,
                log_gentoo_over_adelie=math.log(gn/an) if min(an,gn)>0 else None,
                september_sic_pct=s[1],aug_nov_sic_pct=average(s)))
        # Availability-only exclusion of any zero abundance: no log1p pseudo-replacement.
        if any(r["log_gentoo_over_adelie"] is None for r in rows):continue
        if len(sy)<5 or sy[-1]-sy[0]<10:raise ValueError("Historical pair support changed")
        observed=lambda attr: [r[attr] for r in rows]
        full=list(range(1991,2021))
        def all_ice(months):
            return [average([ice[(pair["site_id"],y,m)] for m in months]) for y in full]
        sa=10*slope(sy,observed("log_adelie"))
        sg=10*slope(sy,observed("log_gentoo"))
        ratio=10*slope(sy,observed("log_gentoo_over_adelie"))
        log1p=10*slope(sy,[math.log1p(r["gentoo_n"])-math.log1p(r["adelie_n"]) for r in rows])
        if abs(log1p-float(pair["common_year_log1p_ratio_slope_decade"]))>1e-9:
            raise ValueError("Original slope conflict "+pair["site_id"])
        sites.append(dict(site_id=pair["site_id"],region=pair["region"],
            n_common_years=len(sy),first_year=sy[0],last_year=sy[-1],
            adelie_log_count_slope_per_decade=sa,gentoo_log_count_slope_per_decade=sg,
            real_log_gentoo_adelie_ratio_slope_per_decade=ratio,
            observed_years_september_sic_slope_pp_per_decade=10*slope(sy,observed("september_sic_pct")),
            observed_years_aug_nov_sic_slope_pp_per_decade=10*slope(sy,observed("aug_nov_sic_pct")),
            full_1991_2020_september_sic_slope_pp_per_decade=10*slope(full,all_ice((9,))),
            full_1991_2020_aug_nov_sic_slope_pp_per_decade=10*slope(full,all_ice((8,9,10,11)))))
        years+=rows
        for i in range(1,len(rows)):
            before,after=rows[i-1],rows[i]
            if after["year"]!=before["year"]+1:continue
            da=after["log_adelie"]-before["log_adelie"]
            dg=after["log_gentoo"]-before["log_gentoo"]
            intervals.append(dict(site_id=pair["site_id"],region=pair["region"],
                start_year=before["year"],end_year=after["year"],
                delta_log_adelie=da,delta_log_gentoo=dg,delta_log_ratio=dg-da,
                same_sign_growth=int(da*dg>0),opposite_sign_growth=int(da*dg<0),
                delta_sic_september_pp=after["september_sic_pct"]-before["september_sic_pct"],
                delta_sic_aug_nov_pp=after["aug_nov_sic_pct"]-before["aug_nov_sic_pct"]))
    sites.sort(key=lambda r:r["site_id"])
    years.sort(key=lambda r:(r["site_id"],r["year"]))
    intervals.sort(key=lambda r:(r["site_id"],r["end_year"]))
    names=[r["site_id"] for r in sites]
    if names!=["ARDL","BISC","LION","LLAN","PCHA","PETE"] or (len(years),len(intervals))!=(67,45):
        raise ValueError("Source matching changed")
    loo=[]
    for site in names:
        sub=[x for x in intervals if x["site_id"]!=site]
        loo.append(dict(excluded_site=site,intervals=len(sub),
          correlation_species_delta_log_count=pearson(sub,"delta_log_adelie","delta_log_gentoo"),
          correlation_delta_ratio_delta_september_ice=pearson(sub,"delta_log_ratio","delta_sic_september_pp")))
    f=[r for r in source["future"] if r["site_id"] in names and
       r["experiment"]=="ssp585" and r["period"]=="2081-2100"]
    if len(f)!=6 or len({r["site_id"] for r in f})!=6:raise ValueError("CMIP6 site support mismatch")
    summary={
      "date":"2026-11-02","status":"exploratory_source_matched_niche_timescale_divergence_no_causal_warming_inference",
      "source_git_blobs":{k:v[1] for k,v in INPUTS.items()},
      "n_bio_rows":len(source["bio"]),"n_monthly_satellite_rows":len(source["ice"]),
      "n_original_species_pair_groups":len(source["pairs"]),
      "selection":"ADPE/GEPE identical method, >=5 coobserved years spanning >=10 years, strictly both positive all coobserved years (post-hoc)",
      "site_codes":names,"n_sites":len(sites),"n_regions":len({r["region"] for r in sites}),
      "n_site_years":len(years),"n_contiguous_year_intervals":len(intervals),
      "n_sites_opposite_absolute_trends":sum(r["adelie_log_count_slope_per_decade"]<0 and r["gentoo_log_count_slope_per_decade"]>0 for r in sites),
      "n_sites_real_ratio_rising":sum(r["real_log_gentoo_adelie_ratio_slope_per_decade"]>0 for r in sites),
      "n_observation_window_september_ice_rising":sum(r["observed_years_september_sic_slope_pp_per_decade"]>0 for r in sites),
      "n_observation_window_aug_nov_ice_rising":sum(r["observed_years_aug_nov_sic_slope_pp_per_decade"]>0 for r in sites),
      "n_full_1991_2020_aug_nov_ice_declining":sum(r["full_1991_2020_aug_nov_sic_slope_pp_per_decade"]<0 for r in sites),
      "n_one_year_species_change_same_direction":sum(x["same_sign_growth"] for x in intervals),
      "n_one_year_species_change_opposite_direction":sum(x["opposite_sign_growth"] for x in intervals),
      "corr_one_year_species_growth":pearson(intervals,"delta_log_adelie","delta_log_gentoo"),
      "corr_one_year_ratio_change_sic_change":pearson(intervals,"delta_log_ratio","delta_sic_september_pp"),
      "leave_one_site_out":loo,
      "future_ssp585_2081_2100_physical_only":{
         "n_sites":len(f),"n_three_model_warming":sum(r["all3_tas_increase"]=="1" for r in f),
         "n_three_model_sic_decrease":sum(r["all3_sic_decrease"]=="1" for r in f),
         "mean_temperature_change_C":average([float(r["tas_C_change_model_mean"]) for r in f]),
         "mean_seaice_change_pp":average([float(r["SIC_pp_change_model_mean"]) for r in f])
      },
      "limits":["two geographic regions","site- and year-dependent sampling","one-year intervals non-independent",
                "nearshore SIC not individual foraging SIC","no identified causal warming effect",
                "climate-to-nests future projection disallowed","phenology matched camera and nesting footprints not co-registered"]
    }
    if (summary["n_sites_opposite_absolute_trends"],summary["n_sites_real_ratio_rising"],
        summary["n_observation_window_september_ice_rising"],
        summary["n_observation_window_aug_nov_ice_rising"],
        summary["n_full_1991_2020_aug_nov_ice_declining"],
        summary["n_one_year_species_change_same_direction"],
        summary["n_one_year_species_change_opposite_direction"])!=(6,6,4,2,6,20,25):
        raise ValueError("Source-defined contrasts no longer match audited expected values")
    outdir=Path(outdir)
    outdir.mkdir(parents=True,exist_ok=True)
    writecsv(outdir/"site_trends.csv",sites)
    writecsv(outdir/"site_years.csv",years)
    writecsv(outdir/"annual_intervals.csv",intervals)
    (outdir/"summary.json").write_text(json.dumps(summary,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    return summary
if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",type=Path,default=ROOT/"niche_timescale_divergence_v1")
    args=parser.parse_args()
    d=run(args.out)
    print(json.dumps(d,ensure_ascii=False,indent=2))
