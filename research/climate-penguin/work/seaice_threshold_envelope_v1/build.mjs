// Reproducible sensitivity envelope: conditional future SIC *exposure*, NOT penguin demography.
// Usage: node research/climate-penguin/work/seaice_threshold_envelope_v1/build.mjs --check-receipt
// Native Node>=20, source blob pinned, exactly 39 historical Adélie sites / 3 CMIP6 models.
import {readFileSync,mkdirSync,writeFileSync} from "node:fs";
import {join,resolve} from "node:path";
import {createHash} from "node:crypto";

const root=resolve("research/climate-penguin/outputs");
const outdir=join(root,"seaice_threshold_envelope_v1");
const sources={
  history:["historical_ice_breeding_transfer_v1/adeli_39site_historical_climate_growth.csv","db58938630e80d22ba445600ce1ad3f554c452e2"],
  marine:["climate_penguin/macro_monthly_seaice_1991_2020.csv","4fcea71c2d8b1069b6ad143f6522061ed434daf5"],
  cmip:["cmip6_projection_v1/site_model_changes.csv","b383ef1cc3b0807b0bd010ca0e825937ab83ce97"],
  bio:["comparison_audit/mapppd_unambiguous_site_seasons.csv","fc134e364cf38699fa7611d7dee5fbbbcb370c0a"]
};
const receipt=JSON.parse(readFileSync(join(outdir,"expected_receipt.json"),"utf8"));
function parseCSV(s){
 const r=[];let cols=[],v="",q=false;
 for(let i=0;i<s.length;i++){
  const c=s[i];
  if(q){if(c==='"'&&s[i+1]==='"'){v+='"';i++}else if(c==='"')q=false;else v+=c}
  else if(c==='"')q=true;
  else if(c===','){cols.push(v);v=""}
  else if(c==='\n'){
   cols.push(v.replace(/\r$/,""));if(cols.length>1)r.push(cols);cols=[];v=""
  }else v+=c;
 }
 if(cols.length||v){cols.push(v);r.push(cols)}
 if(q||!r.length)throw Error("Invalid CSV");
 const h=r.shift();
 return r.map((row,i)=>{if(row.length!==h.length)throw Error("Malformed CSV row "+i);return Object.fromEntries(h.map((x,j)=>[x,row[j]]))});
}
function csv(rows){
 if(!rows.length)throw Error("empty CSV");
 const head=Object.keys(rows[0]),q=x=>{let s=x===null||x===undefined?"":String(x);return /[,"\n\r]/.test(s)?'"'+s.replaceAll('"','""')+'"':s};
 return head.join(",")+"\n"+rows.map(x=>head.map(k=>q(x[k])).join(",")).join("\n")+"\n";
}
const d={};
for(const [k,[path,expected]] of Object.entries(sources)){
 const bytes=readFileSync(join(root,path));
 const actual=createHash("sha1").update(Buffer.from("blob "+bytes.length+"\0")).update(bytes).digest("hex");
 if(actual!==expected||receipt.blobs[k]!==expected)throw Error("Source changed "+k+" "+actual);
 d[k]=parseCSV(bytes.toString("utf8"));
}
const historical=d.history;
if(historical.length!==39||d.marine.length!==9600||d.cmip.length!==3816||d.bio.length!==2999)
 throw Error("Source cohort has drifted");
const avg=x=>x.reduce((s,v)=>s+v,0)/x.length;
const total=x=>x.reduce((s,v)=>s+v,0);
const countsBySite=new Map();
for(const row of d.bio){
 if(row.species_id!=="ADPE"||row.count===""||!Number.isFinite(+row.count)||+row.count<0)continue;
 const arr=countsBySite.get(row.site_id)||[];arr.push(row);countsBySite.set(row.site_id,arr);
}
const obsIce=new Map();
for(const x of d.marine){
 if(x.inner_km!=="0"||![8,9,10,11].includes(+x.month))continue;
 if(x.complete_month!=="True")throw Error("incomplete observed month "+x.site_id);
 const key=x.site_id+"|"+x.year,arr=obsIce.get(key)||[];
 arr.push(+x.sic_mean);obsIce.set(key,arr);
}
const sites=historical.map(x=>{
 let annual=[],aligned=[];
 for(let year=1991;year<=2020;year++){
  const val=obsIce.get(x.site_id+"|"+year);
  if(!val||val.length!==4||!val.every(Number.isFinite))throw Error("Monthly ice incomplete "+x.site_id+"/"+year);
  const m=avg(val);annual.push(m);
  if(year>=1995&&year<=2014)aligned.push(m);
 }
 const obs30=avg(annual),obs20=avg(aligned);
 if(Math.abs(obs30- +x.historical_nearshore_AugNov_SIC_mean_pct)>1e-8)
  throw Error("Historical source SIC not reproduced "+x.site_id);
 const list=(countsBySite.get(x.site_id)||[]).sort((a,b)=>+b.season-+a.season);
 if(!list.length)throw Error("No observed latest count for "+x.site_id);
 return {
  site_id:x.site_id,region:x.region,observed_growth_slope_decade:+x.count_growth_log1p_slope_per_decade,
  observed_SIC_1991_2020_pct:obs30,observed_SIC_1995_2014_pct:obs20,
  latest_recorded_count:+list[0].count,latest_count_year:+list[0].season,
  latest_count_method:list[0].method,historical_trend_method:x.method
 };
});
const allids=new Set(sites.map(x=>x.site_id));
if(allids.size!==39)throw Error("duplicate historical site");
const denominator=total(sites.map(x=>x.latest_recorded_count));
if(denominator!==1074279)throw Error("Latest count denominator changed "+denominator);
const crozier=sites.filter(x=>["CRZE","CRZW"].includes(x.site_id));
if(crozier.length!==2||total(crozier.map(x=>x.latest_recorded_count))!==242681)
 throw Error("Cape Crozier original census count changed");
const models=["ACCESS-CM2","BCC-CSM2-MR","CESM2"];
const exps=["ssp245","ssp585"],periods=["2041-2060","2081-2100"];
const changes=new Map();
for(const x of d.cmip.filter(x=>x.cohort==="macro_40"&&x.variable_id==="siconc")){
 const k=[x.source_id,x.experiment_id,x.period].join("|"),q=changes.get(k)||new Map();
 if(q.has(x.site_id))throw Error("Double original model exposure "+x.site_id);
 q.set(x.site_id,{delta:+x.change,grid:x.grid_cell_id,dist:+x.distance_km});
 changes.set(k,q);
}
const thresholdGrid=Array.from({length:201},(_,i)=>Math.round((60+i*.1)*10)/10);
const sourceRows=[],siteForecasts=[],sweep=[];
function pctCount(rows){return total(rows.map(x=>x.latest_recorded_count))/denominator*100}
function one(model,scenario,period,baseline){
 const projected=changes.get([model,scenario,period].join("|"));
 if(!projected||projected.size!==40)throw Error("CMIP cohort incomplete "+model+scenario+period);
 const m=sites.map(s=>{
  const pred=projected.get(s.site_id);
  if(!pred||!Number.isFinite(pred.delta))throw Error("Missing future "+s.site_id);
  const current=baseline==="1995-2014"?s.observed_SIC_1995_2014_pct:s.observed_SIC_1991_2020_pct;
  const future=Math.max(0,Math.min(100,current+pred.delta));
  return {...s,observed_reference_SIC_pct:current,model_SIC_delta_pp:pred.delta,
   conditional_future_SIC_pct:future,CMIP_grid_cell_id:pred.grid,grid_distance_km:pred.dist,
   model,scenario,period,observed_baseline:baseline};
 });
 if(m.length!==39)throw Error("Missing source matched sites");
 siteForecasts.push(...m);
 for(const threshold of thresholdGrid){
  const below_now=m.filter(x=>x.observed_reference_SIC_pct<threshold);
  const below_future=m.filter(x=>x.conditional_future_SIC_pct<threshold);
  const crossed=m.filter(x=>x.observed_reference_SIC_pct>=threshold&&x.conditional_future_SIC_pct<threshold);
  const crossed_positive=crossed.filter(x=>x.observed_growth_slope_decade>0);
  sweep.push({observed_baseline:baseline,scenario,period,model,threshold_SIC_pct:threshold,
   new_crossing_site_n:crossed.length,
   new_crossing_site_pct:crossed.length/39*100,
   new_crossing_recorded_count_pct:pctCount(crossed),
   new_crossing_historical_growth_positive_recorded_count_pct:pctCount(crossed_positive),
   future_below_site_n:below_future.length,
   future_below_recorded_count_pct:pctCount(below_future),
   observed_below_site_n:below_now.length,
   observed_below_recorded_count_pct:pctCount(below_now),
   observed_vs_future_total_below_change_pp:pctCount(below_future)-pctCount(below_now)});
 }
}
for(const baseline of ["1995-2014","1991-2020"])
for(const scenario of exps)for(const period of periods)for(const model of models)one(model,scenario,period,baseline);
if(sweep.length!==2*2*2*3*201||siteForecasts.length!==2*2*2*3*39)throw Error("Scenario cross-product changed");
const results=[];
const atThreshold=[];
const summaryByScenario=[];
const nearly=[60,65,70,75,77.5,79,80];
for(const baseline of ["1995-2014","1991-2020"])
for(const scenario of exps)for(const period of periods){
 const ss=sweep.filter(x=>x.observed_baseline===baseline&&x.scenario===scenario&&x.period===period);
 const mn=x=>Math.min(...x),mx=x=>Math.max(...x);
 const envelope={
  observed_baseline:baseline,scenario,period,
  threshold_band_min_pct:60,threshold_band_max_pct:80,
  new_crossing_count_pct_min:mn(ss.map(x=>x.new_crossing_recorded_count_pct)),
  new_crossing_count_pct_max:mx(ss.map(x=>x.new_crossing_recorded_count_pct)),
  total_future_below_pct_min:mn(ss.map(x=>x.future_below_recorded_count_pct)),
  total_future_below_pct_max:mx(ss.map(x=>x.future_below_recorded_count_pct)),
  new_crossing_sites_min:mn(ss.map(x=>x.new_crossing_site_n)),
  new_crossing_sites_max:mx(ss.map(x=>x.new_crossing_site_n)),
  threshold_points_n:thresholdGrid.length,climate_models_n:models.length
 };
 for(const lohi of [[70,80],[75,79]]){
  const part=ss.filter(x=>x.threshold_SIC_pct>=lohi[0]&&x.threshold_SIC_pct<=lohi[1]);
  envelope["subband_"+lohi.join("_")+"_new_crossing_min_pct"]=mn(part.map(x=>x.new_crossing_recorded_count_pct));
  envelope["subband_"+lohi.join("_")+"_new_crossing_max_pct"]=mx(part.map(x=>x.new_crossing_recorded_count_pct));
 }
 summaryByScenario.push(envelope);
 for(const tau of nearly){
  const rows=ss.filter(x=>x.threshold_SIC_pct===tau);
  if(rows.length!==3)throw Error("Threshold omitted "+tau);
  atThreshold.push({
   observed_baseline:baseline,scenario,period,threshold_SIC_pct:tau,
   min_model_new_crossing_count_pct:mn(rows.map(x=>x.new_crossing_recorded_count_pct)),
   max_model_new_crossing_count_pct:mx(rows.map(x=>x.new_crossing_recorded_count_pct)),
   min_model_future_below_pct:mn(rows.map(x=>x.future_below_recorded_count_pct)),
   max_model_future_below_pct:mx(rows.map(x=>x.future_below_recorded_count_pct)),
   min_model_crossing_n:mn(rows.map(x=>x.new_crossing_site_n)),
   max_model_crossing_n:mx(rows.map(x=>x.new_crossing_site_n)),
  });
 }
}
const robustSiteBands=[];
for(const scenario of exps)for(const period of periods)
for(const baseline of ["1995-2014","1991-2020"]){
 const rows=siteForecasts.filter(x=>x.scenario===scenario&&x.period===period&&x.observed_baseline===baseline);
 for(const site of sites){
  const all=rows.filter(x=>x.site_id===site.site_id);
  if(all.length!==3)throw Error("Site climate models not exactly three "+site.site_id);
  const observed=all[0].observed_reference_SIC_pct,
        maxFuture=Math.max(...all.map(x=>x.conditional_future_SIC_pct)),
        minFuture=Math.min(...all.map(x=>x.conditional_future_SIC_pct));
  const common=thresholdGrid.filter(t=>t<=observed&&t>maxFuture);
  robustSiteBands.push({
   observed_baseline:baseline,scenario,period,site_id:site.site_id,region:site.region,
   latest_recorded_count:site.latest_recorded_count,observed_SIC_pct:observed,
   min_model_future_SIC_pct:minFuture,max_model_future_SIC_pct:maxFuture,
   common_crossing_threshold_min_pct:common.length?Math.min(...common):"",
   common_crossing_threshold_max_pct:common.length?Math.max(...common):"",
   number_candidate_thresholds_all_three_cross:common.length
  });
 }
}
const receiptValues={
 original_sites:sites.length,latest_count_total:denominator,
 crozier_count:total(crozier.map(x=>x.latest_recorded_count)),
 site_year_start:Math.min(...sites.map(x=>x.latest_count_year)),
 site_year_end:Math.max(...sites.map(x=>x.latest_count_year)),
 main_late_775_min:atThreshold.find(x=>x.observed_baseline==="1995-2014"&&x.scenario==="ssp585"&&x.period==="2081-2100"&&x.threshold_SIC_pct===77.5).min_model_new_crossing_count_pct,
 main_late_775_max:atThreshold.find(x=>x.observed_baseline==="1995-2014"&&x.scenario==="ssp585"&&x.period==="2081-2100"&&x.threshold_SIC_pct===77.5).max_model_new_crossing_count_pct,
 main_late_full_max:summaryByScenario.find(x=>x.observed_baseline==="1995-2014"&&x.scenario==="ssp585"&&x.period==="2081-2100").new_crossing_count_pct_max,
};
if(process.argv.includes("--check-receipt")){
 for(const [k,v] of Object.entries(receipt.values)){
  const actual=receiptValues[k];
  if(!Number.isFinite(actual)||Math.abs(actual-v)>1e-8)
    throw Error("Frozen independently calculated value differs: "+k+" "+actual+" vs "+v);
 }
 // Monotonicity applies to total future threshold exposure, not to *newly crossing* exposure.
 for(const base of ["1995-2014","1991-2020"])for(const sc of exps)for(const pe of periods)for(const model of models){
  const a=sweep.filter(x=>x.observed_baseline===base&&x.scenario===sc&&x.period===pe&&x.model===model);
  for(let i=1;i<a.length;i++)if(a[i].future_below_recorded_count_pct+1e-10<a[i-1].future_below_recorded_count_pct)
   throw Error("Total below threshold should be nondecreasing");
 }
}
mkdirSync(outdir,{recursive:true});
writeFileSync(join(outdir,"scenario_threshold_grid.csv"),csv(sweep));
writeFileSync(join(outdir,"site_scenario_physical_values.csv"),csv(siteForecasts));
writeFileSync(join(outdir,"scenario_range_summary.csv"),csv(summaryByScenario));
writeFileSync(join(outdir,"selected_thresholds.csv"),csv(atThreshold));
writeFileSync(join(outdir,"robust_all3_model_site_crossing_bands.csv"),csv(robustSiteBands));
const facts={
 status:"quantified_exposure_threshold_sensitivity_not_future_nesting_risk_or_demographic_prediction",
 research_snapshot:"2026-11-01",
 historic_adeli_sites:39,
 latest_count_weight_sum:denominator,
 latest_count_calendar_range:[receiptValues.site_year_start,receiptValues.site_year_end],
 climate_models:models,scenarios:exps,periods,
 physical_baseline_primary:"1995-2014",
 physical_baseline_sensitivity:"1991-2020",
 threshold_sensitivity_grid:{"min_pct":60,"max_pct":80,"step_pp":0.1,"n":thresholdGrid.length},
 crozier:crozier.map(x=>({site_id:x.site_id,latest_recorded_count:x.latest_recorded_count,
  observed_sic_1995_2014:x.observed_SIC_1995_2014_pct})),
 source_blobs:Object.fromEntries(Object.entries(sources).map(([k,[,sha]])=>[k,sha])),
 checks:receiptValues,
 boundary:"Threshold band is analyst-defined unsupported biological response; model min/max is not uncertainty confidence interval. Latest noncontemporaneous MAPPPD counts mix observational metrics; population and survival not estimated. 39 selected sites, regional skew and repeated climate cells; coarse marine grid. Future counts not forecast."
};
writeFileSync(join(outdir,"summary.json"),JSON.stringify({facts,scenarios:summaryByScenario,selected:atThreshold},null,2)+"\n");
writeFileSync(join(outdir,"validation.json"),JSON.stringify({source_blobs_checked:true,receipt_checked:process.argv.includes("--check-receipt"),n_source_sites:39,n_site_scenario_rows:siteForecasts.length,n_sensitivity_values:sweep.length,n_scenario_envelopes:summaryByScenario.length,n_selected_threshold_summary:atThreshold.length,n_site_robustness_rows:robustSiteBands.length,do_not_treat_as_probability:true},null,2)+"\n");
console.log("EXPOSURE THRESHOLD ENVELOPE "+JSON.stringify({receipt:receiptValues,scenarios:summaryByScenario.map(x=>({baseline:x.observed_baseline,scenario:x.scenario,period:x.period,range_crossing:[x.new_crossing_count_pct_min,x.new_crossing_count_pct_max],range_new_75_79:[x.subband_75_79_new_crossing_min_pct,x.subband_75_79_new_crossing_max_pct]})),late_775:atThreshold.filter(x=>x.scenario==="ssp585"&&x.period==="2081-2100"&&x.threshold_SIC_pct===77.5),robust_crozier:robustSiteBands.filter(x=>x.scenario==="ssp585"&&x.period==="2081-2100"&&x.observed_baseline==="1995-2014"&&["CRZW","CRZE"].includes(x.site_id)),receipt_passed:process.argv.includes("--check-receipt")}));
