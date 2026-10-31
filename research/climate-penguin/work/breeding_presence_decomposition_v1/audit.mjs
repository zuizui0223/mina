// Post-hoc source audit of biological species replacement versus log1p pseudo-count ratios.
// Run: node research/climate-penguin/work/breeding_presence_decomposition_v1/audit.mjs
import {readFileSync, writeFileSync, mkdirSync} from "node:fs";
import {createHash} from "node:crypto";
import {resolve, join} from "node:path";
const base=resolve("research/climate-penguin/outputs"),out=join(base,"breeding_presence_decomposition_v1");
const originals={
  bio:["comparison_audit/mapppd_unambiguous_site_seasons.csv","fc134e364cf38699fa7611d7dee5fbbbcb370c0a"],
  paired:["warming_species_breeding_v1/matched_species_breeding_change.csv","f17b4a21e9e5a045a40f5a4af9019e3bbc011758"],
  future:["warming_species_breeding_v1/future_climate_coobserved_sites.csv","97ae24e98a0cb5f6b36e275d036cb4b71c953312"]
};
function parseCSV(s){
  const rows=[];let row=[],value="",quoted=false;
  for(let i=0;i<s.length;i++){
    const c=s[i];
    if(quoted){if(c==='"'&&s[i+1]==='"'){value+='"';i++}else if(c==='"')quoted=false;else value+=c;}
    else if(c==='"')quoted=true;else if(c===','){row.push(value);value="";}else if(c==='\n'){row.push(value.replace(/\r$/,""));if(row.length>1)rows.push(row);row=[];value="";}else value+=c;
  }
  if(row.length||value){row.push(value);rows.push(row);}
  if(quoted||!rows.length)throw Error("invalid CSV");
  const h=rows.shift();
  return rows.map((r,i)=>{if(r.length!==h.length)throw Error("CSV width "+i);return Object.fromEntries(h.map((v,j)=>[v,r[j]]));});
}
function csv(rows){if(!rows.length)throw Error("empty rows");const h=Object.keys(rows[0]);
  const quoted=v=>{let s=v==null?"":String(v);return /[,"\n\r]/.test(s)?'"'+s.replaceAll('"','""')+'"':s;};
  return h.join(",")+"\n"+rows.map(r=>h.map(k=>quoted(r[k])).join(",")).join("\n")+"\n";}
function mean(a){return a.reduce((s,x)=>s+x,0)/a.length;}
function slopeDecade(x,y){
  const xm=mean(x),ym=mean(y);
  const den=x.reduce((s,v)=>s+(v-xm)**2,0);
  if(den<=0)throw Error("invalid slope span");
  return 10*x.reduce((s,v,i)=>s+(v-xm)*(y[i]-ym),0)/den;
}
function assertNear(a,b,name,eps=1e-8){if(!Number.isFinite(a)||Math.abs(a-b)>eps)throw Error("Mismatch "+name+" "+a+" <> "+b);}
const data={};
for(const [k,[path,expect]] of Object.entries(originals)){
  const b=readFileSync(join(base,path));
  const sha=createHash("sha1").update(Buffer.from("blob "+b.length+"\0")).update(b).digest("hex");
  if(sha!==expect)throw Error("Original input blob drift "+k+": "+sha);
  data[k]=parseCSV(b.toString("utf8"));
}
if(data.bio.length!==2999||data.paired.length!==13||data.future.length!==32)throw Error("Original source cohort drift");
const index=new Map(data.bio.map(r=>[[r.site_id,r.species_id,r.season,r.method].join("|"),r]));
const results=[],allYears=[];
for(const p of data.paired){
  if(p.gate!=="1"||p.reference_species!=="ADPE"||p.method_reference!==p.method_compared)throw Error("Unmatched original count methods");
  const years=p.common_years.split(";").map(Number);
  if(years.length<5||years.at(-1)-years[0]<10)throw Error("Underlying long-term gate changed");
  const v=years.map(year=>{
    const ad=index.get([p.site_id,"ADPE",year,p.method_reference].join("|"));
    const other=index.get([p.site_id,p.compared_species,year,p.method_compared].join("|"));
    if(!ad||!other||ad.count===""||other.count==="")throw Error("Source missing count");
    const a=Number(ad.count),b=Number(other.count);
    if(!Number.isFinite(a)||!Number.isFinite(b)||a<0||b<0)throw Error("Invalid nests");
    return {site_id:p.site_id,region:p.region,compared_species:p.compared_species,year,adelie_nests:a,other_nests:b,
      coexistence_both_positive:a>0&&b>0,
      log1p_other_minus_adelie:Math.log1p(b)-Math.log1p(a),
      true_log_ratio_both_positive:a>0&&b>0?Math.log(b/a):null,
      observed_other_share:a+b>0?b/(a+b):null};
  });
  const xs=v.map(r=>r.year);
  const slopeAd=slopeDecade(xs,v.map(r=>Math.log1p(r.adelie_nests)));
  const slopeOther=slopeDecade(xs,v.map(r=>Math.log1p(r.other_nests)));
  const slopePseudo=slopeOther-slopeAd;
  assertNear(slopePseudo,+p.common_year_log1p_ratio_slope_decade,p.site_id+" "+p.compared_species);
  const positive=v.filter(r=>r.coexistence_both_positive);
  // Two distinguishable outputs: all-year co-observation and post-hoc positive-year sensitivity.
  // The all-year strict gate is independent of observed trend direction.
  const continuousCoobserved=positive.length===v.length;
  const validSubset=positive.length>=3&&(positive.at(-1).year-positive[0].year)>=10;
  const strictRatio=validSubset?slopeDecade(positive.map(r=>r.year),positive.map(r=>r.true_log_ratio_both_positive)):null;
  const firstDrop=continuousCoobserved?slopeDecade(xs.slice(1),v.slice(1).map(r=>r.true_log_ratio_both_positive)):null;
  const lastDrop=continuousCoobserved?slopeDecade(xs.slice(0,-1),v.slice(0,-1).map(r=>r.true_log_ratio_both_positive)):null;
  results.push({
    site_id:p.site_id,region:p.region,compared_species:p.compared_species,
    shared_years:v.length,years_both_species_positive:positive.length,
    years_adelie_zero:v.filter(r=>r.adelie_nests===0).length,
    years_other_zero:v.filter(r=>r.other_nests===0).length,
    all_common_years_both_positive:continuousCoobserved,
    all_positive_year_subset_support:validSubset,
    original_log1p_ratio_slope_decade:slopePseudo,
    true_log_ratio_positive_years_slope_decade:strictRatio,
    strict_slope_drop_first:firstDrop,strict_slope_drop_last:lastDrop,
    adelie_absolute_log1p_trend_decade:slopeAd,other_absolute_log1p_trend_decade:slopeOther,
    first_adelie_n:v[0].adelie_nests,last_adelie_n:v.at(-1).adelie_nests,
    first_other_n:v[0].other_nests,last_other_n:v.at(-1).other_nests,
    first_other_share:v[0].observed_other_share,last_other_share:v.at(-1).observed_other_share,
    other_unobserved_all_common_years:v.every(r=>r.other_nests===0),
    classification:continuousCoobserved?"both_species_observed_all_common_years":
      positive.length===0?"other_species_or_adelie_never_copositive":"partial_or_sparse_coobserved"
  });
  allYears.push(...v);
}
const strict=results.filter(r=>r.all_common_years_both_positive);
const bySpecies=Object.fromEntries(["GEPE","CHPE"].map(sp=>{
 const a=results.filter(r=>r.compared_species===sp),s=strict.filter(r=>r.compared_species===sp);
 return [sp,{
  original_pairs:a.length,positive_log1p_ratio_slope:a.filter(r=>r.original_log1p_ratio_slope_decade>0).length,
  strict_full_time_copositive_pairs:s.length,
  strict_actual_log_ratio_positive:s.filter(r=>r.true_log_ratio_positive_years_slope_decade>0).length,
  strict_endpoint_drop_last_positive:s.filter(r=>r.strict_slope_drop_last>0).length,
  absolute_adelie_declining_pairs:a.filter(r=>r.adelie_absolute_log1p_trend_decade<0).length,
  absolute_other_increasing_pairs:a.filter(r=>r.other_absolute_log1p_trend_decade>0).length,
  strong_synchronous_decline_and_growth:s.filter(r=>r.adelie_absolute_log1p_trend_decade<0&&r.other_absolute_log1p_trend_decade>0).length
 }];
}));
const physical=data.future.filter(r=>r.experiment==="ssp585"&&r.period==="2081-2100");
if(physical.length!==8)throw Error("Future group drift");
const summary={
  date:"2026-10-31",status:"original_breeding_composition_positive_result_source_audit_not_climate_causal_test",
  source_original_blobs:Object.fromEntries(Object.entries(originals).map(([k,v])=>[k,v[1]])),
  original_pairs:results.length,original_unique_sites:new Set(results.map(r=>r.site_id)).size,
  original_pairs_with_positive_log1p_ratio_slope:results.filter(r=>r.original_log1p_ratio_slope_decade>0).length,
  strict_pairs_all_shared_years_both_species_positive:strict.length,
  strict_unique_sites:new Set(strict.map(r=>r.site_id)).size,
  strict_true_log_ratio_positive:strict.filter(r=>r.true_log_ratio_positive_years_slope_decade>0).length,
  strict_endpoint_last_year_robust:strict.filter(r=>r.strict_slope_drop_last>0).length,
  original_species_comparisons:bySpecies,
  all_shared_years_other_zero:results.filter(r=>r.other_unobserved_all_common_years).map(r=>r.site_id+"|"+r.compared_species),
  sparse_cases:results.filter(r=>!r.all_common_years_both_positive).map(r=>({
    site:r.site_id,species:r.compared_species,both_positive_years:r.years_both_species_positive,
    years_adelie_zero:r.years_adelie_zero,years_other_zero:r.years_other_zero,
    original_log1p_ratio_decade:r.original_log1p_ratio_slope_decade})),
  true_species_replacement_statement:"Original 13/13 log1p ratio trends do not all represent biological species replacement. The strict all-common-year co-positive subset comprises 10 comparisons at 7 sites; one chinstrap contrast is endpoint-sensitive. The geographic sample and environmental association are not independent.",
  cmip6_exposure_of_original_8_sites:{
    condition:"SSP5-8.5, 2081-2100 versus model 1995-2014",
    model_mean_temperature_change_c:mean(physical.map(r=>+r.tas_C_change_model_mean)),
    model_mean_seaice_change_pp:mean(physical.map(r=>+r.SIC_pp_change_model_mean)),
    not_nest_count_forecast:true
  }
};
if(summary.original_pairs_with_positive_log1p_ratio_slope!==13||
   strict.length!==10||summary.strict_unique_sites!==7||
   summary.strict_true_log_ratio_positive!==10||
   summary.strict_endpoint_last_year_robust!==9||
   bySpecies.GEPE.strict_full_time_copositive_pairs!==6||
   bySpecies.CHPE.strict_full_time_copositive_pairs!==4||
   bySpecies.GEPE.absolute_other_increasing_pairs!==7||
   bySpecies.CHPE.absolute_other_increasing_pairs!==3||
   summary.all_shared_years_other_zero.join()!=="PETE|CHPE")
 throw Error("Frozen independent biological support gate failed");
mkdirSync(out,{recursive:true});
writeFileSync(join(out,"all_matched_breeding_years.csv"),csv(allYears));
writeFileSync(join(out,"pair_absolute_and_real_ratio_trends.csv"),csv(results));
writeFileSync(join(out,"summary.json"),JSON.stringify(summary,null,2)+"\n");
console.log(JSON.stringify(summary,null,2));
