// Threshold-free physical novelty of 20-year future sea-ice climatology relative to
// original overlapping historical 10/15/20-year annual SIC windows. No biological hazard.
import {readFileSync,mkdirSync,writeFileSync} from "node:fs";
import {join,resolve} from "node:path";
import {createHash} from "node:crypto";

const sourceDir=resolve("research/climate-penguin/outputs");
const outputDir=join(sourceDir,"seaice_historical_novelty_v1");
const original={
 history:["historical_ice_breeding_transfer_v1/adeli_39site_historical_climate_growth.csv","db58938630e80d22ba445600ce1ad3f554c452e2"],
 ice:["climate_penguin/macro_monthly_seaice_1991_2020.csv","4fcea71c2d8b1069b6ad143f6522061ed434daf5"],
 cmip:["cmip6_projection_v1/site_model_changes.csv","b383ef1cc3b0807b0bd010ca0e825937ab83ce97"],
 bio:["comparison_audit/mapppd_unambiguous_site_seasons.csv","fc134e364cf38699fa7611d7dee5fbbbcb370c0a"],
 species:["warming_species_breeding_v1/historical_species_site_trends.csv","2b6c0793ea9f9ea9acf0771052cf7a2ad9ab335b"]
};
const expected=JSON.parse(readFileSync(join(outputDir,"expected_receipt.json"),"utf8"));
const mean=a=>a.reduce((s,v)=>s+v,0)/a.length,sum=a=>a.reduce((s,v)=>s+v,0);
const uniq=(a,key)=>new Set(a.map(key)).size;
function parseCSV(s){
 const rs=[];let row=[],v="",quoted=false;
 for(let i=0;i<s.length;i++){
  let c=s[i];
  if(quoted){if(c==='"'&&s[i+1]==='"'){v+='"';i++}else if(c==='"')quoted=false;else v+=c}
  else if(c==='"')quoted=true;
  else if(c===','){row.push(v);v=""}
  else if(c==='\n'){row.push(v.replace(/\r$/,""));if(row.length>1)rs.push(row);row=[];v=""}
  else v+=c;
 }
 if(row.length||v){row.push(v);rs.push(row)}
 if(quoted||rs.length<2)throw Error("Malformed source CSV");
 const header=rs.shift();
 return rs.map((r,i)=>{if(r.length!==header.length)throw Error("CSV row width "+i);
  return Object.fromEntries(header.map((x,j)=>[x,r[j]]))
 });
}
function toCSV(rows){
 if(!rows.length)throw Error("Empty output");
 const head=Object.keys(rows[0]);
 const encode=x=>{const s=x===undefined||x===null?"":String(x);return /[,"\n\r]/.test(s)?'"'+s.replaceAll('"','""')+'"':s};
 return head.join(",")+"\n"+rows.map(r=>head.map(k=>encode(r[k])).join(",")).join("\n")+"\n";
}
function close(actual,want,label){
 if(!Number.isFinite(actual)||Math.abs(actual-want)>1e-8)throw Error("Frozen receipt drift "+label+" "+actual+" expected "+want);
}
const D={},blobs={};
for(const [k,[p,pin]] of Object.entries(original)){
 const data=readFileSync(join(sourceDir,p));
 const sha=createHash("sha1").update(Buffer.from("blob "+data.length+"\0")).update(data).digest("hex");
 if(sha!==pin||expected.git_blobs[k]!==sha)throw Error("Original file changed "+k);
 D[k]=parseCSV(data.toString("utf8"));blobs[k]=sha;
}
if(D.history.length!==39||D.ice.length!==9600||D.cmip.length!==3816||D.bio.length!==2999||D.species.length!==54)
 throw Error("Original 39-site monthly source shape changed");
const mapHistory=new Map(D.history.map(x=>[x.site_id,x]));
if(mapHistory.size!==39)throw Error("Duplicated historical site code");
const monthly=new Map();
for(const r of D.ice){
 if(!mapHistory.has(r.site_id)||r.inner_km!=="0"||![8,9,10,11].includes(+r.month))continue;
 if(r.complete_month!=="True")throw Error("Incomplete original monthly SIC "+r.site_id);
 const key=r.site_id+"|"+r.year,q=monthly.get(key)||[];
 q.push(+r.sic_mean);monthly.set(key,q);
}
const originalCounts=new Map();
for(const r of D.bio){
 if(r.species_id!=="ADPE"||!mapHistory.has(r.site_id)||r.count===""||!Number.isFinite(+r.count)||+r.count<0)continue;
 const q=originalCounts.get(r.site_id)||[];q.push(r);originalCounts.set(r.site_id,q);
}
const sites=[];
for(const h of D.history){
 const annual=[];
 for(let y=1991;y<=2020;y++){
  const arr=monthly.get(h.site_id+"|"+y);
  if(!arr||arr.length!==4||!arr.every(Number.isFinite))throw Error("Missing original site year "+h.site_id+" "+y);
  annual.push(mean(arr));
 }
 if(Math.abs(mean(annual)- +h.historical_nearshore_AugNov_SIC_mean_pct)>1e-8)
  throw Error("Original 30-year mean not reproduced: "+h.site_id);
 const rolling={};
 for(const n of [10,15,20]){
  const vals=Array.from({length:31-n},(_,i)=>mean(annual.slice(i,i+n)));
  if(vals.length!==31-n)throw Error("Wrong rolling windows count");
  rolling[n]={min:Math.min(...vals),max:Math.max(...vals),span:Math.max(...vals)-Math.min(...vals),n:vals.length};
 }
 const countRows=(originalCounts.get(h.site_id)||[]).sort((a,b)=>+b.season-+a.season);
 if(!countRows.length)throw Error("Missing original census at "+h.site_id);
 const latest=countRows[0],annualRef=mean(annual.slice(4,24));
 if(Math.abs(annualRef-rolling[20].min)>1e-8&&["CRZE","CRZW"].includes(h.site_id)){
  throw Error("Original frozen Cape Crozier annual 20-year lower-envelope changed");
 }
 sites.push({
  site_id:h.site_id,region:h.region,
  original_historical_count_growth_decade:+h.count_growth_log1p_slope_per_decade,
  latest_recorded_count:+latest.count,latest_census_year:+latest.season,
  latest_census_method:latest.method,
  observed_SIC_1995_2014_pct:annualRef,observed_SIC_1991_2020_pct:mean(annual),
  original_min_one_year_SIC_pct:Math.min(...annual),
  original_max_one_year_SIC_pct:Math.max(...annual),
  original_annual_SIC_standard_deviation_pp:Math.sqrt(mean(annual.map(x=>(x-mean(annual))**2))),
  historical_10yr_low_pct:rolling[10].min,
  historical_10yr_high_pct:rolling[10].max,
  historical_15yr_low_pct:rolling[15].min,
  historical_15yr_high_pct:rolling[15].max,
  historical_20yr_low_pct:rolling[20].min,
  historical_20yr_high_pct:rolling[20].max,
  historical_10yr_range_pp:rolling[10].span,
  historical_15yr_range_pp:rolling[15].span,
  historical_20yr_range_pp:rolling[20].span,
  historical_20yr_windows_n:rolling[20].n
 });
}
const siteById=new Map(sites.map(x=>[x.site_id,x]));
const models=["ACCESS-CM2","BCC-CSM2-MR","CESM2"];
const scenarios=["ssp245","ssp585"],periods=["2041-2060","2081-2100"],baselines=["1995-2014","1991-2020"];
const modelBy=new Map();
for(const r of D.cmip){
 if(r.variable_id!=="siconc"||r.cohort!=="macro_40")continue;
 const key=[r.source_id,r.experiment_id,r.period].join("|"),a=modelBy.get(key)||new Map();
 if(a.has(r.site_id))throw Error("Duplicate original CMIP model cell site "+key+" "+r.site_id);
 a.set(r.site_id,{change:+r.change,model_grid_id:r.grid_cell_id,grid_distance_km:+r.distance_km});
 modelBy.set(key,a);
}
const N=sum(sites.map(x=>x.latest_recorded_count));
const crozier=sites.filter(x=>["CRZE","CRZW"].includes(x.site_id));
const capeCount=sum(crozier.map(x=>x.latest_recorded_count));
const weighted=(rows,property)=>sum(rows.map(r=>r.latest_recorded_count*r[property]))/sum(rows.map(r=>r.latest_recorded_count));
const share=rows=>100*sum(rows.map(x=>x.latest_recorded_count))/N;
const sourceSiteRows=[],modelRows=[];
for(const baseline of baselines)for(const scenario of scenarios)for(const period of periods)for(const model of models){
 const grid=modelBy.get([model,scenario,period].join("|"));
 if(!grid||grid.size!==40)throw Error("CMIP source cohort changed "+model+scenario+period);
 const data=sites.map(s=>{
  const cm=grid.get(s.site_id);
  if(!cm||!Number.isFinite(cm.change))throw Error("Missing source climate change "+s.site_id);
  const obs=baseline==="1995-2014"?s.observed_SIC_1995_2014_pct:s.observed_SIC_1991_2020_pct;
  const future=Math.max(0,Math.min(100,obs+cm.change));
  return{...s,observed_baseline:baseline,scenario,period,model,
   historical_reference_SIC_pct:obs,
   future_model_change_pp:cm.change,
   conditional_future_20yr_SIC_pct:future,
   clipped_change_pp:future-obs,
   lower_20year_envelope_exceedance_pp:s.historical_20yr_low_pct-future,
   below_historical_20yr_range:future<s.historical_20yr_low_pct,
   beyond_20yr_lower_bound_by_2pp:future<s.historical_20yr_low_pct-2,
   beyond_20yr_lower_bound_by_5pp:future<s.historical_20yr_low_pct-5,
   below_historical_15yr_range:future<s.historical_15yr_low_pct,
   below_historical_10yr_range:future<s.historical_10yr_low_pct,
   below_minimum_historical_single_year:future<s.original_min_one_year_SIC_pct,
   scenario_below_assumed_SIC_77_5:future<77.5,
   novel_20yr_without_crossing_SIC_77_5:future<s.historical_20yr_low_pct&&future>=77.5,
   model_SIC_grid_id:cm.model_grid_id,model_grid_distance_km:cm.grid_distance_km
  };
 });
 if(data.length!==39||uniq(data,x=>x.site_id)!==39)throw Error("Site mismatch");
 sourceSiteRows.push(...data);
 const add=(tag,selected,metrics)=>{
  const ids=selected.filter(metrics);
  return {n:ids.length,count_mass_pct:share(ids),n_model_cells:uniq(ids,x=>x.model_SIC_grid_id)};
 };
 const nov=data.filter(x=>x.below_historical_20yr_range),by2=data.filter(x=>x.beyond_20yr_lower_bound_by_2pp),
       by5=data.filter(x=>x.beyond_20yr_lower_bound_by_5pp),nov10=data.filter(x=>x.below_historical_10yr_range),
       nov15=data.filter(x=>x.below_historical_15yr_range),yearly=data.filter(x=>x.below_minimum_historical_single_year),
       highSicNovel=data.filter(x=>x.novel_20yr_without_crossing_SIC_77_5),
       crop=data.filter(x=>["CRZE","CRZW"].includes(x.site_id)),
       nonCrop=data.filter(x=>!["CRZE","CRZW"].includes(x.site_id));
 modelRows.push({
   observed_baseline:baseline,scenario,period,model,
   original_sites:data.length,
   CMIP_native_cells_total:uniq(data,x=>x.model_SIC_grid_id),
   all_source_median_grid_distance_km:[...data.map(x=>x.model_grid_distance_km)].sort((a,b)=>a-b)[19],
   overall_SIC_change_equal_site_pp:mean(data.map(x=>x.clipped_change_pp)),
   overall_SIC_change_original_count_weighted_pp:weighted(data,"clipped_change_pp"),
   Victoria_Land_SIC_change_count_weighted_pp:weighted(data.filter(x=>x.region==="Victoria Land"),"clipped_change_pp"),
   historical_lower_20yr_n:nov.length,historical_lower_20yr_count_pct:share(nov),
   historical_lower_20yr_2pp_n:by2.length,historical_lower_20yr_2pp_count_pct:share(by2),
   historical_lower_20yr_5pp_n:by5.length,historical_lower_20yr_5pp_count_pct:share(by5),
   historical_lower_15yr_n:nov15.length,historical_lower_15yr_count_pct:share(nov15),
   historical_lower_10yr_n:nov10.length,historical_lower_10yr_count_pct:share(nov10),
   historical_single_year_min_n:yearly.length,historical_single_year_min_count_pct:share(yearly),
   count_novel20_but_future_SIC_at_least_77_5_n:highSicNovel.length,
   count_novel20_but_future_SIC_at_least_77_5_pct:share(highSicNovel),
   Cape_Crozier_below_historical_20yr_2pp_count_pct:share(crop.filter(x=>x.beyond_20yr_lower_bound_by_2pp)),
   historical_lower_20yr_count_pct_excluding_Cape_Crozier_reweight_37:
     100*sum(nonCrop.filter(x=>x.below_historical_20yr_range).map(x=>x.latest_recorded_count))/(N-capeCount),
   n_sites_below_20yr_in_Victoria_Land:nov.filter(x=>x.region==="Victoria Land").length,
   n_sites_below_20yr_outside_Victoria_Land:nov.filter(x=>x.region!=="Victoria Land").length,
   model_cells_below_historical_20yr:uniq(nov,x=>x.model_SIC_grid_id)
 });
}
if(sourceSiteRows.length!==39*2*3*2*2||modelRows.length!==24)
 throw Error("Unexpected future physical site or model cohort dimensions");
const robustRows=[],rangeRows=[];
for(const baseline of baselines)for(const scenario of scenarios)for(const period of periods){
 const filtered=sourceSiteRows.filter(x=>x.observed_baseline===baseline&&x.scenario===scenario&&x.period===period);
 if(filtered.length!==3*39)throw Error("Missing 3-model site projections");
 const siteRows=[];
 for(const site of sites){
  const m=filtered.filter(x=>x.site_id===site.site_id);
  if(m.length!==3)throw Error("Missing model at "+site.site_id);
  const fields=[
   "below_historical_20yr_range",
   "beyond_20yr_lower_bound_by_2pp",
   "beyond_20yr_lower_bound_by_5pp",
   "below_historical_15yr_range",
   "below_historical_10yr_range",
   "below_minimum_historical_single_year",
   "novel_20yr_without_crossing_SIC_77_5"
  ];
  const flags=Object.fromEntries(fields.flatMap(f=>[[f+"_all3",m.every(x=>x[f])],[f+"_any3",m.some(x=>x[f])]]));
  siteRows.push({
   observed_baseline:baseline,scenario,period,site_id:site.site_id,region:site.region,
   latest_recorded_count:site.latest_recorded_count,
   original_20yr_lower_SIC_pct:site.historical_20yr_low_pct,
   original_historical_annual_min_SIC_pct:site.original_min_one_year_SIC_pct,
   min_model_conditional_20yr_SIC_pct:Math.min(...m.map(x=>x.conditional_future_20yr_SIC_pct)),
   max_model_conditional_20yr_SIC_pct:Math.max(...m.map(x=>x.conditional_future_20yr_SIC_pct)),
   minimum_model_margin_below_historical_20yr_lower_pp:Math.min(...m.map(x=>x.lower_20year_envelope_exceedance_pp)),
   maximum_model_margin_below_historical_20yr_lower_pp:Math.max(...m.map(x=>x.lower_20year_envelope_exceedance_pp)),
   ...flags
  });
 }
 robustRows.push(...siteRows);
 const ms=modelRows.filter(x=>x.observed_baseline===baseline&&x.scenario===scenario&&x.period===period);
 if(ms.length!==3)throw Error("Summary climate ensemble missing");
 const all3=siteRows.filter(x=>x.below_historical_20yr_range_all3),
       all3b2=siteRows.filter(x=>x.beyond_20yr_lower_bound_by_2pp_all3),
       all3b5=siteRows.filter(x=>x.beyond_20yr_lower_bound_by_5pp_all3),
       all3d10=siteRows.filter(x=>x.below_historical_10yr_range_all3),
       all3high=siteRows.filter(x=>x.novel_20yr_without_crossing_SIC_77_5_all3);
 rangeRows.push({
  observed_baseline:baseline,scenario,period,
  observed_39_site_count_denominator:N,
  three_model_historical_lower_20yr_count_pct_min:Math.min(...ms.map(x=>x.historical_lower_20yr_count_pct)),
  three_model_historical_lower_20yr_count_pct_max:Math.max(...ms.map(x=>x.historical_lower_20yr_count_pct)),
  three_model_historical_lower_20yr_2pp_pct_min:Math.min(...ms.map(x=>x.historical_lower_20yr_2pp_count_pct)),
  three_model_historical_lower_20yr_2pp_pct_max:Math.max(...ms.map(x=>x.historical_lower_20yr_2pp_count_pct)),
  three_model_historical_lower_20yr_5pp_pct_min:Math.min(...ms.map(x=>x.historical_lower_20yr_5pp_count_pct)),
  three_model_historical_lower_20yr_5pp_pct_max:Math.max(...ms.map(x=>x.historical_lower_20yr_5pp_count_pct)),
  three_model_10yr_lower_pct_min:Math.min(...ms.map(x=>x.historical_lower_10yr_count_pct)),
  three_model_10yr_lower_pct_max:Math.max(...ms.map(x=>x.historical_lower_10yr_count_pct)),
  three_model_yearly_min_pct_min:Math.min(...ms.map(x=>x.historical_single_year_min_count_pct)),
  three_model_yearly_min_pct_max:Math.max(...ms.map(x=>x.historical_single_year_min_count_pct)),
  three_model_novel_but_high_SIC_pct_min:Math.min(...ms.map(x=>x.count_novel20_but_future_SIC_at_least_77_5_pct)),
  three_model_novel_but_high_SIC_pct_max:Math.max(...ms.map(x=>x.count_novel20_but_future_SIC_at_least_77_5_pct)),
  three_model_model_sic_change_equal_site_pp_min:Math.min(...ms.map(x=>x.overall_SIC_change_equal_site_pp)),
  three_model_model_sic_change_equal_site_pp_max:Math.max(...ms.map(x=>x.overall_SIC_change_equal_site_pp)),
  three_model_model_sic_change_count_weighted_pp_min:Math.min(...ms.map(x=>x.overall_SIC_change_original_count_weighted_pp)),
  three_model_model_sic_change_count_weighted_pp_max:Math.max(...ms.map(x=>x.overall_SIC_change_original_count_weighted_pp)),
  robust_all3_20yr_n:all3.length,robust_all3_20yr_count_pct:share(all3),
  robust_all3_20yr_exceedance_more_than_2pp_n:all3b2.length,
  robust_all3_20yr_exceedance_more_than_2pp_count_pct:share(all3b2),
  robust_all3_20yr_exceedance_more_than_5pp_n:all3b5.length,
  robust_all3_20yr_exceedance_more_than_5pp_count_pct:share(all3b5),
  robust_all3_10yr_n:all3d10.length,robust_all3_10yr_count_pct:share(all3d10),
  robust_all3_20yr_but_not_lowSIC77_5_n:all3high.length,robust_all3_20yr_but_not_lowSIC77_5_count_pct:share(all3high),
  robust_all3_Cape_Crozier_both_20yr:crozier.every(x=>all3.some(y=>y.site_id===x.site_id)),
  robust_all3_Cape_Crozier_both_20yr_2pp:crozier.every(x=>all3b2.some(y=>y.site_id===x.site_id)),
  robust_all3_site_ids:all3.map(x=>x.site_id).join(";")
 });
}
if(robustRows.length!==39*2*2*2||rangeRows.length!==8)throw Error("Ensemble cardinality drift");
const median=a=>{const vals=a.slice().sort((x,y)=>x-y);return vals[Math.floor(vals.length/2)]};
// Three penguin species: reuse the same 39 *physical* site coordinate climate rows,
// but select species-supported original long-term breeding-count site codes.
// Site×species pseudo-replicates of climate fields are NOT independent environmental samples.
const species=["ADPE","CHPE","GEPE"];
const speciesSites=new Map(species.map(sp=>[sp,[]]));
const speciesOriginalKeys=new Set();
for(const r of D.species){
 const key=r.site_id+"|"+r.species_id;
 if(speciesOriginalKeys.has(key)||!speciesSites.has(r.species_id)||!siteById.has(r.site_id))
  throw Error("Original 54 species/site climate crosswalk does not match original 39 sites "+key);
 speciesOriginalKeys.add(key);
 const originalSite=siteById.get(r.site_id);
 if(r.region!==originalSite.region)throw Error("Region drift at "+key);
 if(r.species_id==="ADPE"&&Math.abs(+r.slope_log1p_count_decade-originalSite.original_historical_count_growth_decade)>1e-8)
  throw Error("Adelie source species-trend mismatch "+key);
 speciesSites.get(r.species_id).push({
  site_id:r.site_id,species_id:r.species_id,region:r.region,
  original_long_count_method:r.method,
  historical_count_growth_log1p_slope_decade:+r.slope_log1p_count_decade
 });
}
if(speciesSites.get("ADPE").length!==39||speciesSites.get("CHPE").length!==7||speciesSites.get("GEPE").length!==8)
 throw Error("Original species monitoring coverage has changed");
const speciesSiteNicheRows=[],speciesModelRows=[],speciesConsensusRows=[];
for(const baseline of baselines)for(const scenario of scenarios)for(const period of periods){
 const allmodels=sourceSiteRows.filter(x=>x.observed_baseline===baseline&&x.scenario===scenario&&x.period===period);
 for(const sp of species){
  const list=speciesSites.get(sp),members=[];
  for(const src of list){
   const matching=allmodels.filter(x=>x.site_id===src.site_id);
   if(matching.length!==3)throw Error("Missing species site climate model rows "+src.site_id+" "+sp);
   for(const x of matching){
    const rec={
     observed_baseline:baseline,scenario,period,model:x.model,
     site_id:src.site_id,species_id:sp,region:src.region,
     original_long_count_method:src.original_long_count_method,
     historical_count_growth_log1p_slope_decade:src.historical_count_growth_log1p_slope_decade,
     observed_SIC_baseline_pct:x.historical_reference_SIC_pct,
     observed_historical_lower_20year_pct:x.historical_20yr_low_pct,
     future_climate_20yr_SIC_pct:x.conditional_future_20yr_SIC_pct,
     model_grid_cell_id:x.model_SIC_grid_id,
     below_historical_20year_min:x.below_historical_20yr_range,
     below_historical_20year_min_by_2pp:x.beyond_20yr_lower_bound_by_2pp,
     below_historical_20year_min_by_5pp:x.beyond_20yr_lower_bound_by_5pp,
     below_historical_10year_min:x.below_historical_10yr_range
    };
    speciesSiteNicheRows.push(rec);members.push(rec);
   }
  }
  if(members.length!==list.length*3)throw Error("Species source pseudo replication mismatch "+sp);
  for(const model of models){
   const f=members.filter(x=>x.model===model);
   if(f.length!==list.length)throw Error("Species model lacks sites");
   speciesModelRows.push({
    observed_baseline:baseline,scenario,period,model,species_id:sp,
    n_original_species_sites:list.length,
    region_count:uniq(f,x=>x.region),
    original_site_codes_with_novel_lower_20yr_SIC:f.filter(x=>x.below_historical_20year_min).length,
    original_site_codes_at_least_2pp_beyond_hist20yr_min:f.filter(x=>x.below_historical_20year_min_by_2pp).length,
    original_site_codes_at_least_5pp_beyond_hist20yr_min:f.filter(x=>x.below_historical_20year_min_by_5pp).length,
    equal_site_novelty_fraction:f.filter(x=>x.below_historical_20year_min).length/list.length,
    n_distinct_native_CMIP_cells:uniq(f,x=>x.model_grid_cell_id),
    counts_as_independent_climate_replicates:false
   });
  }
  const all3=(criterion)=>list.filter(src=>{
   const observations=members.filter(x=>x.site_id===src.site_id);
   return observations.length===3&&observations.every(x=>x[criterion]);
  });
  speciesConsensusRows.push({
   observed_baseline:baseline,scenario,period,species_id:sp,
   n_original_species_sites:list.length,
   original_species_site_codes_novel_20yr_all3:all3("below_historical_20year_min").length,
   original_species_site_codes_novel_20yr_2pp_all3:all3("below_historical_20year_min_by_2pp").length,
   original_species_site_codes_novel_20yr_5pp_all3:all3("below_historical_20year_min_by_5pp").length,
   original_species_site_codes_novel_10yr_all3:all3("below_historical_10year_min").length,
   species_site_ids_novel_20yr_all3:all3("below_historical_20year_min").map(x=>x.site_id).join(";"),
   source_scope:"only sites in original 54 long-count site-species records; shared climate pixels between different species; NOT a species-specific physiological response"
  });
 }
}
if(speciesSiteNicheRows.length!==54*2*2*2*3||speciesModelRows.length!==3*2*2*2*3||speciesConsensusRows.length!==3*2*2*2)
 throw Error("New three-species site×climate support cross-product incomplete");
const speciesPrimary=speciesModelRows.filter(x=>x.observed_baseline==="1995-2014"&&x.scenario==="ssp585"&&x.period==="2081-2100");
const speciesConsensusPrimary=speciesConsensusRows.filter(x=>x.observed_baseline==="1995-2014"&&x.scenario==="ssp585"&&x.period==="2081-2100");
const original3Species={
 source_species_site_rows:D.species.length,
 species_site_counts:Object.fromEntries(species.map(sp=>[sp,speciesSites.get(sp).length])),
 unique_actual_source_site_codes:uniq(D.species,x=>x.site_id),
 primary_model_species_site_counts:speciesPrimary.map(x=>({species:x.species_id,model:x.model,n_sites:x.n_original_species_sites,novel20_n:x.original_site_codes_with_novel_lower_20yr_SIC})),
 primary_3model_common_sites:speciesConsensusPrimary.map(x=>({species:x.species_id,n_sites:x.n_original_species_sites,novel20_n:x.original_species_site_codes_novel_20yr_all3,novel5_n:x.original_species_site_codes_novel_20yr_5pp_all3}))
};
writeFileSync(join(outputDir,"original_three_species_site_novelty.csv"),toCSV(speciesSiteNicheRows));
writeFileSync(join(outputDir,"three_species_model_site_support.csv"),toCSV(speciesModelRows));
writeFileSync(join(outputDir,"three_species_three_model_site_consensus.csv"),toCSV(speciesConsensusRows));

const fact={
 original_site_n:39,
 species_source_panel_rows:original3Species.source_species_site_rows,
 source_original_CHPE_sites:original3Species.species_site_counts.CHPE,
 source_original_GEPE_sites:original3Species.species_site_counts.GEPE,
 primary_SSP585_late_CHPE_three_model_novel20_n:speciesConsensusPrimary.find(x=>x.species_id==="CHPE").original_species_site_codes_novel_20yr_all3,
 primary_SSP585_late_GEPE_three_model_novel20_n:speciesConsensusPrimary.find(x=>x.species_id==="GEPE").original_species_site_codes_novel_20yr_all3,latest_ADPE_snapshot_count_sum:N,Cape_Crozier_snapshot_count: capeCount,
 min_count_year:Math.min(...sites.map(x=>x.latest_census_year)),max_count_year:Math.max(...sites.map(x=>x.latest_census_year)),
 number_historical_siteyears:39*30,number_20yr_overlapping_windows_per_site:11,
 historical_20yr_band_median_width_pp:median(sites.map(x=>x.historical_20yr_range_pp)),
 original_Crozier_East_1995_2014_SIC:siteById.get("CRZE").observed_SIC_1995_2014_pct,
 original_Crozier_West_1995_2014_SIC:siteById.get("CRZW").observed_SIC_1995_2014_pct,
 scenario_245_mid_ACCESS_historical_20yr_count_pct:modelRows.find(x=>x.observed_baseline==="1995-2014"&&x.scenario==="ssp245"&&x.period==="2041-2060"&&x.model==="ACCESS-CM2").historical_lower_20yr_count_pct,
 scenario_585_late_ACCESS_historical_20yr_count_pct:modelRows.find(x=>x.observed_baseline==="1995-2014"&&x.scenario==="ssp585"&&x.period==="2081-2100"&&x.model==="ACCESS-CM2").historical_lower_20yr_count_pct
};
if(process.argv.includes("--check-receipt")){
 for(const [k,expectedValue] of Object.entries(expected.values)){
  if(!Number.isFinite(fact[k]))throw Error("Nonfinite numerical receipt "+k);
  close(fact[k],expectedValue,k);
 }
 // Annual minima <= any historical rolling average. A condition below the 1-year minimum
 // MUST be below all 10/15/20-year historical minima at that site.
 for(const row of sourceSiteRows){
  if(row.below_minimum_historical_single_year && !(row.below_historical_10yr_range&&row.below_historical_15yr_range&&row.below_historical_20yr_range))
   throw Error("Impossible historical envelope nesting "+row.site_id);
  if(row.beyond_20yr_lower_bound_by_5pp && !row.beyond_20yr_lower_bound_by_2pp)
   throw Error("2/5pp severity nesting broken");
 }
}
mkdirSync(outputDir,{recursive:true});
writeFileSync(join(outputDir,"original_39_site_historical_10_15_20yr_envelopes.csv"),toCSV(sites));
writeFileSync(join(outputDir,"future_site_historical_novelty.csv"),toCSV(sourceSiteRows));
writeFileSync(join(outputDir,"model_scenario_novelty.csv"),toCSV(modelRows));
writeFileSync(join(outputDir,"three_model_site_consensus.csv"),toCSV(robustRows));
writeFileSync(join(outputDir,"three_model_scenario_ranges.csv"),toCSV(rangeRows));
const result={
 status:"source_verified_future_physical_seaice_climatology_novelty_not_demographic_forecast",
 hypothesis:"Future 20-year seasonal SIC may lie below local original historical multidecadal envelope, even where the arbitrary low-ice threshold is not crossed",
 historical_reference:"OSI-SAF 1991–2020 original 30 annual mean Aug-Nov nearshore SIC per breeding site",
 primary_baseline:"1995–2014 observed 20-year SIC + CMIP6 1995–2014-relative anomaly, site matched",
 alternative_baseline:"1991–2020 observed mean + same model anomaly (time-frame sensitivity ONLY)",
 original_population:"39 historical source site codes, selected and geographically biased, mixed census targets 2001–2025",
 historical_windows:"11 overlapping 20-year windows (1991–2010 through 2001–2020), plus 16 overlapping 15-year and 21 overlapping 10-year windows",
 strict_benchmark:"Future 20-year climatological mean must be lower than all local historical 20-year means; 2pp/5pp are sensitivity margins, not significance, hazard or effect sizes",
 caveats:"Overlapping historical windows are correlated, sea ice and climate models have spatial autocorrelation, model grid resolution coarse, only three models/one member, counts noncontemporaneous and mixed metrics. Comparing 20-year future means to 10/15-year minima is a deliberately conservative window-length sensitivity; annual-minimum is a more stringent but timescale-mismatched diagnostic. No biological impact or extinction probabilties.",
 source_git_blobs:blobs,
 receipt:fact,
 model_rows:modelRows,
 ranges:rangeRows,
 three_species_monitoring_site_support:original3Species,
 three_species_model_site_support:speciesModelRows,
 three_species_site_consensus:speciesConsensusRows
};
writeFileSync(join(outputDir,"result.json"),JSON.stringify(result,null,2)+"\n");
writeFileSync(join(outputDir,"validation.json"),JSON.stringify({
 original_source_SHA_checked:true,n_original_sites:sites.length,n_historical_siteyears:39*30,
 n_historical_20yr_windows:39*11,n_site_scenario_model_baseline_rows:sourceSiteRows.length,
 n_model_summaries:modelRows.length,n_ensemble_summaries:rangeRows.length,
 n_all_model_consensus_rows:robustRows.length,
 n_original_three_species_site_trend_rows:speciesSiteNicheRows.length,
 n_species_model_summary_rows:speciesModelRows.length,
 n_species_three_model_agreement_rows:speciesConsensusRows.length,
 expected_receipt_checked:process.argv.includes("--check-receipt"),
 physical_only_no_population_model:true
},null,2)+"\n");
console.log("HISTORICAL SEAICE PHYSICAL NOVELTY "+JSON.stringify({
 receipt:fact,
 primary_ranges:rangeRows.filter(x=>x.observed_baseline==="1995-2014"),
 model_585_late:modelRows.filter(x=>x.observed_baseline==="1995-2014"&&x.scenario==="ssp585"&&x.period==="2081-2100"),
 three_species_source_support:original3Species,
 key_Crozier:sourceSiteRows.filter(x=>x.observed_baseline==="1995-2014"&&x.scenario==="ssp585"&&x.period==="2081-2100"&&["CRZE","CRZW"].includes(x.site_id)).map(x=>({site:x.site_id,model:x.model,future:x.conditional_future_20yr_SIC_pct,hist20low:x.historical_20yr_low_pct,histAnnualMin:x.original_min_one_year_SIC_pct,lower20margin:x.lower_20year_envelope_exceedance_pp})),
 verified:process.argv.includes("--check-receipt")
}));
