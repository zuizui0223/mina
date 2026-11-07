// Reproduce Adélie observed long-term site growth vs environmental climatology and CMIP6 conditional transfer.
// Node.js >= 20. Run from repo root.
import {readFileSync,writeFileSync,mkdirSync} from "node:fs";
import {createHash} from "node:crypto";
import {resolve,join} from "node:path";
function csvParse(s){let rows=[],r=[],v="",q=false;for(let i=0;i<s.length;i++){let c=s[i];if(q){if(c==='"'&&s[i+1]==='"'){v+='"';i++}else if(c==='"')q=false;else v+=c;}else if(c==='"')q=true;else if(c===','){r.push(v);v="";}else if(c==='\n'){r.push(v.replace(/\r$/,""));if(r.length>1)rows.push(r);r=[];v="";}else v+=c;}if(r.length||v){r.push(v);rows.push(r)}if(q)throw Error("Unclosed quote");let h=rows.shift();return rows.map((a,i)=>{if(a.length!==h.length)throw Error("Malformed CSV "+i);return Object.fromEntries(h.map((k,j)=>[k,a[j]]))});}
function csvEncode(rows){const h=Object.keys(rows[0]),q=v=>{let s=v==null?"":String(v);return /[,"\n\r]/.test(s)?'"'+s.replaceAll('"','""')+'"':s};return h.join(",")+"\n"+rows.map(a=>h.map(k=>q(a[k])).join(",")).join("\n")+"\n";}
function compute(input,shas){
 const bio=csvParse(input.bio),ice=csvParse(input.ice),cmip=csvParse(input.cmip);
 if(bio.length!==54||ice.length!==9600||cmip.length!==3816)throw Error("original data changed");
 const hist=bio.filter(x=>x.species_id==="ADPE");
 if(hist.length!==39)throw Error("ADPE cohort changed");
 const mean=a=>a.reduce((s,x)=>s+x,0)/a.length;
 const group=(ar,k)=>{let z=new Map();for(const x of ar){let key=k(x),a=z.get(key)||[];a.push(x);z.set(key,a)}return z};
 const reg=(a,b)=>{const ma=mean(a),mb=mean(b),den=a.reduce((s,x)=>s+(x-ma)**2,0);return den?a.reduce((s,x,i)=>s+(x-ma)*(b[i]-mb),0)/den:null};
 function solve(A,B){const n=A.length,m=A.map((a,i)=>[...a,B[i]]);for(let i=0;i<n;i++){let k=i;for(let j=i+1;j<n;j++)if(Math.abs(m[j][i])>Math.abs(m[k][i]))k=j;[m[i],m[k]]=[m[k],m[i]];let d=m[i][i];if(Math.abs(d)<1e-12)throw Error("Singular design");for(let j=i;j<=n;j++)m[i][j]/=d;for(let j=0;j<n;j++){if(j===i)continue;let q=m[j][i];for(let t=i;t<=n;t++)m[j][t]-=q*m[i][t]}}return m.map(x=>x[n]);}
 const vec=(sic,form)=>{let x=(sic-50)/25;return form==="linear"?[1,x]:[1,x,x*x]};
 const fit=(data,form)=>{const X=data.map(r=>vec(r.sic,form)),y=data.map(r=>r.y),n=X[0].length,A=Array.from({length:n},()=>Array(n).fill(0)),B=Array(n).fill(0);
 for(let i=0;i<X.length;i++)for(let j=0;j<n;j++){B[j]+=X[i][j]*y[i];for(let k=0;k<n;k++)A[j][k]+=X[i][j]*X[i][k]};return solve(A,B);};
 const predict=(beta,x,form)=>vec(x,form).reduce((s,k,i)=>s+k*beta[i],0);
 const near=ice.filter(x=>x.inner_km==="0"&&[8,9,10,11].includes(+x.month));
 const sicMap=new Map();
 for(const x of near){const k=x.site_id+"|"+x.year,a=sicMap.get(k)||[];a.push(+x.sic_mean);sicMap.set(k,a)}
 if(near.length!==4800)throw Error("near ice support "+near.length);
 const cohort=[];
 for(const b of hist){
  const sicYears=Array.from({length:30},(_,i)=>{
   const yr=1991+i,a=sicMap.get(b.site_id+"|"+yr);
   if(!a||a.length!==4)throw Error("historical climate missing "+b.site_id+"/"+yr);
   return mean(a);
  });
  const sic=mean(sicYears),iceSlope=reg(Array.from({length:30},(_,i)=>1991+i),sicYears)*10;
  cohort.push({site_id:b.site_id,region:b.region,method:b.method,
   n_count_years:+b.n_count_years,count_year_span:+b.year_span,
   count_growth_log1p_slope_per_decade:+b.slope_log1p_count_decade,
   historical_nearshore_AugNov_SIC_mean_pct:sic,
   historical_nearshore_AugNov_SIC_trend_pp_decade:iceSlope,
   sic,y:+b.slope_log1p_count_decade});
 }
 const forms=["linear","quadratic"],coefs=Object.fromEntries(forms.map(form=>[form,fit(cohort,form)]));
 const regionDemean=(d)=>{
  const groups=group(d,x=>x.region),r=[];
  for(const a of groups.values()){const mx=mean(a.map(x=>x.sic)),my=mean(a.map(x=>x.y));for(const x of a)r.push({x:x.sic-mx,y:x.y-my});}
  return r;
 };
 const demeaned=regionDemean(cohort),betaRegion=reg(demeaned.map(x=>x.x),demeaned.map(x=>x.y));
 const loso={},loro={};
 for(const form of forms){
  for(const [k,mode] of [["LOSO","site"],["LORO","region"]]){
   let mse=0,msb=0,n=0;
   for(const x of cohort){
    const train=cohort.filter(t=>mode==="site"?t.site_id!==x.site_id:t.region!==x.region);
    if(train.length<6)continue;
    const b=fit(train,form),pred=predict(b,x.sic,form),baseline=mean(train.map(z=>z.y));
    mse+=(x.y-pred)**2;msb+=(x.y-baseline)**2;n++;
   }
   const out={heldout_n:n,rmse_climate:Math.sqrt(mse/n),rmse_intercept_only:Math.sqrt(msb/n),mse_gain_vs_intercept:(msb-mse)/n};
   if(k==="LOSO")loso[form]=out;else loro[form]=out;
  }
 }
 let se=0,sb=0,nRegionCv=0;
 for(const x of cohort){
  const train=cohort.filter(t=>t.site_id!==x.site_id),same=train.filter(z=>z.region===x.region);
  if(!same.length)continue;
  const sub=regionDemean(train),beta=reg(sub.map(t=>t.x),sub.map(t=>t.y));
  const base=mean(same.map(v=>v.y)),pred=base+beta*(x.sic-mean(same.map(v=>v.sic)));
  se+=(x.y-pred)**2;sb+=(x.y-base)**2;nRegionCv++;
 }
 const regionCV={heldout_n:nRegionCv,rmse_added_ice:Math.sqrt(se/nRegionCv),rmse_region_mean_only:Math.sqrt(sb/nRegionCv),mse_gain:(sb-se)/nRegionCv};
 const modelRecords=[
  {model:"linear",beta_coefficients:coefs.linear,sic_slope_per10pp:coefs.linear[1]/2.5,
   in_sample_correlation:reg(cohort.map(x=>x.sic),cohort.map(x=>x.y))*Math.sqrt(cohort.reduce((s,x)=>s+(x.sic-mean(cohort.map(v=>v.sic)))**2,0)/cohort.reduce((s,x)=>s+(x.y-mean(cohort.map(v=>v.y)))**2,0)),
   loso:loso.linear,loro:loro.linear},
  {model:"quadratic",beta_coefficients:coefs.quadratic,sic_slope_per10pp:null,loso:loso.quadratic,loro:loro.quadratic},
  {model:"linear_region_adjusted",beta_coefficients:[betaRegion],sic_slope_per10pp:betaRegion*10,regionCV}
 ];
 const modelMap=new Map(cmip.filter(x=>x.cohort==="macro_40"&&x.variable_id==="siconc").map(x=>[[x.site_id,x.source_id,x.experiment_id,x.period].join("|"),x]));
 if(modelMap.size!==480)throw Error("SIC future source changes 480? "+modelMap.size);
 const scenarios=[["ssp245","2041-2060"],["ssp245","2081-2100"],["ssp585","2041-2060"],["ssp585","2081-2100"]],
   climateNames=["ACCESS-CM2","BCC-CSM2-MR","CESM2"],individual=[],summaries=[];
 const fs=["linear","quadratic","linear_region_adjusted"];
 for(const [ssp,period] of scenarios)for(const model of climateNames)for(const f of fs){
  const groupRows=[];
  for(const site of cohort){
   const row=modelMap.get([site.site_id,model,ssp,period].join("|"));
   if(!row)throw Error("model missing "+site.site_id);
   const delta=+row.change,unbounded=site.sic+delta,bounded=Math.max(0,Math.min(100,unbounded));
   let val;
   if(f==="linear_region_adjusted")val=betaRegion*(bounded-site.sic);
   else val=predict(coefs[f],bounded,f)-predict(coefs[f],site.sic,f);
   const v={species_id:"ADPE",site_id:site.site_id,region:site.region,experiment:ssp,period,climate_model:model,response_model:f,
     observed_1991_2020_sic_mean_pct:site.sic,climate_model_SIC_delta_pp:delta,
     future_sic_observation_delta_unclipped_pct:unbounded, future_sic_clipped_pct:bounded,
     went_beyond_physical_0_to100:bounded!==unbounded?1:0,
     historical_site_log_growth_per_decade:site.y,
     CONDITIONAL_change_in_log_growth_per_decade:val};
   groupRows.push(v);individual.push(v);
  }
  summaries.push({experiment:ssp,period,climate_model:model,response_model:f,n_sites:groupRows.length,
   mean_scenario_change_log_growth_per_decade:mean(groupRows.map(z=>z.CONDITIONAL_change_in_log_growth_per_decade)),
   n_scenario_growth_effect_negative:groupRows.filter(x=>x.CONDITIONAL_change_in_log_growth_per_decade<0).length,
   n_scenario_growth_effect_positive:groupRows.filter(x=>x.CONDITIONAL_change_in_log_growth_per_decade>0).length,
   n_physical_SIC_bounded:groupRows.filter(x=>x.went_beyond_physical_0_to100).length,
   min_site_change:Math.min(...groupRows.map(x=>x.CONDITIONAL_change_in_log_growth_per_decade)),
   max_site_change:Math.max(...groupRows.map(x=>x.CONDITIONAL_change_in_log_growth_per_decade))});
 }
 if(individual.length!==39*4*3*3||summaries.length!==36)throw Error("expected future rows count");
 const anchor=summaries.find(x=>x.experiment==="ssp585"&&x.period==="2081-2100"&&x.climate_model==="ACCESS-CM2"&&x.response_model==="linear");
 if(Math.abs(anchor.mean_scenario_change_log_growth_per_decade-(-.16750296767898057))>1e-11)throw Error("future prediction changed "+anchor.mean_scenario_change_log_growth_per_decade);
 const sensitivity=[];
 for(const [region,ar] of group(cohort,x=>x.region)){
  const train=cohort.filter(x=>x.region!==region),b=fit(train,"linear");
  sensitivity.push({heldout_region:region,n_heldout_sites:ar.length,n_training_sites:train.length,
    linear_sic_slope_log_growth_per_decade_per10pp:b[1]/2.5});
 }
 const P=cohort.map(x=>x.sic),Y=cohort.map(x=>x.y),rawBeta=reg(P,Y),rPearson=rawBeta*Math.sqrt(P.reduce((s,x)=>s+(x-mean(P))**2,0)/Y.reduce((s,x)=>s+(x-mean(Y))**2,0));
 const meta={status:"scenario_transfer_of_historical_climate_growth_relationship_NOT_causal_warming_attribution_or_validated_population_forecast",
  source_git_shas:shas,
  sample:{Adelie_species_site_n:cohort.length,original_cohort_species_site_n:bio.length,exposure_years:30,CMIP6_model_members:3,future_period_conditions:4,site_model_structure_scenario_rows:individual.length},
  historical:{association_r: rPearson,linear_slope_per10pp:rawBeta*10,region_adjusted_slope_per10pp:betaRegion*10,
   LOSO:loso,LORO:loro,within_region_site_holdout:regionCV,leave_one_region_out:sensitivity},
  climate_scenario_summary:summaries,
  claims:"Model is cross-site long-run association. Future perturbation of predicted decadal log-count trend equals f(observed SIC mean + bounded CMIP6 SIC delta) - f(observed SIC mean), not forecast of count level or observed future growth.",
  warning:"Nonlinear model fails LORO strongly, and 39 sites / 5 regions share space. Model response is historical spatial rather than experimentally established temporal transfer. Delta SIC is CMIP6 uncorrected; observed 1991-2020 mean vs model 1995-2014 anomaly are different baselines. For 0-100 outside, clip and flag. Do NOT interpret percent of penguins declining, number of pairs, warming causal coefficients or true predictive distribution."};
 return {meta,files:{"adeli_39site_historical_climate_growth.csv":csvEncode(cohort.map(x=>Object.fromEntries(Object.entries(x).filter(([k])=>!["sic","y"].includes(k))))),
  "future_conditional_growth_component.csv":csvEncode(individual),
  "future_conditional_scenarios.csv":csvEncode(summaries),
  "leave_region_sensitivity.csv":csvEncode(sensitivity),
  "summary.json":JSON.stringify(meta,null,2)+"\n"}};
}
const base=resolve("research/climate-penguin/outputs");
const dest=resolve("research/climate-penguin/outputs/historical_ice_breeding_transfer_v1");
const paths={"bio":"warming_species_breeding_v1/historical_species_site_trends.csv","ice":"climate_penguin/macro_monthly_seaice_1991_2020.csv","cmip":"cmip6_projection_v1/site_model_changes.csv"};
const expected={"bio":"2b6c0793ea9f9ea9acf0771052cf7a2ad9ab335b","ice":"4fcea71c2d8b1069b6ad143f6522061ed434daf5","cmip":"b383ef1cc3b0807b0bd010ca0e825937ab83ce97"};
const source={};
for(const [key,path] of Object.entries(paths)){
 const bytes=readFileSync(join(base,path));
 const sha=createHash("sha1").update(Buffer.from("blob "+bytes.length+"\0")).update(bytes).digest("hex");
 if(sha!==expected[key])throw Error("Input source Git hash changed "+key);
 source[key]=bytes.toString("utf8");
}
const out=compute(source,expected);
mkdirSync(dest,{recursive:true});
for(const [name,body] of Object.entries(out.files))writeFileSync(join(dest,name),body);
console.log(JSON.stringify(out.meta.sample,null,2));
