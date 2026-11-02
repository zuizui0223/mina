#!/usr/bin/env python3
"""Inspect 24 original Macdonald 2026 time-stamped emperor colony point shapefiles.

Download already completed by probe.py to dataset_zip.zip. Inspect the published
coordinate system and DBF source fields before selecting movement estimands.
"""
from collections import Counter,defaultdict
from pathlib import Path
import datetime,hashlib,json,re,struct,zipfile
from probe import OUT,ID

def dbf_read(data):
 if len(data)<32:raise ValueError("DBF header short")
 n,header_length,record_len=struct.unpack_from("<IHH",data,4)
 fields=[]
 for i in range(32,header_length-1,32):
  q=data[i:i+32]
  if q[0]==0x0d:break
  name=q[:11].split(b"\0")[0].decode("latin1")
  typ=chr(q[11]);size=q[16]
  fields.append((name,typ,size))
 rows=[]
 for i in range(n):
  raw=data[header_length+i*record_len:header_length+(i+1)*record_len]
  if len(raw)!=record_len:raise ValueError("Truncated DBF")
  if raw[0:1]==b"*":continue
  pos=1;rec={}
  for name,typ,size in fields:
   value=raw[pos:pos+size].decode("latin1","replace").strip()
   rec[name]=value
   pos+=size
  rows.append(rec)
 return fields,rows

def shape_read(data):
 if len(data)<100 or struct.unpack_from(">I",data,0)[0]!=9994:raise ValueError("Invalid Esri shape header")
 src_type=struct.unpack_from("<i",data,32)[0]
 bbox=struct.unpack_from("<dddd",data,36)
 pts=[];offset=100;types=Counter()
 while offset<len(data):
  if len(data)-offset<8:raise ValueError("Truncated shapefile record header")
  number,wordcount=struct.unpack_from(">ii",data,offset)
  start=offset+8;size=wordcount*2
  if start+size>len(data):raise ValueError("Shapefile record truncated")
  type_id=struct.unpack_from("<i",data,start)[0]
  types[type_id]+=1
  if type_id in (1,11,21):
   x,y=struct.unpack_from("<dd",data,start+4)
   pts.append({"record_number":number,"shape_type":type_id,"x":x,"y":y})
  elif type_id==0:
   pts.append({"record_number":number,"shape_type":0,"x":None,"y":None})
  else:
   pts.append({"record_number":number,"shape_type":type_id,"x":None,"y":None})
  offset=start+size
 return src_type,bbox,types,pts

def main():
 source=OUT/"dataset_zip.zip"
 if not source.exists():raise FileNotFoundError("First probe did not download shapefiles")
 report={"source_dataset_id":ID,"source_parent_zip_sha256":hashlib.sha256(source.read_bytes()).hexdigest(),"per_colony_year":[]}
 with zipfile.ZipFile(source) as z:
  allnames=sorted(n for n in z.namelist() if not n.endswith("/"))
  canonical=hashlib.sha256()
  for name in allnames:
   data=z.read(name)
   canonical.update(len(name).to_bytes(4,"big")+name.encode()+len(data).to_bytes(8,"big")+data)
  report["source_canonical_sha256"]=canonical.hexdigest()
  shpfiles=[name for name in allnames if name.lower().endswith(".shp")]
  if len(shpfiles)!=24:raise ValueError("Expected 24 tracking shapefiles for 3 colonies×8 years, got "+str(len(shpfiles)))
  for path in shpfiles:
   stem=path[:-4]
   dbf,prj=z.read(stem+".dbf"),z.read(stem+".prj")
   projection=prj.decode("utf-8","replace")
   types,rows=dbf_read(dbf)
   shapetype,bbox,shapeTypes,pts=shape_read(z.read(path))
   if len(rows)!=len(pts):raise ValueError("Mismatched source shapefile and DBF records "+path)
   filename=path.split("/")[-1]
   match=re.match(r"([A-Za-z]+)(20\d\d)\.shp",filename)
   if not match:raise ValueError("Unexpected original tracked site/year filename")
   colony,year=match.group(1),int(match.group(2))
   fields=[{"name":n,"type":t,"width":w} for n,t,w in types]
   values={n:Counter(row[n] for row in rows).most_common(8) for n,t,w in types}
   sample=[{**rows[i],"shape_x":pts[i]["x"],"shape_y":pts[i]["y"]} for i in range(min(5,len(rows)))]
   result={"colony":colony,"year":year,"source_shp_filename":filename,"source_shp_sha256":hashlib.sha256(z.read(path)).hexdigest(),
     "source_dbf_sha256":hashlib.sha256(dbf).hexdigest(),"source_CRS_WKT":projection,
     "number_source_points":len(pts),"shape_header_type":shapetype,"record_shape_types":dict(shapeTypes),
     "shape_raw_XY_minmax":{"x_min":min((x["x"] for x in pts if x["x"] is not None),default=None),"x_max":max((x["x"] for x in pts if x["x"] is not None),default=None),
                           "y_min":min((x["y"] for x in pts if x["y"] is not None),default=None),"y_max":max((x["y"] for x in pts if x["y"] is not None),default=None)},
     "field_schema":fields,"common_field_values":values,"first_observations":sample}
   report["per_colony_year"].append(result)
   print("MACDONALD2026 TRACKING SHAPE SOURCE "+json.dumps(result,ensure_ascii=False),flush=True)
 report["per_colony_year"].sort(key=lambda x:(x["colony"],x["year"]))
 report["cohort_counts"]={"source_year_files":len(shpfiles),"source_total_point_records":sum(x["number_source_points"] for x in report["per_colony_year"]),
  "colony_year_counts":{c:{str(x["year"]):x["number_source_points"] for x in report["per_colony_year"] if x["colony"]==c} for c in sorted(set(x["colony"] for x in report["per_colony_year"]))}}
 (OUT/"tracking_original_source_fields.json").write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n")
 print("MACDONALD2026 TRACKING GEOMETRY SOURCE COMPLETE "+json.dumps({"dataset":ID,"canonical_sha256":report["source_canonical_sha256"],"facts":report["cohort_counts"],"crs":list({x["source_CRS_WKT"] for x in report["per_colony_year"]}),"fields_by_colony":{c:report["per_colony_year"][[x["colony"] for x in report["per_colony_year"]].index(c)]["field_schema"] for c in report["cohort_counts"]["colony_year_counts"]}}),flush=True)
if __name__=="__main__":main()
