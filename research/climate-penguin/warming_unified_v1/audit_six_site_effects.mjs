// Source-pinned descriptive audit of reciprocal co-breeding count changes.
import {readFileSync, mkdirSync, writeFileSync} from "node:fs";
import {createHash} from "node:crypto";
import {fileURLToPath} from "node:url";
import {dirname,resolve} from "node:path";
const here=dirname(fileURLToPath(import.meta.url));
const output=resolve(here,"outputs");
const root=resolve(here,"../outputs");
const integrated=resolve(here,"data/six_site_original_breeding_ice.csv");
const sources={
  pair:["warming_species_breeding_v1/matched_species_breeding_change.csv","f17b4a21e9e5a045a40f5a4af9019e3bbc011758"],
  trend:["warming_species_breeding_v1/historical_species_site_trends.csv","2b6c0793ea9f9ea9acf0771052cf7a2ad9ab335b"],
};
function pinned([path,expected]) {
  const b=readFileSync(resolve(root,path));
  const sha=createHash("sha1").update(Buffer.from("blob "+b.length+"\0")).update(b).digest("hex");
  if(sha!==expected) throw new Error("Source-drift "+path+": "+sha);
  return b.toString("utf8");
}
function csv(t){
  const lines=t.trim().split(/\r?\n/);const hdr=lines.shift().split(",");
  return lines.map(l=>{let parts=l.split(",");if(parts.length!==hdr.length)throw new Error("bad CSV format");
    return Object.fromEntries(hdr.map((h,i)=>[h,parts[i]]));});
}
const pairs=csv(pinned(sources.pair)),trends=csv(pinned(sources.trend)),six=csv(readFileSync(integrated,"utf8"));
if(pairs.length!==13||trends.length!==54||six.length!==6)throw new Error("source support changed");
const names=["ARDL","BISC","LION","LLAN","PCHA","PETE"];
if(names.sort().join("|")!==six.map(x=>x.site_id).sort().join("|"))throw new Error("strict six changed");
const tmap=new Map(trends.map(x=>[x.site_id+"/"+x.species_id,x]));
const pmap=new Map(pairs.filter(x=>x.compared_species==="GEPE").map(x=>[x.site_id,x]));
const individual=[];
for(const x of six){
  const id=x.site_id,p=pmap.get(id),a=tmap.get(id+"/ADPE"),g=tmap.get(id+"/GEPE");
  if(!p||!a||!g)throw new Error("Unmatched source "+id);
  for(const [key,target] of [["first_ADPE_n","first_Adelie"],["last_ADPE_n","last_Adelie"],["first_other_n","first_Gentoo"],["last_other_n","last_Gentoo"],["first_year","year0"],["last_year","year1"],["n_shared_years","common_years_n"]]){
    if(+p[key]!==+x[target])throw new Error("source conflict "+id+": "+key);
  }
  const n0=+x.first_Adelie,n1=+x.last_Adelie,m0=+x.first_Gentoo,m1=+x.last_Gentoo;
  if(Math.min(n0,n1,m0,m1)<=0)throw new Error("non-positive strict co-breeding site");
  if(!(+a.slope_log1p_count_decade<0&&+g.slope_log1p_count_decade>0))throw new Error("opposite trend sign failed");
  if(!(n1<n0 && m1>m0))throw new Error("count endpoints do not support reciprocal shift");
  if(!(+(x.log_ratio_slope_decade)>0&&+(x.aug_nov_SIC_full_1991_2020_pp_decade)<0))
    throw new Error("source ratio or full-period SIC sign drift");
  individual.push({site:id,region:x.region,first_year:+x.year0,last_year:+x.year1,common_years:+x.common_years_n,
    first_Adelie:n0,last_Adelie:n1,first_Gentoo:m0,last_Gentoo:m1,
    Adelie_pct_change:100*(n1/n0-1),Gentoo_pct_change:100*(m1/m0-1),
    first_Gentoo_Adelie_ratio:m0/n0,last_Gentoo_Adelie_ratio:m1/n1,
    first_last_ratio_fold:(m1*n0)/(n1*m0),
    common_year_ratio_slope_decade:+x.log_ratio_slope_decade,
    sep_SIC_observed_years_pp_decade:+x.sep_SIC_observed_years_pp_decade,
    augnov_SIC_observed_years_pp_decade:+x.aug_nov_SIC_observed_years_pp_decade,
    augnov_SIC_full_period_pp_decade:+x.aug_nov_SIC_full_1991_2020_pp_decade});
}
const median=xs=>{let a=[...xs].sort((a,b)=>a-b);return a.length%2?a[(a.length-1)/2]:(a[a.length/2-1]+a[a.length/2])/2};
const summary={
  status:"SOURCE_PINNED_DESCRIPTIVE_ONLY",
  source_git_blobs:Object.fromEntries(Object.entries(sources).map(([k,v])=>[k,v[1]])),
  six_site_input_note:"cross-check descriptive SIC from previously audited six-site file (not independent climate reconstruction)",
  n_sites:individual.length,n_regions:new Set(individual.map(x=>x.region)).size,
  n_site_years:individual.reduce((a,x)=>a+x.common_years,0),
  Adelie_absolute_declines:individual.filter(x=>x.Adelie_pct_change<0).length,
  Gentoo_absolute_increases:individual.filter(x=>x.Gentoo_pct_change>0).length,
  Gentoo_Adelie_ratio_grows:individual.filter(x=>x.first_last_ratio_fold>1).length,
  ratio_fold_min:Math.min(...individual.map(x=>x.first_last_ratio_fold)),
  ratio_fold_max:Math.max(...individual.map(x=>x.first_last_ratio_fold)),
  ratio_fold_median:median(individual.map(x=>x.first_last_ratio_fold)),
  median_Adelie_first_last_change_pct:median(individual.map(x=>x.Adelie_pct_change)),
  median_Gentoo_first_last_change_pct:median(individual.map(x=>x.Gentoo_pct_change)),
  ratio_fold_median_leave_one_site: individual.map((_,i)=>
    median(individual.filter((_,j)=>i!==j).map(x=>x.first_last_ratio_fold))
  ).sort((a,b)=>a-b),
  SIC_full_AugNov_decrease:individual.filter(x=>x.augnov_SIC_full_period_pp_decade<0).length,
  SIC_censusyear_September_increase:individual.filter(x=>x.sep_SIC_observed_years_pp_decade>0).length,
  SIC_censusyear_AugNov_increase:individual.filter(x=>x.augnov_SIC_observed_years_pp_decade>0).length,
  limitations:["Six focal sites in two geographic regions; shared climate cells are not six independent experimental replicates.",
   "First/last ratios are descriptive: site periods differ, some initial counts are low.",
   "Population changes and SIC slopes are observational; no warming attribution, competition, dispersal or future nest forecast.",
   "Census-year SIC and 1991–2020 SIC are distinct time windows and month definitions."]
};
if(summary.n_site_years!==67||summary.SIC_censusyear_September_increase!==4||
   summary.SIC_censusyear_AugNov_increase!==2||summary.SIC_full_AugNov_decrease!==6)
   throw new Error("Frozen six-site support has drifted");
mkdirSync(output,{recursive:true});
writeFileSync(resolve(output,"six_site_reciprocal_effects.csv"),
   [Object.keys(individual[0]).join(","),...individual.map(x=>Object.values(x).join(","))].join("\n")+"\n");
writeFileSync(resolve(output,"reciprocal_summary.json"),JSON.stringify(summary,null,2)+"\n");
console.log("SIX_SITE_RESULT="+JSON.stringify(summary));
