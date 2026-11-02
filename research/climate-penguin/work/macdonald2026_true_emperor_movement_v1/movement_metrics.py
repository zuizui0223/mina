#!/usr/bin/env python3
"""Reconstruct actual published emperor colony group-location change from 2017–2024.

Macdonald et al. (2026) archived date-stamped WGS84 MultiPoint group positions
at Atka, Coulman and Washington. A MultiPoint centroid is an OBSERVED group
distribution's arithmetic centroid, not an identified penguin group or single
physical colony and not a per-breeder movement measurement.
Recompute directly from the downloaded source ZIP after inspect.py.
No new dependencies, no fabricated time-series for the LaRue 50-colony panel.
"""
from collections import Counter, defaultdict
from datetime import date
from itertools import combinations
from pathlib import Path
import csv, hashlib, json, math, statistics, zipfile
from probe import OUT, ID, DATA_DOI

# Script name inspect.py shadows stdlib inspect; use relative-local import via existing module.
# The executing Python file directory is first sys.path, so inspect imports this repo's parser.
from inspect import dbf_read, shape_read

EXPECTED_CANONICAL_SHA256 = "e697c1f76056d5e77646d1bfcf484ffe64e00685a1913964ca753d7094f4f105"
COLONIES = ("Atka","Coulman","Washington")
YEARS = tuple(range(2017,2025))

def distkm(a,b):
    lat1,lon1=a;lat2,lon2=b
    phi1,phi2=math.radians(lat1),math.radians(lat2)
    dphi=phi2-phi1
    dl=math.radians((lon2-lon1+180)%360-180)
    h=math.sin(dphi/2)**2+math.cos(phi1)*math.cos(phi2)*math.sin(dl/2)**2
    return 12742*math.atan2(math.sqrt(max(0,h)),math.sqrt(max(0,1-h)))

def centroid(group):
    if not group: return None
    # Original 3 Antarctic colonies are far from ±180 crossing; validate this.
    lons=[float(x) for x,y in group]
    if max(lons)-min(lons)>90: raise ValueError("Longitude-wrap centroid would be invalid")
    return (statistics.mean(float(y) for x,y in group),
            statistics.mean(lons))

def med(x):
    return statistics.median(x) if x else None

def write_csv(path,rows):
    if not rows: raise ValueError("Empty "+path)
    cols=list(rows[0])
    with (OUT/path).open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=cols)
        w.writeheader()
        w.writerows(rows)

def closest(dates,month,day):
    target=date(dates[0]["year"],month,day)
    return min(dates,key=lambda x:(abs((x["date"]-target).days),x["date"]))

def main():
    src=OUT/"dataset_zip.zip"
    if not src.is_file(): raise FileNotFoundError("Original Macdonald 2026 archive not present, run probe.py first")
    rootsha=hashlib.sha256(src.read_bytes()).hexdigest()
    all_samples=defaultdict(list)
    annual=[]
    summary_observations=[]
    all_species={"Atka":"ATKA","Coulman":"COUL","Washington":"WASH"}
    with zipfile.ZipFile(src) as z:
        names=sorted(n for n in z.namelist() if not n.endswith("/"))
        checksum=hashlib.sha256()
        for name in names:
            data=z.read(name)
            checksum.update(len(name).to_bytes(4,"big")+name.encode()+len(data).to_bytes(8,"big")+data)
        if checksum.hexdigest()!=EXPECTED_CANONICAL_SHA256:
            raise ValueError("Original author tracking zip contents changed: "+checksum.hexdigest())
        source_shps=sorted(n for n in names if n.lower().endswith(".shp"))
        if len(source_shps)!=24: raise ValueError("Expected exactly 24 original site×year shapefile cohorts")
        for path in source_shps:
            name=path.split("/")[-1].removesuffix(".shp")
            colony=name[:-(4)]
            year=int(name[-4:])
            if colony not in COLONIES or year not in YEARS:
                raise ValueError("Unexpected shapefile named site-year: "+path)
            stem=path[:-4]
            _,rows=dbf_read(z.read(stem+".dbf"))
            geom_type,_,_,geoms=shape_read(z.read(path))
            prj=z.read(stem+".prj").decode("utf-8","replace")
            if "WGS_1984" not in prj or len(geoms)!=len(rows):
                raise ValueError("Source CRS / DBF row count drift at "+name)
            if geom_type not in (8,18,28): raise ValueError("Not the original MultiPoint source "+name)
            for fieldrow,geom in zip(rows,geoms):
                dateStr=fieldrow.get("Date","")
                try: observed=date.fromisoformat(dateStr)
                except ValueError: raise ValueError("Original record lacked parsable date "+name+" / "+repr(dateStr))
                if observed.year!=year: raise ValueError("Year in original attributes != site shapefile: "+name)
                groups=geom["group_coordinates"]
                n=len(groups)
                if n==0: continue
                for x,y in groups:
                    if not (-90<y<-50 and -180<=x<=180):
                        raise ValueError("Malformed original penguin colony group coordinates")
                c=centroid(groups)
                if abs(c[0]-geom["y"])>1e-8 or abs(c[1]-geom["x"])>1e-8:
                    raise ValueError("Original source group-centroid parser bug")
                within=med([distkm(c,(lat,lon)) for lon,lat in groups])
                item={"colony":colony,"source_site_code":all_species[colony],"year":year,
                    "date":observed,"satellite":fieldrow.get("Satellite",""),
                    "group_count":n,"centroid":c,"within_group_median_radius_km":within,
                    "image_path":fieldrow.get("ImagePath","")}
                all_samples[(colony,year)].append(item)
                summary_observations.append({"colony":colony,"year":year,"date":observed.isoformat(),
                    "satellite":item["satellite"],"group_count":n,
                    "all_detected_group_centroid_lat":c[0],
                    "all_detected_group_centroid_lon":c[1],
                    "within_detected_group_med_radius_km":within})
    if len(all_samples)!=24 or len(summary_observations)!=1110: raise ValueError("Original observation count changed")
    # Collapse duplicate same-date observations to a single date-centroid to avoid
    # treating multiple satellites at the same calendar day as multiple temporal replicates.
    all_daily={}
    same_day_survey_pair_dist=[]
    for (colony,year),items in sorted(all_samples.items()):
        days=defaultdict(list)
        for item in items: days[item["date"]].append(item)
        daily=[]
        for d,images in sorted(days.items()):
            point=centroid([(x["centroid"][1],x["centroid"][0]) for x in images])
            intra=[distkm(a["centroid"],b["centroid"]) for a,b in combinations(images,2)]
            same_day_survey_pair_dist+=intra
            daily.append({"colony":colony,"year":year,"date":d,"centroid":point,
                "number_source_images":len(images),
                "median_detected_group_count":med([x["group_count"] for x in images]),
                "median_source_group_radius_km":med([x["within_group_median_radius_km"] for x in images]),
                "same_day_max_observation_centroid_difference_km":max(intra) if intra else None})
        all_daily[colony,year]=daily
        earliest,latest=daily[0],daily[-1]
        pairs=[(a,b,distkm(a["centroid"],b["centroid"])) for a,b in combinations(daily,2)]
        adj=[distkm(a["centroid"],b["centroid"]) for a,b in zip(daily[:-1],daily[1:])]
        longPairs=[z for a,b,z in pairs if (b["date"]-a["date"]).days>=30]
        earliestLatest=distkm(earliest["centroid"],latest["centroid"])
        selected9=closest(daily,9,15)
        selected10=closest(daily,10,15)
        annual.append({"colony":colony,"year":year,"source_site_code":all_species[colony],
            "source_date_stamped_image_observations":len(items),
            "unique_source_observation_dates":len(daily),
            "first_observed_date":earliest["date"].isoformat(),
            "last_observed_date":latest["date"].isoformat(),
            "source_observation_window_days":(latest["date"]-earliest["date"]).days,
            "first_last_detected_group_centroid_km":earliestLatest,
            "maximum_detected_group_centroid_separation_km":max(z for _,_,z in pairs) if pairs else 0,
            "median_adjacent_observation_centroid_shift_km":med(adj),
            "number_unique_day_pairs_at_least30days":len(longPairs),
            "maximum_separation_over30days_km":max(longPairs) if longPairs else None,
            "September15_nearest_day":selected9["date"].isoformat(),
            "September15_offset_days":abs((selected9["date"]-date(year,9,15)).days),
            "September15_centroid_lat":selected9["centroid"][0],
            "September15_centroid_lon":selected9["centroid"][1],
            "October15_nearest_day":selected10["date"].isoformat(),
            "October15_offset_days":abs((selected10["date"]-date(year,10,15)).days),
            "October15_centroid_lat":selected10["centroid"][0],
            "October15_centroid_lon":selected10["centroid"][1],
            "median_detected_group_count_at_source_observation":med([x["group_count"] for x in items]),
            "median_detected_group_radius_km":med([x["within_group_median_radius_km"] for x in items]),
            "source_detection_centroid_NOT_undistorted_colony_motion":True})
    annual.sort(key=lambda x:(x["colony"],x["year"]))
    transitions=[]
    for colony in COLONIES:
        group=sorted((x for x in annual if x["colony"]==colony),key=lambda x:x["year"])
        if len(group)!=8:raise ValueError("Expected full 8 years for every tracked colony")
        for a,b in zip(group[:-1],group[1:]):
            if b["year"]!=a["year"]+1:raise ValueError("Missing year")
            for season in ("September","October"):
                yr=a["year"]
                cutoff=15 if season=="September" else 10 # explicit season-specific matching quality gate
                anchor=(float(a[f"{season}15_centroid_lat"]),float(a[f"{season}15_centroid_lon"]))
                later=(float(b[f"{season}15_centroid_lat"]),float(b[f"{season}15_centroid_lon"]))
                gap=max(a[f"{season}15_offset_days"],b[f"{season}15_offset_days"])
                transitions.append({"colony":colony,"source_site_code":all_species[colony],
                    "start_year":a["year"],"end_year":b["year"],
                    "season_anchor":season+"15",
                    "first_source_date":a[f"{season}15_nearest_day"],
                    "second_source_date":b[f"{season}15_nearest_day"],
                    "maximum_day_offset_to_target":gap,
                    "season_comparable_within_window":gap<=cutoff,
                    "distance_detected_group_centroids_km":distkm(anchor,later),
                    "detected_group_center_shift_above_2km":distkm(anchor,later)>2,
                    "different_image_group_counts_possible":True,
                    "not_identified_as_same_individual_or_group":True})
    source_points=sum(x["group_count"] for x in summary_observations)
    if source_points!=3681:raise ValueError("Unexpected published group-point total")
    qualifying=[x for x in transitions if x["season_comparable_within_window"]]
    sep=[x for x in qualifying if x["season_anchor"]=="September15"]
    october=[x for x in qualifying if x["season_anchor"]=="October15"]
    within=[x["first_last_detected_group_centroid_km"] for x in annual]
    yearsSummary={}
    for colony in COLONIES:
        c=[x for x in annual if x["colony"]==colony]
        s=[x for x in sep if x["colony"]==colony]
        o=[x for x in october if x["colony"]==colony]
        yearsSummary[colony]={"annual_source_years":len(c),"source_image_observations":sum(x["source_date_stamped_image_observations"] for x in c),
            "first_last_withinyear_centroid_shift_median_km":med([x["first_last_detected_group_centroid_km"] for x in c]),
            "first_last_withinyear_centroid_shift_max_km":max(x["first_last_detected_group_centroid_km"] for x in c),
            "withinyear_first_last_over2km_n":sum(x["first_last_detected_group_centroid_km"]>2 for x in c),
            "year_pair_good_September_matches":len(s),
            "September_nearest15_betweenyear_median_km":med([x["distance_detected_group_centroids_km"] for x in s]),
            "September_nearest15_betweenyear_over2km_n":sum(x["detected_group_center_shift_above_2km"] for x in s),
            "year_pair_good_October_matches":len(o),
            "October_nearest15_betweenyear_median_km":med([x["distance_detected_group_centroids_km"] for x in o]),
            "October_nearest15_betweenyear_over2km_n":sum(x["detected_group_center_shift_above_2km"] for x in o)}
    facts={"author_dataset_DOI":DATA_DOI,"original_canonical_source_checksum":EXPECTED_CANONICAL_SHA256,
        "source_tracked_colonies":len(COLONIES),"original_year_site_files":len(annual),
        "original_observation_date_records":len(summary_observations),"original_group_point_positions":source_points,
        "distinct_siteyear_days":sum(x["unique_source_observation_dates"] for x in annual),
        "siteyears_with_first_last_centroid_shift_gt2km":sum(x>2 for x in within),
        "siteyears_with_first_last_centroid_shift_gt1km":sum(x>1 for x in within),
        "withinyear_first_last_shift_median_km":med(within),
        "betweenyear_all_21_pairs":len([x for x in transitions if x["season_anchor"]=="September15"]),
        "September15_quality_matched_pairs":len(sep),
        "September15_quality_pair_above_2km":sum(x["detected_group_center_shift_above_2km"] for x in sep),
        "October15_quality_matched_pairs":len(october),
        "October15_quality_pair_above_2km":sum(x["detected_group_center_shift_above_2km"] for x in october),
        "same_day_multi_image_pair_n":len(same_day_survey_pair_dist),
        "same_day_multi_image_difference_median_km":med(same_day_survey_pair_dist)}
    OUT.mkdir(parents=True,exist_ok=True)
    write_csv("original_24siteyears_detected_colony_group_centroid_metrics.csv",annual)
    write_csv("original_1110_date_stamped_colony_observations.csv",summary_observations)
    write_csv("actual_colony_group_centroid_betweenyear_21_pairs_two_seasons.csv",transitions)
    (OUT/"movement_metrics_summary.json").write_text(json.dumps({"source_info":{
        "tracking_DOI":DATA_DOI,"source_SHA256_bytes":rootsha,"source_canonical_SHA256":EXPECTED_CANONICAL_SHA256,
        "source_method":"published WGS84 MultiPoint of one or more emperor breeding group detections per date",
        "not_author_50_colony_census_sample":"This 3-site observed group footprint panel is not the 50-site 2009–2018 LaRue abundance model"},
        "facts":facts,"by_colony":yearsSummary,
        "measurement_caveats":["MultiPoint centroids give detectable group-location centroid per survey; exact group identity is not matched across dates",
        "Changes in groups detected or imagery footprint affect centroid; same-day multi-image divergence is an empirical observation-quality check",
        "September/October nearest-image matched contrasts control observation time of year only approximately",
        "The three original colonies span eight years and do not establish substrate causal effect against terrestrial breeding"],
        "not_future_demographic_forecast":True},ensure_ascii=False,indent=2)+"\n")
    print("MACDONALD ORIGINAL DETECTED-GROUP MOVEMENT METRICS "+json.dumps({"facts":facts,"by_colony":yearsSummary,
        "sept_between_year":sep,"oct_between_year":october},ensure_ascii=False),flush=True)

if __name__=="__main__":main()
