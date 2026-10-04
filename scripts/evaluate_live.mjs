/** Billable live evaluation. No fake model results; errors remain in the output. */
import fs from 'node:fs';import {runRag,embed} from '../server/rag.mjs';
if(!process.env.OPENAI_API_KEY)throw Error('OPENAI_API_KEY is required. No live evaluation has run.');
const corpus=JSON.parse(fs.readFileSync('data/chunks.json')),labels=JSON.parse(fs.readFileSync('data/questions.json'));
console.log('labels shape',Array.isArray(labels)?'array':Object.keys(labels));
const questions=Array.isArray(labels)?labels:labels.questions;
if(!Array.isArray(questions))throw Error('Unsupported question data.');
const selected=questions.filter(c=>c.split==='eval');
const limit=process.argv.includes('--all')?selected.length:3;
const vectors=await embed(corpus.chunks.map(c=>c.title+' — '+c.heading+'\n'+c.text),process.env.OPENAI_API_KEY);
const rows=[];
for(const c of selected.slice(0,limit)){try{const r=await runRag(c.question,corpus.chunks,{key:process.env.OPENAI_API_KEY,model:process.env.OPENAI_MODEL||'gpt-4o',vectors});rows.push({...c,...r});console.log(c.id,r.mode,r.abstained,r.latency_ms+'ms');}catch(e){rows.push({...c,error:e.message});console.log(c.id,'ERROR');}}
fs.mkdirSync('results',{recursive:true});fs.writeFileSync('results/live-rag.json',JSON.stringify({created_at:new Date().toISOString(),pdf_sha256:corpus.pdf_sha256,scope:limit===selected.length?'30 reused evaluation questions':'smoke test only',warning:'Previously seen labels; not independent. Generated answer correctness requires separate review.',rows},null,2));
