# Real-User Validation Corpus — Reddit-style problem statements

Source: **Hacker News "Ask HN"** (public Algolia API), 2026-08-28. Reddit itself was fully blocked from this host (403 on API, HTML block page on curl, Cloudflare walls on redlib mirrors, no Chrome for the browser harness), so HN stands in — it gives the same messy first-person decision/problem framing we need, and stays inside our no-therapy, professional/decision boundary better than therapy subs would.

Each case below is a **real post** (trimmed for length, verbatim otherwise). For each we annotate:
- `triggers` — which of the 11 Meta-Model patterns the detector SHOULD fire on.
- `bedrock_hypothesis` — the load-bearing assumption the descent likely reaches (for test/design validation, not a fixed answer).
- `good_for` — which phase(s) it exercises.

These are design-validation fixtures. In Phase B they become golden eval cases: feed the statement, assert the detector fires the expected patterns and the Socratic layer emits an acknowledged, framed, single question.

---

## Case 1 — "Should I quit my job?" (classic stuck)
**Post (Ask HN, 192 pts):** "I'm working for a German automobile corporate in Spain as a project leader. I'm 29, I've studied electronic engineering, I don't have kids, and I'm not married. What I do at my current job all day is emails, spreadsheets, and meetings — none of which uses my engineering degree. I feel like I'm wasting my best years. Should I quit?"

- **triggers:** `unspecified_verb` ("wasting my best years" — what specifically counts as waste?), `modal_possibility` ("Should I quit?" framed as can't-see-alternative), `lost_performative` ("best years" — who says 29 is the threshold?).
- **bedrock_hypothesis:** the assumption that a degree must be *used* in the job for the years to count; and that quitting = the only lever.
- **good_for:** S2 clarification, S3 outcome (what does "not wasting" look like, self-initiated?), S4 viewpoint (from the employer's chair).

## Case 2 — "struggle with motivation at my programming job" (vague cause)
**Post (Ask HN, 39 pts):** "For a while now (a couple of months) I struggle with having any motivation at my programming job. I like the company's profile and have a great team, but: I was hired at a lower level than I interviewed for... I don't feel I'm growing. I just can't seem to care anymore."

- **triggers:** `cause_effect` ("lower level → can't care"), `unspecified_verb` ("growing" — measurable how?), `modal_possibility` ("can't seem to care").
- **bedrock_hypothesis:** conflates *external title* with *internal motivation*; the load-bearing belief is "my effort requires the company to validate me."
- **good_for:** S2 causal-link probe, S3 sensory outcome, S5 ecology (what's the cost of staying disengaged?).

## Case 3 — "stuck in this dilemma" laptop choice (decision paralysis)
**Post (Ask HN, 16 pts):** "Been stuck in this dilemma for a long time and wanted to get out there and make a decision on which way to go, once and for all. I've been an Apple hater for their predatory tactics and overpriced products and also because an unbearable m1 fanboy culture... but the M1 benchmarks are undeniably good. 16gb or 32GB?"

- **triggers:** `universal_quantifier` ("always stuck"), `complex_equivalence` ("Apple = predatory → I must reject even good products"), `unspecified_referent` ("once and for all" — what ends it?).
- **bedrock_hypothesis:** identity ("I am an Apple-hater") fused with a purchase decision; the real question is whether self-image can tolerate the tool.
- **good_for:** S2 complex-equivalence probe, S4 viewpoint (from "future me who just wants the job done"), S3 outcome.

## Case 4 — "how to think about direction in life/career" (overwhelmed)
**Post (Ask HN, 66 pts):** "I'd like to hear some ideas on how to get myself unstuck. Before I get into it, I want to recognize how privileged this whole story is... I'm having a hard time knowing what I actually want versus what I've been told to want. Everything feels like noise."

- **triggers:** `simple_deletion` ("noise" — what specifically?), `unspecified_referent` ("they"/"told to want" — who?), `nominalization` ("direction" as a static thing).
- **bedrock_hypothesis:** no internal compass distinct from external scripts; the load-bearing assumption is "I should already know what I want."
- **good_for:** S2 clarification, S3 outcome (stated in positive — what do you want *instead* of noise?), S5 ecology.

## Case 5 — "Junior dev in charge of rewriting 500k line PHP app" (scope paralysis)
**Post (Ask HN, 13 pts):** "We are a 4 person company... Star is 11 years old and showing its age. It was developed entirely by one of the founders, who has no formal training, and the niche industry we serve has changed... I've been tasked with rewriting it. I have no idea where to start."

- **triggers:** `unspecified_verb` ("rewriting" — what does done look like?), `simple_deletion` ("no idea where to start" — which part specifically?), `modal_possibility` ("no idea" = can't).
- **bedrock_hypothesis:** treats "rewrite" as one monolithic act rather than a sequence; the load-bearing assumption is "I must hold the whole system in my head before moving."
- **good_for:** S2 clarification + chunking (S3), S4 viewpoint (founder's intent), S5 ecology (what breaks if partial?).

## Case 6 — "Should I quit to sell my stock options?" (false binary)
**Post (Ask HN, 33 pts):** "I am an early employee of a company that IPO'd... sitting on a life-changing amount of stock options - mostly already vested. Since IPO I have stayed with the company while many other early employees left. Should I quit to sell, or stay?"

- **triggers:** `comparative_deletion` (implicit "better to sell than stay" — than what baseline?), `unspecified_referent` ("life-changing" — by what measure?), `lost_performative` (norm that leaving = cashing out betrayal).
- **bedrock_hypothesis:** the option set is collapsed to two; the load-bearing assumption is "staying and selling are mutually exclusive."
- **good_for:** S2 comparative + assumption probe, S3 outcome (what do you control?), S4 viewpoint.

## Case 7 — "I am 34 years old refugee how can I find a job" (denial → action)
**Post (Ask HN, 28 pts):** "This is so uncomfortable to me so I decided to do two things: create a new account so no shame in the future, and accept the problem that I have. I've been in a state of denial the entire decade. The paperwork is overwhelming and I don't know what I'm eligible for."

- **triggers:** `universal_quantifier` ("entire decade"), `simple_deletion` ("paperwork overwhelming" — which forms specifically?), `unspecified_verb` ("eligible" — by what rule?).
- **bedrock_hypothesis:** the shame of the past blocks the first concrete eligibility question; load-bearing assumption is "I am not allowed to ask for help."
- **good_for:** S2 clarification, S3 chunking (one form at a time), S5 ecology (what does asking cost?).

---

## Coverage summary (design check)
| Pattern | Cases exercising it |
|---|---|
| simple_deletion | 4, 5, 7 |
| comparative_deletion | 6 |
| unspecified_referent | 1, 3, 4, 5, 6, 7 |
| unspecified_verb | 1, 2, 3, 5, 7 |
| cause_effect | 2 |
| mind_reading | (none yet — add later) |
| complex_equivalence | 3 |
| lost_performative | 1, 6 |
| universal_quantifier | 3, 7 |
| modal_necessity | (sparse — Case 1 "should" leans here) |
| modal_possibility | 1, 2, 5 |

**Gap:** `mind_reading` and `modal_necessity` are under-represented. Phase B eval should include at least one synthetic case for each to guarantee full detector coverage (e.g. "They think I'm not leadership material" → mind_reading; "I must accept this offer or I'll be unemployed forever" → modal_necessity).

Raw scrape saved: `_hn_raw.json` (60 posts). Archive of this file (if revised): `../_archive/agent-system/`.
