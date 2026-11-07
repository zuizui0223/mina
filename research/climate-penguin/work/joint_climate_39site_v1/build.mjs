// 39 source Adélie breeding site codes: joint future CMIP6 physical climate only.
import {readFileSync,writeFileSync,mkdirSync} from "node:fs";
import {resolve,join} from "node:path";
import {createHash} from "node:crypto";
const root=resolve("research/climate-penguin/outputs"),out=join(root,"joint_climate_39site_v1");
const sources={
 climate:["cmip6_projection_v1/site_model_changes.csv","b383ef1cc3b0807b0bd010ca0e825937ab83ce97"],
 history:["historical_ice_breeding_transfer_v1/adeli_39site_historical_climate_growth.csv","db58938630e80d22ba445600ce1ad3f554c452e2"],
 counts:["comparison_audit/mapppd_unambiguous_site_seasons.csv","fc134e364cf38699fa7611d7dee5fbbbcb370c0a"]
};
const expected=JSON.parse(readFileSync(join(out,"expected_receipt.json"),"utf8"));
function parse(s){let rows=[],r=[],v="",q=false;for(let i=0;i<s.length;i++){const c=s[i];
 if(q){if(c==='"'&&s[i+1]==='"'){v+='"';i++}else if(c==='"')q=false;else v+=c}
 else if(c==='"')q=true;else if(c===','){r.push(v);v=""}else if(c==='\n'){r.push(v.replace(/\r$/,""));if(r.length>1)rows.push(r);r=[];v=""}else v+=c}
 if(r.length||v){r.push(v);rows.push(r)}if(q||rows.length<2)throw Error("Invalid CSV");const h=rows.shift();
 return rows.map((x,i)=>{if(x.length!==h.length)throw Error("Wrong columns "+i);return Object.fromEntries(h.map((k,j)=>[k,x[j]]))})}
const raw={};for(const [k,[p,sha]] of Object.entries(sources)){
 const b=readFileSync(join(root,p)),got=createHash("sha1").update(Buffer.from("blob "+b.length+"\0")).update(b).digest("hex");
 if(got!==sha||expected.blobs[k]!==sha)throw Error("Input Git blob changed "+k);
 raw[k]=parse(b.toString("utf8"))}
if(raw.climate.length!==3816||raw.history.length!==39||raw.counts.length!==2999)throw Error("Original source shape drift");
const S=new Set(raw.history.map(x=>x.site_id)),by=new Map();
for(const x of raw.counts){if(!S.has(x.site_id)||x.species_id!=="ADPE"||x.count===""||+x.count<0)continue;
 let arr=by.get(x.site_id)||[];arr.push(x);by.set(x.site_id,arr)}
const sites=raw.history.map(x=>{const z=(by.get(x.site_id)||[]).sort((a,b)=>+b.season-+a.season)[0];
 if(!z)throw Error("Missing source count "+x.site_id);
 return{id:x.site_id,region:x.region,count:+z.count,year:+z.season}});
const sum=a=>a.reduce((s,x)=>s+x,0),weight=a=>sum(a.map(x=>x.count)),N=weight(sites);
if(S.size!==39||N!==1074279)throw Error("Original source site/census drift");
const models=["ACCESS-CM2","BCC-CSM2-MR","CESM2"],map=new Map();
for(const x of raw.climate){if(!S.has(x.site_id)||x.cohort!=="macro_40")continue;
 const k=[x.source_id,x.experiment_id,x.period,x.site_id].join("|"),v=map.get(k)||{};
 if(v[x.variable_id]||!["tas","siconc","sos"].includes(x.variable_id))throw Error("Original future component duplicate");
 v[x.variable_id]={delta:+x.change,unit:x.change_units,cell:x.grid_cell_id,dist:+x.distance_km};
 map.set(k,v)}
if(map.size!==468)throw Error("Future model keys incomplete");
const pct=a=>100*weight(a)/N,source=[],combined=[],summ=[],sensitivity=[],fingerprints=[];
for(const scenario of ["ssp245","ssp585"])for(const period of ["2041-2060","2081-2100"]){
 const group=[];
 for(const s of sites){
  const m=models.map(model=>{const z=map.get([model,scenario,period,s.id].join("|"));
   if(!z||!z.tas||!z.siconc||!z.sos)throw Error("Future model triplet incomplete");
   if(z.tas.unit!=="degC"||z.siconc.unit!=="percentage_points"||z.sos.unit!=="0.001")throw Error("CMIP source units drift");
   const r={scenario,period,model,site_id:s.id,region:s.region,latest_recorded_count:s.count,
    air_warming_C:z.tas.delta,seaice_change_pp:z.siconc.delta,surface_salinity_change:z.sos.delta,
    ice_cell:z.siconc.cell,salt_cell:z.sos.cell,ice_grid_km:z.siconc.dist,salt_grid_km:z.sos.dist};
   source.push(r);return r});
  const min=k=>Math.min(...m.map(x=>x[k])),max=k=>Math.max(...m.map(x=>x[k]));
  const ice=max("seaice_change_pp")<0,fresh=max("surface_salinity_change")<0,warm=min("air_warming_C")>0;
  const r={scenario,period,site_id:s.id,region:s.region,count:s.count,count_year:s.year,
   min_3model_temp_C:min("air_warming_C"),max_3model_temp_C:max("air_warming_C"),
   min_3model_ice_pp:min("seaice_change_pp"),max_3model_ice_pp:max("seaice_change_pp"),
   min_3model_salinity:min("surface_salinity_change"),max_3model_salinity:max("surface_salinity_change"),
   all3_warming:warm,all3_seaice_retreat:ice,all3_freshening:fresh,
   joint_retreat_freshening:ice&&fresh,freshening_without_consistent_retreat:fresh&&!ice,
   retreat_without_consistent_freshening:ice&&!fresh,
   coastal_50km_all3:m.every(x=>x.ice_grid_km<=50&&x.salt_grid_km<=50),
   fingerprint:m.map(x=>x.ice_cell+"#"+x.salt_cell).join("||"),
   crozier:s.id==="CRZE"||s.id==="CRZW"};
  combined.push(r);group.push(r)
 }
 const aggregate=(name,filter)=>{let arr=group.filter(filter),without=arr.filter(x=>!x.crozier);
  return{scenario,period,name,site_codes:arr.length,site_share_pct:100*arr.length/39,
   census_weight:weight(arr),census_pct:pct(arr),marine_fingerprints:new Set(arr.map(x=>x.fingerprint)).size,
   Crozier_count_pct:pct(arr.filter(x=>x.crozier)),
   excluding_Crozier_reweighted_pct:100*weight(without)/831598,
   supported_50km_site_n:arr.filter(x=>x.coastal_50km_all3).length,
   supported_50km_count_pct:pct(arr.filter(x=>x.coastal_50km_all3)),
   site_ids:arr.map(x=>x.site_id).join(";")}}
 summ.push(...[
  aggregate("warming",x=>x.all3_warming),
  aggregate("seaice_retreat",x=>x.all3_seaice_retreat),
  aggregate("surface_freshening",x=>x.all3_freshening),
  aggregate("warming_retreat_freshening",x=>x.all3_warming&&x.joint_retreat_freshening),
  aggregate("freshening_no_common_retreat",x=>x.freshening_without_consistent_retreat),
  aggregate("retreat_no_common_freshening",x=>x.retreat_without_consistent_freshening),
  aggregate("ice5_and_freshening",x=>x.max_3model_ice_pp<=-5&&x.all3_freshening),
  aggregate("ice5_salt005_tas2",x=>x.max_3model_ice_pp<=-5&&x.max_3model_salinity<=-0.05&&x.min_3model_temp_C>=2)]);
 const fm=new Map();for(const x of group){const arr=fm.get(x.fingerprint)||[];arr.push(x);fm.set(x.fingerprint,arr)}
 for(const [f,arr] of fm)fingerprints.push({scenario,period,fingerprint:f,n_site_codes:arr.length,count_pct:pct(arr),
  joint_count_sites:arr.filter(x=>x.joint_retreat_freshening).length,site_ids:arr.map(x=>x.site_id).join(";")});
 for(const ice of [0,2,5,10])for(const salt of [0,0.05,0.1])for(const tas of [0,2]){
  const matched=group.filter(x=>x.max_3model_ice_pp<=-ice&&x.max_3model_salinity<=-salt&&x.min_3model_temp_C>=tas);
  sensitivity.push({scenario,period,ice_decline_min_pp:ice,salinity_decline_min_model_units:salt,
   air_temperature_rise_min_C:tas,site_codes:matched.length,count_pct:pct(matched),
   crozier_count_pct:pct(matched.filter(x=>x.crozier)),site_ids:matched.map(x=>x.site_id).join(";")})}
}
if(source.length!==468||combined.length!==156||summ.length!==32||sensitivity.length!==96)throw Error("Source cartesian grouping drift");
const result=n=>summ.find(x=>x.scenario==="ssp585"&&x.period==="2081-2100"&&x.name===n);
const facts={site_codes:39,model_rows:source.length,site_scenario_rows:combined.length,census_total:N,
 late_ice_n:result("seaice_retreat").site_codes,late_fresh_n:result("surface_freshening").site_codes,
 late_joint_n:result("warming_retreat_freshening").site_codes,
 late_joint_pct:result("warming_retreat_freshening").census_pct,
 late_fresh_no_ice_n:result("freshening_no_common_retreat").site_codes,
 late_fresh_no_ice_pct:result("freshening_no_common_retreat").census_pct,
 late_ice5_fresh_n:result("ice5_and_freshening").site_codes,
 late_ice5_fresh_pct:result("ice5_and_freshening").census_pct,
 late_strong_n:result("ice5_salt005_tas2").site_codes,
 late_strong_pct:result("ice5_salt005_tas2").census_pct};
if(process.argv.includes("--check-receipt"))for(const [k,v] of Object.entries(expected.values)){
 if(!Number.isFinite(facts[k])||Math.abs(facts[k]-v)>1e-8)throw Error("Receipt mismatch "+k+": "+facts[k]+" vs "+v)}
function save(path,arr){let keys=Object.keys(arr[0]),enc=x=>{let s=x===undefined||x===null?"":String(x);
 return /[,"\n\r]/.test(s)?'"'+s.replaceAll('"','""')+'"':s};
 writeFileSync(join(out,path),keys.join(",")+"\n"+arr.map(x=>keys.map(k=>enc(x[k])).join(",")).join("\n")+"\n")}
mkdirSync(out,{recursive:true});
save("original_site_model_joint_conditions.csv",source);save("site_three_model_compound_consensus.csv",combined);
save("scenario_joint_physical_summary.csv",summ);save("magnitude_sensitivity.csv",sensitivity);
save("marine_fingerprint_summary.csv",fingerprints);
writeFileSync(join(out,"result.json"),JSON.stringify({facts,groups:summ,
 interpretation:"CMIP6 three variable physical overlap. Not a forecast of penguin nests, recruitment, survival, vegetation or salinity selection. tas is air temperature not SST; sos is modeled sea-surface salinity in source units 0.001. Latest original mixed census years 2001–2025 are fixed spatial weights, not contemporary population.",model_members:3},null,2)+"\n");
console.log("CMIP6 JOINT ADPE PHYSICAL RESULT "+JSON.stringify({facts,groups:summ,validated:process.argv.includes("--check-receipt")}));
