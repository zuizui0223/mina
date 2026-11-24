// Derived archive chronology and literature table coordinate gate. Run from repo root, Node >=20.
import {readFileSync} from 'node:fs';import {createHash} from 'node:crypto';
const paths=["research/climate-penguin/outputs/comparison_audit/mapppd_unambiguous_site_seasons.csv","research/climate-penguin/outputs/comparison_audit/palmer_five_island_counts.csv","research/climate-penguin/multispecies_vegetation_20261124/RESULT.json","research/climate-penguin/outputs/comparison_audit/palmer_site_coordinates.csv"],pins=["fc134e364cf38699fa7611d7dee5fbbbcb370c0a","20d1c11d6478899954fb837c5505708e78ca539d","0581f0c088c97e2ef32b89b0d9377ebd93fab6ed","99186631ca59a82951611b18023aa391350d8626"];
function compute(raw){
function csv(s){let rows=[],r=[],v="",q=false;for(let i=0;i<s.length;i++){let c=s[i];if(q){if(c==='"'&&s[i+1]==='"'){v+='"';i++}else if(c==='"')q=false;else v+=c;}else if(c==='"')q=true;else if(c===','){r.push(v);v=""}else if(c==='\n'){r.push(v.replace(/\r$/,""));if(r.length>1)rows.push(r);r=[];v=""}else v+=c;}if(r.length||v){r.push(v);rows.push(r)}let h=rows.shift();if(q||rows.some(x=>x.length!==h.length))throw Error("CSV shape");return rows.map(a=>Object.fromEntries(h.map((k,i)=>[k,a[i]])))}
const a=csv(raw[0]),p=csv(raw[1]),prior=JSON.parse(raw[2]),coords=csv(raw[3]);
const cases=prior.episodes.filter(x=>x.n_zero_visits>=2&&x.reappearance===null).map(x=>{
let rows=a.filter(v=>v.site_id===x.site&&v.species_id===x.species&&v.count!==""&&v.method==="ground").map(v=>({year:+v.season,n:+v.count}));
let provenance="MAPPPD ground archive";
if(x.site==="LITC"){rows=p.filter(v=>v.island_name==="LIT").map(v=>({year:+v.year,n:+v.count}));provenance="Palmer LTER fixed monitored island series";}
rows.sort((a,b)=>a.year-b.year);
const first=x.first_zero;const before=rows.filter(v=>v.year<first&&v.n>0);
const last=before.at(-1);const start=1986,end=2021;const recent=before.filter(v=>v.year>=Math.max(start,last.year-9));
const post=rows.filter(v=>v.year>=first&&v.year<=end&&v.n===0);
const priorZeros=rows.filter(v=>v.year<last.year&&v.year>=last.year-10&&v.n===0);
const pre=before.filter(v=>v.year>=start&&v.year<=end);
return {site:x.site,species:x.species,provenance,last_positive:last.year,last_positive_n:last.n,first_observed_zero:first,event_interval_years:first-last.year,pre_archive_positive_years:pre.map(v=>v.year),pre_10y_positive_years:recent.map(v=>v.year),zero_in_10y_prior_to_last_positive:priorZeros.map(v=>v.year),post_archive_zero_years:post.map(v=>v.year),other_species_positive_at_zero:x.zero_observations.some(v=>v.positive_other.length>0),strict_temporal_candidate:first-last.year<=2&&recent.length>=3&&post.length>=3&&priorZeros.length===0};
});
const toRad=d=>d*Math.PI/180;
function km(a,b){let dlat=toRad(b[0]-a[0]),dlon=toRad(b[1]-a[1]),s=Math.sin(dlat/2)**2+Math.cos(toRad(a[0]))*Math.cos(toRad(b[0]))*Math.sin(dlon/2)**2;return 6371.0088*2*Math.asin(Math.sqrt(s));}
const seal=[{site:"HUMB",lat:-64.739,lon:-64.086,actual_n:120,doy:70},{site:"TORG",lat:-64.747,lon:-64.073,actual_n:81,doy:69}].map(x=>{let y=coords.find(v=>v.site_id===x.site);return {...x,MAPPPD_lat:+y.latitude,MAPPPD_lon:+y.longitude,point_distance_km:km([x.lat,x.lon],[+y.latitude,+y.longitude])};});
return {status:"derived_archive_chronology_and_published_source_audit_not_vegetation_effect",cohort:cases,strict_temporal_candidate_sites:cases.filter(x=>x.strict_temporal_candidate).map(x=>x.site),seal_published_table_coordinate_gate:seal,limits:["Temporal criterion only, after viewing prior counts, not pre-registered. No image availability or botanical classification tested.","Published seal coordinates disagree with archive; named sites may be same but no direct spatial join authorized. Raw GPS file and surveyed polygons required.","Other species co-observed positive at site not proof same patch."]};
}
const raw=paths.map((p,i)=>{let b=readFileSync(p);if(createHash('sha1').update('blob '+b.length+'\0').update(b).digest('hex')!==pins[i])throw Error('source SHA mismatch '+p);return b.toString('utf8')});console.log(JSON.stringify(compute(raw),null,2));
