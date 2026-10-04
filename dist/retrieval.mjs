/** Offline lookup: BM25 plus explicit overtime topic routing. Quotes fictional policies; no LLM is called. */
const STOP=new Set('a an the is are i my me can could may what how when do does to for of and in on it be have at will with from this that who we or but if then than so as about until kind provided please tell which much would should'.split(' '));
const ALIASES={dinner:'meal',cab:'taxi',accommodation:'hotel',holiday:'annual leave',ill:'sick',absence:'sick',abroad:'overseas remote',trial:'probation',hobby:'personal interest training',broken:'faulty equipment',hacked:'compromised account',bullying:'harassment',expense:'claim',bank:'privacy',override:'conflict',exposed:'data exposure incident',breach:'data exposure incident'};
export const tokens=s=>(s.toLowerCase().match(/[a-z0-9]+/g)||[]).filter(w=>!STOP.has(w));
export function answer(question,policies){
 if(typeof question!=='string'||!question.trim()||question.length>1000)throw Error('Enter a question of 1–1,000 characters.');
 const base={mode:'offline',sources:[],abstained:true};
 if(/ignore .*instructions|system prompt|override company policy|approve every claim/i.test(question))return {...base,reason:'instruction_attack',answer:'I cannot override policy or reveal internal instructions. Ask HR or Finance to review your case.'};
 const docs=policies.filter(d=>d.active);
 // A broad overtime question spans two policies. Rules choose topics; the answer quotes active source text.
 const overtime=/\bovertime\b|\b(?:work(?:ed|ing)?|stay(?:ed|ing)?)\s+(?:late|extra hours)\b/i.test(question);
 const meal=/\bmeal|\bdinner|\bfood|\balcohol/i.test(question),transport=/\btaxi|\bcab|\btransport|\bride/i.test(question);
 const wage=/\bovertime\s+(?:pay|wages?|salary|rate)\b|\b(?:paid|wages?|compensation|time off|time-off|lieu|compensatory leave)\b/i.test(question);
 const broad=overtime&&((!meal&&!transport)||(/\b(?:allowance|benefits?|compensation|entitlements?)\b/i.test(question))||(meal&&transport));
 if(broad){
  const wageOnly=wage&&!/\ballowance|\bbenefits?|\bentitlements?|\bmeal|\bdinner|\btaxi|\bcab|\btransport/i.test(question);
  const sources=wageOnly?[]:docs.filter(d=>['meal','taxi'].includes(d.id));
  const sections=sources.map(d=>d.title+' [page '+d.page+']\n'+(d.summary||d.text));
  sections.push('Not specified in this handbook: overtime wages, overtime pay rates and compensatory time off. Ask HR to confirm; no entitlement can be inferred from the meal or transport clauses.');
  if(sources.length)sections.push('These are policy conditions, not confirmation of eligibility. Transport requires work after 22:00; finishing exactly at 22:00 does not by itself satisfy that condition.');
  return {...base,sources,abstained:!sources.length,reason:sources.length?'multi_policy_extractive':'insufficient_evidence',answer:(sources.length?'Relevant overtime policies (not a claim approval):\n\n':'')+sections.join('\n\n')};
 }
 // Explicit coverage boundary, authored from handbook exclusions rather than inferred entitlement.
 const outside=/\b(?:salary|salaries|stock options?|vesting|severance|pension|childcare subsidy|mileage|dental|parental|maternity|paternity|hospitalisation|hospitalization)\b/i.test(question);
 const privacyQuestion=/\b(?:enter|share|post|save|store|upload|disclose|privacy)\b/i.test(question);
 if(outside&&!privacyQuestion)return {...base,reason:'insufficient_evidence',answer:'This handbook does not define an entitlement for that topic. Related annual leave, sick leave or expense clauses cannot establish a separate benefit. Ask HR or Finance for the applicable policy.'};
 const terms=docs.map(d=>{const t={};for(const w of tokens(d.title+' '+d.text))t[w]=(t[w]||0)+1;return t;}),lengths=terms.map(t=>Object.values(t).reduce((a,b)=>a+b,0)),avg=lengths.reduce((a,b)=>a+b,0)/docs.length;
 const df={};terms.forEach(t=>Object.keys(t).forEach(w=>df[w]=(df[w]||0)+1));
 const original=tokens(question),expanded=question+' '+Object.entries(ALIASES).filter(([k])=>original.includes(k)).map(([,v])=>v).join(' '), query=new Set(tokens(expanded));
 const ranked=docs.map((d,i)=>{let score=0;for(const w of query){const f=terms[i][w];if(f)score+=Math.log(1+(docs.length-df[w]+.5)/(df[w]+.5))*f*2.5/(f+1.5*(.25+.75*lengths[i]/avg));}return {d,score,i};}).sort((a,b)=>b.score-a.score||a.i-b.i);
 const best=ranked[0],retrieval_score=Math.round(best.score*1000)/1000;
 if(best.score<2)return {...base,retrieval_score,reason:'insufficient_evidence',answer:'I cannot find sufficient evidence in the current demo policy. Ask HR or Finance.'};
 return {...base,retrieval_score,reason:'extractive',abstained:false,sources:[best.d],answer:'Relevant policy excerpt (not a claim approval):\n'+best.d.text};
}
