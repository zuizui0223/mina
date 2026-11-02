#!/usr/bin/env python3
"""Recompute actual 2017–2024 emperor breeding-group mobility from UK PDC MultiPoint source.

Each original shapefile record = dated satellite observation; may contain MULTIPLE
group positions. Seasonal movement is measured for mapped centroid(s), not
individual penguins or breeding population. Controls sensor/season support.
"""
from collections import Counter,defaultdict
from datetime import date
import csv,hashlib,json,math,runpy,zipfile
from pathlib import Path
from probe import OUT,ID
source_parser=runpy.run_path(str(Path(__file__).with_name("inspect.py")))
read_dbf=source_parser["dbf_read"]
read_shp=source_parser["shape_read"]
PIN_CANONICAL_SHA256="e697c1f76056d5e77646d1bfcf484ffe64e00685a1913964ca753d7094f4f105"

def geo(lon1,lat1,lon2,lat2):
 r=math.pi/180
 a=lat1*r;b=lat2*r
 dx=((lon2-lon1+180)%360-180)*r
 q=math.sin((b-a)/2)**2+math.cos(a)*math.cos(b)*math.sin(dx/2)**2
 return 6371.0088*2*math.atan2(math.sqrt(q),math.sqrt(max(0,1-q)))

def maxspan(points):
 if len(points)<2:return 0.0
 return max(geo(*points[i],*points[j]) for i in range(len(points)) for j in range(i+1,len(points)))

def quant(values,q):
 if not values:return None
 v=sorted(values);p=(len(v)-1)*q;i=int(p)
 return v[i] if i==len(v)-1 else v[i]+(v[i+1]-v[i])*(p-i)

def output_csv(name,rows):
 if not rows:raise ValueError("No input rows for output "+name)
 with (OUT/name).open("w",newline="") as f:
  header=list(rows[0])
  w=csv.DictWriter(f,fieldnames=header)
  w.writeheader();w.writerows(rows)

def collect():
 dataset=OUT/"dataset_zip.zip"
 if not dataset.exists():raise ValueError("Original UK PDC archive missing: run probe.py first")
 observations=[];groups=[]
 with zipfile.ZipFile(dataset) as z:
  names=sorted(n for n in z.namelist() if not n.endswith("/"))
  sha=hashlib.sha256()
  for path in names:
   raw=z.read(path)
   sha.update(len(path).to_bytes(4,"big")+path.encode()+len(raw).to_bytes(8,"big")+raw)
  actual=sha.hexdigest()
  if actual!=PIN_CANONICAL_SHA256:raise ValueError("Original published archive member bytes changed "+actual)
  shps=[p for p in names if p.endswith(".shp")]
  if len(shps)!=24:raise ValueError("Not three colony×eight seasonal shapefiles")
  for source in shps:
   stem=source[:-4]
   filename=source.split("/")[-1]
   season=int(filename[-8:-4])
   colony=filename[:-8]
   dbf_fields,dbf=read_dbf(z.read(stem+".dbf"))
   shapetype,bbox,type_counts,geometry=read_shp(z.read(source))
   projection=z.read(stem+".prj").decode()
   if "GCS_WGS_1984" not in projection or shapetype!=8:
    raise ValueError("Unexpected original geodesy or MultiPoint type "+source)
   if len(geometry)!=len(dbf):raise ValueError("Published DBF/shape records do not match")
   for j,(properties,geom) in enumerate(zip(dbf,geometry)):
    dat=date.fromisoformat(properties["Date"].strip())
    if dat.year!=season and not (dat.year==season+1 and dat.month in (1,2,3)):
     raise ValueError("Original source image date outside its breeding-season filename "+source+str(dat))
    values=geom["group_coordinates"]
    if not values:raise ValueError("Source colony record with zero points")
    if any(not (-180<=lon<=180 and -90<=lat<=-50) for lon,lat in values):
     raise ValueError("Invalid recorded WGS84 colony group")
    # circular longitudes unneeded: sources near ±8°, +169°, +165°.
    center=(sum(lon for lon,lat in values)/len(values),sum(lat for lon,lat in values)/len(values))
    if not -180<center[0]<180:raise ValueError("Longitudes cross dateline; require circular center")
    phase=("winter" if dat.month in (4,5,6,7,8) and dat.year==season
           else "spring_summer" if dat.month in (9,10,11,12,1,2,3)
           else "other")
    sensor=properties.get("Satellite","").strip()
    obsID=f"{colony}|{season}|{j+1}"
    diameter=maxspan(values)
    rec={"observation_id":obsID,"colony":colony,"breeding_year":season,
         "source_record_number":geom["record_number"],"date":dat.isoformat(),"day_from_season_Jan1":(dat-date(season,1,1)).days,
         "phase":phase,"sensor":sensor,"image_path":properties.get("ImagePath",""),"time":properties.get("Time",""),
         "number_group_positions":len(values),
         "mean_group_longitude":center[0],"mean_group_latitude":center[1],
         "max_within_image_intergroup_diameter_km":diameter,
         "single_mapped_image_not_animal_count":True}
    observations.append(rec)
    for n,(lon,lat) in enumerate(values,1):
     groups.append({"observation_id":obsID,"colony":colony,"breeding_year":season,
       "date":dat.isoformat(),"phase":phase,"sensor":sensor,"group_number_within_observation":n,
       "longitude_WGS84":lon,"latitude_WGS84":lat,
       "point_is_mapped_group_location_not_individual_penguin":True})
 return actual,observations,groups

def analyze(records,points):
 byObs=defaultdict(list)
 for p in points:byObs[p["observation_id"]].append((p["longitude_WGS84"],p["latitude_WGS84"]))
 byYear=defaultdict(list)
 for p in records:byYear[(p["colony"],p["breeding_year"])].append(p)
 detail=[];summary=[];yearMetrics=[]
 for (colony,year),observations in sorted(byYear.items()):
  obs=sorted(observations,key=lambda x:(x["date"],x["time"],x["observation_id"]))
  if len(obs)<2:raise ValueError("No repeated observation dates")
  first=(obs[0]["mean_group_longitude"],obs[0]["mean_group_latitude"])
  earliest=date.fromisoformat(obs[0]["date"])
  winter=[x for x in obs if x["phase"]=="winter"]
  summer=[x for x in obs if x["phase"]=="spring_summer"]
  def centres(a):return [(x["mean_group_longitude"],x["mean_group_latitude"]) for x in a]
  firstW=centres(winter)[0] if winter else None
  firstS=centres(summer)[0] if summer else None
  for v in obs:
   current=(v["mean_group_longitude"],v["mean_group_latitude"])
   groupPositions=byObs[v["observation_id"]]
   dbase=geo(*first,*current)
   dgroup=max(geo(*first,*p) for p in groupPositions)
   r=max(geo(*current,*p) for p in groupPositions)
   detail.append({**v,"centroid_distance_from_first_observed_km":dbase,
    "furthest_group_from_first_observed_center_km":dgroup,
    "max_group_distance_from_same_image_center_km":r,
    "days_since_first_season_observation":(date.fromisoformat(v["date"])-earliest).days})
  d=[x for x in detail if x["colony"]==colony and x["breeding_year"]==year]
  vals=[x["centroid_distance_from_first_observed_km"] for x in d]
  winterCentres=centres(winter);summerCentres=centres(summer)
  winterMax= maxspan(winterCentres) if len(winterCentres)>=2 else None
  summerMax= maxspan(summerCentres) if len(summerCentres)>=2 else None
  dateDistinct=len(set(x["date"] for x in obs))
  maxGroup=max(x["number_group_positions"] for x in obs)
  # Source satellite modality is part of detection contrast, not biological group-count change.
  row={"colony":colony,"breeding_year":year,"original_dated_image_records":len(obs),
    "unique_observation_calendar_days":dateDistinct,
    "mapped_group_point_records":sum(x["number_group_positions"] for x in obs),
    "first_observed_date":obs[0]["date"],"last_observed_date":obs[-1]["date"],
    "n_winter_image_records":len(winter),"n_spring_summer_image_records":len(summer),
    "winter_first_date":winter[0]["date"] if winter else "",
    "spring_summer_first_date":summer[0]["date"] if summer else "",
    "max_group_count_in_one_image":maxGroup,
    "proportion_multigroup_images":sum(x["number_group_positions"]>1 for x in obs)/len(obs),
    "overall_max_centroid_distance_from_first_observation_km":max(vals),
    "overall_median_centroid_distance_from_first_observation_km":quant(vals,.5),
    "overall_p95_centroid_distance_from_first_observation_km":quant(vals,.95),
    "overall_max_group_distance_from_first_observation_km":max(x["furthest_group_from_first_observed_center_km"] for x in d),
    "overall_max_intergroup_diameter_same_image_km":max(x["max_within_image_intergroup_diameter_km"] for x in obs),
    "max_between_image_centroid_span_in_winter_km":winterMax,
    "max_between_image_centroid_span_in_spring_summer_km":summerMax,
    "spring_summer_minus_winter_centroid_span_km":(summerMax-winterMax) if winterMax is not None and summerMax is not None else None,
    "centroid_distance_first_winter_to_first_spring_summer_km":geo(*firstW,*firstS) if firstW and firstS else None,
    "sensor_count_names":";".join(f"{k}:{v}" for k,v in sorted(Counter(x["sensor"] for x in obs).items())),
    "same_colony_year_not_independent_regional_colony_replicate":True}
  yearMetrics.append(row)
  byPhase=defaultdict(list)
  for x in d:byPhase[x["phase"]].append(x)
  for phase,ar in byPhase.items():
   summary.append({"colony":colony,"breeding_year":year,"phase":phase,
      "image_records":len(ar),"source_group_positions":sum(x["number_group_positions"] for x in ar),
      "centroid_displacement_max_from_first_year_image_km":max(x["centroid_distance_from_first_observed_km"] for x in ar),
      "max_group_distance_from_first_year_image_km":max(x["furthest_group_from_first_observed_center_km"] for x in ar),
      "max_same_image_intergroup_diameter_km":max(x["max_within_image_intergroup_diameter_km"] for x in ar),
      "max_groups_in_one_image":max(x["number_group_positions"] for x in ar),
      "source_sensor_count":";".join(f"{k}:{v}" for k,v in sorted(Counter(x["sensor"] for x in ar).items()))})
 return detail,summary,yearMetrics

def main():
 sha,obs,groups=collect()
 if len(obs)!=1110 or len(groups)!=3681:raise ValueError("Original 24-file source topology changed")
 detail,phases,years=analyze(obs,groups)
 if len(years)!=24:raise ValueError("Not 3 breeding colonies × 8 years")
 output_csv("source_1110_observation_centroids_and_group_spread.csv",detail)
 output_csv("source_3681_group_locations_WGS84.csv",groups)
 output_csv("colony_year_phase_separate_mobility.csv",phases)
 output_csv("original_24_colony_year_centroid_motion.csv",years)
 byColony=defaultdict(list)
 for x in years:byColony[x["colony"]].append(x)
 summary={
  "source_DOI":"10.5285/"+ID,
  "source_publication":"Macdonald et al. 2026; DOI 10.1038/s43247-026-03906-0",
  "source_canonical_SHA256":sha,
  "facts":{"observed_site_years":len(years),"source_dated_images":len(obs),
     "number_group_locations":len(groups),
     "image_records_with_multiple_groups":sum(x["number_group_positions"]>1 for x in obs),
     "colony_years_with_winter_and_spring_summer_both_min2images":sum(x["max_between_image_centroid_span_in_winter_km"] is not None and x["max_between_image_centroid_span_in_spring_summer_km"] is not None for x in years),
     "colony_years_centroid_span_over2km_from_first_image":sum(x["overall_max_centroid_distance_from_first_observation_km"]>2 for x in years),
     "colony_years_any_group_over2km_from_first_image":sum(x["overall_max_group_distance_from_first_observation_km"]>2 for x in years)},
  "by_colony":{name:{
   "n_years":len(vals),
   "median_max_centroid_shift_from_first_image_km":quant([x["overall_max_centroid_distance_from_first_observation_km"] for x in vals],.5),
   "max_centroid_shift_all_years_km":max(x["overall_max_centroid_distance_from_first_observation_km"] for x in vals),
   "n_years_centroid_over2km":sum(x["overall_max_centroid_distance_from_first_observation_km"]>2 for x in vals),
   "n_years_at_least_one_group_over2km":sum(x["overall_max_group_distance_from_first_observation_km"]>2 for x in vals),
   "median_n_groups_max_observed":quant([x["max_group_count_in_one_image"] for x in vals],.5),
   "support_winter_and_summer_years":sum(x["max_between_image_centroid_span_in_winter_km"] is not None and x["max_between_image_centroid_span_in_spring_summer_km"] is not None for x in vals)
  } for name,vals in sorted(byColony.items())},
  "colony_years":years,
  "interpretation":"Coordinates are manually identified group positions, not bird counts. Group centroids are unweighted by birds and split groups are NOT new colonies or extinction. Sensor selection and observation days differ by season and site. Between-year standardized relocation requires season-aligned observation dates; this is within-breeding-season position dynamics only."
 }
 (OUT/"movement_result.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n")
 print("MACDONALD2026 ORIGINAL MOVEMENT METRICS "+json.dumps({"facts":summary["facts"],"by_colony":summary["by_colony"],"by_year":[{k:x[k] for k in ("colony","breeding_year","n_winter_image_records","n_spring_summer_image_records","max_group_count_in_one_image","overall_max_centroid_distance_from_first_observation_km","overall_max_group_distance_from_first_observation_km","max_between_image_centroid_span_in_winter_km","max_between_image_centroid_span_in_spring_summer_km")} for x in years],"sha256":sha},ensure_ascii=False),flush=True)
if __name__=="__main__":main()
