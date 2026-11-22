#!/usr/bin/env python3
"""Retrieve REAL Cook, Fox & Thomson (2021) BAS Antarctic Peninsula historic
glacier-front ZIP (1843–2008), inspect vector schema and source dates.

The original Antarctic Peninsula historical coastal-change product records
glacier and ice-shelf FRONT LINES, not a census of bare rock, not dynamic
land-use patches, and not whole 2-D glacier extent. No local area-gain
inferences or biological colonization causality are permitted by this probe.
"""
from __future__ import annotations
import argparse,collections,datetime,hashlib,io,json,os,urllib.parse,urllib.request,zipfile
from pathlib import Path

BASE="https://ramadda.data.bas.ac.uk"
ENTRY="07727663-9b94-4069-a486-67e4d82177d3"
ZIPNAME="Coastal_change_EPSG.zip"
EXPECTED_BYTES=7493252

def get_bytes(url,limit=40_000_000):
    req=urllib.request.Request(url,headers={"User-Agent":"mina-original-Cook-Fox-Thomson-2021-source-audit/1.0"})
    with urllib.request.urlopen(req,timeout=90) as f:
        buf=f.read(limit+1)
        mime=f.headers.get("Content-Type","")
        return buf,f.status,mime

def get_entries():
    endpoint=f"{BASE}/repository/entry/show?entryid={ENTRY}&output=json"
    content,status,mime=get_bytes(endpoint,1_000_000)
    assert status==200
    root=json.loads(content)
    assert isinstance(root,list)
    selected=[r for r in root if r.get("name")==ZIPNAME]
    if len(selected)!=1:raise ValueError("Official Cook zip entry not uniquely found")
    selected=selected[0]
    assert selected.get("parent")==ENTRY
    return selected,endpoint

def load_zip(entry):
    eid=entry["id"]
    name=entry["name"]
    candidates=[
      f"{BASE}/repository/entry/get/{urllib.parse.quote(name)}?entryid={urllib.parse.quote(eid)}",
      f"{BASE}/repository/entry/get?entryid={urllib.parse.quote(eid)}"
    ]
    errs=[]
    for url in candidates:
        try:
            b,status,mime=get_bytes(url,35_000_000)
            if status==200 and b.startswith(b"PK\x03\x04"):
                return b,url,mime,errs
            errs.append({"url":url,"http_status":status,"mime":mime,
                         "response_first_40":repr(b[:40])})
        except Exception as e:
            errs.append({"url":url,"error":f"{type(e).__name__}: {str(e)[:180]}"})
    raise RuntimeError("Official ZIP not retrieved from two standard RAMADDA entry/get URLs: "+json.dumps(errs))

def audit_zip(data):
    import shapefile
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        assert z.testzip() is None
        names=z.namelist()
        candidates=[n for n in names if n.lower().endswith(".shp") and not n.startswith("__MACOSX")]
        results=[]
        for shp in candidates:
            base=shp[:-4]
            dbf=base+".dbf";shx=base+".shx";prj=base+".prj"
            if dbf not in names or shx not in names:
                results.append({"shape":shp,"status":"missing_required_shape_parts"});continue
            raw=shapefile.Reader(
              shp=io.BytesIO(z.read(shp)),
              dbf=io.BytesIO(z.read(dbf)),
              shx=io.BytesIO(z.read(shx)),
              encoding="latin1"
            )
            schema=[{"name":a[0],"type":a[1],"len":a[2],"decimals":a[3]} for a in raw.fields[1:]]
            previews=[]
            for i in range(min(5,len(raw))):
                rec=raw.record(i)
                previews.append({a["name"]:str(v)[:160] for a,v in zip(schema,rec)})
            datecols=[a["name"] for a in schema if
                      any(t in a["name"].lower() for t in ("date","time","year","epoch","source","glac","acc"))]
            values={}
            for col in datecols[:12]:
                ix=[a["name"] for a in schema].index(col)
                val=collections.Counter(str(raw.record(i)[ix]) for i in range(len(raw)))
                values[col]={"distinct":len(val),"most_common":val.most_common(12)}
            results.append({
               "shape":shp,"status":"SHAPEFILES_SOURCE_RETRIEVED",
               "n_original_features":len(raw),
               "native_shape_type":raw.shapeTypeName,
               "native_bbox":list(raw.bbox),
               "prj_first400":z.read(prj).decode(errors="replace")[:400] if prj in names else None,
               "schema":schema,"original_date_column_summary":values,
               "first_original_feature_attributes":previews
            })
            raw.close()
        return {"source_zip_members":names,"shapefiles":results,
                "zip_has_usable_shapefile":any(x["status"]=="SHAPEFILES_SOURCE_RETRIEVED" for x in results)}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,required=True)
    ar=p.parse_args();ar.out.mkdir(parents=True,exist_ok=True)
    item,entrysource=get_entries()
    data,download_url,mime,errs=load_zip(item)
    assert data.startswith(b"PK\x03\x04") and len(data)<35_000_000
    checksum=hashlib.sha256(data).hexdigest()
    sourcezip=ar.out/"Cook2021_Coastal_change_EPSG_original.zip"
    sourcezip.write_bytes(data)
    details=audit_zip(data)
    report={
      "status":"PASS_ACTUAL_ORIGINAL_COOK2021_HISTORIC_COASTAL_CHANGE_SOURCE_ARCHIVE",
      "source_DOI":"10.5285/07727663-9B94-4069-A486-67E4D82177D3",
      "source_original_RamadDA_entry":ENTRY,
      "original_linked_Cook_ZIP_id":item.get("id"),
      "original_RamadDA_metadata_source_url":entrysource,
      "original_download_url":download_url,
      "n_original_archive_bytes":len(data),
      "source_original_reported_size_bytes":item.get("filesize",None),
      "size_equal_official_repository_metadata":(len(data)==int(item.get("filesize",len(data)))),
      "original_source_sha256":checksum,
      "source_zip_mime":mime,
      "vector_validation":details,
      "source_year_span_is_not_annual_sampling":"1843-2008 compiled front positions",
      "glacier_front_lines_not_ice_free_land_polygons":True,
      "source_site_colony_status_not_jointly_inferred":True,
      "future_colony_date_or_climate_effect_not_inferred":True,
    }
    (ar.out/"Cook2021_original_GIS_source_inspection_receipt.json").write_text(
       json.dumps(report,ensure_ascii=False,indent=2)+"\n")
    print("COOK_2021_SOURCE_ZIP="+json.dumps(
      {"status":report["status"],"bytes":len(data),
       "sha256":checksum,"files":[{"name":z.get("shape"),"status":z.get("status"),
                   "rows":z.get("n_original_features"),"schema":[x["name"] for x in z.get("schema",[])],
                   "date_info":z.get("original_date_column_summary",{}),
                   "source_samples":z.get("first_original_feature_attributes",[])[:2]}
                  for z in details["shapefiles"]]},ensure_ascii=False),flush=True)
if __name__=="__main__":main()
