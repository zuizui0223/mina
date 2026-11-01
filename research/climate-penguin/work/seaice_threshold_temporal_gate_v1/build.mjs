// Original Adélie breeding-count × yearly sea-ice boundary validation.
// Run: node research/climate-penguin/work/seaice_threshold_temporal_gate_v1/build.mjs --check-receipt
// 60–80% is an uncalibrated *hypothetical* scenario band; no biological threshold may be selected post hoc.
import {readFileSync,writeFileSync,mkdirSync} from "node:fs";
import {join,resolve} from "node:path";
import {createHash} from "node:crypto";

const root=resolve("research/climate-penguin/outputs");
const outdir=join(root,"seaice_threshold_temporal_gate_v1");
const sources={
  history:["historical_ice_breeding_transfer_v1/adeli_39site_historical_climate_growth.csv","db58938630e80d22ba445600ce1ad3f554c452e2"],
  satellite:["climate_penguin/macro_monthly_seaice_1991_2020.csv","4fcea71c2d8b1069b6ad143f6522061ed434daf5"],
  count:["comparison_audit/mapppd_unambiguous_site_seasons.csv","fc134e364cf38699fa7611d7dee5fbbbcb370c0a"],
  timing:["climate_penguin/historical_count_interval_timing.csv","f1aa63a99eff97482dde9b1c680c19b36c1dada5"]
};
const expected=JSON.parse(readFileSync(join(outdir,"expected_receipt.json"),"utf8"));
const avg=a=>a.reduce((s,x)=>s+x,0)/a.length;
const sum=a=>a.reduce((s,x)=>s+x,0);
const uniq=(a,f)=>new Set(a.map(f)).size;
function csvParse(s){
 const rows=[];let row=[],value="",quoted=false;
 for(let i=0;i<s.length;i++){
  const c=s[i];
  if(quoted){
   if(c==='"'&&s[i+1]==='"'){value+='"';i++}
   else if(c==='"')quoted=false;
   else value+=c;
  }else if(c==='"')quoted=true;
  else if(c===','){row.push(value);value=""}
  else if(c==='\n'){
   row.push(value.replace(/\r$/,""));
   if(row.length>1)rows.push(row);
   row=[];value="";
  }else value+=c;
 }
 if(row.length||value){row.push(value);rows.push(row)}
 if(quoted||!rows.length)throw Error("Malformed CSV");
 const columns=rows.shift();
 return rows.map((r,i)=>{
  if(r.length!==columns.length)throw Error("Malformed CSV width "+i);
  return Object.fromEntries(columns.map((k,j)=>[k,r[j]]));
 });
}
function csvWrite(rows){
 if(!rows.length)throw Error("Empty output CSV");
 const cols=Object.keys(rows[0]),quote=v=>{
  let s=v===undefined||v===null?"":String(v);
  return /[,"\r\n]/.test(s)?'"'+s.replaceAll('"','""')+'"':s;
 };
 return cols.join(",")+"\n"+rows.map(r=>cols.map(k=>quote(r[k])).join(",")).join("\n")+"\n";
}
const D={};
for(const [key,[path,sha]] of Object.entries(sources)){
 const content=readFileSync(join(root,path));
 const digest=createHash("sha1").update(Buffer.from("blob "+content.length+"\0")).update(content).digest("hex");
 if(digest!==sha||expected.source_git_blobs[key]!==digest)throw Error("Original source drift "+key+" "+digest);
 D[key]=csvParse(content.toString("utf8"));
}
if(D.history.length!==39||D.satellite.length!==9600||D.count.length!==2999)throw Error("Original cohorts changed");
const oldHist=new Map(D.history.map(r=>[r.site_id,r]));
if(oldHist.size!==39)throw Error("Non-unique historic site");
const regions=[...new Set(D.history.map(x=>x.region))].sort();
const historical=D.history.map(r=>({
 site_id:r.site_id,region:r.region,method:r.method,growth_decade:+r.count_growth_log1p_slope_per_decade,
 historic_nearshore_30y_SIC_pct:+r.historical_nearshore_AugNov_SIC_mean_pct,
 observed_growth_negative:+r.count_growth_log1p_slope_per_decade<0
}));
const originalSICMonth=new Map();
for(const r of D.satellite){
 if(!oldHist.has(r.site_id)||r.inner_km!=="0"||![8,9,10,11].includes(+r.month))continue;
 if(r.complete_month!=="True")throw Error("Missing or incomplete original month "+r.site_id);
 const k=r.site_id+"|"+r.year,vals=originalSICMonth.get(k)||[];
 vals.push(+r.sic_mean);originalSICMonth.set(k,vals);
}
const annual=[];
const annualByKey=new Map();
for(const site of historical){
 const vv=[];
 for(let year=1991;year<=2020;year++){
  const m=originalSICMonth.get(site.site_id+"|"+year);
  if(!m||m.length!==4||!m.every(Number.isFinite))throw Error("Missing SIC: "+site.site_id+" "+year);
  const sic=avg(m);
  const row={site_id:site.site_id,region:site.region,year,
   aug_nov_nearshore_sic_pct:sic,
   original_historical_growth_decade:site.growth_decade};
  annual.push(row);vv.push(sic);
  annualByKey.set(site.site_id+"|"+year,row);
 }
 if(Math.abs(avg(vv)-site.historic_nearshore_30y_SIC_pct)>1e-8)
  throw Error("Frozen historical 30-year mean not reproduced at "+site.site_id);
}
if(annual.length!==1170)throw Error("Original annual satellite coverage drift");
const observedCounts=D.count.filter(r=>
 oldHist.has(r.site_id)&&r.species_id==="ADPE"&&r.method===oldHist.get(r.site_id).method
 &&r.count!==""&&Number.isFinite(+r.count)&&+r.count>=0
 &&+r.season>=1991&&+r.season<=2020
);
const countsBySite=new Map();
for(const r of observedCounts){
 const arr=countsBySite.get(r.site_id)||[];
 arr.push(r);countsBySite.set(r.site_id,arr);
}
for(const vals of countsBySite.values())vals.sort((a,b)=>+a.season-+b.season);
const timingByKey=new Map();
for(const r of D.timing){
 const key=[r.site_id,r.start,r.end,r.method_start].join("|");
 if(timingByKey.has(key))throw Error("Duplicate original month audit "+key);
 timingByKey.set(key,r);
}
const pairs=[];
for(const site of historical){
 const vals=countsBySite.get(site.site_id)||[];
 for(let k=1;k<vals.length;k++){
  const lo=vals[k-1],hi=vals[k],start=+lo.season,end=+hi.season;
  if(end!==start+1||+lo.count<=0||+hi.count<=0)continue;
  const begin=annualByKey.get(site.site_id+"|"+start),finish=annualByKey.get(site.site_id+"|"+end);
  if(!begin||!finish)throw Error("SIC count annual join missing");
  const key=[site.site_id,start,end,site.method].join("|");
  const row=timingByKey.get(key);
  if(row){
   if(row.same_known_method!=="True"||row.method_start!==site.method||row.method_end!==site.method
      ||Math.abs(+row.n_start- +lo.count)>1e-8||Math.abs(+row.n_end- +hi.count)>1e-8)
    throw Error("Original count month audit failed for "+key);
  }
  pairs.push({
   site_id:site.site_id,region:site.region,method:site.method,start_year:start,end_year:end,
   original_count_before:+lo.count,original_count_after:+hi.count,
   yearly_log_count_growth:Math.log(+hi.count/+lo.count),
   SIC_start_year_pct:begin.aug_nov_nearshore_sic_pct,
   SIC_end_year_pct:finish.aug_nov_nearshore_sic_pct,
   delta_SIC_pp:finish.aug_nov_nearshore_sic_pct-begin.aug_nov_nearshore_sic_pct,
   month_audit_record_present:!!row,
   both_count_months_known:!!row&&row.both_all_months_known==="True",
   both_count_months_after_november:!!row&&row.both_all_after_november==="True",
   both_count_months_after_september:!!row&&row.both_all_after_september==="True"
  });
 }
}
pairs.sort((a,b)=>a.end_year-b.end_year||a.site_id.localeCompare(b.site_id));
const strict=pairs.filter(x=>x.both_count_months_after_november);
const strictRegions=[...new Set(strict.map(x=>x.region))];
const classified=[];
const accuracy=[];
for(let i=0;i<=200;i++){
 const t=Math.round((60+i*.1)*10)/10;
 const correct=historical.filter(x=>(x.historic_nearshore_30y_SIC_pct<t)===x.observed_growth_negative).length;
 accuracy.push({threshold_SIC_pct:t,original_sites:39,correct,classifier_in_sample_accuracy:correct/39});
}
for(const r of historical){
 const candidates=historical.filter(x=>x.region===r.region);
 const negative=candidates.filter(x=>x.observed_growth_negative).length,positive=candidates.length-negative;
 const modeNegative=negative>positive;
 classified.push({
  ...r,historical_SIC_region_type_mode_negative:modeNegative,
  classified_declining_by_77_5:r.historic_nearshore_30y_SIC_pct<77.5,
  correct_sic_77_5:(r.historic_nearshore_30y_SIC_pct<77.5)===r.observed_growth_negative,
  correct_region_majority_in_sample:modeNegative===r.observed_growth_negative
 });
}
const historicalSIC77=classified.filter(x=>x.correct_sic_77_5).length;
const regionAccuracy=classified.filter(x=>x.correct_region_majority_in_sample).length;
const regionCounts=regions.map(r=>({region:r,n:historical.filter(x=>x.region===r).length,
 negative_trend:historical.filter(x=>x.region===r&&x.observed_growth_negative).length,
 positive_trend:historical.filter(x=>x.region===r&&!x.observed_growth_negative).length}));
const supports=[];
const thresholds=[60,65,70,74.4,75,77.5,79.8,80];
const comparisons=[];
const selectedEvents=[];
const countList=(r,k)=>r.filter(k).length;
for(const a of accuracy){
 const t=a.threshold_SIC_pct;
 const isLow=x=>x.aug_nov_nearshore_sic_pct<t;
 const an=annual.filter(x=>x.aug_nov_nearshore_sic_pct>=60&&x.aug_nov_nearshore_sic_pct<80);
 const starts=pairs.filter(x=>x.SIC_start_year_pct>=60&&x.SIC_start_year_pct<80);
 const down=pairs.filter(x=>x.SIC_start_year_pct>=t&&x.SIC_end_year_pct<t);
 const up=pairs.filter(x=>x.SIC_start_year_pct<t&&x.SIC_end_year_pct>=t);
 const monthDown=down.filter(x=>x.both_count_months_after_november);
 const monthUp=up.filter(x=>x.both_count_months_after_november);
 supports.push({
  threshold_SIC_pct:t,observed_30yr_sites_below:classified.filter(x=>x.historic_nearshore_30y_SIC_pct<t).length,
  annual_siteyears_below:countList(annual,x=>isLow(x)),
  count_pair_start_SIC_below:countList(pairs,x=>x.SIC_start_year_pct<t),
  strict_count_pair_start_SIC_below:countList(strict,x=>x.SIC_start_year_pct<t),
  transitions_into_lower_SIC_n:down.length,
  transitions_into_lower_SIC_strict_count_month_n:monthDown.length,
  transitions_out_of_lower_SIC_n:up.length,
  transitions_out_of_lower_SIC_strict_count_month_n:monthUp.length,
  site_n_with_strict_down:uniq(monthDown,x=>x.site_id),
  site_n_with_strict_up:uniq(monthUp,x=>x.site_id),
  strict_down_mean_log_count_growth:monthDown.length?avg(monthDown.map(x=>x.yearly_log_count_growth)):null,
  strict_up_mean_log_count_growth:monthUp.length?avg(monthUp.map(x=>x.yearly_log_count_growth)):null,
  strict_down_negative_growth_fraction:monthDown.length?monthDown.filter(x=>x.yearly_log_count_growth<0).length/monthDown.length:null
 });
 if(thresholds.includes(t)){
  comparisons.push(supports.at(-1));
  for(const p of [...down.map(x=>({...x,direction:"down"})),...up.map(x=>({...x,direction:"up"}))])
   selectedEvents.push({...p,threshold_SIC_pct:t});
 }
}
// Persistence: a low-SIC year alone is not a 20-year mean regime shift.
const sequences=[];
for(const site of historical)for(const t of [60,75,77.5,80]){
 const series=annual.filter(x=>x.site_id===site.site_id).sort((a,b)=>a.year-b.year);
 let run=[],runs=[];
 for(const r of series){
  if(r.aug_nov_nearshore_sic_pct<t)run.push(r.year);
  else if(run.length){runs.push(run);run=[]}
 }
 if(run.length)runs.push(run);
 const biggest=runs.length?Math.max(...runs.map(x=>x.length)):0;
 sequences.push({site_id:site.site_id,region:site.region,threshold_SIC_pct:t,
  historical_mean_SIC_pct:site.historic_nearshore_30y_SIC_pct,
  total_low_SIC_years:runs.reduce((a,b)=>a+b.length,0),
  number_low_runs:runs.length,longest_consecutive_low_run:biggest,
  number_runs_at_least_3_years:runs.filter(x=>x.length>=3).length,
  starts_and_ends_of_runs:runs.map(a=>a[0]+"-"+a.at(-1)).join(";")});
}
// Chronological conditional hindcast: does a hypothetical binary threshold add predictive value
// beyond past observed site growth for month-verified counts? No future counts enter training.
const ridge=5;const minPrior=30,minPriorSites=5;
function siteMeans(training){
 const groups=new Map();
 for(const x of training){const a=groups.get(x.site_id)||[];a.push(x);groups.set(x.site_id,a)}
 const map=new Map();
 for(const [site,rows] of groups){map.set(site,{meanY:avg(rows.map(x=>x.yearly_log_count_growth)),n:rows.length})}
 return map;
}
const cv=[],cvDetails=[];
for(const a of accuracy){
 const t=a.threshold_SIC_pct;
 let preds=[],xVariation=0,yearsEvaluated=new Set();
 const years=[...new Set(strict.map(x=>x.end_year))].sort((a,b)=>a-b);
 for(const year of years){
  const train=strict.filter(x=>x.end_year<year);
  const test=strict.filter(x=>x.end_year===year);
  if(train.length<minPrior||uniq(train,x=>x.site_id)<minPriorSites)continue;
  const groups=siteMeans(train);
  const groupIndicators=new Map();
  for(const x of train){
   const a=groupIndicators.get(x.site_id)||[];a.push(x.SIC_end_year_pct<t?1:0);groupIndicators.set(x.site_id,a);
  }
  const meani=new Map([...groupIndicators].map(([k,vals])=>[k,avg(vals)]));
  let xy=0,xx=0;
  for(const x of train){
   const indicator=x.SIC_end_year_pct<t?1:0,
    centered=indicator-meani.get(x.site_id);
   xy+=centered*(x.yearly_log_count_growth-groups.get(x.site_id).meanY);
   xx+=centered*centered;
  }
  const beta=xy/(xx+ridge);
  xVariation=Math.max(xx,xVariation);
  const lastTrain=Math.max(...train.map(x=>x.end_year));
  if(lastTrain>=year)throw Error("Chronological leakage");
  for(const x of test){
   const s=groups.get(x.site_id);
   if(!s||s.n<2)continue; // compare same sites with at least two prior verified observations
   yearsEvaluated.add(year);
   const base=s.meanY,ind=x.SIC_end_year_pct<t?1:0;
   preds.push({threshold_SIC_pct:t,site_id:x.site_id,region:x.region,
    test_year:year,training_last_end_year:lastTrain,training_total_intervals:train.length,
    actual_log_growth:x.yearly_log_count_growth,
    prediction_site_past_mean:base,
    prediction_site_past_mean_plus_low_SIC:base+beta*(ind-meani.get(x.site_id)),
    training_beta_shrunk:beta,
    test_seaice_end_year_pct:x.SIC_end_year_pct});
  }
 }
 if(!preds.length)throw Error("Chronological test unsupported");
 const mae=k=>avg(preds.map(x=>Math.abs(x[k]-x.actual_log_growth))),
 rmse=k=>Math.sqrt(avg(preds.map(x=>(x[k]-x.actual_log_growth)**2)));
 const baseMAE=mae("prediction_site_past_mean"),iceMAE=mae("prediction_site_past_mean_plus_low_SIC");
 cv.push({threshold_SIC_pct:t, test_count_pairs:preds.length,
  distinct_test_sites:uniq(preds,x=>x.site_id),
  distinct_test_years:yearsEvaluated.size,
  original_site_mean_MAE:baseMAE,
  hypothetical_low_SIC_extra_MAE:iceMAE,
  delta_MAE_environment_minus_baseline:iceMAE-baseMAE,
  original_site_mean_RMSE:rmse("prediction_site_past_mean"),
  hypothetical_low_SIC_extra_RMSE:rmse("prediction_site_past_mean_plus_low_SIC"),
  maximum_observed_training_indicator_variation:xVariation,
  interpretation:"post_November_count_only_conditional_observed_climate_hindcast_no_Cmip_demography_transfer"});
 if(thresholds.includes(t))cvDetails.push(...preds);
}
if(accuracy.length!==201||supports.length!==201||cv.length!==201)throw Error("Cutoff grid size drift");
const facts={
 historical_sites:historical.length,
 negative_30yr_growth_site_n:historical.filter(x=>x.observed_growth_negative).length,
 positive_30yr_growth_site_n:historical.filter(x=>!x.observed_growth_negative).length,
 historical_30yr_mean_gap_lower:Math.max(...historical.filter(x=>x.historic_nearshore_30y_SIC_pct<80).map(x=>x.historic_nearshore_30y_SIC_pct)),
 historical_30yr_mean_gap_upper:Math.min(...historical.filter(x=>x.historic_nearshore_30y_SIC_pct>=80).map(x=>x.historic_nearshore_30y_SIC_pct)),
 historical_77_5_correct:historicalSIC77,historical_region_mode_correct:regionAccuracy,
 source_region_count:regions.length,
 annual_site_years:annual.length,annual_band_60_80:annual.filter(x=>x.aug_nov_nearshore_sic_pct>=60&&x.aug_nov_nearshore_sic_pct<80).length,
 method_pinned_annual_counts:observedCounts.length,positive_consecutive_same_method_pairs:pairs.length,
 positive_count_pair_sites:uniq(pairs,x=>x.site_id),
 strict_after_november_count_pairs:strict.length,
 strict_after_november_regions:strictRegions,
 pair_start_annual_60_80:pairs.filter(x=>x.SIC_start_year_pct>=60&&x.SIC_start_year_pct<80).length,
 strict_pair_start_annual_60_80:strict.filter(x=>x.SIC_start_year_pct>=60&&x.SIC_start_year_pct<80).length,
 down77_5:pairs.filter(x=>x.SIC_start_year_pct>=77.5&&x.SIC_end_year_pct<77.5).length,
 down77_5_strict:strict.filter(x=>x.SIC_start_year_pct>=77.5&&x.SIC_end_year_pct<77.5).length,
 up77_5:pairs.filter(x=>x.SIC_start_year_pct<77.5&&x.SIC_end_year_pct>=77.5).length,
 crozier_3year_low_77_5:sequences.filter(x=>["CRZE","CRZW"].includes(x.site_id)&&x.threshold_SIC_pct===77.5).map(x=>({site_id:x.site_id,maximum_years:x.longest_consecutive_low_run,n_low_years:x.total_low_SIC_years})),
 hindcast_77_5:cv.find(x=>x.threshold_SIC_pct===77.5),
 historic_rule_scores:accuracy.filter(x=>[60,65,75,77.5,80].includes(x.threshold_SIC_pct)),
 source_git_blobs:Object.fromEntries(Object.entries(sources).map(([k,[p,v]])=>[k,v]))
};
if(process.argv.includes("--check-receipt")){
 for(const [k,expectedValue] of Object.entries(expected.values)){
  const observed=facts[k];
  if(!Number.isFinite(observed)||Math.abs(observed-expectedValue)>1e-8)throw Error("Independent receipt mismatch "+k+" got "+observed+" expected "+expectedValue);
 }
 const base=cv[0].original_site_mean_MAE;
 if(cv.some(x=>Math.abs(x.original_site_mean_MAE-base)>1e-10||x.test_count_pairs!==cv[0].test_count_pairs))
  throw Error("Cannot compare climate thresholds on different chronology validation cohorts");
}
mkdirSync(outdir,{recursive:true});
writeFileSync(join(outdir,"yearly_39site_original_nearshore_ice.csv"),csvWrite(annual));
writeFileSync(join(outdir,"same_method_annual_count_transitions.csv"),csvWrite(pairs));
writeFileSync(join(outdir,"observational_spatial_rule_accuracy.csv"),csvWrite(accuracy));
writeFileSync(join(outdir,"observed_cutoff_annual_transition_support.csv"),csvWrite(supports));
writeFileSync(join(outdir,"site_30yr_growth_sign_vs_ice.csv"),csvWrite(classified));
writeFileSync(join(outdir,"month_verified_selected_annual_crossings.csv"),csvWrite(selectedEvents));
writeFileSync(join(outdir,"three_year_low_sic_episode_support.csv"),csvWrite(sequences));
writeFileSync(join(outdir,"chronological_conditional_hindcast_metrics.csv"),csvWrite(cv));
writeFileSync(join(outdir,"selected_cutoff_chronological_hindcasts.csv"),csvWrite(cvDetails));
writeFileSync(join(outdir,"result.json"),JSON.stringify({status:"annual_source_verified_observability_and_biological_threshold_temporal_gate_only",facts,cutoff_selected:comparisons,
 cutoff_annual_cv:cv.filter(x=>thresholds.includes(x.threshold_SIC_pct)),
 boundary:"Historical site-means are geographically confounded; annual excursions are not equal to decades-long climate regime transitions. No demonstrated causal population response, climate mortality hazard, extinction probability, or forecast.",root_sources:sources},null,2)+"\n");
writeFileSync(join(outdir,"validation.json"),JSON.stringify({source_pins_verified:true,receipt_verified:process.argv.includes("--check-receipt"),count_pairs:pairs.length,strict_after_nov_count_pairs:strict.length,annual_site_years:annual.length,thresholds:accuracy.length,crossing_reference_t:77.5},null,2)+"\n");
console.log("TEMPORAL SEAICE BIOLOGICAL BOUNDARY GATE "+JSON.stringify({facts,selected:comparisons,cv:cv.filter(x=>thresholds.includes(x.threshold_SIC_pct)),receipt_verified:process.argv.includes("--check-receipt")}));
