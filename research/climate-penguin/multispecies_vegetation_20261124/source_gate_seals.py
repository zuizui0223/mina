"""Read-only original Dryad + Plantarctica source gate (no ecological response fit).
Run python source_gate_seals.py OUTDIR. Never treat a failed download as absence.
"""
import csv, hashlib, io, json, pathlib, sys, urllib.request, urllib.error, zipfile
from urllib.parse import quote, urljoin
from concurrent.futures import ThreadPoolExecutor

OUT=pathlib.Path(sys.argv[1]); OUT.mkdir(parents=True,exist_ok=True)
DRYAD="https://datadryad.org/api/v2/datasets/"+quote("doi:10.5061/dryad.qv9s4mwp0",safe="")
PLANT="https://api.figshare.com/v2/file/download/43483098"
MAP="https://www.env.go.jp/nature/nankyoku/kankyohogo/database/jyouyaku/aspa/aspa_pdf_en/113.pdf"
MAX=40*1024*1024
NAMES=("drone_survey_dates_times.csv","fur_seal_locations_all_surveys.csv","fur_seal_locations_d72_d46.csv","exposed_land_mask.zip","surveyed_regions_land_mask.zip","satellite_dem_mosaicked_masked.zip","maxent_prediction.zip")
def retrieve(name,url,kind):
    r={"name":name,"url":url,"status":"failed"}
    try:
        req=urllib.request.Request(url,headers={"User-Agent":"mina-research-source-audit/1.0","Accept":"application/json" if kind=="json" else "*/*"})
        with urllib.request.urlopen(req,timeout=35) as resp:
            raw=resp.read(MAX+1)
            r.update(status_code=resp.status,final_url=resp.geturl(),bytes=len(raw),content_type=resp.headers.get("Content-Type",""))
        if not raw or len(raw)>MAX: raise ValueError("empty or above bounded size")
        if kind=="json": json.loads(raw)
        if kind=="zip" and not zipfile.is_zipfile(io.BytesIO(raw)): raise ValueError("not a ZIP; possible authorization/error page")
        if kind=="pdf" and not raw.lstrip().startswith(b"%PDF-"): raise ValueError("not PDF")
        r.update(status="retrieved",sha256=hashlib.sha256(raw).hexdigest())
        (OUT/name).write_bytes(raw)
    except Exception as exc:
        r["error"]=f"{type(exc).__name__}: {str(exc)[:300]}"
    return r
def main():
    sources=[("dryad_metadata.json",DRYAD,"json"),("dryad_versions.json",DRYAD+"/versions","json"),
             ("dryad_original.zip",DRYAD+"/download","zip"),("plantarctica_original.zip",PLANT,"zip"),
             ("aspa113_2014.pdf",MAP,"pdf")]
    with ThreadPoolExecutor(max_workers=3) as pool: receipts=list(pool.map(lambda v:retrieve(*v),sources))
    result={"status":"SOURCE_GATE_NOT_PASSED","receipts":receipts,"dryad_expected_members":list(NAMES),"files":{},"limitations":["Source support only; no vegetation trend or causal response estimated.","Litchfield not surveyed in 2020; predicted MaxEnt raster is not seal observations.","Never replace actual positions with published table coordinates or a point buffer."]}
    dp=OUT/"dryad_original.zip"
    if dp.exists():
        try:
            with zipfile.ZipFile(dp) as z:
                members={pathlib.PurePosixPath(n).name:n for n in z.namelist() if not n.endswith("/")}
                result["dryad_members"]=sorted(members)
                for name in NAMES:
                    if name not in members: continue
                    b=z.read(members[name])
                    record={"bytes":len(b),"sha256":hashlib.sha256(b).hexdigest()}
                    if name.endswith(".csv"):
                        reader=csv.DictReader(io.StringIO(b.decode("utf-8-sig")))
                        record["columns"]=reader.fieldnames
                        record["rows"]=sum(1 for row in reader)
                    else:
                        with zipfile.ZipFile(io.BytesIO(b)) as inner: record["members"]=inner.namelist()
                    result["files"][name]=record
                result["all_seal_source_members_present"]=all(n in result["files"] for n in NAMES)
        except Exception as exc: result["dryad_schema_error"]=f"{type(exc).__name__}: {exc}"
    plant=OUT/"plantarctica_original.zip"
    result["plantarctica_sha_matches_previous_original"]=plant.exists() and hashlib.sha256(plant.read_bytes()).hexdigest()=="7e304e7a610d03287577e91faff05c009cf82039ae5f227763c37730a548a236"
    if result.get("all_seal_source_members_present") and result["plantarctica_sha_matches_previous_original"]:
        result["status"]="SOURCE_BYTES_AND_SCHEMA_INVENTORY_PASS_SPATIAL_QA_PENDING"
    (OUT/"receipt.json").write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))
    return 0 if result["status"].startswith("SOURCE_BYTES") else 2
if __name__=="__main__": sys.exit(main())
