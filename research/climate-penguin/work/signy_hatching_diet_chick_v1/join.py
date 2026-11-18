"""Original BAS 14-season two-species hatching, diet, and chick-stage join.

Original inputs:
 - Dunn 2018 mean hatching (50% nest-with-chick, one annual estimate per species)
 - BAS individual stomach fish/(fish+crust) fractions, separate sampled birds
 - BAS colony-stage recorded chicks and fledglings, not tracked survival
 - OSI SAF GOPT nearshore sea ice physically distinct from camera 20km winter SIC
No within-individual mechanism or future population prediction.
"""
from __future__ import annotations
import argparse,csv,datetime,hashlib,json,math,statistics
from collections import defaultdict
from pathlib import Path
HATCH_SHA="d86d42a581ec8f5bdf123a2073de17469714ce85031914c32b2489afc2187c94"
DIET_SHA={"Adelie":"ab05193e94864ca05ea54a01154506f8e86f85291e2f01a68abab5d92229a04d",
          "Chinstrap":"a8dc89e0440cc8826925fc65bf9194de5151162b83c7d42db7ba3c97d49b164a",
          "Gentoo":"6f2a5fa1fc136ad6102dee8cd1c429d24c8ab81b50077bd21eb03f4e80fbd902"}
STAGE_SHA={"Adelie":"585f87928ed64d8982ef5bd86d8a785c38df65c39223d88ec17425854c786d62",
           "Chinstrap":"e50e98719ba5eedc6f5e617e0c7aa404ebfba15bc22a51e93e78cd4443bf787b"}
SP=("Adelie","Chinstrap")
EXPECTED=(2001,2002,2003,2004,2005,2006,2007,2008,2009,2011,2012,2013,2014,2015)
def read(p):
 with Path(p).open(newline="",encoding="utf-8") as f:return list(csv.DictReader(f))
def mean(x):
 if not x:raise ValueError("Empty mean")
 return sum(x)/len(x)
def median(x):return statistics.median(x)
def pearson(x,y):
 if len(x)!=len(y) or len(x)<3:return None
 mx,my=mean(x),mean(y)
 a=[v-mx for v in x];b=[v-my for v in y]
 den=math.sqrt(sum(v*v for v in a)*sum(v*v for v in b))
 return sum(v*w for v,w in zip(a,b))/den if den>1e-12 else None
def days(dates):
 if not dates:return None
 return median([datetime.date.fromisoformat(v).toordinal() for v in dates if v])
def save(path,rows):
 if not rows:raise ValueError("No derived records")
 with Path(path).open("w",encoding="utf-8",newline="") as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def run(hatchdir,dietdir,stagedir,outdir):
 hatchdir,dietdir,stagedir,outdir=map(Path,(hatchdir,dietdir,stagedir,outdir))
 hg=json.loads((hatchdir/"hatching_ice_summary.json").read_text())
 dg=json.loads((dietdir/"summary.json").read_text())
 sg=json.loads((stagedir/"source_gate.json").read_text())
 if hg["source_hatching_CSV_sha256"]!=HATCH_SHA or hg["n_paired_hatching_years"]!=17:
  raise ValueError("Hatching original source SHA/years changed")
 if dg["original_summary_sha256"]!=DIET_SHA:raise ValueError("Diet original CSV changed")
 for sp in SP:
  if sg["raw_source"][sp]["selected_csv_sha256"]!=STAGE_SHA[sp]:
   raise ValueError("Original stage source SHA changed "+sp)
 h=read(hatchdir/"paired_17year_hatching_ice.csv")
 orig=read(hatchdir/"original_34_species_seasons.csv")
 diets=read(dietdir/"diet_species_breeding_season.csv")
 stomachs=read(dietdir/"diet_sample_level.csv")
 stage=read(stagedir/"species_annual_stage_summary.csv")
 rawstage=read(stagedir/"source_stage_site_seasons.csv")
 by_hatch={(r["year"],r["species"]):r for r in orig}
 if len(by_hatch)!=34:raise ValueError("Source hatch duplicates")
 di={(r["species"],int(r["season_start"])):r for r in diets}
 st={(r["species"],int(r["season_start"])):r for r in stage}
 by_stomachs=defaultdict(list)
 for s in stomachs:
  if s["species"] in SP:by_stomachs[s["species"],int(s["season_start"])].append(s)
 by_stage=defaultdict(list)
 for r in rawstage:
  if r["species"] in SP:by_stage[r["species"],int(r["season_start"])].append(r)
 actual=[]
 for p in h:
  year=int(p["year"])
  if not all((sp,year) in di and (sp,year) in st and
             int(di[sp,year]["n_valid_stomachs"])>=3 and
             (str(year),sp) in by_hatch for sp in SP):continue
  r=dict(year=year,Adelie_hatching_colony=p["Adelie_colony"],
    Chinstrap_hatching_colony=p["Chinstrap_colony"],
    source_mean_hatch_gap_days=float(p["Chinstrap_minus_Adelie_hatching_gap_days"]),
    source_lay_gap_days=float(p["Chinstrap_minus_Adelie_laying_gap_days"]),
    GOPT_September_SIC=float(p["GOPT_September_ice_pct"]),
    GOPT_AugNov_SIC=float(p["GOPT_AugNov_ice_pct"]))
  for sp in SP:
   d=di[sp,year];v=st[sp,year]
   sample=by_stomachs[sp,year];cells=by_stage[sp,year]
   if len(sample)!=int(d["n_valid_stomachs"]):raise ValueError("Original stomach row count diverged")
   mean_hatch=by_hatch[str(year),sp]
   actual_date=datetime.date.fromisoformat(mean_hatch["hatching_calendar_date"]).toordinal()
   median_stomach=days([s["date"] for s in sample])
   if median_stomach is None:raise ValueError("No dated stomachs in source")
   early=days([s["chick_count_date"] for s in cells if s["chick_count_date"]])
   late=days([s["fledgling_count_date"] for s in cells if s["fledgling_count_date"]])
   r.update({sp+"_n_stomachs":len(sample),
     sp+"_mean_hatch_date":mean_hatch["hatching_calendar_date"],
     sp+"_median_stomach_date":datetime.date.fromordinal(round(median_stomach)).isoformat(),
     sp+"_median_stomach_calendar_ordinal":median_stomach,
     sp+"_mean_hatch_calendar_ordinal":actual_date,
     sp+"_stomach_days_after_population_mean_hatch":median_stomach-actual_date,
     sp+"_fish_fraction":float(d["mean_stomach_fish_fraction"]),
     sp+"_source_colonies_recording_chicks":int(v["observed_colonies"]),
     sp+"_recorded_chicks_per_pair_median":float(v["median_recorded_chicks_per_pair"]),
     sp+"_recorded_fledglings_per_pair_median":float(v["median_recorded_fledglings_per_pair"]) if v["median_recorded_fledglings_per_pair"] else None,
     sp+"_stomach_minus_original_early_chick_count_days":median_stomach-early if early else None,
     sp+"_stomach_minus_original_later_count_days":median_stomach-late if late else None})
  r["diet_sampling_calendar_gap_chinstrap_minus_adelie_days"]=r["Chinstrap_median_stomach_calendar_ordinal"]-r["Adelie_median_stomach_calendar_ordinal"]
  r["diet_sampling_relative_hatch_stage_gap_days"]=r["Chinstrap_stomach_days_after_population_mean_hatch"]-r["Adelie_stomach_days_after_population_mean_hatch"]
  if abs(r["diet_sampling_calendar_gap_chinstrap_minus_adelie_days"]-
    (r["source_mean_hatch_gap_days"]+r["diet_sampling_relative_hatch_stage_gap_days"]))>1e-8:
   raise ValueError("Temporal gap arithmetic identity failed")
  r["fish_fraction_gap_chinstrap_minus_adelie"]=r["Chinstrap_fish_fraction"]-r["Adelie_fish_fraction"]
  r["early_recorded_chick_gap_chinstrap_minus_adelie"]=r["Chinstrap_recorded_chicks_per_pair_median"]-r["Adelie_recorded_chicks_per_pair_median"]
  r["later_recorded_fledgling_gap_chinstrap_minus_adelie"]=(r["Chinstrap_recorded_fledglings_per_pair_median"]-r["Adelie_recorded_fledglings_per_pair_median"]
    if r["Chinstrap_recorded_fledglings_per_pair_median"] is not None and r["Adelie_recorded_fledglings_per_pair_median"] is not None else None)
  actual.append(r)
 actual.sort(key=lambda x:x["year"])
 if tuple(r["year"] for r in actual)!=EXPECTED:raise ValueError("Actual hatching+diet+recorded chicks year intersection changed")
 if any(not 0<=r[sp+"_fish_fraction"]<=1 for r in actual for sp in SP):raise ValueError("Invalid source fish composition")
 gaps=[r["diet_sampling_relative_hatch_stage_gap_days"] for r in actual]
 ad=[r["Adelie_stomach_days_after_population_mean_hatch"] for r in actual]
 chin=[r["Chinstrap_stomach_days_after_population_mean_hatch"] for r in actual]
 if not all(20<=v<=45 for v in ad+chin):raise ValueError("Original stomach sampling age alignment changed")
 def compare(x,y,label):
  a=[r[x] for r in actual];b=[r[y] for r in actual]
  r=pearson(a,b)
  loo=[pearson(a[:i]+a[i+1:],b[:i]+b[i+1:]) for i in range(len(a))]
  return dict(comparison=label,n=14,pearson_r=r,leave_one_year_out_range=[min(loo),max(loo)])
 metrics=[
  compare("source_mean_hatch_gap_days","GOPT_AugNov_SIC","hatching-gap versus nearshore sea ice"),
  compare("source_mean_hatch_gap_days","fish_fraction_gap_chinstrap_minus_adelie","hatching gap versus fish fraction gap"),
  compare("source_mean_hatch_gap_days","early_recorded_chick_gap_chinstrap_minus_adelie","hatching gap versus early chicks difference"),
  compare("source_mean_hatch_gap_days","diet_sampling_relative_hatch_stage_gap_days","hatching gap versus stomach relative-stage difference"),
  compare("fish_fraction_gap_chinstrap_minus_adelie","early_recorded_chick_gap_chinstrap_minus_adelie","fish fraction gap versus early recorded chicks difference")]
 summary=dict(status="original_BAS_14_joint_seasons_two_species_hatch_diet_chick_stages_exploratory",
  years=list(EXPECTED),source_hatch_doi="10.5285/274b49bd-40a4-4e5d-bd5f-69a1ba09d403",
  source_original_hatch_csv_sha256=HATCH_SHA,
  source_original_diet_csv_sha256=DIET_SHA,source_original_stage_csv_sha256=STAGE_SHA,
  n_matched_years=len(actual),n_matched_species_years=len(actual)*2,
  n_source_stomach_samples=sum(r[sp+"_n_stomachs"] for r in actual for sp in SP),
  n_independent_islands=1,
  mean_adelie_stomach_days_after_mean_hatching=mean(ad),
  mean_chinstrap_stomach_days_after_mean_hatching=mean(chin),
  mean_stage_age_gap_chin_minus_adelie=mean(gaps),
  median_stage_age_gap_chin_minus_adelie=median(gaps),
  n_same_stage_within_5days=sum(abs(v)<=5 for v in gaps),
  n_same_stage_within_7days=sum(abs(v)<=7 for v in gaps),
  mean_calendar_stomach_collection_gap_days=mean([r["diet_sampling_calendar_gap_chinstrap_minus_adelie_days"] for r in actual]),
  n_diet_median_after_mean_hatching=sum(r[sp+"_stomach_days_after_population_mean_hatch"]>0 for r in actual for sp in SP),
  n_diet_median_after_original_early_chick_count=sum(r[sp+"_stomach_minus_original_early_chick_count_days"]>0 for r in actual for sp in SP
   if r[sp+"_stomach_minus_original_early_chick_count_days"] is not None),
  metrics=metrics,
  scope_notes=["Mean hatching date is one model-derived date per species-year from ~100 nests, NOT same nests as stomach samples",
    "Diet stomach is chick-rearing adult, not a tagged nest/chick; inferred days since mean hatching is a population-stage proxy",
    "Diet sampled at roughly same brood stage but on different calendar days: year-matched prey environments may differ",
    "Original Adélie hatch colony changes A41 to A39 in 2003; 14-year cross-axis includes only 2 pre-switch years",
    "Fish dietary share is fish/(fish+crust) and does not measure foraging location, quantity or competition",
    "Original recorded chicks and fledglings are separate survey units and not individual survival",
    "One Signy island only; 14 years with nonrandom sample availability and previous literature covering same organism",
    "No causal sea-ice to food to reproductive outcomes or calibrated CMIP6 future penguin biological projections"])
 outdir.mkdir(parents=True,exist_ok=True)
 # Exact original chronology-colony label to independent source breeding census.
 # Do not automatically rescue C69 with ambiguous A69 or arbitrary nearby labels.
 chronology=[]
 target_by_year={}
 for a in actual:
  year=a["year"]
  target_by_year[year]={}
  for sp in SP:
   target=a[sp+"_hatching_colony"]
   orig=by_stage[sp,year]
   candidates=sorted({z["colony"] for z in orig})
   matched=[z for z in orig if z["colony"].strip().upper()==target.upper()]
   if len(matched)>1:raise ValueError("Original stage chronology label duplicate")
   r=matched[0] if matched else None
   ratio=float(r["reported_chicks_per_pair"]) if r and r["reported_chicks_per_pair"] not in ("",None) else None
   late=float(r["recorded_fledglings_per_pair"]) if r and r["recorded_fledglings_per_pair"] not in ("",None) else None
   target_by_year[year][sp]=ratio
   chronology.append(dict(year=year,species=sp,original_hatching_colony=target,
    exact_original_stage_colony_found=bool(r),
    observed_original_stage_colony_labels=";".join(candidates),
    original_stage_chicks_per_pair=ratio,
    original_stage_recorded_fledglings_per_pair=late,
    original_chick_count_date=r["chick_count_date"] if r else "",
    original_late_count_date=r["fledgling_count_date"] if r else "",
    original_source_stage_island_colony_not_individual_100nests=True))
 matched_chronology=[]
 for a in actual:
  year=a["year"];z=target_by_year[year]
  if all(z[sp] is not None for sp in SP):
   matched_chronology.append(dict(year=year,
     hatching_gap_days=a["source_mean_hatch_gap_days"],
     source_chronology_chick_gap_chin_minus_adelie=z["Chinstrap"]-z["Adelie"],
     source_colonies=a["Adelie_hatching_colony"]+"|"+a["Chinstrap_hatching_colony"],
     nearshore_aug_nov_SIC_pct=a["GOPT_AugNov_SIC"]))
 def paircor(rs):
  if len(rs)<3:return None
  return pearson([z["hatching_gap_days"] for z in rs],
    [z["source_chronology_chick_gap_chin_minus_adelie"] for z in rs])
 summary["original_chronology_colony_census_qa"]={
  "n_year_species_colony_rows":len(chronology),
  "n_year_species_exact_matching_colony":sum(r["exact_original_stage_colony_found"] for r in chronology),
  "n_years_with_both_exact_original_colony_chick_counts":len(matched_chronology),
  "all_matched_years_hatch_gap_vs_original_colony_chick_gap_r":paircor(matched_chronology),
  "post_2003_fixed_Adelie_A39_versus_Chinstrap_C69_n":sum(z["year"]>=2003 for z in matched_chronology),
  "post_2003_hatch_gap_vs_original_colony_chick_gap_r":paircor([z for z in matched_chronology if z["year"]>=2003]),
  "is_not_the_same_100_marked_nests":True,
  "original_colony_labels_not_GIS_verified":True,
  "no_imputation_for_absent_colony":True}
 save(outdir/"original_chronology_colony_matching_14years.csv",chronology)
 if matched_chronology:save(outdir/"hatching_chronology_colony_chick_pairs.csv",matched_chronology)
 save(outdir/"fourteen_hatching_food_chicks_years.csv",actual)
 save(outdir/"fourteen_years_three_axis_correlations.csv",metrics)
 (outdir/"summary.json").write_text(json.dumps(summary,indent=2,ensure_ascii=False)+"\n",encoding="utf8")
 return summary
if __name__=="__main__":
 p=argparse.ArgumentParser()
 for name in ("hatch-dir","diet-dir","stage-dir","out"):p.add_argument("--"+name,required=True,type=Path)
 a=p.parse_args()
 r=run(a.hatch_dir,a.diet_dir,a.stage_dir,a.out)
 print(json.dumps({key:r[key] for key in ("n_matched_years","n_source_stomach_samples",
    "mean_adelie_stomach_days_after_mean_hatching","mean_chinstrap_stomach_days_after_mean_hatching",
    "n_same_stage_within_7days","mean_calendar_stomach_collection_gap_days","metrics")},ensure_ascii=False,indent=2))
