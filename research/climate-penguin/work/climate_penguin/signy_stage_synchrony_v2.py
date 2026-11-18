"""Source-backed Signy three-species fledgling-output *change* synchrony.

All three species are from one BAS/CEMP observational system. The two Adelie and
Chinstrap colony-set medians are not whole-island productivity; Gentoo's native
source is an aggregate. Fledglings are creche-stage counts, not recruits.
This is post-observation, not a new confirmatory mechanism or climate forecast.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import statistics
from pathlib import Path

SPECIES=("Adelie","Chinstrap","Gentoo")
PAIR_NAMES=(("Adelie","Chinstrap"),("Adelie","Gentoo"),("Chinstrap","Gentoo"))
SOURCE_PINS={
    "Adelie":"585f87928ed64d8982ef5bd86d8a785c38df65c39223d88ec17425854c786d62",
    "Chinstrap":"e50e98719ba5eedc6f5e617e0c7aa404ebfba15bc22a51e93e78cd4443bf787b",
    "Gentoo":"53fe3821f313ed35840376fcf4d11c8e0e8fbbd63f01ba84a5e21c2db4df6d6b"
}
EXPECTED_YEARS=(1996, *range(1998,2010), *range(2011,2020))
EXPECTED_TRANSITIONS=(*range(1999,2010), *range(2012,2020))


def read_csv(path):
    with Path(path).open(encoding="utf-8",newline="") as f:
        return list(csv.DictReader(f))


def number(v):
    try:
        value=float(v)
    except (ValueError,TypeError):
        return None
    return value if math.isfinite(value) else None


def correlation(x,y):
    if len(x)!=len(y) or len(x)<3:
        raise ValueError("insufficient support to correlate")
    ax=statistics.mean(x)
    ay=statistics.mean(y)
    v=sum((a-ax)*(b-ay) for a,b in zip(x,y))
    den=math.sqrt(sum((a-ax)**2 for a in x)*sum((b-ay)**2 for b in y))
    if den<1e-12:
        raise ValueError("zero centered variance")
    return v/den


def make_panel(annual,raw):
    eligible={}
    for row in annual:
        name=row["species"]
        year=int(row["season_start"])
        val=number(row["median_recorded_fledglings_per_pair"])
        if val is None:
            continue
        key=name,year
        if key in eligible:
            raise ValueError("duplicate annual species")
        eligible[key]=val
    years=sorted(set.intersection(*(
        {y for s,y in eligible if s==species} for species in SPECIES
    )))
    if tuple(years)!=EXPECTED_YEARS:
        raise ValueError("Signy shared original-year cohort changed")
    annual_by_year={y:{s:eligible[(s,y)] for s in SPECIES} for y in years}

    summation={}
    exclusion={}
    source_ids=set()
    for row in raw:
        s=row["species"]
        y=int(row["season_start"])
        if s not in SPECIES:
            raise ValueError("unknown penguin species")
        key=(s,y,row["colony"])
        if key in source_ids:
            raise ValueError("duplicate source colony per season")
        source_ids.add(key)
        value=number(row["recorded_fledglings_per_pair"])
        if value is None:
            continue
        pairs=number(row["pairs"])
        chicks=number(row["fledglings"])
        if pairs is None or pairs<=0 or chicks is None or chicks<0:
            raise ValueError("invalid native pair/fledgling record")
        if not math.isclose(value,chicks/pairs,abs_tol=1e-10):
            raise ValueError("native stage ratio calculation drift")
        if str(row["nest_before_fledglings"])!="True":
            raise ValueError("order of native pair and fledgling counts unresolved")
        if row["source_csv_sha256"]!=SOURCE_PINS[s]:
            raise ValueError("original BAS CSV source hash drift")
        rec=summation.setdefault((s,y),[0.0,0.0])
        rec[0]+=pairs
        rec[1]+=chicks
        if value<=2.0:
            exclusion.setdefault((s,y),[]).append(value)
    weighted={}
    bounded={}
    for y in years:
        weighted[y]={}
        bounded[y]={}
        for s in SPECIES:
            total=summation.get((s,y))
            if not total or total[0]<=0:
                raise ValueError("missing annual native stage numerator/denominator")
            weighted[y][s]=total[1]/total[0]
            keep=exclusion.get((s,y),[])
            if not keep:
                raise ValueError("no nonoutlier stage values")
            bounded[y][s]=statistics.median(keep)
    return annual_by_year,weighted,bounded,years,len(source_ids)


def differences(panel,years):
    delta=[]
    for prev,cur in zip(years[:-1],years[1:]):
        if cur-prev!=1:
            continue
        delta.append({"year":cur,**{
            s:panel[cur][s]-panel[prev][s] for s in SPECIES
        }})
    if tuple(row["year"] for row in delta)!=EXPECTED_TRANSITIONS:
        raise ValueError("complete-year transition support changed")
    return delta


def corr_set(delta):
    return {
        f"{a}|{b}":correlation([r[a] for r in delta],[r[b] for r in delta])
        for a,b in PAIR_NAMES
    }


def quantile(seq,p):
    vals=sorted(seq)
    pos=(len(vals)-1)*p
    a=int(math.floor(pos))
    b=int(math.ceil(pos))
    return vals[a]+(vals[b]-vals[a])*(pos-a)


def rotate_group(values,shift):
    if not values:
        return []
    shift%=len(values)
    return values[-shift:]+values[:-shift] if shift else list(values)


def grouped_rotate(rows,s,off0,off1):
    blocks=([r[s] for r in rows if 1999<=r["year"]<=2009],
            [r[s] for r in rows if 2012<=r["year"]<=2019])
    if tuple(map(len,blocks))!=(11,8):
        raise ValueError("consecutive-year transition blocks drifted")
    return rotate_group(blocks[0],off0)+rotate_group(blocks[1],off1)


def phase_diagnostic(delta,observed):
    """All 88x88 two-block offsets, preserving within-block temporal structure.

    A shifts zero; C and G each shift their 11-year and 8-year blocks
    independently. This is *not* a valid climate-causal p-value.
    """
    a=grouped_rotate(delta,"Adelie",0,0)
    c=grouped_rotate(delta,"Chinstrap",0,0)
    g=grouped_rotate(delta,"Gentoo",0,0)
    observed_stat=statistics.mean(observed.values())
    offsets=[(i,j) for i in range(11) for j in range(8)]
    shifted_c=[grouped_rotate(delta,"Chinstrap",*off) for off in offsets]
    shifted_g=[grouped_rotate(delta,"Gentoo",*off) for off in offsets]
    # Compute exactly, including zero offsets; no Monte Carlo seed.
    ac=[correlation(a,v) for v in shifted_c]
    ag=[correlation(a,v) for v in shifted_g]
    values=[]
    pair_cg=[]
    for i,vc in enumerate(shifted_c):
        for j,vg in enumerate(shifted_g):
            r_cg=correlation(vc,vg)
            pair_cg.append(r_cg)
            values.append((ac[i]+ag[j]+r_cg)/3)
    if len(values)!=7744:
        raise ValueError("phase group size mismatch")
    cg_observed=observed["Chinstrap|Gentoo"]
    # Each relative phase appears 88 times in the 7744 group
    return {
        "observed_mean_pair_r":observed_stat,
        "comparison_count":len(values),
        "null_quantile_025":quantile(values,0.025),
        "null_median":quantile(values,0.50),
        "null_quantile_975":quantile(values,0.975),
        "upper_fraction_including_identity":sum(v>=observed_stat-1e-12 for v in values)/len(values),
        "pair_positive_tails":{
            "Adelie|Chinstrap":sum(v>=observed["Adelie|Chinstrap"]-1e-12 for v in ac)/len(ac),
            "Adelie|Gentoo":sum(v>=observed["Adelie|Gentoo"]-1e-12 for v in ag)/len(ag),
            "Chinstrap|Gentoo":sum(v>=cg_observed-1e-12 for v in pair_cg)/len(pair_cg)
        },
        "interpretation":"post-exposure exact two-block circular-phase diagnostic; not a calibrated ecological null"
    }


def analyze(annual,raw):
    raw_panel,weighted,bounded,years,unique_count=make_panel(annual,raw)
    diffs=differences(raw_panel,years)
    pair_corr=corr_set(diffs)
    weights=corr_set(differences(weighted,years))
    bounded_corr=corr_set(differences(bounded,years))
    no_shocks=[r for r in diffs if r["year"] not in (2012,2013,2015,2016)]
    no_shock_corr=corr_set(no_shocks)
    deletion={}
    within_blocks={}
    for pair in pair_corr:
        a,b=pair.split("|")
        leave=[correlation([z[a] for z in diffs if z["year"]!=x["year"]],
                           [z[b] for z in diffs if z["year"]!=x["year"]]) for x in diffs]
        deletion[pair]={"min":min(leave),"max":max(leave)}
        within_blocks[pair]={}
        for label,lo,hi in (("1999-2009",1999,2009),("2012-2019",2012,2019)):
            sub=[z for z in diffs if lo<=z["year"]<=hi]
            within_blocks[pair][label]=correlation([z[a] for z in sub],[z[b] for z in sub])
    count_sign_equal=sum(
        (r["Adelie"]>0)==(r["Chinstrap"]>0)==(r["Gentoo"]>0)
        for r in diffs if all(r[s]!=0 for s in SPECIES)
    )
    ordered_source_valid=sum(r.get("recorded_fledglings_per_pair") not in ("","None") and
                             r.get("nest_before_fledglings")=="True" for r in raw)
    return {
        "status":"POST_EXPOSURE_OBSERVATIONAL_SYNCHRONY_NOT_NEW_CAUSAL_DISCOVERY",
        "common_years":years,
        "source_rows":len(raw),
        "distinct_source_site_year_keys":unique_count,
        "strict_ordered_fledgling_pair_rows":ordered_source_valid,
        "consecutive_year_transitions":[z["year"] for z in diffs],
        "n_consecutive_transitions":len(diffs),
        "all_species_same_direction_year_changes":count_sign_equal,
        "source_median_pair_correlations":pair_corr,
        "source_weighted_pair_correlations":weights,
        "ratio_le_2_pair_correlations":bounded_corr,
        "shock_years_removed_pair_correlations":no_shock_corr,
        "leave_one_transition_pair_range":deletion,
        "within_block_pair_correlations":within_blocks,
        "phase_group_diagnostic":phase_diagnostic(diffs,pair_corr),
        "yearly_differences":diffs,
        "limits":[
            "The same BAS/CEMP data underlie Dunn et al. (2016), which already reports Chinstrap-Gentoo breeding success association r=0.73.",
            "Fledglings are reported pre-departure creche-stage counts, not adult recruits; ratios can exceed two and source group boundaries vary.",
            "Adelie/Chinstrap colony medians and Gentoo island aggregate are different spatial grains, so high correlations cannot isolate trophic responses.",
            "Single-island shared-year synchrony is not independent ocean-climate replication or a measured food/salinity effect.",
            "This does not quantify future nesting pairs, recolonization, N_eff, or vegetation response."
        ]
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--derived-dir",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    p.add_argument("--check-known",action="store_true")
    arg=p.parse_args()
    annual_path=arg.derived_dir/"species_annual_stage_summary.csv"
    raw_path=arg.derived_dir/"source_stage_site_seasons.csv"
    results=analyze(read_csv(annual_path),read_csv(raw_path))
    if arg.check_known:
        known={"Adelie|Chinstrap":0.794364142838016,
               "Adelie|Gentoo":0.702585668658692,
               "Chinstrap|Gentoo":0.7382168266825719}
        if results["n_consecutive_transitions"]!=19 or len(results["common_years"])!=22:
            raise ValueError("source support receipt changed")
        for key,v in known.items():
            if not math.isclose(results["source_median_pair_correlations"][key],v,abs_tol=1e-10):
                raise ValueError("source correlation re-check failed for "+key)
    arg.out.mkdir(parents=True,exist_ok=True)
    year_diffs=results.pop("yearly_differences")
    with (arg.out/"first_differences.csv").open("w",newline="",encoding="utf-8") as f:
        writer=csv.DictWriter(f,fieldnames=["year",*SPECIES])
        writer.writeheader()
        writer.writerows(year_diffs)
    results["source_derived_csv_sha256"]={
        "annual":hashlib.sha256(annual_path.read_bytes()).hexdigest(),
        "colonies":hashlib.sha256(raw_path.read_bytes()).hexdigest()
    }
    (arg.out/"result.json").write_text(json.dumps(results,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({
        "years":len(results["common_years"]),
        "transitions":results["n_consecutive_transitions"],
        "correlations":results["source_median_pair_correlations"],
        "weighted":results["source_weighted_pair_correlations"],
        "shock_years_removed":results["shock_years_removed_pair_correlations"],
        "phase_diagnostic":results["phase_group_diagnostic"],
        "checked":arg.check_known
    },ensure_ascii=False))


if __name__=="__main__":
    main()
