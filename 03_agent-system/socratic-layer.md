# Socratic Messaging Layer — Source of Truth

This layer sits between the deterministic Meta-Model detector/router and the user. The detector still outputs a `pattern` + `surface` (unchanged, auditable). The router now maps each pattern to a `socratic_intent` (a Paul–Elder Socratic move) and a base template. Gemini may paraphrase wording, but the `pattern → socratic_intent → template` triple is always logged in the Problem Graph, so the proof-of-work survives.

## 1. Socratic move taxonomy (Paul–Elder, 8 types)
`clarification`, `probe-assumption`, `probe-evidence`, `probe-implication`, `probe-alternative`, `probe-viewpoint`, `probe-concept`, `meta-cognition`.

## 2. Pattern → Socratic intent mapping (single source of truth)

| pattern | socratic_intent | template_id | base template |
|---|---|---|---|
| simple_deletion | clarification | simple_deletion_1 | "When you say '[surface]', what specifically are you pointing at?" |
| comparative_deletion | probe-criteria | comparative_deletion_1 | "Faster than what — what's the benchmark you're measuring against?" |
| unspecified_referent | probe-assumption | unspecified_referent_1 | "You said '[surface]' — what made that feel like one actor / one mind?" |
| unspecified_verb | clarification | unspecified_verb_1 | "When you say '[surface]', what exactly did they do or say?" |
| cause_effect | probe-causal-link | cause_effect_1 | "How does '[surface]' actually produce that result — and what if it didn't?" |
| mind_reading | probe-evidence | mind_reading_1 | "What did you actually see or hear that tells you that?" |
| complex_equivalence | probe-equation | complex_equivalence_1 | "How does '[surface]' come to equal that — what link are you drawing?" |
| lost_performative | probe-source | lost_performative_1 | "Who says that — where did that rule come from?" |
| universal_quantifier | probe-alternative | universal_quantifier_1 | "Every time? Was there one moment it didn't — what was different?" |
| modal_necessity | probe-assumption | modal_necessity_1 | "What would actually break if you didn't — what if another way were possible?" |
| modal_possibility | probe-barrier | modal_possibility_1 | "What exactly stands in the way — and what would have to be true for it to be possible?" |
| meta_frame | meta-cognition | meta_frame_1 | "When you evaluate '[surface]', what happens if you treat it with curiosity rather than criticism?" |

## 3. Generation rule
`socratic_question(detection)` returns the base template with `[surface]` substituted. Gemini Pro MAY paraphrase for tone, but the logged triple (`pattern`, `socratic_intent`, `template_id`) is immutable. A judge replays detection → socratic_intent → question.

## 4. Voice rules (non-negotiable)
- Ask from assumed ignorance; never assert, never imply the answer.
- One question per turn.
- Follow the user's own logic; don't redirect to the agent's agenda.
- If the user asks for the answer, return a Socratic counter-question.
- **Clean Language Zero-Contamination Invariant (David Grove):** The agent must NEVER introduce unprompted metaphors, external analogies, or leading interpretations. Questions must strictly reuse the user's verbatim words and tokens.
- **No-LaTeX Plain Markdown Invariant:** Never output LaTeX formatting (`$...$`, `$$...$$`, `\rightarrow`, `\text{}`). Always use clean markdown and plain unicode characters (e.g. `→`) to ensure zero raw command leakage in chat.
- **Empathic framing (added 2026-08-28):** the Socratic method is rigorous, but the *voice* must make the user feel seen. Acknowledge the weight of what they brought before descending. Validation is not agreement — it is recognition that the problem is real to them.

## 5. Framing vocabulary — the "bedrock / descend" narrative (explicit, user-facing)
Core intuition (user, 2026-08-28): problems stack on top of each other; the fix is to descend to the load-bearing (first-principles) assumption rather than patch the top layer. Grounded in three established frameworks (see `02_map/VERIFICATION.md` defensible-lineage principle — this is framing, not NLP branding):
- **First principles thinking** (Aristotle *arche*; Descartes' methodic doubt; Musk "boil to fundamental truths, reason up") → detector strips distortions until the irreducible assumption is reached, then outcome is reasoned up from it.
- **Complexity debt / back to basics** (Wordsphere: "accumulated layers mask fundamental weaknesses") → the user's stacked problems ARE the complexity debt; the Problem Graph visualizes the layers; we strip to the core mechanic.
- **Root cause / Five Whys** (Toyota) → the S2 clarification loop is a cognitive five-whys; each Socratic question descends one layer.
- **Bedrock / load-bearing assumption** (Munger; Lean "bedrock of thinking") → the anchor metaphor for the bottom-most node.

**Orienting narrative strings (explicit, user-facing — use verbatim where natural):**
- Open: "Problems stack — each one rests on an assumption beneath it. Let's descend together to the load-bearing one."
- probe-assumption: "What's this actually resting on?"
- probe-causal-link: "Let's find what really drives this."
- clarification: "Back to what's actually being said."
- probe-evidence: "What is this built on?"
- probe-alternative: "Stripped to zero, what has to be true?"
- bridge-upstream: "Now that we have immediate traction on [downstream action], let's look at what is draining that tank so completely before you even walk through the door."
- Close: "Here's the bedrock this was sitting on — and the outcome that follows from it."

These strings are the *framing layer* — independent of the per-pattern question template. The template elicits; the framing string orients the user to the descent and reassures them the process is deliberate. **Both are logged** — the framing string is part of the `question` node's `framing_string` field, alongside the audit triple.

## 6. Empathic + Socratic turn shape
Each agent turn = (acknowledgement) + (framing string) + (Socratic question). Example:
> "That sounds like a real weight to carry. [acknowledgement] Problems stack — let's find what this one rests on. [framing] When you say 'they won't listen' — what made it feel like one mind deciding? [Socratic question]"

**Dual-Horizon Turn Shape (when upstream depletion co-occurs with downstream symptom):**
> 1. Acknowledge both: "Arriving home completely depleted is heavy, and it makes sense that evening routines feel overwhelming."
> 2. Triage downstream: "Let's set a simple 10-minute container for tonight so you get immediate breathing room."
> 3. Bridge upstream: "Once that's in place, let's explore what is emptying your tank during the day before you even get home."

The acknowledgement is genuine recognition, never a scripted filler. The method stays Socratic; the voice stays human.

## 7. Deepening Protocol — digging *with* the user past a shallow first answer
A user's first reply to a probe is often a closure ("that's the only thing," "I don't know," "it's just obvious") rather than a real answer. The router must NOT resolve a detection on a closure. Instead it escalates through a **deepening ladder** before marking the detection resolved. This honors that people frequently under-dig their own reasoning.

### 7.1 Closure-signal detector (runs after every answer in S2)
Mark the answer as a *closure* if ANY hold:
- Short / one-word / "I don't know" / "that's it" / "only one thing" / "it's obvious".
- No concrete observation supplied where the intent was `probe-evidence` / `clarification` / `probe-assumption`.
- Restates the original claim without new specificity.
If closure AND the pattern still lacks a concrete instance → enter deepening (max 2 extra cycles; then resolve regardless to avoid looping).

### 7.2 Deepening techniques (defensible lineages — no NLP branding)
| technique | lineage | when to use | example phrasing |
|---|---|---|---|
| Observation vs interpretation split | CBT "check the facts" / DBT | mind_reading, cause_effect | "Literally — what were the words? And what did you add on top of them?" |
| Evidence ladder (descend to one concrete moment) | Paul–Elder probe-evidence | mind_reading, unspecified_referent | "If you point to the single moment that sealed it — what was it?" |
| Temporal / recency probe | Motivational interviewing (elaboration) | any closure | "Did that land in the moment, or grow afterward?" |
| Third-position reality check | Perceptual positions (de-branded "viewpoint") | mind_reading, complex_equivalence | "A colleague heard only the comment, not your conclusion — what would they say you had evidence for?" |
| Positive-intent ladder | Core Transformation (backward chaining) | resistance, modal_necessity, ecology conflicts | "When you hesitate to do that, what higher protective outcome is that part of you trying to achieve?" |
| Metacognitive nudge | Paul–Elder meta-cognition | ANY early closure | "We landed on 'that's the only thing' fast — full stop, or is there a part you haven't said yet?" |
| Stay-with (reflective restatement, don't fill gap) | MI "resist the righting reflex" | ANY closure | "So the comment sits there as the whole case." (then wait — invite, don't propel) |

### 7.3 Per-pattern deepening ladder (priority order)
- `mind_reading`: observation/interpretation split → evidence ladder → third-position → metacognitive nudge.
- `cause_effect`: evidence ladder ("what specifically links X to Y?") → temporal → metacognitive.
- `complex_equivalence`: observation/interpretation split → third-position.
- `unspecified_referent` / `unspecified_verb` / `simple_deletion`: evidence ladder (one concrete instance) → metacognitive.
- `modal_necessity` / `modal_possibility`: positive-intent ladder ("what is that protecting?") → "what exactly breaks?" → evidence ladder.
- `meta_frame`: metacognitive nudge ("what shifts if you observe with curiosity?") → observation/interpretation split.
- `universal_quantifier`: "one exception?" → evidence ladder.
- `lost_performative`: "who said?" → third-position.

### 7.4 Logging
Each deepening turn is its own `question` node (style: socratic, `deepen_cycle: n`) linked to the same detection, with the same immutable triple + framing string. The audit trail shows precisely how many descents it took to reach bedrock.
