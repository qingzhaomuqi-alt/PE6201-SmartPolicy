/** Bundle dependency-free Worker and explicit allow-listed public assets. */
import fs from 'node:fs';
const allowed=['index.html','style.css','app.mjs','retrieval.mjs','policies.json','Demo_Company_Policy.pdf'];
const types={html:'text/html; charset=utf-8',css:'text/css; charset=utf-8',mjs:'text/javascript; charset=utf-8',json:'application/json',pdf:'application/pdf'};
const assets=Object.fromEntries(allowed.map(name=>['/'+name,{data:fs.readFileSync('public/'+name).toString('base64'),type:types[name.split('.').at(-1)]}]));
const data=JSON.parse(fs.readFileSync('data/chunks.json'));
let vectors=null;
if(fs.existsSync('data/embeddings.json')){const e=JSON.parse(fs.readFileSync('data/embeddings.json'));if(e.pdf_sha256!==data.pdf_sha256||e.chunk_ids.join('|')!==data.chunks.map(c=>c.id).join('|'))throw Error('Stale embedding index; regenerate it.');vectors=e.vectors;}
const source='const ASSETS='+JSON.stringify(assets)+';\nconst CHUNKS='+JSON.stringify(data.chunks)+';\nconst VECTORS='+JSON.stringify(vectors)+';\n'+fs.readFileSync('server/rag.mjs','utf8').replaceAll('export ','')+'\n'+fs.readFileSync('server/worker.mjs','utf8').replace(/^import .*;\n/m,'');
fs.mkdirSync('dist/server',{recursive:true});fs.mkdirSync('dist/.openai',{recursive:true});fs.writeFileSync('dist/server/index.js',source);fs.copyFileSync('.openai/hosting.json','dist/.openai/hosting.json');console.log('Built RAG Worker with '+data.chunks.length+' PDF chunks.');
