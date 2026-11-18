/**
 * Same-year source-pinned six-site Adélie/Gentoo focal-pair sum.
 * This is exploratory analysis after prior endpoint results, not preregistration.
 * Run: node research/climate-penguin/warming_unified_v1/paired_compensation/build.mjs
 */
import {readFileSync,writeFileSync,mkdirSync} from "node:fs";
import {createHash} from "node:crypto";
import {dirname,resolve} from "node:path";
import {fileURLToPath} from "node:url";
const here=dirname(fileURLToPath(import.meta.url));
const root=resolve(here,"../../outputs");
const dest=resolve(here,"outputs");
const sources={
  matched:["warming_species_breeding_v1/matched_species_breeding_change.csv",
    "f17b4a21e9e5a045a40f5a4af9019e3bbc011758"],
  observations:["comparison_audit/mapppd_unambiguous_site_seasons.csv",
    "fc134e364cf38699fa7611d7dee5fbbbcb370c0a"]
};
function fetchPinned([name,expected]){
  let b=readFileSync(resolve(root,name));
  let sha=createHash("sha1").update(Buffer.from("blob "+b.length+"\0")).update(b).digest("hex");
  if(sha!==expected)throw Error("Input drift "+name+" "+sha);
  return b.toString("utf8");
}
function csv(source){
  let rows=[],row=[],value="",quoted=false;
  for(let i=0;i<source.length;i++){
    const c=source[i];
    if(c==='"'){
      if(quoted&&source[i+1]==='"'){value+='"';i++}
      else quoted=!quoted;
    }else if(c===","&&!quoted){row.push(value);value=""}
    else if((c==="\n"||c==="\r")&&!quoted){
      if(c==="\r"&&source[i+1]==="\n")i++;
      row.push(value); value="";
      if(row.length>1||row.some(v=>v!==""))rows.push(row);
      row=[];
    }else value+=c;
  }
  if(quoted)throw Error("Unterminated CSV string");
  if(row.length||value!==""){row.push(value);rows.push(row)}
  const h=rows.shift();
  if(!h||new Set(h).size!==h.length)throw Error("Bad CSV headers");
  return rows.map((z,i)=>{
    if(z.length!==h.length)throw Error("Bad CSV column count at "+(i+2));
    return Object.fromEntries(h.map((key,j)=>[key,z[j]]));
  });
}
function n(v,key){
  let x=Number(v);if(v===""||!Number.isFinite(x))throw Error("Invalid "+key+" "+v);
  return x;
}
function int(v,key){let x=n(v,key);if(!Number.isInteger(x))throw Error("Noninteger "+key);return x}
function mean(a){return a.reduce((s,x)=>s+x,0)/a.length}
function median(a){let b=[...a].sort((x,y)=>x-y);return b.length%2?b[(b.length-1)/2]:(b[b.length/2-1]+b[b.length/2])/2}
function ols(a,xKey,yKey){
  const x=a.map(r=>+r[xKey]), y=a.map(r=>+r[yKey]);
  let xm=mean(x),ym=mean(y),den=x.reduce((s,v)=>s+(v-xm)**2,0);
  if(den<1e-8)throw Error("Insufficient year spread");
  return 10*x.reduce((s,v,i)=>s+(v-xm)*(y[i]-ym),0)/den;
}
function rank(xs){
  let o=xs.map((x,i)=>({x,i})).sort((a,b)=>a.x-b.x),r=[];
  for(let a=0;a<o.length;){let b=a+1;while(b<o.length&&o[b].x===o[a].x)b++;
    let value=(a+1+b)/2;for(let z=a;z<b;z++)r[o[z].i]=value;a=b;}
  return r;
}
function pearson(x,y){
  let xm=mean(x),ym=mean(y);
  let num=x.reduce((s,v,i)=>s+(v-xm)*(y[i]-ym),0);
  let dx=x.reduce((s,v)=>s+(v-xm)**2,0),dy=y.reduce((s,v)=>s+(v-ym)**2,0);
  return dx>0&&dy>0?num/Math.sqrt(dx*dy):null;
}
function writeCSV(path,rows){
  if(!rows.length)throw Error("Empty table");
  const h=Object.keys(rows[0]);
  const cell=x=>{let v=String(x??"");return /[",\n\r]/.test(v)?'"'+v.replaceAll('"','""')+'"':v};
  writeFileSync(path,[h.map(cell).join(","),...rows.map(row=>h.map(k=>cell(row[k])).join(","))].join("\n")+"\n");
}
let matched=csv(fetchPinned(sources.matched));
let original=csv(fetchPinned(sources.observations));
let focus=new Set(["ARDL","BISC","LION","LLAN","PCHA","PETE"]);
let pairs=matched.filter(p=>focus.has(p.site_id)&&p.reference_species==="ADPE"&&p.compared_species==="GEPE");
if(pairs.length!==6||new Set(pairs.map(r=>r.site_id)).size!==6)throw Error("Wrong strict paired sites");
let index=new Map(),clash=[];
for(const r of original){
  let k=[r.site_id,r.species_id,r.season].join("|");
  if(index.has(k))clash.push(k);
  index.set(k,r);
}
if(clash.length)throw Error("Original unique count source contains duplicate site/species/season: "+clash.slice(0,3));
let siteRows=[],all=[],chinstrap=[];
for(const p of pairs){
  const site=p.site_id;let ys=p.common_years.split(";").map(y=>int(y,"source shared year"));
  if(new Set(ys).size!==ys.length||ys.some((y,i)=>i>0&&y<ys[i-1]))throw Error("Year order");
  if(ys.length!==int(p.n_shared_years,"n_shared_years")||ys.length<5)throw Error("Source shared years mismatch "+site);
  let series=[];
  for(const year of ys){
    let a=index.get([site,"ADPE",year].join("|")),g=index.get([site,"GEPE",year].join("|"));
    if(!a||!g)throw Error("Missing matched species "+site+"/"+year);
    if(a.method!==p.method_reference||g.method!==p.method_compared)throw Error("Method not comparable "+site+"/"+year);
    let A=n(a.count,"Adelie"),G=n(g.count,"Gentoo");
    if(A<=0||G<=0||!Number.isInteger(A)||!Number.isInteger(G))throw Error("Nonpositive/inaccurate nest count "+site+"/"+year);
    let P=A+G;
    let record={site_id:site,region:p.region,year,Adelie_nests:A,Gentoo_nests:G,
      focal_pair_subtotal_nests:P,Gentoo_share_within_pair:G/P,
      log_Adelie:Math.log(A),log_Gentoo:Math.log(G),log_focal_pair_subtotal:Math.log(P),
      log_Gentoo_Adelie_ratio:Math.log(G/A)};
    series.push(record);all.push(record);
    let h=index.get([site,"CHPE",year].join("|"));
    chinstrap.push({site_id:site,year,matched_Adelie_Gentoo_methods:p.method_reference+"|"+p.method_compared,
      chinstrap_record_exists:!!h,chinstrap_method:h?.method??"",chinstrap_nests:(h?.count??""),
      chinstrap_method_matches_both:!!h && h.method===p.method_reference&&h.method===p.method_compared});
  }
  let first=series[0],last=series.at(-1);
  let checks=[
    ["first_ADPE_n",first.Adelie_nests],["last_ADPE_n",last.Adelie_nests],
    ["first_other_n",first.Gentoo_nests],["last_other_n",last.Gentoo_nests],
    ["first_year",first.year],["last_year",last.year]];
  for(const [key,v] of checks){if(n(p[key],key)!==v)throw Error("Endpoint source drift "+site+" "+key);}
  if(!(first.Adelie_nests>last.Adelie_nests && first.Gentoo_nests<last.Gentoo_nests))
    throw Error("Reciprocal source evidence not reproduced "+site);
  const adloss=first.Adelie_nests-last.Adelie_nests,gengain=last.Gentoo_nests-first.Gentoo_nests;
  let slope=ols(series,"year","log_focal_pair_subtotal"),
      noFirst=ols(series.slice(1),"year","log_focal_pair_subtotal"),
      noLast=ols(series.slice(0,-1),"year","log_focal_pair_subtotal"),
      pearsonr=pearson(rank(series.map(x=>x.year)),rank(series.map(x=>x.log_focal_pair_subtotal)));
  siteRows.push({site_id:site,region:p.region,n_shared_years:series.length,year_first:first.year,year_last:last.year,
    initial_Adelie_nests:first.Adelie_nests,final_Adelie_nests:last.Adelie_nests,
    initial_Gentoo_nests:first.Gentoo_nests,final_Gentoo_nests:last.Gentoo_nests,
    initial_focal_pair_subtotal_nests:first.focal_pair_subtotal_nests,
    final_focal_pair_subtotal_nests:last.focal_pair_subtotal_nests,
    subtotal_pct_change:100*(last.focal_pair_subtotal_nests/first.focal_pair_subtotal_nests-1),
    ratio_fold:(last.Gentoo_nests/last.Adelie_nests)/(first.Gentoo_nests/first.Adelie_nests),
    Gentoo_gain_divided_by_Adelie_loss:gengain/adloss,
    Gentoo_share_first:first.Gentoo_share_within_pair,Gentoo_share_last:last.Gentoo_share_within_pair,
    all_year_log_subtotal_slope_per_decade:slope,
    all_year_log_Adelie_slope_per_decade:ols(series,"year","log_Adelie"),
    all_year_log_Gentoo_slope_per_decade:ols(series,"year","log_Gentoo"),
    all_year_log_Gentoo_Adelie_ratio_slope_per_decade:ols(series,"year","log_Gentoo_Adelie_ratio"),
    subtotal_drop_first_year_slope_per_decade:noFirst,
    subtotal_drop_last_year_slope_per_decade:noLast,
    subtotal_Spearman_rho:pearsonr,
    subtotal_endpoint_increase:last.focal_pair_subtotal_nests>first.focal_pair_subtotal_nests,
    subtotal_all_year_increase:slope>0,
    subtotal_deletion_sign_stable:slope>0&&noFirst>0&&noLast>0,
    focal_pair_only_not_entire_penguin_community:true});
}
all.sort((a,b)=>a.site_id.localeCompare(b.site_id)||a.year-b.year);
siteRows.sort((a,b)=>a.site_id.localeCompare(b.site_id));
if(all.length!==67||siteRows.length!==6)throw Error("Fixed 67 paired site-years not recovered");
const sum={
 status:"POST_HOC_EXPLORATORY_SOURCE_PINNED",
 units:"6 strictly paired same-method site records / 67 site-years / 2 regions",
 source_blobs:Object.fromEntries(Object.entries(sources).map(([k,v])=>[k,v[1]])),
 n_sites:siteRows.length,n_pair_site_years:all.length,n_regions:new Set(siteRows.map(r=>r.region)).size,
 count_endpoint_subtotal_increases:siteRows.filter(r=>r.subtotal_endpoint_increase).length,
 count_all_year_subtotal_growth_slopes:siteRows.filter(r=>r.subtotal_all_year_increase).length,
 count_positive_slope_stable_to_drop_first_and_last:siteRows.filter(r=>r.subtotal_deletion_sign_stable).length,
 median_subtotal_pct_change:median(siteRows.map(r=>r.subtotal_pct_change)),
 median_ratio_fold:median(siteRows.map(r=>r.ratio_fold)),
 min_subtotal_pct_change:Math.min(...siteRows.map(r=>r.subtotal_pct_change)),
 max_subtotal_pct_change:Math.max(...siteRows.map(r=>r.subtotal_pct_change)),
 chinstrap_source:{
  n_paired_years_with_source_chinstrap_record:chinstrap.filter(r=>r.chinstrap_record_exists).length,
  n_paired_years_with_same_method_chinstrap_record:chinstrap.filter(r=>r.chinstrap_method_matches_both).length,
  n_all_paired_site_years:chinstrap.length
 },
 verdict:siteRows.filter(r=>r.subtotal_endpoint_increase).length>=5&&siteRows.filter(r=>r.subtotal_deletion_sign_stable).length>=4
   ?"FOCAL_PAIR_SUBTOTAL_COMPENSATION_DESCRIPTIVE_SUPPORTED":"MIXED_OR_ENDPOINT_SENSITIVE",
 caution:[
 "Two-species subtotal is not full penguin-community total; Chinstrap may be present.",
 "Paired site years across six sites do not constitute independent climate trials.",
 "Source-selected sites and heterogeneous observation spans prevent population-level prevalence inference.",
 "Site-specific total counts cannot distinguish reproduction, survival, movement or environmental cause.",
 "This is post-result exploratory analysis; no unplanned p-value or significance claim."
 ]
};
mkdirSync(dest,{recursive:true});
writeCSV(resolve(dest,"six_site_yearly_focal_pair_counts.csv"),all);
writeCSV(resolve(dest,"six_site_compensation_metrics.csv"),siteRows);
writeCSV(resolve(dest,"chinstrap_observability_audit.csv"),chinstrap);
writeFileSync(resolve(dest,"summary.json"),JSON.stringify(sum,null,2)+"\n");
console.log("FOCAL_PAIR_RESULT="+JSON.stringify(sum));
console.log("SITE_METRICS="+JSON.stringify(siteRows));
