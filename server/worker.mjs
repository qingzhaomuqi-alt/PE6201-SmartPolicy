/** Hosted HTTP boundary. Keys stay in runtime secrets. No claims or questions are stored. */
import {runRag,embed,validateQuestion} from './rag.mjs';
// Build injects ASSETS, CHUNKS and optional precomputed VECTORS.
let vectorPromise=null;
const limits=new Map();
function json(v,status=200){return new Response(JSON.stringify(v),{status,headers:{'Content-Type':'application/json','Cache-Control':'no-store','X-Content-Type-Options':'nosniff'}});}
function allow(ip){const now=Date.now();for(const [k,v] of limits)if(now-v.time>60000)limits.delete(k);if(limits.size>2000)limits.clear();const v=limits.get(ip)||{time:now,count:0};v.count++;limits.set(ip,v);return v.count<=10;}
export default {async fetch(request,env){
 const url=new URL(request.url),path=url.pathname;
 if(path==='/api/status')return json({rag_configured:Boolean(env.OPENAI_API_KEY&&env.LLM_ENABLED==='true'),generation_model:env.OPENAI_MODEL||'gpt-4o',embedding_model:'text-embedding-3-small',chunks:CHUNKS.length});
 if(path==='/api/ask'){
  if(request.method!=='POST')return json({error:'Use POST.'},405);
  if(request.headers.get('origin')&&request.headers.get('origin')!==url.origin)return json({error:'Cross-origin requests are not allowed.'},403);
  if(!env.OPENAI_API_KEY||env.LLM_ENABLED!=='true')return json({error:'Live RAG is awaiting model configuration. Use the clearly labelled policy lookup mode meanwhile.'},503);
  if(!allow(request.headers.get('cf-connecting-ip')||'local'))return json({error:'Too many requests. Please wait one minute.'},429);
  if(!request.headers.get('content-type')?.includes('application/json'))return json({error:'JSON is required.'},415);
  try{
   const reader=request.body?.getReader();if(!reader)return json({error:'A question is required.'},400);let size=0,parts=[];
   while(true){const {done,value}=await reader.read();if(done)break;size+=value.length;if(size>8192){await reader.cancel();return json({error:'Request too large.'},413);}parts.push(value);}
   const bytes=new Uint8Array(size);let offset=0;for(const p of parts){bytes.set(p,offset);offset+=p.length;}
   let q;try{q=validateQuestion(JSON.parse(new TextDecoder().decode(bytes)).question);}catch{return json({error:'Enter a question of 1–1,000 characters.'},400);}
   if(!vectorPromise)vectorPromise=(VECTORS?Promise.resolve(VECTORS):embed(CHUNKS.map(c=>c.title+' — '+c.heading+'\n'+c.text),env.OPENAI_API_KEY)).catch(e=>{vectorPromise=null;throw e;});
   return json(await runRag(q,CHUNKS,{key:env.OPENAI_API_KEY,model:env.OPENAI_MODEL||'gpt-4o',vectors:await vectorPromise}));
  }catch{return json({error:'The model service could not produce a validated answer. Please retry or use policy lookup. No generated answer has been substituted.'},502);}
 }
 if(!['GET','HEAD'].includes(request.method))return new Response('Method not allowed',{status:405});
 const asset=ASSETS[path==='/'?'/index.html':path];if(!asset)return new Response('Not found',{status:404});
 const bytes=Uint8Array.from(atob(asset.data),c=>c.charCodeAt(0));return new Response(request.method==='HEAD'?null:bytes,{headers:{'Content-Type':asset.type,'X-Content-Type-Options':'nosniff','Content-Security-Policy':"default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; object-src 'none'; base-uri 'self'; frame-ancestors 'self' https://chatgpt.com https://*.chatgpt.com"}});
}};
