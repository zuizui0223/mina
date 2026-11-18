"""Strict same-island/same-breeding-season Signy 3-axis penguin source join.

Camera timing: exact physical SIGNc camera, source paper (2016-2020).
Diet: original BAS individual-stomach samples for Adelie/Chinstrap.
Land: independent BAS colony-year chicks/fledgling counts.
The 2016-2019 intersection is an island-season join, NOT the same birds,
nesting polygons, diet prey before chick counts, or independently sampled islands.
"""
from __future__ import annotations
import argparse,csv,hashlib,itertools,json,math,statistics,datetime
from collections import defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
CAMERA=ROOT/"outputs/temporal_niche_pair_v1/exact_camera_pairs.csv"
CAMERA_BLOB="f54895e3d5ceca5d3e929b2d7843937b0544246b"
DIET_SHAS={"Adelie":"ab05193e94864ca05ea54a01154506f8e86f85291e2f01a68abab5d92229a04d",
 "Chinstrap":"a8dc89e0440cc8826925fc65bf9194de5151162b83c7d42db7ba3c97d49b164a",
 "Gentoo":"6f2a5fa1fc136ad6102dee8cd1c429d24c8ab81b50077bd21eb03f4e80fbd902"}
STAGE_SHAS={"Adelie":"585f87928ed64d8982ef5bd86d8a785c38df65c39223d88ec17425854c786d62",
 "Chinstrap":"e50e98719ba5eedc6f5e617e0c7aa404ebfba15bc22a51e93e78cd4443bf787b",
 "Gentoo":"53fe3821f313ed35840376fcf4d11c8e0e8fbbd63f01ba84a5e21c2db4df6d6b"}
SPECIES=("Adelie","Chinstrap")
def read(path):
 with Path(path).open(newline="",encoding="utf-8") as h:return list(csv.DictReader(h))
def mean(x):
 if not x:raise ValueError("Mean of no observations")
 return sum(x)/len(x)
def median(x):
 if not x:return None
 return statistics.median(x)
def correlation(x,y):
 if len(x)!=len(y) or len(x)<3:return None
 ax=mean(x);ay=mean(y)
 u=[v-ax for v in x];w=[v-ay for v in y]
 den=math.sqrt(sum(v*v for v in u)*sum(v*v for v in w))
 return sum(a*b for a,b in zip(u,w))/den if den>1e-12 else None
def exact_perm(x,y):
 if len(x)!=len(y) or len(x)>8 or len(x)<3:raise ValueError("Enumeration limited to 3-8 source years")
 r=correlation(x,y)
 if r is None:return {"r":None,"n_permutations":0,"extreme":0,"two_sided":None,"loo":None}
 vals=[]
 for order in itertools.permutations(y):
  vals.append(correlation(x,order))
 extreme=sum(abs(t)>=abs(r)-1e-12 for t in vals if t is not None)
 loo=[correlation(x[:i]+x[i+1:],y[:i]+y[i+1:]) for i in range(len(y))]
 return dict(r=r,n_permutations=len(vals),extreme=extreme,two_sided=extreme/len(vals),
   leave_one_year_out=loo,year_exchangeability_unverified=True)
def vnum(value):
 try:
  x=float(value)
  return x if math.isfinite(x) else None
 except (ValueError,TypeError):return None
def day(value):
 if not value:return None
 return datetime.date.fromisoformat(value)
def daymedian(vals):
 v=[a.toordinal() for a in vals if a is not None]
 return datetime.date.fromordinal(round(median(v))) if v else None
def datediff(a,b):
 return (a-b).days if a is not None and b is not None else None
def write(path,rows):
 if not rows:raise ValueError("Empty output")
 with Path(path).open("w",newline="",encoding="utf-8") as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]))
  w.writeheader();w.writerows(rows)
def run(diet_dir,stage_dir,out):
 diet_dir,stage_dir,out=map(Path,(diet_dir,stage_dir,out))
 raw=CAMERA.read_bytes()
 blob=hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()
 if blob!=CAMERA_BLOB:raise ValueError("Fixed exact camera source drift")
 original_camera=read(CAMERA)
 if len(original_camera)!=15:raise ValueError("Camera source row count drift")
 timing={int(r["year"]):r for r in original_camera if r["pair"]=="Adelie-Chinstrap" and r["camera"]=="SIGNc"}
 if sorted(timing)!=[2016,2017,2018,2019,2020]:raise ValueError("Signy exact camera pair original years changed")
 diet_source=json.loads((diet_dir/"summary.json").read_text(encoding="utf-8"))
 stage_source=json.loads((stage_dir/"source_gate.json").read_text(encoding="utf-8"))
 if diet_source["original_summary_sha256"]!=DIET_SHAS:raise ValueError("Original diet SHA changed")
 for sp in SPECIES:
  if stage_source["raw_source"][sp]["selected_csv_sha256"]!=STAGE_SHAS[sp]:
   raise ValueError("Original stage source changed "+sp)
 diets=read(diet_dir/"diet_species_breeding_season.csv")
 pair_ice=read(diet_dir/"diet_pair_season_antecedent_sic.csv")
 samples=read(diet_dir/"diet_sample_level.csv")
 stages=read(stage_dir/"species_annual_stage_summary.csv")
 source_stage=read(stage_dir/"source_stage_site_seasons.csv")
 di={(r["species"],int(r["season_start"])):r for r in diets}
 st={(r["species"],int(r["season_start"])):r for r in stages}
 pi={(r["pair"],int(r["breeding_season_start"])):r for r in pair_ice}
 if len(di)!=len(diets) or len(st)!=len(stages) or len(pi)!=len(pair_ice):
  raise ValueError("Source duplicate at species/year or pair/year")
 # Fixed by input availability, never by observed response signs.
 joined_years=[y for y in sorted(timing) if all(
    (sp,y) in di and int(di[sp,y]["n_valid_stomachs"])>=3 and
    (sp,y) in st and vnum(st[sp,y]["median_recorded_chicks_per_pair"]) is not None
    for sp in SPECIES) and ("Adelie-Chinstrap",y) in pi]
 if joined_years!=[2016,2017,2018,2019]:
  raise ValueError("Source complete-case intersection changed")
 full_col=defaultdict(dict);raw_groups=defaultdict(list);stomachs=defaultdict(list)
 for r in source_stage:
  sp=r["species"];y=int(r["season_start"])
  if sp not in SPECIES or y not in joined_years:continue
  raw_groups[sp,y].append(r)
  ratio=vnum(r["reported_chicks_per_pair"])
  if ratio is not None:
   if r["colony"] in full_col[sp,y]:raise ValueError("Duplicate original colony in paired year")
   full_col[sp,y][r["colony"]]=ratio
 for s in samples:
  sp=s["species"];y=int(s["season_start"])
  if sp in SPECIES and y in joined_years:stomachs[sp,y].append(s)
 fixed_labels={sp:sorted(set.intersection(*(set(full_col[sp,y]) for y in joined_years)))
               for sp in SPECIES}
 if any(len(z)<2 for z in fixed_labels.values()):raise ValueError("Insufficient fixed source colony labels")
 result=[]
 for y in joined_years:
  cam=timing[y];sic=pi["Adelie-Chinstrap",y]
  entry={"year":y,"camera":"SIGNc","camera_pair":"Adelie-Chinstrap",
    "camera_timing_gap_days":int(cam["gap_days"]),
    "camera_20km_winter_sic_pct":float(cam["winter_sic_20km_pct"]),
    "GOPT_nearshore_september_sic_pct":float(sic["preceding_sep_sic_pct"]),
    "GOPT_nearshore_aug_nov_sic_pct":float(sic["preceding_aug_nov_sic_pct"])}
  for sp in SPECIES:
   d=di[sp,y];s=st[sp,y]
   samples_this=stomachs[sp,y]
   if len(samples_this)!=int(d["n_valid_stomachs"]):
    raise ValueError("Original date-sample support inconsistent")
   fish=vnum(d["mean_stomach_fish_fraction"])
   if not 0<=fish<=1:raise ValueError("Invalid fish fraction")
   chick=vnum(s["median_recorded_chicks_per_pair"])
   late=vnum(s["median_recorded_fledglings_per_pair"])
   if late is None:raise ValueError("Unverified later breeding stage")
   sample_dates=[day(x["date"]) for x in samples_this]
   early_dates=[day(x["chick_count_date"]) for x in raw_groups[sp,y]]
   late_dates=[day(x["fledgling_count_date"]) for x in raw_groups[sp,y]]
   early=daymedian(early_dates);late_date=daymedian(late_dates);sdate=daymedian(sample_dates)
   entry.update({sp+"_n_stomachs":len(samples_this),
     sp+"_fish_within_fish_plus_crust":fish,
     sp+"_chicks_per_pair_median":chick,
     sp+"_recorded_fledglings_per_pair_median":late,
     sp+"_n_original_colonies":int(s["observed_colonies"]),
     sp+"_n_fixed_colony_labels":len(fixed_labels[sp]),
     sp+"_fixed_colony_chicks_per_pair_median":median([full_col[sp,y][key] for key in fixed_labels[sp]]),
     sp+"_median_stomach_date":sdate.isoformat() if sdate else "",
     sp+"_median_early_chick_count_date":early.isoformat() if early else "",
     sp+"_median_late_count_date":late_date.isoformat() if late_date else "",
     sp+"_stomach_minus_early_chick_count_days":datediff(sdate,early),
     sp+"_stomach_minus_late_count_days":datediff(sdate,late_date),
     sp+"_n_original_chick_dates":sum(d is not None for d in early_dates),
     sp+"_n_original_late_dates":sum(d is not None for d in late_dates)})
  entry["Chinstrap_minus_Adelie_fish_gap"]=entry["Chinstrap_fish_within_fish_plus_crust"]-entry["Adelie_fish_within_fish_plus_crust"]
  entry["Chinstrap_minus_Adelie_early_chick_gap"]=entry["Chinstrap_chicks_per_pair_median"]-entry["Adelie_chicks_per_pair_median"]
  entry["Chinstrap_minus_Adelie_fixed_label_early_chick_gap"]=entry["Chinstrap_fixed_colony_chicks_per_pair_median"]-entry["Adelie_fixed_colony_chicks_per_pair_median"]
  entry["Chinstrap_minus_Adelie_recorded_fledgling_gap"]=entry["Chinstrap_recorded_fledglings_per_pair_median"]-entry["Adelie_recorded_fledglings_per_pair_median"]
  result.append(entry)
 if [(r["year"],r["camera_timing_gap_days"]) for r in result]!=[(2016,18),(2017,29),(2018,29),(2019,19)]:
  raise ValueError("Exact camera independent source receipt failed")
 if [(r["Adelie_n_stomachs"],r["Chinstrap_n_stomachs"]) for r in result]!=[(30,31),(30,31),(30,30),(30,30)]:
  raise ValueError("Original stomach source support differs")
 contrasts={
  "camera_timing_vs_winter_20km_ice":("camera_timing_gap_days","camera_20km_winter_sic_pct"),
  "camera_timing_vs_GOPT_sep_ice":("camera_timing_gap_days","GOPT_nearshore_september_sic_pct"),
  "camera_timing_vs_fish_share_gap":("camera_timing_gap_days","Chinstrap_minus_Adelie_fish_gap"),
  "camera_timing_vs_early_chick_gap":("camera_timing_gap_days","Chinstrap_minus_Adelie_early_chick_gap"),
  "fish_share_gap_vs_early_chick_gap":("Chinstrap_minus_Adelie_fish_gap","Chinstrap_minus_Adelie_early_chick_gap"),
  "fish_share_gap_vs_fixed_chick_gap":("Chinstrap_minus_Adelie_fish_gap","Chinstrap_minus_Adelie_fixed_label_early_chick_gap")
 }
 metrics=[]
 for name,(x,y) in contrasts.items():
  stats=exact_perm([v[x] for v in result],[v[y] for v in result])
  metrics.append({"comparison":name,"x":x,"y":y,**stats})
 notes={
  "date":"2026-11-03","status":"strict_source_matched_2016_2019_Signy_three_axis_four_seasons_exploratory",
  "cameras_matched_from_original":5,"n_three_axis_years":len(result),
  "all_Signy_three_axis_breeding_season_start_years":joined_years,
  "camera_2020_stage_data_available":False,
  "unique_physical_cameras":1,"unique_islands":1,
  "source_camera_git_blob":CAMERA_BLOB,
  "source_BAS_diet_sha256":DIET_SHAS,
  "source_BAS_stage_sha256":{sp:STAGE_SHAS[sp] for sp in SPECIES},
  "fixed_original_colony_label_count":{sp:len(v) for sp,v in fixed_labels.items()},
  "fixed_labels_not_verified_equivalent_GIS_footprints":True,
  "original_sample_recruitment_false":True,
  "n_exact_permutations_per_four_year_contrast":24,
  "metrics":metrics,
  "sample_days_and_census_days_same_organism":False,
  "note":[
   "Actual same camera SIGNc settlement difference, but BAS stomach samples and source colonies not matched to the camera footprint",
   "Signy island-by-breeding-season alignment, not within-individual or nesting-patch response",
   "Camera 20 km winter SIC and GOPT 0-100 km September/Aug-Nov SIC are different environmental estimands",
   "Absolute settlement index calendar-day origin is unverified; only pair gaps are used",
   "2020 camera timing is available but stage source years end 2019: no observation was imputed",
   "N=4 seasons, all exact 4! tests are posthoc; no confirmed cross-axis climate mediation",
   "Source diet sampled during chick rearing; timing relative to early and late counts audited but not same individual",
   "Fish proportion does not measure absolute krill/fish intake",
   "Original fledgling counts do not measure recruitment or directly tracked fledging survival",
   "Do not project future phenology, competition, prey composition or nest counts from CMIP6"
  ]
 }
 out.mkdir(parents=True,exist_ok=True)
 write(out/"source_matched_four_breeding_seasons.csv",result)
 write(out/"four_season_exact_24_permutations.csv",metrics)
 (out/"summary.json").write_text(json.dumps(notes,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 return notes
if __name__=="__main__":
 p=argparse.ArgumentParser()
 p.add_argument("--diet-dir",type=Path,required=True)
 p.add_argument("--stage-dir",type=Path,required=True)
 p.add_argument("--out",type=Path,required=True)
 a=p.parse_args()
 result=run(a.diet_dir,a.stage_dir,a.out)
 print(json.dumps({"source_matching_years":result["n_three_axis_years"],
     "years":result["all_Signy_three_axis_breeding_season_start_years"],
     "original_colonies":result["fixed_original_colony_label_count"],
     "metrics":result["metrics"]},ensure_ascii=False,indent=2))
