// Original Antarctic breeding-site climate novelty: non-overlapping historical decade control.
// A physical exposure comparison only, NOT a threshold for demographic damage.
// Run: node research/climate-penguin/work/seaice_nonoverlap_decade_v1/build.mjs --check-receipt
import {readFileSync,writeFileSync,mkdirSync} from "node:fs";
import {resolve,join} from "node:path";
import {createHash} from "node:crypto";
const dataDir=resolve("research/climate-penguin/outputs");
const outdir=join(dataDir,"seaice_nonoverlap_decade_v1");
const files={
  hist:["historical_ice_breeding_transfer_v1/adeli_39site_historical_climate_growth.csv","db58938630e80d22ba445600ce1ad3f554c452e2"],
  sic:["climate_penguin/macro_monthly_seaice_1991_2020.csv","4fcea71c2d8b1069b6ad143f6522061ed434daf5"],
  cmip:["cmip6_projection_v1/site_model_changes.csv","b383ef1cc3b0807b0bd010ca0e825937ab83ce97"],
  counts:["comparison_audit/mapppd_unambiguous_site_seasons.csv","fc134e364cf38699fa7611d7dee5fbbbcb370c0a"]
};
const expected=JSON.parse(readFileSync(join(outdir,"expected_receipt.json"),"utf8"));
function parseCSV(s){
 const rows=[];let r=[],v="",quoted=false;
 for(let i=0;i<s.length;i++){
  const c=s[i];
  if(quoted){
   if(c==='"'&&s[i+1]==='"'){v+='"';i++}
   else if(c==='"')quoted=false;
   else v+=c;
  }else if(c==='"')quoted=true;
  else if(c===','){r.push(v);v=""}
  else if(c==='\n'){
   r.push(v.replace(/\r$/,""));if(r.length>1)rows.push(r);
   r=[];v="";
  }else v+=c;
 }
 if(r.length||v){r.push(v);rows.push(r)}
 if(quoted||rows.length<2)throw Error("Invalid CSV");
 const h=rows.shift();
 return rows.map((a,i)=>{
  if(a.length!==h.length)throw Error("CSV row width "+i);
  return Object.fromEntries(h.map((name,j)=>[name,a[j]]));
 });
}
function toCSV(rows){
 if(!rows.length)throw Error("Empty rows for CSV");
 const h=Object.keys(rows[0]);
 const e=v=>{const s=v===undefined||v===null?"":String(v);return /[,"\r\n]/.test(s)?'"'+s.replaceAll('"','""')+'"':s};
 return h.join(",")+"\n"+rows.map(row=>h.map(k=>e(row[k])).join(",")).join("\n")+"\n";
}
const mean=a=>a.reduce((s,x)=>s+x,0)/a.length;
const sum=a=>a.reduce((s,x)=>s+x,0);
const nUnique=(a,key)=>new Set(a.map(key)).size;
function close(x,y,key){
 if(!Number.isFinite(x)||Math.abs(x-y)>1e-8)throw Error("Receipt drift "+key+" observed "+x+" expected "+y);
}
const D={};
for(const [name,[path,sha]] of Object.entries(files)){
 const bytes=readFileSync(join(dataDir,path));
 const b=createHash("sha1").update(Buffer.from("blob "+bytes.length+"\0")).update(bytes).digest("hex");
 if(b!==sha||expected.source_git_blobs[name]!==b)throw Error("Original source changed "+name+": "+b);
 D[name]=parseCSV(bytes.toString("utf8"));
}
if(D.hist.length!==39||D.sic.length!==9600||D.cmip.length!==3816||D.counts.length!==2999)
 throw Error("Upstream source cohort changed");
const byHistorical=new Map(D.hist.map(x=>[x.site_id,x]));
if(byHistorical.size!==39)throw Error("Duplicate selected site");
const monthly=new Map();
for(const row of D.sic){
 if(!byHistorical.has(row.site_id)||row.inner_km!=="0"||![8,9,10,11].includes(+row.month))continue;
 if(row.complete_month!=="True")throw Error("Partial SIC month "+row.site_id);
 const key=row.site_id+"|"+row.year,a=monthly.get(key)||[];
 a.push(+row.sic_mean);monthly.set(key,a);
}
const countBySite=new Map();
for(const row of D.counts){
 if(!byHistorical.has(row.site_id)||row.species_id!=="ADPE"||row.count===""||!Number.isFinite(+row.count)||+row.count<0)continue;
 const a=countBySite.get(row.site_id)||[];a.push(row);countBySite.set(row.site_id,a);
}
const sites=[],decadalTransitions=[];
for(const hist of D.hist){
 const annual=[];
 for(let year=1991;year<=2020;year++){
  const vals=monthly.get(hist.site_id+"|"+year);
  if(!vals||vals.length!==4||!vals.every(Number.isFinite))throw Error("SIC source not complete "+hist.site_id+"/"+year);
  annual.push(mean(vals));
 }
 const original30=mean(annual);
 close(original30,+hist.historical_nearshore_AugNov_SIC_mean_pct,"original30 "+hist.site_id);
 const decade=[mean(annual.slice(0,10)),mean(annual.slice(10,20)),mean(annual.slice(20,30))];
 const declines=[decade[0]-decade[1],decade[1]-decade[2]];
 const largestDrop=Math.max(0,...declines);
 const countRows=(countBySite.get(hist.site_id)||[]).sort((a,b)=>+b.season-+a.season);
 if(!countRows.length)throw Error("Missing source counts "+hist.site_id);
 const site={
  site_id:hist.site_id,region:hist.region,
  observed_annual_1991_2020_n:annual.length,
  SIC_1991_2000_10yr_pct:decade[0],SIC_2001_2010_10yr_pct:decade[1],SIC_2011_2020_10yr_pct:decade[2],
  consecutive_decadal_drop_1991to2001_pp:declines[0],
  consecutive_decadal_drop_2001to2011_pp:declines[1],
  largest_historical_10yr_to_10yr_drop_pp:largestDrop,
  historical_three_independent_decades_min_pct:Math.min(...decade),
  historical_three_independent_decades_range_pp:Math.max(...decade)-Math.min(...decade),
  observed_SIC_1995_2014_pct:mean(annual.slice(4,24)),
  observed_SIC_1991_2020_pct:original30,
  observed_historical_growth_decade:+hist.count_growth_log1p_slope_per_decade,
  latest_recorded_ADPE_count:+countRows[0].count,
  latest_count_year:+countRows[0].season,latest_count_method:countRows[0].method,
  historical_growth_method:hist.method
 };
 sites.push(site);
 for(let k=0;k<2;k++){
  decadalTransitions.push({
   site_id:hist.site_id,region:hist.region,transition:k===0?"1991–2000 to 2001–2010":"2001–2010 to 2011–2020",
   actual_observed_drop_pp:declines[k],
   observed_drop_of_at_least_2pp:declines[k]>2,
   observed_drop_of_at_least_5pp:declines[k]>5,
   original_current_count_weight:site.latest_recorded_ADPE_count
  });
 }
}
const nSites=sites.length,N=sum(sites.map(x=>x.latest_recorded_ADPE_count)),crozier=sites.filter(x=>["CRZE","CRZW"].includes(x.site_id));
if(nSites!==39||N!==1074279||sum(crozier.map(x=>x.latest_recorded_ADPE_count))!==242681)
 throw Error("Source snapshot census changed");
const orderedDrop=sites.map(x=>x.largest_historical_10yr_to_10yr_drop_pp).sort((a,b)=>a-b);
const orderedRange=sites.map(x=>x.historical_three_independent_decades_range_pp).sort((a,b)=>a-b);
const modelRows=new Map();
for(const x of D.cmip){
 if(x.variable_id!=="siconc"||x.cohort!=="macro_40")continue;
 const k=[x.source_id,x.experiment_id,x.period].join("|"),a=modelRows.get(k)||new Map();
 if(a.has(x.site_id))throw Error("Duplicate model site key");
 a.set(x.site_id,{change:+x.change,model_grid_id:x.grid_cell_id,model_grid_distance_km:+x.distance_km});
 modelRows.set(k,a);
}
const models=["ACCESS-CM2","BCC-CSM2-MR","CESM2"],scenarios=["ssp245","ssp585"],periods=["2041-2060","2081-2100"],baselines=["1995-2014","1991-2020"],margins=[0,2,5];
const future=[],summary=[],consensus=[];
const countPercent=a=>100*sum(a.map(x=>x.latest_recorded_ADPE_count))/N;
for(const baseline of baselines)for(const scenario of scenarios)for(const period of periods){
 const across=[];
 for(const model of models){
  const grid=modelRows.get([model,scenario,period].join("|"));
  if(!grid||grid.size!==40)throw Error("Model grid support changed "+model+scenario+period);
  const rows=sites.map(x=>{
   const z=grid.get(x.site_id);
   if(!z||!Number.isFinite(z.change))throw Error("Model missing source site");
   const current=baseline==="1995-2014"?x.observed_SIC_1995_2014_pct:x.observed_SIC_1991_2020_pct;
   const projected=Math.max(0,Math.min(100,current+z.change));
   return {...x,model,scenario,period,observed_baseline:baseline,
    original_observed_SIC_pct:current,conditional_future_20yr_SIC_pct:projected,
    physical_SIC_decline_pp:current-projected,
    excess_decline_vs_max_observed_decadal_drop_pp:current-projected-x.largest_historical_10yr_to_10yr_drop_pp,
    below_all_three_original_nonoverlap_decades_pp:x.historical_three_independent_decades_min_pct-projected,
    model_grid_id:z.model_grid_id,model_grid_distance_km:z.model_grid_distance_km,
    source_unit:"SIC anomaly scenario only, not a demographic decline"
   };
  });
  future.push(...rows);
  across.push({model,rows});
  for(const margin of margins){
   const stronger=rows.filter(x=>x.excess_decline_vs_max_observed_decadal_drop_pp>margin);
   const novel=rows.filter(x=>x.below_all_three_original_nonoverlap_decades_pp>margin);
   const cap=stronger.filter(x=>["CRZE","CRZW"].includes(x.site_id));
   summary.push({observed_baseline:baseline,scenario,period,model,comparison_margin_pp:margin,
    projected_drop_exceeds_largest_historical_decadal_drop_site_n:stronger.length,
    projected_drop_exceeds_largest_historical_decadal_drop_count_weight_pct:countPercent(stronger),
    projected_drop_exceeds_largest_historical_decadal_drop_unique_CMIP_cells:nUnique(stronger,x=>x.model_grid_id),
    future_mean_below_all_3_historical_nonoverlap_decades_site_n:novel.length,
    future_mean_below_all_3_historical_nonoverlap_decades_count_weight_pct:countPercent(novel),
    crozier_contribution_to_excess_drop_count_weight_pp:countPercent(cap),
    without_crozier_reweighted_37site_pct:100*(sum(stronger.map(x=>x.latest_recorded_ADPE_count))-sum(cap.map(x=>x.latest_recorded_ADPE_count)))/(N-242681),
    comparison_note:"physical projected 20-year mean change compared with observed nonoverlapping 10-year means; not a hazard test"
   });
  }
 }
 for(const margin of margins){
  const every=sites.filter(x=>across.every(y=>y.rows.find(q=>q.site_id===x.site_id).excess_decline_vs_max_observed_decadal_drop_pp>margin));
  const everyMin=sites.filter(x=>across.every(y=>y.rows.find(q=>q.site_id===x.site_id).below_all_three_original_nonoverlap_decades_pp>margin));
  const cap=every.filter(x=>["CRZE","CRZW"].includes(x.site_id));
  consensus.push({observed_baseline:baseline,scenario,period,comparison_margin_pp:margin,
   common_three_model_exceeds_largest_historical_decadal_drop_site_n:every.length,
   common_three_model_exceeds_largest_historical_decadal_drop_count_weight_pct:countPercent(every),
   common_three_model_below_historical_three_decades_min_site_n:everyMin.length,
   common_three_model_below_historical_three_decades_min_count_weight_pct:countPercent(everyMin),
   common_Crozier_current_count_weight_pp:countPercent(cap),
   common_nonCrozier_source_count:sum(every.filter(x=>!["CRZE","CRZW"].includes(x.site_id)).map(x=>x.latest_recorded_ADPE_count)),
   common_excluding_Crozier_reweighted_37site_pct:100*sum(every.filter(x=>!["CRZE","CRZW"].includes(x.site_id)).map(x=>x.latest_recorded_ADPE_count))/(N-242681),
   all_models_share_one_member_each:true
  });
 }
}
if(future.length!==936||summary.length!==72||consensus.length!==24||decadalTransitions.length!==78)
 throw Error("Source cohort or scenario Cartesian product incomplete");
const fact={
 historic_sites_n:nSites,original_historical_siteyears:39*30,original_nonoverlapping_decadal_blocks_per_site:3,
 original_latest_ADPE_count_total:N,
 median_3_decades_full_range_pp:orderedRange[19],
 median_max_historical_consecutive_decade_drop_pp:orderedDrop[19],
 crozier_east_max_historical_decadal_drop_pp:sites.find(x=>x.site_id==="CRZE").largest_historical_10yr_to_10yr_drop_pp,
 crozier_west_max_historical_decadal_drop_pp:sites.find(x=>x.site_id==="CRZW").largest_historical_10yr_to_10yr_drop_pp,
 ssp585_late_0pp_model_common:consensus.find(x=>x.observed_baseline==="1995-2014"&&x.scenario==="ssp585"&&x.period==="2081-2100"&&x.comparison_margin_pp===0).common_three_model_exceeds_largest_historical_decadal_drop_count_weight_pct,
 ssp585_late_2pp_model_common:consensus.find(x=>x.observed_baseline==="1995-2014"&&x.scenario==="ssp585"&&x.period==="2081-2100"&&x.comparison_margin_pp===2).common_three_model_exceeds_largest_historical_decadal_drop_count_weight_pct,
 ssp585_late_5pp_model_common:consensus.find(x=>x.observed_baseline==="1995-2014"&&x.scenario==="ssp585"&&x.period==="2081-2100"&&x.comparison_margin_pp===5).common_three_model_exceeds_largest_historical_decadal_drop_count_weight_pct,
 ssp585_late_5pp_common_non_crozier_count:consensus.find(x=>x.observed_baseline==="1995-2014"&&x.scenario==="ssp585"&&x.period==="2081-2100"&&x.comparison_margin_pp===5).common_nonCrozier_source_count
};
if(process.argv.includes("--check-receipt")){
 for(const [key,val] of Object.entries(expected.values))close(fact[key],val,key);
 for(const x of future){
  if(x.physical_SIC_decline_pp<-100||x.physical_SIC_decline_pp>100)throw Error("Physical change impossible");
 }
 for(const grp of [summary,consensus]){
  const keys=["observed_baseline","scenario","period","comparison_margin_pp"];
  if(grp.length===72)keys.push("model");
  if(nUnique(grp,x=>keys.map(k=>x[k]).join("|"))!==grp.length)throw Error("Duplicate scenario summary");
 }
}
mkdirSync(outdir,{recursive:true});
writeFileSync(join(outdir,"site_nonoverlap_historical_3_decades.csv"),toCSV(sites));
writeFileSync(join(outdir,"original_site_decadal_change_events.csv"),toCSV(decadalTransitions));
writeFileSync(join(outdir,"future_nonoverlap_decadal_comparison.csv"),toCSV(future));
writeFileSync(join(outdir,"model_level_decadal_change_envelopes.csv"),toCSV(summary));
writeFileSync(join(outdir,"three_model_common_decadal_exceedance.csv"),toCSV(consensus));
const result={
 status:"verified_physical_SIC_change_exceeds_recorded_nonoverlapping_decadal_changes_not_demographic_forecast",
 source_git_blobs:Object.fromEntries(Object.entries(files).map(([k,[p,sha]])=>[k,sha])),
 reference:"three disjoint 10-year observed averages: 1991-2000, 2001-2010, 2011-2020",
 scenario:"three single-member CMIP6 model anomalies added to matched 1995-2014 observed SIC, future 20-year climatology",
 distinction:"Future mean of 20 years versus historical decade-to-decade *changes of 10-year means*; window durations differ. This is scale/context sensitivity, never a statistical test, hazard or future penguin demographics.",
 margins_pp:margins,
 observations:{
   site_codes:nSites,latest_counts_total:N,crozier_2_codes_count:242681,
   median_nonoverlap_decadal_envelope_width_pp:fact.median_3_decades_full_range_pp,
   median_largest_historical_decadal_decline_pp:fact.median_max_historical_consecutive_decade_drop_pp
 },
 fact,three_model_consensus:consensus,model_specific:summary
};
writeFileSync(join(outdir,"result.json"),JSON.stringify(result,null,2)+"\n");
writeFileSync(join(outdir,"validation.json"),JSON.stringify({
 source_SHA_pinned:true,independent_receipt_pass:process.argv.includes("--check-receipt"),
 n_historical_siteyear_observations:39*30,n_nonoverlap_decade_means:39*3,
 n_original_decade_transition_events:decadalTransitions.length,
 n_future_site_model_records:future.length,n_scenario_margin_model_rows:summary.length,n_three_model_intersections:consensus.length,
 biological_damage_threshold_assumed:false,predicts_future_nest_abundance:false
},null,2)+"\n");
console.log("NONOVERLAP DECADE CLIMATE BENCHMARK "+JSON.stringify({
 fact,
 common_main:consensus.filter(x=>x.observed_baseline==="1995-2014"),
 ssp585_late_crozier:future.filter(x=>x.observed_baseline==="1995-2014"&&x.scenario==="ssp585"&&x.period==="2081-2100"&&["CRZE","CRZW"].includes(x.site_id))
  .map(x=>({model:x.model,site:x.site_id,priorDecadalMaxDrop:x.largest_historical_10yr_to_10yr_drop_pp,futureDecline:x.physical_SIC_decline_pp,conditionalFuture:x.conditional_future_20yr_SIC_pct})),
 verified:process.argv.includes("--check-receipt")
}));
