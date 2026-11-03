"""Calendar-date vs breeding-stage matching of original Signy BAS stomach diets.

The measured rows are adults sampled during chick-rearing in 2001–2019.
NO identical observation dates is a sampling-design finding, not proof that
penguin foraging or species resource niches never overlap. Distinguish
the physical sample calendar and each species' mean hatching phase.
"""
from __future__ import annotations
import argparse,csv,datetime,hashlib,json,math,statistics
from collections import defaultdict
from pathlib import Path
SAMPLES_SHA={
 "Adelie":"ab05193e94864ca05ea54a01154506f8e86f85291e2f01a68abab5d92229a04d",
 "Chinstrap":"a8dc89e0440cc8826925fc65bf9194de5151162b83c7d42db7ba3c97d49b164a",
 "Gentoo":"6f2a5fa1fc136ad6102dee8cd1c429d24c8ab81b50077bd21eb03f4e80fbd902"}
HATCH_SHA="d86d42a581ec8f5bdf123a2073de17469714ce85031914c32b2489afc2187c94"
SP=("Adelie","Chinstrap","Gentoo")
PAIRS=(("Adelie","Chinstrap"),("Adelie","Gentoo"),("Chinstrap","Gentoo"))
WINDOWS=(0,1,3,5,7,10)
FOURTEEN=(2001,2002,2003,2004,2005,2006,2007,2008,2009,2011,2012,2013,2014,2015)
def read(p):
 with Path(p).open(newline="",encoding="utf-8") as f:return list(csv.DictReader(f))
def mean(a):return sum(a)/len(a)
def med_date(records):
 dates=sorted(datetime.date.fromisoformat(x["date"]).toordinal() for x in records)
 return statistics.median(dates)
def date_dict(records):
 ans=defaultdict(list)
 for r in records:ans[datetime.date.fromisoformat(r["date"])].append(r)
 return dict(ans)
def selectable(a,b,k):
 """All original stomachs whose original collection date is within k calendar
 days of >=1 original source date for the other species in same season.
 Stomachs are NOT matched to distinct individual partners and do not multiply
 the number of climate-year replicates.
 """
 aa=date_dict(a);bb=date_dict(b)
 chosen_a=[v for d,vals in aa.items() if min(abs((d,e).days) for e in bb)<=k for v in vals]
 chosen_b=[v for d,vals in bb.items() if min(abs((d,e).days) for e in aa)<=k for v in vals]
 return chosen_a,chosen_b
def csvout(p,rows):
 if not rows:raise ValueError("No CSV output")
 with Path(p).open("w",newline="",encoding="utf-8") as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def run(dietdir,hatchdir,out):
 dietdir,hatchdir,out=map(Path,(dietdir,hatchdir,out))
 dg=json.loads((dietdir/"summary.json").read_text(encoding="utf-8"))
 hg=json.loads((hatchdir/"hatching_ice_summary.json").read_text(encoding="utf-8"))
 if dg["original_summary_sha256"]!=SAMPLES_SHA or dg["n_valid_stomach_records"]!=1364:
  raise ValueError("Original source diet SHA or grain changed")
 if hg["source_hatching_CSV_sha256"]!=HATCH_SHA or hg["n_paired_hatching_years"]!=17:
  raise ValueError("Original hatch source SHA or 17-year support changed")
 source=read(dietdir/"diet_sample_level.csv")
 source_dates=defaultdict(list)
 for r in source:
  sp=r["species"];y=int(r["season_start"])
  if sp not in SP or not 2001<=y<=2019:raise ValueError("Unexpected BAS source year/species")
  if not 0<=float(r["fish_within_fish_plus_crust"])<=1:
   raise ValueError("Invalid original wet mass fraction")
  source_dates[sp,y].append(r)
 hatch_original=read(hatchdir/"original_34_species_seasons.csv")
 hatch={(int(x["year"]),x["species"]):datetime.date.fromisoformat(x["hatching_calendar_date"]).toordinal()
  for x in hatch_original}
 if len(hatch)!=34:raise ValueError("Original 34 mean-hatching source rows changed")
 rows=[];matched=[]
 for first,second in PAIRS:
  years=sorted(set(y for sp,y in source_dates if sp==first)&set(y for sp,y in source_dates if sp==second))
  for yr in years:
   aa=source_dates[first,yr];bb=source_dates[second,yr]
   if min(len(aa),len(bb))<3:raise ValueError("Original co-sampled season too small")
   da=date_dict(aa);db=date_dict(bb)
   overlap=len(set(da)&set(db))
   min_gap=min(abs((a-b).days) for a in da for b in db)
   first_day=min(da);last_day=max(da);second_first=min(db);second_last=max(db)
   date_range_intersection=max(0,(min(last_day,second_last)-max(first_day,second_first)).days+1)
   row=dict(pair=first+"-"+second,season_start=yr,
     n_individual_stomachs_first=len(aa),n_individual_stomachs_second=len(bb),
     n_distinct_source_dates_first=len(da),n_distinct_source_dates_second=len(db),
     n_exact_identical_calendar_collection_dates=overlap,
     min_separation_of_original_collection_dates_days=min_gap,
     calendar_collection_span_intersection_days=date_range_intersection,
     first_species_sample_date_first=first_day.isoformat(),
     first_species_sample_date_last=last_day.isoformat(),
     second_species_sample_date_first=second_first.isoformat(),
     second_species_sample_date_last=second_last.isoformat(),
     signed_second_first_minus_first_last_days=(second_first-last_day).days,
     original_fish_share_gap_second_minus_first=
      mean([float(z["fish_within_fish_plus_crust"]) for z in bb])-
      mean([float(z["fish_within_fish_plus_crust"]) for z in aa]))
   rows.append(row)
   for k in WINDOWS:
    a,b=selectable(aa,bb,k)
    valid=len(a)>=3 and len(b)>=3
    matched.append(dict(pair=row["pair"],season_start=yr,
      maximum_nearest_other_species_sample_day_distance=k,
      n_selected_stomachs_first=len(a),n_selected_stomachs_second=len(b),
      n_selected_collection_days_first=len({r["date"] for r in a}),
      n_selected_collection_days_second=len({r["date"] for r in b}),
      both_species_at_least_three_stomachs=valid,
      selected_fish_fraction_first=mean([float(r["fish_within_fish_plus_crust"]) for r in a]) if valid else None,
      selected_fish_fraction_second=mean([float(r["fish_within_fish_plus_crust"]) for r in b]) if valid else None,
      fish_share_gap_second_minus_first=(
       mean([float(r["fish_within_fish_plus_crust"]) for r in b])-
       mean([float(r["fish_within_fish_plus_crust"]) for r in a])) if valid else None))
 if len(rows)!=37:raise ValueError("Expected 19 Adelie-Chinstrap + 9 x 2 other pairs")
 if any(r["n_exact_identical_calendar_collection_dates"]>0 for r in rows):
  raise ValueError("Original zero same-day pairs receipt changed")
 bypair=defaultdict(list)
 for r in rows:bypair[r["pair"]].append(r)
 response={}
 for pair,coll in bypair.items():
  pairstats=dict(n_paired_breeding_seasons=len(coll),
   n_seasons_with_exact_same_calendar_day=sum(r["n_exact_identical_calendar_collection_dates"]>0 for r in coll),
   minimum_date_separation_range_days=[min(r["min_separation_of_original_collection_dates_days"] for r in coll),
                                       max(r["min_separation_of_original_collection_dates_days"] for r in coll)],
   n_seasons_with_overlapping_original_calendar_date_ranges=sum(r["calendar_collection_span_intersection_days"]>0 for r in coll))
  for k in WINDOWS:
   sub=[r for r in matched if r["pair"]==pair and r["maximum_nearest_other_species_sample_day_distance"]==k]
   viable=[r for r in sub if r["both_species_at_least_three_stomachs"]]
   pairstats["within_"+str(k)+"_days"]=dict(n_breeding_seasons_with_3_stomachs_each=len(viable),
      n_original_stomachs_first=sum(int(r["n_selected_stomachs_first"]) for r in viable),
      n_original_stomachs_second=sum(int(r["n_selected_stomachs_second"]) for r in viable),
      n_positive_second_species_fish_gaps=sum(r["fish_share_gap_second_minus_first"]>0 for r in viable),
      mean_equal_season_weight_fish_share_gap=mean([r["fish_share_gap_second_minus_first"] for r in viable]) if viable else None)
  response[pair]=pairstats
 if {k:response[k]["n_paired_breeding_seasons"] for k in response}!={
  "Adelie-Chinstrap":19,"Adelie-Gentoo":9,"Chinstrap-Gentoo":9}:
  raise ValueError("Original source pair year support drift")
 if (response["Adelie-Chinstrap"]["within_7_days"]["n_breeding_seasons_with_3_stomachs_each"]!=11
  or response["Adelie-Gentoo"]["within_7_days"]["n_breeding_seasons_with_3_stomachs_each"]!=8
  or response["Chinstrap-Gentoo"]["within_7_days"]["n_breeding_seasons_with_3_stomachs_each"]!=3):
  raise ValueError("Original 7-day nearest match gate drift")
 stage=[]
 for year in FOURTEEN:
  coll=next((r for r in rows if r["pair"]=="Adelie-Chinstrap" and r["season_start"]==year),None)
  if coll is None:raise ValueError("14-year original hatch+diet source intersection drift")
  a=source_dates["Adelie",year];b=source_dates["Chinstrap",year]
  if (year,"Adelie") not in hatch or (year,"Chinstrap") not in hatch:raise ValueError("Missing original hatch")
  ma=med_date(a);mb=med_date(b);ha=hatch[year,"Adelie"];hb=hatch[year,"Chinstrap"]
  stage.append(dict(year=year,mean_hatching_gap_chinstrap_minus_adelie_days=hb-ha,
    sample_calendar_median_gap_chinstrap_minus_adelie_days=mb-ma,
    Adelie_median_sample_days_after_mean_hatch=ma-ha,
    Chinstrap_median_sample_days_after_mean_hatch=mb-hb,
    chinstrap_minus_adelie_breeding_stage_sample_day_difference=(mb-hb)-(ma-ha),
    original_first_Adelie_sample=coll["first_species_sample_date_first"],
    original_last_Adelie_sample=coll["first_species_sample_date_last"],
    original_first_Chinstrap_sample=coll["second_species_sample_date_first"],
    original_last_Chinstrap_sample=coll["second_species_sample_date_last"],
    minimum_same_calendar_sample_day_distance=coll["min_separation_of_original_collection_dates_days"],
    physical_calendar_sample_ranges_overlap=coll["calendar_collection_span_intersection_days"]>0,
    n_true_joint_day_stomach_samples=coll["n_exact_identical_calendar_collection_dates"]))
 if len(stage)!=14:raise ValueError("14 original date pairs expected")
 if any(r["physical_calendar_sample_ranges_overlap"] for r in stage):
  raise ValueError("Original 14-season nonoverlap receipt changed")
 result=dict(date="2026-11-04",
  status="original_source_calendar_observation_design_and_stage_sample_overlap_audit",
  source_BAS_diet_original_CSV_SHA256=SAMPLES_SHA,
  source_Dunn_2018_original_hatching_CSV_SHA256=HATCH_SHA,
  n_original_diet_stomachs=len(source),n_total_paired_species_years=len(rows),
  calendar_pair_support=response,
  hatching_14_season_support=dict(
   years=list(FOURTEEN),n_years=len(stage),
   n_original_both_species_same_day_stomach_collection_seasons=sum(r["n_true_joint_day_stomach_samples"]>0 for r in stage),
   n_calendar_date_range_overlapping_seasons=sum(r["physical_calendar_sample_ranges_overlap"] for r in stage),
   closest_collection_date_gap_min_days=min(r["minimum_same_calendar_sample_day_distance"] for r in stage),
   closest_collection_date_gap_max_days=max(r["minimum_same_calendar_sample_day_distance"] for r in stage),
   n_relative_hatch_stage_within_7days=sum(abs(r["chinstrap_minus_adelie_breeding_stage_sample_day_difference"])<=7 for r in stage),
   mean_calendar_sampling_gap_days=mean([r["sample_calendar_median_gap_chinstrap_minus_adelie_days"] for r in stage]),
   mean_hatching_gap_days=mean([r["mean_hatching_gap_chinstrap_minus_adelie_days"] for r in stage]),
   mean_stage_relative_gap_days=mean([r["chinstrap_minus_adelie_breeding_stage_sample_day_difference"] for r in stage])),
  all_seasons_with_exact_same_day_stomachs=0,
  original_9_year_Adelie_Gentoo_calendar_near_7day_mean_gap=response["Adelie-Gentoo"]["within_7_days"]["mean_equal_season_weight_fish_share_gap"],
  no_contemporaneous_two_species_stomach_diet_test=True,
  interpretation=["No two species sampled on the exact same calendar day in these original source series; this is observation coverage, not proof of segregated animal foraging",
   "Publisher stomach sampling occurred in 5 or fewer sessions/year/species, tuned to each species chick rearing stage",
   "Nearest-date <=7 days selects edge samples and cannot repair >~29-day biological chick age difference or identify prey competition",
   "Each source stomach independently collected, but season is climate replication unit; do not multiply stomachs/days into independent years",
   "Hatching mean is species-year from separate ~100 nest monitoring, not known hatch date of stomach-sampled adult",
   "Matching near-calendar dates does not establish same ocean waters, foraging places, available prey, or capture rates",
   "Gentoo fish-share contrast for calendar-nearby dates remains descriptive only; it is conditioned on sample availability",
   "Published Signy studies have compared co-rearing species directly in other years; do not conclude penguins never forage simultaneously",
   "For real same-date foraging spatial partition use observed GPS tracks and, for prey capture claims, matched TDR or diet from those birds"])
 out.mkdir(parents=True,exist_ok=True)
 csvout(out/"all_37_species_pair_seasons_calendar_support.csv",rows)
 csvout(out/"all_222_pair_year_window_sample_support.csv",matched)
 csvout(out/"hatching_14_seasons_sampling_stage_and_calendar.csv",stage)
 (out/"summary.json").write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
 return result
if __name__=="__main__":
 p=argparse.ArgumentParser()
 p.add_argument("--diet-dir",required=True,type=Path)
 p.add_argument("--hatch-dir",required=True,type=Path)
 p.add_argument("--out",required=True,type=Path)
 a=p.parse_args()
 result=run(a.diet_dir,a.hatch_dir,a.out)
 print(json.dumps({"n_original_source_stomachs":result["n_original_diet_stomachs"],
    "pair_years":result["n_total_paired_species_years"],
    "pairs":result["calendar_pair_support"],
    "hatching":result["hatching_14_season_support"]},ensure_ascii=False,indent=2))
