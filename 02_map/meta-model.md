# The Meta-Model — Linguistic Diagnostic Matrix

Source: paper §2. A rule-based deconstruction engine: detect Surface Structure violations → generate precision questions that recover Deep Structure data. Three filter families: **Deletion**, **Distortion**, **Generalization** (§1.1).

Core axiom: a "problem state" is representational impoverishment, not reality. `dim(S_problem) << dim(D_experience) << dim(T)`. The agent's job is to restore missing dimensions — never to advise inside the user's impoverished map.

## Diagnostic patterns

| Pattern | Trigger | Question | Class of |
|---|---|---|---|
| Simple Deletion | "I'm terrified." | "What specifically are you terrified of?" | Deletion |
| Comparative Deletion | "We need a better approach." / "It's too expensive." | "Better than what, specifically? What's the current baseline and the exact threshold?" | Deletion |
| Unspecified Referential Index | "People are blocking me." / "They don't understand." | "Who specifically? Which individual holds the veto power?" | Deletion |
| Unspecified Verb | "My co-founder is undermining me." | "How specifically? What exact words or actions in the last meeting?" | Deletion |
| Cause-Effect | "Her silence makes me angry." | "How specifically does her silence cause you to choose anger?" | Distortion |
| Mind Reading | "My team thinks I'm incompetent." | "What observable data told you that — exact words spoken, or an expression you're interpreting?" | Distortion |
| Complex Equivalence | "He didn't reply, which means he doesn't respect me." | "How does a delayed reply equal disrespect? Ever delayed replying to someone you respected?" | Distortion |
| Lost Performative | "It's unprofessional to show frustration." | "Who established that rule? In what context would it be the highest professional service?" | Generalization |
| Universal Quantifier | "I always mess up." / "Nobody ever listens." | "Always? Was there ever one exception? What was different about it?" | Generalization |
| Modal Necessity | "I have to handle everything myself." | "What would happen if you didn't? What specifically prevents delegating?" | Generalization |
| Modal Possibility | "I can't pitch VCs; I freeze up." | "What prevents you? What would happen if you did? What would you need to make it possible?" | Generalization |

## Detection heuristics (for a classifier layer)

- Comparatives (-er, more, less, too) → missing baseline.
- Ambiguous plurals (they, people, management) → missing referent.
- Causal conjunctions (makes, causes, forces) → cause-effect distortion.
- "X means Y" → complex equivalence.
- Universal quantifiers (always, never, all, none, everybody) → seek counter-example.
- Necessity modals (must, should, have to) → simulate consequence boundary.
- Possibility modals (can't, impossible) → identify blocking condition.

## The Wheelbarrow Test (de-nominalization)

If a noun can't be put in a wheelbarrow, it's a frozen process: re-verb it. "I have a communication problem" → "How specifically are you communicating, with whom, about what?" Nominalizations erase agency, freeze temporal dynamics, and are unfixable as objects — unpack them into verbs with agents and time.
