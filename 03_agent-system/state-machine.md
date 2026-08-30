# 5-Phase Operational State Machine

## States
`S0_IDLE → S1_INGEST → S2_CLARIFY → S3_OUTCOME → S4_ANGLE → S5_ECOLOGY → S6_DONE`

## Per-state behaviour
- **S1_INGEST** — classify utterance; emit detections as graph nodes. Transition: if ≥1 detection → S2; else → S2 with `open` flag.
- **S2_CLARIFY** — pop highest-priority unresolved detection; router selects template; ask one question; record answer. **Deepening sub-loop:** if the answer is a *closure signal* (see socratic-layer.md §7.1) and the pattern still lacks a concrete instance, escalate through the per-pattern deepening ladder (§7.3), max 2 extra cycles, each its own `question` node. Only mark the detection resolved after a concrete answer OR after max cycles. Loop S2 until all detections cleared or user signals move-on. Transition → S3.
- **S3_OUTCOME** — for each WFO predicate not yet satisfied, ask its canonical question (positive framing, self-initiation, sensory evidence, chunk/granularity, ecology). Transition → S4 when all predicates have a draft; → S2 if a predicate reveals a hidden distortion.
- **S4_ANGLE** — generate 1st/2nd/3rd/systemic perspectives + one reframe; attach as `perspective` nodes. Transition → S5.
- **S5_ECOLOGY** — probe costs/trade-offs; add `constraint`/`cost` nodes; if a fatal ecology conflict → back to S3. Transition → S6.
- **S6_DONE** — synthesize: present the well-formed outcome + the perspectives + the graph trace; offer export.

## Transition table
| From | Event | To | Action |
|---|---|---|---|
| S0 | user_msg | S1 | classify |
| S1 | detection(s) | S2 | enqueue detections |
| S1 | none | S2 | open clarify |
| S2 | answer logged | S2 | next detection or →S3 |
| S2 | closure signal + not concrete | S2 | deepen (cycle ≤2) on same detection |
| S2 | deepened → concrete OR max cycles | S2 | resolve detection |
| S2 | user "move on" | S3 | |
| S3 | predicate missing | S3 | ask predicate Q |
| S3 | all drafted | S4 | |
| S3 | distortion found | S2 | re-clarify |
| S4 | perspectives done | S5 | |
| S5 | conflict | S3 | re-architecture |
| S5 | clear | S6 | synthesize |
| S6 | export | S0 | persist + reset |

## Priority order for detections (S2)
Cause-Effect / Mind-Reading / Complex-Equivalence (distortions first — they fabricate structure) → Unspecified referent / verb / simple deletion → Modal necessity/possibility → Universal quantifier → Comparative deletion → Nominalization.
