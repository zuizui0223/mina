// Ross Island area-vs-sector count concentration and source-year climate observability
// ORIGINAL MAPPPD unit: recorded count (not independently certified pairs/individuals)
// node research/climate-penguin/work/ross_island_spatial_scale_v1/build.mjs --check-receipt
import {readFileSync,mkdirSync,writeFileSync} from "node:fs";
import {resolve,join} from "node:path";
import {createHash} from "node:crypto";
const ROOT=resolve("research/climate-penguin/outputs"),OUT=join(ROOT,"ross_island_spatial_scale_v1");
const INPUT={
 MAPPPD:["comparison_audit/mapppd_unambiguous_site_seasons.csv","fc134e364cf38699fa7611d7dee5fbbbcb370c0a"],
 historical:["historical_ice_breeding_transfer_v1/adeli_39site_historical_climate_growth.csv","db58938630e80d22ba445600ce1ad3f554c452e2"],
 satellite:["climate_penguin/macro_monthly_seaice_1991_2020.csv","4fcea71c2d8b1069b6ad143f6522061ed434daf5"],
 vegetation:["vegetation_response_v1/site_species_cohort.csv","23fea5988889303ecdc16f4b5309073cf38e366a"],
 snow:["september_snow_v1/september_summary.csv","204fb5bf1ab14496ca783d4d08e3b72fd5cfd8b4"],
 locations:["climate_penguin/daily_ice_locations.csv","1c5214ab355d3d2e19bc33e5de4693fa21f38731"],
 countTiming:["climate_penguin/historical_count_interval_timing.csv","f1aa63a99eff97482dde9b1c680c19b36c1dada5"],
};
const RECEIPT=JSON.parse(readFileSync(join(OUT,"expected_receipt.json"),"utf8"));
function parseCSV(s){
 const rows=[];let cols=[],value="",q=false;
 for(let i=0;i<s.length;i++){
  const c=s[i];
  if(q){if(c==='"'&&s[i+1]==='"'){value+='"';i++}else if(c==='"')q=false;else value+=c}
  else if(c==='"')q=true;
  else if(c===','){cols.push(value);value=""}
  else if(c==='\n'){cols.push(value.replace(/\r$/,""));if(cols.length>1)rows.push(cols);cols=[];value=""}
  else value+=c;
 }
 if(cols.length||value){cols.push(value);rows.push(cols)}
 if(q||rows.length<2)throw Error("Original source malformed");
 const header=rows.shift();
 return rows.map((r,i)=>{
  if(r.length!==header.length)throw Error("Original CSV field count "+i);
  return Object.fromEntries(header.map((k,j)=>[k,r[j]]));
 });
}
function csv(rows){
 if(!rows.length)throw Error("Empty output CSV");
 const head=Object.keys(rows[0]),esc=x=>{
  const s=x===undefined||x===null?"":String(x);
  return /[,"\r\n]/.test(s)?'"'+s.replaceAll('"','""')+'"':s;
 };
 return head.join(",")+"\n"+rows.map(r=>head.map(k=>esc(r[k])).join(",")).join("\n")+"\n";
}
const D={};
for(const [k,[file,sha]] of Object.entries(INPUT)){
 const b=readFileSync(join(ROOT,file)),actual=createHash("sha1").update(Buffer.from("blob "+b.length+"\0")).update(b).digest("hex");
 if(actual!==sha||RECEIPT.source_git_blobs[k]!==sha)throw Error("Input SHA drift "+k+" "+actual);
 D[k]=parseCSV(b.toString("utf8"));
}
if(D.MAPPPD.length!==2999||D.historical.length!==39||D.satellite.length!==9600||D.vegetation.length!==246||
 D.snow.length!==1166)throw Error("Upstream original cohort changed");
const sum=a=>a.reduce((s,v)=>s+v,0),mean=a=>sum(a)/a.length,unique=(a,k)=>new Set(a.map(k)).size;
const near=(a,b,k)=>{if(!Number.isFinite(a)||Math.abs(a-b)>1e-8)throw Error("Independent fixed numeric mismatch "+k+": "+a+" vs "+b)};
function pearson(a,b){
 if(a.length!==b.length||a.length<4) return null;
 const ma=mean(a),mb=mean(b);
 let xx=0,yy=0,xy=0;
 for(let i=0;i<a.length;i++){const dx=a[i]-ma,dy=b[i]-mb;xx+=dx*dx;yy+=dy*dy;xy+=dx*dy}
 return xx>0&&yy>0?xy/Math.sqrt(xx*yy):null;
}
const areaSources={
 "Cape Bird":["BRDM","BRDN","BRDS"],
 "Cape Crozier":["CRZE","CRZW"],
 "Cape Royds":["ROYD"]
};
const sourceCodes=Object.values(areaSources).flat();
if(unique(sourceCodes,x=>x)!==6)throw Error("Original Ross Island sector code duplication");
const cohort=new Map(D.historical.map(x=>[x.site_id,x])),longIDs=new Set(cohort.keys());
const vegetation=new Map(D.vegetation.filter(x=>x.species_id==="ADPE"&&longIDs.has(x.site_id)).map(x=>[x.site_id,x]));
const matched31=[...vegetation.keys()];
if(matched31.length!==31||sourceCodes.some(x=>!vegetation.has(x)))throw Error("Source 31 land-vectors or Ross Island support changed");
const modelLoc=new Map(D.locations.filter(x=>x.cohort==="macro_40"&&longIDs.has(x.site_id)).map(x=>[x.site_id,x.location_id]));
const snowByLocation=new Map();
for(const x of D.snow){
 const arr=snowByLocation.get(x.location_id)||[];
 arr.push(x);snowByLocation.set(x.location_id,arr);
}
const snowVariability=[...snowByLocation].map(([id,arr])=>{
 const swe=arr.map(x=>+x.september_00utc_mean_swe_m);
 if(arr.length!==11||arr.some(x=>x.complete!=="True"))throw Error("ERA5 source snow annual completeness drift "+id);
 const ma=Math.max(...swe),mi=Math.min(...swe);
 return{location_id:id,years:arr.length,minimum_September_SWE_m:mi,maximum_September_SWE_m:ma,
  historical_SWE_range_2011_2021_m:ma-mi,
  source_ERA5_grid_cell_id:arr[0].grid_lat+"|"+arr[0].grid_lon,
  source_ERA5_land_fraction:+arr[0].land_fraction,
  matched_original_39_sites:[...modelLoc].filter(([site,loc])=>loc===id).map(([site])=>site).join(";"),
  among_original_39:[...modelLoc.values()].includes(id),
  among_original_31:[...vegetation.keys()].some(site=>modelLoc.get(site)===id),
  no_interannual_variance_at_ERA5_grid:ma-mi<=1e-10
 };
}).sort((a,b)=>a.location_id.localeCompare(b.location_id));
const bySnowLocation=new Map(snowVariability.map(x=>[x.location_id,x]));
const variability31=matched31.map(x=>bySnowLocation.get(modelLoc.get(x)));
if(variability31.some(x=>!x))throw Error("Original snow 31-site support incomplete");
const vals39=[...longIDs].map(id=>bySnowLocation.get(modelLoc.get(id)));
if(vals39.some(x=>!x))throw Error("Original snow 39-site support incomplete");
const sicMonths=new Map();
for(const r of D.satellite){
 if(!longIDs.has(r.site_id)||r.inner_km!=="0"||![8,9,10,11].includes(+r.month))continue;
 if(r.complete_month!=="True")throw Error("Original nearshore SIC month incomplete");
 const k=r.site_id+"|"+r.year,arr=sicMonths.get(k)||[];
 arr.push(+r.sic_mean);sicMonths.set(k,arr);
}
const annualSIC=new Map();
for(const [k,arr] of sicMonths){
 if(arr.length!==4||!arr.every(Number.isFinite))throw Error("Source SIC year incomplete "+k);
 annualSIC.set(k,mean(arr));
}
const allCounts=new Map();
for(const x of D.MAPPPD){
 if(!longIDs.has(x.site_id)||x.species_id!=="ADPE"||x.count===""||!Number.isFinite(+x.count)||+x.count<=0)continue;
 if(x.method!==cohort.get(x.site_id).method)continue; 
 if(+x.season<1991||+x.season>2020)continue;
 const arr=allCounts.get(x.site_id)||[];
 arr.push(x);allCounts.set(x.site_id,arr);
}
for(const arr of allCounts.values())arr.sort((a,b)=>+a.season-+b.season);
const timing=new Map();
for(const x of D.countTiming){
 const key=[x.site_id,x.start,x.end,x.method_start].join("|");
 if(timing.has(key))throw Error("Original date audit repeated key");
 timing.set(key,x);
}
const strictAnnual=[];
for(const [site,rows] of allCounts){
 if(!vegetation.has(site))continue;
 for(let i=1;i<rows.length;i++){
  const x=rows[i-1],y=rows[i],start=+x.season,end=+y.season;
  if(end!==start+1||start<2011||end>2020)continue;
  const gate=timing.get([site,start,end,x.method].join("|"));
  if(!gate||gate.both_all_after_november!=="True")continue;
  const snowLoc=modelLoc.get(site),s0=D.snow.find(z=>z.location_id===snowLoc&&+z.year===start),s1=D.snow.find(z=>z.location_id===snowLoc&&+z.year===end);
  if(!s0||!s1)throw Error("Count years lack snow");
  strictAnnual.push({
   site_id:site,region:cohort.get(site).region,start_year:start,end_year:end,
   original_count_method:x.method,source_count_start:+x.count,source_count_end:+y.count,
   annual_log_recorded_count_change:Math.log(+y.count/+x.count),
   source_snow_cell:snowLoc,source_ERA5_land_fraction:+s1.land_fraction,
   source_ERA5_SWE_start_m:+s0.september_00utc_mean_swe_m,source_ERA5_SWE_end_m:+s1.september_00utc_mean_swe_m,
   source_ERA5_September_SWE_change_m:+s1.september_00utc_mean_swe_m- +s0.september_00utc_mean_swe_m,
   satellite_seaice_start_pct:annualSIC.get(site+"|"+start),
   satellite_seaice_end_pct:annualSIC.get(site+"|"+end),
   source_original_static_vegetation_detection:vegetation.get(site).map_status,
   nearshore_ice_time_change_is_observed_but_not_causal:true,
   ERA5_grid_SWE_is_not_on_nest_snow:true
  });
 }
}
strictAnnual.sort((a,b)=>a.end_year-b.end_year||a.site_id.localeCompare(b.site_id));
if(strictAnnual.length!==56)throw Error("Original late-2011–2020 strict-time count support drift");
const strictLand=strictAnnual.filter(x=>x.source_ERA5_land_fraction>=.5);
const recross=new Map();
for(const x of D.MAPPPD){
 if(x.species_id!=="ADPE"||x.method!=="aerial"||+x.count<=0||!sourceCodes.includes(x.site_id))continue;
 if(x.n_rows!=="1"||x.n_counts!=="1")throw Error("Ross original count row nonunique or ambiguous "+x.site_id+x.season);
 const year=+x.season,ar=recross.get(year)||[];
 ar.push(x);recross.set(year,ar);
}
const completeYears=[...recross].filter(([year,a])=>a.length===6&&year>=1985&&year<=2024).sort((a,b)=>a[0]-b[0]);
if(completeYears.length!==31)throw Error("Ross six same-source-site aerial census years changed");
const rossSectorRows=[],rossYears=[],rossIce=[];
function neff(arr){const t=sum(arr);return t*t/sum(arr.map(v=>v*v))}
for(const [year,rows] of completeYears){
 const byCode=new Map(rows.map(x=>[x.site_id,x]));
 if(byCode.size!==6)throw Error("Original Ross duplicate sector "+year);
 const byArea=Object.fromEntries(Object.entries(areaSources).map(([area,parts])=>[area,sum(parts.map(s=>+byCode.get(s).count))]));
 const totals=sourceCodes.map(k=>+byCode.get(k).count),total=sum(totals);
 const areaValues=Object.values(byArea);
 const row={year,total_six_original_aerial_counts:total,
  recorded_Cape_Bird:byArea["Cape Bird"],recorded_Cape_Crozier:byArea["Cape Crozier"],recorded_Cape_Royds:byArea["Cape Royds"],
  N_eff_three_districts:neff(areaValues),N_eff_six_source_sectors:neff(totals),
  Crozier_share:byArea["Cape Crozier"]/total,
  Bird_share:byArea["Cape Bird"]/total,Royds_share:byArea["Cape Royds"]/total,
  original_six_source_codes_complete:true,census_target_not_certified_same_as_breeding_pairs:true};
 rossYears.push(row);
 for(const [area,parts] of Object.entries(areaSources))for(const site of parts){
  const x=byCode.get(site);
  rossSectorRows.push({year,area,source_site_code:site,original_aerial_count:+x.count,
   original_single_census_row:Number(x.n_rows),original_count_records:Number(x.n_counts),
   source_original_site_name:x.site_name,longitude:+x.longitude,latitude:+x.latitude,
   static_mapped_lichen_vegetation_status:vegetation.get(site).map_status,
   source_snow_ERA5_cell:modelLoc.get(site)});
 }
 if(year>=1991&&year<=2020){
  const sicBy=new Map(sourceCodes.map(id=>[id,annualSIC.get(id+"|"+year)]));
  if([...sicBy.values()].some(x=>!Number.isFinite(x)))throw Error("Ross native SIC missing "+year);
  const meanArea=Object.fromEntries(Object.entries(areaSources).map(([name,parts])=>[name,mean(parts.map(site=>sicBy.get(site)))]));
  const rec={year,nearshore_SIC_Bird_pct:meanArea["Cape Bird"],nearshore_SIC_Crozier_pct:meanArea["Cape Crozier"],
   nearshore_SIC_Royds_pct:meanArea["Cape Royds"],
   Crozier_minus_Bird_nearshore_SIC_pp:meanArea["Cape Crozier"]-meanArea["Cape Bird"],
   mean_six_sector_nearshore_SIC_pct:mean([...sicBy.values()]),
   total_census_count:total,Crozier_count_share:row.Crozier_share,
   unique_sic_sector_codes:6,not_six_independent_ocean_climate_pixels:true};
  rossIce.push(rec);
 }
}
const byIce=new Map(rossIce.map(x=>[x.year,x]));
const consecutive=[];
for(let i=1;i<rossYears.length;i++){
 const a=rossYears[i-1],b=rossYears[i];
 if(b.year!==a.year+1)continue;
 const p=byIce.get(a.year),q=byIce.get(b.year);
 consecutive.push({year:b.year,start_year:a.year,end_year:b.year,
  log_total_recorded_count_change:Math.log(b.total_six_original_aerial_counts/a.total_six_original_aerial_counts),
  change_N_eff_three_districts:b.N_eff_three_districts-a.N_eff_three_districts,
  change_N_eff_six_sectors:b.N_eff_six_source_sectors-a.N_eff_six_source_sectors,
  change_Crozier_census_share:b.Crozier_share-a.Crozier_share,
  observed_same_year_nearshore_seaice_available:!!p&&!!q,
  change_mean_six_sector_SIC_pp:p&&q?q.mean_six_sector_nearshore_SIC_pct-p.mean_six_sector_nearshore_SIC_pct:null,
  change_Crozier_minus_Bird_SIC_contrast_pp:p&&q?q.Crozier_minus_Bird_nearshore_SIC_pp-p.Crozier_minus_Bird_nearshore_SIC_pp:null,
  source_original_single_method_aerial:true});
}
function detrend(y,t){
 const mt=mean(t),my=mean(y),num=sum(t.map((v,i)=>(v-mt)*(y[i]-my))),den=sum(t.map(v=>(v-mt)**2));
 const slope=num/den;
 return y.map((v,i)=>v-my-slope*(t[i]-mt));
}
function era(name,pred){
 const part=rossYears.filter(pred);
 if(part.length<4)throw Error("Insufficient Ross counts for "+name);
 const year=part.map(x=>x.year),logtot=part.map(x=>Math.log(x.total_six_original_aerial_counts)),
  n3=part.map(x=>x.N_eff_three_districts),n6=part.map(x=>x.N_eff_six_source_sectors);
 const rowCV=consecutive.filter(x=>pred({year:x.start_year})&&pred({year:x.end_year}));
 const pearDiff=rowCV.length>3?pearson(rowCV.map(x=>x.log_total_recorded_count_change),rowCV.map(x=>x.change_N_eff_three_districts)):null;
 const r=pearson(logtot,n3);
 const loo=part.map((_,i)=>pearson(part.filter((_,j)=>j!==i).map(x=>Math.log(x.total_six_original_aerial_counts)),
                                    part.filter((_,j)=>j!==i).map(x=>x.N_eff_three_districts)));
 return{era:name,complete_years:part.length,
  first_calendar_year:Math.min(...year),last_calendar_year:Math.max(...year),
  Pearson_log_total_vs_3district_N_eff:r,
  Pearson_log_total_vs_6sector_N_eff:pearson(logtot,n6),
  Pearson_partial_linear_calendar_year_log_total_vs_3district_N_eff:pearson(detrend(logtot,year),detrend(n3,year)),
  leave_one_calendar_year_out_Pearson_min:Math.min(...loo),leave_one_calendar_year_out_Pearson_max:Math.max(...loo),
  fully_consecutive_original_year_intervals:rowCV.length,
  Pearson_true_year_on_year_log_total_vs_delta_N_eff_3districts:pearDiff,
  mean_observed_total_counts:mean(part.map(x=>x.total_six_original_aerial_counts)),
  interpretation:"Single Ross Island, 3 breeding districts, 6 aerial source sectors; descriptive time-scale-dependent allocation; not a cross-island law or climate-caused distribution"};
}
const panels=[
 era("all_1985_2024",x=>x.year>=1985&&x.year<=2024),
 era("historical_1991_2020",x=>x.year>=1991&&x.year<=2020),
 era("historical_early_1991_2009",x=>x.year>=1991&&x.year<=2009),
 era("historical_later_2010_2019",x=>x.year>=2010&&x.year<=2019),
 era("recent_2011_2024",x=>x.year>=2011&&x.year<=2024)
];
const iceHistorical=consecutive.filter(x=>x.observed_same_year_nearshore_seaice_available&&x.start_year>=1991&&x.end_year<=2020);
const iceR=pearson(iceHistorical.map(x=>x.change_Crozier_minus_Bird_SIC_contrast_pp),iceHistorical.map(x=>x.change_Crozier_census_share));
const result={
 original_snow_locations:snowVariability.length,
 original_snow_locations_zero_year_variability:snowVariability.filter(x=>x.no_interannual_variance_at_ERA5_grid).length,
 original_39_sites_zero_snow_year_variability:vals39.filter(x=>x.no_interannual_variance_at_ERA5_grid).length,
 matched_31_vegetation_sites_zero_snow_year_variability:variability31.filter(x=>x.no_interannual_variance_at_ERA5_grid).length,
 original_31_vegetation_source_sites:matched31.length,
 original_same_method_after_nov_2011_2020_count_transitions:strictAnnual.length,
 original_same_method_after_nov_and_ERA5_land_fraction_ge0_5_pairs:strictLand.length,
 original_same_method_after_nov_and_ERA5_land_fraction_ge0_5_sites:unique(strictLand,x=>x.site_id),
 strict_land_pairs_with_snow_SWE_year_delta_nonzero:strictLand.filter(x=>Math.abs(x.source_ERA5_September_SWE_change_m)>1e-10).length,
 Ross_original_complete_six_source_sector_years:rossYears.length,
 Ross_historical_original_six_source_sector_years:rossYears.filter(x=>x.year>=1991&&x.year<=2020).length,
 Ross_original_true_consecutive_year_intervals:consecutive.length,
 Ross_historical_true_consecutive_year_intervals:iceHistorical.length,
 Ross_original_39_member_sector_codes:sourceCodes.length,
 Ross_3district_logtotal_neff_Pearson_1991_2020:panels[1].Pearson_log_total_vs_3district_N_eff,
 Ross_3district_logtotal_neff_Pearson_2010_2019:panels[3].Pearson_log_total_vs_3district_N_eff,
 Ross_3district_logtotal_neff_Pearson_2011_2024:panels[4].Pearson_log_total_vs_3district_N_eff,
 Ross_delta_neff_vs_delta_total_Pearson_1991_2020:panels[1].Pearson_true_year_on_year_log_total_vs_delta_N_eff_3districts,
 Ross_local_Crozier_minus_Bird_SIC_change_vs_count_share_change_Pearson:iceR
};
if(process.argv.includes("--check-receipt"))for(const [key,v] of Object.entries(RECEIPT.values))near(result[key],v,key);
mkdirSync(OUT,{recursive:true});
writeFileSync(join(OUT,"original_ERA5_all106_site_snow_variability_support.csv"),csv(snowVariability));
writeFileSync(join(OUT,"original_2011_2020_month_verified_annual_snow_ice_count_pairs.csv"),csv(strictAnnual));
writeFileSync(join(OUT,"ross_island_original_sector_counts_by_year.csv"),csv(rossSectorRows));
writeFileSync(join(OUT,"ross_island_three_district_counts_Neff_by_year.csv"),csv(rossYears));
writeFileSync(join(OUT,"ross_island_1991_2020_original_seaice_and_count_share.csv"),csv(rossIce));
writeFileSync(join(OUT,"ross_island_original_consecutive_count_seaice_deltas.csv"),csv(consecutive));
writeFileSync(join(OUT,"ross_island_timescale_and_hierarchy_sensitivity.csv"),csv(panels));
writeFileSync(join(OUT,"result.json"),JSON.stringify({
 status:"source_pinned_same_method_single_island_colony_allocation_and_no_dynamic_terrestrial_snow_support",
 receipt:result,panels,
 observed_2019_total:rossYears.find(x=>x.year===2019).total_six_original_aerial_counts,
 observed_2023_total:rossYears.find(x=>x.year===2023).total_six_original_aerial_counts,
 observed_2024_total:rossYears.find(x=>x.year===2024).total_six_original_aerial_counts,
 additional:"Snow records 2011–2021 are an extracted coarse-grid SWE product, no 31-site interannual variation. Six aerial code counts have one original census row and one count per code-year but count target comparability beyond that cannot be certified. Island-area aggregation has three districts on ONE Ross Island, not three island replicates. Local SIC spatial differences do not identify a causal colony response; eastern Southern Ocean climate not modeled into after-2020 count years.",
 sources:Object.fromEntries(Object.entries(INPUT).map(([k,[,sha]])=>[k,sha]))
},null,2)+"\n");
writeFileSync(join(OUT,"validation.json"),JSON.stringify({source_git_blobs_verified:true,expected_numeric_receipt_verified:process.argv.includes("--check-receipt"),Ross_original_sector_codes:sourceCodes,original_31_SWE_temporal_variance_zero:true,Ross_neff_is_compositional_and_scale_invariant:true,source_season_missing_not_interpolated:true,future_breeding_projection:false},null,2)+"\n");
console.log("ROSS ISLAND CLIMATE LAND SOURCE CHECK "+JSON.stringify({receipt:result,panels,selected:rossYears.filter(x=>[1991,2001,2011,2019,2023,2024].includes(x.year)),verified:process.argv.includes("--check-receipt")}));
