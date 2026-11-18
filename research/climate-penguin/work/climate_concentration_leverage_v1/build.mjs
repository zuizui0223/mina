// Recompute the hierarchical shock-concentration endpoints and source-resolution audit.
// Node >= 20, no external libraries. Run at the repo root:
// node research/climate-penguin/work/climate_concentration_leverage_v1/build.mjs
// This is a mathematical sensitivity, NOT an ecological climate-response estimator.
import {readFileSync,writeFileSync} from "node:fs";
import {createHash} from "node:crypto";
import {join} from "node:path";

const base = "research/climate-penguin/outputs/climate_concentration_leverage_v1";
const inputs = {
  palmer: "results/PALMER_BREEDING_PATCH_CONCENTRATION_RESULT_V1.json",
  signyA: "results/SIGNY_BREEDING_PATCH_CONCENTRATION_RESULT_V1.json",
  signyC: "results/SIGNY_CHINSTRAP_BREEDING_PATCH_CONCENTRATION_RESULT_V1.json",
  climate: "research/climate-penguin/outputs/cmip6_exposure_atlas_v1/site_scenario_exposure.csv"
};
const expectedBlobs = {
  "palmer": "241ff94d59c4cfcc25ac81d4ad10bff4a585517b",
  "signyA": "7ad808e34334109918031c2a2685f4dbc5546a14",
  "signyC": "dc96605d8d81448911e3fcd958427d696917718d",
  "climate": "9d7badfd2ad077047cb6f20accc74e3738cf4648"
};
function checkGitBlob(path, expected){
  const buf = readFileSync(path);
  const git = createHash("sha1").update(Buffer.concat([
    Buffer.from("blob "+buf.length+"\0"),buf
  ])).digest("hex");
  if(git!==expected) throw new Error("Git source SHA changed: "+path+" "+git);
  return buf.toString("utf8");
}
const source={};
for(const [key,path] of Object.entries(inputs)){
  source[key]=checkGitBlob(path,expectedBlobs[key]);
}
function parseCSV(text){
  const ar=text.trimEnd().split(/\r?\n/),cols=ar.shift().split(",");
  return ar.map((line,i)=>{
    const r=line.split(",");
    if(r.length!==cols.length) throw new Error("Unexpected CSV columns "+i);
    return Object.fromEntries(cols.map((c,j)=>[c,r[j]]));
  });
}
function csv(rows){
  const keys=Object.keys(rows[0]);
  return keys.join(",")+"\n"+rows.map(r=>keys.map(k=>r[k]??"").join(",")).join("\n")+"\n";
}
function near(a,b){return Math.abs(a-b)<1e-10}
const ep=parseCSV(readFileSync(join(base,"palmer_island_state_endpoints.csv"),"utf8"))
  .map(r=>({year:Number(r.year),island:r.island,total:Number(r.breeding_pairs),
    neff:r.effective_component_number===""?null:Number(r.effective_component_number),
    active:Number(r.active_components)}));
if(ep.length!==10)throw new Error("Palmer endpoint count changed");
const pal=JSON.parse(source.palmer).observed;
for(const island of ["COR","HUM","LIT"]){
  if(!near(ep.find(x=>x.island===island&&x.year===1991).neff,
       pal[island].first_neff))throw new Error("Palmer first Neff changed "+island);
  if(island!=="LIT"&&!near(ep.find(x=>x.island===island&&x.year===2017).neff,
                         pal[island].last_neff))
    throw new Error("Palmer last Neff changed "+island);
}
const yrs=[1991,2017].map(year=>{
 const arr=ep.filter(x=>x.year===year);
 const total=arr.reduce((s,x)=>s+x.total,0);
 const H_island=arr.reduce((s,x)=>s+(x.total/total)**2,0);
 const H_component=arr.reduce((s,x)=>
    s+(x.total>0?(x.total/total)**2/x.neff:0),0);
 const max=Math.max(...arr.map(x=>x.total));
 return {year,total_pairs:total,occupied_islands:arr.filter(x=>x.total>0).length,
   H_island,H_component,neff_islands:1/H_island,neff_components:1/H_component,
   top_island:arr.find(x=>x.total===max).island,top_share:max/total};
});
if(yrs[0].total_pairs!==6689||yrs[1].total_pairs!==140||
   !near(yrs[0].neff_components,31.055698346318692)||
   !near(yrs[1].neff_components,6.148055207026348))
  throw new Error("Original Palmer five-island summary changed");
const a=JSON.parse(source.signyA).observed;
const b=JSON.parse(source.signyC).observed;
const units=[
 {system:"Palmer COR",year_first:1991,year_last:2017,neff_first:pal.COR.first_neff,neff_last:pal.COR.last_neff},
 {system:"Palmer HUM",year_first:1991,year_last:2017,neff_first:pal.HUM.first_neff,neff_last:pal.HUM.last_neff},
 {system:"Palmer LIT last positive",year_first:1991,year_last:2006,neff_first:pal.LIT.first_neff,neff_last:pal.LIT.last_neff},
 {system:"Signy Adelie",year_first:1996,year_last:2019,neff_first:a.first_neff,neff_last:a.last_neff},
 {system:"Signy Chinstrap",year_first:1996,year_last:2019,neff_first:b.first_effective_breeding_patch_number,neff_last:b.last_effective_breeding_patch_number}
];
const rhos=[0,.25,.5,.75,.9,1];
const V=(H0,H1,rho)=>(rho+(1-rho)*H1)/(rho+(1-rho)*H0);
const rows=[];
for(const s of units)for(const rho of rhos){
 const z=V(1/s.neff_first,1/s.neff_last,rho);
 rows.push({...s,shock_scale:"within_island_monitored_components",
  assumed_pairwise_shock_correlation:rho,
  hypothetical_variance_ratio:z,hypothetical_sd_ratio:Math.sqrt(z)});
}
for(const scale of ["island","component"])for(const rho of rhos){
 const H0=scale==="island"?yrs[0].H_island:yrs[0].H_component,
       H1=scale==="island"?yrs[1].H_island:yrs[1].H_component,
       z=V(H0,H1,rho);
 rows.push({system:"Palmer five islands",year_first:1991,year_last:2017,
  neff_first:1/H0,neff_last:1/H1,
  shock_scale:scale==="island"?"between_island":"between_monitored_components_across_5_islands",
  assumed_pairwise_shock_correlation:rho,
  hypothetical_variance_ratio:z,hypothetical_sd_ratio:Math.sqrt(z)});
}
if(rows.length!==42)throw new Error("shock sensitivity rows");
const climate=parseCSV(source.climate).filter(r=>
 ["LITC","BISC","DAMO","PCHA"].includes(r.site_id));
if(climate.length!==16)throw new Error("CMIP6 neighboring place support");
const mapped=climate.map(r=>({
 experiment:r.experiment,period:r.period,site_id:r.site_id,
 location_id:r.location_id,fingerprint:r.marine_fingerprint,
 projected_SIC_change_pp:Number(r.siconc_change_mean_pp),
 maximum_model_ocean_cell_centre_distance_km:Number(r.marine_max_model_cell_distance_km)
}));
for(const exp of ["ssp245","ssp585"])for(const period of ["2041-2060","2081-2100"]){
 const d=mapped.filter(r=>r.experiment===exp&&r.period===period);
 if(new Set(d.map(x=>x.fingerprint)).size!==1||
    new Set(d.map(x=>x.projected_SIC_change_pp)).size!==1)
  throw new Error("Near-Palmer modeled sea ice not shared");
}
const outputs={
 "palmer_region_endpoints.csv":csv(yrs),
 "shock_correlation_sensitivity.csv":csv(rows),
 "nearby_climate_grid_support.csv":csv(mapped)
};
for(const [name,text] of Object.entries(outputs)){
 const existing=readFileSync(join(base,name),"utf8");
 if(existing!==text)throw new Error("Committed derived numeric result mismatch: "+name);
}
console.log(JSON.stringify({
 five_island_H_island_variance_ratio:yrs[1].H_island/yrs[0].H_island,
 five_island_H_colony_variance_ratio:yrs[1].H_component/yrs[0].H_component,
 scenario_sensitivity_rows:rows.length,climate_support_rows:mapped.length,
 validated:true
},null,2));
