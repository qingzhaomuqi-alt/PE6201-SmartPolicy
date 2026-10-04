# Data provenance

`public/Demo_Company_Policy.pdf` is an AI-assisted fictional course handbook, not NTU, EEOC, employer or legal policy. Twenty chapters span physical PDF pages 3–22. `public/policies.json` provides chapter metadata. `chunks.json` contains 100 clauses genuinely extracted from that PDF and checked against authored clause metadata; it records the PDF hash. The parser does not claim arbitrary PDF or OCR support.

`questions.json` preserves 15 development and 30 evaluation questions with source-ID and abstention labels. These AI-assisted questions were seen during development, are not an independent human-annotated answer reference set and cannot alone measure faithfulness. Embedding vectors may be generated with the named API and saved in `embeddings.json`; no such file or fabricated vectors are included until an actual indexing call succeeds.
