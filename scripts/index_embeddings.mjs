/** Optional persistent dense index; embedding API calls are billable. */
import fs from 'node:fs';import {embed} from '../server/rag.mjs';
if(!process.env.OPENAI_API_KEY)throw Error('Set OPENAI_API_KEY privately in your terminal environment.');
const data=JSON.parse(fs.readFileSync('data/chunks.json'));
const vectors=await embed(data.chunks.map(c=>c.title+' — '+c.heading+'\n'+c.text),process.env.OPENAI_API_KEY);
fs.writeFileSync('data/embeddings.json',JSON.stringify({model:'text-embedding-3-small',dimensions:256,pdf_sha256:data.pdf_sha256,chunk_ids:data.chunks.map(c=>c.id),vectors}));console.log('Indexed '+vectors.length+' chunks. Rebuild before publishing.');
