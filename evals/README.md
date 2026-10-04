# Evaluation status

No live LLM/Ragas scores have been measured in this revision. Seven mocked contract tests pass; they validate implementation boundaries, not model quality.

Use scripts/evaluate_live.mjs for real model calls, first smoke then --all (30 reused evaluation labels). Failures remain visible in results/live-rag.json. It records model IDs, retrieved contexts, actual responses, latency and generation-token usage. Embedding usage is not included in the per-answer generation usage. It measures service latency, not employee resolution time.

Use evaluate_ragas.py (pinned Ragas 0.2.15) on actual successful generated answers for faithfulness and reference-free context precision. Abstentions/errors are excluded and counted; never interpret the included-answer score as overall success. Judge metrics can be wrong. This differs from proposal's human-reference context precision and requires independent human review before claimed target achievement. Script integration against live APIs is pending.

Legacy JSON in the repository records the earlier offline baseline. Its scores cannot be transferred to RAG. No metric is fabricated or relabelled. Retained earlier failures and reused labels are described in docs/Proposal_Alignment.md.
