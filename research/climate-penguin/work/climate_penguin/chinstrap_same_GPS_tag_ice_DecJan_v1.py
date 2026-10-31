"""Within identical original GPS deployment IDs: Dec T vs Jan T+1 satellite SIC.

Source-only paired diagnostic, not daily ice, ocean navigability, prey capture
or an independent climatic population sample. Never mix unmatched birds
into a synthetic temporal trend or turn missing tags into zero ice.
"""
from __future__ import annotations
import argparse,csv,json,math,statistics
from collections import defaultdict
from pathlib import Path
EXPECTED_2013={"SI":2,"PI":10}
ISLANDS=("LI","MI","PI","SI")
ORIG_DOI="10.15770/EUM_SAF_OSI_0023"

def read(path):
    with Path(path).open(newline="",encoding="utf-8") as f:return list(csv.DictReader(f))

def paired(rows):
    chosen=[r for r in rows if
            r["nearest_monthly_satellite_ocean_radius_km"]=="20.0" and
            r["strict_publisher_quality_flags"]=="False"]
    if not chosen:raise ValueError("No primary original satellite-GPS source pairs")
    unique={}
    for r in chosen:
        key=(r["site"],int(r["breeding_season"]),r["original_source_tag"],
             int(r["source_year"]),int(r["source_month"]))
        if key in unique:raise ValueError("Duplicate source tag-month")
        unique[key]=r
    out=[]
    for (site,year,tag,ym,month),r in sorted(unique.items()):
        if month!=12 or ym!=year:continue
        later=unique.get((site,year,tag,year+1,1))
        if later is None:continue
        if not (r["mean_observed_monthly_SIC_percent_at_GPS"] and
                later["mean_observed_monthly_SIC_percent_at_GPS"]):
            # Actual 0.0 values are valid text, unlike empty fields.
            continue
        dec=float(r["mean_observed_monthly_SIC_percent_at_GPS"])
        jan=float(later["mean_observed_monthly_SIC_percent_at_GPS"])
        out.append({
            "original_island":site,"season_start":year,"original_GPS_source_tag":tag,
            "dec_calendar_month":f"{year}-12","jan_calendar_month":f"{year+1}-01",
            "source_dec_valid_hourly_GPS":int(r["n_GPS_hours_with_valid_source_sic"]),
            "source_jan_valid_hourly_GPS":int(later["n_GPS_hours_with_valid_source_sic"]),
            "dec_original_OSI_monthly_SIC_percent":dec,
            "jan_original_OSI_monthly_SIC_percent":jan,
            "jan_minus_dec_SIC_percentage_points":jan-dec,
            "source_months_and_GPS_locations_differ":True,
            "same_original_instrument_tag_not_independent_year_or_prey_source":True
        })
    if not out:raise ValueError("No true same-source-tag Dec/Jan overlap")
    groups=defaultdict(list)
    for r in out:groups[r["original_island"],r["season_start"]].append(r)
    summary=[]
    for (site,year),group in sorted(groups.items()):
        diffs=[r["jan_minus_dec_SIC_percentage_points"] for r in group]
        summary.append({
            "original_island":site,"season_start":year,
            "n_identical_source_GPS_tags_observed_both_months":len(group),
            "paired_original_tag_mean_dec_OSI_SIC_percent":statistics.mean(
                r["dec_original_OSI_monthly_SIC_percent"] for r in group),
            "paired_original_tag_mean_jan_OSI_SIC_percent":statistics.mean(
                r["jan_original_OSI_monthly_SIC_percent"] for r in group),
            "paired_mean_jan_minus_dec_SIC_percentage_points":statistics.mean(diffs),
            "n_source_tags_with_monthly_SIC_decrease":sum(x<0 for x in diffs),
            "year_month_GPS_routes_not_constant_and_ice_not_daily":True
        })
    expected=EXPECTED_2013
    for site,n in expected.items():
        entry=next((r for r in summary if r["original_island"]==site
                  and r["season_start"]==2013),None)
        if entry is None or entry["n_identical_source_GPS_tags_observed_both_months"]!=n:
            raise ValueError("Original 2013 same-tag GPS December–January support changed")
    return out,summary

def write(path,rows):
    with Path(path).open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--tag-month",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    a=p.parse_args();rows,summary=paired(read(a.tag_month))
    a.out.mkdir(parents=True,exist_ok=True)
    write(a.out/"source_same_tag_Dec_Jan_SIC.csv",rows)
    write(a.out/"same_tag_island_year_monthly_SIC_summary.csv",summary)
    (a.out/"same_tag_temporal_gate.json").write_text(json.dumps({
       "status":"ORIGINAL_GPS_DEPLOYMENT_DEC_JAN_MONTHLY_SIC_PAIRED_NOT_DAILY_ICE",
       "source_sic_DOI":ORIG_DOI,"n_original_paired_tag_rows":len(rows),
       "source_Signy_2013_paired_tags":2,"source_Powell_2013_paired_tags":10,
       "source_island_year_results":summary,
       "limitations":[
           "Only two same-source tags in Signy Dec2013-Jan2014; cannot infer population winter-to-summer effects.",
           "The same GPS bird may visit different model cells in December and January; temporal change need not reflect melting at identical coordinates.",
           "OSI satellite 25km monthly averages not daily GPS ice accessibility or true krill and feeding.",
           "No independent biological effects or future nest counts calibrated."
       ]
    },indent=2,ensure_ascii=False)+"\n")
    print(json.dumps({"status":"PAIRED_SOURCE_MONTH_SUPPORT_VERIFIED","summary":summary},ensure_ascii=False))
if __name__=="__main__":main()
