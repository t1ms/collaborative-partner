# Data Architecture & Sample Corpus

This directory manages session persistence for the **Collaborative Thinking Partner**.

---

## 1. Zero-PII Policy & Session Isolation
- **Runtime User Sessions:** When running locally or in production, active Problem Graphs (`data/sessions/ses_*.json`) and user depth preferences (`data/tastes/*.json`) are generated ephemerally and are strictly **excluded from version control** via `.gitignore`.
- **Privacy Guarantee:** No live user conversation logs, personal identifiers, or production traces are ever committed to this repository.

---

## 2. Anonymized Sample Data (`data/sample/`)
For hackathon evaluation and local testing reproducibility, synthetic demo fixtures are provided:
- [`sample_session.json`](sample/sample_session.json): A verified, anonymized Problem Graph trace from the Leadership Worked Example (Variant B), illustrating nodes (`UtteranceNode`, `DetectionNode`, `QuestionNode`, `OutcomePredicateNode`) and transition edges.
- [`sample_taste.json`](sample/sample_taste.json): A synthetic user taste profile demonstrating cross-session preference tracking (`preferred_depth`, `tolerance_for_ambiguity`, precedent bank).

---

## 3. Validation Corpus & Offline Scrapes
- The real-world evaluation dataset used to test Meta-Model pattern detection (from Hacker News *Ask HN* and Reddit *r/entrepreneur*) is curated and sampled in [`03_agent-system/validation-corpus.md`](../03_agent-system/validation-corpus.md).
- Raw multi-megabyte JSON scrapes (`_hn_raw.json`, `_reddit_raw.json`) are stored offline in `_archive/raw_scrapes/` to prevent repository bloat and maintain fast clone performance.
