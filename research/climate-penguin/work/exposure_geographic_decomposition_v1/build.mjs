// Reproduce the frozen 46-site geographic decomposition. Node >=20, no external libraries.
// Usage: node research/climate-penguin/work/exposure_geographic_decomposition_v1/build.mjs [outputs_dir] [output_dir]
import {readFileSync,writeFileSync,mkdirSync} from "node:fs";
import {createHash} from "node:crypto";
import {resolve,join} from "node:path";

function parseCSV(text){
 const out=[];let row=[],v="",q=false;
 for(let i=0;i<text.length;i++){const c=text[i];if(q){if(c==='"'&&text[i+1]==='"'){v+='"';i++}else if(c==='"')q=false;else v+=c}
 else if(c==='"')q=true;else if(c===','){row.push(v);v=""}
 else if(c==='\n'){row.push(v.replace(/\r$/,""));if(row.length>1)out.push(row);row=[];v=""}else v+=c}
 if(v||row.length){row.push(v);out.push(row)}if(q)throw Error("unclosed CSV quote");
 const names=out.shift();return out.map((rr,i)=>{if(rr.length!==names.length)throw Error("CSV columns "+i);return Object.fromEntries(names.map((k,j)=>[k,rr[j]]))})
}
function csvEncode(arr,cols){
 const esc=x=>{let v=x===null||x===undefined?"":String(x);return /[",\r\n]/.test(v)?'"'+v.replaceAll('"','""')+'"':v};
 return cols.join(",")+"\n"+arr.map(x=>cols.map(k=>esc(x[k])).join(",")).join("\n")+"\n"
}
function analyze(input,sha){
 const locations=parseCSV(input.sites),physical=parseCSV(input.physical),prior=parseCSV(input.prior);
 if(locations.length!==232||physical.length!==46||prior.length!==72)throw Error("input cohort changed");
 const n=x=>{if(x===""||x===undefined||x===null||!Number.isFinite(Number(x)))throw Error("missing value "+x);return Number(x)};
 const mean=a=>a.reduce((s,v)=>s+v,0)/a.length;
 const rank=a=>{const sorted=a.map((x,i)=>[x,i]).sort((x,y)=>x[0]-y[0]);const ans=[];for(let i=0;i<a.length;){let j=i+1;while(j<a.length&&sorted[i][0]===sorted[j]?.[0])j++;let r=(i+j+1)/2;for(let t=i;t<j;t++)ans[sorted[t][1]]=r;i=j;}return ans};
 const pearson=(a,b)=>{if(a.length!==b.length||a.length<3)return null;const ma=mean(a),mb=mean(b);let cross=0,sx=0,sy=0;for(let i=0;i<a.length;i++){const x=a[i]-ma,y=b[i]-mb;cross+=x*y;sx+=x*x;sy+=y*y}return sx*sy>1e-30?cross/Math.sqrt(sx*sy):null};
 const spearman=(a,b)=>pearson(rank(a),rank(b));
 const mapGroup=(a,fn)=>{const map=new Map();for(const item of a){const k=fn(item),g=map.get(k)||[];g.push(item);map.set(k,g)}return map};
 const residual=(a,fn)=>{const means=new Map([...mapGroup(a,x=>x.region)].map(([k,v])=>[k,mean(v.map(fn))]));return a.map(x=>fn(x)-means.get(x.region))};
 const regionR2=(a,fn)=>{const v=a.map(fn),tot=v.reduce((s,x)=>s+(x-mean(v))**2,0),grp=mapGroup(a,x=>x.region);let within=0;for(const y of grp.values()){const av=mean(y.map(fn));within+=y.reduce((s,x)=>s+(fn(x)-av)**2,0)}return tot?1-within/tot:null};
 const species=["ADPE","CHPE","GEPE"],scenarios=[["ssp245","2041-2060"],["ssp245","2081-2100"],["ssp585","2041-2060"],["ssp585","2081-2100"]];
 const physicalMap=new Map(physical.map(x=>[x.site_id,x]));
 if(physicalMap.size!==46)throw Error("duplicate 46 atlas");
 const sourceSite=new Map(),missing=new Set();
 for(const x of locations){
  const key=[x.experiment,x.period,x.site_id,x.species_id].join("|");
  if(sourceSite.has(key))throw Error("duplicate site/species/scenario "+key);
  sourceSite.set(key,x);
  const h=physicalMap.get(x.site_id);
  if(h){
   if(x.physical_atlas_status!=="original_AEI_REMA_atlas_coordinates_within_2km")throw Error("physical eligibility "+key);
   for(const t of ["mapped_ice_free_area_ha_2000m","tier2_richness_2000m","elevation_relief_p90_p10_m_2000m"]){
    if(Math.abs(n(x[t])-n(h[t]))>1e-9)throw Error("trait inconsistency "+key+" "+t);
   }
  }else {if(x.physical_atlas_status!=="not_in_frozen_122_site_atlas")throw Error("status mismatch "+key);missing.add(x.site_id);}
 }
 if(sourceSite.size!==232||missing.size!==2||!missing.has("BAIL")||!missing.has("HERO"))throw Error("unsupported site semantics changed");
 const uniqueSiteScenarios=[],sourceGroups=mapGroup(locations,x=>[x.experiment,x.period,x.site_id].join("|"));
 for(const [k,items] of sourceGroups){
  const x=items[0], p=physicalMap.get(x.site_id);
  if(!p)continue;
  for(const z of items){if(z.region!==x.region || z.marine_grid_fingerprint!==x.marine_grid_fingerprint || Math.abs(n(z.siconc_change_mean_pp)-n(x.siconc_change_mean_pp))>1e-9)throw Error("same-site climate mismatch "+k)}
  uniqueSiteScenarios.push({
   experiment:x.experiment,period:x.period,site_id:x.site_id,region:x.region,latitude:n(p.latitude),longitude:n(p.longitude),
   n_species_at_site:items.length,marine_fingerprint:x.marine_grid_fingerprint,marine50:x.marine_all3_model_centres_within50km==="1"?1:0,
   mapped_ice_free_area_ha_2km:n(p.mapped_ice_free_area_ha_2000m),tier2_richness_2km:n(p.tier2_richness_2000m),
   relief_p90_p10_m_2km:n(p.elevation_relief_p90_p10_m_2000m),
   ice_decline_positive_pp:-n(x.siconc_change_mean_pp),temp_rise_degC:n(x.tas_change_mean_degC),
   salinity_decrease_original_scale:-n(x.sos_change_mean_native_scale),
   ice_decline_ACCESS_CM2_pp:-n(x["ACCESS-CM2_siconc"]),
   ice_decline_BCC_CSM2_MR_pp:-n(x["BCC-CSM2-MR_siconc"]),
   ice_decline_CESM2_pp:-n(x["CESM2_siconc"])
  });
 }
 if(uniqueSiteScenarios.length!==184)throw Error("46*4 unique source table invalid "+uniqueSiteScenarios.length);
 const traits=[
 ["ice_free_log1p_ha",x=>Math.log1p(x.mapped_ice_free_area_ha_2km)],
 ["relief_log1p_m",x=>Math.log1p(x.relief_p90_p10_m_2km)],
 ["habitat_complex_richness",x=>x.tier2_richness_2km]
 ];
 const climate=[
 ["SIC_3model_mean",x=>x.ice_decline_positive_pp],
 ["SIC_ACCESS_CM2",x=>x.ice_decline_ACCESS_CM2_pp],
 ["SIC_BCC_CSM2_MR",x=>x.ice_decline_BCC_CSM2_MR_pp],
 ["SIC_CESM2",x=>x.ice_decline_CESM2_pp],
 ["tas_3model_mean",x=>x.temp_rise_degC],
 ["sos_3model_mean",x=>x.salinity_decrease_original_scale]
 ];
 const climateTrait=[];
 const byScenario=mapGroup(uniqueSiteScenarios,x=>[x.experiment,x.period].join("|"));
 for(const [ss,period] of scenarios){
  const arr=byScenario.get([ss,period].join("|"));
  if(!arr||arr.length!==46)throw Error("missing 46-site combination");
  const fp=mapGroup(arr,x=>x.marine_fingerprint),regions=mapGroup(arr,x=>x.region);
  if(fp.size!==25||regions.size!==5)throw Error("coarse-grid sample mismatch "+ss+"/"+period);
  if([...fp.values()].some(items=>new Set(items.map(x=>x.region)).size>1))throw Error("marine cell crosses regions");
  for(const [ep,fn] of climate){
    for(const [tr,tfn] of traits){
     const x=arr.map(tfn),y=arr.map(fn);
     const collapsed=[...fp.entries()].map(([key,items])=>({region:items[0].region,x:mean(items.map(tfn)),y:mean(items.map(fn))}));
     const near=arr.filter(x=>x.marine50===1);
     const leaveOne=[...regions.keys()].map(r=>{const z=arr.filter(x=>x.region!==r);return {region:r,r:pearson(z.map(tfn),z.map(fn))}});
     const rawP=pearson(x,y),rawS=spearman(x,y),within=pearson(residual(arr,tfn),residual(arr,fn));
     const gridWithin=pearson(residual(collapsed,x=>x.x),residual(collapsed,x=>x.y));
     const nearWithin=near.length>=3?pearson(residual(near,tfn),residual(near,fn)):null;
     climateTrait.push({
      experiment:ss,period,physical_trait:tr,physical_exposure_endpoint:ep,
      unique_site_codes:arr.length,marine_fingerprints:fp.size,regions:regions.size,
      region_R2_climate:regionR2(arr,fn),pooled_pearson:rawP,pooled_spearman:rawS,
      within_region_pearson:within,
      fingerprint_collapsed_n:collapsed.length,fingerprint_collapsed_pooled_pearson:pearson(collapsed.map(x=>x.x),collapsed.map(x=>x.y)),
      fingerprint_collapsed_within_region_pearson:gridWithin,
      all_ocean_cells_within50km_site_n:near.length,within_region_pearson_marine50:nearWithin,
      leave_out_CentralWestPeninsula_pearson:leaveOne.find(x=>x.region==="Central-west Antarctic Peninsula").r,
      leave_one_region_pearson_min:Math.min(...leaveOne.map(x=>x.r)),leave_one_region_pearson_max:Math.max(...leaveOne.map(x=>x.r))
     });
    }
  }
 }
 if(climateTrait.length!==72)throw Error("expected 4*6*3="+climateTrait.length);
 const base=locations.filter(x=>x.experiment==="ssp245"&&x.period==="2041-2060");
 const groups=mapGroup(base,x=>x.species_id);
 const subset=[
 ["all",x=>true],
 ["three_or_more_observed_seasons",x=>n(x.observed_seasons)>=3],
 ["all_three_marine_cells_within50km",x=>x.marine_all3_model_centres_within50km==="1"],
 ["ground_only",x=>x.methods==="ground"],
 ["physical_AEI_REMA_observed",x=>physicalMap.has(x.site_id)]
 ];
 const portfolios=[];
 for(const spp of species){
  const raw=groups.get(spp);if(!raw)throw Error("missing species");
  for(const [cut,filter] of subset){
   const arr=raw.filter(filter);
   if(!arr.length)continue;
   const totalWeight=arr.reduce((a,b)=>a+n(b.count_median_observed_nests),0);
   const sums=mapGroup(arr,x=>x.marine_grid_fingerprint),cells=[...sums.entries()].map(([k,v])=>({key:k,sites:v.length,W:v.reduce((a,b)=>a+n(b.count_median_observed_nests),0)}));
   const denomSite=arr.reduce((a,b)=>a+n(b.count_median_observed_nests)**2,0),denomCell=cells.reduce((a,b)=>a+b.W*b.W,0);
   const siteNeff=totalWeight**2/denomSite,climateNeff=totalWeight**2/denomCell;
   portfolios.push({
     species_id:spp,cohort:cut,sampled_site_codes:arr.length,observed_marine_fingerprints:cells.length,regions:new Set(arr.map(x=>x.region)).size,
     observed_site_median_sum:totalWeight,
     effective_sampled_site_count:siteNeff,effective_model_marine_fingerprint_count:climateNeff,
     ratio_grid_to_site_effective:climateNeff/siteNeff,
     codes_sharing_a_fingerprint:arr.filter(x=>sums.get(x.marine_grid_fingerprint).length>1).length,
     median_nest_fraction_in_shared_fingerprints:arr.filter(x=>sums.get(x.marine_grid_fingerprint).length>1).reduce((a,b)=>a+n(b.count_median_observed_nests),0)/totalWeight,
     largest_code:arr.slice().sort((a,b)=>n(b.count_median_observed_nests)-n(a.count_median_observed_nests))[0].site_id,
     largest_code_observed_nest_share:Math.max(...arr.map(x=>n(x.count_median_observed_nests)))/totalWeight
   });
  }
 }
 if(portfolios.length!==15)throw Error("missing subset "+portfolios.length);
 const regionalContrasts=[];
 const oldExpected=new Map(prior.filter(x=>x.cohort==="all").map(x=>[[x.species_id,x.experiment,x.period].join("|"),x]));
 for(const [scenario,bucket] of mapGroup(locations,x=>[x.species_id,x.experiment,x.period].join("|"))){
  const [spp,ss,period]=scenario.split("|"),wAll=bucket.reduce((t,x)=>t+n(x.count_median_observed_nests),0);
  const high=x=>x.sea_ice_decline_ge10pp_all3==="1";
  const siteShare=bucket.filter(high).length/bucket.length;
  const observedMass=bucket.filter(high).reduce((t,x)=>t+n(x.count_median_observed_nests),0)/wAll;
  const sub=mapGroup(bucket,x=>x.region);
  const geoExp=[...sub.values()].reduce((sum,reg)=>{
    const wr=reg.reduce((s,x)=>s+n(x.count_median_observed_nests),0);
    return sum+wr/wAll*reg.filter(high).length/reg.length;
  },0);
  const x=oldExpected.get([spp,ss,period].join("|"));
  if(!x||Math.abs(observedMass-n(x.high_sic_loss_median_nest_fraction))>1e-11||Math.abs(geoExp-n(x.region_conditioned_expected_high_sic_nest_share))>1e-11)throw Error("independent mass crosscheck failed "+scenario);
  regionalContrasts.push({
   species_id:spp,experiment:ss,period,
   site_n:bucket.length,region_n:sub.size,high_ice_loss_site_fraction:siteShare,observed_nest_median_weighted_high_ice_loss_fraction:observedMass,
   region_conditioned_equal_site_expected_fraction:geoExp,
   observed_minus_region_expected_pp:(observedMass-geoExp)*100,
   top_site_observed_nest_fraction:Math.max(...bucket.map(x=>n(x.count_median_observed_nests)))/wAll
  });
 }
 if(regionalContrasts.length!==12)throw Error("expected 12 mass checks");
 const dominant=climateTrait.find(x=>x.experiment==="ssp585"&&x.period==="2081-2100"&&x.physical_trait==="ice_free_log1p_ha"&&x.physical_exposure_endpoint==="SIC_3model_mean");
 const gentoo=portfolios.find(x=>x.species_id==="GEPE"&&x.cohort==="all");
 if(Math.abs(dominant.region_R2_climate-.9162284236065783)>1e-10||
    Math.abs(dominant.pooled_pearson-(-.5545167223073433))>1e-10||
    Math.abs(dominant.within_region_pearson-.23861611086536938)>1e-10||
    Math.abs(gentoo.effective_model_marine_fingerprint_count-4.686127042526461)>1e-10)throw Error("source-backed anchors changed");
 const meta={
   status:"completed_descriptive_geographic_source_decomposition_not_climate_breeding_fate_prediction",
   date:"2026-10-31",
   source_git_blobs:sha,inputs:{site_species_scenarios:locations.length,physical_trait_rows:physical.length,prior_summary_rows:prior.length},
   checked:{"physical_codes_and_original_traits":46,"unique_codes_per_scenario":46,"cell_fingerprints_per_scenario":25,"land_climate_rows":uniqueSiteScenarios.length,
     "trait_model_scenario_comparisons":climateTrait.length,"portfolio_subset_rows":portfolios.length,"region_conditioned_species_scenarios":regionalContrasts.length},
   flagship:{
     scenario:"ssp585/2081-2100",
     area_vs_ice_decline_46_codes:{raw_pearson:dominant.pooled_pearson,pooled_spearman:dominant.pooled_spearman,
       region_demeaned_pearson:dominant.within_region_pearson,cell_collapsed_pearson:dominant.fingerprint_collapsed_pooled_pearson,
       cell_collapsed_region_pearson:dominant.fingerprint_collapsed_within_region_pearson,
       region_only_R2:dominant.region_R2_climate,cell_count:dominant.fingerprint_collapsed_n},
     gentoo_current_sampled_nests:{site_codes:gentoo.sampled_site_codes,site_code_effective_n:gentoo.effective_sampled_site_count,
       marine_grid_fingerprints:gentoo.observed_marine_fingerprints,marine_grid_effective_n:gentoo.effective_model_marine_fingerprint_count,
       site_to_grid_ratio:gentoo.ratio_grid_to_site_effective}
   },
   boundaries:[
    "Current AEI 2 km mapped ice-free land/REMA relief is local context, NOT current nesting capacity or future terrestrial change.",
    "The 46 sites are a selected intersection of 122 originally surveyed AEI/REMA candidates and 48 matched climate-breeding codes; 25 model marine fingerprints are NOT statistically independent regions.",
    "Region fixed effects are descriptive demeaning; species count medians mix observation years/methods and do not represent a synchronized breeding abundance census.",
    "The sign reversal is a single selected scenario-conditional spatial diagnostic, NOT a stable biological response or habitat mechanism.",
    "Model sea-ice reduction may improve or worsen feeding/breeding by species and timing; this is not a physical hazard probability.",
    "No within-island stable breeding-subcolony GIS mapping exists at a resolution matched to native CMIP6."
   ]
 };
 uniqueSiteScenarios.sort((a,b)=>a.experiment.localeCompare(b.experiment)||a.period.localeCompare(b.period)||a.site_id.localeCompare(b.site_id));
 climateTrait.sort((a,b)=>a.experiment.localeCompare(b.experiment)||a.period.localeCompare(b.period)||a.physical_exposure_endpoint.localeCompare(b.physical_exposure_endpoint)||a.physical_trait.localeCompare(b.physical_trait));
 portfolios.sort((a,b)=>a.species_id.localeCompare(b.species_id)||a.cohort.localeCompare(b.cohort));
 regionalContrasts.sort((a,b)=>a.experiment.localeCompare(b.experiment)||a.period.localeCompare(b.period)||a.species_id.localeCompare(b.species_id));
 return {meta,files:{
  "site_land_climate.csv":csvEncode(uniqueSiteScenarios,Object.keys(uniqueSiteScenarios[0])),
  "regional_trait_climate_sensitivity.csv":csvEncode(climateTrait,Object.keys(climateTrait[0])),
  "breeding_climate_portfolio.csv":csvEncode(portfolios,Object.keys(portfolios[0])),
  "region_conditioned_allocation.csv":csvEncode(regionalContrasts,Object.keys(regionalContrasts[0])),
  "summary.json":JSON.stringify(meta,null,2)+"\n"
 }};
}
const root=resolve(process.argv[2]||"research/climate-penguin/outputs");
const outDir=resolve(process.argv[3]||"research/climate-penguin/outputs/exposure_geographic_decomposition_v1");
const files={sites:"breeding_allocation_exposure_v1/site_allocation_exposure.csv",physical:"breeding_allocation_exposure_v1/frozen_AEI_REMA_46site_traits.csv",prior:"breeding_allocation_exposure_v1/species_scenario_summary.csv"};
const expected={
  "sites": "67bc986ed52aff59a26ab32fc28393f376c52b6b",
  "physical": "b30e9344e67381a0ddc5ade0edabcc76bf3688c3",
  "prior": "e34823736e8e3df8123b473114279d528b286dcb"
};
const input={};
for(const [id,p] of Object.entries(files)){
 const b=readFileSync(join(root,p));
 const git=createHash("sha1").update(Buffer.from("blob "+b.length+"\0")).update(b).digest("hex");
 if(git!==expected[id])throw Error("upstream Git blob SHA changed for "+id+" "+git);
 input[id]=b.toString("utf8");
}
const x=analyze(input,expected);
mkdirSync(outDir,{recursive:true});
for(const [name,data] of Object.entries(x.files))writeFileSync(join(outDir,name),data);
console.log(JSON.stringify({checked:x.meta.checked,flagship:x.meta.flagship},null,2));
