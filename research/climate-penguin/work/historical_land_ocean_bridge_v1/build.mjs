// Source-pinned 39 historical Adélie sites × land vegetation / recent nest records × CMIP6 physical climate.
// Current vegetation is STATIC mapped detection, not a temporal greening response.
// Reproduce: node research/climate-penguin/work/historical_land_ocean_bridge_v1/build.mjs --check-receipt
import {readFileSync,writeFileSync,mkdirSync} from "node:fs";
import {resolve,join} from "node:path";
import {createHash} from "node:crypto";
const ROOT=resolve("research/climate-penguin/outputs"),OUT=join(ROOT,"historical_land_ocean_bridge_v1");
const SOURCES={
 history:["historical_ice_breeding_transfer_v1/adeli_39site_historical_climate_growth.csv","db58938630e80d22ba445600ce1ad3f554c452e2"],
 vegetation:["vegetation_response_v1/site_species_cohort.csv","23fea5988889303ecdc16f4b5309073cf38e366a"],
 landMarine:["land_marine_colocation_v1/matched_site_species_scenarios.csv","5cc45d5bddeb6a6a4c89880ff38c4cff290f7783"],
 matching:["land_marine_colocation_v1/source_matching_receipt.csv","d6c70a05e357c8629a5e0caa2c13ccff162fc2f5"],
 climate:["cmip6_projection_v1/site_model_changes.csv","b383ef1cc3b0807b0bd010ca0e825937ab83ce97"],
 originalCounts:["comparison_audit/mapppd_unambiguous_site_seasons.csv","fc134e364cf38699fa7611d7dee5fbbbcb370c0a"],
 originalCoordinates:["climate_penguin/daily_ice_locations.csv","1c5214ab355d3d2e19bc33e5de4693fa21f38731"],
 snow:["september_snow_v1/september_summary.csv","204fb5bf1ab14496ca783d4d08e3b72fd5cfd8b4"],
 priorReceipt:["land_marine_colocation_v1/summary.json","c8e5ec2329337fad96e916aff387e84a3e8ea200"]
};
const freeze=JSON.parse(readFileSync(join(OUT,"expected_receipt.json"),"utf8"));
function parse(s){
 const rows=[];let r=[],v="",q=false;
 for(let i=0;i<s.length;i++){const c=s[i];
  if(q){if(c==='"'&&s[i+1]==='"'){v+='"';i++}else if(c==='"')q=false;else v+=c}
  else if(c==='"')q=true;else if(c===','){r.push(v);v=""}
  else if(c==='\n'){r.push(v.replace(/\r$/,""));if(r.length>1)rows.push(r);r=[];v=""}else v+=c;
 }
 if(r.length||v){r.push(v);rows.push(r)}
 if(q||rows.length<2)throw Error("bad original CSV");
 const h=rows.shift();
 return rows.map((r,i)=>{if(r.length!==h.length)throw Error("original CSV shape changed "+i);return Object.fromEntries(h.map((k,j)=>[k,r[j]]))});
}
function csv(rows){
 if(!rows.length)throw Error("attempted empty CSV");
 const fields=Object.keys(rows[0]);
 const escape=x=>{const s=x===null||x===undefined?"":String(x);return /[,"\r\n]/.test(s)?'"'+s.replaceAll('"','""')+'"':s};
 return fields.join(",")+"\n"+rows.map(r=>fields.map(k=>escape(r[k])).join(",")).join("\n")+"\n";
}
function calc(a){return a.reduce((s,x)=>s+x,0)}
const unique=(a,f)=>new Set(a.map(f)).size;
function close(a,b,label,tol=1e-9){if(!Number.isFinite(a)||Math.abs(a-b)>tol)throw Error("inconsistent original "+label+": "+a+" vs "+b)}
const data={};
for(const [key,[rel,sha]] of Object.entries(SOURCES)){
 const b=readFileSync(join(ROOT,rel));
 const actual=createHash("sha1").update(Buffer.from("blob "+b.length+"\0")).update(b).digest("hex");
 if(actual!==sha||freeze.input_git_blobs[key]!==sha)throw Error("Source blob drift "+key+" "+actual);
 data[key]=key==="priorReceipt"?JSON.parse(b.toString("utf8")):parse(b.toString("utf8"));
}
if(data.history.length!==39||data.vegetation.length!==246||data.landMarine.length!==232||data.matching.length!==246||
 data.climate.length!==3816||data.originalCounts.length!==2999||data.snow.length!==1166||
 data.priorReceipt.outputs.matched_source_rows!==58||data.priorReceipt.outputs.scenario_rows!==232)
 throw Error("Original cohort changed; do not reinterpret support");
const s0=new Map(data.history.map(x=>[x.site_id,x]));
if(s0.size!==39)throw Error("Duplicate history sites");
const adpeV=data.vegetation.filter(x=>x.species_id==="ADPE"),allVegetationByKey=new Map(data.vegetation.map(x=>[x.site_id+"|"+x.species_id,x]));
if(allVegetationByKey.size!==246)throw Error("Vegetation site/species source duplicates");
const v39=adpeV.filter(x=>s0.has(x.site_id)).sort((a,b)=>a.site_id.localeCompare(b.site_id));
if(v39.length!==31||new Set(v39.map(x=>x.site_id)).size!==31)throw Error("31-site original land support changed");
const common=new Set(v39.map(x=>x.site_id));
const macroLoc=new Map(data.originalCoordinates.filter(x=>x.cohort==="macro_40"&&s0.has(x.site_id)).map(x=>[x.site_id,x]));
if(macroLoc.size!==39)throw Error("Missing 39 original macro colony source locations");
const bioCountBySite=new Map();
for(const x of data.originalCounts){
 if(x.species_id!=="ADPE"||!s0.has(x.site_id)||x.count===""||!Number.isFinite(+x.count)||+x.count<0)continue;
 const a=bioCountBySite.get(x.site_id)||[];
 a.push(x);bioCountBySite.set(x.site_id,a);
}
const latestBySite=new Map([...bioCountBySite].map(([site,a])=>[site,a.sort((a,b)=>+b.season-+a.season)[0]]));
const countAll39=calc([...latestBySite.values()].map(x=>+x.count));
if(countAll39!==1074279||latestBySite.size!==39)throw Error("39 original source snapshot count drift");
const matchedByKey=new Map();
for(const x of data.landMarine){
 const key=[x.experiment,x.period,x.site_id,x.species_id].join("|");
 if(matchedByKey.has(key))throw Error("Prior land source has duplicate multi-species row "+key);
 matchedByKey.set(key,x);
}
const receiptBySite=new Map();
for(const x of data.matching){
 if(x.species_id!=="ADPE"||!common.has(x.site_id))continue;
 if(receiptBySite.has(x.site_id))throw Error("Duplicate original ADPE matching receipt");
 receiptBySite.set(x.site_id,x);
}
if(receiptBySite.size!==31)throw Error("Missing exact same-site original land matching receipt");
const climateByKey=new Map();
for(const x of data.climate){
 if(x.cohort!=="macro_40"||!s0.has(x.site_id))continue;
 const key=[x.experiment_id,x.period,x.site_id,x.source_id,x.variable_id].join("|");
 if(climateByKey.has(key))throw Error("Upstream original climate duplicate "+key);
 climateByKey.set(key,x);
}
const snowByLoc=new Map();
for(const x of data.snow){const a=snowByLoc.get(x.location_id)||[];a.push(x);snowByLoc.set(x.location_id,a)}
const models=["ACCESS-CM2","BCC-CSM2-MR","CESM2"],times=[["ssp245","2041-2060"],["ssp245","2081-2100"],["ssp585","2041-2060"],["ssp585","2081-2100"]];
const strictSupport=[],statusAll39=[],bridge=[],reconciliations=[],contextSnow=[];
const sByID=new Map(v39.map(x=>[x.site_id,x]));
for(const site of s0.keys()){
 const h=s0.get(site),v=sByID.get(site),last=latestBySite.get(site);
 statusAll39.push({site_id:site,region:h.region,
  original_39_site_long_term_species:"ADPE",
  latest_original_count:+last.count,latest_original_count_year:+last.season,
  land_vegetation_record_matched:!!v,
  reason_not_matched:v?"matched":"no_ADPE_vegetation_row_with_same_original_site_id",
  noncontemporaneous_weight_not_breeding_population:true});
}
for(const v of v39){
 const site=v.site_id,receipt=receiptBySite.get(site),loc=macroLoc.get(site),h=s0.get(site);
 if(!receipt.matching_status.startsWith("matched_")||+receipt.nearest_same_code_distance_km>2)
  throw Error("Original matching receipt no longer matches "+site);
 const values=snowByLoc.get(loc.location_id)||[];
 if(values.length!==11||values.some(x=>x.complete!=="True"))
  throw Error("ERA5 original snow metadata missing 11 complete years "+site);
 const landFractions=values.map(x=>+x.land_fraction);
 if(landFractions.some(x=>Math.abs(x-landFractions[0])>1e-10))throw Error("Time-varying ERA5 grid land mask "+site);
 const snowLand=landFractions[0],gridFinger=values[0].grid_lat+"|"+values[0].grid_lon;
 const meanSWE=calc(values.map(x=>+x.september_00utc_mean_swe_m))/11;
 contextSnow.push({site_id:site,macro_location_id:loc.location_id,ERA5_0_25deg_grid_fingerprint:gridFinger,
  era5_september_2011_2021_years:values.length,
  era5_land_fraction:snowLand,
  era5_september_mean_swe_m:meanSWE,
  mean_swe_positive_years:values.filter(x=>+x.september_00utc_mean_swe_m>0).length,
  caveat:"ERA5 land fraction is marine/land grid support only, not measured nesting-ground snow or future snow"});
}
const snBySite=new Map(contextSnow.map(x=>[x.site_id,x]));
for(const [scenario,period] of times)for(const v of v39){
 const site=v.site_id,old=matchedByKey.get([scenario,period,site,"ADPE"].join("|"));
 if(!old)throw Error("Missing original vegetation×marine joined site-season "+site+scenario+period);
 const same=macroLoc.get(site),snow=snBySite.get(site);
 if(old.location_id!==same.location_id||old.joined_climate_latitude!==same.latitude||
  old.joined_climate_longitude!==same.longitude)
  throw Error("Site matches another climate location or coordinate "+site);
 if(+old.source_to_climate_distance_km>2)throw Error("Site had been overmatched >2km");
 if(old.vegetation_detection_status!==v.map_status||
    old.positive_mapped_vegetation_detection!==(v.positive_mapped_detection==="True"?"1":"0"))
  throw Error("Original static vegetation-map detection changed "+site);
 close(+old.static_mapped_vegetation_lichen_m2_2km,+v.mapped_terrestrial_union_area_2km_m2,"vegetation area",1e-6);
 close(+old.era5_september_surrounding_grid_land_fraction,snow.era5_land_fraction,"ERA5 landfraction");
 if(+old.historical_observed_seasons!==+v.observed_seasons)throw Error("Original recent counts periods changed");
 if(old.historical_count_slope_per_year!==""&&v.observed_log_count_slope_per_year!=="")
  close(+old.historical_count_slope_per_year,+v.observed_log_count_slope_per_year,"recent observed slope",1e-12);
 if((old.historical_count_slope_per_year==="")!==(v.observed_log_count_slope_per_year===""))
  throw Error("Recent count slope empty/nonempty no longer matches original");
 const changes={};
 for(const model of models){
  changes[model]={};
  for(const key of ["tas","siconc","sos"]){
   const c=climateByKey.get([scenario,period,site,model,key].join("|"));
   if(!c)throw Error("Missing original historical-site CMIP6 "+model+"/"+key+"/"+site);
   if(!Number.isFinite(+c.change))throw Error("Nonfinite original model change");
   changes[model][key]={delta:+c.change,cell:c.grid_cell_id,distance:+c.distance_km};
  }
 }
 const nIce=models.filter(model=>changes[model].siconc.delta<0).length;
 const nSalt=models.filter(model=>changes[model].sos.delta<0).length;
 const nWarm=models.filter(model=>changes[model].tas.delta>0).length;
 const maxMarineDist=Math.max(...models.flatMap(model=>[changes[model].siconc.distance,changes[model].sos.distance]));
 if(+old.siconc_decrease_models!==nIce||+old.sos_decrease_models!==nSalt||
  +old.warming_3of3!==(nWarm===3?1:0))
  throw Error("Original land-marine atlas climate differs from 39-site cohort "+scenario+period+site);
 close(+old.marine_max_model_cell_distance_km,maxMarineDist,"max marine model distance",1e-6);
 const all3Marine50=maxMarineDist<=50;
 if((old.all_three_marine_model_cell_centres_within_50km==="1")!==all3Marine50)
  throw Error("Original 50km marine source gate changed");
 const newest=latestBySite.get(site),recentSlope=v.observed_log_count_slope_per_year;
 const historicGrowth=+s0.get(site).count_growth_log1p_slope_per_decade;
 const recentPositive=recentSlope!==""?+recentSlope>0:null;
 const oldPositive=historicGrowth>=0;
 const land05=snow.era5_land_fraction>=.5;
 const vegetationPositive=v.positive_mapped_detection==="True";
 const slopeYears=+v.observed_seasons;
 const jointIceSalt=nIce===3&&nSalt===3;
 const record={experiment:scenario,period,site_id:site,species_id:"ADPE",region:v.region,
  source_land_site_name:v.site_name,
  source_to_model_location_distance_km:+old.source_to_climate_distance_km,
  model_source_location_id:old.location_id,
  study_site_latitude:+v.latitude,study_site_longitude:+v.longitude,
  climate_location_latitude:+old.joined_climate_latitude,climate_location_longitude:+old.joined_climate_longitude,
  original_1991_2020_growth_slope_log1p_per_decade:historicGrowth,
  original_1991_2020_growth_sign:oldPositive?"nonnegative":"negative",
  vegetation_panel_observed_seasons:slopeYears,
  vegetation_panel_year_span:+v.observed_year_span,
  vegetation_panel_first_year:+v.first_observed_season,
  vegetation_panel_last_year:+v.last_observed_season,
  vegetation_panel_methods:v.count_methods,
  vegetation_panel_all_counts_ground:v.all_counts_ground,
  vegetation_panel_log_count_slope_per_year:recentSlope===""?"":+recentSlope,
  recent_vs_longterm_slope_sign_comparison:recentPositive===null?"not_estimable":(recentPositive===oldPositive?"same_sign":"different_sign_not_directly_comparable"),
  static_mapped_vegetation_detection_status:v.map_status,
  static_mapped_positive_vegetation_or_lichen:vegetationPositive,
  static_mapped_vegetation_or_lichen_m2_within_2km:+v.mapped_terrestrial_union_area_2km_m2,
  land_snow_grid_fraction:snow.era5_land_fraction,
  source_ERA5_grid_fingerprint:snow.ERA5_0_25deg_grid_fingerprint,
  source_ERA5_2011_2021_september_mean_SWE_m:snow.era5_september_mean_swe_m,
  all_three_model_marine_cell_max_distance_km:maxMarineDist,
  all_three_marine_cell_within50km:all3Marine50,
  land_grid_fraction_ge0_5:land05,
  at_least_3_original_recent_census_seasons:slopeYears>=3,
  strict_land_marine_coverage:all3Marine50&&land05,
  strict_3season_land_marine_coverage:all3Marine50&&land05&&slopeYears>=3,
  three_model_warming:nWarm===3,
  three_model_seaice_decline:nIce===3,
  three_model_sea_surface_freshening:nSalt===3,
  three_model_joint_ice_freshening:jointIceSalt,
  three_model_freshening_without_all_model_ice_decline:nSalt===3&&nIce!==3,
  three_model_ice_decline_without_all_model_freshening:nIce===3&&nSalt!==3,
  three_model_seaice_decline_at_least5pp:models.every(model=>changes[model].siconc.delta<=-5),
  three_model_seaice_decline_at_least10pp:models.every(model=>changes[model].siconc.delta<=-10),
  native_marine_grid_fingerprint_three_models:models.map(model=>changes[model].siconc.cell+"#"+changes[model].sos.cell).join("||"),
  latest_MAPPPD_count_of_source_site:+newest.count,
  latest_MAPPPD_count_year:+newest.season,
  latest_MAPPPD_count_method:newest.method,
  static_vegetation_is_not_future_vegetation:true,
  descriptive_physical_exposure_not_biological_projection:true};
 bridge.push(record);
 reconciliations.push({experiment:scenario,period,site_id:site,
  source_L_match_status:receipt.matching_status,
  source_land_to_climate_km:+old.source_to_climate_distance_km,
  source_macro_location_id:same.location_id,
  all_variables_agree_with_original_macro_climate:true,
  all_31_land_vegetation_rows_source_verified:true,
  original_breeding_plus_vegetation_same_site_by_coordinates:true,
  all_ERA5_grid_fraction_values_verified:true,
  source_snow_11_complete_years:true});
}
if(bridge.length!==124||reconciliations.length!==124||contextSnow.length!==31||statusAll39.length!==39)
 throw Error("Original same-site land-marine support changed");
const originalDenominator=countAll39,landMatchedDenominator=calc(v39.map(v=>+latestBySite.get(v.site_id).count));
const siteOnce=bridge.filter(x=>x.experiment==="ssp585"&&x.period==="2081-2100");
if(siteOnce.length!==31)throw Error("Missing distinct site records");
const categoryDefinitions={
 all_matched:x=>true,
 mapped_vegetation_positive:x=>x.static_mapped_positive_vegetation_or_lichen,
 marine_all_models_50km:x=>x.all_three_marine_cell_within50km,
 land_grid_fraction_ge0_5:x=>x.land_grid_fraction_ge0_5,
 strict_marine50_land0_5:x=>x.strict_land_marine_coverage,
 strict_marine50_land0_5_and_3_seasons:x=>x.strict_3season_land_marine_coverage,
 joint_ice_freshening:x=>x.three_model_joint_ice_freshening,
 freshening_no_common_ice_retreat:x=>x.three_model_freshening_without_all_model_ice_decline,
 ice_retreat_no_common_freshening:x=>x.three_model_ice_decline_without_all_model_freshening,
 joint_ice_freshening_with_vegetation_map_detection:x=>x.three_model_joint_ice_freshening&&x.static_mapped_positive_vegetation_or_lichen,
 joint_ice_freshening_with_strict_land_marine_support:x=>x.three_model_joint_ice_freshening&&x.strict_land_marine_coverage,
 joint_ice_freshening_with_strict_land_marine_and_3seasons:x=>x.three_model_joint_ice_freshening&&x.strict_3season_land_marine_coverage
};
const groups=[];
for(const [ex,per] of [["ssp245","2041-2060"],["ssp245","2081-2100"],["ssp585","2041-2060"],["ssp585","2081-2100"]]){
 const tmp=bridge.filter(x=>x.experiment===ex&&x.period===per);
 const sumCount=a=>calc(a.map(x=>x.latest_MAPPPD_count_of_source_site));
 for(const [name,fn] of Object.entries(categoryDefinitions)){
  const selected=tmp.filter(fn),mass=sumCount(selected);
  groups.push({experiment:ex,period:per,analysis_group:name,matched_site_codes:selected.length,
   original39_count_mass_weight:mass,original39_count_mass_pct:100*mass/originalDenominator,
   conditional31_matched_mass_pct:100*mass/landMatchedDenominator,
   unique_three_model_marine_fingerprints:unique(selected,x=>x.native_marine_grid_fingerprint_three_models),
   original_vegetation_map_detected_site_codes:selected.filter(x=>x.static_mapped_positive_vegetation_or_lichen).length,
   strict_land_marine_coverage_codes:selected.filter(x=>x.strict_land_marine_coverage).length,
   at_least3_recent_count_seasons_codes:selected.filter(x=>x.at_least_3_original_recent_census_seasons).length,
   original_crozier_2_codes_included:selected.filter(x=>["CRZE","CRZW"].includes(x.site_id)).length,
   source_site_codes:selected.map(x=>x.site_id).join(";"),
   caveat:"original latest counts, mixed 2001–2025 years and targets; non-independence of source codes and coarse ERA5 land mask; physical scenario only"}
  );
 }
}
const region=Array.from(new Set(siteOnce.map(x=>x.region))).sort().map(k=>({
 region:k,matched_ADPE_sites:siteOnce.filter(x=>x.region===k).length,
 mapped_positive:siteOnce.filter(x=>x.region===k&&x.static_mapped_positive_vegetation_or_lichen).length,
 count_3_seasons:siteOnce.filter(x=>x.region===k&&x.at_least_3_original_recent_census_seasons).length,
 all_ground_method:siteOnce.filter(x=>x.region===k&&x.vegetation_panel_all_counts_ground==="True").length,
 original39_weight_pct:100*calc(siteOnce.filter(x=>x.region===k).map(x=>x.latest_MAPPPD_count_of_source_site))/countAll39
}));
const facts={
 original_longterm_sites:39,adpe_vegetation_source_rows:adpeV.length,
 original_ADPE_vegetation_climate_matched_sites:v39.length,
 source_bridge_four_scenarios:bridge.length,
 source_original_39_latest_count_mass:originalDenominator,
 matched31_latest_count_mass:landMatchedDenominator,
 matched31_pct_original39:100*landMatchedDenominator/originalDenominator,
 matched31_mapped_positive_vegetation:siteOnce.filter(x=>x.static_mapped_positive_vegetation_or_lichen).length,
 matched31_unresolved_non_detection:siteOnce.filter(x=>!x.static_mapped_positive_vegetation_or_lichen).length,
 matched31_at_least_2_recent_seasons:siteOnce.filter(x=>x.vegetation_panel_observed_seasons>=2).length,
 matched31_at_least_3_recent_seasons:siteOnce.filter(x=>x.at_least_3_original_recent_census_seasons).length,
 marine50_and_landfraction05_site_codes:siteOnce.filter(x=>x.strict_land_marine_coverage).length,
 marine50_landfraction05_threeSeason_codes:siteOnce.filter(x=>x.strict_3season_land_marine_coverage).length,
 late_joint_ice_fresh_land_matched_sites:siteOnce.filter(x=>x.three_model_joint_ice_freshening).length,
 late_joint_ice_fresh_matched_count_pct_of_original39:groups.find(x=>x.experiment==="ssp585"&&x.period==="2081-2100"&&x.analysis_group==="joint_ice_freshening").original39_count_mass_pct,
 late_joint_strict3_codes:siteOnce.filter(x=>x.three_model_joint_ice_freshening&&x.strict_3season_land_marine_coverage).length,
 late_joint_strict3_count_pct_original39:groups.find(x=>x.experiment==="ssp585"&&x.period==="2081-2100"&&x.analysis_group==="joint_ice_freshening_with_strict_land_marine_and_3seasons").original39_count_mass_pct,
 late_fresh_no_consistent_ice_31_sites:siteOnce.filter(x=>x.three_model_freshening_without_all_model_ice_decline).length,
 late_fresh_no_consistent_ice_31_count_pct_of_original39:groups.find(x=>x.experiment==="ssp585"&&x.period==="2081-2100"&&x.analysis_group==="freshening_no_common_ice_retreat").original39_count_mass_pct,
 landMarine_original_climate_sign_mismatches:0,
 recent_count_negative_slopes:siteOnce.filter(x=>x.vegetation_panel_log_count_slope_per_year!==""&&+x.vegetation_panel_log_count_slope_per_year<0).length,
 older_positive_recent_negative_descriptive_mismatch:siteOnce.filter(x=>x.recent_vs_longterm_slope_sign_comparison==="different_sign_not_directly_comparable"&&x.original_1991_2020_growth_sign==="nonnegative").length
};
if(process.argv.includes("--check-receipt"))for(const [k,expectedValue] of Object.entries(freeze.facts)){
 const actual=facts[k];if(!Number.isFinite(actual)||Math.abs(actual-expectedValue)>1e-8)
  throw Error("Frozen source receipt differs at "+k+": "+actual+" expected "+expectedValue);
}
mkdirSync(OUT,{recursive:true});
writeFileSync(join(OUT,"matched_original_adpe_land_marine_four_scenarios.csv"),csv(bridge));
writeFileSync(join(OUT,"full_original_39_ADPE_land_support_audit.csv"),csv(statusAll39));
writeFileSync(join(OUT,"reconciled_4scenario_original_location_receipts.csv"),csv(reconciliations));
writeFileSync(join(OUT,"source_snow_landgrid_site_support.csv"),csv(contextSnow));
writeFileSync(join(OUT,"land_marine_scenario_support_categories.csv"),csv(groups));
writeFileSync(join(OUT,"region_vegetation_count_method_support.csv"),csv(region));
writeFileSync(join(OUT,"summary.json"),JSON.stringify({status:"static_vegetation_and_observed_recent_count_joined_to_future_physical_climate_no_biological_future_inference",facts,region,category_results:groups,caveat:"Static detected vegetation+lichen polygons are neither measured vegetation cover change nor causal penguin habitat change. Count trend 1991–2020 vs 2017–2023 are distinct time windows, methods/targets and sample support; signs are not evidence of reversal. ERA5 land fraction is coarse land/marine grid coverage, not nesting snow or terrestrial habitat area. Number of independently supported terrestrial+marine source sites is too small for cross-island biological response estimation."},null,2)+"\n");
writeFileSync(join(OUT,"validation.json"),JSON.stringify({git_blobs_checked:true,receipt_checked:process.argv.includes("--check-receipt"),facts,join_duplicates_checked:true,four_scenario_climate_reconciliations:reconciliations.length,original_snow_11year_reconciliation:true,matched_unique_land_sites:31,unmatched_sites_not_imputed_to_zero:true,ecological_demography_future_prediction:false},null,2)+"\n");
console.log("PENGUIN LAND OCEAN CLIMATE BRIDGE "+JSON.stringify({facts,region,groups:groups.filter(x=>x.experiment==="ssp585"&&x.period==="2081-2100").map(x=>({group:x.analysis_group,n:x.matched_site_codes,mass:x.original39_count_mass_weight,pct39:x.original39_count_mass_pct,pct31:x.conditional31_matched_mass_pct,marine_fingerprints:x.unique_three_model_marine_fingerprints,ids:x.source_site_codes})),receipt_checked:process.argv.includes("--check-receipt")}));
