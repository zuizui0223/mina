// Source-pinned observational support audit: does annual SIC cofluctuation link to ADPE count growth?
// No ecological effect test: identify pairwise reuse, strict count-month support and duplicate site/island codes.
import {readFileSync,writeFileSync,mkdirSync} from "node:fs";
import {resolve,join} from "node:path";
import {createHash} from "node:crypto";
const base=resolve("research/climate-penguin/outputs");
const out=join(base,"seaice_covariance_portfolio_v1");
const files={
 hist:["historical_ice_breeding_transfer_v1/adeli_39site_historical_climate_growth.csv","db58938630e80d22ba445600ce1ad3f554c452e2"],
 ice:["climate_penguin/macro_monthly_seaice_1991_2020.csv","4fcea71c2d8b1069b6ad143f6522061ed434daf5"],
 count:["comparison_audit/mapppd_unambiguous_site_seasons.csv","fc134e364cf38699fa7611d7dee5fbbbcb370c0a"],
 month:["climate_penguin/historical_count_interval_timing.csv","f1aa63a99eff97482dde9b1c680c19b36c1dada5"]
};
const exp=JSON.parse(readFileSync(join(out,"expected_breeding_sync_support.json"),"utf8"));
function parseCSV(s){
 const rows=[];let r=[],v="",q=false;
 for(let i=0;i<s.length;i++){
  const c=s[i];if(q){if(c==='"'&&s[i+1]==='"'){v+='"';i++}else if(c==='"')q=false;else v+=c}
  else if(c==='"')q=true;
  else if(c===','){r.push(v);v=""}
  else if(c==='\n'){r.push(v.replace(/\r$/,""));if(r.length>1)rows.push(r);r=[];v=""}
  else v+=c;
 }
 if(r.length||v){r.push(v);rows.push(r)}
 if(q||rows.length<2)throw Error("Invalid source CSV");
 const h=rows.shift();
 return rows.map((r,i)=>{if(r.length!==h.length)throw Error("Wrong CSV width "+i);return Object.fromEntries(h.map((k,j)=>[k,r[j]]))});
}
function toCSV(rows){
 if(!rows.length)throw Error("Empty output");
 const h=Object.keys(rows[0]);
 const q=v=>{const s=v===null||v===undefined?"":String(v);return /[,"\r\n]/.test(s)?'"'+s.replaceAll('"','""')+'"':s};
 return h.join(",")+"\n"+rows.map(x=>h.map(k=>q(x[k])).join(",")).join("\n")+"\n";
}
const D={};
for(const [k,[path,pin]]of Object.entries(files)){
 const bytes=readFileSync(join(base,path));
 const hash=createHash("sha1").update(Buffer.from("blob "+bytes.length+"\0")).update(bytes).digest("hex");
 if(hash!==pin||exp.source_git_blobs[k]!==hash)throw Error("Original source drift "+k+" "+hash);
 D[k]=parseCSV(bytes.toString("utf8"));
}
if(D.hist.length!==39||D.count.length!==2999||D.ice.length!==9600)
 throw Error("Original 39-site source cohort changed");
const H=new Map(D.hist.map(x=>[x.site_id,x]));
if(H.size!==39)throw Error("Duplicate historical site code");
const COUNTS=new Map(),TIMING=new Map(),ICE=new Map();
for(const r of D.count){
 if(!H.has(r.site_id)||r.species_id!=="ADPE"||r.method!==H.get(r.site_id).method||
 r.count===""||!Number.isFinite(+r.count)||+r.count<0||+r.season<1991||+r.season>2020)continue;
 const a=COUNTS.get(r.site_id)||[];a.push(r);COUNTS.set(r.site_id,a);
}
for(const r of D.month){
 const k=[r.site_id,r.start,r.end,r.method_start].join("|");
 if(TIMING.has(k))throw Error("Duplicate count-month audit "+k);
 TIMING.set(k,r);
}
for(const r of D.ice){
 if(!H.has(r.site_id)||r.inner_km!=="0"||![8,9,10,11].includes(+r.month))continue;
 if(r.complete_month!=="True")throw Error("Missing complete month");
 const k=r.site_id+"|"+r.year,a=ICE.get(k)||[];
 a.push(+r.sic_mean);ICE.set(k,a);
}
const mean=a=>a.reduce((s,x)=>s+x,0)/a.length;
const sum=a=>a.reduce((s,x)=>s+x,0);
const correlation=(a,b)=>{
 if(a.length!==b.length||a.length<3)throw Error("Insufficient pairing");
 const x=mean(a),y=mean(b),num=sum(a.map((v,i)=>(v-x)*(b[i]-y))),
 den=Math.sqrt(sum(a.map(v=>(v-x)**2))*sum(b.map(v=>(v-y)**2)));
 return den>0?num/den:null;
};
const original=[];
for(const [site,rs]of COUNTS){
 const sorted=rs.sort((a,b)=>+a.season-+b.season);
 for(let j=1;j<sorted.length;j++){
  const a=sorted[j-1],b=sorted[j],year=+b.season;
  if(year!==+a.season+1||+a.count<=0||+b.count<=0)continue;
  const month=TIMING.get([site,a.season,b.season,a.method].join("|"));
  const temp=ICE.get(site+"|"+year);
  if(!temp||temp.length!==4)throw Error("Missing original source sea ice for count interval");
  original.push({
   source_site_code:site,region:H.get(site).region,year,
   observed_log_count_change:Math.log(+b.count/+a.count),
   original_nearshore_SIC_AugNov_pct:mean(temp),
   both_original_count_months_after_November:month?.both_all_after_november==="True",
   original_count_same_method:true,
   count_timing_supported:!!month
  });
 }
}
if(original.length!==296||new Set(original.map(x=>x.source_site_code)).size!==32||
 original.filter(x=>x.both_original_count_months_after_November).length!==191)
 throw Error("Original chronological count-month support changed");
function district(site){
 if(["BRDM","BRDN","BRDS"].includes(site))return"Cape Bird (3 codes)";
 if(["CRZE","CRZW"].includes(site))return"Cape Crozier (2 codes)";
 return site;
}
function physical(site){
 if(["BRDM","BRDN","BRDS","CRZE","CRZW","ROYD"].includes(site))return"Ross Island (6 source codes)";
 return site;
}
function pairings(which,scheme){
 const obs=original.filter(x=>which==="all_original"||x.both_original_count_months_after_November);
 const groupId=scheme==="site_code"?x=>x:scheme==="breeding_district"?district:physical;
 const map=new Map();
 for(const row of obs){
  const place=groupId(row.source_site_code),key=place+"|"+row.year,a=map.get(key)||[];
  a.push(row);map.set(key,a);
 }
 const aggregated=[...map].map(([key,a])=>({
  area:groupId(a[0].source_site_code),year:a[0].year,region:a[0].region,
  mean_log_count_change:mean(a.map(x=>x.observed_log_count_change)),
  mean_source_nearshore_SIC:mean(a.map(x=>x.original_nearshore_SIC_AugNov_pct)),
  n_source_codes:a.length
 }));
 if(aggregated.some(x=>!Number.isFinite(x.mean_log_count_change)))throw Error("Malformed count");
 const names=[...new Set(aggregated.map(x=>x.area))].sort();
 const pairs=[];
 for(let i=0;i<names.length;i++)for(let j=i+1;j<names.length;j++){
  const a=aggregated.filter(x=>x.area===names[i]),b=aggregated.filter(x=>x.area===names[j]);
  const bm=new Map(b.map(x=>[x.year,x])),matched=a.filter(x=>bm.has(x.year));
  if(matched.length<3)continue;
  const g1=matched.map(x=>x.mean_log_count_change),g2=matched.map(x=>bm.get(x.year).mean_log_count_change);
  const s1=matched.map(x=>x.mean_source_nearshore_SIC),s2=matched.map(x=>bm.get(x.year).mean_source_nearshore_SIC);
  const rG=correlation(g1,g2),rS=correlation(s1,s2);
  if(rG===null||rS===null)continue;
  pairs.push({source_mode:which,spatial_collapsing:scheme,area_a:names[i],area_b:names[j],
   shared_years:matched.length,same_original_reported_region:a[0].region===b[0].region,
   growth_correlation:rG,nearshore_SIC_correlation:rS,
   caution:"Pairs reuse sites/years and source coastal windows; no independent regression or p value"
  });
 }
 const retained=pairs.filter(x=>x.shared_years>=5);
 return{aggregated,pairs,pairsSupported:retained,
  summary:{source_mode:which,spatial_collapsing:scheme,original_site_code_interval_n:obs.length,
   original_site_code_n:new Set(obs.map(x=>x.source_site_code)).size,
   grouped_distinct_area_n:names.length,grouped_area_years:aggregated.length,
   usable_pair_n_shared_years_ge_5:retained.length,
   group_n_in_pair_support:new Set(retained.flatMap(x=>[x.area_a,x.area_b])).size,
   within_original_region_pairs_ge_5:retained.filter(x=>x.same_original_reported_region).length,
   between_original_regions_pairs_ge_5:retained.filter(x=>!x.same_original_reported_region).length,
   distinct_regions_in_pair_support:new Set(retained.flatMap(x=>[
    aggregated.find(a=>a.area===x.area_a).region,aggregated.find(a=>a.area===x.area_b).region])).size,
   claims_permitted:"observational_pair_support_only_no_biological_climate_demography_transfer"}};
}
const summaries=[],pairRows=[],areaYearRows=[];
for(const mode of ["all_original","verified_after_November"])
for(const scheme of ["site_code","breeding_district","physical_Ross_island"]){
 const r=pairings(mode,scheme);
 summaries.push(r.summary);
 pairRows.push(...r.pairs);
 areaYearRows.push(...r.aggregated.map(x=>({...x,source_mode:mode,spatial_collapsing:scheme})));
}
const sel=(mode,scheme)=>summaries.find(x=>x.source_mode===mode&&x.spatial_collapsing===scheme);
const facts={
  original_count_intervals:original.length,
  strict_after_November_intervals:original.filter(x=>x.both_original_count_months_after_November).length,
  site_code_verified_overlap_pairs_5yr:sel("verified_after_November","site_code").usable_pair_n_shared_years_ge_5,
  site_code_verified_unique_sites_5yr:sel("verified_after_November","site_code").group_n_in_pair_support,
  district_verified_overlap_pairs_5yr:sel("verified_after_November","breeding_district").usable_pair_n_shared_years_ge_5,
  district_verified_unique_areas_5yr:sel("verified_after_November","breeding_district").group_n_in_pair_support,
  district_verified_between_region_pair_5yr:sel("verified_after_November","breeding_district").between_original_regions_pairs_ge_5,
  island_collapse_verified_overlap_pairs_5yr:sel("verified_after_November","physical_Ross_island").usable_pair_n_shared_years_ge_5,
  all_original_district_overlap_pairs_5yr:sel("all_original","breeding_district").usable_pair_n_shared_years_ge_5
};
const close=(a,b,k)=>{if(!Number.isFinite(a)||Math.abs(a-b)>1e-9)throw Error("Biological bridge source receipt "+k+" got "+a+" expected "+b)};
if(process.argv.includes("--check-receipt"))for(const [k,v]of Object.entries(exp.values))close(facts[k],v,k);
mkdirSync(out,{recursive:true});
writeFileSync(join(out,"source_pinned_adeli_annual_growth_and_SIC.csv"),toCSV(original));
writeFileSync(join(out,"biological_growth_coobservability_by_spatial_unit.csv"),toCSV(summaries));
writeFileSync(join(out,"pairwise_growth_SIC_correlation_observability.csv"),toCSV(pairRows));
writeFileSync(join(out,"breeding_district_collapse_yearly_source.csv"),toCSV(areaYearRows));
writeFileSync(join(out,"biological_bridge_gate.json"),JSON.stringify({
 status:"empirical_climate_breeding_synchrony_transport_not_identifiable_in_verified_cross_region_panel",
 facts,source_git_blobs:Object.fromEntries(Object.entries(files).map(([k,[,v]])=>[k,v])),
 notes:"Original count intervals with matching site/month and method. 191 calendar-verified intervals narrow to just five pairwise contrasts from four districts all in Victoria Land; Ross Island nesting areas are physically on one island. Several pairs reuse the same site, year and SIC pixel. Numerical r among such pairs cannot establish region-wide environmental forcing of demography or a population portfolio effect.",
 comparisons:summaries
},null,2)+"\n");
console.log("BIOLOGICAL CLIMATE COVARIANCE SUPPORT "+JSON.stringify({
 facts,summary:summaries,verified:process.argv.includes("--check-receipt")
}));
