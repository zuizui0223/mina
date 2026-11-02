"""Join independently source-pinned BAS diet and recorded chick-stage panels at Signy.

Do NOT treat within-species stomach samples or source colonies as independent
marine climate replications. Recorded chicks are not fledged recruits.
"""
from __future__ import annotations
import argparse,csv,json,math
from collections import defaultdict
from pathlib import Path

def read(path):
    with Path(path).open(newline="",encoding="utf-8") as f:return list(csv.DictReader(f))
def number(v):
    try:
        x=float(v)
        return x if math.isfinite(x) else None
    except (TypeError,ValueError):return None
def mean(vals):return sum(vals)/len(vals)
def r(rows,x,y):
    if len(rows)<4:return None
    aa=[t[x] for t in rows]; bb=[t[y] for t in rows]
    if any(z is None for z in aa+bb):return None
    ma=mean(aa);mb=mean(bb)
    den=math.sqrt(sum((t-ma)**2 for t in aa)*sum((t-mb)**2 for t in bb))
    return sum((a-ma)*(b-mb) for a,b in zip(aa,bb))/den if den>1e-12 else None
def savecsv(path,rows):
    if not rows:raise ValueError("No joined rows")
    with Path(path).open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def run(dietdir,stagedir,outdir):
    diet=read(Path(dietdir)/"diet_species_breeding_season.csv")
    pairs=read(Path(dietdir)/"diet_pair_season_antecedent_sic.csv")
    stages=read(Path(stagedir)/"species_annual_stage_summary.csv")
    di={};sc={}
    for row in diet:
        key=row["species"],int(row["season_start"])
        if key in di:raise ValueError("Duplicate diet species-season")
        di[key]=row
    for row in stages:
        key=row["species"],int(row["season_start"])
        if key in sc:raise ValueError("Duplicate stage species-season")
        sc[key]=row
    joined=[]
    for key in sorted(set(di)&set(sc)):
        d,s=di[key],sc[key]
        if int(d["n_valid_stomachs"])<3:continue
        fish=number(d["mean_stomach_fish_fraction"])
        chick=number(s["median_recorded_chicks_per_pair"])
        if fish is None or chick is None or not 0<=fish<=1 or chick<0:continue
        joined.append(dict(species=key[0],breeding_season_start=key[1],
          n_stomach_samples=int(d["n_valid_stomachs"]),
          mean_stomach_fish_fraction=fish,
          median_recorded_chicks_per_pair=chick,
          stage_spatial_unit=s["original_spatial_unit"],
          stage_observed_colonies=int(s["observed_colonies"]),
          stage_strict_date_colonies=int(s["strict_date_colonies"]),
          stage_strict_median_chicks_per_pair=number(s["strict_median_recorded_chicks_per_pair"])))
    jindex={(x["species"],x["breeding_season_start"]):x for x in joined}
    if len(jindex)!=len(joined):raise ValueError("Join duplicated source grain")
    pairjoined=[]
    for row in pairs:
        a,b=row["pair"].split("-")
        year=int(row["breeding_season_start"])
        x=jindex.get((a,year));y=jindex.get((b,year))
        if x is None or y is None:continue
        pairjoined.append(dict(pair=row["pair"],breeding_season_start=year,
          fish_gap_b_minus_a=number(row["fish_share_gap_b_minus_a"]),
          chick_gap_b_minus_a=y["median_recorded_chicks_per_pair"]-x["median_recorded_chicks_per_pair"],
          preceding_september_sic_pct=number(row["preceding_sep_sic_pct"]),
          stage_spatial_unit_a=x["stage_spatial_unit"],
          stage_spatial_unit_b=y["stage_spatial_unit"],
          n_stomachs_a=x["n_stomach_samples"],n_stomachs_b=y["n_stomach_samples"],
          n_stage_components_a=x["stage_observed_colonies"],n_stage_components_b=y["stage_observed_colonies"]))
    if len(joined)<10 or not pairjoined:raise ValueError("No sufficient cross-axis source support")
    per_species={}
    for sp in sorted({row["species"] for row in joined}):
        xx=[row for row in joined if row["species"]==sp]
        per_species[sp]=dict(n_seasons=len(xx),first=min(t["breeding_season_start"] for t in xx),
           last=max(t["breeding_season_start"] for t in xx),
           fish_fraction_vs_chick_stage_r=r(xx,"mean_stomach_fish_fraction","median_recorded_chicks_per_pair"),
           n_chick_stage_gt2=sum(t["median_recorded_chicks_per_pair"]>2 for t in xx),
           n_strict_chick_stage_present=sum(t["stage_strict_median_chicks_per_pair"] is not None for t in xx))
    per_pair={}
    for label in sorted({x["pair"] for x in pairjoined}):
        xx=sorted((row for row in pairjoined if row["pair"]==label),key=lambda x:x["breeding_season_start"])
        per_pair[label]=dict(n_same_seasons=len(xx),
          fish_gap_vs_chick_gap_r=r(xx,"fish_gap_b_minus_a","chick_gap_b_minus_a"),
          fish_gap_vs_antecedent_sic_r=r(xx,"fish_gap_b_minus_a","preceding_september_sic_pct"),
          chick_gap_vs_antecedent_sic_r=r(xx,"chick_gap_b_minus_a","preceding_september_sic_pct"),
          loo_fish_chick_r=[r(xx[:i]+xx[i+1:],"fish_gap_b_minus_a","chick_gap_b_minus_a") for i in range(len(xx))] if len(xx)>=5 else [],
          positive_fish_gap_seasons=sum(t["fish_gap_b_minus_a"]>0 for t in xx))
    summary=dict(
      date="2026-11-02",status="same_signy_season_measured_diet_chick_stage_associations_not_causal",
      underlying_diet_species_seasons=len(diet),underlying_stage_species_seasons=len(stages),
      season_matched_species_rows=len(joined),season_matched_pair_rows=len(pairjoined),
      source_year_overlap=len({t["breeding_season_start"] for t in joined}),
      per_species=per_species,per_pair=per_pair,
      source_grain="BAS individual-stomach mean within species-season versus BAS original-colony median recorded chicks per pair",
      spatial_grain_warning="Gentoo stages from island aggregate vs Adelie/Chinstrap stages from individual colonies; between-species chick-gap magnitudes cannot be interpreted as population fitness contrast",
      observation_time_warning="Chick-stage monitoring and creche diet may overlap in time; environmental exposure does not prove a forward causal chain",
      independent_climate_clusters=1,
      no_future_penguin_count_forecast=True)
    outdir=Path(outdir);outdir.mkdir(parents=True,exist_ok=True)
    savecsv(outdir/"same_season_diet_chick_stage.csv",joined)
    savecsv(outdir/"same_season_pair_diet_chick_gap.csv",pairjoined)
    (outdir/"summary.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return summary
if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--diet-derived",type=Path,required=True)
    p.add_argument("--stage-derived",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    o=p.parse_args()
    print(json.dumps(run(o.diet_derived,o.stage_derived,o.out),ensure_ascii=False,indent=2))
