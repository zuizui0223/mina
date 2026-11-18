"""Original BAS Signy stomach sample fish:crustacean mass and prior-year sea ice.

All biological rates are first calculated for an individual stomach RECORD_ID
and then aggregated by breeding season x species. This is exploratory,
single-island observational evidence, not a forecast or causal effect.
"""
from __future__ import annotations
import argparse,csv,datetime,hashlib,io,json,math,zipfile
from collections import Counter,defaultdict
from pathlib import Path

HERE=Path(__file__).resolve().parents[2]
ICE=HERE/"outputs/climate_penguin/macro_monthly_seaice_1991_2020.csv"
SOURCES={
 "Adelie":("adelie","signy_adelie_diet_summary.csv","ab05193e94864ca05ea54a01154506f8e86f85291e2f01a68abab5d92229a04d",639),
 "Chinstrap":("chinstrap","signy_chinstrap_diet_summary.csv","a8dc89e0440cc8826925fc65bf9194de5151162b83c7d42db7ba3c97d49b164a",653),
 "Gentoo":("gentoo","signy_gentoo_diet_summary.csv","6f2a5fa1fc136ad6102dee8cd1c429d24c8ab81b50077bd21eb03f4e80fbd902",74)
}
FORMATS=("%Y-%m-%d","%d/%m/%Y","%d-%m-%Y","%d.%m.%Y","%d-%b-%Y","%d-%B-%Y","%Y/%m/%d",
         "%Y-%m-%d %H:%M:%S","%d/%m/%Y %H:%M:%S","%d/%m/%y")
def source_stomach_table(zippath,member,sha,nrows):
    with zipfile.ZipFile(zippath) as z:
        names=[name for name in z.namelist() if name.lower().endswith("/"+member) or name==member]
        if len(names)!=1:raise ValueError("Expected exactly one stomach table: "+member)
        raw=z.read(names[0])
    if hashlib.sha256(raw).hexdigest()!=sha:raise ValueError("Original stomach SHA change "+member)
    rows=list(csv.DictReader(io.StringIO(raw.decode("utf-8-sig"))))
    if len(rows)!=nrows:raise ValueError("Original stomach row count changed "+member)
    for required in ("DATE","RECORD_ID","TOTAL_MASS_g","FISH_MASS_g","CRUSTACEAN_MASS_g","EUPHAUSIA_SUPERBA_MASS_g"):
        if required not in rows[0]:raise ValueError("Missing source stomach column: "+required)
    return rows
def timestamp(v):
    x=str(v).strip()
    for fmt in FORMATS:
        try:return datetime.datetime.strptime(x,fmt).date()
        except ValueError:pass
    return None
def season(t):
    if t.month<=4:return t.year-1
    if t.month>=11:return t.year
    return None
def num(x):
    s=str(x).strip().replace(",","")
    if s.lower() in ("","nan","na","n/a","none","null","-",".","unknown"):return None
    try:v=float(s)
    except ValueError:return None
    return v if math.isfinite(v) and v>=0 else None
def mean(vals):
    return sum(vals)/len(vals)
def corr(rows,x,y):
    if len(rows)<4:return None
    xx=[r[x] for r in rows]; yy=[r[y] for r in rows]
    a=mean(xx);b=mean(yy)
    d=math.sqrt(sum((v-a)**2 for v in xx)*sum((v-b)**2 for v in yy))
    return sum((v-a)*(w-b) for v,w in zip(xx,yy))/d if d>1e-12 else None
def writecsv(path,rows):
    if not rows:raise ValueError("No output")
    with Path(path).open("w",newline="",encoding="utf-8") as f:
        writer=csv.DictWriter(f,fieldnames=rows[0].keys())
        writer.writeheader();writer.writerows(rows)
def run(folder,outdir):
    folder,outdir=Path(folder),Path(outdir)
    source={name:source_stomach_table(folder/(short+".zip"),fn,sha,n) for name,(short,fn,sha,n) in SOURCES.items()}
    counters={}
    samples=[]
    for sp,records in source.items():
        ctr=Counter()
        keycount=Counter((str(r["RECORD_ID"]).strip(),str(r["DATE"]).strip()) for r in records)
        ctr["raw_rows"]=len(records)
        ctr["duplicate_sample_key_rows"]=sum(n for n in keycount.values() if n>1)
        for r in records:
            d=timestamp(r["DATE"])
            if d is None:
                ctr["date_unparsed"]+=1;continue
            se=season(d)
            if se is None:
                ctr["outside_breeding_season"]+=1;continue
            if keycount[(str(r["RECORD_ID"]).strip(),str(r["DATE"]).strip())]>1:
                ctr["duplicate_sample_key_excluded"]+=1;continue
            fish,crust,total,krill=[num(r[col]) for col in
                ("FISH_MASS_g","CRUSTACEAN_MASS_g","TOTAL_MASS_g","EUPHAUSIA_SUPERBA_MASS_g")]
            if fish is None or crust is None:
                ctr["missing_fish_or_crust"]+=1;continue
            if total is None or total<=0:
                ctr["missing_or_zero_total"]+=1;continue
            if fish+crust<=0:
                ctr["zero_both_prey_groups"]+=1;continue
            if fish+crust>total*1.05+0.05:
                ctr["fish_plus_crust_over_total_excluded"]+=1;continue
            if krill is not None and krill>crust*1.05+0.05:
                ctr["krill_over_crust_excluded"]+=1;continue
            ctr["valid_fish_crust_sample"]+=1
            samples.append(dict(species=sp,season_start=se,date=d.isoformat(),
                source_sample_id=str(r["RECORD_ID"]).strip(),
                fish_mass_g=fish,crustacean_mass_g=crust,krill_mass_g=krill,
                source_total_mass_g=total,
                fish_within_fish_plus_crust=fish/(fish+crust),
                krill_within_fish_plus_crust=krill/(fish+crust) if krill is not None else None))
        counters[sp]=dict(ctr)
    if not samples:raise ValueError("No valid stomach samples; inspect date/units source")
    grouped=defaultdict(list)
    for s in samples:grouped[(s["species"],s["season_start"])].append(s)
    annual=[]
    for (sp,yr),r in sorted(grouped.items()):
        if not r:continue
        annual.append(dict(species=sp,season_start=yr,n_valid_stomachs=len(r),
            mean_stomach_fish_fraction=mean([x["fish_within_fish_plus_crust"] for x in r]),
            mean_stomach_krill_fraction=mean([x["krill_within_fish_plus_crust"] for x in r if x["krill_within_fish_plus_crust"] is not None]) if any(x["krill_within_fish_plus_crust"] is not None for x in r) else None,
            mean_fish_mass_g=mean([x["fish_mass_g"] for x in r]),
            mean_crustacean_mass_g=mean([x["crustacean_mass_g"] for x in r]),
            n_zero_explicit_fish=sum(x["fish_mass_g"]==0 for x in r)))
    qualified={ (r["species"],r["season_start"]):r for r in annual if r["n_valid_stomachs"]>=3}
    sic={}
    with ICE.open(newline="",encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["site_id"]!="GOPT" or r["inner_km"]!="0" or r["complete_month"]!="True":continue
            sic[(int(r["year"]),int(r["month"]))]=num(r["sic_mean"])
    if len(sic)!=120:raise ValueError("GOPT original nearshore sea-ice source incomplete")
    pairs=[]
    for a,b in (("Adelie","Chinstrap"),("Adelie","Gentoo"),("Chinstrap","Gentoo")):
        yrs=sorted(set(y for sp,y in qualified if sp==a)&set(y for sp,y in qualified if sp==b))
        for year in yrs:
            va,vb=qualified[(a,year)],qualified[(b,year)]
            sea=[sic.get((year,m)) for m in (8,9,10,11)]
            if any(v is None for v in sea):raise ValueError("GOPT pre-breeding SIC missing")
            pairs.append(dict(pair=a+"-"+b,breeding_season_start=year,
                sample_n_a=va["n_valid_stomachs"],sample_n_b=vb["n_valid_stomachs"],
                mean_fish_share_a=va["mean_stomach_fish_fraction"],
                mean_fish_share_b=vb["mean_stomach_fish_fraction"],
                fish_share_gap_b_minus_a=vb["mean_stomach_fish_fraction"]-va["mean_stomach_fish_fraction"],
                preceding_sep_sic_pct=sea[1],preceding_aug_nov_sic_pct=mean(sea)))
    if not pairs:
        # Keep the source quality audit if all pairs are unsupported.
        raise ValueError("No same-season two-species samples with >=3 stomachs per species")
    pairresult={}
    for label in sorted({p["pair"] for p in pairs}):
        rr=[p for p in pairs if p["pair"]==label]
        cor=corr(rr,"preceding_sep_sic_pct","fish_share_gap_b_minus_a")
        loo=[corr(rr[:i]+rr[i+1:],"preceding_sep_sic_pct","fish_share_gap_b_minus_a") for i in range(len(rr))] if len(rr)>=5 else []
        pairresult[label]=dict(n_paired_seasons=len(rr),
            earliest_season=min(r["breeding_season_start"] for r in rr),
            latest_season=max(r["breeding_season_start"] for r in rr),
            mean_gap_fish_share_b_minus_a=mean([r["fish_share_gap_b_minus_a"] for r in rr]),
            n_gap_positive=sum(r["fish_share_gap_b_minus_a"]>0 for r in rr),
            pearson_gap_vs_preceding_september_sic=cor,
            leave_one_season_out_correlations=loo)
    result=dict(date="2026-11-02",status="original_source_trophic_niche_exploratory_not_causal",
        original_summary_rows={sp:len(rs) for sp,rs in source.items()},
        original_summary_sha256={sp:v[2] for sp,v in SOURCES.items()},
        source_quality=counters,n_valid_stomach_records=len(samples),
        n_species_season_aggregates=len(annual),n_paired_species_season=len(pairs),
        seasonal_species_pairs=pairresult,
        estimand="stomach-level fish mass/(fish+crustacean mass), equal weight per nonduplicate stomach; not energy, not entire diet; missing never zero",
        temporal_join="calendar Jan-Apr stomach samples => austral breeding season begins preceding year; pre-feeding nearshore GOPT SIC Aug-Nov of season-start",
        non_claims=["no climate causal inference","no population forecast","no independent island replication",
                    "GOPT coastal sea ice is not direct foraging access","prey field missingness can bias taxon comparisons",
                    "species-seasons, not stomachs, are ecological comparison units"])
    outdir.mkdir(parents=True,exist_ok=True)
    writecsv(outdir/"diet_sample_level.csv",samples)
    writecsv(outdir/"diet_species_breeding_season.csv",annual)
    writecsv(outdir/"diet_pair_season_antecedent_sic.csv",pairs)
    (outdir/"summary.json").write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    return result
if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--source-dir",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    print(json.dumps(run(args.source_dir,args.out),ensure_ascii=False,indent=2))
