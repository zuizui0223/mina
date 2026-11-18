"""Exploratory Signy 3-species stomach fish-share gap vs sea ice, 2001-2009.

All source stomachs are verified by signy_diet_climate_v1. Year is the
ecological replicate (1 island, 9 seasons), NOT the 772 stomachs. The
two-window exact permutation assumes exchangeable years, and does not correct
the full exploratory search. No climate-to-fitness or CMIP6 biological claim.
"""
from __future__ import annotations
import argparse,csv,datetime,hashlib,itertools,json,math,random
from collections import defaultdict
from pathlib import Path

SPECIES=("Adelie","Chinstrap","Gentoo")
YEARS=tuple(range(2001,2010))
RAW_SHA={"Adelie":"ab05193e94864ca05ea54a01154506f8e86f85291e2f01a68abab5d92229a04d",
"Chinstrap":"a8dc89e0440cc8826925fc65bf9194de5151162b83c7d42db7ba3c97d49b164a",
"Gentoo":"6f2a5fa1fc136ad6102dee8cd1c429d24c8ab81b50077bd21eb03f4e80fbd902"}

def readcsv(p):
    with Path(p).open(newline="",encoding="utf-8") as f:return list(csv.DictReader(f))
def avg(v):
    if not v:raise ValueError("Empty mean")
    return sum(v)/len(v)
def corr(x,y):
    if len(x)!=len(y) or len(x)<3:raise ValueError("Insufficient aligned years")
    a=[v-avg(x) for v in x]; b=[v-avg(y) for v in y]
    den=math.sqrt(sum(v*v for v in a)*sum(v*v for v in b))
    return sum(s*t for s,t in zip(a,b))/den if den>1e-12 else None
def med(v):
    a=sorted(v); n=len(a);return a[n//2] if n%2 else (a[n//2-1]+a[n//2])/2
def qtile(v,p):
    a=sorted(v); f=(len(a)-1)*p;i=int(f);t=f-i
    return a[i]*(1-t)+a[min(i+1,len(a)-1)]*t
def detrend(v):
    t=list(range(len(v)));mt=avg(t);mv=avg(v)
    slope=sum((x-mt)*(y-mv) for x,y in zip(t,v))/sum((x-mt)**2 for x in t)
    return [y-(mv+slope*(i-mt)) for i,y in enumerate(v)]
def daymatch(src,anchors,days):
    a=[datetime.date.fromisoformat(x["date"]) for x in anchors]
    if not a:return []
    return [r for r in src if min(abs((datetime.date.fromisoformat(r["date"])-x).days) for x in a)<=days]
def exact2(x,w,y):
    """Two-sided 9! exact test, plus max-|r| test across two ice windows."""
    if len(y)!=9:raise ValueError("Nine source seasons required")
    def cent(v):
        m=avg(v);a=[x-m for x in v]; d=math.sqrt(sum(x*x for x in a))
        if d<=1e-12:raise ValueError("Flat input")
        return a,d
    a,ad=cent(x);b,bd=cent(w);c,cd=cent(y)
    r1=sum(u*v for u,v in zip(a,c))/(ad*cd)
    r2=sum(u*v for u,v in zip(b,c))/(bd*cd)
    counts=[0,0,0];total=0
    for p in itertools.permutations(c):
        total+=1
        z=abs(sum(u*v for u,v in zip(a,p))/(ad*cd))
        v=abs(sum(u*t for u,t in zip(b,p))/(bd*cd))
        counts[0]+=z+1e-12>=abs(r1)
        counts[1]+=v+1e-12>=abs(r2)
        counts[2]+=max(z,v)+1e-12>=max(abs(r1),abs(r2))
    assert total==math.factorial(len(y))
    return dict(n_permutations=total,sep_r=r1,aug_nov_r=r2,
        sep_extreme=counts[0],aug_nov_extreme=counts[1],max_two_extreme=counts[2],
        sep_p=counts[0]/total,aug_nov_p=counts[1]/total,
        max_two_window_p=counts[2]/total,
        assumption="exchangeable years; not a confirmatory or comprehensive multiple-test correction")
def writecsv(p,rows):
    if not rows:raise ValueError("No output rows")
    with Path(p).open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def run(indir,outdir,bootstrap=3000):
    indir,outdir=Path(indir),Path(outdir)
    files=["diet_sample_level.csv","diet_species_breeding_season.csv","diet_pair_season_antecedent_sic.csv","summary.json"]
    paths={x:indir/x for x in files}
    sample=readcsv(paths[files[0]]);annual=readcsv(paths[files[1]]);pairs=readcsv(paths[files[2]])
    source=json.loads(paths[files[3]].read_text(encoding="utf-8"))
    if (len(sample),len(annual),len(pairs))!=(1364,47,37) or source["original_summary_sha256"]!=RAW_SHA:
        raise ValueError("Original BAS source quantities/SHA differ")
    stomachs=defaultdict(list)
    for r in sample:stomachs[r["species"],int(r["season_start"])].append(r)
    original_annual={(r["species"],int(r["season_start"])):r for r in annual}
    icepairs={(r["pair"],int(r["breeding_season_start"])):r for r in pairs}
    years=[];data={}
    for year in YEARS:
        if any((sp,year) not in stomachs or (sp,year) not in original_annual for sp in SPECIES):
            raise ValueError("Three species/year missing")
        means={};weighted={};middles={};ns={}
        for sp in SPECIES:
            ss=stomachs[sp,year]; values=[float(r["fish_within_fish_plus_crust"]) for r in ss]
            fish=sum(float(r["fish_mass_g"]) for r in ss)
            crust=sum(float(r["crustacean_mass_g"]) for r in ss)
            means[sp]=avg(values);weighted[sp]=fish/(fish+crust);middles[sp]=med(values);ns[sp]=len(ss)
            if abs(means[sp]-float(original_annual[sp,year]["mean_stomach_fish_fraction"]))>1e-10:
                raise ValueError("Original stomach mean discrepancy")
            data[sp,year]=values
        for name in ("Adelie-Gentoo","Chinstrap-Gentoo","Adelie-Chinstrap"):
            if (name,year) not in icepairs:raise ValueError("Pair-year lacking")
        original=icepairs["Adelie-Gentoo",year]
        sep=float(original["preceding_sep_sic_pct"])
        aug=float(original["preceding_aug_nov_sic_pct"])
        if any(abs(sep-float(icepairs[p,year]["preceding_sep_sic_pct"]))>1e-8
               for p in ("Chinstrap-Gentoo","Adelie-Chinstrap")):
            raise ValueError("Sea ice differs within island-year")
        gent=stomachs["Gentoo",year]; adel=stomachs["Adelie",year];chin=stomachs["Chinstrap",year]
        a7=daymatch(adel,gent,7);a10=daymatch(adel,gent,10);c7=daymatch(chin,gent,7)
        years.append(dict(year=year,sep_sic_pct=sep,aug_nov_sic_pct=aug,
          adelie_n=ns["Adelie"],chinstrap_n=ns["Chinstrap"],gentoo_n=ns["Gentoo"],
          adelie_fish=means["Adelie"],chinstrap_fish=means["Chinstrap"],gentoo_fish=means["Gentoo"],
          marine_gap=means["Gentoo"]-(means["Adelie"]+means["Chinstrap"])/2,
          gap_mass_weighted=weighted["Gentoo"]-(weighted["Adelie"]+weighted["Chinstrap"])/2,
          gap_median=middles["Gentoo"]-(middles["Adelie"]+middles["Chinstrap"])/2,
          adelie_n_7day=len(a7),chinstrap_n_7day=len(c7),
          adelie_n_10day=len(a10),
          gap_gentoo_adelie_7day=means["Gentoo"]-avg([float(r["fish_within_fish_plus_crust"]) for r in a7]) if len(a7)>=3 else None,
          gap_gentoo_adelie_10day=means["Gentoo"]-avg([float(r["fish_within_fish_plus_crust"]) for r in a10]) if len(a10)>=3 else None))
    if sum(r["gentoo_n"] for r in years)!=73:raise ValueError("Gentoo sample years changed")
    x=[r["sep_sic_pct"] for r in years];w=[r["aug_nov_sic_pct"] for r in years]
    y=[r["marine_gap"] for r in years]
    exact=exact2(x,w,y)
    def description(xx,key):
        z=[r[key] for r in years]
        loo=[corr(xx[:i]+xx[i+1:],y[:i]+y[i+1:]) for i in range(9)]
        n=len(y);circular=[corr(xx,y[-i:]+y[:-i]) if i else corr(xx,y) for i in range(n)]
        return dict(pearson_r=corr(xx,y),mass_weighted_r=corr(xx,[r["gap_mass_weighted"] for r in years]),
            median_based_r=corr(xx,[r["gap_median"] for r in years]),
            year_detrended_r=corr(detrend(xx),detrend(y)),
            first_diff_r=corr([xx[i]-xx[i-1] for i in range(1,9)],
                              [y[i]-y[i-1] for i in range(1,9)]),
            leave_one_season_r_range=[min(loo),max(loo)],
            nine_circular_shift_extreme_fraction=sum(abs(v)+1e-12>=abs(circular[0]) for v in circular)/9,
            slope_fish_fraction_gap_per_10pp_sic=10*sum((v-avg(xx))*(t-avg(y)) for v,t in zip(xx,y))/sum((v-avg(xx))**2 for v in xx))
    sensitivity={}
    for gap in (7,10):
        yy=[r for r in years if r["adelie_n_"+str(gap)+"day"]>=3]
        sensitivity[str(gap)+"day_adelie_gentoo"]=dict(years=[r["year"] for r in yy],
          n_years=len(yy),r_september=corr([r["sep_sic_pct"] for r in yy],[r["gap_gentoo_adelie_"+str(gap)+"day"] for r in yy]),
          r_aug_nov=corr([r["aug_nov_sic_pct"] for r in yy],[r["gap_gentoo_adelie_"+str(gap)+"day"] for r in yy]))
    sensitivity["chinstrap_gentoo_years_7day_3stomachs"]=sum(r["chinstrap_n_7day"]>=3 for r in years)
    rng=random.Random(20261102);bb=[]
    for _ in range(bootstrap):
        gaps=[]
        for yr in YEARS:
            f={sp:avg(rng.choices(data[sp,yr],k=len(data[sp,yr]))) for sp in SPECIES}
            gaps.append(f["Gentoo"]-(f["Adelie"]+f["Chinstrap"])/2)
        bb.append((corr(x,gaps),corr(w,gaps),avg(gaps)))
    output=dict(date="2026-11-02",status="exploratory_original_BAS_3species_diet_gap_not_climate_causal",
      n_years=len(years),n_source_stomachs_all_years=len(sample),
      n_stomachs_in_all_three_species_years={sp:sum(len(data[sp,yr]) for yr in YEARS) for sp in SPECIES},
      mean_fish_fractions={sp:avg([r[sp.lower()+"_fish"] for r in years]) for sp in SPECIES},
      mean_fish_gap=avg(y),positive_fish_gap_years=sum(t>0 for t in y),
      correlation={"september":description(x,"marine_gap"),"aug_nov":description(w,"marine_gap")},
      exact_two_window_permutation=exact,date_matched=sensitivity,
      stomach_conditional_bootstrap=dict(seed=20261102,n=bootstrap,
        sep_r_95pct=[qtile([v[0] for v in bb],.025),qtile([v[0] for v in bb],.975)],
        aug_nov_r_95pct=[qtile([v[1] for v in bb],.025),qtile([v[1] for v in bb],.975)],
        mean_gap_95pct=[qtile([v[2] for v in bb],.025),qtile([v[2] for v in bb],.975)],
        not_year_cluster_inference=True),
      source_sha256={f:hashlib.sha256(p.read_bytes()).hexdigest() for f,p in paths.items()},
      no_future_diet_or_breeding_forecast=True,
      limitations=["one island, nine seasons, posthoc chosen composite and predictor windows",
          "earlier 2001-2009 diets and historical sea ice cannot identify 2050 response",
          "permutation assumes exchangeable seasons; circular shift has only nine positions",
          "different within-season sample dates, especially for chinstrap",
          "fish share limited to fish/(fish+crustacean), not foraging success or energy",
          "Gentoo seasons include 6-10 stomachs; non-independent stomach subsamples"])
    if (exact["sep_extreme"],exact["aug_nov_extreme"],exact["max_two_extreme"])!=(15105,4839,7944):
        raise ValueError("Independent exact-permutation receipt changed")
    if output["n_stomachs_in_all_three_species_years"]!={"Adelie":349,"Chinstrap":350,"Gentoo":73}:
        raise ValueError("Matched triple-year source count changed")
    outdir.mkdir(parents=True,exist_ok=True);writecsv(outdir/"nine_year_fish_gap.csv",years)
    (outdir/"summary.json").write_text(json.dumps(output,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return output

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--derived",type=Path,required=True);p.add_argument("--out",type=Path,required=True)
    p.add_argument("--bootstrap",type=int,default=3000)
    args=p.parse_args()
    d=run(args.derived,args.out,args.bootstrap)
    print(json.dumps({"n_years":d["n_years"],"permutation":d["exact_two_window_permutation"],
                     "date_matched":d["date_matched"]},ensure_ascii=False,indent=2))
