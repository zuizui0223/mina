import fs from 'node:fs';
import crypto from 'node:crypto';
function run(inputs) {
const parse=s=>{let [header,...lines]=s.trim().split(/\r?\n/);let h=header.split(",");return lines.map(l=>{let a=l.split(",");if(a.length!==h.length)throw Error("CSV schema");return Object.fromEntries(h.map((k,i)=>[k,a[i]]))})};
const assert=(c,msg)=>{if(!c)throw Error(msg)}, sum=x=>x.reduce((a,v)=>a+v,0), close=(a,b,tol=1e-9)=>Math.abs(a-b)<tol, number=s=>{assert(s!==""&&s!=null&&Number.isFinite(Number(s)),"numeric support");return Number(s)};
const support=parse(inputs.support), rosters=parse(inputs.rosters), v5=JSON.parse(inputs.v5), v8=parse(inputs.v8);
const out={status:"EXECUTED_HISTORICAL_CHANGE_FIELD_ALIGNMENT",cohorts:[],future_comparisons:[],limits:"Deterministic fixed-roster accounting of noncontemporaneous count medians. No causal effect, climate benefit, temporal transfer or biological forecast. Historical observed fields and CMIP6 anomaly fields differ in source/baseline and interval. No historical SST/future TAS or polynya/future SIC comparison."};
function calc(rows,variable){
  const n0=sum(rows.map(q=>number(q.n0))),n1=sum(rows.map(q=>number(q.n1)));
  assert(n0>0&&n1>0,"positive totals");
  const a=rows.map(q=>({p0:number(q.n0)/n0,p1:number(q.n1)/n1,x0:number(q[variable+"0"]),x1:number(q[variable+"1"])}));
  const E0=sum(a.map(z=>z.p0*z.x0)), E1=sum(a.map(z=>z.p1*z.x1));
  const earlyChange=sum(a.map(z=>z.p0*(z.x1-z.x0))), recentChange=sum(a.map(z=>z.p1*(z.x1-z.x0)));
  const A=sum(a.map(z=>(z.p1-z.p0)*(z.x1-z.x0))),R0=sum(a.map(z=>(z.p1-z.p0)*z.x0)),R1=sum(a.map(z=>(z.p1-z.p0)*z.x1)),R=(R0+R1)/2,L=(earlyChange+recentChange)/2;
  assert(close(A,recentChange-earlyChange)&&close(A,R1-R0)&&close(E1-E0,R+L),"accounting identity");
  return {early_weighted_change:earlyChange,recent_weighted_change:recentChange,change_field_contrast:A,early_level_reweighting:R0,recent_level_reweighting:R1,midpoint_level_reweighting:R,location_term:L,total:E1-E0,weighted_early_level:E0,weighted_recent_level:E1};
}
for(const z of v5.cohorts){
  const short=z.name.startsWith("short"), parent=z.name.includes("parent"), radius=short?(z.name.endsWith("_25")?"25":"100"):"0";
  const rows=(parent?support:rosters).filter(q=>q.comparison===(short?"polynya":"long")&&q.radius===radius&&q.eligible_counts==="True").sort((a,b)=>a.site_id.localeCompare(b.site_id));
  assert(rows.length===z.n&&new Set(rows.map(q=>q.site_id)).size===z.n,"roster size");
  assert(rows.map(q=>q.site_id).sort().join("|")===z.sites.slice().sort().join("|"),"site identity");
  assert(close(sum(rows.map(q=>number(q.n0))),z.composition.n0)&&close(sum(rows.map(q=>number(q.n1))),z.composition.n1),"count totals");
  const results={};
  for(const [variable,old] of Object.entries(z.exposure)){
     const a=calc(rows,variable);
     assert(close(a.midpoint_level_reweighting,old.redistribution)&&close(a.location_term,old.local)&&close(a.total,old.total),"prior accounting");
     const omit={};for(const reg of [...new Set(rows.map(q=>q.source_region))].sort()){let rr=rows.filter(q=>q.source_region!==reg);if(rr.length>=2&&sum(rr.map(q=>number(q.n0)))>0&&sum(rr.map(q=>number(q.n1)))>0)omit[reg]=calc(rr,variable).change_field_contrast;}
     results[variable]={...a,omit_region_change_field:omit,all_estimable_omissions_same_sign:Object.values(omit).length>0&&Object.values(omit).every(v=>v*a.change_field_contrast>0)};
  }
  out.cohorts.push({name:z.name,n:z.n,results});
}
assert(sum(out.cohorts.map(x=>Object.keys(x.results).length))===16,"16 historical rows");
for(const v of v8){
  const map={"long_parent23_all":"long_parent23","long_complete17_all":"long_complete17","short_parent15_all":"short_parent15_100","short_complete9_all":"short_complete9_100"};
  const z=out.cohorts.find(q=>q.name===map[v.cohort]),variable=v.variable==="siconc"?"sic_pp":v.variable==="sos"?"salinity":null;
  assert(z&&variable,"future schema");
  const d=number(v.late_weights)-number(v.early_weights),models=[number(v.ACCESS_difference),number(v.BCC_difference),number(v.CESM2_difference)];
  assert(close(d,sum(models)/3,3e-9),"future mean identity");
  const a=z.results[variable]?.change_field_contrast??null;
  out.future_comparisons.push({cohort:z.name,scenario:v.scenario,period:v.period,variable,historical_change_field_contrast:a,future_change_field_contrast:d,model_contrasts:models,same_sign_historical_and_future_mean:a===null?null:a*d>0,all_models_same_sign_as_historical:a===null?null:models.every(x=>x*a>0)});
}
assert(out.future_comparisons.length===32,"future extract size");
return out;
}
const keys=['support','rosters','v5','v8'];
const pins=[{"key":"support","commit":"c67e55c9f4f657ef308c02a85c6ff366dce8e1f4","path":"research/climate-penguin/macro_panantarctic_v1/redistribution_marine_exposure_20261120/matched_support.csv","blob":"da2b63a6d290d5f786badbcd0fbc0931f41ad52a"},{"key":"rosters","commit":"c67e55c9f4f657ef308c02a85c6ff366dce8e1f4","path":"research/climate-penguin/macro_panantarctic_v1/redistribution_marine_exposure_20261120/matched_rosters.csv","blob":"bc1a1401d9130bd30bfeae13cc8c6225491cc275"},{"key":"v5","commit":"06f6e7c7a35724e5a8b2ef8cb8034f6a14c6a327","path":"research/unified_breeding_reorganization_v1/ENVIRONMENT_INTEGRATION_BRIDGE_RESULT_20261125.json","blob":"5d050f907d9983a341e1050e837267c5521887d2"},{"key":"v8","commit":"06f6e7c7a35724e5a8b2ef8cb8034f6a14c6a327","path":"research/unified_breeding_reorganization_v1/ANTARCTIC_V8_FIGURE_EXTRACT.csv","blob":"5c6c7c566571fdc324717000d1cb234198aba4e9"}];
if(process.argv.length!==7)throw Error('Usage: node historical_change_field_v9.mjs matched_support.csv matched_rosters.csv V5.json V8.csv output.json');
const inputs={};for(let i=0;i<4;i++){const raw=fs.readFileSync(process.argv[i+2]);const sha=crypto.createHash('sha1').update(Buffer.concat([Buffer.from('blob '+raw.length),Buffer.from([0]),raw])).digest('hex');if(sha!==pins[i].blob)throw Error('Git blob pin '+keys[i]);inputs[keys[i]]=raw.toString('utf8');}
const out=run(inputs);out.source_pins=pins;out.execution="Executed from verified Git blobs using JavaScript in the current tool session. No raw source archive redownload or new CI claimed. Reproducer uses identical run function and verifies Git blob hashes.";fs.writeFileSync(process.argv[6],JSON.stringify(out,null,2)+'\n');
