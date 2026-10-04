/** Local equivalent of the hosted Worker. Read secrets from environment, never the browser. */
import http from 'node:http';
import worker from '../dist/server/index.js';
const env={OPENAI_API_KEY:process.env.OPENAI_API_KEY,OPENAI_MODEL:process.env.OPENAI_MODEL||'gpt-4o',LLM_ENABLED:process.env.LLM_ENABLED||'false'};
http.createServer(async(req,res)=>{try{const pieces=[];if(req.method==='POST')for await(const part of req)pieces.push(part);const body=req.method==='POST'?Buffer.concat(pieces):undefined;const r=await worker.fetch(new Request('http://localhost:8000'+req.url,{method:req.method,headers:req.headers,body}),env);res.writeHead(r.status,Object.fromEntries(r.headers));res.end(Buffer.from(await r.arrayBuffer()));}catch{res.writeHead(500);res.end('Server error');}}).listen(8000,'127.0.0.1',()=>console.log('SmartPolicy: http://localhost:8000 · live RAG enabled: '+Boolean(env.OPENAI_API_KEY&&env.LLM_ENABLED==='true')));
