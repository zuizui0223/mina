// Rebuild geographic link and conditional sign audit. Node >=20; no third-party packages.
// Usage: node research/climate-penguin/work/future_direction_identifiability_v1/build.mjs [outputs_root] [output_dir]
import {readFileSync,writeFileSync,mkdirSync} from "node:fs";
import {resolve,join} from "node:path";
import {createHash} from "node:crypto";
function parseCSV(s){
  const rec=[];let row=[],field="",q=false;
  for(let i=0;i<s.length;i++){const c=s[i];if(q){if(c==='"'&&s[i+1]==='"'){field+='"';i++}else if(c==='"')q=false;else field+=c;}
    else if(c==='"')q=true;else if(c===','){row.push(field);field=""}
    else if(c==='\n'){row.push(field.replace(/\r$/,""));if(row.length>1)rec.push(row);row=[];field=""}else field+=c;}
  if(field||row.length){row.push(field);rec.push(row)}
  if(q)throw Error("unclosed quote");
  const columns=rec.shift();return rec.map((cells,i)=>{if(cells.length!==columns.length)throw Error("CSV source col count: "+i);return Object.fromEntries(columns.map((c,j)=>[c,cells[j]]))});
}
function csvEncode(rows,cols){
 const val=x=>{const s=x==null?"":String(x);return /[\",\n\r]/.test(s)?'"'+s.replaceAll('"','""')+'"':s;};
 return cols.join(",")+"\n"+rows.map(r=>cols.map(c=>val(r[c])).join(",")).join("\n")+"\n";
}
function haversine(a,b){
 const rad=Math.PI/180,lat1=Number(a.latitude)*rad,lat2=Number(b.latitude)*rad;
 const dlat=lat2-lat1,dlon=(Number(b.longitude)-Number(a.longitude))*rad;
 return 12742.0176*Math.asin(Math.min(1,Math.sqrt(Math.max(0,Math.sin(dlat/2)**2+Math.cos(lat1)*Math.cos(lat2)*Math.sin(dlon/2)**2))));
}
function buildDirectionalAudit(source,sourceSha){
 const behavior=parseCSV(source.behavior),land=parseCSV(source.land),two=parseCSV(source.two),four=parseCSV(source.four);
 if(behavior.length!==288||land.length!==232||two.length!==3936||four.length!==3936)throw Error("data cohorts changed "+[behavior.length,land.length,two.length,four.length]);
 const spp={ADPE:"Adelie",CHPE:"Chinstrap",GEPE:"Gentoo"};
 const models=["ACCESS-CM2","BCC-CSM2-MR","CESM2"],modes=["site","site_year"],experiments=["ssp245","ssp585"],periods=["2041-2060","2081-2100"];
 const base=land.filter(x=>x.experiment==="ssp245"&&x.period==="2041-2060");
 if(base.length!==58||new Set(base.map(x=>x.site_id+"|"+x.species_id)).size!==58)throw Error("base identity inconsistent");
 const byCamera=new Map();
 for(const x of behavior){
  const sp=spp[Object.keys(spp).find(k=>spp[k]===x.species)];
  if(!sp)throw Error("unknown camera species "+x.species);
  const k=x.species+"|"+x.cam;const a=byCamera.get(k)||[];a.push(x);byCamera.set(k,a);
 }
 const receipts=[],eligible=[];
 for(const x of base){
   const cams=byCamera.get(spp[x.species_id]+"|"+x.site_id)||[];
   const distances=cams.map(c=>haversine(x,{latitude:c.lat,longitude:c.long}));
   const largest=distances.length?Math.max(...distances):null,smallest=distances.length?Math.min(...distances):null;
   const status=!cams.length?"no_camera_same_species_site_code":largest>2?"some_camera_source_coordinates_over_2km":"all_camera_source_coordinates_within_2km";
   const r={
     site_id:x.site_id,species_id:x.species_id,region:x.region,static_breeding_latitude:x.latitude,static_breeding_longitude:x.longitude,
     camera_rows:cams.length,camera_dist_min_km:smallest??"",camera_dist_max_km:largest??"",
     camera_source_location_ids:[...new Set(cams.map(y=>y.location_id))].sort().join(";"),
     source_climate_location_id:x.location_id,source_climate_distance_km:x.source_to_climate_distance_km,
     camera_join_status:status
   };
   receipts.push(r);
   if(status==="all_camera_source_coordinates_within_2km")eligible.push({original:x,cameraRows:cams});
 }
 if(eligible.length!==19)throw Error("camera eligible cohort changed "+eligible.length);
 const toKey=x=>[x.scope,x.species,x.cam,x.source_id,x.member_id,x.experiment_id,x.period,x.mode,x.transform].join("|");
 const twoMap=new Map(two.map(x=>[toKey(x),x])),fourMap=new Map(four.map(x=>[toKey(x),x]));
 if(twoMap.size!==3936||fourMap.size!==3936)throw Error("duplicate two/four model record");
 const paired=[];
 const landMap=new Map(land.map(x=>[[x.experiment,x.period,x.site_id,x.species_id].join("|"),x]));
 for(const item of eligible){
  const r=item.original;
  for(const ss of experiments)for(const period of periods)for(const model of models)for(const mode of modes){
    const key=["all_source_labels",spp[r.species_id],r.site_id,model,model==="CESM2"?"r4i1p1f1":"r1i1p1f1",ss,period,mode,"bounded"].join("|");
    const x=twoMap.get(key),y=fourMap.get(key);
    if(!x||!y)throw Error("paired model key missing "+key);
    if(x.physical_ice!=="True"||y.physical_ice!=="True")throw Error("bounded climate not physical "+key);
    const landRow=landMap.get([ss,period,r.site_id,r.species_id].join("|"));if(!landRow)throw Error("land key missing");
    for(const [env,z] of [["air_ice",x],["air_ice_salt_water",y]]){
      const shift=Number(z.index_shift);if(!Number.isFinite(shift))throw Error("invalid shift "+key);
      paired.push({
        site_id:r.site_id,species_id:r.species_id,region:r.region,
        experiment:ss,period,climate_model:model,climate_member:z.member_id,
        adjustment:mode,environment_specification:env,
        conditional_settlement_shift_days:shift,
        four_environment_hull_outside:env==="air_ice_salt_water"?(y.outside_four_variable_hull==="True"?1:0):"",
        observed_marginal_range_outside:env==="air_ice_salt_water"?(y.outside_any_species_marginal_range==="True"?1:0):(x.outside_air_ice_marginal_range==="True"?1:0),
        marine_fingerprint:landRow.marine_fingerprint,
        all_three_marine_model_cells_within_50km:landRow.all_three_marine_model_cell_centres_within_50km,
        three_model_ice_loss_ge10pp:landRow.siconc_loss_ge10pp_3of3
      });
    }
  }
 }
 if(paired.length!==912)throw Error("expected 912 conditional values; saw "+paired.length);
 paired.sort((a,b)=>a.experiment.localeCompare(b.experiment)||a.period.localeCompare(b.period)||a.site_id.localeCompare(b.site_id)||a.species_id.localeCompare(b.species_id)||a.climate_model.localeCompare(b.climate_model)||a.adjustment.localeCompare(b.adjustment)||a.environment_specification.localeCompare(b.environment_specification));
 const grouped=new Map();
 for(const x of paired){const k=[x.experiment,x.period,x.site_id,x.species_id].join("|");const ar=grouped.get(k)||[];ar.push(x);grouped.set(k,ar);}
 const output=[];
 for(const [k,ar] of grouped){
  if(ar.length!==12)throw Error("incomplete scenario panel "+k);
  const vals=ar.map(x=>x.conditional_settlement_shift_days),up=vals.filter(x=>x>0),down=vals.filter(x=>x<0),zeros=vals.filter(x=>x===0);
  const ref=landMap.get([ar[0].experiment,ar[0].period,ar[0].site_id,ar[0].species_id].join("|"));
  const fourR=ar.filter(x=>x.environment_specification==="air_ice_salt_water");
  if(fourR.length!==6)throw Error("hull subpanel incomplete "+k);
  output.push({
    experiment:ar[0].experiment,period:ar[0].period,site_id:ar[0].site_id,species_id:ar[0].species_id,region:ar[0].region,
    latitude:ref.latitude,longitude:ref.longitude,marine_fingerprint:ref.marine_fingerprint,
    three_model_ice_loss_ge10pp:ref.siconc_loss_ge10pp_3of3,all_three_marine_model_cells_within_50km:ref.all_three_marine_model_cell_centres_within_50km,
    observed_year_count:ref.historical_observed_seasons,observed_vegetation_detection_status:ref.vegetation_detection_status,
    specification_values:ar.length,number_negative:down.length,number_positive:up.length,number_zero:zeros.length,
    min_shift_days:Math.min(...vals),max_shift_days:Math.max(...vals),
    all_specifications_same_sign:up.length===ar.length||down.length===ar.length?1:0,
    model_structure_direction_mixed:up.length>0&&down.length>0?1:0,
    four_environment_hull_outside_of_six:fourR.filter(x=>x.four_environment_hull_outside===1).length,
    any_four_environment_hull_outside:fourR.some(x=>x.four_environment_hull_outside===1)?1:0
  });
 }
 output.sort((a,b)=>a.experiment.localeCompare(b.experiment)||a.period.localeCompare(b.period)||a.site_id.localeCompare(b.site_id)||a.species_id.localeCompare(b.species_id));
 if(output.length!==76)throw Error("expected 76 site scenario summaries");
 const scenarioStats=[];
 for(const ss of experiments)for(const period of periods){
  const a=output.filter(x=>x.experiment===ss&&x.period===period);
  scenarioStats.push({
    experiment:ss,period,site_species:a.length,distinct_site_ids:new Set(a.map(x=>x.site_id)).size,
    full_12_specifications:a.filter(x=>x.specification_values===12).length,
    signs_mixed:a.filter(x=>x.model_structure_direction_mixed===1).length,
    all_same_sign:a.filter(x=>x.all_specifications_same_sign===1).length,
    at_least_one_four_environment_hull_outside:a.filter(x=>x.any_four_environment_hull_outside===1).length,
    six_of_six_four_environment_hull_outside:a.filter(x=>x.four_environment_hull_outside_of_six===6).length,
    three_model_ice_loss_ge10pp:a.filter(x=>x.three_model_ice_loss_ge10pp==="1").length,
    strong_ice_loss_and_sign_robust:a.filter(x=>x.three_model_ice_loss_ge10pp==="1"&&x.all_specifications_same_sign===1).length
  });
 }
 const meta={
  status:"all_future_settlement_directions_specification_dependent_in_strict_land_camera_cohort_not_calibrated_forecast",
  source_git_blob_sha:sourceSha,
  counts:{camera_raw_rows:behavior.length,baseline_land_species_rows:base.length,two_environment_rows:two.length,four_environment_rows:four.length,location_camera_receipts:receipts.length,eligible_matched_site_species:eligible.length,excluded_no_same_code_camera:receipts.filter(x=>x.camera_join_status==="no_camera_same_species_site_code").length,excluded_camera_geography_gt2km:receipts.filter(x=>x.camera_join_status==="some_camera_source_coordinates_over_2km").length,paired_model_variant_rows:paired.length,scenario_site_species_rows:output.length},
  scenarios:scenarioStats,
  scope:"Same camera species and site code with ALL source camera coordinates within 2 km of static breeding-source point; all_source_labels, bounded ice, 3 climate models, site or site_year fixed effects, two- and four-variable models.",
  interpretation:"Conditional scenario shifts are on day scale, not validated absolute arrival dates or future nest/vegetation predictions. Signs are not probabilities. 4D hull outside is a diagnostic of empirical support.",
  caveat:"Model variants share the same source birds and climate models, so 12 variants are NOT independent biological replicates. Seasonal and camera-date alignment, coast/land precision, prey observations, and independent out-of-time response calibration remain unresolved."
 };
 const numericGeo=new Set(["three_model_ice_loss_ge10pp","all_three_marine_model_cells_within_50km","observed_year_count","specification_values","number_negative","number_positive","number_zero","min_shift_days","max_shift_days","all_specifications_same_sign","model_structure_direction_mixed","four_environment_hull_outside_of_six","any_four_environment_hull_outside"]);
 const geo={type:"FeatureCollection",name:"Conditional settlement response direction uncertainty, NOT calibrated forecast",features:output.map((x,i)=>({type:"Feature",id:i+1,geometry:{type:"Point",coordinates:[Number(x.longitude),Number(x.latitude)]},properties:Object.fromEntries(Object.entries(x).filter(([k])=>!["longitude","latitude"].includes(k)).map(([k,v])=>[k,numericGeo.has(k)?Number(v):v]))}))};
 return {meta,files:{
  "camera_geography_receipt.csv":csvEncode(receipts,Object.keys(receipts[0])),
  "paired_variant_shifts.csv":csvEncode(paired,Object.keys(paired[0])),
  "site_scenario_direction_identifiability.csv":csvEncode(output,Object.keys(output[0])),
  "site_scenario_direction_identifiability.geojson":JSON.stringify(geo)+"\n",
  "summary.json":JSON.stringify(meta,null,2)+"\n"
 }};
}
const base=resolve(process.argv[2]||"research/climate-penguin/outputs");
const outDir=resolve(process.argv[3]||"research/climate-penguin/outputs/future_direction_identifiability_v1");
const paths={behavior:"climate_penguin/behavior_ocean_join.csv",land:"land_marine_colocation_v1/matched_site_species_scenarios.csv",two:"conditional_response_v1/site_index_shifts.csv",four:"four_environment_scenarios_v1/site_components.csv"};
const expectedGitBlobs={
  "behavior": "31373115b5f1b46d990952e69c4a705da3e00827",
  "land": "5cc45d5bddeb6a6a4c89880ff38c4cff290f7783",
  "two": "6288feab14ea84719932c0760aca2f4860a5065c",
  "four": "f1e7cecd958e1ec011489ad279782b9d1327aa5f"
};
const src={};
for(const [name,path] of Object.entries(paths)){
 const bytes=readFileSync(join(base,path));
 const sha=createHash("sha1").update(Buffer.concat([Buffer.from("blob "+bytes.length+"\0"),bytes])).digest("hex");
 if(sha!==expectedGitBlobs[name])throw Error("source Git blob sha mismatch: "+name+" / "+sha);
 src[name]=bytes.toString("utf8");
}
const r=buildDirectionalAudit(src,expectedGitBlobs);
mkdirSync(outDir,{recursive:true});
for(const [p,c] of Object.entries(r.files))writeFileSync(join(outDir,p),c);
console.log(JSON.stringify(r.meta.scenarios,null,2));
