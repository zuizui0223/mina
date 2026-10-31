// Two fixed historical windows, same single counting method; no causal effect inference.
// Node >=20. Run from the repository root.
import {readFileSync,writeFileSync,mkdirSync} from "node:fs";
import {createHash} from "node:crypto";
import {resolve,join} from "node:path";
function csvParse(t){let data=[],row=[],v="",q=false;for(let i=0;i<t.length;i++){const c=t[i];if(q){if(c==='"'&&t[i+1]==='"'){v+='"';i++}else if(c==='"')q=false;else v+=c;}else if(c==='"')q=true;else if(c===','){row.push(v);v=""}else if(c==='\n'){row.push(v.replace(/\r$/,""));if(row.length>1)data.push(row);row=[];v=""}else v+=c;}if(v||row.length){row.push(v);data.push(row)}const hd=data.shift();return data.map(a=>{if(a.length!==hd.length)throw Error("bad csv cols");return Object.fromEntries(hd.map((k,i)=>[k,a[i]]))})}
function csvOut(rows){const h=Object.keys(rows[0]),esc=v=>{const s=v==null?"":String(v);return /[,"\r\n]/.test(s)?'"'+s.replaceAll('"','""')+'"':s};return h.join(",")+"\n"+rows.map(row=>h.map(k=>esc(row[k])).join(",")).join("\n")+"\n"}
function compute(src,sourceSha){
 const bio=csvParse(src.bio),selected=csvParse(src.sites).filter(x=>x.species_id==="ADPE"),ice=csvParse(src.ice),old=JSON.parse(src.model);
 if(bio.length!==2999||selected.length!==39||ice.length!==9600)throw Error("input source cohort changed");
 const mean=a=>a.reduce((s,x)=>s+x,0)/a.length;
 const slope=(x,y)=>{const a=mean(x),b=mean(y),den=x.reduce((s,z)=>s+(z-a)**2,0);return den?x.reduce((s,z,i)=>s+(z-a)*(y[i]-b),0)/den:null};
 const pearson=(a,b)=>{if(a.length<3)return null;const ma=mean(a),mb=mean(b),da=a.map(x=>x-ma),db=b.map(x=>x-mb),den=Math.sqrt(da.reduce((s,x)=>s+x*x,0)*db.reduce((s,x)=>s+x*x,0));return den?da.reduce((s,x,i)=>s+x*db[i],0)/den:null};
 const cm=new Map();for(const x of ice.filter(x=>x.inner_km==="0"&&[8,9,10,11].includes(+x.month))){const k=x.site_id+"|"+x.year,a=cm.get(k)||[];a.push(+x.sic_mean);cm.set(k,a);}
 const yearBlocks=[[1991,2005],[2006,2020]],out=[],fail=[];
 const beta=+old.historical.linear_slope_per10pp/10;
 if(Math.abs(beta-.01672273272231719)>1e-12)throw Error("model beta mismatch");
 for(const s of selected){
  const b=bio.filter(x=>x.site_id===s.site_id&&x.species_id==="ADPE"&&x.method===s.method&&+x.season>=1991&&+x.season<=2020&&x.count!==""&&+x.count>=0);
  let periods=[];
  for(const [a,z] of yearBlocks){
   const count=b.filter(x=>+x.season>=a&&+x.season<=z),ys=count.map(x=>+x.season);
   const climate=[];for(let year=a;year<=z;year++){const vv=cm.get(s.site_id+"|"+year);if(!vv||vv.length!==4)throw Error("missing source SIC "+s.site_id);climate.push(mean(vv))}
   const span=ys.length?Math.max(...ys)-Math.min(...ys):0;
   periods.push({n:ys.length,span,ice_mean:mean(climate),g:ys.length>=3&&span>=5?slope(ys,count.map(x=>Math.log1p(+x.count)))*10:null});
  }
  const supported=periods.every(x=>x.g!==null);
  const x={site_id:s.site_id,region:s.region,source_method:s.method,
   early_period:"1991-2005",early_n:periods[0].n,early_span:periods[0].span,
   late_period:"2006-2020",late_n:periods[1].n,late_span:periods[1].span,
   historical_ice_mean_early:periods[0].ice_mean,historical_ice_mean_late:periods[1].ice_mean,
   delta_ice_late_minus_early_pp:periods[1].ice_mean-periods[0].ice_mean,
   early_log_growth_decade:periods[0].g,late_log_growth_decade:periods[1].g,
   observed_change_log_growth_decade:supported?periods[1].g-periods[0].g:null,
   CONDITIONAL_predicted_change_from_spatial_climate_beta:supported?beta*(periods[1].ice_mean-periods[0].ice_mean):null,
   historical_temporal_gate:supported?1:0};
  out.push(x);if(supported)fail.push(x);
 }
 if(out.length!==39||fail.length!==23)throw Error("expected 39 source / 23 supported "+out.length+"/"+fail.length);
 const x=fail.map(a=>a.delta_ice_late_minus_early_pp),y=fail.map(a=>a.observed_change_log_growth_decade),pred=fail.map(a=>a.CONDITIONAL_predicted_change_from_spatial_climate_beta);
 const by=Map.groupBy(fail,x=>x.region),dx=[],dy=[];
 for(const arr of by.values()){const m=mean(arr.map(z=>z.delta_ice_late_minus_early_pp)),n=mean(arr.map(z=>z.observed_change_log_growth_decade));for(const z of arr){dx.push(z.delta_ice_late_minus_early_pp-m);dy.push(z.observed_change_log_growth_decade-n)}}
 const meta={status:"historical_temporal_transfer_diagnostic_not_out_of_time_training_independent_validation",
  source_sha:sourceSha,original:{"full_selected_Adelie_sites":out.length,"two_15year_period_sites_with_3plus_count_years_and_5plus_span_each":fail.length,"regions":Object.fromEntries([...by].map(([k,v])=>[k,v.length]))},
  analysis:{time_window_early:"1991-2005",time_window_late:"2006-2020",environment:"original satellite Aug-Nov nearby mean SIC",response:"difference in fitted log1p nest count slopes per decade",
    mean_ice_shift_pp:mean(x),mean_actual_shift_log_growth_decade:mean(y),historical_spatial_slope_implied_mean_shift:mean(pred),
    correlation_between_period_ice_and_growth_shift:pearson(x,y),within_region_correlation:pearson(dx,dy),
    fixed_spatial_model_prediction_RMSE:Math.sqrt(mean(y.map((v,i)=>(v-pred[i])**2))),
    zero_change_reference_RMSE:Math.sqrt(mean(y.map(v=>v*v))),
    exploratory_slope_per10pp:slope(x,y)*10},
  meaning:"This checks temporal association for the same count method and fixed periods; no cause attribution, no independent heldout climate transfer because beta was fitted using full 1991-2020 source sites.",
  caveats:["Biological early/late regression slopes depend strongly on counts, and site-year support is selected by observation density.","Only 2 historical blocks; some regions contain <=2 sites, and SIC observational buffers overlap.","1991-2005 vs 2006-2020 is an exploratory time sensitivity, not a frozen hypothesis test.","Small mean historical SIC shift does not identify response to 2100 extreme future warming."]};
 return {meta,files:{"two_period_historical_growth_sic.csv":csvOut(out),"summary.json":JSON.stringify(meta,null,2)+"\n"}};
}
const base=resolve("research/climate-penguin/outputs");
const output=resolve("research/climate-penguin/outputs/historical_temporal_transfer_v1");
const paths={"bio":"comparison_audit/mapppd_unambiguous_site_seasons.csv","sites":"warming_species_breeding_v1/historical_species_site_trends.csv","ice":"climate_penguin/macro_monthly_seaice_1991_2020.csv","model":"historical_ice_breeding_transfer_v1/summary.json"};
const expected={"bio":"fc134e364cf38699fa7611d7dee5fbbbcb370c0a","sites":"2b6c0793ea9f9ea9acf0771052cf7a2ad9ab335b","ice":"4fcea71c2d8b1069b6ad143f6522061ed434daf5","model":"913344733e372c3a6ae5cb6a988a0a98b13ffc82"};
const source={};for(const [k,path] of Object.entries(paths)){
 const buf=readFileSync(join(base,path));
 const git=createHash("sha1").update(Buffer.from("blob "+buf.length+"\0")).update(buf).digest("hex");
 if(git!==expected[k])throw Error("source SHA changed "+k);
 source[k]=buf.toString("utf8");
}
const result=compute(source,expected);
mkdirSync(output,{recursive:true});
for(const [name,body] of Object.entries(result.files))writeFileSync(join(output,name),body);
console.log(JSON.stringify(result.meta.analysis,null,2));
