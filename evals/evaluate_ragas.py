"""Evaluate actual generated outputs only; no metrics are invented.
Uses reference-free LLM context precision and faithfulness. Both are model judgments,
not proof of factual correctness. Abstentions/errors are excluded and reported.
"""
import json, os
from pathlib import Path
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from ragas import EvaluationDataset, evaluate
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper
from ragas.metrics import Faithfulness, LLMContextPrecisionWithoutReference
if not os.environ.get('OPENAI_API_KEY'): raise RuntimeError('Private OPENAI_API_KEY required.')
root=Path(__file__).resolve().parents[1]
data=json.loads((root/'results/live-rag.json').read_text())
valid=[r for r in data['rows'] if r.get('llm_called') and not r.get('abstained') and not r.get('error')]
if not valid: raise RuntimeError('No successful generated answers to evaluate. Run live evaluation first.')
samples=[{'user_input':r['question'],'response':r['answer'],'retrieved_contexts':[c['text'] for c in r['retrieved_contexts']]} for r in valid]
llm=LangchainLLMWrapper(ChatOpenAI(model=os.environ.get('OPENAI_EVAL_MODEL','gpt-4o'),temperature=0))
result=evaluate(EvaluationDataset.from_list(samples),metrics=[Faithfulness(),LLMContextPrecisionWithoutReference()],llm=llm,embeddings=LangchainEmbeddingsWrapper(OpenAIEmbeddings(model='text-embedding-3-small')),raise_exceptions=True)
frame=result.to_pandas();frame.to_csv(root/'results/ragas-results.csv',index=False)
summary={'status':'live evaluation completed','included':len(valid),'excluded':len(data['rows'])-len(valid),'faithfulness':float(frame.faithfulness.mean()),'context_precision_without_reference':float(frame.llm_context_precision_without_reference.mean()),'caveat':'LLM judged metrics on reused labels. Not independent human annotation; not the original reference-based precision promise.'}
(root/'results/ragas-summary.json').write_text(json.dumps(summary,indent=2));print(summary)
