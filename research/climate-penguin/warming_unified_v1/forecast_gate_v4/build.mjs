/* Forecast v4: actual-origin five-year count forecast, source-verified v3 as ground truth.
   This is an exploratory hindcast, not validated 2050/2100 breeding forecasts. */
import {readFileSync,writeFileSync,mkdirSync} from "node:fs";
import {resolve,dirname} from "node:path";
import {fileURLToPath} from "node:url";
import {execFileSync} from "node:child_process";
import {createHash} from "node:crypto";
import assert from "node:assert/strict";
const here=dirname(fileURLToPath(import.meta.url));
const v3=resolve(here,"../forecast_gate_v3");
execFileSync(process.execPath,[resolve(v3,"build.mjs")],{timeout:120000});
const out=resolve(here,"outputs");
const csv=s=>{const lines=s.trim().split(/\r?\n/),head=lines.shift().split(",");
  return lines.map(x=>{const a=x.split(",");assert.equal(a.length,head.length);
    return Object.fromEntries(head.map((key,i)=>[key,a[i]]));});};
const mean=a=>{assert(a.length>0);return a.reduce((s,x)=>s+x,0)/a.length;};
const score=(a,p,y="actual")=>{const e=a.map(r=>r[p]-r[y]);
  return {n:e.length,mae:mean(e.map(Math.abs)),rmse:Math.sqrt(mean(e.map(x=>x*x))),bias:mean(e)};};
const toCsv=(a,keys)=>[keys.join(","),...a.map(r=>keys.map(k=>String(r[k]??"")).join(","))].join("\n")+"\n";
const panel=csv(readFileSync(resolve(v3,"outputs/fiveyear_panel.csv"),"utf8"))
  .map(r=>({...r,end:+r.end,delta_log1p_n:+r.delta_log1p_n,delta_sic_pp:+r.delta_sic_pp}));
const archived=csv(readFileSync(resolve(v3,"outputs/chronological_predictions.csv"),"utf8"));
const prev=JSON.parse(readFileSync(resolve(v3,"outputs/metrics.json"),"utf8"));
assert.equal(prev.status,"NOT_VALIDATED_FOR_FUTURE_BREEDING_FORECAST");
assert.equal(panel.length,87);assert.equal(archived.length,47);
const indexed=new Map(archived.map(r=>[r.end+"/"+r.unit,r]));
assert.equal(indexed.size,47);
const regions=[...new Set(panel.map(r=>r.region))].sort();
function linearSolve(A,B){
 A=A.map(row=>row.slice());B=B.slice();
 for(let j=0;j<B.length;j++){
  let best=j;for(let i=j+1;i<B.length;i++)if(Math.abs(A[i][j])>Math.abs(A[best][j]))best=i;
  [A[j],A[best]]=[A[best],A[j]];[B[j],B[best]]=[B[best],B[j]];
  assert(Math.abs(A[j][j])>1e-12,"singular");
  const pivot=A[j][j];for(let k=j;k<B.length;k++)A[j][k]/=pivot;B[j]/=pivot;
  for(let i=0;i<B.length;i++)if(i!==j){const d=A[i][j];
   for(let k=j;k<B.length;k++)A[i][k]-=d*A[j][k];B[i]-=d*B[j];}
 }return B;
}
function predict(train,test,interact){
 const f=r=>{const a=[1,+(r.sp==="CHPE"),+(r.sp==="GEPE"),
   ...regions.slice(1).map(z=>+(r.region===z)),(r.end-2010)/10,r.delta_sic_pp/10];
   if(interact)a.push(r.delta_sic_pp/10*(r.sp==="CHPE"),
                      r.delta_sic_pp/10*(r.sp==="GEPE"));
   return a;};
 const X=train.map(f),x=f(test),n=x.length;
 const penalties=[0,3,3,...regions.slice(1).map(()=>4),4,
                   ...(interact?[8,14,14]:[8])];
 assert.equal(n,penalties.length);
 const A=Array.from({length:n},(_,i)=>Array.from({length:n},(_,j)=>
   X.reduce((s,row)=>s+row[i]*row[j],0)+(i===j?penalties[i]:0)));
 const B=Array.from({length:n},(_,i)=>X.reduce((s,row,k)=>s+row[i]*train[k].delta_log1p_n,0));
 const beta=linearSolve(A,B);
 return x.reduce((s,v,i)=>s+v*beta[i],0);
}
function uniqueClimate(a){
 const distinct=new Map();
 for(const r of a){const key=r.site+"/"+r.end;
  if(distinct.has(key))assert(Math.abs(distinct.get(key).delta_sic_pp-r.delta_sic_pp)<1e-8);
  else distinct.set(key,r);
 }return [...distinct.values()];
}
const predicted=[];
for(const year of [2010,2015,2020]){
 const train=panel.filter(r=>r.end<year);
 const held=panel.filter(r=>r.end===year);
 assert(train.length&&held.length);
 const climate=uniqueClimate(train);
 for(const test of held){
  const saved=indexed.get(year+"/"+test.unit);assert(saved);
  assert.equal(saved.site,test.site);
  assert(Math.abs(+saved.actual_delta_log1p_n-test.delta_log1p_n)<1e-9);
  assert(Math.abs(+saved.delta_sic_pp-test.delta_sic_pp)<1e-9);
  const oracle=predict(train,test,false);
  const oracleInteraction=predict(train,test,true);
  assert(Math.abs(oracle-(+saved.pred_ice))<1e-8,"v3 ice reconstruction failed");
  assert(Math.abs(oracleInteraction-(+saved.pred_species_ice))<1e-8,"v3 interaction reconstruction failed");
  const sitePast=climate.filter(x=>x.site===test.site).sort((a,b)=>a.end-b.end);
  const regionPast=climate.filter(x=>x.region===test.region);
  const nextIce={zero:0,
   last:sitePast.length?sitePast.at(-1).delta_sic_pp:0,
   region:regionPast.length?mean(regionPast.map(x=>x.delta_sic_pp)):0};
  const row={year,site:test.site,sp:test.sp,region:test.region,unit:test.unit,
    actual:test.delta_log1p_n,actual_ice_pp:test.delta_sic_pp,
    n_training:train.length,n_past_site:sitePast.length,n_past_region:regionPast.length,
    pred_zero:+saved.pred_zero,pred_oracle_ice:oracle,
    pred_oracle_species_ice:oracleInteraction};
  for(const [mode,ice] of Object.entries(nextIce)){
   row["ice_pred_"+mode+"_pp"]=ice;
   row["pred_"+mode+"_ice"]=predict(train,{...test,delta_sic_pp:ice},false);
   row["pred_"+mode+"_species_ice"]=predict(train,{...test,delta_sic_pp:ice},true);
  }
  predicted.push(row);
 }
}
assert.equal(predicted.length,47);
const models=["pred_zero","pred_oracle_ice","pred_oracle_species_ice",
 ...["zero","last","region"].flatMap(s=>["pred_"+s+"_ice","pred_"+s+"_species_ice"])];
const scores=Object.fromEntries(models.map(x=>[x,score(predicted,x)]));
assert(Math.abs(scores.pred_zero.mae-prev.scores.zero.mae)<1e-10);
assert(Math.abs(scores.pred_oracle_ice.mae-prev.scores.ice.mae)<1e-10);
assert(Math.abs(scores.pred_oracle_species_ice.mae-prev.scores.species_ice.mae)<1e-10);
const period=Object.fromEntries([2010,2015,2020].map(y=>
 [y,Object.fromEntries(models.map(x=>[x,score(predicted.filter(r=>r.year===y),x)]))]));
const iceScore=Object.fromEntries(["zero","last","region"].map(s=>{
 const e=predicted.map(r=>r["ice_pred_"+s+"_pp"]-r.actual_ice_pp);
 return [s,{mae:mean(e.map(Math.abs)),rmse:Math.sqrt(mean(e.map(x=>x*x))),n:e.length}];
}));
const fpath=resolve(here,"../data/six_site_future_physical.csv"),fb=readFileSync(fpath);
const fsha=createHash("sha1").update(Buffer.from("blob "+fb.length+"\0")).update(fb).digest("hex");
assert.equal(fsha,"1343d1668380c11d45db98440c993edd9c7b86e8");
const future=csv(fb.toString("utf8"));assert.equal(future.length,24);
const scenarios=[];
for(const experiment of ["ssp245","ssp585"])for(const periodName of ["2041-2060","2081-2100"]){
 const sub=future.filter(x=>x.experiment===experiment&&x.period===periodName);
 const marine=sub.filter(x=>x.source_verified_marine==="1");
 assert.equal(sub.length,6);assert.equal(marine.length,4);
 const cells=new Map(marine.map(x=>[x.marine_fingerprint,+x.SIC_pp_change_mean]));
 assert.equal(cells.size,2);
 scenarios.push({ssp:experiment,period:periodName,
  air_degC_6site:mean(sub.map(x=>+x.tas_C_change_mean)),
  SIC_pp_4site:mean(marine.map(x=>+x.SIC_pp_change_mean)),
  SIC_pp_2cell:mean([...cells.values()]),
  n_sites:6,n_marine_sites:4,n_marine_cells:2,
  future_nests:null,future_nesting_space:null});
}
const result={status:"COMPLETE_ORIGIN_TIME_VALIDATION__FUTURE_BREEDING_NOT_CALIBRATED",
 input_git_blobs:{...prev.input_git_blobs,physical:fsha},
 origin_rule:"train.end < heldout.end; heldout SIC is never used as input to test predictions",
 oracle_regression_reproduced:94,
 observations:{...prev.cohorts,test:predicted.length},
 scores,period_scores:period,ice_delta_forecast_scores:iceScore,
 beats_zero_pooled_mae:models.filter(m=>m!=="pred_zero"&&scores[m].mae<scores.pred_zero.mae),
 physical_scenarios:scenarios,
 future_biological_forecasts:null,
 limitations:["Training-only climate predictors are rudimentary baseline extrapolations, not GCM forecasts",
  "Different site-species rows and adjacent transitions are correlated",
  "No leave-region-out success, no historical CMIP6 delta calibration, no 2050/2100 count or patch output",
  "Post-result exploratory audit; candidate winner is not a validated future forecasting skill"]};
mkdirSync(out,{recursive:true});
writeFileSync(resolve(out,"metrics.json"),JSON.stringify(result,null,2)+"\n");
writeFileSync(resolve(out,"predictions.csv"),toCsv(predicted,Object.keys(predicted[0])));
writeFileSync(resolve(out,"future_physical_only.csv"),toCsv(scenarios,Object.keys(scenarios[0])));
const fmt=n=>n.toFixed(4);
const report=[
 "# 温暖化と繁殖の予測適格性：v4", "",
 "これは将来海氷を実測済みと仮定したv3ではなく、予測開始時の気候履歴だけを用いる追加の時間順検証。原巣数の47件、20地点、29地点×種。隣接期・同一地点で依存あり。", "",
 "## 過去の繁殖巣数変化予測：5年間のΔmean(log1p nests)", "",
 "| 予測 | MAE | RMSE |","|---|---:|---:|",
 ...models.map(k=>"| "+k+" | "+fmt(scores[k].mae)+" | "+fmt(scores[k].rmse)+" |"),
 "",
 "## 予測開始時点に知られていた海氷変化だけで次期海氷を予測", "",
 "| 海氷入力 | 次期ΔSIC誤差MAE(pp) |","|---|---:|",
 ...Object.keys(iceScore).map(k=>"| "+k+" | "+fmt(iceScore[k].mae)+" |"),
 "",
 "## 2050・2100年に相当する気候の物理投影（繁殖巣数は予測していない）", "",
 "| SSP | 期間 | 6地点の気温変化 °C | 4海洋適格地点の海氷変化 pp | 原海洋格子数 |",
 "|---|---|---:|---:|---:|",
 ...scenarios.map(r=>"| "+r.ssp+" | "+r.period+" | "+fmt(r.air_degC_6site)+" | "+fmt(r.SIC_pp_4site)+" | "+r.n_marine_cells+" |"),
 "",
 "判定: 過去期間の学習終了年より新しい海氷観測値を予測入力には使わず、v3のオラクル予測94個の正確な再計算を先に要求する。巣数・種比・区画利用・絶滅確率の将来数値は出力しない。生物未来予測が可能という証拠ではない。",
 ""].join("\n");
writeFileSync(resolve(out,"READOUT_JA.md"),report);
console.log(JSON.stringify({mae:Object.fromEntries(Object.entries(scores).map(([k,v])=>[k,v.mae])),iceScore,scenarios,better:result.beats_zero_pooled_mae},null,2));