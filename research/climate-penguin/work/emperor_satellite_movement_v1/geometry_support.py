#!/usr/bin/env python3
"""Satellite location fields: geometric validity and true repeated observation support.

CRITICAL: 'img_lat1'/'img_lon' can be image centroids or placeholders;
distances between them are only IMAGE coordinate changes until independently validated
as penguin footprint locations. Never label displacement as biological movement.
"""
from collections import Counter,defaultdict
from pathlib import Path
import json,math,statistics
from schema_audit import OUT,parse_worksheet

def num(v):
 try:
  x=float(str(v).strip())
  return x if math.isfinite(x) else None
 except (ValueError,TypeError):
  return None

def distance(lat1,lon1,lat2,lon2):
 r=math.pi/180
 x1,x2=lat1*r,lat2*r
 dlat=(lat2-lat1)*r
 dlon=((lon2-lon1+180)%360-180)*r
 h=math.sin(dlat/2)**2+math.cos(x1)*math.cos(x2)*math.sin(dlon/2)**2
 return 6371.0*2*math.atan2(math.sqrt(h),math.sqrt(max(0,1-h)))

def percentile(a,p):
 if not a:return None
 b=sorted(a)
 i=(len(b)-1)*p
 k=int(i)
 return b[k] if k+1==len(b) else b[k]+(b[k+1]-b[k])*(i-k)

def main():
 data=(OUT/"empe_satellite_2023-05-25.xlsx").read_bytes()
 tabs=list(parse_worksheet(data))
 if len(tabs)!=1:
  raise ValueError("Expected exactly one original source satellite worksheet")
 _,fields,records=tabs[0]
 needed=("site_id","img_year","img_long","img_lat","img_lat1","img_lon","img_qualit","area_m2","bpresent","remove")
 if any(k not in fields for k in needed):
  raise ValueError("Original source geometry/quality fields altered")
 states=Counter()
 group=defaultdict(list)
 siteStatic=defaultdict(set)
 sample=[]
 for row in records:
  sid=row["site_id"].strip()
  year=num(row["img_year"])
  lat0=num(row["img_lat"])
  lon0=num(row["img_long"])
  lat1=num(row["img_lat1"])
  lon1=num(row["img_lon"])
  area=num(row["area_m2"])
  qual=str(row["img_qualit"])
  for k in ["area_m2","img_qualit","bpresent","breakup","remove","partial","distributi","check","source"]:
   states[(k,str(row.get(k,""))[:70])]+=1
  if year is None or not 2009<=year<=2018:
   states[("filter","outside_2009_2018")]+=1
   continue
  siteStatic[sid].add((lat0,lon0))
  valid0=lat0 is not None and lon0 is not None and -90<=lat0<=-50 and -180<=lon0<=180
  valid1=lat1 is not None and lon1 is not None and -90<=lat1<=-50 and -180<=lon1<=180
  if not valid0:states[("geometry","bad_static")]+=1
  if not valid1:states[("geometry","no_valid_image_point")]+=1
  if not valid1 and lat1==0 and lon1==0:states[("geometry","zero_zero_image_point")]+=1
  if valid1 and valid0:
   dist=distance(lat0,lon0,lat1,lon1)
   if dist>100:states[("geometry","image_more_100km_from_static")]+=1
  else:dist=None
  if area is None:states[("area","missing")]+=1
  elif area==0:states[("area","zero")]+=1
  else:states[("area","positive")]+=1
  if valid1 and area is not None and area>0:
   states[("support","valid_geo_and_positive_area")]+=1
   group[(sid,int(year))].append({"lat":lat1,"lon":lon1,"static_dist_km":dist,"quality":qual,"area":area,
    "site":sid,"year":int(year),"source":row.get("source"),"image_catalog":row.get("Catalog_id"),
    "month":row.get("img_month"),"bpresent":row.get("bpresent"),"remove":row.get("remove")})
   if len(sample)<15:sample.append({"site":sid,"year":int(year),"lat":lat1,"lon":lon1,"static_dist_km":round(dist,3) if dist is not None else None,
    "qual":qual,"area":area,"bpresent":row.get("bpresent"),"remove":row.get("remove"),
    "source":row.get("source"),"img_catalog":row.get("Catalog_id")})
  if valid1 and (area is None or area==0):states[("support","valid_geo_without_positive_area")]+=1
 matched=defaultdict(list)
 for (site,year),arr in group.items():
  matched[site].append(year)
 dists=[]
 possible=[]
 byyear=Counter()
 for (site,year),a in sorted(group.items()):
  byyear[year]+=1
  for i in range(len(a)):
   for j in range(i+1,len(a)):
    dists.append(distance(a[i]["lat"],a[i]["lon"],a[j]["lat"],a[j]["lon"]))
  following=group.get((site,year+1),[])
  if not following:continue
  matrix=[distance(x["lat"],x["lon"],y["lat"],y["lon"]) for x in a for y in following]
  possible.append({"site":site,"start_year":year,"end_year":year+1,
   "number_image_points_first":len(a),"number_image_points_second":len(following),
   "nearest_image_coordinate_shift_km":min(matrix),
   "largest_image_coordinate_shift_km":max(matrix),
   "single_image_pair":len(a)==len(following)==1,
   "source_coordinates_are_NOT_certified_colony_footprints":True})
 positives=[x for vs in group.values() for x in vs]
 summary={
  "original_satellite_rows":len(records),
  "original_2009_2018_siteIDs":len(siteStatic),
  "source_static_coordinates_constant_within_colony":sum(len(a)==1 for a in siteStatic.values()),
  "source_static_coordinates_vary_within_colony":sum(len(a)>1 for a in siteStatic.values()),
  "image_geographic_point_and_positive_area_siteyears":len(group),
  "image_geographic_point_and_positive_area_distinct_siteIDs":len(matched),
  "image_geographic_point_positive_area_observations":len(positives),
  "observed_siteyears_by_year":dict(sorted(byyear.items())),
  "siteIDs_with_at_least_2_image_years":sum(len(set(v))>=2 for v in matched.values()),
  "siteIDs_with_at_least_3_image_years":sum(len(set(v))>=3 for v in matched.values()),
  "siteyear_repeated_image_point_pairs":sum(len(v)>=2 for v in group.values()),
  "within_siteyear_image_coordinate_spread_km_p50":percentile(dists,.5),
  "within_siteyear_image_coordinate_spread_km_p95":percentile(dists,.95),
  "valid_image_point_static_distance_km_p50":percentile([x["static_dist_km"] for x in positives if x["static_dist_km"] is not None],.5),
  "valid_image_point_static_distance_km_p95":percentile([x["static_dist_km"] for x in positives if x["static_dist_km"] is not None],.95),
  "candidate_consecutive_image_coordinate_pair_n":len(possible),
  "candidate_consecutive_image_point_shift_over_2km":sum(x["nearest_image_coordinate_shift_km"]>2 for x in possible),
  "candidate_consecutive_single_image_pair_n":sum(x["single_image_pair"] for x in possible),
  "position_evidence_NOT_equivalent_to_penguin_colony_movement":True
 }
 report={"facts":summary,"top_categorical_original_value_counts":[{"field":k,"value":v,"n":n}
 for (k,v),n in states.most_common(100)],"example_valid_rows":sample,
  "largest_candidate_shifts":sorted(possible,key=lambda x:x["nearest_image_coordinate_shift_km"],reverse=True)[:35],
  "warning":"Image coordinate fields may be satellite imagery georeference/scene centers, not breeding group centroid. Without source provenance this is NOT an annual colony movement measurement."}
 (OUT/"geometry_support.json").write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n")
 import csv
 if possible:
  with (OUT/"candidate_image_coordinate_shifts_NOT_colony_movement.csv").open("w",newline="") as f:
   writer=csv.DictWriter(f,fieldnames=list(possible[0]))
   writer.writeheader()
   writer.writerows(possible)
 print("EMPEROR ORIGINAL SATELLITE GEOMETRY SUPPORT "+json.dumps(report,ensure_ascii=False),flush=True)
if __name__=="__main__":main()
