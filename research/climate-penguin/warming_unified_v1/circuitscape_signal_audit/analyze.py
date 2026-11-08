#!/usr/bin/env python3
"""Diagnose whether original 45 GPS-day marine ice surfaces contain spatial signal.

No Circuitscape reruns and no modification/selection of the six existing GPS scores.
Compares frozen ArcInfo R(beta) cells to original daily OSI source values for all 90
source island-days. Distinct same-day GPS cells are only outcomes in an ancillary
distance-bin SIC exposure audit.
"""
from __future__ import annotations

from collections import defaultdict
import csv
import json
import math
from pathlib import Path

import numpy as np
import xarray as xr

HERE=Path(__file__).resolve().parent
RUN=HERE.parent/"circuitscape_gate"/"gps_same_day"/"daily_outputs"
SIC=Path("build/chinstrap_gps_circuit_original/original_sic")
OUT=HERE/"outputs"
OUT.mkdir(parents=True,exist_ok=True)
BINS=(10.,35.,60.,85.,110.,135.,160.)
EXPECTED={(2011,"LI"),(2011,"SI"),(2013,"PI"),(2013,"SI"),(2015,"MI"),(2015,"SI")}
ORIGINAL_DAYS={(2011,"LI"):6,(2011,"SI"):6,(2013,"PI"):14,(2013,"SI"):14,(2015,"MI"):25,(2015,"SI"):25}

def rows(path:Path):
    with path.open(newline="",encoding="utf-8") as file:
        return list(csv.DictReader(file))

def write_rows(path, recs):
    if not recs:raise ValueError("No rows for "+str(path))
    header=list(recs[0])
    with path.open("w",newline="",encoding="utf-8") as file:
        writer=csv.DictWriter(file,fieldnames=header)
        writer.writeheader()
        writer.writerows(recs)

def asc(path):
    with path.open(encoding="ascii") as file:
        hdr=[next(file).strip().split() for _ in range(6)]
    meta={name.lower():float(value) for name,value in hdr}
    a=np.loadtxt(path,skiprows=6)
    if a.shape!=(int(meta["nrows"]),int(meta["ncols"])):
        raise ValueError("Unmatched source raster dims for "+str(path))
    return a,meta

def align(a,b):
    for k in ("ncols","nrows","xllcorner","yllcorner","cellsize"):
        if not math.isclose(a[k],b[k],rel_tol=1e-12,abs_tol=1e-9):
            raise ValueError("Native raster geometry misaligned: "+k)

def avg(a):
    return float(np.mean(a)) if len(a) else None

def summarize(a):
    if not len(a):raise ValueError("Empty grid segment")
    return {
      "n":int(len(a)),
      "mean_sic_percent":float(np.mean(a)),
      "sd_sic_pp":float(np.std(a)),
      "min_sic_percent":float(np.min(a)),
      "max_sic_percent":float(np.max(a)),
      "range_sic_pp":float(np.ptp(a)),
      "p10_sic_percent":float(np.quantile(a,.10)),
      "p90_sic_percent":float(np.quantile(a,.90)),
      "p90_minus_p10_sic_pp":float(np.quantile(a,.9)-np.quantile(a,.1)),
      "fraction_exact_zero_sic":float(np.mean(np.abs(a)<=1e-8)),
      "fraction_sic_ge1":float(np.mean(a>=1.)),
      "fraction_sic_ge15":float(np.mean(a>=15.)),
      "fraction_sic_ge30":float(np.mean(a>=30.))
    }

def main():
    pre=json.loads((RUN/"source_and_model_preflight.json").read_text(encoding="utf-8"))
    if pre["source_days"]!=45 or pre["original_paired_island_days"]!=90 or pre["source_supported_scenarios"]!=270:
        raise ValueError("Original circuit source roster / support changed")
    cases=rows(RUN/"island_day_source_domain_support.csv")
    visits=rows(RUN/"gps_original_source_pixel_visits.csv")
    if len(cases)!=90 or len(visits)!=629:raise ValueError(f"Wrong 90 original island-days / 629 GPS pixels: {len(cases)}, {len(visits)}")
    by=defaultdict(list)
    for r in visits:by[r["case_id"]].append(r)
    if len({r["case_id"] for r in cases})!=90:raise ValueError("Duplicate original case IDs")
    allcases=[];allbands=[];allgps=[];original_cache={}
    max_orig_err=0.;max_inverse_err=0.
    for rec in cases:
        key=rec["case_id"]
        if rec["status"]!="READY":raise ValueError("Original frozen 90 all ready gate failed")
        path=RUN/"cases"/key
        base,meta=asc(path/"resistance_uniform.asc")
        pos,h1=asc(path/"resistance_ice_penalty.asc")
        neg,h2=asc(path/"resistance_ice_favor.asc")
        dist,hd=asc(path/"distance.asc")
        src,hs=asc(path/"source.asc")
        ground,hg=asc(path/"grounds.asc")
        for header in (h1,h2,hd,hs,hg):align(meta,header)
        domain=base>0
        if not np.array_equal(domain,pos>0) or not np.array_equal(domain,neg>0):
            raise ValueError("Resistance model hypothesis missing pixel differently from null")
        if not np.allclose(base[domain],1.,rtol=0,atol=1e-10):
            raise ValueError("Uniform ocean baseline not exactly one")
        if not (np.all(pos[domain]>0) and np.all(neg[domain]>0)):
            raise ValueError("Positive resistance requirement failed")
        sic=np.zeros_like(pos)
        sic[domain]=50*np.log(pos[domain])
        inverse_error=float(np.max(np.abs(np.log(pos[domain])+np.log(neg[domain]))))
        max_inverse_err=max(max_inverse_err,inverse_error)
        if inverse_error>1e-8 or np.min(sic[domain])<-.00000001 or np.max(sic[domain])>100.00000001:
            raise ValueError("Original β+2/−2 reciprocal or SIC physical bounds failed")
        sic[domain]=np.clip(sic[domain],0,100)
        # All physically valid score-band ocean pixels, NOT selected by GPS presence.
        good=domain&(dist>=10)&(dist<160)&(src<0)&(ground<0)
        if not good.any():raise ValueError("No fixed available marine cells in 10–160km window")
        date=rec["date"]
        if date not in original_cache:
            f=SIC/(date+".nc")
            if not f.exists():raise ValueError("Original daily OSI netCDF missing "+date)
            with xr.open_dataset(f) as ds:
                original_cache[date]=np.asarray(ds["ice_conc"].values[0],dtype=float)
        original=original_cache[date]
        y0=int(rec["native_min_row"]);x0=int(rec["native_min_col"])
        nrow=int(rec["grid_shape_rows"]);ncol=int(rec["grid_shape_cols"])
        portion=original[y0:y0+nrow,x0:x0+ncol]
        if portion.shape!=base.shape:raise ValueError("Reconstructed crop and original OSI disagree")
        if rec["y_reversed_in_ascii"]=="True":portion=portion[::-1,:]
        if rec["x_reversed_in_ascii"]=="True":portion=portion[:,::-1]
        if not np.isfinite(portion[domain]).all():
            raise ValueError("Declared valid source cells include missing original daily SIC")
        source_error=float(np.max(np.abs(portion[domain]-sic[domain])))
        max_orig_err=max(max_orig_err,source_error)
        if source_error>1e-7:raise ValueError("Circuit resistance-derived SIC does not match source OSI: "+str(source_error))
        bg=summarize(sic[good])
        domain_sig=summarize(sic[domain])
        band_avail={}
        for b in range(6):
            mask=good&(dist>=BINS[b])&(dist<BINS[b+1])
            a=sic[mask]
            band_avail[b]={"mask":mask,"arr":a}
            if len(a):
                ss=summarize(a)
                allbands.append({"case_id":key,"year":int(rec["season_start"]),"island":rec["island"],
                   "date":date,"bin_low_km":BINS[b],"bin_high_km":BINS[b+1],**ss})
        observed=[]
        for v in by[key]:
            if v["within_fixed_score_distance_bins"]!="True":continue
            flat=int(v["native_source_pixel"]);r,c=divmod(flat,432)
            i=r-y0;j=c-x0
            if rec["y_reversed_in_ascii"]=="True":i=nrow-i-1
            if rec["x_reversed_in_ascii"]=="True":j=ncol-j-1
            if not(0<=i<nrow and 0<=j<ncol and good[i,j]):
                raise ValueError("Source GPS pixel not eligible on original raster")
            original_distance=float(v["source_cell_distance_km"])
            if abs(original_distance-dist[i,j])>1e-4:raise ValueError("GPS/raster distance misalignment")
            b=int(np.searchsorted(BINS,original_distance,side="right")-1)
            if not(0<=b<6):raise ValueError("Fixed recorded GPS outside scoring bins")
            avail=band_avail[b]["arr"]
            if len(avail)<3:raise ValueError("GPS distance bin has insufficient ocean support")
            gps_sic=float(sic[i,j])
            if abs(gps_sic-float(v["original_daily_sic"]))>1e-7:
                raise ValueError("Recorded GPS source cell SIC does not match original raster")
            diff=float(gps_sic-np.mean(avail))
            pct=(float(np.sum(avail<gps_sic-1e-8))+.5*float(np.sum(np.abs(avail-gps_sic)<=1e-8)))/len(avail)
            gpsrow={"case_id":key,"year":int(rec["season_start"]),"island":rec["island"],
                "date":date,"source_flat_native_pixel":flat,
                "distance_km":original_distance,"distance_bin_index":b,
                "gps_original_sic_percent":gps_sic,
                "background_distance_bin_mean_sic_percent":float(np.mean(avail)),
                "gps_minus_distance_bin_background_sic_pp":diff,
                "source_sic_rank_in_available_distance_bin":float(pct),
                "n_available_pixels_in_its_distance_bin":len(avail)}
            allgps.append(gpsrow);observed.append(gpsrow)
        if not observed:raise ValueError("No source GPS in registered score area "+key)
        c={ "case_id":key,"year":int(rec["season_start"]),"island":rec["island"],"date":date,
            "n_original_gps_cells_scored":len(observed),
            "n_source_connected_ocean_cells":int(domain.sum()),
            "n_fixed_distance_score_area_cells":int(good.sum()),
            "SIC_entire_connected_mean":domain_sig["mean_sic_percent"],
            "SIC_entire_connected_sd":domain_sig["sd_sic_pp"],
            "SIC_entire_connected_range":domain_sig["range_sic_pp"],
            **{"score_area_"+k:val for k,val in bg.items()},
            "score_area_SIC_perfectly_constant":bool(bg["range_sic_pp"]<=1e-8),
            "entire_circuit_SIC_perfectly_constant":bool(domain_sig["range_sic_pp"]<=1e-8),
            "score_area_SIC_p90_p10_below_1pp":bool(bg["p90_minus_p10_sic_pp"]<1.),
            "n_GPS_sic_ge15":sum(x["gps_original_sic_percent"]>=15 for x in observed),
            "mean_GPS_minus_distance_bin_background_sic_pp":avg([x["gps_minus_distance_bin_background_sic_pp"] for x in observed]),
            "mean_GPS_SIC_percent":avg([x["gps_original_sic_percent"] for x in observed]),
            "n_score_bins_with_GPS":len({x["distance_bin_index"] for x in observed}),
            "max_circuit_resistance_product_inverse_log_error":inverse_error,
            "max_original_source_ice_reconstruction_error_pp":source_error}
        allcases.append(c)
    if len(allcases)!=90 or len(allgps)!=629:raise ValueError("Case/GPS intersection changed unexpectedly")
    if len(original_cache)!=45:raise ValueError("Not all original GPS fixed same-day SIC files inspected")
    grouping=defaultdict(list)
    for r in allcases:grouping[(r["year"],r["island"])].append(r)
    if set(grouping)!={(2011,"LI"),(2011,"SI"),(2013,"PI"),(2013,"SI"),(2015,"MI"),(2015,"SI")}:
        raise ValueError("Original island-year blocks changed")
    source_days={ (2011,"LI"):6,(2011,"SI"):6,(2013,"PI"):14,(2013,"SI"):14,(2015,"MI"):25,(2015,"SI"):25}
    blocks=[]
    for (year,island),rr in sorted(grouping.items()):
        if len(rr)!=source_days[year,island]:raise ValueError("Islands or GPS dates incomplete")
        blocks.append({
            "year":year,"island":island,"n_original_GPS_days":len(rr),
            "n_original_unique_GPS_cell_day_matches":sum(x["n_original_gps_cells_scored"] for x in rr),
            "mean_score_area_SIC_percent_day_equal":avg([x["score_area_mean_sic_percent"] for x in rr]),
            "mean_score_area_SIC_sd_pp_day_equal":avg([x["score_area_sd_sic_pp"] for x in rr]),
            "mean_score_area_SIC_p90_minus_p10_pp_day_equal":avg([x["score_area_p90_minus_p10_sic_pp"] for x in rr]),
            "mean_score_area_fraction_sic_ge1":avg([x["score_area_fraction_sic_ge1"] for x in rr]),
            "mean_score_area_fraction_sic_ge15":avg([x["score_area_fraction_sic_ge15"] for x in rr]),
            "n_days_entire_circuit_SIC_perfectly_constant":sum(x["entire_circuit_SIC_perfectly_constant"] for x in rr),
            "n_days_score_area_SIC_perfectly_constant":sum(x["score_area_SIC_perfectly_constant"] for x in rr),
            "n_days_score_area_SIC_p90_p10_below_1pp":sum(x["score_area_SIC_p90_p10_below_1pp"] for x in rr),
            "mean_GPS_minus_distance_matched_background_sic_pp_day_equal":avg([x["mean_GPS_minus_distance_bin_background_sic_pp"] for x in rr])
        })
    summary={"status":"FULL_ORIGINAL_SIGNAL_IDENTIFIABILITY_AUDIT_COMPLETE",
       "analysis_type":"POST_RESULT_PHYSICAL_SIGNAL_QC_NOT_NEW_INDEPENDENT_PREDICTION",
       "original_45_day_receipt_source":str(RUN/"original_45_daily_SIC_receipts.json"),
       "n_original_calendar_days":len(original_cache),
       "n_original_island_days":len(allcases),
       "n_original_gps_native_source_cell_days":len(allgps),
       "n_island_year_blocks":len(blocks),
       "n_island_days_entire_circuit_uniform_ice":sum(x["entire_circuit_SIC_perfectly_constant"] for x in allcases),
       "n_island_days_score_area_uniform_ice":sum(x["score_area_SIC_perfectly_constant"] for x in allcases),
       "n_island_days_score_area_nearly_constant_low_p90_minus_p10":sum(x["score_area_SIC_p90_p10_below_1pp"] for x in allcases),
       "mean_block_equal_score_area_ice_pp":avg([x["mean_score_area_SIC_percent_day_equal"] for x in blocks]),
       "mean_block_equal_score_area_ice_sd_pp":avg([x["mean_score_area_SIC_sd_pp_day_equal"] for x in blocks]),
       "mean_block_equal_distance_matched_gps_ice_contrast_pp":avg([x["mean_GPS_minus_distance_matched_background_sic_pp_day_equal"] for x in blocks]),
       "max_orig_daily_NetCDF_to_Circuitscape_raster_SIC_error_pp":max_orig_err,
       "max_ice_penalty_favor_inverse_log_error":max_inverse_err,
       "interpretation":["SIC uniform across a circuit means R=exp(beta*SIC/100) scales all conductances equally; normalized currents cannot identify beta.",
       "SIC variation is a necessary, not sufficient, source of sea-ice current contrast.",
       "A modeled ocean background cell not in GPS is not a documented non-use observation.",
       "Six island-year blocks do not provide independently replicated climate-penguin transitions.",
       "No biological movement beta, migration rates or breeding climate effect were estimated."]}
    write_rows(OUT/"original_90_island_day_ice_signal.csv",allcases)
    write_rows(OUT/"original_distance_bin_source_ice.csv",allbands)
    write_rows(OUT/"original_629_GPS_pixel_distance_matched_SIC.csv",allgps)
    write_rows(OUT/"island_year_signal_summary.csv",blocks)
    (OUT/"ice_signal_identifiability.json").write_text(json.dumps(summary,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print("ICE_SIGNAL_IDENTIFIABILITY="+json.dumps(summary,ensure_ascii=False),flush=True)
    print("ICE_SIGNAL_SIX_ISLAND_YEAR_BLOCKS="+json.dumps(blocks,ensure_ascii=False),flush=True)

if __name__=="__main__":main()
