# Proposal alignment and remaining gaps

Implemented code paths: PDF clause extraction with physical page citations, dense embeddings, BM25, reciprocal-rank fusion, GPT-4o grounded generation, abstention, per-statement cited IDs, review-request draft, live evaluation capture and Ragas evaluator.

Verified locally: PDF extraction 100 clauses/20 chapters, source-page metadata, ranking primitives, mocked API contracts, citation validation, missing-credential handling, API failure handling, server boundary and JavaScript syntax. Mock tests are not a real LLM demonstration.

Pending: real API connection; generated-output review; live and Ragas metrics; independent human annotations; task-time study; full browser QA. No claim is made that the >85% generation metrics are reached.

Changed deliberately: synthetic handbook replaces unverified EEOC source; custom website replaces Streamlit; small in-memory vector index replaces managed DB; human-review draft replaces automatic notification. RBAC and zero-data-retention agreements remain absent. Original unsupported 45%/8-minute baseline figures are not repeated as measured facts.

Old report: describes the offline build; update it after live testing and retain user's chosen layout. Do not merely rename old BM25 scores as Ragas scores.
