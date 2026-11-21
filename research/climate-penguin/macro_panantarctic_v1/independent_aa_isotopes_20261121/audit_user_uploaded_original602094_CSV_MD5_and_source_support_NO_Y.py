#!/usr/bin/env python3
"""Verify native uploaded USAP-DC DOI10.15784/602094 ZIP and frozen annual support.

SOURCE-ONLY. Never calculate numerical isotope or trophic-position values.
User upload is passed as a CLI file path, not stored in git. No environmental
joining, no phenylalanine/bulk isotope or polynya regression.
"""
from __future__ import annotations
import argparse,csv,hashlib,io,json,zipfile
from collections import Counter
from pathlib import Path

NAME="usapdc_602094/Michelson_2026_Adelie_Feathers_SIA_CSIA_Data.csv"
ORIGINAL_MD5="f9a91c9d9bf3dba9607bf0767df8c206"
REQ=("Sample_ID","Species","Sample_type","Region","Area","Site",
     "Year_collected","Latitude","Longitude","Specimen_type",
     "d15N","Phe_d15N","Glu_d15N","Trophic_position")
VALUES=("d15N","Phe_d15N","Glu_d15N","Trophic_position")
BAD={"","NA","N/A","nan","NaN","None","NULL","null"}

def main(p,out):
    out.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(p) as z:
        if z.testzip() is not None:raise ValueError("Original ZIP native CRC error")
        files=[x for x in z.infolist() if not x.is_dir()]
        if len(files)!=1 or files[0].filename!=NAME:
            raise ValueError("Original uploaded DOI 602094 expected member does not match")
        raw=z.read(NAME)
        if hashlib.md5(raw).hexdigest()!=ORIGINAL_MD5:
            raise ValueError("Official publisher original CSV MD5 mismatch")
        csv_crc=f"{files[0].CRC:08x}"
    reader=csv.DictReader(io.StringIO(raw.decode("utf-8-sig")))
    if reader.fieldnames is None or len(reader.fieldnames)!=45 or not set(REQ).issubset(reader.fieldnames):
        raise ValueError("Original 602094 source CSV schema drift")
    rows=list(reader)
    if len(rows)!=108 or len({r["Sample_ID"] for r in rows})!=108:
        raise ValueError("Original 108 unique specimen source denominator drift")
    if {r["Species"].strip() for r in rows}!={"Adelie penguin"}:
        raise ValueError("Unexpected original biological species")
    if {r["Sample_type"].strip() for r in rows}!={"Breast feather"}:
        raise ValueError("Original feather tissue drift")
    if any("moult" in k.lower() or "molt" in k.lower() or "formation" in k.lower()
           or "feather_growth" in k.lower() for k in reader.fieldnames):
        raise ValueError("Potential actual feather production year now present: revisit frozen temporal gate")
    year=lambda r:int(r["Year_collected"])
    valid=lambda r,key:r[key].strip() not in BAD
    modern=[r for r in rows if 2000<=year(r)<=2016]
    eligible=[r for r in rows if 2004<=year(r)<=2010 or 2013<=year(r)<=2016]
    # Only the existence flags of the four measured outcomes; no numerical
    # values of trophic position, bulk or AA isotope are parsed.
    complete=[r for r in eligible if all(valid(r,k) for k in VALUES)]
    def counts(d):
        return {"samples":len(d),"site_collection_years":len({(r["Site"],year(r)) for r in d}),
          "source_site_labels":len({r["Site"] for r in d}),
          "source_region_names":sorted({r["Region"] for r in d}),
          "source_region_count":len({r["Region"] for r in d})}
    stages={"full_source":counts(rows),"modern_collection_years_2000_2016":counts(modern),
      "frozen_collection_years_2004_2010_or_2013_2016":counts(eligible),
      "complete_four_original_isotope_TP_columns":counts(complete)}
    if not(stages["modern_collection_years_2000_2016"]["samples"]==36
           and stages["frozen_collection_years_2004_2010_or_2013_2016"]["samples"]==25
           and stages["frozen_collection_years_2004_2010_or_2013_2016"]["site_collection_years"]==15
           and stages["complete_four_original_isotope_TP_columns"]["samples"]==10
           and stages["complete_four_original_isotope_TP_columns"]["site_collection_years"]==9
           and stages["complete_four_original_isotope_TP_columns"]["source_region_count"]==2):
        raise ValueError("Previously verified original data provenance/source support changed")
    siteyear={}
    for r in eligible:
        key=(r["Site"],year(r),r["Region"])
        if key not in siteyear: siteyear[key]={"Site":r["Site"],"Year_collected":year(r),
           "Region":r["Region"],"n_original_specimens":0,"n_with_four_isotope_TP_fields":0}
        siteyear[key]["n_original_specimens"]+=1
        siteyear[key]["n_with_four_isotope_TP_fields"]+=int(all(valid(r,k) for k in VALUES))
    all_s=[r for _,r in sorted(siteyear.items())]
    if len(all_s)!=15:raise ValueError("Original 15 site×collection year groups drift")
    with (out/"USAP602094_FROZEN_SITE_COLLECTION_YEAR_SOURCE_ONLY.csv").open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(all_s[0]));w.writeheader();w.writerows(all_s)
    n_yrs=Counter()
    for r in complete: n_yrs[(r["Site"],year(r))]=1
    by_site=Counter(site for site,_ in n_yrs)
    rec={"status":"REAL_OFFICIAL_SOURCE_MD5_VERIFIED_BUT_NO_GO_TP_POLYNYA_TEMPORAL_REGION_SUPPORT",
      "source_public_DOI":"10.15784/602094",
      "original_upload_name":p.name,
      "uploaded_ZIP_SHA256":hashlib.sha256(p.read_bytes()).hexdigest(),
      "publisher_CSV_MD5_verified":ORIGINAL_MD5,
      "native_original_CSV_SHA256":hashlib.sha256(raw).hexdigest(),
      "original_source_CSV_bytes":len(raw),"original_source_ZIP_member_CRC32":csv_crc,
      "original_source_108_by_45":True,"original_Adelie_breast_feathers":True,
      "specimen_types":dict(Counter(r["Specimen_type"] for r in rows)),
      "stages":stages,
      "frozen_gate_summary":{
         "at_least_20_unique_site_by_true_moult_years":False,
         "at_least_5_sites":len(by_site)>=5,
         "at_least_3_broad_independent_marine_regions":len({r["Region"] for r in complete})>=3,
         "at_least_3_sites_with_2_years":sum(n>=2 for n in by_site.values())>=3,
         "explicit_true_feather_moult_synthesis_year_available":False,
         "native_DEEPAA_environment_join_checked":False},
      "all_four_fields_checked_only_for_nonmissing_flags":list(VALUES),
      "no_numerical_isotope_or_TP_values_read":True,
      "no_persistent_original_raw_isotope_CSV_saved":True,
      "no_isotope_polynya_regression_run":True,
      "no_new_independent_foodweb_effect_claim":True}
    (out/"USAP602094_REAL_PUBLISHER_CSV_SOURCE_SUPPORT_GATE.json").write_text(
        json.dumps(rec,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps({"status":rec["status"],"support":stages,
       "all_frozen_gates":rec["frozen_gate_summary"]},indent=2,ensure_ascii=False))
if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--input-zip",type=Path,required=True)
    ap.add_argument("--out",type=Path,required=True)
    a=ap.parse_args()
    main(a.input_zip,a.out)
