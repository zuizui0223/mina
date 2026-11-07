/**
 * Forecast gate v3: temporally ordered five-year breeding-count change test.
 * SOURCE ONLY: original MAPPPD count records and original satellite SIC, locked
 * to exact source git blob SHAs. No 2050/2100 population forecast is made.
 * Run: node research/climate-penguin/warming_unified_v1/forecast_gate_v3/build.mjs
 * Node standard library only. Input data must be committed at the pinned paths.
 */
import { readFileSync, writeFileSync, mkdirSync } from "node:fs";
import { resolve, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import { createHash } from "node:crypto";
const here = dirname(fileURLToPath(import.meta.url));
const root = resolve(here, "../../outputs");
const out = resolve(here, "outputs");
const sources = {
  counts: ["comparison_audit/mapppd_unambiguous_site_seasons.csv", "fc134e364cf38699fa7611d7dee5fbbbcb370c0a"],
  ice: ["climate_penguin/macro_monthly_seaice_1991_2020.csv", "4fcea71c2d8b1069b6ad143f6522061ed434daf5"],
  cohort: ["warming_species_breeding_v1/historical_species_site_trends.csv", "2b6c0793ea9f9ea9acf0771052cf7a2ad9ab335b"],
};
function readPinned([p, sha]) {
  const bytes = readFileSync(resolve(root, p));
  const hash = createHash("sha1").update(Buffer.from("blob " + bytes.length + "\0")).update(bytes).digest("hex");
  if (hash !== sha) throw new Error("Input blob drift: " + p + " " + hash);
  return bytes.toString("utf8");
}
function parseCSV(t) {
  const lines = t.trim().split(/\r?\n/);
  const h = lines[0].split(",");
  return lines.slice(1).map(line => {
    const a = []; let b = ""; let q = false;
    for (let i = 0; i < line.length; i++) {
      const c = line[i];
      if (c === '"') { if (q && line[i+1] === '"') { b += '"'; i++; } else q = !q; }
      else if (c === "," && !q) { a.push(b); b = ""; }
      else b += c;
    }
    a.push(b);
    if (a.length !== h.length) throw new Error("Malformed CSV row");
    return Object.fromEntries(h.map((k,i) => [k,a[i]]));
  });
}
function avg(a) { if (!a.length) throw new Error("empty mean"); return a.reduce((s,x) => s+x,0)/a.length; }
function buildRows(counts, ice, trends) {
  const cohort = new Map(trends.map(t => [t.site_id+"/"+t.species_id, t]));
  if (trends.length !== 54) throw new Error("Cohort changed");
  const good = counts.filter(r => {
    const t = cohort.get(r.site_id+"/"+r.species_id);
    return t && t.method === r.method && r.count !== "" && Number.isFinite(+r.count);
  });
  const iceYear = new Map();
  for (const x of ice) {
    if (+x.inner_km !== 0 || ![8,9,10,11].includes(+x.month)) continue;
    const key = x.site_id+"/"+x.year, a = iceYear.get(key) ?? [];
    a.push(+x.sic_mean); iceYear.set(key,a);
  }
  const results = [];
  for (const t of trends) {
    const sub = good.filter(x => x.site_id===t.site_id && x.species_id===t.species_id);
    const bins = [];
    for (let start=1991; start<2020; start+=5) {
      const end = Math.min(start+4,2020);
      const measured = sub.filter(x => +x.season>=start && +x.season<=end);
      if (measured.length<2) continue;
      const sic = [];
      for (let yy=start; yy<=end; yy++) {
        const v=iceYear.get(t.site_id+"/"+yy);
        if (v?.length===4) sic.push(...v);
      }
      if (sic.length !== (end-start+1)*4) continue;
      bins.push({start,end,n:measured.length,
        logcount:avg(measured.map(x=>Math.log1p(+x.count))),sic:avg(sic)});
    }
    for (let i=1;i<bins.length;i++) {
      const a=bins[i-1], b=bins[i];
      if (b.start-a.start!==5) continue;
      results.push({
        site:t.site_id,sp:t.species_id,region:t.region,
        unit:t.site_id+"/"+t.species_id,
        prev_period:a.start+"-"+a.end,
        next_period:b.start+"-"+b.end,end:b.end,
        n_prev:a.n,n_next:b.n,
        delta_log1p_n:b.logcount-a.logcount,
        delta_sic_pp:b.sic-a.sic,
      });
    }
  }
  results.sort((a,b)=>a.end-b.end||a.site.localeCompare(b.site)||a.sp.localeCompare(b.sp));
  if (results.length!==87 || new Set(results.map(r=>r.site)).size!==20
      || new Set(results.map(r=>r.unit)).size!==29) throw new Error("Frozen five-year panel changed");
  return results;
}
const models = ["zero","species","region_species","site","time","ice","species_ice"];
function solve(A,B) {
  A=A.map(row=>row.slice()); B=B.slice(); const n=B.length;
  for (let j=0;j<n;j++) {
    let imax=j;
    for (let i=j+1;i<n;i++) if (Math.abs(A[i][j])>Math.abs(A[imax][j])) imax=i;
    [A[j],A[imax]]=[A[imax],A[j]];
    [B[j],B[imax]]=[B[imax],B[j]];
    if (Math.abs(A[j][j])<1e-12) throw new Error("Singular ridge");
    const pivot=A[j][j];
    for (let k=j;k<n;k++) A[j][k]/=pivot;
    B[j]/=pivot;
    for (let i=0;i<n;i++) {
      if (i===j) continue;
      const d=A[i][j];
      for (let k=j;k<n;k++) A[i][k]-=d*A[j][k];
      B[i]-=d*B[j];
    }
  }
  return B;
}
function predict(train,x,kind,regions) {
  if (kind==="zero") return 0;
  if (kind==="species") {
    const a=train.filter(r=>r.sp===x.sp);
    return avg(a.map(r=>r.delta_log1p_n));
  }
  if (kind==="region_species") {
    const a=train.filter(r=>r.sp===x.sp&&r.region===x.region);
    return a.length>=3 ? avg(a.map(r=>r.delta_log1p_n)) : predict(train,x,"species",regions);
  }
  if (kind==="site") {
    const a=train.filter(r=>r.unit===x.unit);
    return a.length ? avg(a.map(r=>r.delta_log1p_n)) : predict(train,x,"species",regions);
  }
  const feat = r => {
    const f=[1, +(r.sp==="CHPE"), +(r.sp==="GEPE"),
      ...regions.slice(1).map(z=>+(r.region===z)),(r.end-2010)/10];
    if (kind==="ice" || kind==="species_ice") {
      f.push(r.delta_sic_pp/10);
      if (kind==="species_ice") f.push(r.delta_sic_pp/10*(r.sp==="CHPE"),
                                      r.delta_sic_pp/10*(r.sp==="GEPE"));
    }
    return f;
  };
  const X=train.map(feat),T=feat(x),n=T.length;
  const penalties=[0,3,3,...regions.slice(1).map(()=>4),4,
    ...(kind==="ice"?[8]:kind==="species_ice"?[8,14,14]:[])];
  if (penalties.length!==n) throw new Error("Penalty dimension changed");
  const A=Array.from({length:n},(_,i)=>Array.from({length:n},(_,j)=>
    X.reduce((s,r)=>s+r[i]*r[j],0)+(i===j?penalties[i]:0)));
  const B=Array.from({length:n},(_,i)=>
    X.reduce((s,r,k)=>s+r[i]*train[k].delta_log1p_n,0));
  const beta=solve(A,B);
  return T.reduce((s,v,i)=>s+v*beta[i],0);
}
function score(rows) {
  const ans={};
  for (const model of models) {
    const errors=rows.map(r=>r["pred_"+model]-r.actual_delta_log1p_n);
    ans[model]={
      mae:avg(errors.map(Math.abs)),
      rmse:Math.sqrt(avg(errors.map(e=>e*e))),
      mean_bias:avg(errors),
    };
  }
  return ans;
}
function csvWrite(rows, fields) {
  return [fields.join(","), ...rows.map(r=>fields.map(k=>String(r[k])).join(","))].join("\n")+"\n";
}
const count=parseCSV(readPinned(sources.counts));
const ice=parseCSV(readPinned(sources.ice));
const cohorts=parseCSV(readPinned(sources.cohort));
const panel=buildRows(count,ice,cohorts);
const regions=[...new Set(panel.map(x=>x.region))].sort();
const predictions=[];
for (const testEnd of [2010,2015,2020]) {
  const train=panel.filter(x=>x.end<testEnd);
  const test=panel.filter(x=>x.end===testEnd);
  for (const r of test) {
    const entry={end:r.end,site:r.site,sp:r.sp,region:r.region,unit:r.unit,
      prev_period:r.prev_period,next_period:r.next_period,
      n_training:train.length,
      actual_delta_log1p_n:r.delta_log1p_n,
      delta_sic_pp:r.delta_sic_pp};
    for (const model of models) entry["pred_"+model]=predict(train,r,model,regions);
    predictions.push(entry);
  }
}
if (predictions.length!==47 || [2010,2015,2020].some(e=>!predictions.some(x=>x.end===e)))
  throw new Error("Chronology or test cohort changed");
const summary={
  status:"NOT_VALIDATED_FOR_FUTURE_BREEDING_FORECAST",
  outcome:"delta mean log1p observed nests between adjacent nonoverlapping five-year bins",
  time_gate:"train periods strictly before held-out period ending 2010, 2015, 2020",
  forcing:"retrospective perfect-forcing 8-11 month observed SIC within each 5-year bin; not an operational origin-time forecast",
  input_git_blobs:Object.fromEntries(Object.entries(sources).map(([k,v])=>[k,v[1]])),
  cohorts:{site_species_original:cohorts.length, fiveyear_transitions:panel.length,
    sites:new Set(panel.map(x=>x.site)).size,site_species:new Set(panel.map(x=>x.unit)).size,
    regions:regions.length, test_transitions:predictions.length,
    test_year_counts:Object.fromEntries([2010,2015,2020].map(y=>[y,predictions.filter(x=>x.end===y).length]))},
  scores:score(predictions),
  scores_by_test_period:Object.fromEntries([2010,2015,2020].map(y=>[y,score(predictions.filter(r=>r.end===y))])),
  test_species_counts:Object.fromEntries(["ADPE","CHPE","GEPE"].map(sp=>[sp,predictions.filter(x=>x.sp===sp).length])),
  scored_models:models,
  verdict:"No climate model beats the zero-change benchmark on pooled MAE; no 2050/2100 nest count projection.",
  limitations:["Repeated site/region climate cells","Adjacent transitions share a five-year source block",
    "Same-month census chronology not established","Post-result exploratory design",
    "CMIP6 coastal forcing bias unvalidated","Selected 54 site-species cohorts are not global sampling"],
};
mkdirSync(out,{recursive:true});
writeFileSync(resolve(out,"fiveyear_panel.csv"),csvWrite(panel,
 ["site","sp","region","unit","prev_period","next_period","end","n_prev","n_next","delta_log1p_n","delta_sic_pp"]));
writeFileSync(resolve(out,"chronological_predictions.csv"),csvWrite(predictions,
 ["end","site","sp","region","unit","prev_period","next_period","n_training",
  "actual_delta_log1p_n","delta_sic_pp",...models.map(m=>"pred_"+m)]));
writeFileSync(resolve(out,"metrics.json"),JSON.stringify(summary,null,2)+"\n");
console.log(JSON.stringify({cohorts:summary.cohorts,scores:summary.scores,verdict:summary.verdict},null,2));
