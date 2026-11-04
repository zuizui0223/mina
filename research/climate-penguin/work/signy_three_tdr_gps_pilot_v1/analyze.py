"""Signy BAS original GPS matched to original per-bird TDR dive candidates.

This is a source-first, bounded pilot with no pressure-outcome-based tag choice:
choose up to 10 lexicographically first original GPS/TDR-identical IDs per
species x 2013/2015 among tags having >=10 source GPS hours at 10-150km.
For gentoo 2015 there is one potential tag; it cannot support species inference.

Publisher original TDR pressure requires unverified zero-offset correction.
GPS/TDR matching is timestamp only, no clock shifts fitted; pressure-defined
dives are candidates, NOT confirmed prey capture, foraging or krill consumption.
The same 2 species GPS dates/hours are previous results, not new climates.
"""
from __future__ import annotations
import argparse,csv,datetime as dt,hashlib,io,json,math,statistics,sys,zipfile
from pathlib import Path
from collections import defaultdict

REPO=Path(__file__).resolve().parents[4]
UTIL=REPO/"research/climate-penguin/work/climate_penguin"
sys.path.insert(0,str(UTIL))
sys.path.insert(0,str(REPO/"research/climate-penguin/work/signy_three_species_TDR_GPS_source_v1"))
import signy_gps_krill_access_v1 as gps
import chinstrap_tdr_pressure_gps_pilot_v1 as pilot
import audit as source_gate

SPECIES=("Adelie","Chinstrap","Gentoo")
YEARS=(2013,2015)
MAX_PER_SPECIES_YEAR=10
CUTS=(2.,5.,10.)
MIN_RADIUS_KM=(0.,2.,5.,10.,20.)
MAX_RADIUS_KM=150.
MAIN_CUTOFF=5.
MAIN_MIN_RADIUS_KM=2.

def csvwrite(path,rows,fields):
 with Path(path).open("w",newline="",encoding="utf-8") as f:
  wr=csv.DictWriter(f,fieldnames=fields)
  wr.writeheader()
  for r in rows:wr.writerow({k:r.get(k,"") for k in fields})
def time_hour(t):
 return dt.datetime.fromtimestamp(float(t),dt.timezone.utc).strftime("%Y-%m-%dT%H:00Z")
def sep_km(a,b):
 la,lo=a;lb,ln=b
 h=math.sin(math.radians(lb-la)/2)**2+math.cos(math.radians(la))*math.cos(math.radians(lb))*math.sin(math.radians(ln-lo)/2)**2
 return 12742.0176*math.asin(min(1,math.sqrt(max(0,h))))
def jaccard(a,b):
 u=a|b
 return len(a&b)/len(u) if u else None
def median(x):return statistics.median(x)
def percentile(x,p):
 a=sorted(x)
 if not a:return None
 f=(len(a)-1)*p
 i=int(f);d=f-i
 return a[i]*(1-d)+a[min(i+1,len(a)-1)]*d
def site_cells(a,step):
 return {(math.floor(z["lat"]/step),math.floor(z["lon"]/step)) for z in a}
def read_pressure(z,member):
 with z.open(member) as original:
  table=csv.DictReader(io.TextIOWrapper(original,encoding="utf-8-sig",newline=""))
  cols=set(table.fieldnames or [])
  if not {"DateTime","Pressure [dBars]"}.issubset(cols):
   raise ValueError("Publisher TDR source schema changed "+member+" "+str(cols))
  raw=[]
  for i,row in enumerate(table):
   if i>2_000_000:raise ValueError("Exceeded original per-TDR file safety count "+member)
   t=dt.datetime.fromisoformat(row["DateTime"].replace("Z","+00:00"))
   try:pressure=float(row["Pressure [dBars]"])
   except (ValueError,TypeError):pressure=float("nan")
   raw.append((t,pressure))
 return raw
def select_source_tags(root,max_source_tags_per_species_year=MAX_PER_SPECIES_YEAR):
 if max_source_tags_per_species_year<1:raise ValueError("Source tag cap must be >=1")
 tracks,verified=gps.read_tracks(root/"gps")
 if verified["canonical_member_content_sha256"]!=gps.TRACK_SHA:
  raise ValueError("Original 3-species BAS GPS data source SHA drift")
 tdr_rosters={}
 for sp in SPECIES:
  source=source_gate.SRC[sp]
  roster=source_gate.source_track_roster(root/"tdr"/(sp.lower()+".zip"),source["prefix"],"TDR")
  tdr_rosters[sp]={r["id"]:r for r in roster if r["header_ok"] and not r["empty_or_short"]}
 trackroster=defaultdict(list)
 allsource=defaultdict(list)
 for track in tracks:
  sp=track["species"];year=track["season"]
  if sp not in SPECIES or year not in YEARS:continue
  allsource[sp,year].append(track)
  if track["deployment"] not in tdr_rosters[sp]:continue
  arr=track["points"]
  if len(arr)<10:continue
  spikes=gps.singleton_spike_mask(arr)
  km=gps.geodesic([z[1] for z in arr],[z[2] for z in arr])
  eligible=[z for i,z in enumerate(arr) if not spikes[i] and 10<=km[i]<=150]
  hourly=gps.selected_hourly(eligible)
  if len(hourly)<10:continue
  trackroster[sp,year].append(track)
 selections={}
 for sp in SPECIES:
  for year in YEARS:
   selected=sorted(trackroster[sp,year],key=lambda t:t["deployment"])[:max_source_tags_per_species_year]
   selections[sp,year]=selected
 if not all(selections["Adelie",y] and selections["Chinstrap",y] for y in YEARS):
  raise ValueError("No two-species GPS/TDR original source-eligible tracks")
 return tracks,tdr_rosters,allsource,trackroster,selections,verified
def run(root,out,max_source_tags_per_species_year=MAX_PER_SPECIES_YEAR):
 root,out=map(Path,(root,out))
 tracks,rosters,allsource,trackroster,selections,gpsreceipt=select_source_tags(root,max_source_tags_per_species_year)
 selected=defaultdict(list)
 tracking=[];attempts=[];all_events=[]
 byspecies_hour=defaultdict(list)
 for sp in SPECIES:
  with zipfile.ZipFile(root/"tdr"/(sp.lower()+".zip")) as z:
   for year in YEARS:
    source=allsource[sp,year]
    okay=trackroster[sp,year]
    chosen=selections[sp,year]
    tracking.append(dict(species=sp,season_start=year,
       n_original_deployments_in_GPS_archive=len(source),
       n_matched_original_GPS_TDR_source_eligible=len(okay),
       n_fixed_lexicographic_selected=len(chosen),
       n_source_TDR_members_with_schema_valid=len(rosters[sp])))
    for track in chosen:
     native=track["deployment"]
     tdr=rosters[sp][native]
     row=dict(species=sp,season_start=year,original_tag=native,
       original_source_TDR_member=tdr["member"],original_TDR_crc32=tdr["crc32"],
       n_original_GPS_source_fixes=len(track["points"]))
     raw=read_pressure(z,tdr["member"])
     row["n_original_TDR_rows"]=len(raw)
     try:
      _,times,pressure,dupe,nonfinite=pilot.get_clean_pressure(raw)
      corrected,cal=pilot.hour_offset(times,pressure)
     except ValueError as err:
      row["measurement_qa_status"]="NO_CALIBRATION_OR_SUPPORT"
      row["reason"]=str(err)[:240]
      attempts.append(row)
      continue
     row["measurement_qa_status"]="PROVISIONAL_CORRECTION"
     row["reason"]=""
     row["n_duplicate_pressure_times"]=dupe
     row["n_nonfinite_pressure"]=nonfinite
     row["hourly_p01_drift_range_dbar"]=cal["surface_q01_drift_range_dbar"]
     row["drift_over_2_dbar"]=cal["surface_q01_drift_range_dbar"]>2.
     original_fix=[(p[0],p[1],p[2]) for p in track["points"]]
     for cut in CUTS:
      event=pilot.dive_candidates(times,corrected,cut)
      paired,check=pilot.gps_time_brackets(event,original_fix)
      row[f"n_events_at_{int(cut)}dbar"]=len(event)
      row[f"n_events_GPS_time_bracket_{int(cut)}dbar"]=len(paired)
      if cut!=MAIN_CUTOFF:continue
      row["n_GPS_bracket_eligible_main"]=len(paired)
      row["median_nearest_original_GPS_timedelta_seconds"]=(
        median([q["original_GPS_time_offset_seconds"] for q in paired]) if paired else None)
      sub=[]
      for ev in paired:
       lat=ev["nearest_original_GPS_lat"];lon=ev["nearest_original_GPS_lon"]
       radial=float(gps.geodesic([lat],[lon])[0])
       for radius in MIN_RADIUS_KM:
        if radius<=radial<=MAX_RADIUS_KM:
         row[f"n_GPS_bracket_events_radial_{int(radius)}_{int(MAX_RADIUS_KM)}km"]=(
           row.get(f"n_GPS_bracket_events_radial_{int(radius)}_{int(MAX_RADIUS_KM)}km",0)+1)
       if MAIN_MIN_RADIUS_KM<=radial<=MAX_RADIUS_KM:
        sub.append(dict(species=sp,year=year,tag=native,
          peak_clock_hour=time_hour(ev["peak_timestamp"]),radial_km=radial,
          lat=float(lat),lon=float(lon),
          original_GPS_time_offset_seconds=ev["original_GPS_time_offset_seconds"],
          provisional_dive_peak_dbar=ev["peak_corrected_pressure_dbar"]))
      hours=defaultdict(list)
      for q in sub:hours[q["peak_clock_hour"]].append(q)
      for h,samples in sorted(hours.items()):
       # Exactly one ORIGINAL nearest-GPS position per source tag x clock hour.
       # Choose the middle source event by radial distance, not a fake centroid.
       s=sorted(samples,key=lambda q:q["radial_km"])
       chosen_sample=s[(len(s)-1)//2]
       byspecies_hour[sp,year,h].append(chosen_sample)
       all_events.append(chosen_sample)
      row["n_unique_source_diving_GPS_hours_main"]=len(hours)
      row["n_main_radial_2_150km_candidate_events"]=len(sub)
      row["original_GPS_bracket_definition"]="both actual source fixes span <=600s, nearest <=300s"
      row["dive_definition"]="provisional hour-q1 baseline, >=5dbar for >=10sec, <=3sec pressure gaps"
     attempts.append(row)
 # Aggregate by *same* source clock hour and year, one actual matched GPS location/tag/hour.
 perhour=[]
 for year in YEARS:
  ah={h for sp,y,h in byspecies_hour if sp=="Adelie" and y==year}
  ch={h for sp,y,h in byspecies_hour if sp=="Chinstrap" and y==year}
  for h in sorted(ah&ch):
   a=byspecies_hour["Adelie",year,h]
   c=byspecies_hour["Chinstrap",year,h]
   if any(len(vals)!=len({v["tag"] for v in vals}) for vals in (a,c)):
    raise ValueError("same-tag-hour dive candidate pseudo repetition")
   row=dict(year=year,original_GPS_clock_hour=h,
       n_Adelie_source_tags_with_TDR_candidate=len(a),
       n_Chinstrap_source_tags_with_TDR_candidate=len(c),
       Adelie_median_radial_km=median([x["radial_km"] for x in a]),
       Chinstrap_median_radial_km=median([x["radial_km"] for x in c]),
       Chinstrap_minus_Adelie_radial_diff_km=median([x["radial_km"] for x in c])-median([x["radial_km"] for x in a]),
       source_0p1deg_candidate_GPS_cell_jaccard=jaccard(site_cells(a,.1),site_cells(c,.1)),
       source_0p2deg_candidate_GPS_cell_jaccard=jaccard(site_cells(a,.2),site_cells(c,.2)),
       n_verified_prey_captures=0,no_real_dive_confirmation=True)
   perhour.append(row)
 by_day=defaultdict(list)
 for r in perhour:by_day[r["year"],r["original_GPS_clock_hour"][:10]].append(r)
 perday=[]
 for (year,day),hours in sorted(by_day.items()):
  aa={v["tag"] for h in hours for v in byspecies_hour["Adelie",year,h["original_GPS_clock_hour"]]}
  cc={v["tag"] for h in hours for v in byspecies_hour["Chinstrap",year,h["original_GPS_clock_hour"]]}
  perday.append(dict(year=year,source_calendar_day_UTC_or_publisher_clock=day,
    n_both_species_source_candidate_dive_GPS_hours=len(hours),
    n_Adelie_original_TDR_deployments=len(aa),n_Chinstrap_original_TDR_deployments=len(cc),
    minimum_two_source_tags_each=len(aa)>=2 and len(cc)>=2,
    median_same_hour_radial_diff_chinstrap_minus_adelie_km=median([h["Chinstrap_minus_Adelie_radial_diff_km"] for h in hours]),
    median_same_hour_GPS_cell_jaccard_0p1degree=median([h["source_0p1deg_candidate_GPS_cell_jaccard"] for h in hours])))
 summary=[]
 for y in YEARS:
  ta=[r for r in attempts if r["species"]=="Adelie" and r["season_start"]==y]
  tc=[r for r in attempts if r["species"]=="Chinstrap" and r["season_start"]==y]
  found=[r for r in perday if r["year"]==y]
  good=[r for r in found if r["minimum_two_source_tags_each"]]
  hours=[r for r in perhour if r["year"]==y]
  summary.append(dict(season_start=y,
    n_Adelie_original_source_tags_selected=len(ta),
    n_Chinstrap_original_source_tags_selected=len(tc),
    n_Gentoo_original_source_tags_selected=sum(r["species"]=="Gentoo" and r["season_start"]==y for r in attempts),
    n_Adelie_source_tags_with_pressure_ZOC=sum(r["measurement_qa_status"]=="PROVISIONAL_CORRECTION" for r in ta),
    n_Chinstrap_source_tags_with_pressure_ZOC=sum(r["measurement_qa_status"]=="PROVISIONAL_CORRECTION" for r in tc),
    n_original_same_clock_hour_A_C_TDR_candidate_GPS_locations=len(hours),
    n_original_same_calendar_days_with_both_candidate_dive_locations=len(found),
    n_same_day_with_min_two_GPS_TDR_tags_per_species=len(good),
    median_same_hour_observed_dive_candidate_radial_diff_km=median([r["Chinstrap_minus_Adelie_radial_diff_km"] for r in hours]) if hours else None,
    median_daily_radial_diff_if_two_tags_each=median([r["median_same_hour_radial_diff_chinstrap_minus_adelie_km"] for r in good]) if good else None,
    n_original_sensor_UTC_sync_independently_verified=0,
    inference_unit="two breeding seasons, one island, original tags/days/hours nested, not independent years"))
 out.mkdir(parents=True,exist_ok=True)
 fields=["species","season_start","original_tag","original_source_TDR_member","original_TDR_crc32",
         "n_original_GPS_source_fixes","n_original_TDR_rows","measurement_qa_status","reason",
         "n_duplicate_pressure_times","n_nonfinite_pressure","hourly_p01_drift_range_dbar","drift_over_2_dbar"]+[
          f"n_events_at_{v}dbar" for v in (2,5,10)]+[
          f"n_events_GPS_time_bracket_{v}dbar" for v in (2,5,10)]+[
          "n_GPS_bracket_eligible_main","median_nearest_original_GPS_timedelta_seconds"]+[
          f"n_GPS_bracket_events_radial_{int(r)}_150km" for r in MIN_RADIUS_KM]+[
          "n_unique_source_diving_GPS_hours_main","n_main_radial_2_150km_candidate_events",
          "original_GPS_bracket_definition","dive_definition"]
 csvwrite(out/"original_source_tag_TDR_GPS_QA.csv",attempts,fields)
 csvwrite(out/"source_year_TDR_GPS_support.csv",tracking,list(tracking[0]))
 csvwrite(out/"same_clock_hour_A_C_candidate_dive_GPS_support.csv",perhour,
  ["year","original_GPS_clock_hour","n_Adelie_source_tags_with_TDR_candidate",
   "n_Chinstrap_source_tags_with_TDR_candidate",
   "Adelie_median_radial_km","Chinstrap_median_radial_km",
   "Chinstrap_minus_Adelie_radial_diff_km",
   "source_0p1deg_candidate_GPS_cell_jaccard",
   "source_0p2deg_candidate_GPS_cell_jaccard",
   "n_verified_prey_captures","no_real_dive_confirmation"])
 csvwrite(out/"same_day_A_C_candidate_dive_GPS_support.csv",perday,
  ["year","source_calendar_day_UTC_or_publisher_clock","n_both_species_source_candidate_dive_GPS_hours",
   "n_Adelie_original_TDR_deployments","n_Chinstrap_original_TDR_deployments",
   "minimum_two_source_tags_each","median_same_hour_radial_diff_chinstrap_minus_adelie_km",
   "median_same_hour_GPS_cell_jaccard_0p1degree"])
 csvwrite(out/"by_year_summary.csv",summary,list(summary[0]))
 total=dict(date="2026-11-05",status="predeclared_source_tag_pilot_pressure_derived_dive_GPS_locations_not_confirmed_prey",
  original_gps_three_species_SHA256=gpsreceipt["canonical_member_content_sha256"],
  original_TDR_zip_wrapper_sha256={sp:hashlib.sha256((root/"tdr"/(sp.lower()+".zip")).read_bytes()).hexdigest() for sp in SPECIES},
  source_tag_selection=("GPS qual >=10 hours in 10–150km, exact GPS/TDR deployment ID, "
      + ("ALL available source-matched tags" if max_source_tags_per_species_year>=999 else "lexicographic first up to "+str(max_source_tags_per_species_year)+" per species/year")
      + "; no selection using TDR dive outcomes"),
  max_source_tags_per_species_year=max_source_tags_per_species_year,
  all_source_eligible_tags_included=(max_source_tags_per_species_year>=999),
  n_original_source_eligible_tags=sum(len(v) for v in trackroster.values()),
  main_pressure_cutoff_dbar=MAIN_CUTOFF,main_min_radius_km=MAIN_MIN_RADIUS_KM,
  n_source_selected_tags=len(attempts),
  n_original_source_tags_with_sensor_calibration=sum(r["measurement_qa_status"]=="PROVISIONAL_CORRECTION" for r in attempts),
  n_original_source_tags_with_pressure_baseline_drift_over_2_dbar=sum(r.get("drift_over_2_dbar",False) for r in attempts),
  n_years=len(summary),by_year=summary,
  n_A_C_same_original_GPS_clock_hours_with_both_pressure_candidate_locations=len(perhour),
  n_A_C_same_day_with_both_pressure_candidate_locations=len(perday),
  n_A_C_same_day_at_least_two_tags_each=sum(r["minimum_two_source_tags_each"] for r in perday),
  all_GPS_gps_only_previous_exposure_not_rederived_here=True,
  limits=["Selection includes all original source-eligible GPS/TDR tags when cap>=999, else a capped source-first pilot; neither is a representative wildlife survey",
   "Existing published Signy GPS/TDR leapfrog foraging/sea-stage niche findings are prior art; no novelty claim for mere dive detection",
   "Hour-wise 1-percentile source pressure baseline is provisional; no independently known surface zero or validated depths",
   "No pressure-to-verified prey capture, no krill/fish prey observation, and some candidate dives may be travelling",
   "TDR and GPS clock shifts not verified with external synchronization; source clock was used unchanged",
   "Same source GPS fix nearest to TDR candidate peak within 300sec and bracket <=600sec: an inferred location, not direct underwater location",
   "Source common GPS hour 2013 vs 2015 comparison may have different GPS deployments/year and nonrandom tagging",
   "One Signy island, no causal warming/marine competition response and no CMIP6 future penguin biological forecast"])
 (out/"summary.json").write_text(json.dumps(total,indent=2,ensure_ascii=False)+"\n")
 print(json.dumps({k:total[k] for k in ("n_source_selected_tags","n_original_source_tags_with_sensor_calibration",
  "n_original_source_tags_with_pressure_baseline_drift_over_2_dbar",
  "n_A_C_same_original_GPS_clock_hours_with_both_pressure_candidate_locations",
  "n_A_C_same_day_with_both_pressure_candidate_locations","by_year")},ensure_ascii=False,indent=2))
 return total
if __name__=="__main__":
 p=argparse.ArgumentParser();p.add_argument("--source",type=Path,required=True)
 p.add_argument("--out",type=Path,required=True)
 p.add_argument("--max-source-tags-per-species-year",type=int,default=MAX_PER_SPECIES_YEAR)
 a=p.parse_args();run(a.source,a.out,a.max_source_tags_per_species_year)
