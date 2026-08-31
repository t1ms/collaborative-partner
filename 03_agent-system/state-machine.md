# 5-Phase Operational State Machine & Guardrail Architecture

## States & Turn Budgets
`S0_IDLE → S1_INGEST → S2_CLARIFY → S3_OUTCOME → S4_ANGLE → S5_ECOLOGY → S6_DONE`

| Phase | Min Turns | Max Turns | Skippable? | Purpose |
|---|---|---|---|---|
| **S0_IDLE / S1_INGEST** | 0 | 1 | ❌ No | Ingest problem statement, classify patterns, dual-horizon triage |
| **S2_CLARIFY** | 1 | 5 | ❌ No | Deconstruct assumptions & cognitive distortions; S2 deepening loop |
| **S3_OUTCOME** | 1 | 3 | ❌ No | Well-Formed Outcome sieve (positive, self-initiated, sensory) |
| **S4_ANGLE** | 0 | 2 | ✅ Yes | 3rd-position observer reframe; skippable if LLM recommends `skip_next` |
| **S5_ECOLOGY** | 1 | 2 | ❌ No | Systemic trade-off and secondary constraint mapping |
| **S6_DONE** | 1 | 1 | ❌ No | Synthesis into live Architecture Decision Record (ADR) |
| **Total Session** | — | **15** | — | Hard ceiling across all phases to guarantee artifact closure |

## 6-Layer Mechanical Guardrails (Route B Veto Engine)
1. **Turn Budget Hard Caps**: Vetoes LLM `stay` requests once phase maximum is reached (forces advance); vetoes premature `advance` before phase minimums.
2. **Mandatory Phase Gates**: S2, S3, S5, and S6 are strictly non-skippable. Only S4 may be bypassed via `skip_next`.
3. **Structured JSON Output Protocol**: Typed envelope with `response_text`, `socratic_intent`, `phase_action`, `phase_reason`, and `detected_insight`.
4. **Anti-Spiral Brake**: Automatically overrides `stay` into `advance` if user token overlap (>60%) or stalled intents persist across 3 consecutive turns.
5. **Disengagement vs. Closure Pivots**:
   - **Closure Signal** (*"that's it"*, *"obviously"*) $\to$ escalate S2 deepening ladder.
   - **Disengagement Signal** (*"idk"*, *"how would I know"*) $\to$ in S4/S5, pivot to concrete experiential grounding questions (*"When this system was running smoothly, what was different?"*) instead of advancing into ungrounded phases.
6. **Domain Boundary Enforcement & Fallback**: Domain vocabulary injection, banned clinical term filtering, and graceful deterministic fallback on LLM timeout.

## Per-state behaviour
- **S1_INGEST** — Classify utterance; emit detections as graph nodes. Transition $\to$ S2.
- **S2_CLARIFY** — Pop highest-priority unresolved detection; router selects template or LLM context question. If shallow closure $\to$ 2-cycle deepening ladder. If all resolved or max turns reached $\to$ S3.
- **S3_OUTCOME** — Sieve WFO predicates (Positive state $\to$ Self-Initiated $\to$ Sensory Evidence). Transition $\to$ S4 (or $\to$ S5 if `skip_next`).
- **S4_ANGLE** — Generate 1st/2nd/3rd/systemic perspectives + reframe. If user disengages (*"idk"*), pivot to concrete past instance. Transition $\to$ S5.
- **S5_ECOLOGY** — Stress-test systemic costs and trade-offs. If user disengages (*"idk"*), pivot to concrete next-day simulation. Transition $\to$ S6.
- **S6_DONE** — Synthesize completed ADR / Decision Canvas and emit final summary.

## Priority order for detections (S2)
Distortions first (Cause-Effect / Mind-Reading / Complex-Equivalence — they fabricate structure) $\to$ Deletions (Unspecified referent / verb / simple deletion) $\to$ Generalizations (Modal necessity / possibility $\to$ Universal quantifier $\to$ Comparative deletion).
