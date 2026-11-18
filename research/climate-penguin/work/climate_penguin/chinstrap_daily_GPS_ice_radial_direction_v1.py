"""Daily satellite SIC in actual Chinstrap GPS path vs same-distance ocean rings.

Source: original BAS Chinstrap GPS v2 and original EUMETSAT OSI SAF OSI-450-a1
v3.1 daily SIC. Retain three original matched island-year pairs, all original
45 GPS-common days, full observed GPS and satellite source-quality support.

The comparison answers only: "Did satellite pixels near actually observed
GPS locations have more/less daily sea ice than other OSI-valid ocean pixels
at comparable colony-centre distance that same day?" It is NOT a test of
true penguin-reachable water, daily ice passage blockade, GPS-dive/feeding,
independent krill abundance or future nesting/population changes.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,math,statistics
from pathlib import Path
from collections import defaultdict
import numpy as np
import xarray as xr
import chinstrap_daily_ice_same_day_GPS_2013_v1 as satellite
import chinstrap_daily_SIC_three_island_year_pairs_v1 as original
import south_orkney_chinstrap_island_krill_v1 as colony
import signy_gps_krill_access_v1 as geodesic

PAIRS=((2011,"LI"),(2013,"PI"),(2015,"MI"))
DOI="10.15770/EUM_SAF_OSI_0023"
GPS_DOI="10.5285/8f8ccba5-01af-4b00-8a3b-c3c85b24bf92"
RADII=(20.,35.)
STRICT=(False,True)
RING_KM=25.
MAX_SOURCE_CELL_KM=175.
SIC_THRESHOLD=15.

def ring_means(values, source_indices, lat, lon, anchor):
    """Cos-latitude weighted source-native ocean SIC in 25km radial bins.

    All available bearings are considered. This does NOT measure movement
    paths that penguins could actually reach through ice or around coastlines.
    """
    indices=np.asarray(source_indices,dtype=np.int64)
    la=np.asarray(lat,dtype=float)[indices]
    lo=np.asarray(lon,dtype=float)[indices]
    v=np.asarray(values,dtype=float)[indices]
    dist=np.asarray(geodesic.geodesic(la,lo,anchor[0],anchor[1]),dtype=float)
    keep=(dist<=MAX_SOURCE_CELL_KM)&(dist>=0)&np.isfinite(v)&(v>=0)&(v<=100.0001)
    rings={}
    weights=np.cos(np.deg2rad(la[keep]))
    keys=np.floor(dist[keep]/RING_KM).astype(int)
    valid_idx=indices[keep]
    if len(valid_idx)<5:raise ValueError("No independent satellite valid-ocean radial background")
    for key in sorted(set(keys.tolist())):
        x=keys==key
        rings[int(key)]=float(np.average(v[keep][x],weights=weights[x]))
    return rings,{int(p):int(b) for p,b in zip(valid_idx,keys)},len(valid_idx)

def source_pixel_excess(observed,ring_of_pixel,reference):
    """Each original satellite pixel only once, not each hourly GPS fix."""
    values=[]
    background=[]
    for pixel,value in sorted(observed.items()):
        key=ring_of_pixel.get(int(pixel))
        if key is None or key not in reference:continue
        if not math.isfinite(value) or not 0<=value<=100.0001:
            raise ValueError("Nonphysical original daily SIC")
        values.append(float(value))
        background.append(reference[key])
    if not values:
        return {"n_matched_native_source_pixels":0,
                "mean_GPS_SIC_percent":None,
                "mean_same_day_same_radius_source_SIC_percent":None,
                "GPS_minus_radial_source_SIC_pp":None,
                "source_GPS_cells_SIC_ge15_fraction":None,
                "n_native_pixels_not_in_175km_source_background":len(observed)}
    return {
        "n_matched_native_source_pixels":len(values),
        "mean_GPS_SIC_percent":float(statistics.mean(values)),
        "mean_same_day_same_radius_source_SIC_percent":float(statistics.mean(background)),
        "GPS_minus_radial_source_SIC_pp":float(statistics.mean(values)-statistics.mean(background)),
        "source_GPS_cells_SIC_ge15_fraction":sum(x>=SIC_THRESHOLD for x in values)/len(values),
        "n_native_pixels_not_in_175km_source_background":len(observed)-len(values)}

def run(gps_zip,netcdf_folder,receipt):
    daypositions,pairdates,locked=original.original_source_days(gps_zip)
    records,_=colony.read_all_chinstrap(gps_zip)
    centers=colony.island_source_centers(records)
    days=sorted(set().union(*(set(pairdates[y,other]) for y,other in PAIRS)))
    receipts={x["date"]:x for x in receipt["source_original_daily_netcdfs"]}
    if set(days)!=set(receipts):raise ValueError("Original source daily files do not cover pre-frozen GPS days")
    if len(days)!=45 or len(centers)!=7:raise ValueError("Source 45-day/7-island-year data grain drift")
    coords_hash=None
    tagresults=[]
    annualresults=[]
    comparison=[]
    monthly=[]
    for year,other in PAIRS:
        for day in pairdates[year,other]:
            record=receipts[day]
            satellite_day=satellite.open_day(netcdf_folder/record["file"],record)
            with xr.open_dataset(netcdf_folder/record["file"]) as data:
                lat=np.asarray(data["lat"].values,dtype=float).ravel()
                lon=np.asarray(data["lon"].values,dtype=float).ravel()
            if len(lat)!=432**2 or len(lon)!=432**2:
                raise ValueError("Original OSI 25km geolocation grid shape drift")
            shape_hash=hashlib.sha256(lat.tobytes()+lon.tobytes()).hexdigest()
            if coords_hash is not None and coords_hash!=shape_hash:
                raise ValueError("Satellite native longitude/latitude grid changes across original days")
            coords_hash=shape_hash
            daily_tag_by_site={}
            for site in ("SI",other):
                center=centers[site,year]
                anchor=center["center_lat"],center["center_lon"]
                position_items=sorted((tag,p) for (site0,year0,tag,day0),p in daypositions.items()
                                      if (site0,year0,day0)==(site,year,day))
                if not position_items:
                    raise ValueError("Original pre-frozen GPS day lacks one paired island")
                daily_tag_by_site[site]=position_items
                for strict in STRICT:
                    quality="strict" if strict else "all"
                    means,bins,n_source=ring_means(
                        satellite_day["values"],satellite_day[quality+"_ids"],lat,lon,anchor)
                    for radius in RADII:
                        seen={}
                        candidate_count=0
                        raw_matching=0
                        source_pixel_exclusions=0
                        permitted=[]
                        for tag,points in position_items:
                            pixel_map=satellite.sample(satellite_day,points,radius,strict)
                            raw_matching+=len(pixel_map)
                            score=source_pixel_excess(pixel_map,bins,means)
                            candidate_count+=int(score["n_matched_native_source_pixels"]>0)
                            source_pixel_exclusions+=score["n_native_pixels_not_in_175km_source_background"]
                            row={
                                "season_start":year,"other_island":other,"GPS_calendar_date":day,
                                "island":site,"original_GPS_tag":tag,
                                "source_GPS_hourly_positions":len(points),
                                "nearest_original_satellite_pixel_limit_km":radius,
                                "strict_quality_flags":strict,"radial_background_bin_km":RING_KM,
                                "n_model_valid_source_ocean_background_pixels":n_source,
                                **score,
                                "unmeasured_accessible_ocean_and_dive_status":True}
                            tagresults.append(row)
                            if score["n_matched_native_source_pixels"]:
                                permitted.append(row)
                            for pixel,value in pixel_map.items():
                                if pixel not in bins:continue
                                if pixel in seen and not math.isclose(seen[pixel],value,abs_tol=1e-9):
                                    raise ValueError("Conflicting observed SIC for identical original native satellite cell")
                                seen[pixel]=value
                        score=source_pixel_excess(seen,bins,means)
                        # Unique-source-pixel is the conservative main unit;
                        # equal-tag means are for sampling-effort sensitivity.
                        tagdiffs=[r["GPS_minus_radial_source_SIC_pp"] for r in permitted]
                        result={
                            "season_start":year,"other_island":other,
                            "GPS_calendar_date":day,"island":site,
                            "nearest_original_satellite_pixel_limit_km":radius,
                            "strict_quality_flags":strict,
                            "n_original_GPS_tags_with_fixes":len(position_items),
                            "n_original_GPS_tags_with_eligible_satellite_cells":candidate_count,
                            "n_original_native_ocean_pixels_qualifying_before_175km":raw_matching,
                            "n_original_native_satellite_pixels_in_source_background":n_source,
                            "n_original_GPS_pixels_outside_175km_background":source_pixel_exclusions,
                            **score,
                            "equal_tag_mean_GPS_minus_radial_source_SIC_pp":float(statistics.mean(tagdiffs)) if tagdiffs else None,
                            "satellite_ice_is_daily_mean_not_penguin_passability":True}
                        annualresults.append(result)
            for strict in STRICT:
                for radius in RADII:
                    xs=[r for r in annualresults if r["season_start"]==year and
                        r["GPS_calendar_date"]==day and r["other_island"]==other and
                        r["nearest_original_satellite_pixel_limit_km"]==radius and
                        r["strict_quality_flags"]==strict]
                    if len(xs)!=2:raise ValueError("Only paired island-source day comparison valid")
                    bysite={x["island"]:x for x in xs}
                    a,b=bysite["SI"],bysite[other]
                    ai=a["GPS_minus_radial_source_SIC_pp"]
                    bi=b["GPS_minus_radial_source_SIC_pp"]
                    comparison.append({
                        "season_start":year,"other_island":other,"GPS_calendar_date":day,
                        "nearest_satellite_source_km":radius,"strict_satellite_source_flags":strict,
                        "n_Signy_original_native_visited_SIC_pixels":a["n_matched_native_source_pixels"],
                        "n_other_original_native_visited_SIC_pixels":b["n_matched_native_source_pixels"],
                        "Signy_GPS_minus_same_day_radial_SIC_pp":ai,
                        "other_GPS_minus_same_day_radial_SIC_pp":bi,
                        "Signy_minus_other_GPS_radial_relative_SIC_pp":ai-bi if ai is not None and bi is not None else None,
                        "ice_navigation_not_measured_by_valid_ocean_pixel":True})
    if len(comparison)!=45*4:
        raise ValueError("One native satellite day or quality sensitivity was lost")
    for year,other in PAIRS:
        for month in ("12","01"):
            for strict in STRICT:
                for radius in RADII:
                    rr=[r for r in comparison if r["season_start"]==year and
                        r["other_island"]==other and r["GPS_calendar_date"][4:6]==month and
                        r["nearest_satellite_source_km"]==radius and
                        r["strict_satellite_source_flags"]==strict]
                    values=[r["Signy_minus_other_GPS_radial_relative_SIC_pp"] for r in rr
                            if r["Signy_minus_other_GPS_radial_relative_SIC_pp"] is not None]
                    monthly.append({
                        "season_start":year,"other_island":other,
                        "month":("Dec" if month=="12" else "Jan"),
                        "nearest_original_satellite_limit_km":radius,
                        "strict_satellite_flags":strict,
                        "source_GPS_shared_dates":len(rr),
                        "valid_native_cell_daily_differences":len(values),
                        "n_days_Signy_radial_excess_negative":sum(
                            r["Signy_GPS_minus_same_day_radial_SIC_pp"] is not None and
                            r["Signy_GPS_minus_same_day_radial_SIC_pp"]<0 for r in rr),
                        "n_days_other_radial_excess_negative":sum(
                            r["other_GPS_minus_same_day_radial_SIC_pp"] is not None and
                            r["other_GPS_minus_same_day_radial_SIC_pp"]<0 for r in rr),
                        "mean_Signy_minus_other_radial_adjusted_GPS_SIC_pp":(
                            float(statistics.mean(values)) if values else None),
                        "source_day_block_not_independent_GPS_or_satellite_pixels":True
                    })
    result={"status":"SOURCE_OBSERVED_GPS_DAILY_ICE_DIRECTIONAL_VS_RADIAL_OCEAN_BACKGROUND",
            "original_GPS_DOI":GPS_DOI,"original_OSI_SAF_DOI":DOI,
            "source_native_GPS_total":locked["original_GPS_source_tracks"],
            "GPS_source_qualified":locked["original_source_qualified_tracks"],
            "original_day_from_GPS_before_observed_ice":locked["same_year_island_pair_support"],
            "original_SIC_n_days":len(days),"n_daily_island_comparisons":len(comparison),
            "n_native_GPS_tag_day_geo_quality_rows":len(tagresults),
            "n_native_island_day_quality_rows":len(annualresults),
            "n_month_source_sensitivities":len(monthly),
            "original_satellite_source_grid_sha256":coords_hash,
            "month_primary_radius20_flagstandard":[x for x in monthly if
                 x["nearest_original_satellite_limit_km"]==20 and not x["strict_satellite_flags"]],
            "warnings":[
               "SIC satellite 25km daily mean is not actual ice navigability or a passage barrier at the time of GPS.",
               "Radial reference assumes all OSI valid ocean pixels in the same 25km island-centric ring are reachable; this is not independently verified and may cross islands, glacier, or ice barriers.",
               "Source-original GPS tags were not observed diving/capturing prey at these fixes.",
               "Tags can share the same native satellite pixel; source-pixel dedup and day-block summaries are retained; days and pixels are spatially/temporally correlated.",
               "Some native GPS pixels are excluded if the closest satellite pixel centre falls >175km from the island source anchor; exposure coverage and exclusions retained.",
               "Original satellite quality flags and two nearest radii (20/35km) retained; no missingness recoded as no ice.",
               "Only three matched other-island-year pairs, with other island confounded with year; 2011 December n1 day.",
               "No trained Freer krill GAM causal inference or demographic/vegetation 2050/2100 forecast enabled."]}
    verify_original_45_day_radius_SIC_receipts(
        tagresults,annualresults,comparison,monthly)
    return tagresults,annualresults,comparison,monthly,result

def verify_original_45_day_radius_SIC_receipts(tags,sites,contrasts,monthly):
    """Numerical reproducibility of publisher-original data; not hypothesis p-values."""
    primary=[r for r in monthly if r["nearest_original_satellite_limit_km"]==20
             and not r["strict_satellite_flags"]]
    expected={
        (2011,"LI","Dec"):(1,0.0),
        (2011,"LI","Jan"):(5,0.0),
        (2013,"PI","Dec"):(3,12.229572851552945),
        (2013,"PI","Jan"):(11,0.4706488415063152),
        (2015,"MI","Dec"):(5,0.7098052633161792),
        (2015,"MI","Jan"):(20,0.0)
    }
    by={(r["season_start"],r["other_island"],r["month"]):r for r in primary}
    if set(by)!=set(expected):raise ValueError("Original three-pair source time support changed")
    for key,(days,value) in expected.items():
        row=by[key]
        if (row["source_GPS_shared_dates"],row["valid_native_cell_daily_differences"])!=(days,days):
            raise ValueError("Original GPS day / source SIC missingness changed "+str(key))
        if not math.isclose(row["mean_Signy_minus_other_radial_adjusted_GPS_SIC_pp"],
                            value,abs_tol=1e-10,rel_tol=1e-10):
            raise ValueError("Original publisher SIC distance-matched observed value drift "+str(key))
    tagged=[r for r in tags if r["season_start"]==2013 and
            r["GPS_calendar_date"].startswith("201312") and
            r["nearest_original_satellite_pixel_limit_km"]==20 and
            not r["strict_quality_flags"] and
            r["GPS_minus_radial_source_SIC_pp"] is not None]
    signy=[r for r in tagged if r["island"]=="SI"]
    powell=[r for r in tagged if r["island"]=="PI"]
    if not (len(signy)==12 and all(r["GPS_minus_radial_source_SIC_pp"]>0 for r in signy)
            and len(powell)==22 and
            sum(r["GPS_minus_radial_source_SIC_pp"]<0 for r in powell)==15):
        raise ValueError("Original 2013 December tag-day signed SIC contrasts changed")
    orig=[r for r in sites if r["season_start"]==2013 and
          r["GPS_calendar_date"].startswith("201312") and
          r["nearest_original_satellite_pixel_limit_km"]==20 and
          not r["strict_quality_flags"]]
    si=[r["GPS_minus_radial_source_SIC_pp"] for r in orig if r["island"]=="SI"]
    pi=[r["GPS_minus_radial_source_SIC_pp"] for r in orig if r["island"]=="PI"]
    if len(si)!=3 or len(pi)!=3 or not all(x>0 for x in si) or not all(x<0 for x in pi):
        raise ValueError("Original GPS native 2013 December paired SIC directions drift")
    if not (math.isclose(statistics.mean(si),6.027418136115822,abs_tol=1e-10)
            and math.isclose(statistics.mean(pi),-6.202154715437124,abs_tol=1e-10)):
        raise ValueError("Daily native pixel mean SIC excess receipt changed")
    original_primary=[r for r in contrasts if r["season_start"]==2013 and
        r["GPS_calendar_date"].startswith("201312") and
        r["nearest_satellite_source_km"]==20 and not r["strict_satellite_source_flags"]]
    if len(original_primary)!=3:
        raise ValueError("Original 2013 source day count changed")
    for strict in (False,True):
        for radius in (20.,35.):
            part=[r for r in contrasts if r["season_start"]==2013 and
                  r["GPS_calendar_date"].startswith("201312") and
                  r["nearest_satellite_source_km"]==radius and r["strict_satellite_source_flags"]==strict]
            if len(part)!=3:
                raise ValueError("Original source spatial sensitivity coverage changed")
            if any(not math.isclose(a["Signy_minus_other_GPS_radial_relative_SIC_pp"],
                      b["Signy_minus_other_GPS_radial_relative_SIC_pp"],abs_tol=1e-10)
                   for a,b in zip(part,original_primary)):
                raise ValueError("Original satellite source flag/nearest ocean radius sensitivity changed")
    return True

def write_csv(path,records):
    if not records:raise ValueError("Empty source result")
    with Path(path).open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=list(records[0]))
        w.writeheader();w.writerows(records)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--gps-zip",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    p.add_argument("--phase",choices=("discover","download","analyze"),required=True)
    a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
    positions,days,locked=original.original_source_days(a.gps_zip)
    if a.phase=="discover":
        (a.out/"source_days_fixed_before_SIC.json").write_text(
            json.dumps(locked,indent=2,ensure_ascii=False)+"\n")
        print(json.dumps({"status":"SOURCE_GPS_DAYS_FROZEN_BEFORE_SIC",
                          "support":locked["same_year_island_pair_support"],
                          "unique_original_dates":locked["unique_calendar_dates"]},ensure_ascii=False))
    elif a.phase=="download":
        old=json.loads((a.out/"source_days_fixed_before_SIC.json").read_text())
        if old["unique_calendar_dates"]!=locked["unique_calendar_dates"]:
            raise ValueError("Original GPS days changed after source-freeze")
        files=original.fetch_daily(days,a.out/"original_OSI_daily")
        (a.out/"publisher_original_SIC_daily_receipts.json").write_text(
            json.dumps(files,indent=2,ensure_ascii=False)+"\n")
        print(json.dumps({"status":"SOURCE_DAILY_SATELLITE_RETRIEVED",
                          "n_source_original_days":len(files["source_original_daily_netcdfs"])}))
    else:
        source_receipt=json.loads((a.out/"publisher_original_SIC_daily_receipts.json").read_text())
        tag,site,pairs,month,results=run(a.gps_zip,a.out/"original_OSI_daily",source_receipt)
        write_csv(a.out/"GPS_original_tag_day_radial_ice_excess.csv",tag)
        write_csv(a.out/"GPS_native_pixel_island_day_radial_ice_excess.csv",site)
        write_csv(a.out/"same_calendar_day_Signy_other_radial_ice_excess.csv",pairs)
        write_csv(a.out/"same_GPS_month_day_block_radial_excess_summary.csv",month)
        (a.out/"decision.json").write_text(
            json.dumps(results,indent=2,ensure_ascii=False)+"\n")
        print("SOURCE_DAILY_GPS_RADIAL_ICE="+json.dumps({
            "status":results["status"],"source_45_days":results["original_SIC_n_days"],
            "primary_month":results["month_primary_radius20_flagstandard"],
            "source_n_tags":results["n_native_GPS_tag_day_geo_quality_rows"]},ensure_ascii=False))
if __name__=="__main__":main()
