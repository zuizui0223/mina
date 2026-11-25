import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
function lagDiagnostic(csv){
 const [header,...lines]=csv.trim().split(/\r?\n/),names=header.split(",").slice(1),map=new Map(lines.map(l=>{let [y,...v]=l.split(",").map(Number);return [y,v];}));const L=[1,5,10,20];const sum=x=>x.reduce((a,b)=>a+b,0),median=x=>{if(!x.length)return null;let a=x.slice().sort((a,b)=>a-b);return (a[(a.length-1)>>1]+a[a.length>>1])/2;};
 if(map.size!==26||names.length!==6)throw Error("support");
 const rows=[];for(let h of L){for(let [y,a] of map){let c=map.get(y+h);if(!c)continue;let n0=sum(a),n1=sum(c),p=a.map(v=>v/n0),q=c.map(v=>v/n1),u0=sum(a.map(x=>x*(x-1)))/(n0*(n0-1)),u1=sum(c.map(x=>x*(x-1)))/(n1*(n1-1));rows.push({lag:h,start:y,end:y+h,N0:n0,N1:n1,stratum:n1/n0<1/1.1?"decline":n1/n0>1.1?"increase":"near_stable",tv:.5*sum(p.map((v,i)=>Math.abs(v-q[i]))),d2:u0+u1-2*sum(p.map((v,i)=>v*q[i])),deltaU:u1-u0});}}
 const stats=x=>({n:x.length,medianTV:median(x.map(z=>z.tv)),medianD2:median(x.map(z=>z.d2)),medianDeltaU:median(x.map(z=>z.deltaU))});
 const summary=L.map(h=>({lag:h,all:stats(rows.filter(x=>x.lag===h)),strata:Object.fromEntries(["decline","near_stable","increase"].map(k=>[k,stats(rows.filter(x=>x.lag===h&&x.stratum===k))]))}));
 if(summary[0].all.n!==23)throw Error("annual support drift");
 return {status:"POST_RESULT_SAME_SOURCE_LAG_DIAGNOSTIC",summary,rows,limits:"One Ross Island system, overlapping intervals and unequal start-year support across lags; same six census units; no inference or general time-scale claim."};
}
const b=readFileSync(process.argv[2]);if(createHash('sha1').update('blob '+b.length+'\0').update(b).digest('hex')!=='eaf47bf87158ef219d75b1be9eb8e50d0703ebaa')throw Error('source');
console.log(JSON.stringify(lagDiagnostic(b.toString('utf8')),null,2));
