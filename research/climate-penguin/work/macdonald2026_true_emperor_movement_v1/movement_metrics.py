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
    source_label_vs_actual_date_year=Counter()
    first_mismatched_original_dates=[]
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
                if abs(observed.year-year)>1:
                    raise ValueError("Original source date unexpectedly outside ±1 calendar year: "+name+" "+dateStr)
                source_label_vs_actual_date_year[observed.year-year]+=1
                if observed.year!=year and len(first_mismatched_original_dates)<25:
                    first_mismatched_original_dates.append({"source_filename":name,"source_date":dateStr,"offset_from_filename_year":observed.year-year})
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
                    "image_path":fieldrow.get("ImagePath",""),"original_group_lon_lat":groups}
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
    # Stronger source-grounded stage comparison: separate winter (Apr–Aug) from
    # later spring (Oct–Nov) rather than treating Jan/Feb of the next calendar
    # year as an anomalous source date. Original season-year includes those dates.
    seasonal_rows=[]
    daily_stage_positions=[]
    all_stage_differences=[]
    for colony in COLONIES:
        for year in YEARS:
            days=all_daily[colony,year]
            winter=[x for x in days if x["date"].year==year and 4<=x["date"].month<=8]
            late=[x for x in days if x["date"].year==year and x["date"].month in (10,11)]
            if not winter:
                seasonal_rows.append({"colony":colony,"year":year,"early_winter_source_days":0,
                    "late_spring_source_days":len(late),"early_winter_ref_first3_dates":"",
                    "median_winter_group_centroid_distance_km":None,
                    "median_late_spring_group_centroid_distance_km":None,
                    "median_winter_grouppoint_distance_km":None,
                    "median_late_spring_group_point_distance_km":None,
                    "late_minus_winter_centroid_distance_km":None,
                    "late_minus_winter_group_point_distance_km":None,
                    "source_status":"missing_original_AprAug_reference"})
                continue
            winter.sort(key=lambda x:x["date"])
            base=centroid([(x["centroid"][1],x["centroid"][0]) for x in winter[:min(3,len(winter))]])
            samples_by_day=defaultdict(list)
            for im in all_samples[colony,year]:
                samples_by_day[im["date"]].append(im)
            for day in days:
                # Every group is a manually mapped detected sub-group, not an
                # identified track. Divide within each image by its own number
                # of groups so extra satellite scenes are not false abundance.
                imgs=samples_by_day[day["date"]]
                means=[]
                for im in imgs:
                    dd=[distkm(base,(float(lat),float(lon))) for lon,lat in im["original_group_lon_lat"]]
                    means.append(statistics.mean(dd))
                individual_mean=statistics.mean(means)
                season="winter_AprAug" if day["date"].year==year and 4<=day["date"].month<=8 else (
                    "late_spring_OctNov" if day["date"].year==year and day["date"].month in (10,11) else
                    "other_or_next_year")
                daily_stage_positions.append({"colony":colony,"season_year":year,
                    "observation_date":day["date"].isoformat(),"source_season":season,
                    "number_images":day["number_source_images"],
                    "median_detected_groups":day["median_detected_group_count"],
                    "group_centroid_distance_from_first3_winter_days_km":distkm(base,day["centroid"]),
                    "mean_detected_group_point_distance_from_first3_winter_days_km":individual_mean,
                    "original_group_identity_not_tracked":True})
            records=[x for x in daily_stage_positions if x["colony"]==colony and x["season_year"]==year]
            early=[x for x in records if x["source_season"]=="winter_AprAug"]
            late_rows=[x for x in records if x["source_season"]=="late_spring_OctNov"]
            wc=med([x["group_centroid_distance_from_first3_winter_days_km"] for x in early])
            lc=med([x["group_centroid_distance_from_first3_winter_days_km"] for x in late_rows])
            wp=med([x["mean_detected_group_point_distance_from_first3_winter_days_km"] for x in early])
            lp=med([x["mean_detected_group_point_distance_from_first3_winter_days_km"] for x in late_rows])
            source_status="paired_winter_and_late_spring" if len(late_rows)>=2 and len(early)>=2 else "limited_stage_support"
            rec={"colony":colony,"year":year,"early_winter_source_days":len(early),
                "late_spring_source_days":len(late_rows),
                "early_winter_ref_first3_dates":";".join(x["date"].isoformat() for x in winter[:3]),
                "median_winter_group_centroid_distance_km":wc,
                "median_late_spring_group_centroid_distance_km":lc,
                "median_winter_grouppoint_distance_km":wp,
                "median_late_spring_group_point_distance_km":lp,
                "late_minus_winter_centroid_distance_km":lc-wc if lc is not None else None,
                "late_minus_winter_group_point_distance_km":lp-wp if lp is not None else None,
                "source_status":source_status}
            seasonal_rows.append(rec)
            if source_status=="paired_winter_and_late_spring":all_stage_differences.append(rec)
    if len(seasonal_rows)!=24: raise ValueError("Original 3×8 seasonal support changed")
    write_csv("original_24siteyears_earlywinter_vs_latespring_movement.csv",seasonal_rows)
    write_csv("original_1075_daily_source_mapped_group_position_offsets.csv",daily_stage_positions)
    def percentile(x,p):
        if not x:return None
        a=sorted(x);i=(len(a)-1)*p;j=int(i)
        return a[j] if j>=len(a)-1 else a[j]+(i-j)*(a[j+1]-a[j])
    source_stage_summary={
       "original_source_years":24,
       "siteyears_with_winter_AprAug_reference":sum(x["early_winter_source_days"]>0 for x in seasonal_rows),
       "siteyears_with_latespring_OctNov_images":sum(x["late_spring_source_days"]>0 for x in seasonal_rows),
       "siteyears_paired_at_least2_days_each_stage":len(all_stage_differences),
       "paired_siteyears_late_spring_median_group_point_displacement_gt_winter":
          sum(x["late_minus_winter_group_point_distance_km"]>0 for x in all_stage_differences),
       "paired_siteyears_late_spring_median_centroid_displacement_gt_winter":
          sum(x["late_minus_winter_centroid_distance_km"]>0 for x in all_stage_differences),
       "paired_siteyears_late_minus_winter_median_group_point_difference_km":
          med([x["late_minus_winter_group_point_distance_km"] for x in all_stage_differences]),
       "paired_siteyears_late_minus_winter_median_centroid_difference_km":
          med([x["late_minus_winter_centroid_distance_km"] for x in all_stage_differences]),
       "same_day_mapped_centroid_difference_p95_km":percentile(same_day_survey_pair_dist,.95),
       "same_day_mapped_centroid_difference_max_km":max(same_day_survey_pair_dist),
       "source_days_with_multi_sensor_replicate_pairs":len(same_day_survey_pair_dist),
       "source_climate_covariate_absent":True,
    }

    # Baseline-free check: instead of measuring both seasons against a *winter*
    # reference point (which can inherently favor winter), compare adjacent
    # observation dates of similar elapsed duration within each season.
    baseline_free_adjacent_day_movement_speeds=[]
    baseline_free_season_comparison=[]
    for colony in COLONIES:
        for year in YEARS:
            days=all_daily[colony,year]
            site_recs=[]
            for before,after in zip(days[:-1],days[1:]):
                dt=(after["date"]-before["date"]).days
                if not 3<=dt<=14:continue
                def stageOf(x):
                    if x.year!=year:return "other"
                    if 4<=x.month<=8:return "winter_AprAug"
                    if x.month in (10,11):return "late_spring_OctNov"
                    return "other"
                period=stageOf(before["date"])
                if period=="other" or period!=stageOf(after["date"]):continue
                step=distkm(before["centroid"],after["centroid"])
                r={"colony":colony,"season_year":year,"stage":period,
                    "from_date":before["date"].isoformat(),"to_date":after["date"].isoformat(),
                    "day_difference":dt,"group_centroid_separation_km":step,
                    "group_centroid_separation_km_per_day":step/dt,
                    "same_observed_median_group_count":before["median_detected_group_count"]==after["median_detected_group_count"],
                    "multiple_source_images_on_either_date":before["number_source_images"]>1 or after["number_source_images"]>1,
                    "different_winter_SAR_vs_spring_optical_sensors_possible":True}
                baseline_free_adjacent_day_movement_speeds.append(r)
                site_recs.append(r)
            win=[x for x in site_recs if x["stage"]=="winter_AprAug"]
            spring=[x for x in site_recs if x["stage"]=="late_spring_OctNov"]
            valid=len(win)>=2 and len(spring)>=2
            r={"colony":colony,"season_year":year,"winter_3to14day_pairs":len(win),
                "late_spring_3to14day_pairs":len(spring),"both_stages_at_least2_pairs":valid,
                "winter_median_group_centroid_km_per_day":med([x["group_centroid_separation_km_per_day"] for x in win]),
                "late_spring_median_group_centroid_km_per_day":med([x["group_centroid_separation_km_per_day"] for x in spring]),
                "winter_source_same_detected_group_count_pairs":sum(x["same_observed_median_group_count"] for x in win),
                "late_spring_source_same_detected_group_count_pairs":sum(x["same_observed_median_group_count"] for x in spring),
                "stage_rate_difference_late_minus_winter_km_per_day":(
                    med([x["group_centroid_separation_km_per_day"] for x in spring])-
                    med([x["group_centroid_separation_km_per_day"] for x in win])) if valid else None,
                "sensor_and_group_count_detection_confounded":True}
            baseline_free_season_comparison.append(r)
    write_csv("source_same_3to14day_lag_observed_group_centroid_offsets.csv",baseline_free_adjacent_day_movement_speeds)
    write_csv("baseline_free_withinyear_winter_latespring_rate_comparison.csv",baseline_free_season_comparison)
    valid_pairs=[x for x in baseline_free_season_comparison if x["both_stages_at_least2_pairs"]]
    baseline_free_summary={
        "source_consecutive_3to14day_pairs":len(baseline_free_adjacent_day_movement_speeds),
        "winter_source_pairs":sum(x["stage"]=="winter_AprAug" for x in baseline_free_adjacent_day_movement_speeds),
        "latespring_source_pairs":sum(x["stage"]=="late_spring_OctNov" for x in baseline_free_adjacent_day_movement_speeds),
        "siteyears_paired_at_least2_short_lag_pairs_each_stage":len(valid_pairs),
        "siteyears_latespring_speed_greater_than_winter":sum(x["stage_rate_difference_late_minus_winter_km_per_day"]>0 for x in valid_pairs),
        "paired_median_latespring_minus_winter_km_per_day":med([x["stage_rate_difference_late_minus_winter_km_per_day"] for x in valid_pairs]),
        "caveat":"Stage-specific sensors (winter SAR vs spring optical), detection and group count differences; point-to-point apparent centroid velocity, not penguin locomotion."}
    # Direct source crosswalk: three original tracked 2017-2018 colony sites
    # are present as fixed IDs in the 50-colony Bayesian abundance panel.
    # This joint membership is source-grounded, but a n=3 descriptive join
    # cannot identify substrate movement causing abundance changes.
    author=Path("research/climate-penguin/outputs/emperor_ice_land_substrate_v1/author_colony_summary.csv")
    authorBytes=author.read_bytes()
    mHash=hashlib.sha1(b"blob "+str(len(authorBytes)).encode()+b"\0"+authorBytes).hexdigest()
    if mHash!="133c900c9dfbf2ce23ca403c9a59edecd9b51ace":raise ValueError("Original LaRue author model summary Git blob drift")
    sourceModel=list(csv.DictReader(authorBytes.decode("utf-8").splitlines()))
    if len(sourceModel)!=500:raise ValueError("LaRue model source panel drift")
    three_source_crosswalk=[]
    for colony in COLONIES:
        sitecode={"Atka":"ATKA","Coulman":"COUL","Washington":"WASH"}[colony]
        rows=[x for x in sourceModel if x["site_id"]==sitecode and int(x["year"]) in (2017,2018)]
        if len(rows)!=2:raise ValueError("Original 50-colony observed movement site-year overlap not recovered")
        start=next(x for x in rows if int(x["year"])==2017)
        end=next(x for x in rows if int(x["year"])==2018)
        if not (float(start["N_mean"])>0 and float(end["N_mean"])>0):
            raise ValueError("Expected positive modelled 2017–2018 population index both years")
        year2017=next(x for x in annual if x["colony"]==colony and x["year"]==2017)
        year2018=next(x for x in annual if x["colony"]==colony and x["year"]==2018)
        september=next(x for x in transitions if x["colony"]==colony and x["start_year"]==2017 and x["season_anchor"]=="September15")
        three_source_crosswalk.append({
            "colony":colony,"LaRue_author_50model_source_id":sitecode,
            "LaRue_2017_posterior_marginal_mean_adult_index":float(start["N_mean"]),
            "LaRue_2018_posterior_marginal_mean_adult_index":float(end["N_mean"]),
            "modelled_adult_index_change_pct":100*(float(end["N_mean"])/float(start["N_mean"])-1),
            "both_author_2017_and_2018_modelled_colony_indices_positive":True,
            "Macdonald_2017_earlylate_group_centroid_km":year2017["first_last_detected_group_centroid_km"],
            "Macdonald_2018_earlylate_group_centroid_km":year2018["first_last_detected_group_centroid_km"],
            "Macdonald_2017_to_2018_September_group_centroid_km":september["distance_detected_group_centroids_km"],
            "different_satellite_sensing_and_modelled_adult_index_estimand":True,
            "three_colony_join_not_a_population_motion_regression":True})
    write_csv("original_2017_2018_three_colony_movement_vs_modelled_adult_index_crosswalk.csv",three_source_crosswalk)

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
        "filename_year_minus_observation_year_distribution":dict(sorted(source_label_vs_actual_date_year.items())),
        "first_original_filename_date_mismatches":first_mismatched_original_dates,
        "earlywinter_vs_latespring_quality_gate":source_stage_summary,
        "baseline_free_short_lag_velocity_gate":baseline_free_summary,
        "three_original_tracked_colony_modelled_adult_index_crosswalk":three_source_crosswalk,
        "same_day_multi_image_pair_n":len(same_day_survey_pair_dist),
        "same_day_multi_image_difference_median_km":med(same_day_survey_pair_dist)}
    if "--check-receipt" in __import__("sys").argv:
        receipt=json.loads((OUT/"expected_receipt.json").read_text(encoding="utf-8"))
        if receipt["original_source_canonical_sha256"]!=EXPECTED_CANONICAL_SHA256:
            raise ValueError("Original doi-backed tracking source changed")
        for k,want in receipt["facts"].items():
            got=facts.get(k)
            if got is None:
                raise ValueError("Missing receipt field "+k)
            if isinstance(want,(float,int)):
                if abs(got-want)>1e-9:raise ValueError("Independent numeric receipt mismatch "+k+" "+str(got)+" != "+str(want))
            elif got!=want:raise ValueError("Independent receipt mismatch "+k)
        for k,want in receipt["baseline_free"].items():
            got=baseline_free_summary.get(k)
            if got is None or abs(got-want)>1e-9:raise ValueError("Independent baseline-free receipt mismatch "+k+" "+str(got))
        if receipt["original_2017_2018_crosswalk_names"]!=[x["LaRue_author_50model_source_id"] for x in three_source_crosswalk]:
            raise ValueError("Original observed tracking vs modelled 3 site IDs drift")
        if receipt["observational_paired_siteyear_expected"]!=len(all_stage_differences):
            raise ValueError("Original observed winter to spring sample size changed")

    OUT.mkdir(parents=True,exist_ok=True)
    write_csv("original_24siteyears_detected_colony_group_centroid_metrics.csv",annual)
    write_csv("original_1110_date_stamped_colony_observations.csv",summary_observations)
    write_csv("actual_colony_group_centroid_betweenyear_21_pairs_two_seasons.csv",transitions)
    (OUT/"movement_metrics_summary.json").write_text(json.dumps({"source_info":{
        "tracking_DOI":DATA_DOI,"source_SHA256_bytes":rootsha,"source_canonical_SHA256":EXPECTED_CANONICAL_SHA256,
        "source_method":"published WGS84 MultiPoint of one or more emperor breeding group detections per date",
        "not_author_50_colony_census_sample":"This 3-site observed group footprint panel is not the 50-site 2009–2018 LaRue abundance model"},
        "facts":facts,"withinyear_earlywinter_vs_latespring_siteyear":seasonal_rows,
        "by_stage":source_stage_summary,"baseline_free":baseline_free_summary,"modelled_index_2017_2018":three_source_crosswalk,"by_colony":yearsSummary,
        "measurement_caveats":["MultiPoint centroids give detectable group-location centroid per survey; exact group identity is not matched across dates",
        "Changes in groups detected or imagery footprint affect centroid; same-day multi-image divergence is an empirical observation-quality check",
        "September/October nearest-image matched contrasts control observation time of year only approximately",
        "The three original colonies span eight years and do not establish substrate causal effect against terrestrial breeding"],
        "not_future_demographic_forecast":True},ensure_ascii=False,indent=2)+"\n")
    print("MACDONALD ORIGINAL DETECTED-GROUP MOVEMENT METRICS "+json.dumps({"facts":facts,"stage_summary":source_stage_summary,"by_colony":yearsSummary,
        "sept_between_year":sep,"oct_between_year":october},ensure_ascii=False),flush=True)

if __name__=="__main__":main()
