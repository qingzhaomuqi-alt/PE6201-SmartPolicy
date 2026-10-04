# Data explainer

## Sources and provenance
All text is synthetic and developed with AI assistance for PE6201. No real employee records or proprietary employer documents were collected. These are not NTU rules or employment-law guidance. The MIT licence covers the supplied authored code and dataset.

## Policy collection
The application loads `../dist/policies.json`: 20 active chapters, version `2026-10-expanded-demo`. Each record has id, title, active, version, summary, clauses (heading and text), full searchable text, and the physical PDF page. `../dist/Demo_Company_Policy.pdf` has 22 pages: cover, contents and 20 chapters; overtime meal and taxi chapters are on pages 3 and 4. The app indexes JSON, not a PDF parser. It does not support arbitrary document uploads.

`../handbook_base_policies.json` preserves the original 15 fictional summaries. `../build_handbook.py` retains numerical limits, adds process details and five chapters, and regenerates the final JSON and PDF. Exclusion topics are deliberately unspecified; they must not be treated as benefits. Re-run evaluation after changing data.

## Question labels
`questions.json` contains 45 predeclared inputs: 15 development and 30 evaluation, with id, split, question, expected_policy and expected_abstain. Evaluation contains 17 answerable and 13 unanswerable/adversarial cases. The runtime retrieval module never reads this file. Labels were reused and inspected during development, so this is a regression set, not an independent held-out test.

Policy and label authorship is shared with the implementation. Real-world usefulness needs independently authored questions, policy-owner review and controlled comparison with handbook search.
