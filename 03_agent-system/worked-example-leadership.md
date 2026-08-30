# Worked Example — "They don't think I'm leadership material"

A live-trace simulation of the design (architecture.md + socratic-layer.md + state-machine.md) against a problem statement. This is the `mind_reading` gap-filler from `validation-corpus.md` — a pattern no real HN post exercised.

**Seed statement (user, Turn 1):** "They don't think I'm leadership material, so I shouldn't bother applying for the promotion."

---

## S1 — Ingestion + Classify
Detector fires 4 patterns (priority per state-machine.md: distortions first):

| # | pattern | surface | socratic_intent | template_id | confidence |
|---|---|---|---|---|---|
| d1 | mind_reading | "They don't think I'm leadership material" | probe-evidence | mind_reading_1 | 0.9 |
| d2 | cause_effect | "so I shouldn't bother applying" | probe-causal-link | cause_effect_1 | 0.85 |
| d3 | unspecified_referent | "They" | probe-assumption | unspecified_referent_1 | 0.8 |
| d4 | lost_performative | "shouldn't" | probe-source | lost_performative_1 | 0.7 |

Graph nodes created: `utterance#1` → `detection#d1..d4`.

## S2 — Clarify (one question per turn, distortions first)

**Turn 2 (d1, mind_reading):**
> *Acknowledgement:* "That's a heavy thing to carry — feeling pre-judged before you've had the chance."
> *Framing:* "What is this built on?"
> *Socratic question:* "What did you actually see or hear that told you they don't think you're leadership material?"
> *Logged:* `{pattern: mind_reading, socratic_intent: probe-evidence, template_id: mind_reading_1, framing_string: "What is this built on?", style: socratic}`

**User:** "Well… my skip-level said the last project 'lacked strategic ownership.' That's the only thing."

> *Closure-signal detector:* answer closes with "that's the only thing" → no concrete observation of *their internal state*, just one reported comment. `mind_reading` still lacks the actual evidence the user used to infer "they don't think I'm material." → **enter deepening (cycle 1 of 2).**

**Turn 2.1 (deepen cycle 1 — observation/interpretation split):**
> *Acknowledgement:* "Fair — one comment. But notice you leapt from 'lacked strategic ownership' to 'they don't think I'm material.' Those aren't the same thing."
> *Framing:* "What is this built on?"
> *Socratic question:* "Literally — what were their words? And what did you add on top of them to land on 'not material'?"
> *Logged:* `{mind_reading, probe-evidence, mind_reading_1, "What is this built on?", deepen_cycle: 1}`

**User (illustrative):** "She said 'you operated the project but didn't set its direction.' I guess I read 'operated' as 'just a doer, not a leader.'"

> *Closure-signal detector:* still one comment, but the user has now split observation ("operated, didn't set direction") from interpretation ("just a doer"). Concrete instance present → **resolve d1.** (One deepening cycle reached bedrock; no need for cycle 2.)

**Turn 3 (d2, cause_effect):**
> *Acknowledgement:* "Okay — so one piece of feedback became the whole story in your head. I get why that sticks."
> *Framing:* "Let's find what really drives this."
> *Socratic question:* "How does their one comment actually mean you shouldn't apply — and what if it didn't?"
> *Logged:* `{cause_effect, probe-causal-link, cause_effect_1, "Let's find what really drives this."}`

**Turn 4 (d3, unspecified_referent):**
> *Acknowledgement:* "Naming the source matters — 'they' can feel like a wall when it's really one person."
> *Framing:* "What's this actually resting on?"
> *Socratic question:* "When you say 'they' — was it the skip-level, or a wider group? What made it feel like one mind deciding?"
> *Logged:* `{unspecified_referent, probe-assumption, unspecified_referent_1, "What's this actually resting on?"}`

**Turn 5 (d4, lost_performative):**
> *Acknowledgement:* "The word 'shouldn't' carries weight — like there's a rule you'd be breaking."
> *Framing:* "Back to what's actually being said."
> *Socratic question:* "Who says you shouldn't apply — where did that rule come from?"
> *Logged:* `{lost_performative, probe-source, lost_performative_1, "Back to what's actually being said."}`

## S3 — Outcome Architecture
**Turn 6:**
> *Acknowledgement:* "You've already done the hard part — you've separated one comment from your whole worth."
> *Framing:* "Stripped to zero, what has to be true?"
> *Socratic question:* "In the positive — what do you want instead of 'not applying'? State it as something you control. What would 'a real shot at the promotion' look like, owned by you?"
> *User:* "I want to submit an application that shows two examples of strategic ownership, and ask my manager for 15 minutes to discuss it."

Outcome predicates logged: `positive ✓, self_initiated ✓, sensory ✓ (two examples + 15-min meeting), chunk ✓`.

## S4 — Multi-angle
**Turn 7:**
> *Acknowledgement:* "Holding both views at once is uncomfortable but useful."
> *Socratic prompts:*
> - *From their chair:* "If your skip-level saw two concrete examples of strategic ownership, what would that do to the 'lacked' label?"
> - *Systemic:* "If nobody ever applied unless they were already 100% seen as ready, how would the promotion pipeline stay alive?"

## S5 — Ecology
**Turn 8:**
> *Acknowledgement:* "Let's check this won't cost you something you value."
> *Socratic question:* "If you apply and don't get it — what's the actual trade-off? What do you stand to lose versus what you learn?"

## S6 — Close (bedrock)
> "Here's the bedrock this was sitting on: the unexamined assumption that one person's single comment = a fixed verdict on your leadership, and that 'they' thinking it settles what you're allowed to do. Stripped to zero, the only load-bearing fact is one piece of feedback. From there the outcome follows naturally: you own the application, you show the examples, you ask for the conversation. Here is your own thinking, debugged and visible."

Graph closes: `outcome_predicate`s + `perspective`s + `constraint` linked to root.

---

## What this proves about the design
- **Detector coverage:** exercises `mind_reading` (the flagged gap) + `cause_effect` + `unspecified_referent` + `lost_performative` in one short statement.
- **Audit trail:** every question carries the immutable triple (`pattern`, `socratic_intent`, `template_id`) + `framing_string` — a judge can replay exactly which rule fired.
- **Voice:** acknowledgement precedes every question; the bedrock metaphor is named explicitly at close.
- **Bedrock reached:** the descent moved from "they don't think I'm material" → "one comment = fixed verdict" → "I'm not allowed to try" → the actual fact (one piece of feedback). That is the first-principles / complexity-debt descent in action.

---

## Appendix — Variant B: double closure ("I don't know" on deepen cycle 1)

Same seed, same S1 detections. Diverges at Turn 2.1 answer.

**Turn 2.1 answer (Variant B):** "I don't know… it's just obvious, I guess."
> *Closure detector:* `I don't know` + `just obvious` + still no concrete observation → **closure again** → enter **deepen cycle 2/2** (per-pattern ladder for `mind_reading`: observation_split → evidence_ladder → third_position → metacognitive_nudge → next is `metacognitive_nudge`).

**Turn 2.2 (deepen cycle 2 — metacognitive nudge):**
> *Acknowledgement:* "We landed on 'I don't know' fast — which makes sense, this thought has been running in the background."
> *Framing:* "What is this built on?"
> *Socratic question:* "Is that a full stop — 'there's nothing else' — or is there a part you haven't said yet? If you stayed with that moment for 10 more seconds, what detail comes back?"
> *Logged:* `{mind_reading, probe-evidence, mind_reading_1, "What is this built on?", deepen_cycle: 2, technique: metacognitive_nudge}`

**User:** "…She said 'you operated the project but didn't set its direction.' I heard 'operated' and filed it as 'just a doer.'"
> *Detector:* now observation/interpretation split present → concrete → **resolve d1** at cycle 2. (If still vague, we'd resolve anyway — max 2 caps looping.)

**Continues:** Turn 3 (d2 cause_effect) → Turn 4 (d3) → Turn 5 (d4) → S3/S4/S5/S6 identical to main trace.

**What Variant B proves:**
- Without cycle 2, d1 would have been falsely resolved on a closure. The ladder *stayed with* instead of advancing.
- Audit shows 1 base + 2 deepen nodes, same triple, `deepen_cycle` 1→2, `technique` logged — judge sees exactly how deep we dug.
- Voice held on cycle 2: names the speed without shaming, invites a 10-second stay-with, never implies withholding.
