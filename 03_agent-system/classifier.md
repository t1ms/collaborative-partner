# Meta-Model Classifier & Router

## Input → detection
Gemini 3.5 classifies each user utterance into zero or more patterns. Each detection records: `pattern`, `span` (char offsets), `surface` (the exact phrase), `confidence`, and `layer` (`upstream_state` vs `downstream_symptom`).

### Layer Tagging Rules (Dual-Horizon Triage)
- **`upstream_state`**: Systemic capacity, physiological exhaustion, chronic depletion, burnout, boundary erosion, baseline mood/energy ("tired, depressed, barely getting by", "drained before I start").
- **`downstream_symptom`**: Acute behavioral frictions, situational habits, interpersonal incidents, surface guilt ("on phone instead of playing with kids", "delayed answering Slack", "procrastinating on deck").
- **Graph Link**: When an utterance contains both, emit an `upstream_state → downstream_symptom` causal edge in the Problem Graph. The orchestrator triages the downstream symptom for immediate momentum while preserving the upstream state for bedrock descent.

### Pattern catalogue (canonical 11; see VERIFICATION.md)
Full Socratic mapping (intent + base template) lives in `socratic-layer.md`. Summary columns below.

| pattern | trigger example | precision question template | socratic_intent | template_id |
|---|---|---|---|---|
| simple_deletion | "I feel overwhelmed" | "By which specific X?" | clarification | simple_deletion_1 |
| comparative_deletion | "much faster" | "Faster than what baseline / threshold?" | probe-criteria | comparative_deletion_1 |
| unspecified_referent | "they won't" | "Who specifically is 'they'?" | probe-assumption | unspecified_referent_1 |
| unspecified_verb | "he's undermining me" | "How specifically — what exact words/acts?" | clarification | unspecified_verb_1 |
| cause_effect | "his tone makes me shut down" | "How does X compel Y? If you didn't, what would you feel?" | probe-causal-link | cause_effect_1 |
| mind_reading | "they think I'm incompetent" | "What observable data told you that?" | probe-evidence | mind_reading_1 |
| complex_equivalence | "no invite = pushing me out" | "How does A equal B? Ever forget to invite someone you valued?" | probe-equation | complex_equivalence_1 |
| lost_performative | "it's unprofessional to show anger" | "Who set that rule? When would the opposite be true?" | probe-source | lost_performative_1 |
| universal_quantifier | "every time I scale, it fails" | "Every single time? Was there one exception — what differed?" | probe-alternative | universal_quantifier_1 |
| modal_necessity | "I must work 80h or it collapses" | "What exact catastrophe at hour 60? If capped at 40, what changes?" | probe-assumption | modal_necessity_1 |
| modal_possibility | "I can't pitch VCs" | "What specifically prevents the first sentence? What would make it possible?" | probe-barrier | modal_possibility_1 |
| meta_frame | "I hate that I get so anxious" | "When you evaluate '[surface]', what happens if you treat it with curiosity rather than criticism?" | meta-cognition | meta_frame_1 |

## Router (deterministic)
For a detection `d`, `route(d)`:
1. If `d.pattern` ∈ distortions → template from distortions row.
2. Else by table above.
3. Emit one `question` node linked to `d`.

This rule table is the **auditable core**: a judge can see detection→question mapping with no LLM opacity.

## Socratic Generation Layer
`route(d)` now returns `{question, socratic_intent, template_id, framing_string}` instead of a bare question. The `question` text comes from the base template in `socratic-layer.md`; `framing_string` is the orienting narrative (also from `socratic-layer.md` §5). Gemini Pro MAY paraphrase the question for tone/empathy, but the logged triple (`pattern`, `socratic_intent`, `template_id`) is immutable — paraphrasing never alters it. This preserves the audit trail while switching the voice to Socratic + empathic.

### Deepening (see socratic-layer.md §7)
If the answer to a routed question is a *closure* (§7.1) and still lacks a concrete instance, the router does **not** resolve the detection. It re-emits a *deepening* `question` node for the **same** detection: same immutable triple, plus `deepen_cycle: n` (1..2) and `technique` (e.g. `observation_split`, `metacognitive_nudge`). The per-pattern ladder in §7.3 selects the technique. Max 2 extra cycles per detection — then resolve regardless. Each deepening turn is its own auditable `question` node.

## Confidence gating
- conf ≥ 0.8 → auto-ask.
- 0.5–0.8 → ask, but label as "possible" and allow user to reject.
- < 0.5 → hold; surface only if no higher-confidence detection exists.
