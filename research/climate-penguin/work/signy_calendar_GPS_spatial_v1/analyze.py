"""Strict SAME CLOCK HOUR/day GPS opportunity for two Signy penguin species.

Publisher original BAS Signy Adélie/Chinstrap/Gentoo GPS sources validated
by existing original 168-deployment/174127-position content checksum.
Compare two species observed within the SAME ORIGINAL GPS hour/day, not
separate sequential chick-stage stomach sampling dates. GPS points are
positions/transits, NOT validated foraging, krill intake, or niche competition.
"""
from __future__ import annotations
import argparse,csv,datetime as dt,importlib.util,json,math,statistics
from collections import defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
GPS_SCRIPT=ROOT/"research/climate-penguin/work/climate_penguin/signy_gps_krill_access_v1.py"
SPECIES=("Adelie","Chinstrap")
SOURCE_YEARS=(2011,2013,2015)
def module():
 spec=importlib.util.spec_from_file_location("verified_gps",GPS_SCRIPT)
 m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 return m
def hour_of(ts):
 if ts.tzinfo is not None:ts=ts.astimezone(dt.timezone.utc).replace(tzinfo=None)
 return ts.replace(minute=0,second=0,microsecond=0)
def gridded(s,step):
 return {(math.floor(r["lat"]/step),math.floor(r["lon"]/step)) for r in s}
def jaccard(a,b):
 union=a|b
 return len(a&b)/len(union) if union else None
def distance_km(a,b):
 lat1,lon1=a;lat2,lon2=b
 v=math.sin(math.radians(lat2-lat1)/2)**2+math.cos(math.radians(lat1))*math.cos(math.radians(lat2))*math.sin(math.radians(lon2-lon1)/2)**2
 return 12742.0176*math.asin(math.sqrt(min(1,max(0,v))))
def median(values):return statistics.median(values)
def average(values):return sum(values)/len(values)
def csvsave(path,rows,fields):
 with Path(path).open("w",newline="",encoding="utf-8") as f:
  w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
def run(root,out):
 original=module()
 tracks,receipt=original.read_tracks(root)
 if len(tracks)!=168:raise ValueError("Original BAS GPS coverage drift")
 if receipt["canonical_member_content_sha256"]!=original.TRACK_SHA:
  raise ValueError("Original GPS collection SHA drift")
 source=defaultdict(list)
 original_tracks_by_year=defaultdict(set)
 qualified_tracks_by_year=defaultdict(set)
 for tr in tracks:
  sp=tr["species"];year=tr["season"]
  if sp not in SPECIES:continue
  original_tracks_by_year[sp,year].add(tr["deployment"])
  points=tr["points"]
  if not points:continue
  spike=original.singleton_spike_mask(points)
  km=original.geodesic([r[1] for r in points],[r[2] for r in points])
  keep=[point for i,point in enumerate(points) if not spike[i] and 10<=km[i]<=150]
  chosen=original.selected_hourly(keep)
  if len(chosen)<10:continue
  qualified_tracks_by_year[sp,year].add(tr["deployment"])
  for time,lat,lon,_ in chosen:
   clock=hour_of(time)
   key=sp,year,clock.date()
   source[key].append(dict(tag=tr["deployment"],lat=float(lat),lon=float(lon),
                          h=clock.isoformat(),km=float(original.geodesic([lat],[lon])[0])))
 years=sorted(set(y for sp,y in original_tracks_by_year if sp=="Adelie")&
              set(y for sp,y in original_tracks_by_year if sp=="Chinstrap"))
 if tuple(years)!=SOURCE_YEARS:raise ValueError("Original GPS two-species seasons changed")
 dayrows=[];hourrows=[];summaryrows=[]
 for year in years:
  all_days=sorted(set(day for (sp,y,day) in source if y==year))
  species_a_days={day for (sp,y,day) in source if y==year and sp=="Adelie"}
  species_b_days={day for (sp,y,day) in source if y==year and sp=="Chinstrap"}
  common_dates=sorted(species_a_days&species_b_days)
  days2tags=0
  for day in common_dates:
   a=source["Adelie",year,day];b=source["Chinstrap",year,day]
   ta={r["tag"] for r in a};tb={r["tag"] for r in b}
   if len(ta)>=2 and len(tb)>=2:days2tags+=1
   ha={r["h"] for r in a};hb={r["h"] for r in b}
   shared=sorted(ha&hb)
   for hour in shared:
    aa=[v for v in a if v["h"]==hour];bb=[v for v in b if v["h"]==hour]
    pos_a=(average([v["lat"] for v in aa]),average([v["lon"] for v in aa]))
    pos_b=(average([v["lat"] for v in bb]),average([v["lon"] for v in bb]))
    hourrows.append(dict(season_start=year,date=day.isoformat(),GPS_hour=hour,
      n_adelie_original_deployments=len({r["tag"] for r in aa}),
      n_chinstrap_original_deployments=len({r["tag"] for r in bb}),
      Adelie_median_original_GPS_km_from_fixed_anchor=median([r["km"] for r in aa]),
      Chinstrap_median_original_GPS_km_from_fixed_anchor=median([r["km"] for r in bb]),
      median_GPS_radial_difference_chin_minus_adelie_km=median([r["km"] for r in bb])-median([r["km"] for r in aa]),
      observed_hour_species_centroid_distance_km=distance_km(pos_a,pos_b),
      actual_ocean_foraging_event_confirmed=False))
   rec=dict(season_start=year,date=day.isoformat(),source_Adelie_hourly_positions=len(a),
     source_Chinstrap_hourly_positions=len(b),n_Adelie_original_deployments=len(ta),
     n_Chinstrap_original_deployments=len(tb),n_GPS_clock_hours_with_both_species=len(shared),
     original_Adelie_median_km=median([r["km"] for r in a]),
     original_Chinstrap_median_km=median([r["km"] for r in b]),
     median_GPS_radial_difference_chin_minus_adelie_km=
       median([r["km"] for r in b])-median([r["km"] for r in a]),
     GPS_0p1deg_cell_jaccard=jaccard(gridded(a,.1),gridded(b,.1)),
     GPS_0p2deg_cell_jaccard=jaccard(gridded(a,.2),gridded(b,.2)),
     species_same_GPS_hour_at_least_once=len(shared)>0,
     original_GPS_10_150km_hourly_filter_no_dive_validation=True)
   dayrows.append(rec)
  these_days=[r for r in dayrows if r["season_start"]==year]
  these_hours=[r for r in hourrows if r["season_start"]==year]
  strict_days=[r for r in these_days if r["n_Adelie_original_deployments"]>=2 and r["n_Chinstrap_original_deployments"]>=2]
  strict_radial=sorted(r["median_GPS_radial_difference_chin_minus_adelie_km"] for r in strict_days)
  def empirical_quantile(a,p):
   if not a:return None
   z=(len(a)-1)*p;i=int(z);w=z-i
   return a[i]*(1-w)+a[min(i+1,len(a)-1)]*w
  summaryrows.append(dict(season_start=year,
    n_original_Adelie_deployments=len(original_tracks_by_year["Adelie",year]),
    n_original_Chinstrap_deployments=len(original_tracks_by_year["Chinstrap",year]),
    n_qualified_Adelie_deployments=len(qualified_tracks_by_year["Adelie",year]),
    n_qualified_Chinstrap_deployments=len(qualified_tracks_by_year["Chinstrap",year]),
    n_days_Adelie_hourly_GPS=len(species_a_days),n_days_Chinstrap_hourly_GPS=len(species_b_days),
    n_calendar_days_with_both_species_GPS=len(these_days),
    n_both_species_same_clock_hour_bins=len(these_hours),
    n_joint_days_with_at_least_2_deployments_each=days2tags,
    n_joint_hours_at_least_2_deployments_each=sum(
      z["n_adelie_original_deployments"]>=2 and z["n_chinstrap_original_deployments"]>=2 for z in these_hours),
    n_joint_days_with_0p1deg_observed_cell_overlap=sum(r["GPS_0p1deg_cell_jaccard"]>0 for r in these_days),
    n_strict_2plus_tag_joint_days_with_Chinstrap_farther_than_Adelie=sum(
      r["median_GPS_radial_difference_chin_minus_adelie_km"]>0 for r in strict_days),
    strict_2plus_tag_joint_day_median_Chinstrap_minus_Adelie_km=median(strict_radial) if strict_radial else None,
    strict_2plus_tag_joint_day_radial_Q25_km=empirical_quantile(strict_radial,.25),
    strict_2plus_tag_joint_day_radial_Q75_km=empirical_quantile(strict_radial,.75),
    strict_2plus_tag_joint_day_median_0p1deg_cell_jaccard=median(
      [r["GPS_0p1deg_cell_jaccard"] for r in strict_days]) if strict_days else None,
    equal_joint_day_median_species_radial_difference_km=
      median([r["median_GPS_radial_difference_chin_minus_adelie_km"] for r in these_days])
      if these_days else None,
    equal_joint_hour_median_species_centroid_separation_km=
      median([r["observed_hour_species_centroid_distance_km"] for r in these_hours])
      if these_hours else None))
 if len(summaryrows)!=3:raise ValueError("Expected 3 observed physical GPS breeding seasons")
 out=Path(out);out.mkdir(parents=True,exist_ok=True)
 csvsave(out/"gps_two_species_by_season.csv",summaryrows,list(summaryrows[0]))
 fieldsday=["season_start","date","source_Adelie_hourly_positions","source_Chinstrap_hourly_positions",
   "n_Adelie_original_deployments","n_Chinstrap_original_deployments",
   "n_GPS_clock_hours_with_both_species","original_Adelie_median_km","original_Chinstrap_median_km",
   "median_GPS_radial_difference_chin_minus_adelie_km",
   "GPS_0p1deg_cell_jaccard","GPS_0p2deg_cell_jaccard",
   "species_same_GPS_hour_at_least_once","original_GPS_10_150km_hourly_filter_no_dive_validation"]
 csvsave(out/"original_GPS_same_calendar_day_species_pairs.csv",dayrows,fieldsday)
 fieldshour=["season_start","date","GPS_hour","n_adelie_original_deployments",
   "n_chinstrap_original_deployments",
   "Adelie_median_original_GPS_km_from_fixed_anchor",
   "Chinstrap_median_original_GPS_km_from_fixed_anchor",
   "median_GPS_radial_difference_chin_minus_adelie_km",
   "observed_hour_species_centroid_distance_km","actual_ocean_foraging_event_confirmed"]
 csvsave(out/"original_GPS_same_clock_hour_species_pairs.csv",hourrows,fieldshour)
 result=dict(date="2026-11-04",
  status="original_BAS_two_species_source_clock_hour_GPS_spatial_support_not_prey_overlap",
  original_168_deployment_source_SHA=receipt["canonical_member_content_sha256"],
  n_original_tracking_deployments=len(tracks),
  n_shared_source_seasons=len(years),original_source_shared_years=years,
  year_summary=summaryrows,
  same_calendar_day_count=len(dayrows),same_GPS_clock_hour_bin_count=len(hourrows),
  original_source_dates_timezones="Original recorded timestamp ISO; aware values normalized to UTC, naive values treated as native source clock. Verify original timezone metadata before absolute-time ecological claims.",
  limitations=["One source GPS position per tag per source hour to reduce 1-sec/3-min fix frequency imbalance",
    "Same GPS clock-hour bin is concurrent LOCATION observation, not confirmed prey capture or competition",
    "Most tags may be at different clock hours, calendar years and chick stages; no causal climate inference",
    "Offshore-distance 10–150 km around Signy anchor is NOT an actual ocean-land raster mask",
    "Satellite GPS points include movement and transits; no TDR matched diving and no krill biomass measured here",
    "Grid Jaccard depends on arbitrary 0.1/0.2 deg scale, sampling effort, ocean accessibility, and geography",
    "Fixed Signy anchor and GPS spike filter inherited from already SHA-checked earlier audit",
    "Individual deployments are nested within single island/year, NOT independent environmental years",
    "GPS source years only 2011,2013,2015 with both species; not 14-year stomach sampling timeline",
    "This checks empirical same-time GPS observability, not diet at identical dates or field-level prey segregation"])
 (out/"summary.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 print(json.dumps({"n_original_source_tracks":len(tracks),
  "years":years,"same_calendar_days":len(dayrows),
  "same_clock_hours":len(hourrows),"year_summary":summaryrows},
  ensure_ascii=False,indent=2))
 return result
if __name__=="__main__":
 p=argparse.ArgumentParser()
 p.add_argument("--gps-root",required=True,type=Path)
 p.add_argument("--out",required=True,type=Path)
 a=p.parse_args();run(a.gps_root,a.out)
