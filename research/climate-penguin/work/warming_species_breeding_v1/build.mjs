// Reproduce source-backed same-site penguin breeding community shifts and CMIP6 warming conditions.
// Node >=20, from repo root.
import {readFileSync,writeFileSync,mkdirSync} from "node:fs";
import {createHash} from "node:crypto";
import {resolve,join} from "node:path";
function parseCSV(s){
 const rows=[];let r=[],v="",q=false;for(let i=0;i<s.length;i++){const c=s[i];if(q){if(c==='"'&&s[i+1]==='"'){v+='"';i++}else if(c==='"')q=false;else v+=c;}else if(c==='"')q=true;else if(c===','){r.push(v);v="";}else if(c==='\n'){r.push(v.replace(/\r$/,""));if(r.length>1)rows.push(r);r=[];v="";}else v+=c;}
 if(r.length||v){r.push(v);rows.push(r)}const h=rows.shift();if(q)throw Error("quotes");return rows.map((a,i)=>{if(a.length!==h.length)throw Error("columns "+i);return Object.fromEntries(h.map((k,j)=>[k,a[j]]))});
}
function toCSV(rows){const h=Object.keys(rows[0]),q=v=>{const s=v==null?"":String(v);return /[,"\n\r]/.test(s)?'"'+s.replaceAll('"','""')+'"':s};return h.join(",")+"\n"+rows.map(x=>h.map(k=>q(x[k])).join(",")).join("\n")+"\n"}
function compute(inputs,sha){
 const bio=parseCSV(inputs.bio),loc=parseCSV(inputs.locations),ice=parseCSV(inputs.ice),cmip=parseCSV(inputs.cmip);
 if(bio.length!==2999||loc.length!==106||ice.length!==9600||cmip.length!==3816)throw Error("upstream cohort drift");
 const sit=new Set(loc.filter(x=>x.cohort==="macro_40").map(x=>x.site_id));
 if(sit.size!==40)throw Error("macro count");
 const ss=["ADPE","CHPE","GEPE"];
 const mu=a=>a.reduce((z,v)=>z+v,0)/a.length,reg=(year,y)=>{let a=mu(year),b=mu(y),d=year.reduce((s,x)=>s+(x-a)**2,0);return year.reduce((s,x,i)=>s+(x-a)*(y[i]-b),0)/d;};
 const group=(a,key)=>{let m=new Map();for(const x of a){let k=key(x),d=m.get(k)||[];d.push(x);m.set(k,d)}return m};
 const all=bio.filter(x=>sit.has(x.site_id)&&ss.includes(x.species_id)&&+x.season>=1991&&+x.season<=2020);
 const trends=[],records=new Map(),lookup=new Map();
 for(const [key,a] of group(all,x=>x.site_id+"|"+x.species_id)){
  let g=[...group(a.filter(x=>x.count!==""&&Number.isFinite(+x.count)&&+x.count>=0&&x.method!=="unknown"),x=>x.method)].map(([method,b])=>{let v=b.slice().sort((x,y)=>+x.season- +y.season);return {method,rows:v,n:v.length,span:+v.at(-1).season- +v[0].season}});
  g=g.filter(x=>x.n>=4&&x.span>=10).sort((a,b)=>b.n-a.n||b.span-a.span||a.method.localeCompare(b.method));
  if(!g.length)continue;
  const m=g[0],d=m.rows,y=d.map(x=>+x.season),log=d.map(x=>Math.log1p(+x.count));
  const t={site_id:d[0].site_id,species_id:d[0].species_id,region:d[0].region,method:m.method,
   n_count_years:d.length,year_span:m.span,first_year:y[0],last_year:y.at(-1),n_zero_counts:d.filter(x=>+x.count===0).length,
   slope_log1p_count_decade:reg(y,log)*10};
  trends.push(t);records.set(key,d);lookup.set(key,t);
 }
 if(trends.length!==54||ss.some((s,i)=>trends.filter(x=>x.species_id===s).length!==[39,7,8][i]))throw Error("trend cohort change");
 const candidates=[],paired=[];
 for(const other of ["GEPE","CHPE"])for(const ad of trends.filter(x=>x.species_id==="ADPE")){
  const o=lookup.get(ad.site_id+"|"+other);if(!o)continue;
  const ar=records.get(ad.site_id+"|ADPE"),br=records.get(ad.site_id+"|"+other),bm=new Map(br.map(x=>[+x.season,x])),am=new Map(ar.map(x=>[+x.season,x]));
  const common=[...am.keys()].filter(y=>bm.has(y)).sort((a,b)=>a-b),ratio=common.map(y=>Math.log1p(+bm.get(y).count)-Math.log1p(+am.get(y).count));
  const span=common.at(-1)-common[0],ok=common.length>=5&&span>=10&&ad.method===o.method;
  const p={site_id:ad.site_id,region:ad.region,reference_species:"ADPE",compared_species:other,
    method_reference:ad.method,method_compared:o.method,common_years:common.join(";"),
    n_shared_years:common.length,shared_span_years:span,gate:ok?1:0,
    failure_reason:ok?"":common.length<5?"shared_years_lt5":span<10?"span_lt10":"method_diff",
    common_year_log1p_ratio_slope_decade:reg(common,ratio)*10,
    same_year_trend_drop_first:common.length>=4?reg(common.slice(1),ratio.slice(1))*10:null,
    same_year_trend_drop_last:common.length>=4?reg(common.slice(0,-1),ratio.slice(0,-1))*10:null,
    first_year:common[0],last_year:common.at(-1),
    first_ADPE_n:+am.get(common[0]).count,last_ADPE_n:+am.get(common.at(-1)).count,
    first_other_n:+bm.get(common[0]).count,last_other_n:+bm.get(common.at(-1)).count};
  candidates.push(p);if(ok)paired.push(p);
 }
 if(candidates.length!==15||paired.length!==13||paired.some(x=>x.common_year_log1p_ratio_slope_decade<=0))throw Error("paired effect drift");
 const codes=[...new Set(paired.map(x=>x.site_id))].sort();if(codes.length!==8)throw Error("matched site count");
 const iceIndex=new Map(ice.map(x=>[[x.site_id,x.year,x.month,x.inner_km].join("|"),x]));
 const future=cmip.filter(x=>x.cohort==="macro_40");
 if(future.length!==1440)throw Error("cmip macro count");
 const cmap=new Map(future.map(x=>[[x.site_id,x.source_id,x.experiment_id,x.period,x.variable_id].join("|"),x]));
 if(cmap.size!==1440)throw Error("cmip macro duplicate");
 const models=["ACCESS-CM2","BCC-CSM2-MR","CESM2"],scenario=[["ssp245","2041-2060"],["ssp245","2081-2100"],["ssp585","2041-2060"],["ssp585","2081-2100"]];
 const climate=[];
 for(const site of codes){
  const years=[];for(let year=1991;year<=2020;year++){let vv=[];for(const month of [8,9,10,11]){const x=iceIndex.get([site,year,month,0].join("|"));if(!x||x.complete_month!=="True")throw Error("missing historical ice "+site);vv.push(+x.sic_mean);}years.push(mu(vv))}
  const hist=mu(years),histDelta=reg(Array.from({length:30},(_,i)=>i+1991),years)*10;
  for(const [exp,period] of scenario){
   const env={};for(const v of ["tas","siconc","sos"]){
    env[v]=models.map(model=>{const x=cmap.get([site,model,exp,period,v].join("|"));if(!x)throw Error("CMIP data absence "+site+model+v);return {delta:+x.change,dist:+x.distance_km}});
   }
   climate.push({site_id:site,region:lookup.get(site+"|ADPE").region,experiment:exp,period,
    historical_obs_SIC_1991_2020_mean_pct:hist,historical_obs_SIC_trend_pp_decade:histDelta,
    tas_C_change_model_mean:mu(env.tas.map(x=>x.delta)),tas_C_change_min:Math.min(...env.tas.map(x=>x.delta)),tas_C_change_max:Math.max(...env.tas.map(x=>x.delta)),
    SIC_pp_change_model_mean:mu(env.siconc.map(x=>x.delta)),SIC_pp_change_min:Math.min(...env.siconc.map(x=>x.delta)),SIC_pp_change_max:Math.max(...env.siconc.map(x=>x.delta)),
    sos_change_model_mean:mu(env.sos.map(x=>x.delta)),
    all3_tas_increase:env.tas.every(x=>x.delta>0)?1:0,all3_sic_decrease:env.siconc.every(x=>x.delta<0)?1:0,
    all3_marine_cell_within50km:env.siconc.every(x=>x.dist<=50)?1:0,
    all3_sic_loss_ge10pp:env.siconc.every(x=>x.delta<=-10)?1:0});
  }
 }
 if(climate.length!==32||climate.some(x=>!x.all3_tas_increase||!x.all3_sic_decrease))throw Error("future climate signs different");
 const combined=paired.flatMap(p=>climate.filter(x=>x.site_id===p.site_id).map(x=>({...x,
    compared_species:p.compared_species,n_matched_years:p.n_shared_years,observed_ratio_decadal_trend:p.common_year_log1p_ratio_slope_decade,
    output_type:"observed_breeding_change_plus_conditional_physical_future_not_future_breeding_prediction"})));
 if(combined.length!==52)throw Error("joins unexpected");
 const effects=["GEPE","CHPE"].map(s=>{const q=paired.filter(x=>x.compared_species===s),a=q.map(x=>x.common_year_log1p_ratio_slope_decade).sort((a,b)=>a-b);return {
  contrast:s+"/ADPE",n_sites:q.length,n_ratio_trend_positive:q.filter(x=>x.common_year_log1p_ratio_slope_decade>0).length,
  leave_first_positive:q.filter(x=>x.same_year_trend_drop_first>0).length,
  leave_last_positive:q.filter(x=>x.same_year_trend_drop_last>0).length,
  average_decadal_log1p_ratio_trend:mu(a),median_decadal_log1p_ratio_trend:a[Math.floor(a.length/2)]}});
 const scenarios=scenario.map(([exp,period])=>{const a=climate.filter(x=>x.experiment===exp&&x.period===period);return {
  experiment:exp,period,n_site_codes:a.length,three_models_warming_sites:a.filter(x=>x.all3_tas_increase).length,
  three_models_SIC_decline_sites:a.filter(x=>x.all3_sic_decrease).length,
  sites_with_all3_ocean_cells_50km:a.filter(x=>x.all3_marine_cell_within50km).length,
  sites_3model_SIC_decline10pp:a.filter(x=>x.all3_sic_loss_ge10pp).length,
  eight_sites_mean_temperature_change_C:mu(a.map(x=>x.tas_C_change_model_mean)),
  eight_sites_mean_ice_change_pp:mu(a.map(x=>x.SIC_pp_change_model_mean))
 }});
 const metadata={status:"observed_matched_penguin_breeding_shift_with_projected_warming_conditions_not_causal_attribution_or_nesting_count_forecast",
  date:"2026-10-31",source_blob_sha:sha,
  inputs:{mapppd_records:bio.length,ice_monthly_records:ice.length,CMIP6_model_changes:cmip.length,macro_site_codes:40},
  outputs:{historical_species_sites:trends.length,candidates:candidates.length,matched_species_pairs:paired.length,
    unique_co_observed_site_codes:codes.length,site_scenarios:climate.length,paired_breeding_future_rows:combined.length},
  effects,scenario_climate:scenarios,
  caveats:"Count slopes are a source-backed historical biological phenomenon, not identified warming effects. Climatic CMIP6 changes only indicate future physical conditions, not calibrated biological responses. Same 8 sites share regions and ocean grid cells, model ensemble small. Zero counts retained as log1p, same method & years enforced, no independent climate->fitness coefficient."};
 return {meta:metadata,files:{
  "historical_species_site_trends.csv":toCSV(trends),
  "same_site_species_ratio_source_gate.csv":toCSV(candidates),
  "matched_species_breeding_change.csv":toCSV(paired),
  "future_climate_coobserved_sites.csv":toCSV(climate),
  "observed_breeding_future_environment.csv":toCSV(combined),
  "summary.json":JSON.stringify(metadata,null,2)+"\n"}};
}
const base=resolve("research/climate-penguin/outputs");
const output=resolve("research/climate-penguin/outputs/warming_species_breeding_v1");
const paths={"bio":"comparison_audit/mapppd_unambiguous_site_seasons.csv","locations":"climate_penguin/daily_ice_locations.csv","ice":"climate_penguin/macro_monthly_seaice_1991_2020.csv","cmip":"cmip6_projection_v1/site_model_changes.csv"};
const expected={"bio":"fc134e364cf38699fa7611d7dee5fbbbcb370c0a","locations":"1c5214ab355d3d2e19bc33e5de4693fa21f38731","ice":"4fcea71c2d8b1069b6ad143f6522061ed434daf5","cmip":"b383ef1cc3b0807b0bd010ca0e825937ab83ce97"};
const inputs={};
for(const [id,path] of Object.entries(paths)){
 const bytes=readFileSync(join(base,path));
 const computed=createHash("sha1").update(Buffer.from("blob "+bytes.length+"\0")).update(bytes).digest("hex");
 if(computed!==expected[id])throw Error("source changed "+id+" "+computed);
 inputs[id]=bytes.toString("utf8");
}
const result=compute(inputs,expected);
mkdirSync(output,{recursive:true});
for(const [filename,content] of Object.entries(result.files))writeFileSync(join(output,filename),content);
console.log(JSON.stringify(result.meta,null,2));
