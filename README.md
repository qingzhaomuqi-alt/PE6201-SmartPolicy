# SmartPolicy — RAG implementation update

Public site: https://smartpolicy-pe6201.qingzhaomuqi.chatgpt.site

**Implementation is ready; live LLM activation and measurement are pending API configuration.** The live page defaults to an explicitly labelled offline policy lookup when no runtime key is configured. Selecting Live RAG without configuration shows an error; it never substitutes an offline answer and claims it was generated.

## Run without the plugin

Use Node.js 20+ (no npm dependencies). From this folder:

```sh
node scripts/build.mjs
node scripts/serve.mjs
```

Open http://localhost:8000. This starts policy lookup. To use real RAG, set `OPENAI_API_KEY` privately in your terminal environment, set `LLM_ENABLED=true`, and restart. The server does not load `.env` automatically. Never send keys to chat, place them in frontend code, or commit them to GitHub. A ChatGPT subscription is not an API credential. API calls incur provider charges. Alternatively open `SmartPolicy_RAG_Colab.ipynb` and use Colab Secrets; the notebook gives the same engine a temporary Gradio demo URL.

PowerShell secret entry without echo:
```powershell
$smartPolicyKey = Read-Host 'OpenAI API key' -AsSecureString
$env:OPENAI_API_KEY = [System.Net.NetworkCredential]::new('', $smartPolicyKey).Password
$env:LLM_ENABLED = 'true'
node scripts/serve.mjs
```

macOS/Linux:
```sh
read -s -p 'OpenAI API key: ' SMARTPOLICY_KEY
export OPENAI_API_KEY="$SMARTPOLICY_KEY"
unset SMARTPOLICY_KEY
export LLM_ENABLED=true
node scripts/serve.mjs
```

## Hosted activation

Public runtime values are not configured by local environment variables. Configure `OPENAI_API_KEY` as a **server runtime secret**, `LLM_ENABLED=true`, and optionally `OPENAI_MODEL=gpt-4o` through the hosting account's secure configuration or an available credential integration. Do not put secrets in `.openai/hosting.json`. Until this is done, the original public URL is a lookup demo plus an inactive Live RAG option, not a tested live RAG deployment.

## Pipeline and modules

- `public/`: existing chat UI, PDF, policy JSON and labelled offline baseline. `app.mjs` calls `/api/ask` for RAG; `retrieval.mjs` is only the offline baseline.
- `scripts/ingest_pdf.py`: extracts the actual PDF text into 100 clause chunks, validates each clause against metadata and records a PDF SHA-256. This parser supports this chapter-per-page handbook, not arbitrary scanned PDFs.
- `data/chunks.json`: extracted clause text and physical page/section/version references.
- `server/rag.mjs`: clause BM25 + text-embedding-3-small cosine ranking + reciprocal-rank fusion; sends retrieved evidence to GPT-4o Responses API. Strict JSON schema requires a source ID for each policy statement. Citation ID validation cannot prove factual entailment.
- `server/worker.mjs`: server-only credential boundary, request size checks, timeout handling, best-effort per-isolate rate limits and static file serving.
- `scripts/build.mjs`: bundles the Worker and only approved public files; no secrets enter the artifact.
- `scripts/index_embeddings.mjs`: optional saved 256-dimensional vector index; without it vectors are generated and cached per server isolate on first live request, which can repeat on cold starts.
- `scripts/serve.mjs`: local HTTP adapter for the same Worker.
- `tests/rag.test.mjs`: mocked contract tests; **not evidence that GPT-4o was called**.
- `scripts/evaluate_live.mjs`: actual billable model evaluation, records failures, contexts, output, tokens and latency.
- `evals/evaluate_ragas.py`: billable Ragas faithfulness and reference-free context precision on real successful generated answers only.
- `docs/`: product documentation and implementation-status notes.

## Regenerate data and test

The extracted chunks are already provided. Optional regeneration:
```sh
python -m pip install -r requirements.txt
python build_handbook.py
cp dist/policies.json dist/Demo_Company_Policy.pdf public/
python scripts/ingest_pdf.py
node scripts/build.mjs
node --test tests/rag.test.mjs
```
On Windows copy the two regenerated files using File Explorer or `Copy-Item`. Rebuild embeddings after any PDF change; stale saved indices are rejected by the build.

## Actual evaluations — only after credentials work

```sh
node scripts/evaluate_live.mjs
node scripts/evaluate_live.mjs --all
python -m pip install -r evals/requirements.txt
python evals/evaluate_ragas.py
```
The first command runs 3 smoke questions; `--all` runs the 30 reused evaluation labels. Ragas additionally makes judge calls and can be costly. Scores and target achievement remain **unmeasured** until output files exist. The old 94.1% source / 93.3% decision scores are offline baseline metrics, not generated-answer correctness or Ragas scores. Questions were seen during development. Existing labels are AI-assisted source/abstention labels, not an independently human-annotated answer set.

## Proposal changes and responsible use

This now implements code paths for LLM generation, PDF clause extraction, sparse–dense hybrid retrieval, citations and a human-review draft button. The review button prepares text; it does not send a request or connect to a staffed help desk. We retain the 20-chapter fictional handbook: no verified EEOC corpus was supplied. The small vector collection uses an in-memory/JSON index, not Pinecone or Chroma. The custom browser frontend replaces Streamlit/Chainlit. RBAC, a workplace time study, calibrated confidence and verified provider zero-retention arrangements are not implemented. API `store:false` is not proof of zero retention. It is an information-only demonstration, not production HR software.

Public API endpoints can be abused: the rate limit is best-effort per isolate and no global spend cap or authentication is provided. Use provider project spending controls and keep public activation limited to coursework. Questions and retrieved synthetic excerpts go to OpenAI in live mode; do not enter personal or confidential data. Any organisational deployment requires access controls, policy ownership and independent review. AI assisted the code and synthetic data; the student must review the submission.

**The previous final report describes the pre-RAG website and must be revised after real API testing before being presented as the report for this implementation.**
