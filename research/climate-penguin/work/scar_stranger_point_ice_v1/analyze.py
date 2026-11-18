"""Independent Stranger Point Adelie food-mass vs antecedent nearshore SIC.

Exploratory second marine site, distinct from the three-species Signy diet
study. Published fish mass is extremely low. Uses fixed original SCAR source
398 and three geographic proxies; no response calibration or future forecast.
"""
from __future__ import annotations
import argparse,csv,json,math,datetime,tempfile,importlib.util,itertools
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
GRAIN=ROOT/"work/scar_external_diet_grain_v2/inspect.py"
sp=importlib.util.spec_from_file_location("scar_grain",GRAIN)
mod=importlib.util.module_from_spec(sp);sp.loader.exec_module(mod)
LOC=ROOT/"outputs/climate_penguin/daily_ice_locations.csv"
ICE=ROOT/"outputs/climate_penguin/macro_monthly_seaice_1991_2020.csv"
COORD=(-62.26667,-58.61667)  # SCAR Composite Gazetteer Stranger Point (approximate)
PROXIES=("LLAN","PTHO","ARDL")

def read(path):
    with Path(path).open(newline="",encoding="utf-8") as f:return list(csv.DictReader(f))
def mean(a):return sum(a)/len(a)
def pearson(a,b):
    if len(a)!=len(b) or len(a)<3:return None
    ma=mean(a);mb=mean(b);xx=[x-ma for x in a];yy=[y-mb for y in b]
    d=math.sqrt(sum(x*x for x in xx)*sum(y*y for y in yy))
    return sum(x*y for x,y in zip(xx,yy))/d if d>1e-12 else None
def rank(a):
    ordered=sorted(range(len(a)),key=lambda i:a[i])
    ranks=[0.0]*len(a)
    i=0
    while i<len(a):
        j=i+1
        while j<len(a) and a[ordered[j]]==a[ordered[i]]:j+=1
        for k in range(i,j):ranks[ordered[k]]=(i+j+1)/2
        i=j
    return ranks
def summary_corr(a,b):
    r=pearson(a,b)
    sp=pearson(rank(a),rank(b))
    if len(a)<5:return dict(n=len(a),pearson=r,spearman=sp)
    lo=[pearson(a[:i]+a[i+1:],b[:i]+b[i+1:]) for i in range(len(a))]
    lo=[v for v in lo if v is not None]
    shifts=[pearson(a,b[t:]+b[:t]) for t in range(len(a))]
    if r is None or not lo:return dict(n=len(a),pearson=r,spearman=sp,
        leave_one_season_pearson_min=None,leave_one_season_pearson_max=None,
        circular_shifts_extreme_count=None,n_circular_shifts=len(shifts),
        circular_shift_only_exploratory=True)
    return dict(n=len(a),pearson=r,spearman=sp,
        leave_one_season_pearson_min=min(lo),leave_one_season_pearson_max=max(lo),
        circular_shifts_extreme_count=sum(abs(v)+1e-12>=abs(r) for v in shifts if v is not None),
        n_circular_shifts=len(shifts),
        circular_shift_only_exploratory=True)
def recorded_above_rounding_gap(ice,fish):
    """Exact 6-vs-6 label permutation of recorded >0 vs rounded 0 annual fractions.

    These recorded zero fractions do not establish that fish were biologically absent.
    The year-exchangeability assumption is unverified; exploratory only.
    """
    mark=[v>0 for v in fish]
    n_pos=sum(mark)
    if not (0<n_pos<len(mark)):return None
    obs=mean([x for x,yes in zip(ice,mark) if yes])-mean([x for x,yes in zip(ice,mark) if not yes])
    vals=0;extreme=0
    for choice in itertools.combinations(range(len(mark)),n_pos):
        mask=set(choice)
        delta=mean([x for i,x in enumerate(ice) if i in mask])-mean([x for i,x in enumerate(ice) if i not in mask])
        vals+=1
        extreme+=abs(delta)+1e-12>=abs(obs)
    return dict(n=len(mark),n_recorded_positive=n_pos,n_recorded_zero=len(mark)-n_pos,
        mean_ice_difference_positive_minus_zero_pp=obs,
        exact_year_label_permutations=vals,extreme_assignments=extreme,
        nominal_two_sided_fraction=extreme/vals,rounded_zero_is_not_true_absence=True,
        no_exchangeability_or_confirmatory_p_claim=True)

def write(path,rows):
    with Path(path).open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def run(original,output):
    with tempfile.TemporaryDirectory() as temp:
        support=mod.run(Path(original),Path(temp))
        allrows=read(Path(temp)/"prey_mass_per_source_sample.csv")
    if support["sources"]["398"]["n_fish_and_crust_mass"]!=12:raise ValueError("Stranger Point source support changed")
    sp=[r for r in allrows if r["source_id"]=="398"]
    if len(sp)!=12:raise ValueError("12 original annual diet records required")
    diet=[]
    for r in sp:
        year=int(r["breeding_season_start"])
        fish=float(r["fish_fraction_of_all_prey"])
        krill=float(r["crust_fraction_of_all_prey"])
        if not (0<=fish<=0.0015 and .997<=krill<=1.):
            raise ValueError("Published fish/krill fraction bounds breached")
        if int(r["n_trace_sentinel_rows"])!=0 or int(r["n_aggregate_prey_rows"])!=0:
            raise ValueError("Source 398 has trace/aggregate hierarchy")
        diet.append(dict(season_start=year,original_calendar_year=int(r["original_calendar_year"]),
            site="Stranger Point",predator_species="Adelie",
            n_original_prey_rows=int(r["n_rows"]),source_id=398,
            fish_wet_mass_fraction_original=fish,krill_wet_mass_fraction_original=krill,
            fish_of_fish_plus_krill=fish/(fish+krill),
            source_sample_id=r["sample_id"],
            source_single_published_annual_aggregate=True))
    diet.sort(key=lambda r:r["season_start"])
    if [r["season_start"] for r in diet]!=[2002,2003,2004,2005,2007,2008,2009,2010,2011,2012,2013,2014]:
        raise ValueError("Original breeding-season annual list changed")
    locs=[r for r in read(LOC) if r["cohort"]=="macro_40" and r["site_id"] in PROXIES]
    if len(locs)!=3:raise ValueError("Missing climate proxy")
    km={r["site_id"]:mod.s.haversine(COORD,(float(r["latitude"]),float(r["longitude"]))) if hasattr(mod.s,"haversine") else
     2*6371*math.asin(math.sqrt(math.sin(math.radians((float(r["latitude"])-COORD[0])/2))**2+
     math.cos(math.radians(COORD[0]))*math.cos(math.radians(float(r["latitude"])))*
     math.sin(math.radians((float(r["longitude"])-COORD[1])/2))**2))
     for r in locs}
    if any(km[k]>25 for k in PROXIES):raise ValueError("Proxy >25km away")
    rows=read(ICE)
    index={(r["site_id"],int(r["year"]),int(r["month"])):float(r["sic_mean"])
        for r in rows if r["inner_km"]=="0" and r["complete_month"]=="True"}
    outrows=[];stats={}
    for source in PROXIES:
        part=[]
        for d in diet:
            y=d["season_start"]
            month={m:index[(source,y,m)] for m in (8,9,10,11)}
            part.append(dict(site=d["site"],season_start=y,source_id=398,
                n_published_annual_aggregate_records=1,
                fish_fraction=d["fish_of_fish_plus_krill"],
                krill_fraction=d["krill_wet_mass_fraction_original"],
                proxy_site_id=source,proxy_distance_km=km[source],
                prior_september_sic_pct=month[9],
                prior_aug_nov_sic_pct=mean(list(month.values())),
                original_calendar_year=d["original_calendar_year"]))
        for cov in ("prior_september_sic_pct","prior_aug_nov_sic_pct"):
            x=[r[cov] for r in part];y=[r["fish_fraction"] for r in part]
            adjacent=[(a,b) for a,b in zip(part[:-1],part[1:]) if b["season_start"]==a["season_start"]+1]
            a=[b[cov]-a[cov] for a,b in adjacent];b=[q["fish_fraction"]-p["fish_fraction"] for p,q in adjacent]
            stats[source+"_"+cov]=dict(**summary_corr(x,y),
                contiguous_year_intervals=len(adjacent),
                first_difference_pearson=pearson(a,b))
        outrows+=part
    cape=[r for r in allrows if r["source_id"]=="22"]
    cape_result=[]
    for d in cape:
        val=d["fish_within_fish_plus_crust"]
        cape_result.append(dict(breeding_season_start=int(d["breeding_season_start"]),
           location="Cape Shirreff",species=d["species"],
           fish_fraction_of_fish_plus_krill=(float(val) if val not in ("",None) else None),
           fish_fraction_original_if_resolved=(float(d["fish_fraction_of_all_prey"]) if d["fish_fraction_of_all_prey"] not in ("",None) else None),
           trace_sentinel_rows=int(d["n_trace_sentinel_rows"]),
           source_sample_count_from_paper=int(d["n_rows"]),
           source_id=22,assessed_metric="literature-aggregated prey mass fraction, NOT stomach mean"))
    cape_result.sort(key=lambda x:(x["breeding_season_start"],x["species"]))
    if len(cape_result)!=4:raise ValueError("2x2 external species-year support changed")
    if any(x["fish_fraction_of_fish_plus_krill"] is not None for x in cape_result if x["species"]=="Chinstrap" and x["breeding_season_start"]==2008):
        raise ValueError("Trace fish mistakenly promoted to numeric zero")
    outcome=dict(date="2026-11-02",status="independent_one_species_12year_food_ice_descriptive_no_causality",
       source_398_n_years=len(diet),n_site_ice_proxy_combinations=len(outrows),
       original_site="Stranger Point",study_source="Juáres et al 2018, Polar Biology, source_id 398",
       diet_measured_stage="January crèche, previous-year austral breeding season",
       independent_breeding_seasons=12,real_independent_marine_climate_locations=1,
       n_fish_fraction_exact_zero=sum(r["fish_wet_mass_fraction_original"]==0 for r in diet),
       max_fish_fraction_original=max(r["fish_wet_mass_fraction_original"] for r in diet),
       n_proxy_locations=3,nearby_reference_distance_km=km,
       source_22_cape_shirreff={"n_pair_seasons":2,"n_source_groups":len(cape),
          "valid_both_species_numeric_fish_and_crust_pair_seasons":
            sum(all(any(x["breeding_season_start"]==yr and x["species"]==sp and
                    x["fish_fraction_of_fish_plus_krill"] is not None for x in cape_result)
                for sp in ("Chinstrap","Gentoo")) for yr in (2007,2008)),
          "trace_season_not_zero":"Chinstrap, breeding season 2008"},
       correlations_by_proxy_window=stats,
       zero_versus_positive_year_sensitivity={ref:recorded_above_rounding_gap(
           [r["prior_september_sic_pct"] for r in outrows if r["proxy_site_id"]==ref],
           [r["fish_fraction"] for r in outrows if r["proxy_site_id"]==ref]) for ref in PROXIES},
       n_distinct_not_independent_marine_proxy_time_series=2,
       source_git_blob=mod.s.BLOB,
       flags=["single Adélie species; cannot reproduce multi-species niche gap",
         "all year values are published source-level fraction aggregates, NOT independent bird stomachs",
         "coastal SIC 0-100km regional proxies and sampled stomach habitat may differ",
         "fish is approximately zero; correlation is extremely sensitive to trace/rounding",
         "three nearby proxies are dependent, not three independent climate sites",
         "multiple exploratory comparisons; no formal evidence of a climate effect",
         "no future diet, nests, or multispecies competition prediction"])
    output=Path(output);output.mkdir(parents=True,exist_ok=True)
    write(output/"stranger_point_12_seasons_food_and_ice.csv",outrows)
    write(output/"cape_shirreff_external_two_species_years.csv",cape_result)
    (output/"summary.json").write_text(json.dumps(outcome,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps({k:outcome[k] for k in
        ("source_398_n_years","n_fish_fraction_exact_zero","max_fish_fraction_original","source_22_cape_shirreff","correlations_by_proxy_window")},ensure_ascii=False,indent=2))
    return outcome
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--diet",type=Path,required=True);p.add_argument("--out",type=Path,required=True)
    v=p.parse_args();run(v.diet,v.out)
