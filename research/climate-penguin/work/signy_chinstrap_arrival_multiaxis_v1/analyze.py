"""Link Signy chinstrap count-session timing with diet, chicks and sea ice.

Source data are SHA-pinned publisher archives. This is NOT true arrival
phenology: annual weighted date of OBSERVED incoming-bird counts depends on
the first survey date/staff presence. Only season-year is aligned; individual
birds, nests and the physical SIGNc camera footprint are NOT co-registered.
"""
from __future__ import annotations
import argparse,csv,datetime,hashlib,json,math
from pathlib import Path
DIET_SHA={"Adelie":"ab05193e94864ca05ea54a01154506f8e86f85291e2f01a68abab5d92229a04d",
"Chinstrap":"a8dc89e0440cc8826925fc65bf9194de5151162b83c7d42db7ba3c97d49b164a",
"Gentoo":"6f2a5fa1fc136ad6102dee8cd1c429d24c8ab81b50077bd21eb03f4e80fbd902"}
ARRIVAL_SHA="b8fd11b8ad1d34b2ff85838cbacac746d516efd51418df5b0fe183d1303ab239"
STAGE_SHA={"Adelie":"585f87928ed64d8982ef5bd86d8a785c38df65c39223d88ec17425854c786d62",
"Chinstrap":"e50e98719ba5eedc6f5e617e0c7aa404ebfba15bc22a51e93e78cd4443bf787b"}
WINDOWS=("GOPT_ice_September_pct","GOPT_ice_AugNov_pct")
def read(path):
 with Path(path).open(encoding="utf8",newline="") as f:return list(csv.DictReader(f))
def mean(v):
 if not v:raise ValueError("No values")
 return sum(v)/len(v)
def corr(x,y):
 if len(x)!=len(y) or len(x)<3:return None
 ma=mean(x);mb=mean(y)
 a=[v-ma for v in x];b=[v-mb for v in y]
 d=math.sqrt(sum(v*v for v in a)*sum(v*v for v in b))
 return sum(v*w for v,w in zip(a,b))/d if d>1e-12 else None
def residual(x,z):
 mz=mean(z);mx=mean(x)
 d=sum((v-mz)**2 for v in z)
 if d<1e-12:return None
 slope=sum((v-mz)*(u-mx) for v,u in zip(z,x))/d
 return [u-mx-slope*(v-mz) for u,v in zip(x,z)]
def partial(x,y,first):
 a=residual(x,first);b=residual(y,first)
 return corr(a,b) if a is not None and b is not None else None
def doy_no_leap(v):
 d=datetime.date.fromisoformat(v)
 return datetime.date(2001,d.month,d.day).timetuple().tm_yday
def save(path,records):
 with Path(path).open("w",encoding="utf8",newline="") as f:
  w=csv.DictWriter(f,fieldnames=list(records[0]));w.writeheader();w.writerows(records)
def run(arrival_dir,diet_dir,stage_dir,out):
 arrival_dir,diet_dir,stage_dir,out=map(Path,(arrival_dir,diet_dir,stage_dir,out))
 ag=json.loads((arrival_dir/"summary.json").read_text(encoding="utf8"))
 dg=json.loads((diet_dir/"summary.json").read_text(encoding="utf8"))
 sg=json.loads((stage_dir/"source_gate.json").read_text(encoding="utf8"))
 if ag["source_inner_csv_sha256"]!=ARRIVAL_SHA:raise ValueError("Chinstrap arrival source SHA drift")
 if dg["original_summary_sha256"]!=DIET_SHA:raise ValueError("Diet source SHAs drift")
 for species in STAGE_SHA:
  if sg["raw_source"][species]["selected_csv_sha256"]!=STAGE_SHA[species]:
   raise ValueError("Original BAS breeding count source drift "+species)
 original_arrivals=read(arrival_dir/"original_arrival_count_year_effort.csv")
 fish=read(diet_dir/"diet_species_breeding_season.csv")
 env=read(diet_dir/"diet_pair_season_antecedent_sic.csv")
 stage=read(stage_dir/"species_annual_stage_summary.csv")
 d={(r["species"],int(r["season_start"])):r for r in fish}
 e={(r["pair"],int(r["breeding_season_start"])):r for r in env}
 s={(r["species"],int(r["season_start"])):r for r in stage}
 original_eligible=[]
 matched=[]
 for x in original_arrivals:
  y=int(x["year"]);n=int(x["n_survey_dates"])
  if n<4:continue  # fixed field-effort gate, not optimized for correlations.
  original_eligible.append(y)
  if not all((sp,y) in d and (sp,y) in s for sp in ("Adelie","Chinstrap")):continue
  if ("Adelie-Chinstrap",y) not in e:continue
  if min(int(d[sp,y]["n_valid_stomachs"]) for sp in ("Adelie","Chinstrap"))<3:continue
  ice=e["Adelie-Chinstrap",y]
  first=doy_no_leap(x["first_date"])
  observed=doy_no_leap(x["weighted_median_observed_count_date"])
  if observed<first:raise ValueError("Published observed-count median earlier than first survey")
  obs={}
  for sp in ("Adelie","Chinstrap"):
   obs[sp+"_fish_fraction"]=float(d[sp,y]["mean_stomach_fish_fraction"])
   obs[sp+"_recorded_chicks_per_pair"]=float(s[sp,y]["median_recorded_chicks_per_pair"])
   obs[sp+"_n_stomachs"]=int(d[sp,y]["n_valid_stomachs"])
   obs[sp+"_n_original_colonies"]=int(s[sp,y]["observed_colonies"])
  matched.append(dict(year=y,n_arrival_count_sessions=n,
   first_survey_calendar_doy_365=first,
   weighted_median_observed_arrival_count_calendar_doy_365=observed,
   weighted_median_after_first_survey_days=observed-first,
   survey_duration_days=int(x["span_calendar_days"]),
   GOPT_ice_September_pct=float(ice["preceding_sep_sic_pct"]),
   GOPT_ice_AugNov_pct=float(ice["preceding_aug_nov_sic_pct"]),
   **obs,Chinstrap_minus_Adelie_fish_fraction=obs["Chinstrap_fish_fraction"]-obs["Adelie_fish_fraction"],
   Chinstrap_minus_Adelie_early_chick_per_pair=obs["Chinstrap_recorded_chicks_per_pair"]-obs["Adelie_recorded_chicks_per_pair"]))
 if len(original_eligible)!=16 or len(matched)!=13 or [r["year"] for r in matched]!=[2001,2002,2003,2004,2005,2006,2007,2009,2011,2015,2016,2017,2018]:
  raise ValueError("Original-year and field-effort strict cohort changed")
 x=[r["weighted_median_observed_arrival_count_calendar_doy_365"] for r in matched]
 first=[r["first_survey_calendar_doy_365"] for r in matched]
 names=list(WINDOWS)+["Chinstrap_fish_fraction","Chinstrap_recorded_chicks_per_pair",
   "Chinstrap_minus_Adelie_fish_fraction","Chinstrap_minus_Adelie_early_chick_per_pair"]
 metrics=[]
 for col in names:
  y=[r[col] for r in matched]
  metrics.append(dict(outcome_or_covariate=col,n_breeding_seasons=13,
   correlation_with_observed_weighted_chinstrap_count_date=corr(x,y),
   association_conditioned_on_first_available_survey_date=partial(x,y,first),
   first_survey_date_vs_other_variable_r=corr(first,y),
   method_scope="source-sampled observed arrival-count median; not true species settlement date or interspecies phenology"))
 # Also report the 16-year all-original survey-effort confounding.
 first16=[doy_no_leap(r["first_date"]) for r in original_arrivals if int(r["n_survey_dates"])>=4]
 med16=[doy_no_leap(r["weighted_median_observed_count_date"]) for r in original_arrivals if int(r["n_survey_dates"])>=4]
 if len(first16)!=16:raise ValueError("Effort audit no longer contains 16 years")
 summary=dict(date="2026-11-03",status="source_verified_observation_process_diagnostics_not_true_arrival_phenology",
  source_chinstrap_arrival_csv_sha256=ARRIVAL_SHA,source_diet_original_csv_sha256=DIET_SHA,
  source_stage_original_csv_sha256=STAGE_SHA,n_original_calendar_years=17,
  original_calendar_years_with_at_least_four_sessions=original_eligible,
  n_at_least_four_session_calendar_years=len(original_eligible),
  n_same_island_years_with_diet_and_recorded_chick_stage=len(matched),
  matched_calendar_years=[r["year"] for r in matched],
  original_16_year_start_vs_observed_count_median_r=corr(first16,med16),
  matched_13_year_start_vs_observed_count_median_r=corr(first,x),
  metrics=metrics,
  original_2008_single_survey_excluded=True,
  n_distinct_islands=1,
  no_inter_species_settlement_gap=True,
  no_seaice_causal_inference=True,
  limitations=["The first field survey is constrained by station opening and cannot show the true first bird arrival",
    "Observed count-weighted median is left-censored and depends on session schedule, total birds counted, and coverage",
    "Survey sessions within each year are not independent climate-year samples",
    "Same-island-year matching does not connect surveyed arrivals to nesting pairs or individual BAS stomach samples",
    "Calendar 365-day index is leap-year-standardized for November dates",
    "The phenology/diet/chick comparisons were posthoc exploratory and not preregistered",
    "Longer n=13 survey-window series is not equivalent to the actual paired-species SIGNc camera timing gap n=4",
    "No transfer of environment coefficients to CMIP6 future penguin counts or arrival dates"])
 out.mkdir(parents=True,exist_ok=True)
 save(out/"same_island_year_arrival_effort_diet_chick.csv",matched)
 save(out/"observed_arrival_proxy_correlations.csv",metrics)
 (out/"summary.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
 print(json.dumps({"n_matched":len(matched),"years":summary["matched_calendar_years"],
                   "first_vs_observed":summary["matched_13_year_start_vs_observed_count_median_r"],
                   "SIC_associations":metrics[:2]},ensure_ascii=False,indent=2))
 return summary
if __name__=="__main__":
 p=argparse.ArgumentParser()
 p.add_argument("--arrival-dir",type=Path,required=True)
 p.add_argument("--diet-dir",type=Path,required=True)
 p.add_argument("--stage-dir",type=Path,required=True)
 p.add_argument("--out",type=Path,required=True)
 a=p.parse_args();run(a.arrival_dir,a.diet_dir,a.stage_dir,a.out)
