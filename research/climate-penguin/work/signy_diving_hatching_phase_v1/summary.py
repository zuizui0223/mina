"""Signy dive-associated original GPS vs GPS-only, conditional on published hatch phase.

Runs from pinned source-derived CI artifacts; one climate island, two seasons,
one season (2015) with both sides of chinstrap hatching actually sampled.
Means are not tagged-bird nest stages, diving pressure is provisional.
"""
import argparse,csv,datetime as dt,hashlib,json,statistics
from collections import defaultdict
from pathlib import Path
HASH={
 "dive":"4b3c09b76baebfd0dfd12ae3fd8bebb41ed2ae4f95c7412548783e4a2b8dd528",
 "gps":"e081cc2912f559f703b6bbc5c27e1473e096eb6c342aa819e62ca15dd92c126e",
 "hatch":"357c05a64c35b963ab3161cf3d5a43c47b87ddb6e5e27c1d9bd72ce282be03a8"}
def load(p,kind):
 b=Path(p).read_bytes()
 if hashlib.sha256(b).hexdigest()!=HASH[kind]:raise ValueError("SHA receipt changed "+kind)
 return list(csv.DictReader(b.decode("utf-8-sig").splitlines()))
def period(d,a,c):
 return "pre-Adelie" if d<a else "between-hatching" if d<c else "post-Chinstrap"
def med(x):return statistics.median(x)
def save(p,a):
 with Path(p).open("w",newline="",encoding="utf8") as f:
  if not a:raise ValueError("No rows")
  w=csv.DictWriter(f,fieldnames=list(a[0]));w.writeheader();w.writerows(a)
def run(dive,gps,hatch,out):
 D=load(dive,"dive");G=load(gps,"gps");H=load(hatch,"hatch")
 if (len(D),len(G),len(H))!=(693,1121,34):raise ValueError("Derived original source lengths drifted")
 dates={(int(r["year"]),r["species"]):dt.date.fromisoformat(r["hatching_calendar_date"]) for r in H}
 if len(dates)!=34:raise ValueError("Source hatching duplicate key")
 gpsindex={(int(r["season_start"]),r["GPS_hour"][:13]):r for r in G}
 if len(gpsindex)!=len(G):raise ValueError("Original GPS hour duplicate")
 seen=set();days=defaultdict(list);nstrict=0
 for r in D:
  year=int(r["year"]);hour=r["original_GPS_clock_hour"][:13]
  if (year,hour) in seen:raise ValueError("Candidate source duplicate hour")
  seen.add((year,hour))
  strict=min(int(r["n_Adelie_source_tags_with_TDR_candidate"]),int(r["n_Chinstrap_source_tags_with_TDR_candidate"]))>=2
  if not strict:continue
  nstrict+=1
  day=dt.date.fromisoformat(r["original_GPS_clock_hour"][:10])
  phase=period(day,dates[year,"Adelie"],dates[year,"Chinstrap"])
  ref=gpsindex.get((year,hour))
  days[year,day.isoformat(),phase].append((float(r["Chinstrap_minus_Adelie_radial_diff_km"]),
     float(ref["median_GPS_radial_difference_chin_minus_adelie_km"]) if ref else None))
 if nstrict!=171:raise ValueError("Strict 171 source-hour support drifted")
 daily=[]
 for (year,date,phase),vals in sorted(days.items()):
  valid=[(a,b) for a,b in vals if b is not None]
  if not valid:raise ValueError("No GPS baseline on strict day")
  daily.append(dict(year=year,date=date,phase=phase,n_strict_dive_source_hours=len(vals),
   n_same_hour_original_GPS_controls=len(valid),
   dive_candidate_median_radial_diff_km=med([a for a,b in vals]),
   GPS_only_same_hour_median_radial_diff_km=med([b for a,b in valid]),
   n_chinstrap_farther_hours=sum(a>0 for a,b in vals)))
 groups=defaultdict(list)
 for r in daily:groups[r["year"],r["phase"]].append(r)
 stage=[]
 for (year,phase),rr in sorted(groups.items()):
  stage.append(dict(year=year,phase=phase,Adelie_mean_hatch=dates[year,"Adelie"].isoformat(),
    Chinstrap_mean_hatch=dates[year,"Chinstrap"].isoformat(),
    n_source_days=len(rr),n_source_hours=sum(r["n_strict_dive_source_hours"] for r in rr),
    n_source_hours_with_GPS_control=sum(r["n_same_hour_original_GPS_controls"] for r in rr),
    median_equal_days_dive_candidate_km=med([r["dive_candidate_median_radial_diff_km"] for r in rr]),
    median_equal_days_GPS_only_same_hour_km=med([r["GPS_only_same_hour_median_radial_diff_km"] for r in rr]),
    n_days_chinstrap_farther=sum(r["dive_candidate_median_radial_diff_km"]>0 for r in rr)))
 expected={(2013,"between-hatching"):(5,39.699549445987955,42.619472780813226),
 (2015,"between-hatching"):(7,13.82508426347227,3.8604336848523317),
 (2015,"post-Chinstrap"):(7,-29.981148912377094,-27.367668819764138)}
 if set((r["year"],r["phase"]) for r in stage)!=set(expected):raise ValueError("Source stage phase coverage changed")
 for r in stage:
  n,div,base=expected[r["year"],r["phase"]]
  if r["n_source_days"]!=n or abs(r["median_equal_days_dive_candidate_km"]-div)>1e-8 or abs(r["median_equal_days_GPS_only_same_hour_km"]-base)>1e-8:
   raise ValueError("Real source stage/day receipt drift")
 out=Path(out);out.mkdir(parents=True,exist_ok=True)
 save(out/"source_clock_hour_strict_daily.csv",daily)
 save(out/"source_hatching_phase_annual_summary.csv",stage)
 result=dict(date="2026-11-05",status="verified_original_Clewlow2019_leapfrog_hatching_phase_source_reanalysis",
   original_source_derived_input_SHA256=HASH,
   source_original_run_ids={"dive":41922844790,"gps":41730811560,"hatching":41590421785},
   original_full_78_dive_source_hours=len(D),strict_2plus_tags_each_hour_bins=nstrict,
   strictly_source_matched_days=len(daily),source_hatching_phase=stage,
   n_seasons_with_both_sides_of_Chinstrap_hatch=1,all_data_one_island_and_two_seasons=True,
   cannot_conclude_climate_causality=True,source_pressure_5dbar_candidate_not_verified_prey=True,
   prior_art="Clewlow et al 2019 DOI 10.1111/1365-2656.12919 reported leapfrog foraging at Signy",
   limitations=["GPS-only comparator retains exact original clock hours but not necessarily identical birds",
   "Source pressure uses unvalidated 1st percentile/60min baseline; no captured fish or krill",
   "Mean hatching data derive from different nests, not source GPS-tagged bird hatching",
   "One original 2013 strict period only before Chinstrap mean hatching, so no independent 2013 sign-reversal test",
   "Year 2015 7 before/7 after days are temporally ordered and nonrandom; no causal/p-value claim",
   "Repeated GPS/TDR tag hours are not independent days, years, sites or climate replicates",
   "No numerical future penguin population or niche projection from CMIP6"])
 (out/"summary.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
 print(json.dumps({"strict_hours":nstrict,"stage":stage},ensure_ascii=False))
 return result
if __name__=="__main__":
 p=argparse.ArgumentParser()
 for key in ("dive","gps","hatch","out"):p.add_argument("--"+key,required=True,type=Path)
 a=p.parse_args();run(a.dive,a.gps,a.hatch,a.out)
