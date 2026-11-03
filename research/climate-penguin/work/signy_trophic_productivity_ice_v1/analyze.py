"""Signy marine diet, antecedent sea ice and recorded chicks: exact-year audit.

Strict 2001-2009 same island/year 3 species. Original BAS diet and stage
source hashes are checked upstream, and rechecked in this script.
Spatial colony roster can change: use all observed plus fixed-colony subset.
All analyses exploratory; year exchangeability is unverified.
"""
from __future__ import annotations
import argparse,csv,hashlib,itertools,json,math
from collections import defaultdict
from pathlib import Path

SPECIES=("Adelie","Chinstrap","Gentoo")
YEARS=tuple(range(2001,2010))
ICE=("sep_sic_pct","aug_nov_sic_pct")
DIET_SHA={
 "Adelie":"ab05193e94864ca05ea54a01154506f8e86f85291e2f01a68abab5d92229a04d",
 "Chinstrap":"a8dc89e0440cc8826925fc65bf9194de5151162b83c7d42db7ba3c97d49b164a",
 "Gentoo":"6f2a5fa1fc136ad6102dee8cd1c429d24c8ab81b50077bd21eb03f4e80fbd902"}
STAGE_SHA={
 "Adelie":"585f87928ed64d8982ef5bd86d8a785c38df65c39223d88ec17425854c786d62",
 "Chinstrap":"e50e98719ba5eedc6f5e617e0c7aa404ebfba15bc22a51e93e78cd4443bf787b",
 "Gentoo":"53fe3821f313ed35840376fcf4d11c8e0e8fbbd63f01ba84a5e21c2db4df6d6b"}
def read(path):
 with Path(path).open(encoding="utf-8",newline="") as f:return list(csv.DictReader(f))
def val(v):
 try:
  x=float(v)
  return x if math.isfinite(x) else None
 except (ValueError,TypeError):return None
def mean(a):
 if not a:raise ValueError("empty array")
 return sum(a)/len(a)
def median(a):
 b=sorted(a);return b[len(b)//2] if len(b)%2 else .5*(b[len(b)//2-1]+b[len(b)//2])
def centered(x):
 m=mean(x);return [v-m for v in x]
def corr(x,y):
 if len(x)!=len(y) or len(x)<3:return None
 a,b=centered(x),centered(y)
 den=math.sqrt(sum(v*v for v in a)*sum(v*v for v in b))
 return sum(v*w for v,w in zip(a,b))/den if den>1e-12 else None
def residual(x,z):
 zz=centered(z);xx=centered(x)
 den=sum(t*t for t in zz)
 if den<1e-12:return None
 slope=sum(a*b for a,b in zip(xx,zz))/den
 return [a-slope*b for a,b in zip(xx,zz)]
def partial(x,y,z):
 a=residual(x,z);b=residual(y,z)
 return corr(a,b) if a is not None and b is not None else None
def yearslope_residual(x):
 return residual(x,list(range(len(x))))
def loo_range(x,y):
 a=[corr(x[:i]+x[i+1:],y[:i]+y[i+1:]) for i in range(len(x))]
 a=[v for v in a if v is not None]
 return [min(a),max(a)] if a else [None,None]
def exact_year_permutation(ice,stage):
 """Preserve cross-species association by permuting YEAR rows together.

 2 ice windows x 3 species, max-absolute-r correction within these 6
 exploratory comparisons only. No valid p without year exchangeability.
 """
 if len(ice)!=9 or len(stage)!=9:raise ValueError("exact 9 years expected")
 def standardized(x):
  a=centered(x);d=math.sqrt(sum(t*t for t in a))
  if d<1e-12:raise ValueError("zero variance")
  return [v/d for v in a]
 xx=[standardized([r[k] for r in ice]) for k in ICE]
 yy=[standardized([r[sp] for r in stage]) for sp in SPECIES]
 observed=[[sum(a*b for a,b in zip(x,y)) for y in yy] for x in xx]
 exceed=[[0]*3 for _ in range(2)];exceed_max=0;allmax=max(abs(v) for row in observed for v in row)
 total=0
 for p in itertools.permutations(range(9)):
  results=[[sum(x[t]*y[p[t]] for t in range(9)) for y in yy] for x in xx]
  for i in range(2):
   for j in range(3):
    exceed[i][j]+=abs(results[i][j])+1e-12>=abs(observed[i][j])
  exceed_max+=max(abs(v) for row in results for v in row)+1e-12>=allmax
  total+=1
 assert total==362880
 return {"n_exact_permutations":total,"observed_r":observed,
         "extreme_counts":exceed,"unadjusted_two_sided_fraction":[[v/total for v in row] for row in exceed],
         "joint_max_absolute_r_extreme_count":exceed_max,
         "joint_six_comparison_fraction":exceed_max/total,
         "null_assumption":"all nine annual observation vectors exchangeable; unverified",
         "family_scope":"three species x September/Aug-Nov SIC; other previous exploratory choices not corrected"}

def save(path,rows):
 if not rows:raise ValueError("No output rows")
 with Path(path).open("w",newline="",encoding="utf-8") as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def run(diet_dir,stage_dir,out):
 diet_dir,stage_dir,out=map(Path,(diet_dir,stage_dir,out))
 diet_gate=json.loads((diet_dir/"summary.json").read_text(encoding="utf-8"))
 stage_gate=json.loads((stage_dir/"source_gate.json").read_text(encoding="utf-8"))
 if diet_gate["original_summary_sha256"]!=DIET_SHA:raise ValueError("Diet source SHA drift")
 for sp in SPECIES:
  if stage_gate["raw_source"][sp]["selected_csv_sha256"]!=STAGE_SHA[sp]:
   raise ValueError("Stage source SHA drift "+sp)
 diet=read(diet_dir/"diet_species_breeding_season.csv")
 icepairs=read(diet_dir/"diet_pair_season_antecedent_sic.csv")
 stage=read(stage_dir/"species_annual_stage_summary.csv")
 stage_rows=read(stage_dir/"source_stage_site_seasons.csv")
 if len(diet)!=47 or len(stage)!=66 or len(icepairs)!=37:
  raise ValueError("Source species-season support drift")
 diet_index={(r["species"],int(r["season_start"])):r for r in diet}
 stage_index={(r["species"],int(r["season_start"])):r for r in stage}
 if len(diet_index)!=len(diet) or len(stage_index)!=len(stage):raise ValueError("Duplicate species-season")
 ice_index={(r["pair"],int(r["breeding_season_start"])):r for r in icepairs}
 if len(ice_index)!=len(icepairs):raise ValueError("Duplicate paired ice season")
 fullcol=defaultdict(dict)
 for r in stage_rows:
  sp=r["species"];yr=int(r["season_start"]);col=r["colony"]
  if yr not in YEARS or sp not in ("Adelie","Chinstrap"):continue
  value=val(r["reported_chicks_per_pair"])
  if value is None:continue
  if col in fullcol[sp,yr]:raise ValueError("Duplicate strict stage colony")
  fullcol[sp,yr][col]=value
 fixed={}
 for sp in ("Adelie","Chinstrap"):
  fixed[sp]=set.intersection(*(set(fullcol[sp,y]) for y in YEARS))
  if len(fixed[sp])<3:raise ValueError("Too few persistent source colony labels")
 records=[];stage_vector=[];ice_vector=[]
 for year in YEARS:
  yr={"year":year};chicks={};source_pair=None
  for sp in SPECIES:
   key=sp,year
   if key not in diet_index or key not in stage_index:raise ValueError("Missing 3 species original overlapping years")
   dd= diet_index[key];st=stage_index[key]
   fish=val(dd["mean_stomach_fish_fraction"])
   chick=val(st["median_recorded_chicks_per_pair"])
   count=int(dd["n_valid_stomachs"])
   if fish is None or chick is None or not (0<=fish<=1) or chick<0 or count<3:
    raise ValueError("Invalid source measurements")
   yr[sp+"_fish"]=fish;yr[sp+"_chicks_per_pair"]=chick
   yr[sp+"_n_stomachs"]=count
   yr[sp+"_n_original_chick_units"]=int(st["observed_colonies"])
   yr[sp+"_spatial_unit"]=st["original_spatial_unit"]
   yr[sp+"_chicks_per_pair_fixed_roster"]=(median([fullcol[sp,year][k] for k in sorted(fixed[sp])]) if sp in fixed else chick)
   yr[sp+"_recorded_fledglings_per_pair"]=val(st.get("median_recorded_fledglings_per_pair"))
   chicks[sp]=chick
  sics=[]
  for pair in ("Adelie-Chinstrap","Adelie-Gentoo","Chinstrap-Gentoo"):
   r=ice_index.get((pair,year))
   if r is None:raise ValueError("Missing original ice for species pair")
   sics.append([val(r["preceding_sep_sic_pct"]),val(r["preceding_aug_nov_sic_pct"])])
  if any(v is None for row in sics for v in row):raise ValueError("Missing sea ice")
  if max(abs(sics[i][k]-sics[0][k]) for i in range(3) for k in range(2))>1e-8:
   raise ValueError("Original species pair sea ice conflict")
  yr["sep_sic_pct"],yr["aug_nov_sic_pct"]=sics[0]
  records.append(yr);stage_vector.append(chicks);ice_vector.append({k:yr[k] for k in ICE})
 if any(sum(int(r[sp+"_n_stomachs"]) for r in records)!=n for sp,n in
    (("Adelie",349),("Chinstrap",350),("Gentoo",73))):
  raise ValueError("Original strict 9-year stomach count mismatch")
 if len(records)!=9:raise ValueError("Nine annual replicates required")
 exact=exact_year_permutation(ice_vector,stage_vector)
 metrics=[];fledgling_support={};stage_n9={}
 for sp in SPECIES:
  food=[r[sp+"_fish"] for r in records]
  chick=[r[sp+"_chicks_per_pair"] for r in records]
  fixedchick=[r[sp+"_chicks_per_pair_fixed_roster"] for r in records]
  fledgling=[r[sp+"_recorded_fledglings_per_pair"] for r in records]
  stage_n9[sp]=[r[sp+"_n_original_chick_units"] for r in records]
  fledgling_support[sp]=sum(v is not None for v in fledgling)
  for i,window in enumerate(ICE):
   x=[r[window] for r in records]
   rfood=corr(x,food);rchick=corr(x,chick)
   metrics.append(dict(species=sp,ice_window=window,n_years=len(records),
     n_fixed_colonies=len(fixed.get(sp,[])),
     n_fledgling_years=fledgling_support[sp],
     r_ice_fish=rfood,r_ice_recorded_chicks=rchick,
     r_ice_recorded_chicks_fixed_colonies=corr(x,fixedchick),
     r_fish_recorded_chicks=corr(food,chick),
     r_fish_recorded_chicks_partial_ice=partial(food,chick,x),
     r_ice_chicks_detrend_year=corr(yearslope_residual(x),yearslope_residual(chick)),
     r_delta_ice_delta_recorded_chicks=corr([x[j]-x[j-1] for j in range(1,9)],
                                            [chick[j]-chick[j-1] for j in range(1,9)]),
     r_ice_fledglings_when_full=corr(x,fledgling) if fledgling_support[sp]==9 else None,
     loo_ice_chicks_min=loo_range(x,chick)[0],loo_ice_chicks_max=loo_range(x,chick)[1],
     exact_two_sided_year_permutation_fraction=exact["unadjusted_two_sided_fraction"][i][SPECIES.index(sp)],
     source_climate_independent_islands=1))
 out.mkdir(parents=True,exist_ok=True)
 save(out/"strict_nine_years_three_species.csv",records)
 save(out/"axis_relation_by_species_and_seaice_window.csv",metrics)
 result=dict(date="2026-11-03",status="exploratory_same_Signy_9_seasons_3species_ice_diet_chick_coanalysis",
   season_start_years=list(YEARS),n_temporal_replications=9,n_independent_geographic_islands=1,
   n_species=3,source_diet_SHA256=DIET_SHA,source_stage_SHA256=STAGE_SHA,
   original_stage_spatial_unit={"Adelie":"source_colony","Chinstrap":"source_colony",
                                "Gentoo":"island_aggregate_no_colony_field"},
   fixed_original_colony_label_count={sp:len(ids) for sp,ids in fixed.items()},
   fixed_label_stability_not_geospatially_verified=True,
   n_fledgling_ratio_years=fledgling_support,
   stage_units_per_year=stage_n9,
   exact_joint_9_year_permutations=exact,
   metrics=metrics,
   limits=["Diet sampled during chick rearing: individual nesting pairs are not matched to stomach samples",
     "Original recorded chicks per breeding pair is not survival or recruitment",
     "Adelie/Chinstrap colony median vs Gentoo island aggregate prevents causal species-pair fitness comparisons",
     "Persistent colony LABELS are not verified immutable GIS nesting patches",
     "Observational years may be temporally autocorrelated; full permutation p values are illustrative",
     "All environment windows and outcomes are posthoc exploratory and six-test correction covers only this family",
     "Partials cannot identify a direct path from food to chick output",
     "No validation for CMIP6 food, reproduction, population or competition forecasts"])
 (out/"summary.json").write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
 return result
if __name__=="__main__":
 p=argparse.ArgumentParser()
 p.add_argument("--diet-dir",type=Path,required=True);p.add_argument("--stage-dir",type=Path,required=True)
 p.add_argument("--out",type=Path,required=True)
 a=p.parse_args()
 z=run(a.diet_dir,a.stage_dir,a.out)
 print(json.dumps({"source_years":z["n_temporal_replications"],
   "fixed_colonies":z["fixed_original_colony_label_count"],
   "joint_six":z["exact_joint_9_year_permutations"]["joint_six_comparison_fraction"],
   "recorded_fledgling_years":z["n_fledgling_ratio_years"]},ensure_ascii=False,indent=2))
