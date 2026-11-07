// Reproduce Antarctic 40-site spatial coherence of observed 1991-2020 sea ice.
// Node.js >=20. Run from repository root:
// node research/climate-penguin/work/sic_spatial_coherence_macro40_v1/build.mjs [outputs_root] [output_dir]
import {readFileSync,writeFileSync,mkdirSync} from "node:fs";
import {createHash} from "node:crypto";
import {resolve,join} from "node:path";

function parseCSV(s){
 const out=[];let row=[],field="",q=false;
 for(let i=0;i<s.length;i++){
  const c=s[i];if(q){if(c==='"'&&s[i+1]==='"'){field+='"';i++}else if(c==='"')q=false;else field+=c}
  else if(c==='"')q=true;else if(c===','){row.push(field);field=""}
  else if(c==='\n'){row.push(field.replace(/\r$/,""));if(row.length>1)out.push(row);row=[];field=""}else field+=c;
 }
 if(field||row.length){row.push(field);out.push(row)}
 if(q)throw Error("bad quote");
 const h=out.shift();return out.map((x,i)=>{if(x.length!==h.length)throw Error("bad CSV width "+i);return Object.fromEntries(h.map((name,j)=>[name,x[j]]))});
}
function csvEncode(rows,cols){
 const escape=v=>{const s=v==null?"":String(v);return /[",\r\n]/.test(s)?'"'+s.replaceAll('"','""')+'"':s;};
 return cols.join(",")+"\n"+rows.map(row=>cols.map(k=>escape(row[k])).join(",")).join("\n")+"\n";
}
function macroDistanceCoherence(data,provenance){
 const raw=parseCSV(data.sic),positions=parseCSV(data.positions),records=positions.filter(x=>x.cohort==="macro_40").sort((a,b)=>a.site_id.localeCompare(b.site_id));
 if(raw.length!==9600||positions.length!==106||records.length!==40)throw Error("original support changed");
 const n=v=>{if(v==null||v===""||!Number.isFinite(Number(v)))throw Error("invalid number "+v);return Number(v)};
 const avg=v=>v.reduce((s,x)=>s+x,0)/v.length;
 const median=v=>{const a=v.slice().sort((a,b)=>a-b),j=Math.floor(a.length/2);return a.length%2?a[j]:(a[j-1]+a[j])/2};
 const yearly=Array.from({length:30},(_,i)=>String(1991+i));
 const climateMap=new Map(raw.map(x=>[[x.site_id,x.year,x.month,x.inner_km].join("|"),x]));
 if(climateMap.size!==9600)throw Error("duplicate observed sea ice");
 const ll=(a,b)=>{
   const rad=Math.PI/180,la=n(a.latitude)*rad,lb=n(b.latitude)*rad,dl=lb-la,dlo=(n(b.longitude)-n(a.longitude))*rad;
   const z=Math.sin(dl/2)**2+Math.cos(la)*Math.cos(lb)*Math.sin(dlo/2)**2;
   return 12742.0176*Math.asin(Math.min(1,Math.sqrt(z)));
 };
 const cc=(a,b)=>{
   if(a.length!==30||b.length!==30)throw Error("not 30 years");
   const x=avg(a),y=avg(b),A=a.map(v=>v-x),B=b.map(v=>v-y);
   const cov=A.reduce((s,z,i)=>s+z*B[i],0),sa=A.reduce((s,z)=>s+z*z,0),sb=B.reduce((s,z)=>s+z*z,0);
   if(!(sa>0&&sb>0))throw Error("constant source series");
   return cov/Math.sqrt(sa*sb);
 };
 const periods=[["0–50 km",0,50],["50–100 km",50,100],["100–250 km",100,250],["250–500 km",250,500],["500–1000 km",500,1000],["≥1000 km",1000,40000]];
 const pairs=[];
 const group=(a,fn)=>{const m=new Map;for(const x of a){const key=fn(x),list=m.get(key)||[];list.push(x);m.set(key,list)}return m};
 for(const band of [0,100])for(const month of [8,9,10,11]){
   const siteMatrix=new Map();
   for(const site of records){
     const series=yearly.map(y=>{
      const k=[site.site_id,y,month,band].join("|"),row=climateMap.get(k);
      if(!row||row.complete_month!=="True"||n(row.days)!==n(row.expected_days)||n(row.supported_days)!==n(row.days))throw Error("site year noncomplete "+k);
      const val=n(row.sic_mean);if(val<0||val>100)throw Error("SIC out of bounds "+k);
      return val;
     });
     siteMatrix.set(site.site_id,series);
   }
   for(let i=0;i<records.length;i++)for(let j=i+1;j<records.length;j++){
     const a=records[i],b=records[j],distance=ll(a,b),rho=cc(siteMatrix.get(a.site_id),siteMatrix.get(b.site_id));
     const interval=periods.find(p=>distance>=p[1]&&distance<p[2]);
     if(!interval)throw Error("distance bin out of domain");
     pairs.push({month,inner_km:band,site_1:a.site_id,site_2:b.site_id,
       geographic_distance_km:distance,annual_SIC_Pearson_r:rho,distance_bin:interval[0]});
   }
 }
 if(pairs.length!==6240)throw Error("pair output incomplete");
 const strata=group(pairs,x=>[x.month,x.inner_km,x.distance_bin].join("|")),binRows=[],leaveOne=[];
 for(const month of [8,9,10,11])for(const band of [0,100])for(const [label,low,hi] of periods){
  const key=[month,band,label].join("|"),v=strata.get(key);
  if(!v||v.length===0)throw Error("empty distance band "+key);
  const cor=v.map(x=>x.annual_SIC_Pearson_r);
  const orderedDistances=v.map(x=>x.geographic_distance_km);
  const row={month,inner_km:band,distance_bin:label,lower_distance_km:low,upper_distance_km_exclusive:hi,
    station_pair_n:v.length,unique_stations_represented:new Set(v.flatMap(x=>[x.site_1,x.site_2])).size,
    median_distance_km:median(orderedDistances),median_annual_SIC_Pearson_r:median(cor),
    mean_annual_SIC_Pearson_r:avg(cor),r_min:Math.min(...cor),r_max:Math.max(...cor)};
  binRows.push(row);
  for(const site of records){
   const remainder=v.filter(x=>x.site_1!==site.site_id&&x.site_2!==site.site_id);
   if(!remainder.length)throw Error("leave out station loses all pair "+key);
   leaveOne.push({month,inner_km:band,distance_bin:label,removed_site_id:site.site_id,
    pairs_retained:remainder.length,median_r_after_leaving_site_out:median(remainder.map(x=>x.annual_SIC_Pearson_r))});
  }
 }
 if(binRows.length!==48||leaveOne.length!==1920)throw Error("bin support wrong");
 const diagonal=[];
 for(const month of [8,9,10,11]){
  for(const p of periods){
   const nRow=binRows.find(x=>x.month===month&&x.inner_km===0&&x.distance_bin===p[0]);
   const fRow=binRows.find(x=>x.month===month&&x.inner_km===100&&x.distance_bin===p[0]);
   if(!nRow||!fRow||nRow.station_pair_n!==fRow.station_pair_n)throw Error("distance pair mismatch");
   diagonal.push({month,distance_bin:p[0],station_pair_n:nRow.station_pair_n,
    near_0_100km_median_annual_r:nRow.median_annual_SIC_Pearson_r,
    offshore_100_500km_median_annual_r:fRow.median_annual_SIC_Pearson_r,
    offshore_minus_near_median_r:fRow.median_annual_SIC_Pearson_r-nRow.median_annual_SIC_Pearson_r});
  }
 }
 const near=binRows.find(x=>x.month===9&&x.inner_km===0&&x.distance_bin==="0–50 km");
 const mid=binRows.find(x=>x.month===9&&x.inner_km===0&&x.distance_bin==="250–500 km");
 const far=binRows.find(x=>x.month===9&&x.inner_km===0&&x.distance_bin==="≥1000 km");
 const off=binRows.find(x=>x.month===9&&x.inner_km===100&&x.distance_bin==="250–500 km");
 if(Math.abs(near.median_annual_SIC_Pearson_r-.9912946729477736)>1e-12||
 Math.abs(mid.median_annual_SIC_Pearson_r-.3153535517541149)>1e-12||
 Math.abs(far.median_annual_SIC_Pearson_r-.011319142247277788)>1e-12||
 Math.abs(off.median_annual_SIC_Pearson_r-.7970395285026719)>1e-12)throw Error("fixed primary numerical anchor mismatch");
 const crossLeave=leaveOne.filter(x=>x.month===9&&x.inner_km===0&&x.distance_bin==="250–500 km");
 const sm={
   date:"2026-10-31",
   status:"verified_observed_ice_spatial_coherence_by_distance_not_independent_site_biology",
   source_git_blob_sha:provenance,
   primary_September_near:{
    r_lt50km:near.median_annual_SIC_Pearson_r,nPairs_lt50km:near.station_pair_n,
    r_250_500km:mid.median_annual_SIC_Pearson_r,nPairs_250_500km:mid.station_pair_n,
    r_ge1000km:far.median_annual_SIC_Pearson_r,nPairs_ge1000km:far.station_pair_n,
    SeptemberOffshore_250_500km:off.median_annual_SIC_Pearson_r,
    leave_one_out_range_r_250_500km:[Math.min(...crossLeave.map(x=>x.median_r_after_leaving_site_out)),Math.max(...crossLeave.map(x=>x.median_r_after_leaving_site_out))]
   },
   study_units:{sites:records.length,years:yearly.length,site_year_month_band_rows:raw.length,site_pairs_per_month_band:780,pair_scenarios:pairs.length,month_band_distance_bin_rows:binRows.length,all_site_leave_one_out_rows:leaveOne.length,cross_scale_bin_rows:diagonal.length},
   bins:periods.map(x=>x[0]),
   interpretation:"Geographic coherence of source-observed sea-ice averages depends on distance and offshore buffer size. This does not identify a causal climate-population relationship or a unique biological climate refuge.",
   restrictions:[
    "40 fixed macro Pygoscelis sampling sites are not a uniformly random survey of Antarctic coastal sea ice.",
    "The 780 pairs reuse 40 original sites and must not be treated as independent statistical units.",
    "SIC marine buffers overlap at short distances; offshore 100-500km averages intentionally smooth variation and mechanically increase correlation.",
    "Temporal correlations over 30 years may reflect shared trends and regional regimes; no validated process-specific coherence length.",
    "No colony/subcolony-specific marine or feeding-track ice data, and no sea-ice effects on breeding counts estimated."
   ]
 };
 return {meta:sm,files:{
 "macro40_site_coordinates.csv":csvEncode(records,["site_id","latitude","longitude","cohort","location_id"]),
 "pairwise_30year_ice_correlations.csv":csvEncode(pairs,Object.keys(pairs[0])),
 "month_band_distance_bins.csv":csvEncode(binRows,Object.keys(binRows[0])),
 "paired_near_offshore_distance_bins.csv":csvEncode(diagonal,Object.keys(diagonal[0])),
 "leave_one_site_out_median_correlations.csv":csvEncode(leaveOne,Object.keys(leaveOne[0])),
 "summary.json":JSON.stringify(sm,null,2)+"\n"
 }};
}
const root=resolve(process.argv[2]||"research/climate-penguin/outputs");
const out=resolve(process.argv[3]||"research/climate-penguin/outputs/sic_spatial_coherence_macro40_v1");
const files={sic:"climate_penguin/macro_monthly_seaice_1991_2020.csv",positions:"climate_penguin/daily_ice_locations.csv"};
const pinned={
  "sic": "4fcea71c2d8b1069b6ad143f6522061ed434daf5",
  "positions": "1c5214ab355d3d2e19bc33e5de4693fa21f38731"
};
const input={};
for(const [key,file] of Object.entries(files)){
 const bytes=readFileSync(join(root,file));
 const sha=createHash("sha1").update(Buffer.concat([Buffer.from("blob "+bytes.length+"\0"),bytes])).digest("hex");
 if(sha!==pinned[key])throw new Error("Git blob source changed: "+file+" expected "+pinned[key]+" got "+sha);
 input[key]=bytes.toString("utf8");
}
const result=macroDistanceCoherence(input,pinned);
mkdirSync(out,{recursive:true});
for(const [name,content] of Object.entries(result.files))writeFileSync(join(out,name),content);
console.log(JSON.stringify(result.meta.primary_September_near,null,2));
