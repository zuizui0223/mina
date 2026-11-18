"""Posthoc Signy per-species trophic response and four-year rolling origin.

Uses original BAS SHA-checked stomach samples via existing niche v2 workflow.
Single island, 9 seasons, only 4 heldout chronological test seasons; do not
extrapolate fitted biological coefficients to CMIP6.
"""
import argparse,csv,hashlib,json,math
from pathlib import Path
YEARS=list(range(2001,2010))
SPECIES=("adelie","chinstrap","gentoo")
RESPONSES=("adelie_fish","chinstrap_fish","gentoo_fish","marine_gap")
WINDOWS=("aug_nov_sic_pct","sep_sic_pct")
def mean(x):return sum(x)/len(x)
def fit(x,y):
    xm=mean(x);ym=mean(y);den=sum((v-xm)**2 for v in x)
    if den<=1e-12:raise ValueError("No historical ice variation")
    beta=sum((v-xm)*(u-ym) for v,u in zip(x,y))/den
    return beta,ym-beta*xm
def cov(x,y):return mean([(a-mean(x))*(b-mean(y)) for a,b in zip(x,y)])
def pearson(x,y):
    den=math.sqrt(cov(x,x)*cov(y,y))
    return cov(x,y)/den if den>1e-12 else None
def save(path,items):
    with path.open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(items[0]))
        w.writeheader();w.writerows(items)
def run(p,out):
    p=Path(p)
    with p.open(encoding="utf-8",newline="") as f:rr=list(csv.DictReader(f))
    if len(rr)!=9 or [int(r["year"]) for r in rr]!=YEARS:raise ValueError("Expected 2001-2009 original season panel")
    needed=set(RESPONSES+WINDOWS+tuple(s+"_n" for s in SPECIES))
    rows=[{k:float(r[k]) for k in needed} for r in rr]
    counts={sp:int(sum(r[sp+"_n"] for r in rows)) for sp in SPECIES}
    if counts!={"adelie":349,"chinstrap":350,"gentoo":73}:raise ValueError("Raw verified stomach sample counts drift")
    for r in rows:
        if not all(0<=r[sp+"_fish"]<=1 for sp in SPECIES):raise ValueError("Invalid fish fraction")
        if abs(r["marine_gap"]-(r["gentoo_fish"]-.5*(r["adelie_fish"]+r["chinstrap_fish"])))>1e-10:
            raise ValueError("Original source triple-species fish gap does not reconcile")
    predictions=[];metrics=[];contributions={}
    for window in WINDOWS:
        x=[r[window] for r in rows]
        contrib={sp:cov(x,[r[sp+"_fish"] for r in rows]) for sp in SPECIES}
        contributions[window]=dict(**contrib,
          gap=cov(x,[r["marine_gap"] for r in rows]),
          gentoo_absolute_fraction_of_covariance=abs(contrib["gentoo"])/(abs(contrib["gentoo"])+.5*abs(contrib["adelie"])+.5*abs(contrib["chinstrap"])))
        if abs(contributions[window]["gap"]-(contrib["gentoo"]-.5*(contrib["adelie"]+contrib["chinstrap"])))>1e-12:
            raise ValueError("Covariance decomposition failed")
        for sp in RESPONSES:
            y=[r[sp] for r in rows]
            for test_index in range(5,9):
                slope,intercept=fit(x[:test_index],y[:test_index])
                pred=slope*x[test_index]+intercept; baseline=mean(y[:test_index])
                predictions.append(dict(window=window,response=sp,year=YEARS[test_index],training_seasons=test_index,
                   observed=y[test_index],prior_ice_pct=x[test_index],ice_linear_prediction=pred,
                   historical_mean_prediction=baseline,ice_absolute_error=abs(y[test_index]-pred),
                   historical_mean_absolute_error=abs(y[test_index]-baseline),
                   out_of_0_1_range=(not 0<=pred<=1) if sp!="marine_gap" else False))
            ff=[z for z in predictions if z["window"]==window and z["response"]==sp]
            ice_mae=mean([z["ice_absolute_error"] for z in ff])
            baseline_mae=mean([z["historical_mean_absolute_error"] for z in ff])
            metrics.append(dict(window=window,response=sp,n_training_start=5,n_heldout=4,
                heldout_seasons="2006;2007;2008;2009",original_n_seasons=9,
                in_sample_pearson_r=pearson(x,y),rolling_ice_MAE=ice_mae,
                rolling_historical_mean_MAE=baseline_mae,
                relative_MAE_difference_pct=100*(ice_mae/baseline_mae-1),
                n_ice_beats_historical_mean=sum(z["ice_absolute_error"]<z["historical_mean_absolute_error"] for z in ff),
                n_unbounded_predictions_outside_fraction=sum(z["out_of_0_1_range"] for z in ff)))
    g=next(r for r in metrics if r["window"]=="aug_nov_sic_pct" and r["response"]=="gentoo_fish")
    if abs(g["rolling_ice_MAE"]-.16800575348294394)>1e-9 or abs(g["rolling_historical_mean_MAE"]-.3113850020021918)>1e-9:
        raise ValueError("Verified BAS source result mismatch")
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    save(out/"species_four_year_chronological_predictions.csv",predictions)
    save(out/"species_window_summary.csv",metrics)
    result=dict(date="2026-11-02",analysis="posthoc exploratory species-specific Signy fish niche response",
        observation_unit="one Signy island x 9 breeding seasons; stomachs not climate replicates",
        n_years=9,n_heldout_chronological_years=4,actual_breeding_years=YEARS,
        n_original_9yr_valid_stomachs=counts,
        original_verified_nine_year_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),
        species_covariance_contributions=contributions,
        metrics=metrics,
        no_generalized_warming_or_CMIP6_biological_prediction=True,
        limitations=["Only four later test seasons, same geographic location and published samples",
            "Exposure windows and Gentoo-dominant contrast examined after viewing first results",
            "A positive within-sample historical hindcast gain is not independent evidence of climate causality",
            "Fish/(fish+crustacean) is wet mass composition, not food energy or foraging success",
            "Nearshore SIC 0-100km is not the bird-specific foraging ice conditions",
            "This simple linear model is not validated for 2050/2100 physical climate extrapolation"])
    (out/"summary.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return result
if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--nine-year",type=Path,required=True)
    parser.add_argument("--out",type=Path,required=True)
    a=parser.parse_args()
    z=run(a.nine_year,a.out)
    print(json.dumps({"n_heldout":z["n_heldout_chronological_years"],
      "gentoo_aug_nov_MAE":[t for t in z["metrics"] if t["response"]=="gentoo_fish" and t["window"]=="aug_nov_sic_pct"]},ensure_ascii=False))
