"""Exploratory original Signy penguin diet ↔ pre-departure fledgling output.

Frozen source fields and species-year grain selected from a preceding
headers-only audit. No krill availability, climate causal effect or 2100 nest
forecast is inferred. One stomach-sample record is not one ecosystem year.
"""
from __future__ import annotations
import argparse
import csv
import datetime as dt
import hashlib
import io
import json
import math
import re
import statistics
import zipfile
from collections import Counter,defaultdict
from pathlib import Path

SOURCE={
    "Adelie":("signy_adelie_diet_summary.csv","ab05193e94864ca05ea54a01154506f8e86f85291e2f01a68abab5d92229a04d"),
    "Chinstrap":("signy_chinstrap_diet_summary.csv","a8dc89e0440cc8826925fc65bf9194de5151162b83c7d42db7ba3c97d49b164a"),
    "Gentoo":("signy_gentoo_diet_summary.csv","6f2a5fa1fc136ad6102dee8cd1c429d24c8ab81b50077bd21eb03f4e80fbd902")
}
COLS=("DATE","RECORD_ID","TOTAL_MASS_g","EUPHAUSIA_SUPERBA_MASS_g","FISH_MASS_g")
SPECIES=("Adelie","Chinstrap","Gentoo")


def number(v):
    if v is None or str(v).strip().lower() in ("","na","nan","none","n/a","unknown"):
        return None
    try:
        x=float(str(v).strip())
    except ValueError:
        return None
    return x if math.isfinite(x) else None


def date(v):
    value=str(v).strip()
    if re.fullmatch(r"\d{4}-\d{1,2}-\d{1,2}",value):
        y,m,d=(int(x) for x in value.split("-"))
        return dt.date(y,m,d)
    if re.fullmatch(r"\d{1,2}/\d{1,2}/\d{4}",value):
        d,m,y=(int(x) for x in value.split("/"))
        return dt.date(y,m,d)
    if re.fullmatch(r"\d{4}/\d{1,2}/\d{1,2}",value):
        y,m,d=(int(x) for x in value.split("/"))
        return dt.date(y,m,d)
    raise ValueError("unrecognized exact diet sample DATE (no imputation): "+value)


def load_diet_zip(species,path):
    name,sha=SOURCE[species]
    if not zipfile.is_zipfile(path):
        raise ValueError("publisher ZIP invalid")
    with zipfile.ZipFile(path) as z:
        matching=[n for n in z.namelist() if n.endswith("/"+name) or n==name]
        if len(matching)!=1:
            raise ValueError(f"unresolved publisher diet summary CSV {species}: {matching}")
        raw=z.read(matching[0])
    if hashlib.sha256(raw).hexdigest()!=sha:
        raise ValueError("original diet source SHA mismatch "+species)
    rows=list(csv.DictReader(io.StringIO(raw.decode("utf-8-sig"))))
    if not set(COLS).issubset(set(rows[0])):
        raise ValueError("source diet measurement columns changed")
    samples=[];audit=Counter(); seen=set()
    for i,r in enumerate(rows,1):
        observation=date(r["DATE"])
        year=observation.year if observation.month>=7 else observation.year-1
        sample_id=str(r["RECORD_ID"]).strip()
        if not sample_id:
            audit["missing_record_id"]+=1
            continue
        key=(sample_id,observation)
        if key in seen:
            audit["duplicate_original_sample_id_date"]+=1
            continue
        seen.add(key)
        total=number(r["TOTAL_MASS_g"])
        krill=number(r["EUPHAUSIA_SUPERBA_MASS_g"])
        fish=number(r["FISH_MASS_g"])
        if total is None or krill is None:
            audit["missing_mass_input"]+=1
            continue
        if total<=0 or krill<0 or krill>total+1e-8:
            audit["invalid_or_outside_total_mass"]+=1
            continue
        if fish is not None and (fish<0 or fish>total+1e-8):
            audit["fish_fraction_invalid"]+=1
            fish=None
        audit["valid_stomach_samples"]+=1
        samples.append(dict(species=species,season_start=year,
                           date=observation.isoformat(),
                           record_id=sample_id,
                           krill_share=krill/total,
                           stomach_total_g=total,
                           fish_share=fish/total if fish is not None else None,
                           original_row=i))
    audit["source_summary_rows"]=len(rows)
    audit["source_csv_sha256"]=sha
    audit["source_years_observed"]=len({r["season_start"] for r in samples})
    return samples,dict(audit)


def summary(samples):
    groups=defaultdict(list)
    for row in samples:
        groups[row["species"],row["season_start"]].append(row)
    out=[]
    for (sp,year),rr in sorted(groups.items()):
        krill=[r["krill_share"] for r in rr]
        total=[r["stomach_total_g"] for r in rr]
        out.append(dict(species=sp,season_start=year,n_sample=len(rr),
             krill_fraction_mean=statistics.mean(krill),
             krill_fraction_median=statistics.median(krill),
             mean_stomach_content_mass_g=statistics.mean(total),
             median_stomach_content_mass_g=statistics.median(total),
             first_diet_sample=min(r["date"] for r in rr),
             last_diet_sample=max(r["date"] for r in rr),
             target_min3=len(rr)>=3))
    return out


def pearson(x,y):
    if len(x)<5:
        return None
    ax=statistics.mean(x);ay=statistics.mean(y)
    a=[v-ax for v in x];b=[v-ay for v in y]
    denom=math.sqrt(sum(z*z for z in a)*sum(z*z for z in b))
    return sum(z*w for z,w in zip(a,b))/denom if denom>1e-10 else None


def stage_index(stage_annual,stage_raw):
    annual={}
    for r in stage_annual:
        k=r["species"],int(r["season_start"])
        score=number(r["median_recorded_fledglings_per_pair"])
        if score is not None:
            if k in annual:raise ValueError("duplicate annual stage")
            annual[k]=score
    dates=defaultdict(list)
    for r in stage_raw:
        if number(r["recorded_fledglings_per_pair"]) is None:
            continue
        d=r["fledgling_count_date"]
        if d:
            dates[(r["species"],int(r["season_start"]))].append(d)
    return annual,dates


def link(diet,stages,stage_dates):
    rows=[]
    for r in diet:
        if r["n_sample"]<3:
            continue
        key=r["species"],r["season_start"]
        if key not in stages:
            continue
        dates=stage_dates.get(key,[])
        earliest=min(dates) if dates else None
        latest=max(dates) if dates else None
        diet_before_all=bool(earliest and r["last_diet_sample"]<earliest)
        diet_after_all=bool(latest and r["first_diet_sample"]>=latest)
        rows.append({**r,
            "fledglings_per_pair_median":stages[key],
            "earliest_fledgling_count":earliest or "",
            "latest_fledgling_count":latest or "",
            "all_diet_samples_before_every_fledgling_count":diet_before_all,
            "all_diet_samples_after_every_fledgling_count":diet_after_all,
            "stage_dates_available":bool(dates)
        })
    return rows


def analyze(rows):
    res={}
    for sp in SPECIES:
        data=sorted([r for r in rows if r["species"]==sp],key=lambda z:z["season_start"])
        variables=("krill_fraction_mean","krill_fraction_median","mean_stomach_content_mass_g")
        y=[r["fledglings_per_pair_median"] for r in data]
        result={
            "species_years":len(data),
            "year_min":min([r["season_start"] for r in data],default=None),
            "year_max":max([r["season_start"] for r in data],default=None),
            "all_diet_samples_precede_all_fledgling_counts":sum(r["all_diet_samples_before_every_fledgling_count"] for r in data),
            "all_diet_samples_after_fledgling_counts":sum(r["all_diet_samples_after_every_fledgling_count"] for r in data),
            "ambiguous_or_mixed_chronology":sum(
                not r["all_diet_samples_before_every_fledgling_count"] and
                not r["all_diet_samples_after_every_fledgling_count"] for r in data)
        }
        for var in variables:
            xx=[r[var] for r in data]
            result["same_season_r_"+var]=pearson(xx,y)
            diffs=[(data[i][var]-data[i-1][var],
                    y[i]-y[i-1]) for i in range(1,len(data))
                   if data[i]["season_start"]==data[i-1]["season_start"]+1]
            result["consecutive_year_changes_"+var]=len(diffs)
            result["change_r_"+var]=(pearson([x for x,_ in diffs],[z for _,z in diffs])
                                     if diffs else None)
        res[sp]=result
    pairs={}
    for species_a,species_b in (("Adelie","Chinstrap"),("Adelie","Gentoo"),("Chinstrap","Gentoo")):
        a={r["season_start"]:r for r in rows if r["species"]==species_a}
        b={r["season_start"]:r for r in rows if r["species"]==species_b}
        years=sorted(set(a)&set(b))
        data=[(a[y],b[y]) for y in years]
        pair_diff=[(r2["krill_fraction_mean"]-r1["krill_fraction_mean"],
                    r2["fledglings_per_pair_median"]-r1["fledglings_per_pair_median"])
                   for r1,r2 in data]
        pairs[f"{species_a}|{species_b}"]={
            "same_years":len(years),
            "between_species_difference_r":pearson([x for x,_ in pair_diff],[v for _,v in pair_diff]),
            "no_independent_island_replication":True
        }
    return {"species":res,"same_island_species_pairs":pairs}


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--diet-dir",required=True,type=Path)
    ap.add_argument("--stage-dir",required=True,type=Path)
    ap.add_argument("--out",required=True,type=Path)
    args=ap.parse_args()
    diet_rows=[];sources={}
    for sp in SPECIES:
        items,audit=load_diet_zip(sp,args.diet_dir/(sp.lower()+".zip"))
        diet_rows+=items;sources[sp]=audit
    annual=summary(diet_rows)
    stage,dates=stage_index(
        list(csv.DictReader((args.stage_dir/"species_annual_stage_summary.csv").open(newline="",encoding="utf-8"))),
        list(csv.DictReader((args.stage_dir/"source_stage_site_seasons.csv").open(newline="",encoding="utf-8"))))
    matched=link(annual,stage,dates)
    result=dict(
        status="POST_SOURCE_EXPLORATORY_DIET_STAGE_ASSOCIATION_NO_CAUSAL_OR_FUTURE_FORECAST",
        source_audit=sources,
        all_species_annual_diet_rows=len(annual),
        linked_species_years=len(matched),
        all_three_diet_and_stage_years=sorted(set.intersection(
            *[{r["season_start"] for r in matched if r["species"]==sp} for sp in SPECIES])),
        metrics=analyze(matched),
        caveats=[
            "Stomach sample krill mass share reflects the food returned by captured breeders, not ambient krill biomass.",
            "This is a single island and common sample campaigns; birds, samples and colony rows do not replicate climate years.",
            "Sampling date during creche may not precede fledgling counting in all species-years; chronology output retained.",
            "Stage index uses source-colony median for Adelie and Chinstrap, aggregate series for Gentoo.",
            "No population growth or breeding area/Neff future forecast is fitted.",
            "Raw numerator/denominator anomalies, missingness and sampling effort are retained separately."
        ]
    )
    args.out.mkdir(parents=True,exist_ok=True)
    with (args.out/"diet_stage_species_year.csv").open("w",newline="",encoding="utf-8") as f:
        if matched:
            w=csv.DictWriter(f,fieldnames=list(matched[0]))
            w.writeheader();w.writerows(matched)
    (args.out/"result.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result,ensure_ascii=False))

if __name__=="__main__":
    main()
