#!/usr/bin/env python3
"""Original EN4 in-situ salinity test for the 2019/2020 GLORYS source-year hold.

Fixed 2017-2018 vs 2019-2020 Aug-Nov; publisher original *raw* profiles,
not gridded EN4 estimates and not GLORYS. Reject comparisons lacking
same-region, same-month, adequate distinct-instrument support.
Do not redistribute individual profile salinities or platform identifiers.
"""
from __future__ import annotations
import argparse, hashlib, importlib.util, io, json, re, sys, zipfile
from collections import Counter, defaultdict
from pathlib import Path
import numpy as np
import netCDF4

ROOT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location(
    "en4_source_2015", ROOT/"pilot_EN4_2015_raw_profile_salinity_coverage.py")
en4=importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(en4)

YEARS=(2017,2018,2019,2020)
MONTHS=(8,9,10,11)
DEPTHS=(10,20)
RADII=(100,250)
MIN_PLATFORMS=3
MIN_MONTHS=2
BASE=en4.BASE
# Existing first-party 2015 source reader uses byte ranges with a 600 MB cap
# for each annual archive, and checks original monthly CRC32 and SHA256.
def parse_month(raw,year,month,sites):
    observations=[]
    metrics=Counter()
    with netCDF4.Dataset("en4_original_month",memory=raw) as d:
        required=en4.SOURCE_DIMS
        if any(k not in d.variables for k in required):
            raise ValueError("Original EN4 NetCDF profile schema drift")
        lat=np.asarray(np.ma.filled(d.variables["LATITUDE"][:],np.nan),float).reshape(-1)
        lon=np.asarray(np.ma.filled(d.variables["LONGITUDE"][:],np.nan),float).reshape(-1)
        matches=en4.coordinates_nearest_to_original_colonies(sites,lat,lon)
        metrics["global_profiles"]=len(lat)
        metrics["within_250km_pre_QC"]=len(matches)
        for index,(site,distance) in matches.items():
            if en4.letter(d.variables["POSITION_QC"][index])!="1":
                metrics["rejected_position_QC"]+=1
                continue
            if en4.letter(d.variables["PROFILE_PSAL_QC"][index])!="1":
                metrics["rejected_profile_QC"]+=1
                continue
            depths=np.asarray(np.ma.filled(d.variables["DEPH_CORRECTED"][index,:],np.nan),float).reshape(-1)
            salts=np.asarray(np.ma.filled(d.variables["PSAL_CORRECTED"][index,:],np.nan),float).reshape(-1)
            flags=np.asarray(d.variables["PSAL_CORRECTED_QC"][index,:]).reshape(-1)
            accepted=np.array([en4.letter(v)=="1" for v in flags],dtype=bool)
            valid=(accepted & np.isfinite(depths) & np.isfinite(salts) &
                   (depths>=0) & (salts>=28) & (salts<=38))
            if not valid.any():
                metrics["rejected_no_valid_shallow_salt_level"]+=1
                continue
            project=en4.original_profile_metadata_text(d,"PROJECT_NAME",index)
            platform=en4.original_profile_metadata_text(d,"PLATFORM_NUMBER",index)
            family=en4.instrument_family(project)
            # Never write source platform identifiers to disk or GitHub.
            identifier=family+"|"+platform if platform else ""
            for depthmax in DEPTHS:
                idx=np.flatnonzero(valid & (depths<=depthmax))
                if len(idx)==0:
                    continue
                j=idx[np.argmin(depths[idx])]
                observations.append({
                    "year":int(year),"month":int(month),"region":site["source_region"],
                    "depthmax":int(depthmax),"distance_km":float(distance),
                    "salinity":float(salts[j]),"sample_depth_m":float(depths[j]),
                    "family":family,"platform_private":identifier
                })
                metrics["QC_valid_depth_le_"+str(depthmax)]+=1
    return observations,dict(metrics)

def summarize(obs):
    """One instrument has one average within each region×year×month cell."""
    results=[]
    for radius in RADII:
        for depth in DEPTHS:
            sub=[r for r in obs if r["distance_km"]<=radius and r["depthmax"]==depth]
            groups=defaultdict(list)
            for o in sub:
                groups[(o["region"],o["year"],o["month"])].append(o)
            # Include only supported observed cells, and never treat missing as zero.
            for (reg,year,month),rows in sorted(groups.items()):
                platforms=defaultdict(list)
                for row in rows:
                    if row["platform_private"]:
                        platforms[row["platform_private"]].append(row["salinity"])
                means=[float(np.mean(x)) for x in platforms.values()]
                ready=len(means)>=MIN_PLATFORMS and len(rows)>=MIN_PLATFORMS
                results.append({
                    "source_region":reg,"year":year,"month":month,
                    "radius_km":radius,"depthmax_m":depth,
                    "n_actual_QC_profiles":len(rows),
                    "n_identified_platforms":len(platforms),
                    "n_unidentified_platform_profiles":len(rows)-sum(len(x) for x in platforms.values()),
                    "n_unique_instrument_families":len({x["family"] for x in rows}),
                    "support_ge_3_platforms":ready,
                    "platform_equal_mean_salinity_if_supported":float(np.mean(means)) if ready else None,
                    "platform_equal_sd_salinity_if_supported":float(np.std(means)) if ready else None,
                    "raw_profiles_never_archived":True,
                })
    # Evaluate one fixed, stringent 2017-18 vs 2019-20 test, not trend-picking.
    comparisons=[]
    cell_idx={(z["source_region"],z["year"],z["month"],z["radius_km"],z["depthmax_m"]):z
              for z in results}
    regions=sorted({r["region"] for r in obs})
    for radius in RADII:
        for depth in DEPTHS:
            for reg in regions:
                shared=[]
                for m in MONTHS:
                    four=[cell_idx.get((reg,y,m,radius,depth)) for y in YEARS]
                    if all(x is not None and x["support_ge_3_platforms"] for x in four):
                        shared.append(m)
                baseline=[cell_idx[(reg,y,m,radius,depth)]["platform_equal_mean_salinity_if_supported"]
                          for m in shared for y in (2017,2018)]
                recent=[cell_idx[(reg,y,m,radius,depth)]["platform_equal_mean_salinity_if_supported"]
                        for m in shared for y in (2019,2020)]
                eligible=len(shared)>=MIN_MONTHS
                comparisons.append({
                    "source_region":reg,"radius_km":radius,"depthmax_m":depth,
                    "n_four_year_months_with_ge3_platforms":len(shared),
                    "fully_matched_months":shared,
                    "supported_test":eligible,
                    "pre2019_platform_equal_month_average":float(np.mean(baseline)) if eligible else None,
                    "post2019_platform_equal_month_average":float(np.mean(recent)) if eligible else None,
                    "2019_2020_minus_2017_2018":float(np.mean(recent)-np.mean(baseline)) if eligible else None,
                    "not_equivalent_to_GLORYS_1993_2018_reference":True
                })
    return results,comparisons

def accepted_588_sites_from_frozen_climate_cohort(path):
    """Use previously source-validated original 588-site coordinates in this branch.

    Avoid an expired or inaccessible remote Actions artifact; do not infer
    latitude, longitude or missing sites from species presence.
    """
    import csv
    with path.open(encoding="utf-8",newline="") as h:
        original=list(csv.DictReader(h))
    required={"site_id","source_region","block","lat","lon"}
    if len(original)!=588 or any(not required.issubset(r) for r in original):
        raise ValueError("Fixed 588-site physical source coordinate roster changed")
    sites=[]
    for r in original:
        lat=float(r["lat"]);lon=float(r["lon"])
        if not (np.isfinite(lat) and np.isfinite(lon) and -90<=lat<=-55 and -180<=lon<=180):
            raise ValueError("Invalid original polar source coordinates")
        sites.append({"site_id":r["site_id"],"source_region":r["source_region"],
                      "source_250km_block":r["block"],
                      "colony_latitude":str(lat),"colony_longitude":str(lon)})
    if len({r["site_id"] for r in sites})!=588 or len({r["source_region"] for r in sites})!=18:
        raise ValueError("Original 588 climate site/18 source region roster drift")
    return sites

def make_receipts(geography,output):
    sites=accepted_588_sites_from_frozen_climate_cohort(geography)
    output.mkdir(parents=True,exist_ok=True)
    records=[];months=[];receipts=[]
    for year in YEARS:
        url=BASE+f"EN.4.2.2.profiles.g10.{year}.zip"
        head=en4.open_head(url)
        if head.get("status")!=200 or not head.get("size_bytes"):
            raise RuntimeError("Source annual EN4 ZIP unavailable: "+str(head))
        remote=en4.HTTPRangeZipReader(url,head["size_bytes"])
        annual={"year":year,"publisher_url":url,
                "publisher_year_zip_size_bytes":head["size_bytes"],
                "source_method":"verified HTTP206 original ZIP range",
                "whole_year_archive_SHA256_NOT_computed":True,
                "only_Aug_to_Nov_members_read":True,"months":[]}
        with zipfile.ZipFile(remote) as z:
            names=z.namelist()
            for month in MONTHS:
                matches=[x for x in names if re.search(r"\."+str(year)+f"{month:02d}"+r"\.nc$",x,re.I)]
                if len(matches)!=1:
                    raise ValueError("Original year ZIP missing unique NetCDF member: "+str((year,month)))
                name=matches[0];member=z.getinfo(name)
                src=z.read(name) # ZIP verifies original publisher CRC32
                observed,counts=parse_month(src,year,month,sites)
                records.extend(observed)
                months.append({"year":year,"month":month,"profile_QC_counts":counts})
                annual["months"].append({
                    "month":month,"original_ZIP_member":name,
                    "original_member_CRC32":f"{member.CRC:08x}",
                    "uncompressed_netCDF_sha256":hashlib.sha256(src).hexdigest(),
                    "uncompressed_netCDF_bytes":len(src),
                    "CRC32_checked_on_full_member":True
                })
                del src
                print("EN4_RAW_PROFILE_MONTH="+json.dumps(months[-1]),flush=True)
        annual["http206_requested_source_bytes"]=remote.bytes_transferred
        annual["http206_source_requests"]=remote.http_range_requests
        receipts.append(annual)
    cells,contrasts=summarize(records)
    strict=[x for x in contrasts if x["radius_km"]==100 and x["depthmax_m"]==10 and x["supported_test"]]
    from csv import DictWriter
    def write_csv(path,rows):
        if not rows:return
        with path.open("w",newline="") as h:
            writer=DictWriter(h,fieldnames=list(rows[0]))
            writer.writeheader();writer.writerows(rows)
    write_csv(output/"original_profile_region_year_month_observation_coverage.csv",cells)
    write_csv(output/"raw_salt_strict_platform_month_matched_contrasts.csv",contrasts)
    result={
        "source_product":"Met Office EN4.2.2 g10 original QC raw in-situ profile measurements",
        "years":list(YEARS),"months":list(MONTHS),
        "source_site_universe":595,"GLORYS_geography_eligible_sites":588,
        "n_original_reporting_regions":18,
        "n_QC_depth20_observations_within250km":len([x for x in records if x["depthmax"]==20]),
        "n_QC_depth10_observations_within100km":len([x for x in records if x["depthmax"]==10 and x["distance_km"]<=100]),
        "year_month_count_by_source":months,
        "n_regions_with_supported_strict_four_year_matched_comparison":len(strict),
        "strict_supported_region_comparisons":strict,
        "strict_evidence_status":"COMPARISON_SUPPORTED_IN_SOME_REGIONS" if strict else "NO_INDEPENDENT_TIME_MATCHED_STRICT_18REGION_TEST",
        "does_not_validate_an_18region_common_year_mode_without_18region_coverage":True,
        "does_not_have_1993_2018_multi_year_reference_period":True,
        "raw_profiles_and_identifiers_never_redistributed":True,
        "GLORYS_may_have_assimilated_some_of_these_real_instruments":True,
        "publisher_receipts":receipts
    }
    (output/"EN4_2017_2020_RAW_TIME_MATCH_SOURCE_GATE.json").write_text(
        json.dumps(result,indent=2,ensure_ascii=False)+"\n")
    print("EN4_2017_2020_SOURCE_VERDICT="+json.dumps({
        "n_sites":result["GLORYS_geography_eligible_sites"],
        "observations_100km_10m":result["n_QC_depth10_observations_within100km"],
        "regions_supported":len(strict),
        "strict_status":result["strict_evidence_status"]},ensure_ascii=False),flush=True)

def selftest():
    artificial=[]
    for region in ["A","B"]:
        for y in YEARS:
            for m in (8,9):
                for plat in range(3):
                    artificial.append({"region":region,"year":y,"month":m,"platform_private":f"fake{plat}",
                                      "salinity":34+plat/100-(0.3 if y>=2019 else 0),
                                      "distance_km":50,"depthmax":10,"family":"TEST","sample_depth_m":3})
    groups,comp=summarize(artificial)
    eligible=[z for z in comp if z["radius_km"]==100 and z["depthmax_m"]==10 and z["supported_test"]]
    assert len(eligible)==2 and all(abs(z["2019_2020_minus_2017_2018"]+0.3)<1e-10 for z in eligible)
    incomplete=[x for x in artificial if not (x["region"]=="B" and x["year"]==2020 and x["month"]==9)]
    _,comp2=summarize(incomplete)
    assert not [z for z in comp2 if z["source_region"]=="B" and z["radius_km"]==100 and z["depthmax_m"]==10 and z["supported_test"]]
    print("SYNTHETIC_AGGREGATE_QA_PASS")

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--geography",type=Path)
    p.add_argument("--out",type=Path)
    p.add_argument("--self-test",action="store_true")
    args=p.parse_args()
    selftest()
    if not args.self_test:
        if not args.geography or not args.out:
            p.error("--geography and --out required for original source")
        make_receipts(args.geography,args.out)
if __name__=="__main__":main()
