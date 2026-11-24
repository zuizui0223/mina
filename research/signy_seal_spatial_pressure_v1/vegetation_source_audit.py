"""Publisher source and schema inventory only; no plant/seal outcome join."""
import argparse,csv,hashlib,io,json,re,zipfile
from pathlib import Path
import requests
from openpyxl import load_workbook
import fitz

DOI="10.6084/m9.figshare.18282695"
API="https://api.figshare.com/v2/articles/18282695"
DC="https://api.datacite.org/dois/"+DOI
MAP="https://nora.nerc.ac.uk/id/eprint/539135/1/Global%20Change%20Biology%20-%202025%20-%20Dunn%20-%20Temporary%20Absence%20of%20Warming%20in%20the%20Northern%20Weddell%20Sea%20Validates%20Expected%20Responses.pdf"
GEO="https://ramadda.data.bas.ac.uk/repository/entry/show?entryid=af80c82c-b6a0-4978-92e0-efe063c390af&output=zip.tree"
def sha(b):return hashlib.sha256(b).hexdigest()
def get(url,limit=80_000_000):
    with requests.get(url,timeout=(15,75),stream=True) as r:
        r.raise_for_status()
        chunks=[];n=0
        for c in r.iter_content(1<<20):
            n+=len(c)
            if n>limit:raise ValueError("source exceeds bounded intake")
            chunks.append(c)
        return b"".join(chunks)
def key(v):return re.sub(r"[^a-z0-9]","",str(v).lower())
LAT={"lat","latitude","latitudedegreesnorth","decimallatitude"}
LON={"lon","long","longitude","longitudedegreeseast","decimallongitude"}
XY={"x","y","easting","northing","utmx","utmy","xcoord","ycoord","east","north"}
YEAR={"year","surveyyear","season","date","surveydate","samplingyear"}
ID={"id","siteid","site","plotid","plot","locationid","populationid","pointid","sampleid","station","locality"}
def structural_table(header,rows):
    h=["" if x is None else str(x) for x in header]
    kk=[key(x) for x in h]
    n=0;coord=0;years=set()
    lat=[i for i,k in enumerate(kk) if k in LAT];lon=[i for i,k in enumerate(kk) if k in LON]
    ycols=[i for i,k in enumerate(kk) if k in YEAR]
    for row in rows:
        if not any(v is not None and str(v).strip() for v in row):continue
        n+=1
        if len(lat)==len(lon)==1 and max(lat+lon)<len(row):
            try:
                a,b=float(row[lat[0]]),float(row[lon[0]])
                if -61<=a<=-60 and -46<=b<=-45:coord+=1
            except (ValueError,TypeError):pass
        for i in ycols:
            if i<len(row):
                m=re.search(r"\b(19\d\d|20\d\d)\b",str(row[i]))
                if m:years.add(m.group(0))
    return {"header":h,"data_rows":n,"coordinate_candidate_fields":[h[i] for i,k in enumerate(kk) if k in LAT|LON|XY],
      "coordinate_complete_rows_in_broad_signy_bbox":coord if len(lat)==len(lon)==1 else None,
      "year_candidate_fields":[h[i] for i in ycols],"year_labels":sorted(years),
      "site_id_candidate_fields":[h[i] for i,k in enumerate(kk) if k in ID],
      "note":"First row header only; multirow headers/projected CRS need review; no abundance values reported."}
def inventory(name,b,depth=0):
    out={"name":name,"bytes":len(b),"sha256":sha(b)}
    ext=Path(name).suffix.lower()
    try:
        if ext in (".csv",".tsv",".txt"):
            for enc in ("utf-8-sig","cp1252"):
                try:s=b.decode(enc,errors="strict");break
                except UnicodeDecodeError:continue
            try:d=csv.Sniffer().sniff(s[:8192],delimiters=",;\t")
            except csv.Error:d="excel-tab" if ext==".tsv" else "excel"
            rr=csv.reader(io.StringIO(s),d);out["table"]=structural_table(next(rr,[]),rr);out["encoding"]=enc
        elif ext in (".xlsx",".xlsm"):
            wb=load_workbook(io.BytesIO(b),read_only=True,data_only=True)
            out["sheets"]=[]
            for w in wb.worksheets:
                it=iter(w.values);out["sheets"].append({"name":w.title,**structural_table(next(it,[]),it)})
            wb.close()
        elif ext==".xls":
            import xlrd
            wb=xlrd.open_workbook(file_contents=b,on_demand=True)
            out["sheets"]=[]
            for w in wb.sheets():
                out["sheets"].append({"name":w.name,**structural_table(w.row_values(0) if w.nrows else [],(w.row_values(i) for i in range(1,w.nrows)))})
            wb.release_resources()
        elif ext==".zip" and depth<2:
            with zipfile.ZipFile(io.BytesIO(b)) as z:
                if sum(v.file_size for v in z.infolist())>150_000_000:raise ValueError("bounded expanded-size limit")
                if z.testzip() is not None:raise ValueError("corrupt ZIP")
                out["members"]=[inventory(v.filename,z.read(v),depth+1) for v in z.infolist() if not v.is_dir()]
        elif ext==".geojson":
            j=json.loads(b);fs=j.get("features",[])
            out["gis"]={"feature_count":len(fs),"geometry_types":sorted({str((f.get("geometry") or {}).get("type")) for f in fs}),
             "properties":sorted({k for f in fs for k in (f.get("properties") or {})}),"declared_crs":j.get("crs","GeoJSON standard default WGS84; verify")}
        elif ext==".prj":
            out["crs_text"]=b.decode("utf-8",errors="strict")
        elif ext==".shp":
            import shapefile
            # Shape geometry inventory; attributes/CRS reviewed via companion files.
            r=shapefile.Reader(shp=io.BytesIO(b));out["gis"]={"geometry_type":r.shapeTypeName,"bbox":list(r.bbox),"shape_count":sum(1 for _ in r.iterShapes())}
        elif ext==".dbf":
            import shapefile
            r=shapefile.Reader(dbf=io.BytesIO(b));out["gis"]={"record_count":r.numRecords,"fields":[str(f[0]) for f in r.fields]}
    except Exception as e:out["inspection_error"]=str(e)
    return out
def plants():
    r={"doi":DOI,"api":API,"status":"SOURCE_BLOCKED","files":[]}
    try:
        dc=json.loads(get(DC,2_000_000))["data"]["attributes"]
        r["datacite"]={k:dc.get(k) for k in ("doi","titles","publicationYear","url","relatedIdentifiers")}
    except Exception as e:r["datacite_error"]=str(e)
    try:
        j=json.loads(get(API,2_000_000))
        r["record"]={k:j.get(k) for k in ("id","doi","title","description","published_date","version","license","url_public_html")}
        if str(j.get("id"))!="18282695" or str(j.get("doi","")).split(".v")[0].lower()!=DOI.lower():raise ValueError("identity mismatch")
        if not j.get("files"):raise ValueError("no publisher files")
        for f in j["files"]:
            item={"name":f.get("name"),"id":f.get("id"),"expected_md5":f.get("computed_md5") or f.get("supplied_md5"),"expected_bytes":f.get("size"),"url":f.get("downloadUrl")};r["files"].append(item)
            try:
                url=item["url"]
                if not url or not url.startswith("https://"):raise ValueError("missing HTTPS download")
                b=get(url)
                if item["expected_bytes"] is not None and len(b)!=item["expected_bytes"]:raise ValueError("size mismatch")
                if not item["expected_md5"] or hashlib.md5(b).hexdigest()!=item["expected_md5"]:raise ValueError("MD5 missing or mismatch")
                item.update(verified=True,inventory=inventory(item["name"],b))
            except Exception as e:item.update(verified=False,error=str(e))
        r["status"]="PUBLISHER_FILES_VERIFIED_SCHEMA_REVIEW_REQUIRED" if all(f.get("verified") for f in r["files"]) else "PARTIAL_SOURCE_BLOCKED"
    except Exception as e:r["error"]=str(e)
    return r
def map_source(out):
    r={"url":MAP,"status":"MAP_UNAVAILABLE"}
    try:
        b=get(MAP,25_000_000);r["sha256"]=sha(b);r["bytes"]=len(b)
        d=fitz.open(stream=b,filetype="pdf")
        if "10.1111/gcb.70290" not in "".join(p.get_text() for p in d[:2]).lower():raise ValueError("PDF identity")
        pages=[i for i,p in enumerate(d) if re.search(r"FIGURE\s*2\s*[|]",p.get_text(),re.I) and "six zones" in p.get_text().lower()]
        r["candidate_pages_zero_based"]=pages
        if len(pages)!=1:raise ValueError("figure page not unique")
        p=d[pages[0]];r["figure_page_images"]=len(p.get_images())
        p.get_pixmap(matrix=fitz.Matrix(2,2)).save(out/"seal_map_page.png")
        r["status"]="PUBLISHED_MAP_PAGE_RENDERED_MANUAL_GEOREFERENCE_REQUIRED"
        r["zone_geometry_verified"]=False
    except Exception as e:r["error"]=str(e)
    return r
def main():
    p=argparse.ArgumentParser();p.add_argument("--out",type=Path,required=True);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
    r={"status":"SOURCE_GATE_ONLY","plant_seal_join_executed":False,"plants":plants(),"seal_map":map_source(a.out)}
    try:
        b=get(GEO);r["land_cover_reference"]={"doi":"10.5285/af80c82c-b6a0-4978-92e0-efe063c390af","inventory":inventory("landcover.zip",b),"use":"2020 surface and geographic reference, not vegetation outcome"}
    except Exception as e:r["land_cover_reference"]={"error":str(e)}
    (a.out/"source_receipt.json").write_text(json.dumps(r,indent=2,ensure_ascii=False)+"\n")
    print(json.dumps(r,ensure_ascii=False))
if __name__=="__main__":main()
