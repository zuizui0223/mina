// Fixed original breeding-census allocation × observed annual coastal SIC covariation, 1991–2020.
// No future survival/abundance forecast and NO claim that model cells are independent bird foraging habitats.
// Run: node research/climate-penguin/work/seaice_covariance_portfolio_v1/build.mjs --check-receipt
import {readFileSync,writeFileSync,mkdirSync} from "node:fs";
import {join,resolve} from "node:path";
import {createHash} from "node:crypto";

const root=resolve("research/climate-penguin/outputs");
const out=join(root,"seaice_covariance_portfolio_v1");
const sources={
  hist:["historical_ice_breeding_transfer_v1/adeli_39site_historical_climate_growth.csv","db58938630e80d22ba445600ce1ad3f554c452e2"],
  ice:["climate_penguin/macro_monthly_seaice_1991_2020.csv","4fcea71c2d8b1069b6ad143f6522061ed434daf5"],
  counts:["comparison_audit/mapppd_unambiguous_site_seasons.csv","fc134e364cf38699fa7611d7dee5fbbbcb370c0a"],
  cmip:["cmip6_projection_v1/site_model_changes.csv","b383ef1cc3b0807b0bd010ca0e825937ab83ce97"]
};
const exp=JSON.parse(readFileSync(join(out,"expected_receipt.json"),"utf8"));
function csvParse(s){
 const rows=[];let row=[],value="",quoted=false;
 for(let i=0;i<s.length;i++){
  const c=s[i];
  if(quoted){if(c==='"'&&s[i+1]==='"'){value+='"';i++}else if(c==='"')quoted=false;else value+=c;}
  else if(c==='"')quoted=true;
  else if(c===','){row.push(value);value=""}
  else if(c==='\n'){row.push(value.replace(/\r$/,""));if(row.length>1)rows.push(row);row=[];value=""}
  else value+=c;
 }
 if(row.length||value){row.push(value);rows.push(row)}
 if(quoted||rows.length<2)throw Error("Invalid source CSV");
 const head=rows.shift();
 return rows.map((r,i)=>{
  if(r.length!==head.length)throw Error("Source CSV row width "+i);
  return Object.fromEntries(head.map((name,j)=>[name,r[j]]));
 });
}
function toCSV(rows){
 if(!rows.length)throw Error("Empty output");
 const head=Object.keys(rows[0]);
 const q=x=>{const s=x===null||x===undefined?"":String(x);return /[,"\r\n]/.test(s)?'"'+s.replaceAll('"','""')+'"':s};
 return head.join(",")+"\n"+rows.map(x=>head.map(k=>q(x[k])).join(",")).join("\n")+"\n";
}
const DATA={};
for(const [key,[rel,sha]] of Object.entries(sources)){
 const src=readFileSync(join(root,rel));
 const blob=createHash("sha1").update(Buffer.from("blob "+src.length+"\0")).update(src).digest("hex");
 if(blob!==sha||exp.source_git_blobs[key]!==sha)throw Error("Upstream original Git blob changed "+key+" "+blob);
 DATA[key]=csvParse(src.toString("utf8"));
}
if(DATA.hist.length!==39||DATA.ice.length!==9600||DATA.counts.length!==2999||DATA.cmip.length!==3816)
 throw Error("Original source cohort changed");
const mean=a=>a.reduce((s,x)=>s+x,0)/a.length;
const sum=a=>a.reduce((s,x)=>s+x,0);
const std=a=>Math.sqrt(sum(a.map(v=>(v-mean(a))**2))/(a.length-1));
const nUnique=(a,k)=>new Set(a.map(k)).size;
const close=(x,y,label)=>{
 if(!Number.isFinite(x)||Math.abs(x-y)>1e-8)throw Error("Independent numeric receipt mismatch: "+label+" got "+x+" vs "+y);
};
const siteSet=new Set(DATA.hist.map(x=>x.site_id));
if(siteSet.size!==39)throw Error("Historical sites are not unique");
const countsBySite=new Map();
for(const r of DATA.counts){
 if(!siteSet.has(r.site_id)||r.species_id!=="ADPE"||r.count===""||!Number.isFinite(+r.count)||+r.count<0)continue;
 const a=countsBySite.get(r.site_id)||[];a.push(r);countsBySite.set(r.site_id,a);
}
const iceMap=new Map();
for(const r of DATA.ice){
 if(!siteSet.has(r.site_id)||![8,9,10,11].includes(+r.month)||r.complete_month!=="True")continue;
 if(!["0","100"].includes(r.inner_km))throw Error("Unexpected original ice band "+r.inner_km);
 const k=r.site_id+"|"+r.year+"|"+r.inner_km,a=iceMap.get(k)||[];
 a.push(+r.sic_mean);iceMap.set(k,a);
}
const years=Array.from({length:30},(_,i)=>1991+i);
const rawSource=DATA.hist.map(h=>{
 const candidate=(countsBySite.get(h.site_id)||[]).sort((a,b)=>+b.season-+a.season);
 if(!candidate.length)throw Error("No recorded nest count "+h.site_id);
 const sameMethod=candidate.find(z=>z.method===h.method);
 if(!sameMethod)throw Error("No count matching selected historic method "+h.site_id);
 const one={site_id:h.site_id,region:h.region,
  original_hist_method:h.method,latest_count:+candidate[0].count,
  latest_count_year:+candidate[0].season,latest_count_method:candidate[0].method,
  selected_method_latest_count:+sameMethod.count,selected_method_latest_year:+sameMethod.season};
 for(const [band,key] of [[0,"near"],[100,"off"]]){
  one[key]=years.map(year=>{
   const vals=iceMap.get(h.site_id+"|"+year+"|"+band);
   if(!vals||vals.length!==4||!vals.every(Number.isFinite))throw Error("Missing annual original SIC "+h.site_id+" "+year+" "+band);
   return mean(vals);
  });
 }
 close(mean(one.near),+h.historical_nearshore_AugNov_SIC_mean_pct,"source historical SIC "+h.site_id);
 return one;
});
const n=rawSource.length,T=years.length;
const totalCount=sum(rawSource.map(x=>x.latest_count));
const sameMethodTotal=sum(rawSource.map(x=>x.selected_method_latest_count));
const crozierCount=sum(rawSource.filter(x=>["CRZE","CRZW"].includes(x.site_id)).map(x=>x.latest_count));
const latest=rawSource.map(x=>x.latest_count/totalCount);
const selectedMethod=rawSource.map(x=>x.selected_method_latest_count/sameMethodTotal);
const equal=rawSource.map(()=>1/n);
const noCrozier=rawSource.map(x=>["CRZE","CRZW"].includes(x.site_id)?0:x.latest_count/(totalCount-crozierCount));
const regionNames=[...new Set(rawSource.map(x=>x.region))];
const byRegion=new Map(regionNames.map(region=>[region,rawSource.map((x,i)=>x.region===region?i:-1).filter(i=>i!==-1)]));
const regionalEqual=rawSource.map(x=>{
 const sameRegion=byRegion.get(x.region);
 return sum(sameRegion.map(i=>rawSource[i].latest_count))/totalCount/sameRegion.length;
});
const weights={latest,equal,regionEqual:regionalEqual,selectedHistoricMethod:selectedMethod,noCrozier};
const weightFields=Object.keys(weights);
for(const [key,w] of Object.entries(weights))close(sum(w),1,"weight-normalization "+key);
if(totalCount!==1074279||sameMethodTotal!==1099853||crozierCount!==242681)
 throw Error("Frozen census snapshot values changed");
function detrend(a){
 const m=mean(a),t=(a.length-1)/2;
 const xx=sum(a.map((_,i)=>(i-t)**2));
 const b=sum(a.map((v,i)=>(i-t)*(v-m)))/xx;
 return a.map((v,i)=>v-m-b*(i-t));
}
function standardized(a){
 const m=mean(a),sd=std(a);
 if(sd<1e-9)throw Error("No climate temporal variation in source band");
 return a.map(x=>(x-m)/sd);
}
function portValues(mat,w){
 if(mat.length!==n||w.length!==n)throw Error("Wrong matrix dimensions");
 return years.map((_,t)=>sum(w.map((value,i)=>value*mat[i][t])));
}
function portfolio(mat,w){
 const yr=portValues(mat,w);
 return {mean:mean(yr),sd:std(yr),minimum:Math.min(...yr),maximum:Math.max(...yr),annual:yr};
}
const diagnostics=[],annualPortfolio=[],siteRows=[];
const bandMats={};
for(const key of ["near","off"]){
 const raw=rawSource.map(x=>x[key]);
 const standardizedOriginal=raw.map(standardized);
 const residual=raw.map(detrend);
 const residualStandardized=residual.map(standardized);
 bandMats[key]={raw,standardized:standardizedOriginal,detrended:residual,detrendedStandardized:residualStandardized};
 for(const wname of weightFields){
  const w=weights[wname],a=portfolio(raw,w),
   z=portfolio(standardizedOriginal,w),d=portfolio(residual,w),
   dz=portfolio(residualStandardized,w);
  const record={
   spatial_band:key==="near"?"0-100km":"100-500km",
   original_site_n:n,observed_calendar_years:T,weight_scheme:wname,
   mean_physical_SIC_pct:a.mean,
   physical_SIC_annual_SD_pp:a.sd,
   standardized_site_anomaly_common_SD:z.sd,
   detrended_physical_SIC_annual_SD_pp:d.sd,
   detrended_standardized_anomaly_common_SD:dz.sd,
   covariance_equivalent_units_heuristic:1/(z.sd*z.sd),
   detrended_covariance_equivalent_units_heuristic:1/(dz.sd*dz.sd),
   note:"Observed annual satellite SIC covariance, not independent ecological risks or future breeding demography"
  };
  diagnostics.push(record);
  for(let j=0;j<years.length;j++){
   annualPortfolio.push({
    year:years[j],spatial_band:record.spatial_band,weight_scheme:wname,
    original_record_weighted_SIC_pct:a.annual[j],
    sitewise_standardized_anomaly:z.annual[j],
    detrended_physical_anomaly_pp:d.annual[j],
    detrended_sitewise_standardized_anomaly:dz.annual[j]
   });
  }
 }
 for(const item of rawSource){
  siteRows.push({
   site_id:item.site_id,region:item.region,spatial_band:key==="near"?"0-100km":"100-500km",
   latest_recorded_count:item.latest_count,latest_count_year:item.latest_count_year,
   latest_count_method:item.latest_count_method,historical_method:item.original_hist_method,
   latest_record_of_historical_method:item.selected_method_latest_count,
   mean_1991_2020_SIC_pct:mean(item[key]),
   observed_annual_SIC_SD_pp:std(item[key]),
   original_year_range:"1991–2020",months:"August–November"
  });
 }
}
const permutationReference=[];
const permutations=12000;
for(const band of ["near","off"]){
 const matrices=bandMats[band],score={};
 const permutationDistribution={raw:[],z:[],zDetrended:[]};
 let seed=20261101;
 const rng=()=>{
  seed=(Math.imul(seed,1664525)+1013904223)>>>0;
  return seed/4294967296;
 };
 for(let b=0;b<permutations;b++){
  const shuffled=latest.slice();
  for(const ids of byRegion.values()){
   const ordered=ids.map(i=>shuffled[i]);
   for(let i=ordered.length-1;i>0;i--){
    const j=Math.floor(rng()*(i+1));
    [ordered[i],ordered[j]]=[ordered[j],ordered[i]];
   }
   for(let j=0;j<ids.length;j++)shuffled[ids[j]]=ordered[j];
  }
  permutationDistribution.raw.push(portfolio(matrices.raw,shuffled).sd);
  permutationDistribution.z.push(portfolio(matrices.standardized,shuffled).sd);
  permutationDistribution.zDetrended.push(portfolio(matrices.detrendedStandardized,shuffled).sd);
 }
 const observed={
  raw:portfolio(matrices.raw,latest).sd,
  z:portfolio(matrices.standardized,latest).sd,
  zDetrended:portfolio(matrices.detrendedStandardized,latest).sd
 };
 for(const [metric,arr] of Object.entries(permutationDistribution)){
  arr.sort((a,b)=>a-b);
  const take=p=>arr[Math.floor(arr.length*p)];
  const smaller=arr.filter(x=>x<=observed[metric]).length;
  permutationReference.push({
   spatial_band:band==="near"?"0-100km":"100-500km",
   statistic:metric,
   original_census_allocation_observed_SD:observed[metric],
   region_size_shuffles:permutations,
   region_conditioned_shuffle_mean_SD:mean(arr),
   region_conditioned_shuffle_median_SD:take(.5),
   region_conditioned_shuffle_p05_SD:take(.05),
   region_conditioned_shuffle_p95_SD:take(.95),
   fraction_arithmetic_shuffles_no_greater_than_observed:smaller/permutations,
   fraction_arithmetic_shuffles_not_below_observed:(permutations-smaller)/permutations,
   source_of_randomness:"deterministic LCGenerator 20261101 reset per spatial band",
   inference:"descriptive counterfactual on fixed geographic site-code map; not a biologically calibrated p-value"
  });
 }
}
// The *same* 39 site weights applied to observationally anchored future marine SIC changes.
// This is a physical exposure index only, not a forecast of colony growth, breeding success,
// climate response, or spatial redistribution in 2050/2100.
const originalCMIP=new Map();
for(const r of DATA.cmip){
 if(r.cohort!=="macro_40"||r.variable_id!=="siconc")continue;
 const id=[r.source_id,r.experiment_id,r.period].join("|"),
  m=originalCMIP.get(id)||new Map();
 if(m.has(r.site_id))throw Error("Multiple source climate rows for original site");
 m.set(r.site_id,+r.change);
 originalCMIP.set(id,m);
}
const futureWeightedMeanShifts=[];
const minmax=(a)=>[Math.min(...a),Math.max(...a)];
for(const experiment of ["ssp245","ssp585"])
for(const period of ["2041-2060","2081-2100"])
for(const model of ["ACCESS-CM2","BCC-CSM2-MR","CESM2"]){
 const mp=originalCMIP.get([model,experiment,period].join("|"));
 if(!mp||mp.size!==40)throw Error("Original 40 macro site model support changed");
 const siteChanges=rawSource.map(s=>{
  const anomaly=mp.get(s.site_id);
  if(!Number.isFinite(anomaly))throw Error("Missing CMIP6 future physical anomaly "+s.site_id);
  const obs=mean(s.near.slice(4,24));
  return Math.min(100,Math.max(0,obs+anomaly))-obs;
 });
 for(const [scheme,w] of Object.entries(weights)){
  const avgPhysical=sum(w.map((wi,i)=>wi*siteChanges[i]));
  futureWeightedMeanShifts.push({
   experiment,period,model,site_count:rawSource.length,weight_scheme:scheme,
   physically_clipped_mean_nearshore_SIC_change_pp:avgPhysical,
   historical_satellite_reference:"1995–2014 (August–November)",
   future_CMIP6_period:"2041–2060 or 2081–2100",
   interpretation:"observed_anchor_plus_model_anomaly_not_a_breeding_population_forecast"
  });
 }
}
if(futureWeightedMeanShifts.length!==60||nUnique(futureWeightedMeanShifts,x=>[x.experiment,x.period,x.model,x.weight_scheme].join("|"))!==60)
 throw Error("Original CMIP6 4x3x5 physical portfolio cohort changed");
const late585=futureWeightedMeanShifts.filter(x=>x.experiment==="ssp585"&&x.period==="2081-2100");
const byWeight=[];
for(const scheme of weightFields){
 const arr=late585.filter(x=>x.weight_scheme===scheme).map(x=>x.physically_clipped_mean_nearshore_SIC_change_pp);
 if(arr.length!==3)throw Error("Missing 3 CMIP physical model shifts");
 const [min,max]=minmax(arr);
 byWeight.push({weight_scheme:scheme,scenario:"ssp585",period:"2081-2100",model_min_change_pp:min,model_max_change_pp:max,model_count:3});
}

const find=(band,w)=>diagnostics.find(x=>x.spatial_band===band&&x.weight_scheme===w);
const northMean=rawSource.filter(x=>x.region==="Victoria Land");
const countInNorth=sum(northMean.map(x=>x.latest_count));
const facts={
 original_sites:n,
 original_annual_site_years:n*T,
 latest_census_count_total:totalCount,
 same_historical_method_latest_count_total:sameMethodTotal,
 cape_crozier_census_count:crozierCount,
 victoria_land_latest_count_share:countInNorth/totalCount,
 near_equal_rawSD_pp:find("0-100km","equal").physical_SIC_annual_SD_pp,
 near_latest_rawSD_pp:find("0-100km","latest").physical_SIC_annual_SD_pp,
 near_equal_standardizedSD:find("0-100km","equal").standardized_site_anomaly_common_SD,
 near_latest_standardizedSD:find("0-100km","latest").standardized_site_anomaly_common_SD,
 near_latest_detrended_standardizedSD:find("0-100km","latest").detrended_standardized_anomaly_common_SD,
 near_equal_detrended_standardizedSD:find("0-100km","equal").detrended_standardized_anomaly_common_SD,
 off_equal_standardizedSD:find("100-500km","equal").standardized_site_anomaly_common_SD,
 off_latest_standardizedSD:find("100-500km","latest").standardized_site_anomaly_common_SD,
 off_equal_rawSD_pp:find("100-500km","equal").physical_SIC_annual_SD_pp,
 off_latest_rawSD_pp:find("100-500km","latest").physical_SIC_annual_SD_pp,
 ssp585_late_ACCESS_latest_physical_change_pp:late585.find(x=>x.model==="ACCESS-CM2"&&x.weight_scheme==="latest").physically_clipped_mean_nearshore_SIC_change_pp,
 ssp585_late_ACCESS_equal_physical_change_pp:late585.find(x=>x.model==="ACCESS-CM2"&&x.weight_scheme==="equal").physically_clipped_mean_nearshore_SIC_change_pp,
 ssp585_late_BCC_latest_physical_change_pp:late585.find(x=>x.model==="BCC-CSM2-MR"&&x.weight_scheme==="latest").physically_clipped_mean_nearshore_SIC_change_pp,
 ssp585_late_BCC_equal_physical_change_pp:late585.find(x=>x.model==="BCC-CSM2-MR"&&x.weight_scheme==="equal").physically_clipped_mean_nearshore_SIC_change_pp,
 ssp585_late_CESM_latest_physical_change_pp:late585.find(x=>x.model==="CESM2"&&x.weight_scheme==="latest").physically_clipped_mean_nearshore_SIC_change_pp,
 ssp585_late_CESM_equal_physical_change_pp:late585.find(x=>x.model==="CESM2"&&x.weight_scheme==="equal").physically_clipped_mean_nearshore_SIC_change_pp
};
if(process.argv.includes("--check-receipt")){
 for(const [key,want] of Object.entries(exp.values))close(facts[key],want,key);
 for(const row of diagnostics){
  if(!(row.mean_physical_SIC_pct>=0&&row.mean_physical_SIC_pct<=100))throw Error("SIC mean out of range");
  if(!Number.isFinite(row.standardized_site_anomaly_common_SD))throw Error("Nonfinite anomaly SD");
 }
}
mkdirSync(out,{recursive:true});
writeFileSync(join(out,"fixed_site_source_and_annual_sic_traits.csv"),toCSV(siteRows));
writeFileSync(join(out,"annual_weighted_and_standardized_SIC_portfolios.csv"),toCSV(annualPortfolio));
writeFileSync(join(out,"observed_spatial_covariance_weight_diagnostics.csv"),toCSV(diagnostics));
writeFileSync(join(out,"region_constrained_count_shuffle_reference.csv"),toCSV(permutationReference));
writeFileSync(join(out,"future_climate_mean_change_same_site_weights.csv"),toCSV(futureWeightedMeanShifts));
writeFileSync(join(out,"ssp585_late_future_mean_change_weight_ranges.csv"),toCSV(byWeight));
writeFileSync(join(out,"summary.json"),JSON.stringify({
 status:"source_verified_spatial_covariance_of_observed_sea_ice_not_penguin_climate_risk",
 original_source_git_blobs:Object.fromEntries(Object.entries(sources).map(([k,[,sha]])=>[k,sha])),
 source_cohort:{original_site_codes:n,calendar_years:[1991,2020],original_site_years:T*n,
  current_census_weight_count:totalCount,current_census_latest_years:"noncontemporaneous 2001–2025",
  current_victoria_share:countInNorth/totalCount,original_Crozier_weight:crozierCount},
 facts,diagnostics,region_conditioned_shuffles:permutationReference,
 future_climate_same_site_weight_changes:futureWeightedMeanShifts,
 future_ssp585_late_model_ranges:byWeight,
 scientific_interpretation:"Unstandardized (raw pp) count-weighted nearshore temporal SIC fluctuations are smaller than equal-site, but unit-SD-normalized anomalies show greater spatial covariance. This is driven largely by the site-geography composition: within-region shuffles do not show a special nearshore allocation. Offshore band is more synchronous and has different within-region allocation. These are not survival or nest growth results.",
 caveats:"Original 39 sites selected/bias toward Victoria Land. Several adjacent site codes share overlapping nearshore SIC windows and model cells; 30 annual observations and 5 regions are not independent replicated environments. Latest 2001–2025 counts can be different methods/targets; normalized SD is a hypothetical statistical standardization, not biological response or danger. Shared-variance effective-unit number is a covariance heuristic only, not number of independent breeding sites, island habitats, or climate realizations."
},null,2)+"\n");
writeFileSync(join(out,"validation.json"),JSON.stringify({
 source_git_blobs_pinned:true,
 frozen_receipt_checked:process.argv.includes("--check-receipt"),
 historical_site_codes:n,historical_years:T,observed_bands:2,
 output_site_band_rows:siteRows.length,output_annual_portfolios:annualPortfolio.length,
 output_portfolio_statistics:diagnostics.length,output_shuffle_reference:permutationReference.length,
 original_CMIP_model_rows:DATA.cmip.length,output_scenario_weight_model_rows:futureWeightedMeanShifts.length,
 consecutive_years:years.every((x,i)=>x===1991+i),
 trained_demographic_response_model:false,
 forecast_of_future_penguin_nests:false,
 interpreted_as_ecological_inferential_p_value:false
},null,2)+"\n");
console.log("BREEDING CENSUS CLIMATE COVARIANCE "+JSON.stringify({
 source_facts:facts,
 near_models:diagnostics.filter(x=>x.spatial_band==="0-100km"),
 off_models:diagnostics.filter(x=>x.spatial_band==="100-500km"),
 permutation_summary:permutationReference,
 SSP585_late_future_climate_same_source_weight_comparison:byWeight,
 original_receipt_passed:process.argv.includes("--check-receipt")
}));
