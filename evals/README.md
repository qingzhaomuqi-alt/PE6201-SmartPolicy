# Evaluation explainer

Run `node evaluate.mjs` from the repository root. It imports the same `dist/retrieval.mjs` used in the website, reads fixed labels and writes results/cases.json and results/metrics.json. Results should reproduce; no API, model randomness or remote data is involved. `node check-parity.mjs` and `node check-handbook.mjs` run targeted regression checks; they are not extra independent accuracy evidence.

Definitions for the 30 evaluation cases:
- Correct decision: expected top source on an answerable question, or abstention on an unanswerable question. Full generated-answer correctness is not assessed.
- Answerable source selection: 16 correct top sources / 17 answerable inputs = 94.1%.
- Decision accuracy: 28 correct decisions / 30 inputs = 93.3%.
- Abstention recall: 12 true abstentions / 13 unanswerable inputs = 92.3%.
- Abstention precision: 12 true abstentions / 12 abstentions = 100%.
- Answered source precision: 16 correct sources / 18 answered inputs = 88.9%.
- Coverage: 18 answered inputs / 30 total inputs = 60%.
Development decisions: 14/15.

Targets were 85% answerable source selection and 90% abstention recall. These targets are nominally exceeded only on reused development-influenced labels. No independent validation, live LLM/Ragas assessment, human task-time study or calibrated confidence was performed. The original 15-section build and expanded 20-chapter corpus differ; score changes are not a controlled measure of retrieval improvement. Explicit unsupported-topic rules also make some negative cases easier.

Retained failures: Q11 (development), personal monitor purchase → meals; Q22, missing receipt → security incidents; Q40, employment-dispute law → privacy. False matches remain despite valid source links. Multi-source overtime completeness and legal/time eligibility are not assessed by the single-source labels.

Root website-evaluation.json contains historical v3 before/after evidence; handbook-v4-evaluation.json contains the recorded v4 responses used for the final report. results/cases.json is the fresh reproducible output. The optional WebMCP interface lacks live validation; simulated DOM interaction checks are separate from retrieval scores.
