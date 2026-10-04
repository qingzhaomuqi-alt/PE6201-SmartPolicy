# SmartPolicy PE6201 Final Project

Public demo: https://smartpolicy-pe6201.qingzhaomuqi.chatgpt.site

Final website snapshot: `2026-10-expanded-demo`, 20 fictional policy chapters and a 22-page handbook. This repository reproduces the website described in the final report. The older Python/Colab project is a different snapshot and is not part of this package.

## Run the website locally

Requires Python 3 only for a static HTTP server. No pip install, API key or GPU is needed.

Windows, from this repository folder:
```shell
py -m http.server 8000 --directory dist
```
macOS/Linux:
```shell
python3 -m http.server 8000 --directory dist
```
Open http://localhost:8000 in your browser. Keep the terminal open; Ctrl+C stops the server. Do not open index.html by double-clicking, because the browser must fetch policies.json through HTTP.

## Use the assistant

Enter English policy questions or choose an example. Enter sends; Shift+Enter adds a line. Each question is processed independently. Back to questions and Ask another question return to the starting view; View previous answers restores the session conversation. Refreshing clears the session.

Try `I worked overtime until 10 PM, what kind of allowance or compensation is provided?` to see meal and taxi evidence. Try `What is the overtime pay rate?` to see insufficient evidence. Claims and leave are not approved by this assistant.

## Reproduce evaluations

Install Node.js 20 or newer if you want to run JavaScript checks (Node is not required just to open the website):
```shell
node evaluate.mjs
node check-parity.mjs
node check-handbook.mjs
```
`evaluate.mjs` reads fixed labels in data/questions.json, calls the actual browser retrieval module, and writes results/metrics.json and results/cases.json. The two checks exercise legacy correct decisions, input limits, broad overtime handling, source pages and five new topics. These checks are not an independent benchmark. See evals/README.md for definitions, caveats and known failures.

## Regenerate the handbook if needed

The PDF is already included. Optional regeneration requires Python and reportlab:
```shell
python -m pip install reportlab
python build_handbook.py
```
On Windows replace `python` with `py`. The generator rebuilds dist/policies.json and dist/Demo_Company_Policy.pdf from handbook_base_policies.json plus authored additions. After editing policy data, rerun evaluations and verify page references.

## Files and modules

| File | Responsibility |
|---|---|
| dist/index.html and style.css | Responsive chat interface |
| dist/app.mjs | Safe text rendering, session history, form actions and source links |
| dist/retrieval.mjs | Stop words, vocabulary expansion, BM25, explicit overtime routing and coverage boundaries |
| dist/policies.json | Active fictional policy collection with summaries, clauses, versions and PDF pages |
| dist/Demo_Company_Policy.pdf | Matching handbook with clickable contents |
| build_handbook.py | Deterministic policy text construction and PDF layout |
| evaluate.mjs | Reproducible legacy-label evaluation |
| check-parity.mjs and check-handbook.mjs | Targeted regression checks |
| website-evaluation.json | Historical v3 before/after evidence used by regression checks |
| handbook-v4-evaluation.json | Recorded expanded-corpus responses underlying the final report |
| docs/ | Product documentation, final report and submission checklist |

## Limitations and disclosure

No LLM or external model API is called. Topic routing and unsupported-topic rules are authored heuristics. Sources are fictional, AI-assisted coursework data, not NTU or real employer policies. The 45 labels were seen during development; corpus changes and coverage rules make original and expanded results non-comparable as a controlled experiment. Current evaluation decisions are 28/30, with two retained failures; this does not demonstrate generalisation, full answer correctness or employee time savings.

No employee authentication, production access controls or approval transactions are implemented. Questions are handled in the browser and kept only in page memory by the application; hosting may retain technical access logs. Do not enter employee records, confidential information or credentials. Browser interaction logic was checked using a simulated DOM; comprehensive live browser and accessibility testing was not performed. The optional feature-detected WebMCP action is not independently validated.

The project was developed with AI assistance. QI QINGZHAOMU is responsible for reviewing the submission, understanding it and complying with course disclosure requirements. See docs/Product_Documentation.md, data/README.md and evals/README.md.
