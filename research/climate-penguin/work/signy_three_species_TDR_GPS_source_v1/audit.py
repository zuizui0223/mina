"""Source first inventory: original BAS TDR vs GPS, three Signy penguins.

Inspect ZIP directory and tiny CSV heads only, not pressure outcomes.
Original deployment ID is the join key, not similar timestamps or locations.
Source TDR pressure is dbar; dive/foraging cannot be inferred from headers.
"""
from __future__ import annotations
import argparse,csv,hashlib,io,json,re,zipfile
from collections import Counter
from pathlib import Path

SRC={
 "Adelie":{"tid":"bf62d713-93e5-487f-acba-1ec2da35c7e1","gid":"55b4d36f-c5e1-4d64-bb14-0b832dcd4b88","prefix":"SIA","expected_tdr":None,"expected_gps":41},
 "Chinstrap":{"tid":"da13e049-be2b-4345-bbdd-ab960cb24731","gid":"8f8ccba5-01af-4b00-8a3b-c3c85b24bf92","prefix":"SIC","expected_tdr":None,"expected_gps":121},
 "Gentoo":{"tid":"ff0cbcb7-bdad-4d03-bdf2-a54c54d67d9f","gid":"9cb04ca6-f88f-4368-b715-45ff73ff81eb","prefix":"SIG","expected_tdr":None,"expected_gps":11},
}
def get_header(z,item):
 with z.open(item) as fh:
  chunk=fh.read(8192)
 if not chunk:return [],"",0
 content=chunk.decode("utf-8-sig",errors="replace")
 lines=content.splitlines()
 if not lines:return [],"",0
 reader=csv.reader(io.StringIO("\n".join(lines[:8])))
 head=next(reader,[])
 rows=list(reader)
 datetime_idx=next((i for i,x in enumerate(head) if x.lower().replace(" ","")=="datetime"),None)
 first=next((r[datetime_idx] for r in rows if datetime_idx is not None and len(r)>datetime_idx and r[datetime_idx].strip()),"")
 return head,first,len(rows)
def source_track_roster(path,prefix,role):
 if not zipfile.is_zipfile(path):raise ValueError("Publisher original invalid ZIP "+str(path))
 entries=[];by_id={};matched_names=[];diagnostic=[]
 with zipfile.ZipFile(path) as z:
  for info in z.infolist():
   if info.is_dir():continue
   name=Path(info.filename).name
   upper=name.upper()
   # Existing source-verified gps.read_tracks accepts a publisher filename
   # with extra tokens between original tag and final _GPS.csv.
   if upper.startswith(prefix) and upper.endswith(".CSV"):
    diagnostic.append(name)
   if not (upper.startswith(prefix) and upper.endswith(".CSV") and "_"+role.upper() in upper):
    continue
   rawid=upper.split("_")[0]
   if not re.fullmatch(re.escape(prefix.upper())+r"\d{3,4}",rawid):
    continue
   matched_names.append(name)
   head,first,nprobe=get_header(z,info)
   if role=="GPS":
    valid={"DateTime","Latitude_degrees_north","Longitude_degrees_east"}.issubset(set(head))
   else:
    valid="DateTime" in head and any(q.lower().startswith("pressure") for q in head)
   x=dict(id=rawid,member=info.filename,size=info.file_size,compressed_size=info.compress_size,
          crc32=f"{info.CRC:08x}",header=head,header_ok=valid,
          source_datetime_first=first,first_rows_probed=nprobe,empty_or_short=info.file_size<120 or not first)
   # Duplicate version2 publisher GPS member SIC005 exists: permit only
   # identical compressed-source CRC and content length for same original ID.
   if rawid in by_id:
    seen=by_id[rawid]
    if (seen["crc32"],seen["size"])!=(x["crc32"],x["size"]):
     raise ValueError("Conflicting duplicate original deployment "+role+" "+rawid)
    x["duplicate_original_identical_member"]=True
   else:
    by_id[rawid]=x
    x["duplicate_original_identical_member"]=False
   entries.append(x)
 if not entries:
  raise ValueError("No source files matched role "+role+" prefix "+prefix+
                   "; candidate examples="+str(sorted(diagnostic)[:10])+
                   "; sample members="+str([a.filename for a in zipfile.ZipFile(path).infolist()[:8]]))
 return sorted(entries,key=lambda x:(x["id"],x["member"]))
def run(source,out):
 source,out=map(Path,(source,out))
 summary={}
 for sp,c in SRC.items():
  gps=source_track_roster(source/"gps"/(sp.lower()+".zip"),c["prefix"],"GPS")
  tdr=source_track_roster(source/"tdr"/(sp.lower()+".zip"),c["prefix"],"TDR")
  if len(gps)!=c["expected_gps"]:raise ValueError(f"{sp} GPS source roster changed: {len(gps)}; names="+str([x["member"] for x in gps[:7]]))
  if c["expected_tdr"] is not None and len(tdr)!=c["expected_tdr"]:
   raise ValueError(f"{sp} TDR source roster changed: {len(tdr)}")
  gp={r["id"]:r for r in gps if r["header_ok"] and not r["empty_or_short"]}
  dp={r["id"]:r for r in tdr if r["header_ok"] and not r["empty_or_short"]}
  matched=sorted(set(gp)&set(dp))
  no_gps=sorted(set(dp)-set(gp))
  no_tdr=sorted(set(gp)-set(dp))
  joins=[dict(species=sp,original_id=id,original_gps_crc=gp[id]["crc32"],
    original_tdr_crc=dp[id]["crc32"],original_gps_first_source_time=gp[id]["source_datetime_first"],
    original_tdr_first_source_time=dp[id]["source_datetime_first"],
    original_tdr_uncompressed_bytes=dp[id]["size"]) for id in matched]
  summary[sp]=dict(gps_original_count=len(gps),tdr_original_count=len(tdr),
   original_GPS_doI="10.5285/"+c["gid"],original_TDR_DOI="10.5285/"+c["tid"],
   source_gps_nonempty_schema_valid=len(gp),source_tdr_nonempty_schema_valid=len(dp),
   original_duplicate_gps_member_rows=sum(x["duplicate_original_identical_member"] for x in gps),
   original_duplicate_tdr_member_rows=sum(x["duplicate_original_identical_member"] for x in tdr),
   n_same_deployment_source_GPS_and_TDR=len(matched),
   source_deployments_GPS_only=no_tdr,source_deployments_TDR_only=no_gps,
   n_tdr_original_bytes=sum(v["size"] for v in tdr),
   n_bad_tdr_headers=sum(not v["header_ok"] for v in tdr),
   tdr_source_header_schemas={str(k):n for k,n in Counter(tuple(v["header"]) for v in tdr).items()},
   source_matched_deployments=joins,original_tdr_first_source_sha_not_checked=True)
 out.mkdir(parents=True,exist_ok=True)
 (out/"source_inventory.json").write_text(json.dumps(dict(date="2026-11-05",
  status="three_species_source_GPS_TDR_matched_deployment_roster_only",
  species=summary,all_gps_and_tdr_source_cessions_public=True,
  no_pressure_values_loaded=True,no_dives_or_foraging_claim=True,
  original_zip_wrapper_SHA_not_inferred_from_CRC=True,
  limits=["Original TDR full pressure has not been read; 8KB head/CRC are source-schema receipts, not integrity of full measured data",
  "TDR sensor clock synchronization with GPS not externally verified",
  "GPS original 168-track content hash was established in existing mina GPS source receipt; this new file inventory independently matches IDs",
  "A matched TDR source file does not ensure temporally overlapping dive locations",
  "Species and years have different deployments and source sensor calibrations; missingness is not evidence of nondiving",
  "No future climate scenario or reproduction response from this inventory"]),ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 print(json.dumps({k:{z:v[z] for z in
  ("gps_original_count","tdr_original_count","source_gps_nonempty_schema_valid",
   "source_tdr_nonempty_schema_valid","n_same_deployment_source_GPS_and_TDR",
   "n_tdr_original_bytes","n_bad_tdr_headers")} for k,v in summary.items()},ensure_ascii=False,indent=2))
 return summary
if __name__=="__main__":
 p=argparse.ArgumentParser()
 p.add_argument("--source",required=True,type=Path)
 p.add_argument("--out",required=True,type=Path)
 a=p.parse_args();run(a.source,a.out)
