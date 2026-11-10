// Reproduce LaRue et al. 2024 50 Emperor colony Bayesian *marginal* indices
// and 2009/2018 same-source-count terrestrial penguin fixed-roster comparison.
// The fixed-composition benchmark is arithmetic; never claim a causal substrate effect.
import {readFileSync,writeFileSync,mkdirSync} from "node:fs";
import {join,resolve} from "node:path";
import {createHash} from "node:crypto";
const ROOT=resolve("research/climate-penguin/outputs"),DIR=join(ROOT,"emperor_ice_land_substrate_v1");
const FILE={
 emperor:["emperor_ice_land_substrate_v1/author_colony_summary.csv","133c900c9dfbf2ce23ca403c9a59edecd9b51ace"],
 global:["emperor_ice_land_substrate_v1/author_global_abundance.csv","0d1e79adca696b61f4c6f0d4d0eee6fa6d628a29"],
 change:["emperor_ice_land_substrate_v1/author_global_change.csv","b2a603e8b1d7d605b46eebb4b547671fe6eb68e1"],
 land:["comparison_audit/mapppd_unambiguous_site_seasons.csv","fc134e364cf38699fa7611d7dee5fbbbcb370c0a"]
};
function csvParse(s){
 let rows=[],row=[],v="",q=false;
 for(let i=0;i<s.length;i++){const c=s[i];
  if(q){if(c==='"'&&s[i+1]==='"'){v+='"';i++}else if(c==='"')q=false;else v+=c}
  else if(c==='"')q=true;else if(c===','){row.push(v);v=""}
  else if(c==='\n'){row.push(v.replace(/\r$/,""));if(row.length>1)rows.push(row);row=[];v=""}else v+=c;
 }
 if(row.length||v){row.push(v);rows.push(row)}
 if(q||rows.length<2)throw Error("Malformed source CSV");
 let h=rows.shift();
 return rows.map((r,i)=>{if(r.length!==h.length)throw Error("Wrong CSV fields at "+i);
  return Object.fromEntries(h.map((k,j)=>[k,r[j]]))});
}
function writeCSV(filename,rows){
 if(rows.length===0)throw Error("Empty output CSV "+filename);
 let keys=Object.keys(rows[0]),esc=x=>{let s=x===null||x===undefined?"":String(x);return /[,"\n\r]/.test(s)?'"'+s.replaceAll('"','""')+'"':s};
 writeFileSync(join(DIR,filename),keys.join(",")+"\n"+rows.map(r=>keys.map(k=>esc(r[k])).join(",")).join("\n")+"\n");
}
const receipt=JSON.parse(readFileSync(join(DIR,"expected_receipt.json"),"utf8"));
const D={};
for(const [name,[path,sha]] of Object.entries(FILE)){
 const bytes=readFileSync(join(ROOT,path));
 const hash=createHash("sha1").update(Buffer.from("blob "+bytes.length+"\0")).update(bytes).digest("hex");
 if(hash!==sha||receipt.blobs[name]!==sha)throw Error("Original author/source file changed "+name+" "+hash);
 D[name]=csvParse(bytes.toString("utf8"));
}
if(D.emperor.length!==500||D.global.length!==10||D.change.length!==1||D.land.length!==2999)
 throw Error("Source input sizes drifted");
const sum=x=>x.reduce((s,v)=>s+v,0),neff=x=>{let s=sum(x);return s*s/sum(x.map(v=>v*v))},pc=(a,b)=>100*(b/a-1);
const ids=[...new Set(D.emperor.map(x=>x.site_id))].sort(),years=[...new Set(D.emperor.map(x=>+x.year))].sort((a,b)=>a-b);
if(ids.length!==50||years.length!==10||years[0]!==2009||years.at(-1)!==2018)throw Error("50 colony 10 year source changed");
const idx=new Map();
for(const r of D.emperor){let key=r.site_id+"|"+r.year;if(idx.has(key))throw Error("duplicate original model output");
 for(const col of ["N_mean","N_median","N_se","N_q025","N_q975"])if(!Number.isFinite(+r[col])||+r[col]<0)throw Error("invalid posterior marginal");
 idx.set(key,r)}
const val=(id,year,key)=>+idx.get(id+"|"+year)[key];
const vec=(list,y,key)=>list.map(id=>val(id,y,key));
const annual=years.map(year=>{
 let a=vec(ids,year,"N_mean"),b=vec(ids,year,"N_median"),published=D.global.find(x=>+x.Year===year);
 if(!published||Math.abs(sum(a)- +published.N_mean)>1e-7)throw Error("Source global mean not reproduced "+year);
 return{year,colonies:ids.length,sum_posterior_marginal_means:sum(a),
 sum_posterior_marginal_medians:sum(b),N_eff_from_posterior_marginal_means:neff(a),
 N_eff_from_posterior_marginal_medians:neff(b),
 number_positive_modelled_index:a.filter(x=>x>0).length,number_modelled_zero:a.filter(x=>x===0).length,
 published_global_joint_posterior_mean:+published.N_mean,published_global_joint_posterior_median:+published.N_median}});
const a=vec(ids,2009,"N_mean"),b=vec(ids,2018,"N_mean"),c=vec(ids,2009,"N_median"),d=vec(ids,2018,"N_median");
const persistent=ids.filter(id=>val(id,2009,"N_mean")>0&&val(id,2018,"N_mean")>0);
const lost=ids.filter(id=>val(id,2009,"N_mean")>0&&val(id,2018,"N_mean")===0);
const gained=ids.filter(id=>val(id,2009,"N_mean")===0&&val(id,2018,"N_mean")>0);
const reduced=ids.map(id=>lost.includes(id)?0:val(id,2009,"N_mean"));
const p0=vec(persistent,2009,"N_mean"),p1=vec(persistent,2018,"N_mean");
const nullN=neff(a.map(x=>x*sum(b)/sum(a)));
const end={
 mean_index_2009:sum(a),mean_index_2018:sum(b),mean_index_change_pct:pc(sum(a),sum(b)),
 sum_colony_medians_2009:sum(c),sum_colony_medians_2018:sum(d),sum_colony_medians_change_pct:pc(sum(c),sum(d)),
 N_eff_from_means_2009:neff(a),N_eff_from_means_2018:neff(b),
 N_eff_from_means_change_pct:pc(neff(a),neff(b)),
 N_eff_from_medians_2009:neff(c),N_eff_from_medians_2018:neff(d),
 N_eff_from_medians_change_pct:pc(neff(c),neff(d)),
 persistent_colonies:persistent.length,positive_to_modelled_zero:lost.length,modelled_zero_to_positive:gained.length,
 lost_codes:lost.join(";"),gained_codes:gained.join(";"),
 initial_weight_fraction_lost_pct:100*sum(vec(lost,2009,"N_mean"))/sum(a),
 fixed_composition_null_N_eff_2018:nullN,fixed_composition_null_delta_pct:pc(neff(a),nullN),
 zero_only_counterfactual_delta_N_eff_pct:pc(neff(a),neff(reduced)),
 persistent_only_N_eff_2009:neff(p0),persistent_only_N_eff_2018:neff(p1),
 persistent_only_N_eff_change_pct:pc(neff(p0),neff(p1)),
 published_global_change_posterior_median:+D.change[0]["50%"],
 published_global_decline_probability:+D.change[0].Prob_Decline};
const status=ids.map(id=>({site_id:id,ice_region:idx.get(id+"|2009").ice_reg,
 model_mean_2009:val(id,2009,"N_mean"),model_mean_2018:val(id,2018,"N_mean"),
 model_median_2009:val(id,2009,"N_median"),model_median_2018:val(id,2018,"N_median"),
 stayed_positive:persistent.includes(id),became_modelled_zero:lost.includes(id),
 became_modelled_positive:gained.includes(id),annual_colony_movement_not_observed:true}));
const yearsDelta=years.slice(1).map(year=>{
 const before=vec(ids,year-1,"N_mean"),after=vec(ids,year,"N_mean");
 const disappearing=ids.filter(id=>val(id,year-1,"N_mean")>0&&val(id,year,"N_mean")===0);
 const reappearing=ids.filter(id=>val(id,year-1,"N_mean")===0&&val(id,year,"N_mean")>0);
 return{start_year:year-1,end_year:year,index_change_pct:pc(sum(before),sum(after)),
 N_eff_change_pct:pc(neff(before),neff(after)),became_modelled_zero:disappearing.length,
 became_positive:reappearing.length,zero_codes:disappearing.join(";"),reappear_codes:reappearing.join(";")};
});
const fastIce=[...new Set(D.emperor.map(x=>x.ice_reg))].sort();
if(fastIce.length!==8)throw Error("published ice region assignment changed");
const regions=[],regAnnual=[];
for(const region of fastIce){
 const sites=ids.filter(id=>idx.get(id+"|2009").ice_reg===region);
 const x=vec(sites,2009,"N_mean"),y=vec(sites,2018,"N_mean");
 regions.push({ice_region:region,n_colonies:sites.length,mean_index_2009:sum(x),mean_index_2018:sum(y),
 index_change_pct:pc(sum(x),sum(y)),N_eff_2009:neff(x),N_eff_2018:neff(y),N_eff_change_pct:pc(neff(x),neff(y)),
 lost_modelled_zero:lost.filter(id=>sites.includes(id)).join(";"),gained_positive:gained.filter(id=>sites.includes(id)).join(";")});
 for(const year of years){const v=vec(sites,year,"N_mean");
 regAnnual.push({ice_region:region,year,modelled_index:sum(v),N_eff_from_marginal_means:neff(v)})}
}
const landRows=D.land.filter(x=>["ADPE","CHPE","GEPE"].includes(x.species_id)&&+x.count>0&&x.n_rows==="1"&&x.n_counts==="1"&&!["unknown","ground|uav"].includes(x.method));
const byLand=new Map();
for(const x of landRows){const k=[x.species_id,x.region,x.method,x.season,x.site_id].join("|");
 if(byLand.has(k))throw Error("duplicate original land census");byLand.set(k,x)}
const terrestrial=[];
for(const key of [...new Set(landRows.map(x=>[x.species_id,x.region,x.method].join("|")))].sort()){
 const [species,region,method]=key.split("|");
 const a0=landRows.filter(x=>x.species_id===species&&x.region===region&&x.method===method&&x.season==="2009");
 const second=new Set(landRows.filter(x=>x.species_id===species&&x.region===region&&x.method===method&&x.season==="2018").map(x=>x.site_id));
 const both=a0.map(x=>x.site_id).filter(id=>second.has(id)).sort();
 if(both.length<2)continue;
 const counts=year=>both.map(id=>+byLand.get([species,region,method,String(year),id].join("|")).count);
 const v0=counts(2009),v1=counts(2018);
 terrestrial.push({species,region,method,fixed_positive_site_codes:both.length,site_codes:both.join(";"),
 count2009:sum(v0),count2018:sum(v1),count_change_pct:pc(sum(v0),sum(v1)),
 N_eff_2009:neff(v0),N_eff_2018:neff(v1),N_eff_change_pct:pc(neff(v0),neff(v1)),
 original_census_not_emperor_modelled_adult_index:true});
}
const ross=terrestrial.find(x=>x.species==="ADPE"&&x.region==="Victoria Land"&&x.method==="aerial");
if(!ross||ross.fixed_positive_site_codes!==6)throw Error("Ross original six sector comparison no longer supported");
const district={Bird:["BRDM","BRDN","BRDS"],Crozier:["CRZE","CRZW"],Royds:["ROYD"]};
const districtCounts=year=>Object.values(district).map(parts=>sum(parts.map(id=>{
 const row=byLand.get(["ADPE","Victoria Land","aerial",String(year),id].join("|"));
 if(!row)throw Error("Ross source sector not held fixed");return +row.count
})));
const island0=districtCounts(2009),island1=districtCounts(2018);
const Ross={
 island:"Ross Island, ONE island",districts:3,source_sectors:6,
 count2009:sum(island0),count2018:sum(island1),count_change_pct:pc(sum(island0),sum(island1)),
 N_eff_three_districts_2009:neff(island0),N_eff_three_districts_2018:neff(island1),
 N_eff_three_districts_change_pct:pc(neff(island0),neff(island1))};
const decline=regions.filter(x=>x.index_change_pct<0);
const facts={
 original_emperor_source_rows:D.emperor.length,emperor_sites:ids.length,emperor_years:years.length,
 emperor_sum_marginal_means_change_pct:end.mean_index_change_pct,
 emperor_sum_marginal_medians_change_pct:end.sum_colony_medians_change_pct,
 emperor_N_eff_means_change_pct:end.N_eff_from_means_change_pct,
 emperor_N_eff_medians_change_pct:end.N_eff_from_medians_change_pct,
 emperor_persistent_sites:end.persistent_colonies,
 emperor_persistent_N_eff_change_pct:end.persistent_only_N_eff_change_pct,
 emperor_model_zero_only_N_eff_change_pct:end.zero_only_counterfactual_delta_N_eff_pct,
 emperor_fast_ice_regions:fastIce.length,declining_emperor_regions:decline.length,
 declining_regions_with_N_eff_loss:decline.filter(x=>x.N_eff_change_pct<0).length,
 declining_regions_with_N_eff_gain:decline.filter(x=>x.N_eff_change_pct>0).length,
 matched_land_2009_2018_panels:terrestrial.length,
 Ross_source_aerial_sector_codes:ross.fixed_positive_site_codes,
 Ross_aerial_total_change_pct:ross.count_change_pct,
 Ross_sixsector_N_eff_change_pct:ross.N_eff_change_pct
};
if(process.argv.includes("--check-receipt"))for(const [k,expected] of Object.entries(receipt.values)){
 if(!Number.isFinite(facts[k])||Math.abs(facts[k]-expected)>1e-7)throw Error("Independent frozen numeric receipt mismatch "+k+" "+facts[k]+" vs "+expected)
}
mkdirSync(DIR,{recursive:true});
writeCSV("emperor_50_colonies_10years_derived.csv",annual);
writeCSV("emperor_50_colony_endpoint_partition.csv",status);
writeCSV("emperor_annual_blink_diagnostic.csv",yearsDelta);
writeCSV("emperor_8_fast_ice_regions_2009_2018.csv",regions);
writeCSV("emperor_8region_annual_N_eff.csv",regAnnual);
writeCSV("terrestrial_2009_2018_fixed_site_rosters.csv",terrestrial);
writeFileSync(join(DIR,"summary.json"),JSON.stringify({status:"original_emperor_posterior_marginals_and_fixed_site_land_census_comparison_not_causal_substrate",external_source_commit:"davidiles/EMPE_Global@13f71112da43c1fd082273677757b41c550457ed",
 DOI:"10.5061/dryad.m63xsj48v",facts,emperor:end,regional:regions,terrestrial,Ross,
 limits:"Emperor N_eff computed from separate marginal posteriors is not posterior mean/CI of N_eff; original 50×10 outputs have no joint draws. Zero adult index need not indicate extinction; movement is not encoded in named site IDs. Land Ross is six sectors in one island; emperor is 50 colonies continent-wide; spatial grain, geographic areas, species and survey observation models differ. Fixed composition null is arithmetic without Palmer-style count-error calibration; no causal breeding substrate effect inferred."},null,2)+"\n");
writeFileSync(join(DIR,"validation.json"),JSON.stringify({input_git_blobs_verified:true,published_global_index_means_reproduced_10years:true,receipt_verified:process.argv.includes("--check-receipt"),N_eff_posterior_uncertainty_not_invented:true,substrate_causality_not_claimed:true},null,2)+"\n");
console.log("EMPEROR SUBSTRATE SOURCE TEST "+JSON.stringify({facts,Emperor:end,emperor_regions:regions.map(x=>({region:x.ice_region,n:x.n_colonies,index:x.index_change_pct,N_eff:x.N_eff_change_pct})),land_rosters:terrestrial,Ross,receipt_ok:process.argv.includes("--check-receipt")}));
