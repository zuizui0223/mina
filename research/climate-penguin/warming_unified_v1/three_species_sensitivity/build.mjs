/**
 * Three-species complete-case sensitivity for warming-unified penguin paper.
 * Original same site / same year / same known method MAPPPD census counts.
 * Outcome-aware exploratory work; contract frozen prior to opening CHPE trajectories.
 * Run: node research/climate-penguin/warming_unified_v1/three_species_sensitivity/build.mjs
 */
import {readFileSync,writeFileSync,mkdirSync} from "node:fs";
import {createHash} from "node:crypto";
import {dirname,resolve} from "node:path";
import {fileURLToPath} from "node:url";
const dir=dirname(fileURLToPath(import.meta.url)), src=resolve(dir,"../../outputs"),out=resolve(dir,"outputs");
const input={
 pair:["warming_species_breeding_v1/matched_species_breeding_change.csv","f17b4a21e9e5a045a40f5a4af9019e3bbc011758"],
 counts:["comparison_audit/mapppd_unambiguous_site_seasons.csv","fc134e364cf38699fa7611d7dee5fbbbcb370c0a"]
};
function getPinned([rel,blob]){
 const bytes=readFileSync(resolve(src,rel));
 const now=createHash("sha1").update(Buffer.from("blob "+bytes.length+"\0")).update(bytes).digest("hex");
 if(now!==blob)throw Error("Source sha drift: "+rel+" "+now);
 return bytes.toString("utf8");
}
function csv(t){
 const rows=[];let row=[],buf="",quoted=false;
 for(let i=0;i<t.length;i++){const c=t[i];
  if(c==='"'){if(quoted&&t[i+1]==='"'){buf+='"';i++;}else quoted=!quoted;}
  else if(c===","&&!quoted){row.push(buf);buf="";}
  else if((c==="\r"||c==="\n")&&!quoted){if(c==="\r"&&t[i+1]==="\n")i++;row.push(buf);buf="";if(row.length>1||row.some(x=>x!==""))rows.push(row);row=[];}
  else buf+=c;
 }
 if(quoted)throw Error("CSV quote unclosed");
 if(row.length||buf!==""){row.push(buf);rows.push(row);}
 const hdr=rows.shift();
 if(!hdr||new Set(hdr).size!==hdr.length)throw Error("CSV header invalid");
 return rows.map((r,i)=>{if(r.length!==hdr.length)throw Error("CSV mismatch at "+i+" "+r.length+"/"+hdr.length);return Object.fromEntries(hdr.map((k,j)=>[k,r[j]]));});
}
function num(v,k){if(v===undefined||v===null||String(v).trim()==="")throw Error("Missing "+k);const n=Number(v);if(!Number.isFinite(n))throw Error("Nonfinite "+k+": "+v);return n;}
function integer(v,k){let n=num(v,k);if(!Number.isInteger(n))throw Error("Non-integer "+k);return n;}
function mean(a){return a.reduce((sum,x)=>sum+x,0)/a.length;}
function med(a){let b=[...a].sort((x,y)=>x-y);return b.length%2?b[(b.length-1)/2]:(b[b.length/2-1]+b[b.length/2])/2;}
function slope(recs,key){const xx=recs.map(r=>r.year),yy=recs.map(r=>r[key]),mx=mean(xx),my=mean(yy);
 const den=xx.reduce((a,x)=>a+(x-mx)**2,0);if(den<1e-12)throw Error("No time variance");
 return 10*xx.reduce((a,x,i)=>a+(x-mx)*(yy[i]-my),0)/den;
}
function writecsv(path,records){
 if(!records.length)throw Error("Empty CSV");
 const h=Object.keys(records[0]);const esc=x=>{let s=String(x??"");return /[,\"\r\n]/.test(s)?'"'+s.replaceAll('"','""')+'"':s};
 writeFileSync(path,[h.map(esc).join(","),...records.map(r=>h.map(k=>esc(r[k])).join(","))].join("\n")+"\n");
}
const pairs=csv(getPinned(input.pair)), counts=csv(getPinned(input.counts));
if(pairs.length!==13||counts.length!==2999)throw Error("Original MAPPPD grain changed");
const six=["ARDL","BISC","LION","LLAN","PCHA","PETE"];
const strict=pairs.filter(r=>six.includes(r.site_id)&&r.reference_species==="ADPE"&&r.compared_species==="GEPE");
if(strict.length!==6||new Set(strict.map(r=>r.site_id)).size!==6)throw Error("Original co-breeding cohort changed");
const by=new Map();
for(const r of counts){const k=r.site_id+"|"+r.species_id+"|"+r.season;if(by.has(k))throw Error("Duplicate accepted original count "+k);by.set(k,r);}
const panel=[],support=[],siteRows=[];
for(const p of strict){
 const years=p.common_years.split(";").map(y=>integer(y,"common_year"));
 if(years.length!==integer(p.n_shared_years,"n_shared_years")||new Set(years).size!==years.length||years.some((v,i)=>i&&v<=years[i-1]))throw Error("Malformed exact original shared years");
 const series=[];
 for(const year of years){
  const a=by.get(p.site_id+"|ADPE|"+year),g=by.get(p.site_id+"|GEPE|"+year),c=by.get(p.site_id+"|CHPE|"+year);
  if(!a||!g||a.method!==p.method_reference||g.method!==p.method_compared)throw Error("A/G original matched method drift");
  const A=integer(a.count,"ADPE"+year),G=integer(g.count,"GEPE"+year);
  if(A<=0||G<=0)throw Error("Original A/G not both positive");
  let eligible=!!c&&c.method===a.method&&c.method===g.method&&c.count!==""&&Number.isFinite(Number(c.count))&&Number.isInteger(Number(c.count))&&Number(c.count)>=0;
  support.push({site_id:p.site_id,year,Adelie_Gentoo_matched:true,
    chinstrap_record_present:!!c,chinstrap_same_known_method:!!c&&c.method===a.method&&c.method===g.method,
    chinstrap_valid_nest_count:!!c&&c.count!==""&&Number.isInteger(Number(c.count))&&Number(c.count)>=0,
    three_species_eligible:eligible,chinstrap_missing_not_zero:!eligible});
  if(!eligible)continue;
  const C=integer(c.count,"CHPE"+year),P2=A+G,P3=A+G+C;
  const r={site_id:p.site_id,region:p.region,year,source_method:a.method,
    Adelie_nests:A,Gentoo_nests:G,Chinstrap_nests:C,
    focal_pair_nests:P2,three_species_subtotal_nests:P3,
    Adelie_three_share:A/P3,Gentoo_three_share:G/P3,Chinstrap_three_share:C/P3,
    log_two_subtotal:Math.log(P2),log_three_subtotal:Math.log(P3),
    log1p_Chinstrap:Math.log1p(C)};
  if(Math.abs(r.Adelie_three_share+r.Gentoo_three_share+r.Chinstrap_three_share-1)>1e-12)throw Error("Share sum not 1");
  panel.push(r);series.push(r);
 }
 const summary={site_id:p.site_id,region:p.region,n_pair_years:years.length,n_triplet_years:series.length,
  first_triplet_year:series.length?series[0].year:"",last_triplet_year:series.length?series.at(-1).year:"",
  triple_span_years:series.length?series.at(-1).year-series[0].year:"",unavailable_original_pair_years:years.length-series.length};
 if(!series.length){siteRows.push({...summary,status:"NO_COMPLETE_THREE_SPECIES_YEARS"});continue;}
 if(series.length<5||series.at(-1).year-series[0].year<10)throw Error("Tri-support gate fails "+p.site_id);
 const first=series[0],last=series.at(-1);
 const delta=(k)=>last[k]-first[k];
 const percent=(k)=>100*(last[k]/first[k]-1);
 const sl2=slope(series,"log_two_subtotal"),sl3=slope(series,"log_three_subtotal");
 const eligibleRobust=series.length>=6;
 const drop2first=eligibleRobust?slope(series.slice(1),"log_two_subtotal"):null,
       drop2last=eligibleRobust?slope(series.slice(0,-1),"log_two_subtotal"):null,
       drop3first=eligibleRobust?slope(series.slice(1),"log_three_subtotal"):null,
       drop3last=eligibleRobust?slope(series.slice(0,-1),"log_three_subtotal"):null;
 siteRows.push({...summary,status:"COMPLETE_THREE_SPECIES_SERIES",
  first_Adelie:first.Adelie_nests,last_Adelie:last.Adelie_nests,
  first_Gentoo:first.Gentoo_nests,last_Gentoo:last.Gentoo_nests,
  first_Chinstrap:first.Chinstrap_nests,last_Chinstrap:last.Chinstrap_nests,
  delta_Adelie_nests:delta("Adelie_nests"),delta_Gentoo_nests:delta("Gentoo_nests"),delta_Chinstrap_nests:delta("Chinstrap_nests"),
  first_pair_total:first.focal_pair_nests,last_pair_total:last.focal_pair_nests,
  first_three_total:first.three_species_subtotal_nests,last_three_total:last.three_species_subtotal_nests,
  pair_pct_change:percent("focal_pair_nests"),three_pct_change:percent("three_species_subtotal_nests"),
  pair_log_slope_decade:sl2,three_log_slope_decade:sl3,
  chinstrap_log1p_slope_decade:slope(series,"log1p_Chinstrap"),
  Adelie_first_share:first.Adelie_three_share,Adelie_last_share:last.Adelie_three_share,
  Gentoo_first_share:first.Gentoo_three_share,Gentoo_last_share:last.Gentoo_three_share,
  Chinstrap_first_share:first.Chinstrap_three_share,Chinstrap_last_share:last.Chinstrap_three_share,
  pair_endpoint_positive:delta("focal_pair_nests")>0,three_endpoint_positive:delta("three_species_subtotal_nests")>0,
  endpoint_direction_agrees:Math.sign(delta("focal_pair_nests"))===Math.sign(delta("three_species_subtotal_nests")),
  pair_slope_positive:sl2>0,three_slope_positive:sl3>0,
  slope_direction_agrees:Math.sign(sl2)===Math.sign(sl3),
  pair_dropfirst_slope_decade:drop2first,pair_droplast_slope_decade:drop2last,
  three_dropfirst_slope_decade:drop3first,three_droplast_slope_decade:drop3last,
  pair_positive_endpoint_deletion_robust:eligibleRobust?sl2>0&&drop2first>0&&drop2last>0:null,
  three_positive_endpoint_deletion_robust:eligibleRobust?sl3>0&&drop3first>0&&drop3last>0:null
 });
}
panel.sort((a,b)=>a.site_id.localeCompare(b.site_id)||a.year-b.year);
siteRows.sort((a,b)=>a.site_id.localeCompare(b.site_id));
support.sort((a,b)=>a.site_id.localeCompare(b.site_id)||a.year-b.year);
const used=siteRows.filter(r=>r.status==="COMPLETE_THREE_SPECIES_SERIES");
if(panel.length!==54||support.length!==67||used.length!==5||siteRows.length!==6||used.reduce((s,r)=>s+r.n_triplet_years,0)!==54||
   !siteRows.find(r=>r.site_id==="BISC"&&r.n_triplet_years===0))throw Error("Pre-frozen support 54/67/5/BISC failed");
const count=key=>used.filter(x=>x[key]).length;
const threeEndpointPositive=count("three_endpoint_positive"),
      threeSlopePositive=count("three_slope_positive");
const result={
 status:"EXPLORATORY_FULL_THREE_SPECIES_SENSITIVITY_COMPLETED",
 source_blobs:Object.fromEntries(Object.entries(input).map(([k,v])=>[k,v[1]])),
 n_original_focal_pair_site_years:support.length,n_triplet_site_years:panel.length,n_triplet_sites:used.length,
 n_triplet_regions:new Set(used.map(x=>x.region)).size,
 excluded_site:"BISC (no same-method CHPE observations)",n_missing_chinstrap_records:support.filter(x=>!x.three_species_eligible).length,
 same_year_pair_positive_endpoints:count("pair_endpoint_positive"),
 same_year_three_positive_endpoints:threeEndpointPositive,
 same_year_pair_positive_slopes:count("pair_slope_positive"),
 same_year_three_positive_slopes:threeSlopePositive,
 endpoint_sign_concordance:count("endpoint_direction_agrees"),
 slope_sign_concordance:count("slope_direction_agrees"),
 robust_three_positive_slopes:used.filter(x=>x.three_positive_endpoint_deletion_robust===true).length,
 eligible_three_endpoint_robustness_sites:used.filter(x=>x.three_positive_endpoint_deletion_robust!==null).length,
 median_three_pct_change:med(used.map(x=>x.three_pct_change)),
 range_three_pct_change:[Math.min(...used.map(x=>x.three_pct_change)),Math.max(...used.map(x=>x.three_pct_change))],
 verdict:threeEndpointPositive>=4&&threeSlopePositive>=4
   ?"THREE_SPECIES_SUBTOTAL_INCREASE_RECURS_IN_SELECTED_FIVE_SITES"
   :"FOCAL_PAIR_COMPENSATION_NOT_ROBUST_TO_COMPLETE_THREE_SPECIES",
 explanation_constraints:[
  "Three counted penguin species are not necessarily the entire local penguin community.",
  "All 54 site-years selected by complete, known-method CHPE; BISC cannot be checked.",
  "Site histories differ in year span; five sites only from two regions.",
  "A zero CHPE recorded nest count stays zero; missing counts are never converted to zero.",
  "Exploratory after two-species endpoints known. No causal warming or individual-replacement claim."
 ]};
mkdirSync(out,{recursive:true});
writecsv(resolve(out,"three_species_same_year_54.csv"),panel);
writecsv(resolve(out,"site_6_support_gate.csv"),support);
writecsv(resolve(out,"site_6_summary_with_BISC_unavailable.csv"),siteRows);
writeFileSync(resolve(out,"summary.json"),JSON.stringify(result,null,2)+"\n");
console.log("THREE_SPECIES_RESULT="+JSON.stringify(result));
console.log("THREE_SPECIES_SITE_ROWS="+JSON.stringify(siteRows));
