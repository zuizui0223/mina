// Reproduce the exposure-only atlas. Requires Node.js >=20, no npm dependencies.
// Usage: node research/climate-penguin/work/cmip6_exposure_atlas_v1/build.mjs [original_input_dir] [output_dir]
import {readFileSync,writeFileSync,mkdirSync} from "node:fs";
import {resolve,join} from "node:path";
function parseCSV(s){
 const data=[];let row=[],val="",quote=false;
 for(let i=0;i<s.length;i++){const c=s[i];
  if(quote){if(c==='"'&&s[i+1]==='"'){val+='"';i++;}else if(c==='"')quote=false;else val+=c;}
  else if(c==='"')quote=true;else if(c===','){row.push(val);val="";}
  else if(c==='\n'){row.push(val.replace(/\r$/,""));if(row.length>1)data.push(row);row=[];val="";}
  else val+=c;
 }
 if(val||row.length){row.push(val);data.push(row);}
 if(quote)throw Error("CSV quote");
 const columns=data.shift();return data.map((r,i)=>{if(r.length!==columns.length)throw Error("bad columns row "+i);return Object.fromEntries(columns.map((k,j)=>[k,r[j]]))});
}
function encodeCSV(rows,cols){
 const enc=x=>{const s=x==null?"":String(x);return /[,\"\r\n]/.test(s)?'"'+s.replaceAll('"','""')+'"':s;};
 return cols.join(",")+"\n"+rows.map(r=>cols.map(c=>enc(r[c])).join(",")).join("\n")+"\n";
}
function buildAtlas(content,provenance){
 const changes=parseCSV(content["site_model_changes.csv"]),hist=parseCSV(content["seasonal_climatologies.csv"]).filter(x=>x.experiment_id==="historical"),ens=parseCSV(content["site_model_ensemble.csv"]);
 if(changes.length!==3816||hist.length!==954||ens.length!==1272)throw Error("upstream cohort changed");
 const models=["ACCESS-CM2","BCC-CSM2-MR","CESM2"], exps=["ssp245","ssp585"], periods=["2041-2060","2081-2100"],vars=["tas","siconc","sos"];
 const num=x=>{const n=Number(x);if(x===""||!Number.isFinite(n))throw Error("invalid number "+x);return n;};
 const avg=x=>x.reduce((a,b)=>a+b,0)/x.length;
 const key4=x=>[x.experiment_id,x.period,x.location_id,x.variable_id].join("|");
 const histMap=new Map(hist.map(x=>[[x.source_id,x.location_id,x.variable_id].join("|"),x]));
 const ensMap=new Map(ens.map(x=>[key4(x),x]));
 if(histMap.size!==954||ensMap.size!==1272)throw Error("upstream duplicate");
 const grouped=new Map();
 for(const x of changes){const k=[x.experiment_id,x.period,x.location_id].join("|");const ar=grouped.get(k)||[];ar.push(x);grouped.set(k,ar);}
 const all=[],locMeta=new Map(),fps=new Set();let checked=0;
 for(const [k,group] of grouped){
  if(group.length!==9)throw Error("incomplete 9-model-variable records "+k);
  const a=group[0], loc=a.location_id, locId=[a.site_id,a.cohort,a.latitude,a.longitude].join("|");
  if(locMeta.has(loc)&&locMeta.get(loc)!==locId)throw Error("unstable location "+loc);
  locMeta.set(loc,locId);
  const data={};
  for(const v of vars){
    const sub=group.filter(x=>x.variable_id===v).sort((x,y)=>models.indexOf(x.source_id)-models.indexOf(y.source_id));
    if(sub.length!==3||sub.some((x,i)=>x.source_id!==models[i]||num(x.complete_years)!==20))throw Error("model missing "+k+"/"+v);
    const delta=sub.map(x=>num(x.change)),base=sub.map(x=>num(x.baseline_1995_2014)),future=sub.map(x=>num(x.seasonal_mean)),dist=sub.map(x=>num(x.distance_km));
    const hsd=sub.map(x=>{const h=histMap.get([x.source_id,loc,v].join("|"));if(!h||Math.abs(num(h.seasonal_mean)-num(x.baseline_1995_2014))>1e-8)throw Error("historical mismatch "+k);return num(h.annual_sd)});
    const e=ensMap.get([a.experiment_id,a.period,loc,v].join("|"));
    if(!e||num(e.n_models)!==3||Math.abs(num(e.change_mean)-avg(delta))>1e-9||Math.abs(num(e.change_min)-Math.min(...delta))>1e-9||Math.abs(num(e.change_max)-Math.max(...delta))>1e-9)throw Error("ensemble crosscheck "+k+"/"+v);
    checked++;
    data[v]={sub,delta,base,future,dist,hsd,mean:avg(delta),min:Math.min(...delta),max:Math.max(...delta),negative:delta.filter(x=>x<0).length,positive:delta.filter(x=>x>0).length};
  }
  const fp=data.siconc.sub.map(x=>x.grid_cell_id).join("|");
  fps.add(fp);all.push({a,loc,data,fp});
 }
 if(grouped.size!==424||locMeta.size!==106||fps.size!==43||checked!==1272)throw Error("incorrect support "+grouped.size+" "+locMeta.size+" "+fps.size+" "+checked);
 const fpIDs=new Map([...fps].sort().map((x,i)=>[x,"F"+String(i+1).padStart(3,"0")]));
 const site=[],fpGroups=new Map();
 for(const p of all){
  const t=p.data.tas,i=p.data.siconc,s=p.data.sos,fp=fpIDs.get(p.fp),maxDist=Math.max(...i.dist);
  const row={
   experiment:p.a.experiment_id,period:p.a.period,location_id:p.loc,site_id:p.a.site_id,cohort:p.a.cohort,
   latitude:p.a.latitude,longitude:p.a.longitude,marine_fingerprint:fp,
   marine_max_model_cell_distance_km:maxDist,marine_all_3_models_within_50km:maxDist<=50?1:0,
   tas_change_mean_degC:t.mean,tas_change_min_degC:t.min,tas_change_max_degC:t.max,
   tas_increase_models:t.positive,tas_change_ge2_hist_sd_models:t.delta.filter((d,j)=>t.hsd[j]>0&&d>=2*t.hsd[j]).length,
   siconc_baseline_mean_pct:avg(i.base),siconc_future_mean_pct:avg(i.future),
   siconc_change_mean_pp:i.mean,siconc_change_min_pp:i.min,siconc_change_max_pp:i.max,
   siconc_decrease_models:i.negative,siconc_loss_ge5pp_all3:i.delta.every(d=>d<=-5)?1:0,
   siconc_loss_ge10pp_all3:i.delta.every(d=>d<=-10)?1:0,
   siconc_loss_ge20pp_all3:i.delta.every(d=>d<=-20)?1:0,
   siconc_future_below15pct_models:i.future.filter(x=>x<15).length,
   siconc_from_baseline_ge15_to_future_lt15_models:i.future.filter((x,j)=>i.base[j]>=15&&x<15).length,
   sos_change_mean_native001:s.mean,sos_change_min_native001:s.min,sos_change_max_native001:s.max,
   sos_decrease_models:s.negative
  };
  site.push(row);
  const groupKey=[row.experiment,row.period,fp].join("|"),arr=fpGroups.get(groupKey)||[];arr.push(row);fpGroups.set(groupKey,arr);
 }
 const cmp=(a,b)=>a.experiment.localeCompare(b.experiment)||a.period.localeCompare(b.period)||a.marine_fingerprint.localeCompare(b.marine_fingerprint);
 site.sort((a,b)=>cmp(a,b)||a.location_id.localeCompare(b.location_id));
 const fpRows=[];
 for(const [g,locs] of fpGroups){
  const first=locs[0];
  for(const loc of locs){if(Math.abs(loc.siconc_change_mean_pp-first.siconc_change_mean_pp)>1e-8||Math.abs(loc.siconc_change_min_pp-first.siconc_change_min_pp)>1e-8)throw Error("repeated fingerprint mismatch "+g);}
  fpRows.push({
   experiment:first.experiment,period:first.period,marine_fingerprint:first.marine_fingerprint,
   n_locations:locs.length,n_site_codes:new Set(locs.map(x=>x.site_id)).size,site_codes:[...new Set(locs.map(x=>x.site_id))].sort().join(";"),
   siconc_change_mean_pp:first.siconc_change_mean_pp,siconc_change_min_pp:first.siconc_change_min_pp,siconc_change_max_pp:first.siconc_change_max_pp,
   siconc_decrease_models:first.siconc_decrease_models,siconc_loss_ge5pp_all3:first.siconc_loss_ge5pp_all3,
   siconc_loss_ge10pp_all3:first.siconc_loss_ge10pp_all3,siconc_loss_ge20pp_all3:first.siconc_loss_ge20pp_all3
  });
 }
 fpRows.sort(cmp);if(fpRows.length!==172)throw Error("fingerprint rows "+fpRows.length);
 const counts=[];
 for(const exp of exps)for(const period of periods){
  const s=site.filter(x=>x.experiment===exp&&x.period===period),f=fpRows.filter(x=>x.experiment===exp&&x.period===period);
  const n=(rows,p)=>rows.filter(p).length;
  counts.push({
   experiment:exp,period,locations:s.length,marine_fingerprints:f.length,
   all3_warming_locations:n(s,x=>x.tas_increase_models===3),
   all3_ice_decline_locations:n(s,x=>x.siconc_decrease_models===3),
   all3_ice_loss5_locations:n(s,x=>x.siconc_loss_ge5pp_all3===1),
   all3_ice_loss10_locations:n(s,x=>x.siconc_loss_ge10pp_all3===1),
   all3_ice_loss10_fingerprints:n(f,x=>x.siconc_loss_ge10pp_all3===1),
   all3_ice_loss20_locations:n(s,x=>x.siconc_loss_ge20pp_all3===1),
   all3_ice_loss10_locations_cell_dist_le50km:n(s,x=>x.siconc_loss_ge10pp_all3===1&&x.marine_all_3_models_within_50km===1),
   all3_marine_cell_dist_le50km_locations:n(s,x=>x.marine_all_3_models_within_50km===1),
   all3_salinity_decline_locations:n(s,x=>x.sos_decrease_models===3),
   mixed_sign_salinity_locations:n(s,x=>x.sos_decrease_models===1||x.sos_decrease_models===2),
   all3_temp_delta_ge2_hist_sd_locations:n(s,x=>x.tas_change_ge2_hist_sd_models===3),
   all3_sic_future_below15pct_locations:n(s,x=>x.siconc_future_below15pct_models===3),
   all3_sic_newly_below15pct_locations:n(s,x=>x.siconc_from_baseline_ge15_to_future_lt15_models===3)
  });
 }
 const meta={
  status:"calculated_conditional_physical_exposure_not_biological_forecast",
  source_git_blob_sha:provenance,
  baseline:"1995-2014",season:"August–November",scenarios:exps,periods,models,
  n_locations:106,n_distinct_site_codes:new Set(site.map(x=>x.site_id)).size,n_marine_fingerprints:43,
  input_checks:{source_change_rows:changes.length,source_historical_rows:hist.length,source_ensemble_rows:ens.length,
   crosschecked_ensemble_rows:checked,site_scenario_rows:site.length,fingerprint_scenario_rows:fpRows.length},
  caveat:"A marine fingerprint is a shared 3-model SIC grid-cell tuple, NOT an independent island or statistical replicate. 15% seasonal-mean SIC is NOT a bird route threshold; 2 historical annual SD is descriptive model climate novelty, NOT a viability threshold.",
  scenarios:counts
 };
 return {files:{
  "site_scenario_exposure.csv":encodeCSV(site,Object.keys(site[0])),
  "marine_fingerprint_scenario.csv":encodeCSV(fpRows,Object.keys(fpRows[0])),
  "summary.json":JSON.stringify(meta,null,2)+"\n"
 },meta};
}
const input=["site_model_changes.csv","seasonal_climatologies.csv","site_model_ensemble.csv"];
const srcDir=resolve(process.argv[2]||"research/climate-penguin/outputs/cmip6_projection_v1");
const outDir=resolve(process.argv[3]||"research/climate-penguin/outputs/cmip6_exposure_atlas_v1");
const content=Object.fromEntries(input.map(n=>[n,readFileSync(join(srcDir,n),"utf8")]));
const r=buildAtlas(content,Object.fromEntries(input.map(n=>[n,"local_run_check_pinned_source_git_blob_shas_in_committed_summary"])));
mkdirSync(outDir,{recursive:true});for(const [name,data] of Object.entries(r.files))writeFileSync(join(outDir,name),data);

// Geographic point layer for QGIS/GeoJSON clients; repeated coordinates across scenarios
// are separate features, not separate islands. Filter by experiment and period to view.
const rowsGeo=parseCSV(r.files["site_scenario_exposure.csv"]);
const numericGeo=["tas_change_mean_degC","tas_change_min_degC","tas_change_max_degC","tas_increase_models","siconc_change_mean_pp","siconc_change_min_pp","siconc_change_max_pp","siconc_loss_ge10pp_all3","siconc_decrease_models","sos_change_mean_native001","sos_decrease_models","marine_max_model_cell_distance_km","marine_all_3_models_within_50km"];
const geojson={type:"FeatureCollection",name:"CMIP6 physical exposure, not future penguin breeding prediction",
  features:rowsGeo.map((x,i)=>({type:"Feature",id:i+1,
    geometry:{type:"Point",coordinates:[Number(x.longitude),Number(x.latitude)]},
    properties:Object.fromEntries([
      ...["experiment","period","location_id","site_id","cohort","marine_fingerprint"].map(k=>[k,x[k]]),
      ...numericGeo.map(k=>[k,Number(x[k])])
    ])}))};
writeFileSync(join(outDir,"site_scenario_exposure.geojson"),JSON.stringify(geojson)+"\\n");

console.log(JSON.stringify(r.meta.scenarios,null,2));
