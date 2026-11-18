// Execute from repository root with Node >= 20, no npm dependencies.
// node research/climate-penguin/work/breeding_allocation_exposure_v1/build.mjs [input_root] [output_root]
import {readFileSync,mkdirSync,writeFileSync} from "node:fs";
import {createHash} from "node:crypto";
import {resolve,join} from "node:path";
function parseCSV(s){
  const rows=[];let row=[],val="",quote=false;
  for(let i=0;i<s.length;i++){
    const c=s[i];
    if(quote){if(c==='"'&&s[i+1]==='"'){val+='"';i++}else if(c==='"')quote=false;else val+=c;}
    else if(c==='"')quote=true;else if(c===','){row.push(val);val="";}
    else if(c==='\n'){row.push(val.replace(/\r$/,""));if(row.length>1)rows.push(row);row=[];val="";}
    else val+=c;
  }
  if(val||row.length){row.push(val);rows.push(row)}
  if(quote)throw Error("unclosed quote");
  const columns=rows.shift();return rows.map((r,i)=>{if(r.length!==columns.length)throw Error("bad CSV cols "+i);return Object.fromEntries(columns.map((h,j)=>[h,r[j]]));});
}
function csvEncode(rows,headers){
 const q=x=>{const s=x==null?"":String(x);return /[",\n\r]/.test(s)?'"'+s.replaceAll('"','""')+'"':s;};
 return headers.join(",")+"\n"+rows.map(x=>headers.map(h=>q(x[h])).join(",")).join("\n")+"\n";
}
function haversineKm(a,b){
 const d=Math.PI/180,A=Number(a.latitude)*d,B=Number(b.latitude)*d,dy=B-A,dx=(Number(b.longitude)-Number(a.longitude))*d;
 return 12742.0176*Math.asin(Math.min(1,Math.sqrt(Math.max(0,Math.sin(dy/2)**2+Math.cos(A)*Math.cos(B)*Math.sin(dx/2)**2))));
}
function buildAllocation(input,physical,sourceShas){
 const land=parseCSV(input.land),bio=parseCSV(input.vegetation),climate=parseCSV(input.model),traits=parseCSV(physical);
 if(land.length!==232||bio.length!==246||climate.length!==3816||traits.length!==46)throw Error("frozen input count changed");
 const num=v=>{const x=Number(v);if(v===""||!Number.isFinite(x))throw Error("nonfinite number "+v);return x};
 const mean=(arr,fn)=>arr.reduce((s,x)=>s+fn(x),0)/arr.length;
 const total=(arr,fn)=>arr.reduce((s,x)=>s+fn(x),0);
 const groups=(arr,fn)=>{const m=new Map();for(const x of arr){const k=fn(x),v=m.get(k)||[];v.push(x);m.set(k,v);}return m;};
 const index=new Map(climate.map(x=>[[x.source_id,x.variable_id,x.experiment_id,x.period,x.location_id].join("|"),x]));
 if(index.size!==3816)throw Error("climate duplicate");
 const physicalBy=new Map(traits.map(x=>[x.site_id,x]));
 if(physicalBy.size!==46)throw Error("duplicate physical site");
 if(Math.abs(total(traits,x=>num(x.mapped_ice_free_area_ha_2000m))-15731)>1e-8||total(traits,x=>num(x.tier2_richness_2000m))!==197||Math.abs(total(traits,x=>num(x.elevation_relief_p90_p10_m_2000m))-13141.9625)>1e-7)throw Error("AEI/REMA derived-value digest mismatch");
 const out=[];
 for(const a of land){
  const b=bio[num(a.source_row_1based)-1];if(!b||a.species_id!==b.species_id||a.site_id!==b.site_id||num(b.count_median)<0)throw Error("biological source or count mismatch");
  const pp=physicalBy.get(a.site_id);let physicalStatus="not_in_frozen_122_site_atlas",d=null;
  if(pp){
   d=haversineKm(pp,{latitude:a.latitude,longitude:a.longitude});
   if(d>2)throw Error("matched physical site too far "+a.site_id+" "+d);
   physicalStatus="original_AEI_REMA_atlas_coordinates_within_2km";
  }
  const vals={};
  for(const name of ["ACCESS-CM2","BCC-CSM2-MR","CESM2"])for(const variable of ["tas","siconc","sos"]){
   const key=[name,variable,a.experiment,a.period,a.location_id].join("|"),c=index.get(key);
   if(!c)throw Error("missing individual CMIP6 "+key);
   vals[name+"_"+variable]=num(c.change);
  }
  const mSic=mean(["ACCESS-CM2","BCC-CSM2-MR","CESM2"],x=>vals[x+"_siconc"]);
  if(Math.abs(mSic-num(a.siconc_change_mean_pp))>1e-9)throw Error("ensemble SIC mismatch "+a.location_id);
  const n=num(b.count_median);
  out.push({
    experiment:a.experiment,period:a.period,site_id:a.site_id,species_id:a.species_id,region:b.region,
    location_id:a.location_id,latitude:a.latitude,longitude:a.longitude,
    source_row_1based:a.source_row_1based,
    count_median_observed_nests:n,observed_seasons:b.observed_seasons,observed_season_list:b.observed_season_list,methods:b.count_methods,
    static_mapped_vegetation_lichen_m2_2km:b.mapped_terrestrial_union_area_2km_m2,
    physical_atlas_status:physicalStatus,physical_atlas_distance_km:d??"",
    mapped_ice_free_area_ha_2000m:pp?num(pp.mapped_ice_free_area_ha_2000m):"",
    tier2_richness_2000m:pp?num(pp.tier2_richness_2000m):"",
    elevation_relief_p90_p10_m_2000m:pp?num(pp.elevation_relief_p90_p10_m_2000m):"",
    marine_grid_fingerprint:a.marine_fingerprint,
    marine_all3_model_centres_within50km:a.all_three_marine_model_cell_centres_within_50km,
    sea_ice_decline_ge10pp_all3:a.siconc_loss_ge10pp_3of3,
    siconc_change_mean_pp:num(a.siconc_change_mean_pp),
    tas_change_mean_degC:num(a.temperature_change_mean_degC),
    sos_change_mean_native_scale:num(a.sos_change_mean_original_scale),
    ...vals
  });
 }
 if(out.length!==232)throw Error("scenario allocation output count");
 const seenPhys=new Set(out.filter(x=>x.physical_atlas_status.startsWith("original")).map(x=>x.site_id));if(seenPhys.size!==46)throw Error("physical atlas mismatch "+seenPhys.size);
 const summary=[],regionSummary=[];
 const variants=["all","3plus_observed_seasons","all_ocean_centres_within_50km","ground_only","physical_atlas_coincident","3plus_and_marine50"];
 const selected=(arr,variant)=>variant==="all"?arr:
   variant==="3plus_observed_seasons"?arr.filter(x=>num(x.observed_seasons)>=3):
   variant==="all_ocean_centres_within_50km"?arr.filter(x=>x.marine_all3_model_centres_within50km==="1"):
   variant==="ground_only"?arr.filter(x=>x.methods==="ground"):
   variant==="physical_atlas_coincident"?arr.filter(x=>x.physical_atlas_status.startsWith("original")):
   arr.filter(x=>num(x.observed_seasons)>=3&&x.marine_all3_model_centres_within50km==="1");
 for(const [groupKey,rawRows] of groups(out,x=>[x.species_id,x.experiment,x.period].join("|"))){
  const [species,experiment,period]=groupKey.split("|");
  for(const variant of variants){
   const arr=selected(rawRows,variant),N=arr.length;if(N===0)continue;
   const W=total(arr,x=>x.count_median_observed_nests);if(W<=0)continue;
   const weighted=x=>total(arr,r=>r.count_median_observed_nests*r[x])/W;
   const unweighted=x=>mean(arr,r=>r[x]);
   const high=arr.filter(x=>x.sea_ice_decline_ge10pp_all3==="1"),massShare=total(high,x=>x.count_median_observed_nests)/W,siteShare=high.length/N;
   const regional=groups(arr,x=>x.region);
   const regionExpectedShare=[...regional.values()].reduce((sum,r)=>sum+(total(r,x=>x.count_median_observed_nests)/W)*(r.filter(x=>x.sea_ice_decline_ge10pp_all3==="1").length/r.length),0);
   const regionExpectedSic=[...regional.values()].reduce((sum,r)=>sum+total(r,x=>x.count_median_observed_nests)/W*mean(r,x=>x.siconc_change_mean_pp),0);
   const top=[...arr].sort((a,b)=>b.count_median_observed_nests-a.count_median_observed_nests);
   const minusTop=top.slice(1),Wrest=total(minusTop,x=>x.count_median_observed_nests);
   const row={
    species_id:species,experiment,period,cohort:variant,n_sites:N,source_nest_median_sum:W,
    effective_number_of_sampled_site_codes_W2_over_sumw2:W*W/total(arr,x=>x.count_median_observed_nests**2),
    largest_site_id:top[0].site_id,largest_site_fraction_of_sampled_median_nests:top[0].count_median_observed_nests/W,
    top_ceil20pct_site_fraction_of_sampled_median_nests:total(top.slice(0,Math.ceil(N*.2)),x=>x.count_median_observed_nests)/W,
    high_sic_loss_n_sites:high.length,
    high_sic_loss_site_fraction:siteShare,
    high_sic_loss_median_nest_fraction:massShare,
    nest_share_minus_site_share_pp:(massShare-siteShare)*100,
    region_conditioned_expected_high_sic_nest_share:regionExpectedShare,
    nest_share_minus_region_conditioned_pp:(massShare-regionExpectedShare)*100,
    siconc_equal_site_change_pp:unweighted("siconc_change_mean_pp"),siconc_nest_weighted_change_pp:weighted("siconc_change_mean_pp"),
    siconc_region_conditioned_expected_pp:regionExpectedSic,siconc_nest_weighted_minus_region_conditioned_pp:weighted("siconc_change_mean_pp")-regionExpectedSic,
    tas_equal_site_change_degC:unweighted("tas_change_mean_degC"),tas_nest_weighted_change_degC:weighted("tas_change_mean_degC"),
    sos_equal_site_change_native:unweighted("sos_change_mean_native_scale"),sos_nest_weighted_change_native:weighted("sos_change_mean_native_scale"),
    marine_grid_fingerprint_count:new Set(arr.map(x=>x.marine_grid_fingerprint)).size,region_count:regional.size,
    ice_share_without_largest_site:Wrest?total(minusTop.filter(x=>x.sea_ice_decline_ge10pp_all3==="1"),x=>x.count_median_observed_nests)/Wrest:"",
    siconc_nest_weighted_without_largest_site:Wrest?total(minusTop,x=>x.count_median_observed_nests*x.siconc_change_mean_pp)/Wrest:""
   };
   for(const name of ["ACCESS-CM2","BCC-CSM2-MR","CESM2"]){
    row["sic_equal_"+name]=unweighted(name+"_siconc");
    row["sic_weighted_"+name]=weighted(name+"_siconc");
   }
   summary.push(row);
  }
  for(const [region,arr] of groups(rawRows,x=>x.region)){
   const W=total(arr,x=>x.count_median_observed_nests),high=arr.filter(x=>x.sea_ice_decline_ge10pp_all3==="1");
   regionSummary.push({species_id:species,experiment,period,region,sites:arr.length,median_nest_sum:W,
     ocean_fingerprint_n:new Set(arr.map(x=>x.marine_grid_fingerprint)).size,
     high_sic_loss_n_sites:high.length,
     high_sic_loss_site_fraction:high.length/arr.length,
     high_sic_loss_nest_fraction:total(high,x=>x.count_median_observed_nests)/W,
     sic_change_site_equal_pp:mean(arr,x=>x.siconc_change_mean_pp),
     sic_change_nest_weighted_pp:total(arr,x=>x.count_median_observed_nests*x.siconc_change_mean_pp)/W
   });
  }
 }
 const order=(a,b)=>a.species_id.localeCompare(b.species_id)||a.experiment.localeCompare(b.experiment)||a.period.localeCompare(b.period)||a.cohort?.localeCompare(b.cohort||"")||0;
 out.sort((a,b)=>a.experiment.localeCompare(b.experiment)||a.period.localeCompare(b.period)||a.site_id.localeCompare(b.site_id)||a.species_id.localeCompare(b.species_id));
 summary.sort(order);regionSummary.sort(order);
 if(summary.length!==72)throw Error("expected 72 variant summary rows "+summary.length);
 const major=summary.filter(x=>x.cohort==="all");
 const bySpecies={};for(const x of major)if(x.experiment==="ssp585"&&x.period==="2081-2100")bySpecies[x.species_id]=x;
 if(Math.abs(bySpecies.ADPE.high_sic_loss_median_nest_fraction-.0019653536763021883)>1e-11||Math.abs(bySpecies.GEPE.high_sic_loss_median_nest_fraction-.6488645007062914)>1e-11||Math.abs(bySpecies.CHPE.nest_share_minus_region_conditioned_pp-(-.5004086110582466))>1e-9)throw Error("fixed source-backed numeric anchor drift");
 const meta={
  status:"spatial_aggregation_exposure_overlay_only_not_breeding_fate_forecast",
  source_git_blob_sha:sourceShas,
  source_physical_archives:{
   hierarchy:{run_id:36520281872,artifact_id:11012935837,zip_sha256:"aa287d9b1bffefc0d8cc9320097d77617711f5a0ac2c8bacdf84f3f71fa03595",source_csv_sha256:"d72b6b50559b2d14b10fecbd96ec29a35112df4241ff4c6e7179cb3765e699fb"},
   terrain:{run_id:36490682577,artifact_id:11001148358,zip_sha256:"93b4c6e7fd02519edc20baebb74847991dfb2168e75361884219a55f184d98d5",source_csv_sha256:"999b3baf1fc79383998d73936fe5e946c9f616c0e97c815ff9263741a62fd181"}
  },
  primary_unit:"species x exact published MAPPPD site_id; population weights from independent 2017–2023 observed nest-count median per site/species, NOT synchronous or exhaustive population size",
  group_independence:"non-independent site codes and same 3-model marine-grid cells; no inferential confidence intervals or p values",
  endpoint:"weighted share in physical marine grid cells with >=10 percentage-point seasonal-mean SIC reduction in each model, and equal-location vs nest-weighted seasonal physical changes, NOT biological harm index",
  site_traits:"46 original AOI sites with 2 km AEI ice-free ecosystem area/richness and REMA relief; ice-free ecosystem is NOT mapped nestable area",
  background_risk_caution:"Strong sea-ice decrease can improve or worsen ecological breeding conditions; lower sea ice is not unconditionally risk; no inference of climate refuge or refuge selection",
  checks:{land_source_rows:land.length,vegetation_source_rows:bio.length,CMIP6_model_source_rows:climate.length,physical_trait_rows:traits.length,physical_trait_site_codes:seenPhys.size,allocation_rows:out.length,scenario_summary_rows:major.length,sensitivity_summary_rows:summary.length,region_summary_rows:regionSummary.length},
  summary_primary:major
 };
 const geoNum=new Set(["count_median_observed_nests","mapped_ice_free_area_ha_2000m","tier2_richness_2000m","elevation_relief_p90_p10_m_2000m","siconc_change_mean_pp","tas_change_mean_degC","sos_change_mean_native_scale"]);
 const collection={type:"FeatureCollection",name:"Observed site-median nest allocation over conditional CMIP6 physical exposure; NOT future penguin harm",features:out.map((x,i)=>({
  type:"Feature",id:i+1,geometry:{type:"Point",coordinates:[num(x.longitude),num(x.latitude)]},
  properties:Object.fromEntries(["experiment","period","site_id","species_id","region","source_row_1based","count_median_observed_nests","observed_seasons","physical_atlas_status","mapped_ice_free_area_ha_2000m","tier2_richness_2000m","elevation_relief_p90_p10_m_2000m","marine_grid_fingerprint","marine_all3_model_centres_within50km","sea_ice_decline_ge10pp_all3","siconc_change_mean_pp","tas_change_mean_degC","sos_change_mean_native_scale"].map(k=>[k,geoNum.has(k)?x[k]===""?null:num(x[k]):x[k]]))
 }))};
 return {files:{
  "site_allocation_exposure.csv":csvEncode(out,Object.keys(out[0])),
  "species_scenario_summary.csv":csvEncode(summary,Object.keys(summary[0])),
  "region_scenario_summary.csv":csvEncode(regionSummary,Object.keys(regionSummary[0])),
  "site_allocation_exposure.geojson":JSON.stringify(collection)+"\n",
  "summary.json":JSON.stringify(meta,null,2)+"\n"
 },meta};
}
const base=resolve(process.argv[2]||"research/climate-penguin/outputs");
const dst=resolve(process.argv[3]||"research/climate-penguin/outputs/breeding_allocation_exposure_v1");
const files={land:"land_marine_colocation_v1/matched_site_species_scenarios.csv",vegetation:"vegetation_response_v1/site_species_cohort.csv",model:"cmip6_projection_v1/site_model_changes.csv"};
const expected={
  "land": "5cc45d5bddeb6a6a4c89880ff38c4cff290f7783",
  "vegetation": "23fea5988889303ecdc16f4b5309073cf38e366a",
  "model": "b383ef1cc3b0807b0bd010ca0e825937ab83ce97"
};
const input={};
for(const [k,p] of Object.entries(files)){
 const buf=readFileSync(join(base,p));
 const hash=createHash("sha1").update(Buffer.from("blob "+buf.length+"\0")).update(buf).digest("hex");
 if(hash!==expected[k])throw Error("Input Git SHA mismatch: "+k+" "+hash+" expected "+expected[k]);
 input[k]=buf.toString("utf8");
}
const sourcePhysical=readFileSync(join(dst,"frozen_AEI_REMA_46site_traits.csv"),"utf8");
const result=buildAllocation(input,sourcePhysical,expected);
// Physical land intersection: source-independent AEI atlas q25 of 114 ha
// is a descriptive cut, not a threshold of biological nesting feasibility.
const allSiteRows=parseCSV(result.files["site_allocation_exposure.csv"]);
const landMarine=[];
for(const experiment of ["ssp245","ssp585"])
for(const period of ["2041-2060","2081-2100"])
for(const species_id of ["ADPE","CHPE","GEPE"]){
 const group=allSiteRows.filter(x=>x.experiment===experiment&&x.period===period&&x.species_id===species_id);
 const mapped=group.filter(x=>x.physical_atlas_status==="original_AEI_REMA_atlas_coordinates_within_2km");
 const low=mapped.filter(x=>Number(x.mapped_ice_free_area_ha_2000m)<=114);
 const strong=mapped.filter(x=>x.sea_ice_decline_ge10pp_all3==="1");
 const joint=low.filter(x=>x.sea_ice_decline_ge10pp_all3==="1");
 const strict=joint.filter(x=>x.marine_all3_model_centres_within50km==="1");
 const weights=mapped.reduce((v,x)=>v+Number(x.count_median_observed_nests),0);
 landMarine.push({
   experiment,period,species_id,
   physical_site_species_n:mapped.length,
   low_AEI_area_at_most_114ha_n:low.length,
   marine_SIC_loss_at_least_10pp_3of3_n:strong.length,
   joint_low_AEI_area_and_strong_ice_loss_n:joint.length,
   joint_low_AEI_area_and_strong_ice_loss_all_marine_cells_within50km_n:strict.length,
   joint_share_of_sampled_site_median_nest_sum:joint.reduce((v,x)=>v+Number(x.count_median_observed_nests),0)/weights,
   joint_site_codes:[...new Set(joint.map(x=>x.site_id))].join(";"),
   region_names:[...new Set(joint.map(x=>x.region))].join(";")
 });
}
if(landMarine.length!==12)throw Error("land/sea crosswalk must have 12 panels");
result.files["joint_land_marine_strata.csv"]=csvEncode(landMarine,Object.keys(landMarine[0]));
mkdirSync(dst,{recursive:true});
for(const [n,s] of Object.entries(result.files))writeFileSync(join(dst,n),s);
console.log(JSON.stringify(result.meta.checks,null,2));
