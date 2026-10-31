// Pure source-backed co-location. Run from repository root with Node >=20.
// node research/climate-penguin/work/land_marine_colocation_v1/build.mjs [input_root] [output_root]
import {readFileSync,writeFileSync,mkdirSync} from "node:fs";
import {resolve,join} from "node:path";
import {createHash} from "node:crypto";
function parseCSV(s){
  const records=[];let row=[],field="",q=false;
  for(let i=0;i<s.length;i++){
    const c=s[i];
    if(q){if(c==='"' && s[i+1]==='"'){field+='"';i++}else if(c==='"')q=false;else field+=c;}
    else if(c==='"')q=true;
    else if(c===','){row.push(field);field="";}
    else if(c==='\n'){row.push(field.replace(/\r$/,""));if(row.length>1)records.push(row);row=[];field="";}
    else field+=c;
  }
  if(field || row.length){row.push(field);records.push(row);}
  if(q)throw Error("unclosed CSV quote");
  const cols=records.shift();
  return records.map((r,i)=>{if(r.length!==cols.length)throw Error("malformed CSV at "+i+": "+r.length+" vs "+cols.length);return Object.fromEntries(cols.map((c,j)=>[c,r[j]]));});
}
function csvEncode(rows,cols){
  const e=x=>{const s=x==null?"":String(x);return /[\",\n\r]/.test(s)?'"'+s.replaceAll('"','""')+'"':s;};
  return cols.join(",")+"\n"+rows.map(x=>cols.map(c=>e(x[c])).join(",")).join("\n")+"\n";
}
function geodesicKm(x,y){
  const a=Math.PI/180,lat1=Number(x.latitude)*a,lat2=Number(y.latitude)*a;
  const dlat=lat2-lat1,dlon=(Number(y.longitude)-Number(x.longitude))*a;
  const t=Math.sin(dlat/2)**2+Math.cos(lat1)*Math.cos(lat2)*Math.sin(dlon/2)**2;
  return 12742.0176*Math.asin(Math.min(1,Math.sqrt(Math.max(0,t))));
}
function buildCoLocation(src,sourceGitShas){
  const climate=parseCSV(src.climate),veg=parseCSV(src.vegetation),snow=parseCSV(src.snow);
  if(climate.length!==424 || veg.length!==246 || snow.length!==1166)throw Error("fixed data support changed");
  const order=[["ssp245","2041-2060"],["ssp245","2081-2100"],["ssp585","2041-2060"],["ssp585","2081-2100"]];
  const ck=x=>[x.experiment,x.period,x.location_id].join("|");
  const climMap=new Map(climate.map(x=>[ck(x),x]));
  if(climMap.size!==424)throw Error("climate duplicate");
  const base=climate.filter(x=>x.experiment==="ssp245"&&x.period==="2041-2060");
  if(base.length!==106||new Set(base.map(x=>x.location_id)).size!==106)throw Error("nonunique study coordinate");
  const bySite=new Map();
  for(const c of base){const a=bySite.get(c.site_id)||[];a.push(c);bySite.set(c.site_id,a);}
  const snowGrid=new Map();
  for(const row of snow){
    const id=row.location_id,f=Number(row.land_fraction),prev=snowGrid.get(id);
    if(!Number.isFinite(f)||f<0||f>1)throw Error("land-fraction bounds");
    if(prev!=null&&Math.abs(prev-f)>1e-9)throw Error("land fraction changed within calendar years "+id);
    snowGrid.set(id,f);
    if(row.complete!=="True"||Number(row.days)!==30)throw Error("incomplete September ERA5 snapshot "+id);
  }
  if(snowGrid.size!==106)throw Error("snow location mismatch");
  const observedSourceKeys=new Set(),receipts=[],matched=[];
  for(let i=0;i<veg.length;i++){
    const v=veg[i],srcKey=[v.site_id,v.species_id].join("|");
    if(observedSourceKeys.has(srcKey))throw Error("duplicate site-species observation "+srcKey);
    observedSourceKeys.add(srcKey);
    if(!["ADPE","CHPE","GEPE"].includes(v.species_id))throw Error("unexpected species");
    if(v.positive_mapped_detection!=="True"&&v.positive_mapped_detection!=="False")throw Error("unexpected positive detection encoding");
    const candidates=(bySite.get(v.site_id)||[]).map(c=>({c,km:geodesicKm(v,c)})).sort((a,b)=>a.km-b.km||a.c.location_id.localeCompare(b.c.location_id));
    const best=candidates[0], eligible=Boolean(best&&best.km<=2+1e-12);
    const status=!best?"site_id_absent":eligible?"matched_exact_site_id_within_2km":"same_site_id_too_far";
    const receipt={
      source_row_1based:i+1,site_id:v.site_id,species_id:v.species_id,site_name:v.site_name,region:v.region,
      source_latitude:v.latitude,source_longitude:v.longitude,matching_status:status,
      nearest_same_code_location_id:best?.c.location_id??"",nearest_same_code_distance_km:best?.km??"",
      matched_locations_within_2km:candidates.filter(x=>x.km<=2).length
    };
    receipts.push(receipt);
    if(eligible)matched.push({v,receipt,reference:best.c});
  }
  if(receipts.length!==246||matched.length!==58)throw Error("matched species support changed "+matched.length);
  const scenarios=[];
  for(const m of matched)for(const [experiment,period] of order){
    const c=climMap.get([experiment,period,m.reference.location_id].join("|"));
    if(!c)throw Error("future climate not found for "+m.reference.location_id);
    const rawSlope=m.v.observed_log_count_slope_per_year;
    const sign=rawSlope===""?"not_estimable":Number(rawSlope)>0?"positive":Number(rawSlope)<0?"negative":"zero";
    scenarios.push({
      experiment,period,
      location_id:c.location_id,site_id:m.v.site_id,species_id:m.v.species_id,
      site_name:m.v.site_name,region:m.v.region,source_row_1based:m.receipt.source_row_1based,
      latitude:m.v.latitude,longitude:m.v.longitude,
      joined_climate_latitude:c.latitude,joined_climate_longitude:c.longitude,
      source_to_climate_distance_km:m.receipt.nearest_same_code_distance_km,
      alternative_climate_coordinates_within_2km:m.receipt.matched_locations_within_2km,
      historical_observed_seasons:m.v.observed_seasons,
      historical_first_season:m.v.first_observed_season,
      historical_last_season:m.v.last_observed_season,
      historical_year_span:m.v.observed_year_span,
      historical_count_method:m.v.count_methods,
      historical_count_slope_per_year:rawSlope,
      historical_slope_sign:sign,
      vegetation_detection_status:m.v.map_status,
      positive_mapped_vegetation_detection:m.v.positive_mapped_detection==="True"?1:0,
      static_mapped_vegetation_lichen_m2_2km:m.v.mapped_terrestrial_union_area_2km_m2,
      era5_september_surrounding_grid_land_fraction:snowGrid.get(c.location_id),
      marine_fingerprint:c.marine_fingerprint,
      all_three_marine_model_cell_centres_within_50km:c.marine_all_3_models_within_50km,
      marine_max_model_cell_distance_km:c.marine_max_model_cell_distance_km,
      warming_3of3:c.tas_increase_models==="3"?1:0,
      temperature_change_mean_degC:c.tas_change_mean_degC,
      temperature_change_min_degC:c.tas_change_min_degC,
      temperature_change_max_degC:c.tas_change_max_degC,
      temperature_change_ge2_historical_model_sd_models:c.tas_change_ge2_hist_sd_models,
      siconc_change_mean_pp:c.siconc_change_mean_pp,
      siconc_change_min_pp:c.siconc_change_min_pp,
      siconc_change_max_pp:c.siconc_change_max_pp,
      siconc_decrease_models:c.siconc_decrease_models,
      siconc_loss_ge5pp_3of3:c.siconc_loss_ge5pp_all3,
      siconc_loss_ge10pp_3of3:c.siconc_loss_ge10pp_all3,
      siconc_loss_ge20pp_3of3:c.siconc_loss_ge20pp_all3,
      siconc_future_below15pct_models:c.siconc_future_below15pct_models,
      sos_change_mean_original_scale:c.sos_change_mean_native001,
      sos_change_min_original_scale:c.sos_change_min_native001,
      sos_change_max_original_scale:c.sos_change_max_native001,
      sos_decrease_models:c.sos_decrease_models
    });
  }
  if(scenarios.length!==232)throw Error("future scenario-cohort crosswalk mismatch");
  const count=(a,p)=>a.filter(p).length;
  const stat=[];
  for(const [e,p] of order){
    const z=scenarios.filter(x=>x.experiment===e&&x.period===p),strong=z.filter(x=>x.siconc_loss_ge10pp_3of3==="1");
    const species=Object.fromEntries(["ADPE","CHPE","GEPE"].map(s=>{
      const a=z.filter(x=>x.species_id===s);
      return [s,{site_species_rows:a.length,with_count_slope:count(a,x=>x.historical_slope_sign!=="not_estimable"),n_3plus_observed_seasons:count(a,x=>+x.historical_observed_seasons>=3),large_future_ice_loss:count(a,x=>x.siconc_loss_ge10pp_3of3==="1")}];
    }));
    stat.push({
      experiment:e,period:p,matched_site_species:z.length,
      distinct_site_codes:new Set(z.map(x=>x.site_id)).size,
      regions:new Set(z.map(x=>x.region)).size,
      distinct_marine_fingerprints:new Set(z.map(x=>x.marine_fingerprint)).size,
      with_count_slope:count(z,x=>x.historical_slope_sign!=="not_estimable"),
      with_3plus_observed_seasons:count(z,x=>+x.historical_observed_seasons>=3),
      with_positive_mapped_vegetation_detection:count(z,x=>x.positive_mapped_vegetation_detection===1),
      all3_marine_cell_within50km:count(z,x=>x.all_three_marine_model_cell_centres_within_50km==="1"),
      all3_marine_cell_within50km_and_count_slope:count(z,x=>x.all_three_marine_model_cell_centres_within_50km==="1"&&x.historical_slope_sign!=="not_estimable"),
      era5_land_fraction_atleast_half:count(z,x=>x.era5_september_surrounding_grid_land_fraction>=0.5),
      both_marine_within50km_and_era5_land_frac_half:count(z,x=>x.all_three_marine_model_cell_centres_within_50km==="1"&&x.era5_september_surrounding_grid_land_fraction>=0.5),
      climate_ice_loss_10pp_3of3_site_species:strong.length,
      climate_ice_loss_10pp_3of3_distinct_site_codes:new Set(strong.map(x=>x.site_id)).size,
      climate_ice_loss_10pp_3of3_distinct_marine_fingerprints:new Set(strong.map(x=>x.marine_fingerprint)).size,
      climate_ice_loss_10pp_3of3_and_marine_all_within50km:count(strong,x=>x.all_three_marine_model_cell_centres_within_50km==="1"),
      climate_ice_loss_10pp_3of3_with_prior_positive_slope:count(strong,x=>x.historical_slope_sign==="positive"),
      climate_ice_loss_10pp_3of3_with_prior_negative_slope:count(strong,x=>x.historical_slope_sign==="negative"),
      climate_ice_loss_10pp_3of3_with_prior_unavailable_slope:count(strong,x=>x.historical_slope_sign==="not_estimable"),
      species
    });
  }
  const meta={
    status:"observed_breeding_and_static_land_context_linked_to_conditional_physical_climate_exposure_not_breeding_forecast",
    data_vintage:"2026-10-31",match_rule:"same site_id, nearest source coordinates within 2 km, deterministic location_id tie; one vegetation source row per species-site; never substitute similar names",
    source_git_blob_sha:sourceGitShas,
    inputs:{climate_rows:climate.length,vegetation_rows:veg.length,era5_snow_month_rows:snow.length,climate_unique_locations:base.length,vegetation_unique_site_species_keys:observedSourceKeys.size},
    outputs:{receipts:receipts.length,matched_source_rows:matched.length,unmatched_source_rows:count(receipts,x=>x.matching_status!=="matched_exact_site_id_within_2km"),scenario_rows:scenarios.length,geojson_features:scenarios.length},
    scenarios:stat,
    caveats:[
      "Climate 8-Nov seasonal mean is not synchronized with 2017-2023 biological census season, and this overlay estimates no future nest trends",
      "Static Plantarctica composite covers vegetation/lichen detected in 2 km circle, not ice-free area, accessible nesting habitat or annual vegetation trends",
      "ERA5 land_fraction is the nearby ~0.25 degree surrounding grid and not the fraction of real breeding land; it is quality support only",
      "Climate 106 locations, 43 marine cell fingerprints and 48 matched site codes are not counts of independent physical islands",
      "Most strong future ice-loss matches use coarse model ocean cells >50 km from colony coordinate; only 3 strict matches in SSP585 2081-2100",
      "Any historical observed count slope with two seasons is not a long-term population trend and is not a future climate response",
      "No causal or prospective prey-to-breeding coefficient, nest-patch area or vegetation change projection is estimated"
    ]
  };
  return {files:{
      "source_matching_receipt.csv":csvEncode(receipts,Object.keys(receipts[0])),
      "matched_site_species_scenarios.csv":csvEncode(scenarios,Object.keys(scenarios[0])),
      "matched_site_species_scenarios.geojson":JSON.stringify({
        type:"FeatureCollection",name:"Static observed breeding/vegetation co-location × conditional 3-model climate exposure; NOT nesting forecast",
        features:scenarios.map((s,i)=>({type:"Feature",id:i+1,geometry:{type:"Point",coordinates:[Number(s.longitude),Number(s.latitude)]},properties:Object.fromEntries(Object.entries(s).filter(([k])=>!["latitude","longitude"].includes(k)).map(([k,val])=>[k,val===""?null:typeof val==="number"?val:val]))}))
      })+"\n",
      "summary.json":JSON.stringify(meta,null,2)+"\n"
    },meta};
}
const base=resolve(process.argv[2]||"research/climate-penguin/outputs");
const out=resolve(process.argv[3]||"research/climate-penguin/outputs/land_marine_colocation_v1");
const inputPaths={climate:"cmip6_exposure_atlas_v1/site_scenario_exposure.csv",vegetation:"vegetation_response_v1/site_species_cohort.csv",snow:"september_snow_v1/september_summary.csv"};
const expectedGitBlobs={
  "climate": "9d7badfd2ad077047cb6f20accc74e3738cf4648",
  "vegetation": "23fea5988889303ecdc16f4b5309073cf38e366a",
  "snow": "204fb5bf1ab14496ca783d4d08e3b72fd5cfd8b4"
};
const source={};
for(const [key,rel] of Object.entries(inputPaths)){
 const buffer=readFileSync(join(base,rel));
 const blob=createHash("sha1").update(Buffer.from("blob "+buffer.length+"\\0")).update(buffer).digest("hex");
 if(blob!==expectedGitBlobs[key])throw Error("source git blob SHA differs: "+key+" observed "+blob+" expected "+expectedGitBlobs[key]);
 source[key]=buffer.toString("utf8");
}
const r=buildCoLocation(source,expectedGitBlobs);
mkdirSync(out,{recursive:true});
for(const [name,body] of Object.entries(r.files))writeFileSync(join(out,name),body);
console.log(JSON.stringify(r.meta.outputs)+"\\n"+JSON.stringify(r.meta.scenarios,null,2));
