// Reproduce observed 1991-2020 site-year SIC variance decomposition. Node.js >= 20.
// node research/climate-penguin/work/observed_sic_covariance_scale_v1/build.mjs [outputs_root] [output_dir]
import {readFileSync,writeFileSync,mkdirSync} from "node:fs";
import {createHash} from "node:crypto";
import {resolve,join} from "node:path";

function parseCSV(s){
  const all=[];let row=[],f="",inQ=false;
  for(let i=0;i<s.length;i++){
    const c=s[i];
    if(inQ){if(c==='"'&&s[i+1]==='"'){f+='"';i++}else if(c==='"')inQ=false;else f+=c;}
    else if(c==='"')inQ=true;
    else if(c===','){row.push(f);f="";}
    else if(c==='\n'){row.push(f.replace(/\r$/,""));if(row.length>1)all.push(row);row=[];f="";}
    else f+=c;
  }
  if(f||row.length){row.push(f);all.push(row);}
  if(inQ)throw Error("open CSV quote");
  const h=all.shift();return all.map((x,i)=>{if(x.length!==h.length)throw Error("CSV width "+i);return Object.fromEntries(h.map((k,j)=>[k,x[j]]));});
}
function encodeCSV(rows,cols){
  const q=v=>{const s=v==null?"":String(v);return /[",\n\r]/.test(s)?'"'+s.replaceAll('"','""')+'"':s;};
  return cols.join(",")+"\n"+rows.map(x=>cols.map(k=>q(x[k])).join(",")).join("\n")+"\n";
}
function analyzeHistoricalSIC(inputs, provenance){
 const full=parseCSV(inputs.monthly),locs=parseCSV(inputs.coords);
 if(full.length!==9600||locs.length!==106)throw Error("source count differs");
 const fixed={
   box:{latitude_min:-65.30,latitude_max:-64.70,longitude_min:-64.20,longitude_max:-63.70},
   cohort:"macro_40",years:[1991,2020],months:[8,9,10,11],inner_km:[0,100],
   variable:"sic_mean",near_label:"near_0_100km",offshore_label:"offshore_100_500km",
   status:"observed_environmental_covariance_no_breeding_response_estimated"
 };
 const n=v=>{if(v==null||v===""||!Number.isFinite(Number(v)))throw Error("invalid source number "+v);return Number(v);};
 const m=arr=>arr.reduce((a,b)=>a+b,0)/arr.length;
 const varSample=a=>a.reduce((s,x)=>s+(x-m(a))**2,0)/(a.length-1);
 const hav=(a,b)=>{
  const rad=Math.PI/180,lat1=n(a.latitude)*rad,lat2=n(b.latitude)*rad;
  const dLat=lat2-lat1,dLon=(n(b.longitude)-n(a.longitude))*rad;
  return 12742.0176*Math.asin(Math.min(1,Math.sqrt(Math.sin(dLat/2)**2+Math.cos(lat1)*Math.cos(lat2)*Math.sin(dLon/2)**2)));
 };
 const selected=locs.filter(x=>x.cohort===fixed.cohort&&n(x.latitude)>=fixed.box.latitude_min&&n(x.latitude)<=fixed.box.latitude_max&&n(x.longitude)>=fixed.box.longitude_min&&n(x.longitude)<=fixed.box.longitude_max).sort((x,y)=>x.site_id.localeCompare(y.site_id));
 const expectedSites=["BISC","LITC","PCHA","PETE","PLEN","YALO"];
 if(selected.length!==6||selected.some((r,i)=>r.site_id!==expectedSites[i]))throw Error("predeclared box no longer recovers 6 sites");
 const coords=new Map(selected.map(x=>[x.site_id,x]));
 const mon=full.filter(x=>coords.has(x.site_id));
 if(mon.length!==1440)throw Error("6 point full observation coverage missing "+mon.length);
 if(mon.some(x=>x.complete_month!=="True"||n(x.days)!==n(x.expected_days)||n(x.days)!==n(x.supported_days)||n(x.sic_mean)<0||n(x.sic_mean)>100))throw Error("month support or SIC physical bounds");
 const seriesMap=new Map(mon.map(x=>[[x.site_id,x.year,x.month,x.inner_km].join("|"),x]));
 if(seriesMap.size!==mon.length)throw Error("duplicate site/year/month/band");
 const years=Array.from({length:30},(_,i)=>1991+i);
 const pear=(aa,bb)=>{
  if(aa.length!==bb.length||aa.length<3)throw Error("bad pair");
  const am=m(aa),bm=m(bb);let num=0,da=0,db=0;
  for(let i=0;i<aa.length;i++){const a=aa[i]-am,b=bb[i]-bm;num+=a*b;da+=a*a;db+=b*b;}
  return da*db>0?num/Math.sqrt(da*db):null;
 };
 const summary=[],pair=[],siteyear=[],extreme=[];
 for(const band of fixed.inner_km)for(const month of fixed.months){
  const siteData=new Map();
  for(const s of expectedSites){
   const a=years.map(year=>{
    const item=seriesMap.get([s,year,month,band].join("|"));
    if(!item)throw Error("no site-year "+s+"/"+year+"/"+month+"/"+band);
    return n(item.sic_mean);
   });
   siteData.set(s,a);
  }
  const all=expectedSites.flatMap(s=>siteData.get(s));
  const grand=m(all);
  const stationMean=new Map(expectedSites.map(id=>[id,m(siteData.get(id))]));
  const yearMean=new Map(years.map((year,j)=>[year,m(expectedSites.map(s=>siteData.get(s)[j]))]));
  let SST=0,SSY=0,SSS=0,SSI=0;
  const sdSite=[];
  const regionSeries=years.map(y=>yearMean.get(y)),vRegion=varSample(regionSeries);
  for(const s of expectedSites){
   const values=siteData.get(s);
   sdSite.push(Math.sqrt(varSample(values)));
   for(let k=0;k<years.length;k++){
    const year=years[k],v=values[k],resid=v-yearMean.get(year)-stationMean.get(s)+grand;
    SST+=(v-grand)**2;
    SSY+=(yearMean.get(year)-grand)**2;
    SSS+=(stationMean.get(s)-grand)**2;
    SSI+=resid**2;
    siteyear.push({
      site_id:s,year,month,inner_km:band,site_latitude:n(coords.get(s).latitude),site_longitude:n(coords.get(s).longitude),
      sic_mean_pct:v,region_six_point_year_equal_mean_pct:yearMean.get(year),
      site_30yr_mean_pct:stationMean.get(s), grand_30yr_mean_pct:grand,
      site_static_offset_pct:stationMean.get(s)-grand,
      site_year_nonshared_residual_pct:resid
    });
   }
  }
  if(Math.abs((SSY+SSS+SSI)/SST-1)>1e-10)throw Error("ANOVA decomposition fails "+band+"/"+month);
  let pairCorr=[],n2Corr=0;
  for(let i=0;i<expectedSites.length;i++)for(let j=i+1;j<expectedSites.length;j++){
   const id1=expectedSites[i],id2=expectedSites[j],
   vals1=siteData.get(id1),vals2=siteData.get(id2),corr=pear(vals1,vals2);
   if(!Number.isFinite(corr))throw Error("undefined correlation");
   pairCorr.push(corr);n2Corr+=2*corr*corr;
   pair.push({month,inner_km:band,site_1:id1,site_2:id2,
      distance_km:hav(coords.get(id1),coords.get(id2)),
      sic_1991_2020_temporal_pearson_r:corr,
      mean_difference_site1_minus_site2_pp:stationMean.get(id1)-stationMean.get(id2),
      annual_difference_sample_sd_pp:Math.sqrt(varSample(vals1.map((v,k)=>v-vals2[k])))});
  }
  pairCorr.sort((a,b)=>a-b);
  const siteRange=years.map((y,k)=>Math.max(...expectedSites.map(s=>siteData.get(s)[k]))-Math.min(...expectedSites.map(s=>siteData.get(s)[k])));
  const sampleVars=expectedSites.map(s=>({s,v:varSample(siteData.get(s))}));
  const ratios=sampleVars.map(z=>z.v/vRegion);
  for(const z of sampleVars)extreme.push({month,inner_km:band,hypothetical_all_weight_at_site:z.s,
    site_sic_interannual_variance:z.v,
    equal_six_sites_interannual_variance:vRegion,
    variance_ratio_full_concentration_vs_equal_sites:z.v/vRegion});
  const corrRank=36/(6+n2Corr);
  summary.push({
   month,inner_km:band,scope:"six_fixed_geographic_box_sites_not_all_five_Palmer_census_islands",
   n_sites:expectedSites.length,n_years:years.length,n_site_years:all.length,
   mean_sic_pct:grand,annual_region_equal_mean_sample_sd_pp:Math.sqrt(vRegion),
   total_deviation_squared:SST,
   year_common_fraction_of_total_SIC_variation:SSY/SST,
   site_fixed_fraction_of_total_SIC_variation:SSS/SST,
   site_by_year_remaining_fraction_of_total_SIC_variation:SSI/SST,
   site_by_year_residual_rmse_pp:Math.sqrt(SSI/all.length),
   year_fraction_of_temporal_variation_after_site_demean:SSY/(SSY+SSI),
   site_idiosyncratic_fraction_of_temporal_variation_after_site_demean:SSI/(SSY+SSI),
   min_pairwise_sic_year_r:pairCorr[0],median_pairwise_sic_year_r:pairCorr[7],max_pairwise_sic_year_r:pairCorr[14],
   correlation_matrix_effective_rank: corrRank,
   mean_six_site_range_in_a_year_pp:m(siteRange),
   median_six_site_range_in_a_year_pp:siteRange.sort((a,b)=>a-b)[14]/2+siteRange[15]/2,
   max_six_site_range_in_a_year_pp:Math.max(...siteRange),
   smallest_full_concentration_variance_ratio:Math.min(...ratios),
   largest_full_concentration_variance_ratio:Math.max(...ratios)
  });
 }
 if(summary.length!==8||pair.length!==120||extreme.length!==48||siteyear.length!==1440)throw Error("derived row counts");
 const septNear=summary.find(x=>x.month===9&&x.inner_km===0);
 const septFar=summary.find(x=>x.month===9&&x.inner_km===100);
 if(Math.abs(septNear.year_common_fraction_of_total_SIC_variation-.8793513944339244)>1e-10||
 Math.abs(septNear.site_by_year_remaining_fraction_of_total_SIC_variation-.01136592209521955)>1e-10||
 Math.abs(septFar.site_by_year_remaining_fraction_of_total_SIC_variation-.0006353172162819851)>1e-10)throw Error("source result anchor drift");
 const meta={
  status:"observed_1991_2020_satellite_SIC_shared_temporal_variation_robust_not_biological_causal_transfer",
  source_git_blob_sha:provenance,
  geofence:fixed,
  numerical_results:summary,
  sample:{original_macro_monthly_rows:full.length,original_geographic_locations:locs.length,selected_macro_site_codes:expectedSites,selected_site_year_month_band_rows:mon.length,year_count:years.length,analysis_subsets:summary.length,pairwise_correlations:pair.length,yearwise_residuals:siteyear.length,single_site_concentration_scenarios:extreme.length},
  comparisons:{near_0_100km:"Buffers overlap, not independent site-specific sea-ice measurements",offshore_100_500km:"Broader overlapping annular buffers, not independent site-specific foraging environments"},
  empirical_limitation:"The six geographic proxy points are NOT the 1991-2017 Palmer LTER five-island colony-code panel. No direct island/polygon exposure or breeding response coefficient is estimated.",
  uncertainty:"Year 1991-2020 provides thirty environmental annual replicates with spatial/serial dependence; pairwise site comparisons are dependent. No p-values; variance ratios are descriptive under fixed spatial weights.",
  known_scale_issue:"These observations are 0-100 and 100-500km marine windows, not 0-5km island-specific snow/melt or foraging track SIC. Strong synchrony can be partly induced by overlapping observational windows.",
  mainInterpretation:"After subtracting site means and common calendar-year means, only the site×year residual remains; concentration can change common-SIC sensitivity only if shocks differ among spatial units (not established at subcolony scale)."
 };
 const files={
  "six_site_geographic_selection.csv":encodeCSV(selected,["site_id","latitude","longitude","cohort","location_id"]),
  "site_year_month_source_decomposition.csv":encodeCSV(siteyear,Object.keys(siteyear[0])),
  "month_band_shared_sic_summary.csv":encodeCSV(summary,Object.keys(summary[0])),
  "pairwise_annual_sic_correlations.csv":encodeCSV(pair,Object.keys(pair[0])),
  "hypothetical_single_site_concentration.csv":encodeCSV(extreme,Object.keys(extreme[0])),
  "summary.json":JSON.stringify(meta,null,2)+"\n"
 };
 return {meta,files};
}
const root=resolve(process.argv[2]||"research/climate-penguin/outputs");
const out=resolve(process.argv[3]||"research/climate-penguin/outputs/observed_sic_covariance_scale_v1");
const files={monthly:"climate_penguin/macro_monthly_seaice_1991_2020.csv",
coords:"climate_penguin/daily_ice_locations.csv"};
const pinned={
  "monthly": "4fcea71c2d8b1069b6ad143f6522061ed434daf5",
  "coords": "1c5214ab355d3d2e19bc33e5de4693fa21f38731"
};
const input={};
for(const [key,path] of Object.entries(files)){
 const raw=readFileSync(join(root,path));
 const blob=createHash("sha1").update(Buffer.concat([Buffer.from("blob "+raw.length+"\0"),raw])).digest("hex");
 if(blob!==pinned[key])throw Error("Source Git SHA mismatch "+path+" observed "+blob+" expected "+pinned[key]);
 input[key]=raw.toString("utf8");
}
const res=analyzeHistoricalSIC(input,pinned);
mkdirSync(out,{recursive:true});
for(const [file,text] of Object.entries(res.files))writeFileSync(join(out,file),text);
console.log(JSON.stringify({sample:res.meta.sample,septNear:res.meta.numerical_results.find(x=>x.month===9&&x.inner_km===0)},null,2));
