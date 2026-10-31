"""Source original: pre-survey SIC Aug-Nov(t-1) vs Skaret Combined krill Jan-Feb(t).

Ice source: 1991-2020 original monthly OSI/SIC at GOPT, near Signy, two
already-fixed source buffers inner_km 0 and 100. Krill source: Skaret2023
Table3 original Combined 2011,12,14-20 (2013 missing due pack ice).
GOPT is NOT the South Orkneys 60,360km2 IMR acoustic survey footprint.
This is exploratory ecological association, not independent Freer model
prediction validation, foraging capture or climate->breeding causality.
"""
from __future__ import annotations
import argparse,csv,hashlib,io,json,math,statistics
from pathlib import Path
import numpy as np
from scipy.stats import pearsonr,spearmanr,kendalltau
SHA={
 "ice":"4fcea71c2d8b1069b6ad143f6522061ed434daf5",
 "loc":"1c5214ab355d3d2e19bc33e5de4693fa21f38731",
 "skaret":"be611777250cd0fe1dfaffffc156cdd8301246cc",
 "corr":"082a1430cfc83945a43596b5d20116d473a8eee3"}
YEARS=(2011,2012,2014,2015,2016,2017,2018,2019,2020)
MONTHS=(8,9,10,11)
RADII=(0,100)
PINS={0:(.412306903577957,.2701301485557568),
      100:(.5191601860504838,.15206324614750621)}

def rows(path,pin):
    raw=Path(path).read_bytes()
    blob=hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()
    if blob!=pin:raise ValueError("Original Git-blob source SHA drift: "+str(path))
    return list(csv.DictReader(io.StringIO(raw.decode("utf-8-sig"))))

def haversine(a,b):
    x,y=math.radians(float(a["latitude"])),math.radians(float(b["latitude"]))
    dx=y-x
    dy=math.radians(float(b["longitude"])-float(a["longitude"]))
    z=math.sin(dx/2)**2+math.cos(x)*math.cos(y)*math.sin(dy/2)**2
    return 2*6371.0088*math.asin(min(1.,math.sqrt(z)))

def join(icefile,locfile,krillfile,correctedfile):
    ice=rows(icefile,SHA["ice"])
    loc=rows(locfile,SHA["loc"])
    acoustic=rows(krillfile,SHA["skaret"])
    corr=rows(correctedfile,SHA["corr"])
    gopt=[x for x in loc if x["site_id"]=="GOPT" and x["cohort"]=="macro_40"]
    sign=[x for x in loc if x["site_id"]=="SIGN" and x["cohort"]=="phenology_coordinate_group"]
    if len(gopt)!=1 or len(sign)!=1 or gopt[0]["location_id"]!="loc020":
        raise ValueError("Registered original GOPT near-Signy ice observation source missing")
    distance=haversine(gopt[0],sign[0])
    if not 0<distance<10:raise ValueError("GOPT not spatially near Signy")
    combined=[r for r in acoustic if r["stratum"]=="Combined"]
    original_years=tuple(sorted(int(r["survey_calendar_year"]) for r in combined))
    if len(acoustic)!=31 or original_years!=YEARS:
        raise ValueError("Skaret Combined primary-source years drift or 2013 erroneously filled")
    canonical={int(z["survey_year"]):z for z in corr}
    if len(canonical)!=12 or any(y not in canonical for y in YEARS):
        raise ValueError("Audited corrected IMR chronology has changed")
    for r in combined:
        y=int(r["survey_calendar_year"])
        if float(r["density_g_m2"])!=float(canonical[y]["overall_density_g_m2"]):
            raise ValueError("Source Skaret Combined differs from corrected authority")
        if (r["survey_coverage"]=="reduced_south")!=(y==2015):
            raise ValueError("Original pack-ice limited 2015 survey status changed")
    if len(ice)!=9600:
        raise ValueError("1991-2020 source ice month/site support no longer 9600")
    index={(r["location_id"],int(r["year"]),int(r["month"]),int(r["inner_km"])):r for r in ice}
    if len(index)!=len(ice):raise ValueError("Duplicate original monthly ice row")
    joined=[]
    for r in combined:
        y=int(r["survey_calendar_year"])
        for radius in RADII:
            month_data=[]
            for m in MONTHS:
                key=("loc020",y-1,m,radius)
                if key not in index:raise ValueError("Missing antecedent original satellite source "+str(key))
                q=index[key]
                if q["complete_month"]!="True" or int(q["days"])!=int(q["expected_days"]) or int(q["supported_days"])!=int(q["days"]):
                    raise ValueError("Incomplete or unsupported original satellite month "+str(key))
                sic=float(q["sic_mean"])
                if not math.isfinite(sic) or not 0<=sic<=100:raise ValueError("Nonphysical source SIC")
                month_data.append(sic)
            joined.append({
              "survey_year":y,"original_acoustic_combined_density_g_m2":float(r["density_g_m2"]),
              "original_acoustic_CV":float(r["coefficient_of_variation"]),
              "original_acoustic_frequency_kHz":int(canonical[y]["acoustic_frequency_kHz"]),
              "source_survey_ice_limited_south":y==2015,
              "satellite_source_year_prior":y-1,
              "satellite_source_site":"GOPT",
              "satellite_site_km_from_SIGN":distance,
              "satellite_inner_km_setting":radius,
              "source_preceding_Aug_Nov_SIC_percent":statistics.mean(month_data),
              "preceding_Aug_SIC_percent":month_data[0],
              "preceding_Sep_SIC_percent":month_data[1],
              "preceding_Oct_SIC_percent":month_data[2],
              "preceding_Nov_SIC_percent":month_data[3],
              "four_source_months_complete":True,
              "SIC_not_same_location_as_regional_acoustic_or_GPS_prey":True})
    if len(joined)!=18:raise ValueError("Original nine year by two radius support lost")
    return joined,distance

def weighted_corr(x,y,w):
    a=np.asarray(x,float);b=np.asarray(y,float);w=np.asarray(w,float)
    aa=a-np.average(a,weights=w);bb=b-np.average(b,weights=w)
    return float(np.average(aa*bb,weights=w)/math.sqrt(
       np.average(aa**2,weights=w)*np.average(bb**2,weights=w)))

def ols_pred(x,y,target):
    xx=np.column_stack([np.ones(len(x)),np.asarray(x,float)])
    if len(x)<4 or np.linalg.matrix_rank(xx)!=2:raise ValueError("Insufficient prior survey years")
    b=np.linalg.lstsq(xx,np.asarray(y,float),rcond=None)[0]
    return float(b[0]+b[1]*target)

def analyze(joined):
    summaries=[];forward=[]
    for radius in RADII:
        z=sorted((q for q in joined if q["satellite_inner_km_setting"]==radius),
                 key=lambda x:x["survey_year"])
        if tuple(r["survey_year"] for r in z)!=YEARS:raise ValueError("Original survey year order drift")
        x=np.array([r["source_preceding_Aug_Nov_SIC_percent"] for r in z])
        y=np.array([r["original_acoustic_combined_density_g_m2"] for r in z])
        cvs=np.array([r["original_acoustic_CV"] for r in z])
        pear=pearsonr(x,y)
        if not(math.isclose(pear.statistic,PINS[radius][0],abs_tol=1e-10) and
               math.isclose(pear.pvalue,PINS[radius][1],abs_tol=1e-10)):
            raise ValueError("Original recorded ice-acoustic association receipt changed")
        spe=spearmanr(x,y);ken=kendalltau(x,y)
        mask2012=np.array([r["survey_year"]!=2012 for r in z])
        mask2015=np.array([r["survey_year"]!=2015 for r in z])
        loor=[pearsonr(np.delete(x,i),np.delete(y,i)).statistic for i in range(9)]
        loof=[]
        for i in range(9):
            tr=np.arange(9)!=i
            base=float(y[tr].mean())
            p=ols_pred(x[tr],y[tr],x[i])
            loof.append((abs(y[i]-base),abs(y[i]-p)))
        for i in range(4,len(x)):
            base=float(y[:i].mean());p=ols_pred(x[:i],y[:i],x[i])
            forward.append({"inner_km":radius,"test_survey_year":z[i]["survey_year"],
                "training_years":";".join(str(t["survey_year"]) for t in z[:i]),
                "n_train":i,"observed_g_m2":float(y[i]),
                "training_only_mean_g_m2":base,"training_only_SIC_OLS_g_m2":p,
                "absolute_error_baseline":abs(y[i]-base),
                "absolute_error_SIC_OLS":abs(y[i]-p),
                "not_real_Freer_out_of_sample_test":True})
        preds=[r for r in forward if r["inner_km"]==radius]
        bm=statistics.mean(r["absolute_error_baseline"] for r in preds)
        sic=statistics.mean(r["absolute_error_SIC_OLS"] for r in preds)
        summaries.append({
          "source_inner_km":radius,"n_original_survey_years":9,
          "original_survey_years":list(YEARS),
          "Pearson_r":float(pear.statistic),"Pearson_p_descriptive":float(pear.pvalue),
          "Spearman_rho":float(spe.statistic),"Spearman_p_descriptive":float(spe.pvalue),
          "Kendall_tau":float(ken.statistic),"Kendall_p_descriptive":float(ken.pvalue),
          "Pearson_log_acoustic_density_r":float(pearsonr(x,np.log(y)).statistic),
          "inverse_reported_acoustic_SE_squared_weighted_Pearson_r":weighted_corr(x,y,1/(y*cvs)**2),
          "exclude_2012_Pearson_r":float(pearsonr(x[mask2012],y[mask2012]).statistic),
          "exclude_2015_ice_limited_Pearson_r":float(pearsonr(x[mask2015],y[mask2015]).statistic),
          "exclude_both_Pearson_r":float(pearsonr(x[mask2012&mask2015],y[mask2012&mask2015]).statistic),
          "leave_one_year_out_r_min":float(min(loor)),
          "leave_one_year_out_r_max":float(max(loor)),
          "leave_one_year_out_mae_mean_baseline_g_m2":statistics.mean(a for a,b in loof),
          "leave_one_year_out_mae_ice_OLS_g_m2":statistics.mean(b for a,b in loof),
          "rolling_origin_test_years":[r["test_survey_year"] for r in preds],
          "rolling_origin_n_test_years":len(preds),
          "rolling_origin_MAE_baseline_g_m2":bm,
          "rolling_origin_MAE_ice_OLS_g_m2":sic,
          "rolling_origin_MAE_relative_improvement":1-sic/bm,
          "source_satellite_near_Signy_not_regional_survey_access":True})
    p=sorted(summaries,key=lambda v:v["Pearson_p_descriptive"])
    previous=0
    for i,item in enumerate(p):
        previous=max(previous,(len(p)-i)*item["Pearson_p_descriptive"])
        item["Holm_two_correlated_exposure_Pearson_p_descriptive"]=min(1.,previous)
    return summaries,forward

def write(path,data):
    with Path(path).open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(data[0]));w.writeheader();w.writerows(data)

def run(args):
    source,dist=join(args.ice,args.sites,args.acoustic,args.corrected)
    models,forward=analyze(source)
    args.out.mkdir(parents=True,exist_ok=True)
    write(args.out/"joined_original_9year_ice_acoustic.csv",source)
    write(args.out/"rolling_origin_source_ice_predictions.csv",forward)
    result={"status":"EXPLORATORY_ORIGINAL_ANTECEDENT_ICE_TO_ACOUSTIC_UNCONFIRMED",
      "Skaret_primary_DOI":"10.1093/icesjms/fsad076",
      "input_source_pinned_Git_blob_SHA":SHA,
      "GOPT_distance_from_SIGN_km":dist,
      "source_years":list(YEARS),
      "source_survey_2013_combined_not_estimable":True,
      "original_complete_satellite_months_used":72,
      "2023_2025_new_acoustics_have_no_corresponding_available_2023_2024_original_monthly_sic":True,
      "original_2026_ice_operational_full_region_acoustics_censored":True,
      "source_two_ice_buffer_diagnostics":models,
      "historical_predictive_rolling_is_posthoc_internal_not_external":True,
      "no_significant_noncausal_ice_acoustic_relation_claim":True,
      "no_future_nest_count_Neff_or_vegetation_forecast":True,
      "cautions":[
       "GOPT near Signy ≠ all IMR North/South survey transects; macro climate buffer support isn't true regional ice accessibility.",
       "9 source years only; 2013 Combined missing due ice and cannot be imputed North-only or zero.",
       "Preceding Aug-Nov year S−1 is temporally prior to Jan-Feb survey S but physical ice location/season not co-located with acoustic krill.",
       "CV weighting approximates density SE only; years use 38/120kHz source frequencies and incomplete 2015 South survey.",
       "Two source ice buffers overlap, not independent discovery confirmation; Pearson p is descriptive, not causal.",
       "2016–20 rolling fits evaluated after seeing historical source years, not genuine held-out post-2020 GAM forecasts.",
       "No independently measured penguin consumption, chick output, nesting N_eff or ice/salinity->prey mechanism identified."]}
    (args.out/"decision.json").write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n")
    print(json.dumps({"status":result["status"],"n_years":9,"near_SIGN_km":dist,
      "scenarios":models},ensure_ascii=False))
    return result

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--ice",required=True,type=Path)
    p.add_argument("--sites",required=True,type=Path)
    p.add_argument("--acoustic",required=True,type=Path)
    p.add_argument("--corrected",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    run(p.parse_args())
if __name__=="__main__":main()
