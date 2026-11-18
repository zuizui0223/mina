// CMIP6 historical nearshore SIC bias audit for the original 39 Adélie census sites.
// The raw model future is deliberately shown as a diagnostic of observational-baseline
// incompatibility; it is NOT a more valid demographic or climate projection than delta correction.
import {readFileSync,writeFileSync,mkdirSync} from "node:fs";
import {resolve,join} from "node:path";
import {createHash} from "node:crypto";
const data=resolve("research/climate-penguin/outputs");
const out=join(data,"seaice_cmip_historical_bias_v1");
const sources={
 hist:["historical_ice_breeding_transfer_v1/adeli_39site_historical_climate_growth.csv","db58938630e80d22ba445600ce1ad3f554c452e2"],
 sic:["climate_penguin/macro_monthly_seaice_1991_2020.csv","4fcea71c2d8b1069b6ad143f6522061ed434daf5"],
 counts:["comparison_audit/mapppd_unambiguous_site_seasons.csv","fc134e364cf38699fa7611d7dee5fbbbcb370c0a"],
 historicalCMIP:["cmip6_projection_v1/seasonal_climatologies.csv","2a794a27fbd6460f7efc78cf09d5d3e98d38fd45"],
 futureCMIP:["cmip6_projection_v1/site_model_changes.csv","b383ef1cc3b0807b0bd010ca0e825937ab83ce97"]
};
const receipt=JSON.parse(readFileSync(join(out,"expected_receipt.json"),"utf8"));
function parseCSV(s){
 const lines=[];let row=[],v="",q=false;
 for(let i=0;i<s.length;i++){
  const c=s[i];
  if(q){if(c==='"'&&s[i+1]==='"'){v+='"';i++}else if(c==='"')q=false;else v+=c}
  else if(c==='"')q=true;
  else if(c===','){row.push(v);v=""}
  else if(c==='\n'){row.push(v.replace(/\r$/,""));if(row.length>1)lines.push(row);row=[];v=""}
  else v+=c;
 }
 if(row.length||v){row.push(v);lines.push(row)}
 if(q||!lines.length)throw Error("Malformed original CSV");
 const h=lines.shift();
 return lines.map((row,i)=>{
  if(row.length!==h.length)throw Error("Original CSV source width mismatch at "+i);
  return Object.fromEntries(h.map((x,j)=>[x,row[j]]));
 });
}
function csv(rows){
 if(!rows.length)throw Error("empty source output");
 const h=Object.keys(rows[0]),esc=x=>{
  const s=x===undefined||x===null?"":String(x);
  return /[,"\n\r]/.test(s)?'"'+s.replaceAll('"','""')+'"':s;
 };
 return h.join(",")+"\n"+rows.map(row=>h.map(k=>esc(row[k])).join(",")).join("\n")+"\n";
}
const avg=a=>{if(!a.length)throw Error("empty average");return a.reduce((s,x)=>s+x,0)/a.length};
const sum=a=>a.reduce((s,x)=>s+x,0);
const uniq=(arr,fn)=>new Set(arr.map(fn)).size;
const close=(a,b,name,eps=1e-8)=>{if(!Number.isFinite(a)||Math.abs(a-b)>eps)throw Error("Source receipt error "+name+" got "+a+" expected "+b)};
function pear(a,b){
 if(a.length!==b.length||a.length<3)return null;
 const am=avg(a),bm=avg(b),cov=sum(a.map((x,i)=>(x-am)*(b[i]-bm)));
 const sx=sum(a.map(x=>(x-am)**2)),sy=sum(b.map(x=>(x-bm)**2));
 return sx>0&&sy>0?cov/Math.sqrt(sx*sy):null;
}
const D={};
for(const [k,[p,sha]] of Object.entries(sources)){
 const bytes=readFileSync(join(data,p));
 const actual=createHash("sha1").update(Buffer.from("blob "+bytes.length+"\0")).update(bytes).digest("hex");
 if(actual!==sha||receipt.source_git_blobs[k]!==sha)throw Error("Source pin change "+k+" "+actual);
 D[k]=parseCSV(bytes.toString("utf8"));
}
if(D.hist.length!==39||D.sic.length!==9600||D.counts.length!==2999||
 D.historicalCMIP.length!==4770||D.futureCMIP.length!==3816)throw Error("Original source cohorts drifted");
const historicalIDs=new Set(D.hist.map(x=>x.site_id));
if(historicalIDs.size!==39)throw Error("Original historical source site duplication");
const SICmonths=new Map();
for(const x of D.sic){
 if(!historicalIDs.has(x.site_id)||x.inner_km!=="0"||![8,9,10,11].includes(+x.month))continue;
 if(x.complete_month!=="True")throw Error("Original observed month incomplete");
 const k=x.site_id+"|"+x.year,a=SICmonths.get(k)||[];
 a.push(+x.sic_mean);SICmonths.set(k,a);
}
const counts=new Map();
for(const x of D.counts){
 if(!historicalIDs.has(x.site_id)||x.species_id!=="ADPE"||
 x.count===""||!Number.isFinite(+x.count)||+x.count<0)continue;
 const a=counts.get(x.site_id)||[];a.push(x);counts.set(x.site_id,a);
}
const sites=[];
for(const h of D.hist){
 const annual=[];
 for(let y=1991;y<=2020;y++){
  const months=SICmonths.get(h.site_id+"|"+y);
  if(!months||months.length!==4||!months.every(Number.isFinite))throw Error("Original monthly SIC missing "+h.site_id+y);
  annual.push(avg(months));
 }
 const observed30=avg(annual);
 close(observed30,+h.historical_nearshore_AugNov_SIC_mean_pct,"source historical 30 year "+h.site_id);
 const observed20=avg(annual.slice(4,24));
 const oldest20=avg(annual.slice(0,20)),newest20=avg(annual.slice(10,30));
 const historical20Min=Math.min(...Array.from({length:11},(_,i)=>avg(annual.slice(i,i+20))));
 const historical20MaxDrop=Math.max(0,oldest20-newest20);
 const a20=annual.slice(4,24),obsSD=Math.sqrt(avg(a20.map(x=>(x-observed20)**2)));
 const a=(counts.get(h.site_id)||[]).sort((a,b)=>+b.season-+a.season);
 if(!a.length)throw Error("No original count weight for "+h.site_id);
 sites.push({
  site_id:h.site_id,region:h.region,latest_recorded_count:+a[0].count,
  latest_recorded_count_year:+a[0].season,
  observed_1995_2014_AugNov_SIC_pct:observed20,
  observed_annual_SIC_SD_1995_2014_pp:obsSD,
  historical_min_rolling_20yr_SIC_pct:historical20Min,
  historical_max_same_20yr_window_drop_10yr_shift_pp:historical20MaxDrop,
  observed_1991_2010_AugNov_SIC_pct:oldest20,
  observed_2001_2020_AugNov_SIC_pct:newest20
 });
}
const siteByID=new Map(sites.map(x=>[x.site_id,x]));
const N=sum(sites.map(x=>x.latest_recorded_count));
if(N!==1074279)throw Error("Original latest count source drift "+N);
const historicalCMIP=new Map();
for(const x of D.historicalCMIP){
 if(x.cohort!=="macro_40"||x.variable_id!=="siconc"||x.experiment_id!=="historical"||
 x.period!=="1995-2014"||!historicalIDs.has(x.site_id))continue;
 const key=x.source_id+"|"+x.site_id;
 if(historicalCMIP.has(key))throw Error("Duplicate historical SIC model key");
 historicalCMIP.set(key,x);
}
const models=["ACCESS-CM2","BCC-CSM2-MR","CESM2"],scenarios=["ssp245","ssp585"],periods=["2041-2060","2081-2100"];
if(historicalCMIP.size!==3*39)throw Error("SIC historical model source not complete");
const historicalRows=[];
for(const model of models)for(const site of sites){
 const h=historicalCMIP.get(model+"|"+site.site_id);
 if(!h||+h.complete_years!==20||!Number.isFinite(+h.seasonal_mean))throw Error("No model historical nearshore support");
 const baseline=+h.seasonal_mean,bias=baseline-site.observed_1995_2014_AugNov_SIC_pct;
 historicalRows.push({
  model,site_id:site.site_id,region:site.region,
  latest_recorded_count:site.latest_recorded_count,
  observed_reference_1995_2014_SIC_pct:site.observed_1995_2014_AugNov_SIC_pct,
  original_model_reference_1995_2014_SIC_pct:baseline,
  model_minus_observed_bias_pp:bias,
  absolute_baseline_bias_pp:Math.abs(bias),
  observed_interannual_SIC_SD_pp:site.observed_annual_SIC_SD_1995_2014_pp,
  model_interannual_SIC_SD_pp:+h.annual_sd,
  SD_model_over_observed_ratio:site.observed_annual_SIC_SD_1995_2014_pp>1e-9?(+h.annual_sd)/site.observed_annual_SIC_SD_1995_2014_pp:null,
  native_model_seaice_grid_id:h.grid_cell_id,
  distance_to_model_coastal_grid_km:+h.distance_km
 });
}
const histByKey=new Map(historicalRows.map(x=>[x.model+"|"+x.site_id,x]));
const historicalSkill=[];
for(const model of models){
 const rows=historicalRows.filter(x=>x.model===model);
 const summary=(label,x)=>({
  model,region:label,site_codes:x.length,distinct_model_seaice_grid_cells:uniq(x,z=>z.native_model_seaice_grid_id),
  source_sites_more_than_25km:x.filter(z=>z.distance_to_model_coastal_grid_km>25).length,
  source_sites_more_than_50km:x.filter(z=>z.distance_to_model_coastal_grid_km>50).length,
  mean_signed_model_minus_observed_bias_pp:avg(x.map(z=>z.model_minus_observed_bias_pp)),
  mean_absolute_model_baseline_error_pp:avg(x.map(z=>z.absolute_baseline_bias_pp)),
  median_absolute_model_baseline_error_pp:x.map(z=>z.absolute_baseline_bias_pp).sort((a,b)=>a-b)[Math.floor(x.length/2)],
  root_mean_squared_model_baseline_error_pp:Math.sqrt(avg(x.map(z=>z.model_minus_observed_bias_pp**2))),
  recorded_census_weighted_model_absolute_error_pp:sum(x.map(z=>z.absolute_baseline_bias_pp*z.latest_recorded_count))/sum(x.map(z=>z.latest_recorded_count)),
  site_level_spatial_model_vs_observed_r:pear(x.map(z=>z.original_model_reference_1995_2014_SIC_pct),x.map(z=>z.observed_reference_1995_2014_SIC_pct))
 });
 historicalSkill.push(summary("ALL",rows));
 for(const reg of [...new Set(rows.map(z=>z.region))].sort())
  historicalSkill.push(summary(reg,rows.filter(z=>z.region===reg)));
}
const futureByKey=new Map();
for(const x of D.futureCMIP){
 if(x.cohort!=="macro_40"||x.variable_id!=="siconc"||!historicalIDs.has(x.site_id))continue;
 const key=[x.source_id,x.experiment_id,x.period,x.site_id].join("|");
 if(futureByKey.has(key))throw Error("CMIP site future key duplicates");
 futureByKey.set(key,x);
}
if(futureByKey.size!==39*models.length*scenarios.length*periods.length)
 throw Error("No original 39-site scenario supports");
const futures=[];
for(const scenario of scenarios)for(const period of periods)
for(const model of models)for(const site of sites){
 const h=histByKey.get(model+"|"+site.site_id),
 future=futureByKey.get([model,scenario,period,site.site_id].join("|"));
 if(!h||!future)throw Error("Broken climate key");
 close(+future.baseline_1995_2014,h.original_model_reference_1995_2014_SIC_pct,"historical vs delta baseline");
 close(+future.seasonal_mean-(+future.baseline_1995_2014),+future.change,"physical future delta identity");
 if(future.grid_cell_id!==h.native_model_seaice_grid_id)throw Error("Source grid cannot change across historical/future");
 const raw=+future.seasonal_mean;
 const corrected=Math.max(0,Math.min(100,site.observed_1995_2014_AugNov_SIC_pct+(+future.change)));
 const record={
  model,scenario,period,site_id:site.site_id,region:site.region,
  latest_recorded_count:site.latest_recorded_count,
  observed_1995_2014_SIC_pct:site.observed_1995_2014_AugNov_SIC_pct,
  historical_20yr_min_SIC_pct:site.historical_min_rolling_20yr_SIC_pct,
  source_model_historical_bias_pp:h.model_minus_observed_bias_pp,
  source_model_historical_abs_bias_pp:h.absolute_baseline_bias_pp,
  native_model_seaice_grid_id:h.native_model_seaice_grid_id,
  distance_to_model_coastal_grid_km:h.distance_to_model_coastal_grid_km,
  raw_native_model_future_seasonal_SIC_pct:raw,
  delta_corrected_future_seasonal_SIC_pct:corrected,
  model_future_change_pp:+future.change,
  model_raw_minus_delta_corrected_SIC_pp:raw-corrected,
  historical_max_20yr_mean_drop_for_10yr_window_shift_pp:site.historical_max_same_20yr_window_drop_10yr_shift_pp,
  raw_model_vs_observed_lower_envelope_pp:site.historical_min_rolling_20yr_SIC_pct-raw,
  delta_corrected_vs_observed_lower_envelope_pp:site.historical_min_rolling_20yr_SIC_pct-corrected,
  historical_model_bias_audit_not_demographic_estimate:true
 };
 for(const margin of [0,2,5]){
  record["raw_model_lower_history_by_"+margin+"pp"]=raw<site.historical_min_rolling_20yr_SIC_pct-margin?1:0;
  record["delta_corrected_lower_history_by_"+margin+"pp"]=corrected<site.historical_min_rolling_20yr_SIC_pct-margin?1:0;
  record["model_change_exceeds_matching_20yr_window_shift_by_"+margin+"pp"]=
   (site.observed_1995_2014_AugNov_SIC_pct-corrected)>site.historical_max_same_20yr_window_drop_10yr_shift_pp+margin?1:0;
 }
 futures.push(record);
}
const weightedPct=a=>100*sum(a.map(x=>x.latest_recorded_count))/N;
const modelScenario=[];
for(const scenario of scenarios)for(const period of periods)for(const model of models){
 const a=futures.filter(x=>x.model===model&&x.scenario===scenario&&x.period===period);
 if(a.length!==39)throw Error("Full model scenario missing");
 const item={scenario,period,model,source_site_codes:a.length,
   distinct_native_model_coastal_cells:uniq(a,x=>x.native_model_seaice_grid_id)};
 for(const margin of [0,2,5]){
  const raw=a.filter(x=>x["raw_model_lower_history_by_"+margin+"pp"]),
  corrected=a.filter(x=>x["delta_corrected_lower_history_by_"+margin+"pp"]);
  item["raw_not_observation_aligned_n_at_margin_"+margin]=raw.length;
  item["raw_not_observation_aligned_weight_pct_at_margin_"+margin]=weightedPct(raw);
  item["delta_corrected_n_at_margin_"+margin]=corrected.length;
  item["delta_corrected_weight_pct_at_margin_"+margin]=weightedPct(corrected);
  item["discordant_classification_site_n_at_margin_"+margin]=a.filter(x=>
   x["raw_model_lower_history_by_"+margin+"pp"]!==x["delta_corrected_lower_history_by_"+margin+"pp"]).length;
 }
 modelScenario.push(item);
}
const supportSets=[
 {distance:25,bias:100},{distance:50,bias:100},{distance:50,bias:15},
 {distance:50,bias:10},{distance:100,bias:100}
];
const consensus=[],modelSkillSiteSupport=[];
for(const scenario of scenarios)for(const period of periods){
 const modelRecords=models.map(model=>futures.filter(x=>x.scenario===scenario&&x.period===period&&x.model===model));
 for(const margin of [0,2,5]){
  const all=sites.filter(s=>modelRecords.every(a=>a.find(x=>x.site_id===s.site_id)["delta_corrected_lower_history_by_"+margin+"pp"]));
  const raw=sites.filter(s=>modelRecords.every(a=>a.find(x=>x.site_id===s.site_id)["raw_model_lower_history_by_"+margin+"pp"]));
  const sameWindow=sites.filter(s=>modelRecords.every(a=>a.find(x=>x.site_id===s.site_id)["model_change_exceeds_matching_20yr_window_shift_by_"+margin+"pp"]));
  consensus.push({
   scenario,period,extra_history_margin_pp:margin,
   three_model_raw_unaligned_original_site_n:raw.length,
   three_model_raw_unaligned_weight_pct:weightedPct(raw),
   three_model_delta_corrected_original_site_n:all.length,
   three_model_delta_corrected_weight_pct:weightedPct(all),
   three_model_20yr_same_length_sliding_window_excess_site_n:sameWindow.length,
   three_model_20yr_same_length_sliding_window_excess_weight_pct:weightedPct(sameWindow),
   two_Crozier_source_code_contribution_to_delta_consensus_pct:weightedPct(all.filter(x=>["CRZE","CRZW"].includes(x.site_id))),
   full_source_site_n:sites.length,full_source_latest_census_count_total:N,
   caveat:"20yr historical means shift 10 years and overlap, future 20yr shift is many decades; raw native future and observed past have model-climatology bias, so raw vs delta is NOT a valid model accuracy contest."
  });
  for(const s of supportSets){
   const supported=sites.filter(site=>models.every(model=>{
    const h=histByKey.get(model+"|"+site.site_id);
    return h.distance_to_model_coastal_grid_km<=s.distance&&h.absolute_baseline_bias_pp<=s.bias;
   }));
   const inside=supported.filter(x=>all.some(y=>x.site_id===y.site_id)),supportTotal=sum(supported.map(x=>x.latest_recorded_count));
   modelSkillSiteSupport.push({
    scenario,period,extra_history_margin_pp:margin,
    all_three_models_max_grid_distance_km:s.distance,
    all_three_models_max_abs_baseline_bias_pp:s.bias,
    supported_original_site_n:supported.length,
    supported_latest_census_count_pct_of_all39:weightedPct(supported),
    three_model_delta_consensus_supported_site_n:inside.length,
    delta_consensus_weight_pct_of_all39:weightedPct(inside),
    delta_consensus_weight_pct_within_supported_sites:supportTotal?100*sum(inside.map(x=>x.latest_recorded_count))/supportTotal:null,
    unsupported_source_sites_n:sites.length-supported.length,
    number_distinct_supported_site_grid_triplets:uniq(supported,site=>models.map(model=>histByKey.get(model+"|"+site.site_id).native_model_seaice_grid_id).join("||")),
    interpretation:"Subset support gate diagnostic, not model skill weighting, statistical confidence, or future nest forecast"
   });
  }
 }
}
const cmpMain=consensus.find(x=>x.scenario==="ssp585"&&x.period==="2081-2100"&&x.extra_history_margin_pp===5),
crozierDetail=futures.filter(x=>x.scenario==="ssp585"&&x.period==="2081-2100"&&["CRZE","CRZW"].includes(x.site_id));
const historicalShift=sites.map(x=>x.historical_max_same_20yr_window_drop_10yr_shift_pp).sort((a,b)=>a-b);
const facts={
 source_site_n:sites.length,model_historical_site_rows:historicalRows.length,
 model_future_site_rows:futures.length,model_scenario_rows:modelScenario.length,
 latest_recorded_original_count_total:N,
 same_length_historical_20yr_window_10yr_shift_median_max_down_pp:historicalShift[19],
 historical_20yr_mean_shift_Crozier_East_pp:siteByID.get("CRZE").historical_max_same_20yr_window_drop_10yr_shift_pp,
 SSP585_late_5pp_three_model_delta_weight_pct:cmpMain.three_model_delta_corrected_weight_pct,
 SSP585_late_5pp_three_model_raw_weight_pct:cmpMain.three_model_raw_unaligned_weight_pct,
 SSP585_late_5pp_three_model_matched_window_weight_pct:cmpMain.three_model_20yr_same_length_sliding_window_excess_weight_pct,
 ACCESS_original_39_site_MAE_pp:historicalSkill.find(x=>x.model==="ACCESS-CM2"&&x.region==="ALL").mean_absolute_model_baseline_error_pp,
 BCC_original_39_site_MAE_pp:historicalSkill.find(x=>x.model==="BCC-CSM2-MR"&&x.region==="ALL").mean_absolute_model_baseline_error_pp,
 CESM2_original_39_site_MAE_pp:historicalSkill.find(x=>x.model==="CESM2"&&x.region==="ALL").mean_absolute_model_baseline_error_pp,
 Crozier_East_ACCESS_historical_model_bias_pp:crozierDetail.find(x=>x.site_id==="CRZE"&&x.model==="ACCESS-CM2").source_model_historical_bias_pp,
 support_50km_and_15pp_n:modelSkillSiteSupport.find(x=>x.scenario==="ssp585"&&x.period==="2081-2100"&&x.extra_history_margin_pp===5&&x.all_three_models_max_grid_distance_km===50&&x.all_three_models_max_abs_baseline_bias_pp===15).supported_original_site_n,
 support_50km_and_15pp_5pp_weight_pct_of_all39:modelSkillSiteSupport.find(x=>x.scenario==="ssp585"&&x.period==="2081-2100"&&x.extra_history_margin_pp===5&&x.all_three_models_max_grid_distance_km===50&&x.all_three_models_max_abs_baseline_bias_pp===15).delta_consensus_weight_pct_of_all39
};
if(process.argv.includes("--check-receipt")){
 for(const [k,v] of Object.entries(receipt.values))close(facts[k],v,k);
 for(const row of futures){
  if(!Number.isFinite(row.delta_corrected_future_seasonal_SIC_pct)||
      row.delta_corrected_future_seasonal_SIC_pct<0||row.delta_corrected_future_seasonal_SIC_pct>100)
   throw Error("Future SIC outside 0–100 percent");
 }
 if(uniq(futures,x=>[x.model,x.scenario,x.period,x.site_id].join("|"))!==futures.length)
  throw Error("Ununique original site×model×scenario key");
}
mkdirSync(out,{recursive:true});
writeFileSync(join(out,"original_model_historical_site_bias.csv"),csv(historicalRows));
writeFileSync(join(out,"historical_model_bias_by_region.csv"),csv(historicalSkill));
writeFileSync(join(out,"future_raw_vs_delta_corrected_site_diagnostic.csv"),csv(futures));
writeFileSync(join(out,"model_scenario_raw_delta_comparison.csv"),csv(modelScenario));
writeFileSync(join(out,"three_model_original_site_consensus_comparison.csv"),csv(consensus));
writeFileSync(join(out,"three_model_grid_distance_and_bias_support.csv"),csv(modelSkillSiteSupport));
writeFileSync(join(out,"matched_20yr_historical_window_change_sites.csv"),csv(sites));
const summary={
 status:"source_pinned_historical_Cmip6_SIC_skill_and_delta_correction_dependence_not_a_biological_forecast",
 historical_reference:"observed 1995–2014 August–November nearshore SIC vs 1995–2014 model historical original native marine grid",
 future_reference:"observed 1995–2014 nearshore SIC + model future-minus-model-historical 1995–2014 SIC; absolute raw model is an invalid observational-comparison diagnostic",
 note:"model independent internal variability not synchronized with annual observations; coastal CMIP6 cell distance and aggregation differ from observed 0–100 km nearshore band",
 source_git_blobs:Object.fromEntries(Object.entries(sources).map(([k,[p,sha]])=>[k,sha])),
 facts,per_model_overall:historicalSkill.filter(x=>x.region==="ALL"),
 primary_SSP585_2081_2100_five_pp:cmpMain,
 crozier:crozierDetail,
 consensus,filter_support:modelSkillSiteSupport,
 climatic_change_window:"two 20-year observed windows (1991–2010 versus 2001–2020), overlapping by 10 years; not an independent historical 20-year change sample; future 20-year time separation differs"
};
writeFileSync(join(out,"result.json"),JSON.stringify(summary,null,2)+"\n");
writeFileSync(join(out,"validation.json"),JSON.stringify({source_blobs_pinned:true,receipt_passed:process.argv.includes("--check-receipt"),historical_sites:sites.length,historical_model_source_cells:historicalRows.length,scenario_site_rows:futures.length,three_model_consensus_groups:consensus.length,support_groups:modelSkillSiteSupport.length,raw_model_and_observed_comparison_not_a_valid_alternative_forecast:true},null,2)+"\n");
console.log("PENGUIN HISTORICAL CMIP6 BIAS AUDIT "+JSON.stringify({facts,per_model_overall:historicalSkill.filter(x=>x.region==="ALL"),primary_5pp:cmpMain,crozier:crozierDetail,support:modelSkillSiteSupport.filter(x=>x.scenario==="ssp585"&&x.period==="2081-2100"&&x.extra_history_margin_pp===5),confirmed:process.argv.includes("--check-receipt")}));
