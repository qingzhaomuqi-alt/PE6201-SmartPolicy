/** Chat UI: live RAG and labelled offline baseline; session history and safe rendering. */
import {answer} from './retrieval.mjs';
const form=document.querySelector('#chat-form'),input=document.querySelector('#question'),send=document.querySelector('#send'),log=document.querySelector('#conversation'),status=document.querySelector('#status'),mode=document.querySelector('#answer-mode');let policies=null,busy=false;
const welcome=document.querySelector('#welcome'),back=document.querySelector('#back-to-questions'),history=document.querySelector('#view-answers');
const text=(tag,content,cls)=>{const n=document.createElement(tag);n.textContent=content;if(cls)n.className=cls;return n;};
function showAnswers(){welcome.hidden=true;log.classList.remove('home');back.hidden=false;}
function backToQuestions(){welcome.hidden=false;log.classList.add('home');back.hidden=true;history.hidden=!log.querySelector('.message');input.value='';status.textContent='Your previous answers are kept in this session';log.scrollTop=0;input.focus();}
back.addEventListener('click',backToQuestions);history.addEventListener('click',()=>{showAnswers();log.scrollTop=log.scrollHeight;input.focus();});
function lock(value){busy=value;input.disabled=value;send.disabled=value;mode.disabled=value;document.querySelectorAll('[data-question]').forEach(b=>b.disabled=value);form.setAttribute('aria-busy',String(value));}
async function submit(question){
 if(busy)return;if(!policies)throw Error('The policy collection is still loading.');if(typeof question!=='string'||!question.trim()||question.length>1000)throw Error('Enter a question of 1–1,000 characters.');
 lock(true);status.textContent=mode.value==='rag'?'Finding evidence and generating an answer…':'Looking up policy text…';
 try{
  let result;if(mode.value==='rag'){const response=await fetch('/api/ask',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({question}),signal:AbortSignal.timeout(90000)});const payload=await response.json();if(!response.ok)throw Error(payload.error||'Live RAG is unavailable.');result=payload;}else result=answer(question,policies);
  showAnswers();log.append(text('div',question,'message user'));const msg=text('div','','message assistant');msg.append(text('div',result.llm_called?'SMARTPOLICY · LLM + HYBRID RETRIEVAL':result.mode==='guard'?'SMARTPOLICY · SAFETY GUARD':'SMARTPOLICY · POLICY LOOKUP · NO LLM','role'),text('div',result.answer,'answer-body'));
  for(const source of result.sources){const card=text('div','','evidence');card.append(text('div','POLICY SOURCE','source-label'),text('h3',source.title),text('p',`Page ${source.page} · ${source.heading||'Policy'} · Version ${source.version}`));if(result.llm_called)card.append(text('p',source.text));const a=text('a',`Read page ${source.page} in the handbook`);a.href=`Demo_Company_Policy.pdf#page=${source.page}`;a.target='_blank';a.rel='noopener';card.append(a);msg.append(card);}
  if(result.abstained)msg.append(text('div','Insufficient evidence. No policy determination made.','notice'));
  const review=text('button','Prepare HR / Finance review','back-button');review.type='button';review.addEventListener('click',()=>{const draft=text('p','Review request: '+question+'\n\nPlease confirm the applicable policy and any missing conditions. This is a draft to send to your organisation’s HR or Finance; no message has been sent.','notice');review.replaceWith(draft);});
  const again=text('button','Ask another question','back-button another-question');again.type='button';again.addEventListener('click',backToQuestions);msg.append(review,again);log.append(msg);input.value='';status.textContent=result.llm_called?`Generated with ${result.model} · ${(result.latency_ms/1000).toFixed(1)} seconds · Check the cited evidence`:'Policy lookup · No LLM was called';log.scrollTop=log.scrollHeight;return result;
 }finally{lock(false);input.focus();}
}
async function safelySubmit(q){try{await submit(q);}catch(e){status.textContent=e.name==='TimeoutError'?'Request timed out. Please retry.':e.message;}}
form.addEventListener('submit',e=>{e.preventDefault();void safelySubmit(input.value);});
input.addEventListener('keydown',e=>{if(e.key==='Enter'&&!e.shiftKey&&!e.isComposing){e.preventDefault();form.requestSubmit();}});
document.querySelectorAll('[data-question]').forEach(b=>b.addEventListener('click',()=>void safelySubmit(b.dataset.question)));
try{const r=await fetch('./policies.json');if(!r.ok)throw Error('Policy collection is unavailable.');policies=await r.json();if(!Array.isArray(policies)||!policies.length)throw Error('Invalid policy collection.');lock(false);let configured=false;try{const health=await fetch('/api/status');configured=health.ok&&(await health.json()).rag_configured;}catch{}
 mode.value=configured?'rag':'lookup';document.querySelector('#rag-configuration').textContent=configured?'Live RAG is configured. Questions and retrieved excerpts are sent to OpenAI for generation.':'Live RAG awaits model configuration. Policy lookup is available and does not call an LLM.';status.textContent='Ask a question in English · Each question is independent';
}catch(e){status.textContent=e.message;}
