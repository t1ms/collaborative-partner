# 01_source/research — Theoretical Foundations, Empirical Grounding & Conversational Architecture

This directory contains the canonical research corpus and empirical papers underpinning the **Collaborative Thinking Partner**. Every cognitive model, state machine transition, and conversational generation configuration in the codebase directly traces to these sources.

---

## Complete Research Corpus (All Available as Clean `.md`)

| Document | Domain / Lineage | Role in Agent & Judging Alignment |
|---|---|---|
| [`bandler-nlp-thinking-partners.md`](bandler-nlp-thinking-partners.md) | Cognitive Modeling & Cybernetics (1975–Present) | **Primary Ontology**: Meta-Model algorithmic parsing, VAKOG submodal coding, TOTE feedback loops, and 5-phase problem-to-outcome pipeline. |
| [`NLP Derivatives and Empirical Validity.md`](NLP%20Derivatives%20and%20Empirical%20Validity.md) | Clinical Psychology & Evidence-Based NLP | **Defensibility & De-branding**: Validates effective linguistic techniques (Clean Language, Socratic questioning) while excising unverified pseudoscience. |
| [`2024-EMMI-Empathic-Multimodal-MI.md`](2024-EMMI-Empathic-Multimodal-MI.md) | Motivational Interviewing (arXiv:2406.16478) | **Working Alliance**: Proves that short, targeted reflections using the user's verbatim words drive the human-agent alliance. |
| [`2026-CARE-Therapeutic-Alliance-LLM.md`](2026-CARE-Therapeutic-Alliance-LLM.md) | Computational Alliance (arXiv:2602.20648) | **Verbosity Guardrail**: Turn-level alliance modeling proving that verbose agent responses drop user trust; rationale-augmented brevity restores it. |
| [`2025-PST-MI-Caregivers-LLM.md`](2025-PST-MI-Caregivers-LLM.md) | Problem-Solving Therapy (arXiv:2506.11376) | **Efficiency vs. Thoroughness**: Proves single-point high-leverage Socratic questions outperform multi-part interrogations. |
| [`Transforming Discussion Language...md`](Transforming%20Discussion%20Language%20-%20Applying%20Marketing%20Communication%20Architecture%20to%20Interpersonal%20and%20Strategic%20Discourse.md) | Strategic Communication & Semantics | **Discourse Architecture**: Operational Inversion (leading with outcomes), Hayakawa's Ladder of Abstraction (vertical oscillation), and Two-Sided Inoculation. |
| **Grice (1975)** | Pragmatics & Linguistics | **Maxim of Quantity**: "Make your contribution as informative as is required, and not more informative than is required." |

---

## Full Scientific Bibliography & Attribution

1. **Cognitive Science & Linguistics:**
   - Bandler, R., & Grinder, J. (1975). *The Structure of Magic I: A Book About Language and Therapy*. Science and Behavior Books.
   - Bandler, R., & Grinder, J. (1976). *The Structure of Magic II*. Science and Behavior Books.
   - Miller, G. A., Galanter, E., & Pribram, K. H. (1960). *Plans and the Structure of Behavior*. Henry Holt & Co. (Origins of the TOTE feedback unit).
   - Dilts, R. (1999). *Sleight of Mouth: The Magic of Conversational Belief Change*. Meta Publications.
   - Grinder, J., & DeLozier, J. (1987). *Turtles All the Way Down: Prerequisites to Personal Genius*. Quantum Leap. (Perceptual positions 1st, 2nd, 3rd).
   - Cameron-Bandler, L. (1978). *They Lived Happily Ever After*. Meta Publications. (Codification of Positive Intent and outcome framing).
   - Hayakawa, S. I. (1949). *Language in Thought and Action*. Harcourt, Brace. (The Ladder of Abstraction).
   - Paul, R., & Elder, L. (2006). *Critical Thinking: Tools for Taking Charge of Your Learning and Your Life* (2nd ed.). Prentice Hall.

2. **Empirical Literature & De-Branding Evidence:**
   - Witkowski, T. (2010). Thirty-five years of research on Neuro-Linguistic Programming. *Polish Psychological Bulletin*, 41(2), 58–66.
   - Passmore, J., & Rowson, T. (2018). Neuro-linguistic programming: a critical review of NLP research and the application of NLP for coaching/mentoring. In *The Psychology of Coaching and Mentoring*.
   - Sturt, J., et al. (2012). Neuro-linguistic programming: a systematic review of the effects on socioemotional outcomes. *British Journal of General Practice*, 62(604), e757–e764.
   - Grove, D. J., & Panzer, C. W. (1989). *Resolving Traumatic Memories: Metaphors and Symbols in Psychotherapy*. Irvington Publishers. (Clean Language).
   - Locke, E. A., & Latham, G. P. (2002). Building a practically useful theory of goal setting and task motivation. *American Psychologist*, 57(9), 705–717.

3. **Conversational Science & LLM Working Alliance:**
   - Galland, L., Pelachaud, C., & Pecune, F. (2024). EMMI - Empathic Multimodal Motivational Interviews Dataset: Analyses and Annotations. *arXiv preprint arXiv:2406.16478*.
   - Li, A., Wang, C., Lu, Y., Xu, R., Ma, L., & Lan, Z. (2026). CARE: An Explainable Computational Framework for Assessing Client-Perceived Therapeutic Alliance Using Large Language Models. *arXiv preprint arXiv:2602.20648*.
   - Wang, L., Carrington, D., Filienko, D., El Jazmi, C., Xie, S. J., De Cock, M., Iribarren, S., & Yuwen, W. (2025). Large Language Model-Powered Conversational Agent Delivering Problem-Solving Therapy (PST) for Family Caregivers. *arXiv preprint arXiv:2506.11376*.
   - Grice, H. P. (1975). Logic and conversation. In *Syntax and Semantics* (Vol. 3, pp. 41–58). Academic Press.
   - Sweller, J. (1988). Cognitive load during problem solving: Effects on learning. *Cognitive Science*, 12(2), 257–285.

4. **Google Cloud ADK Architecture:**
   - Wang, A., Lin, C., & Irani, R. (2026). *Architecting Multi-Agent Teams: Mastering ADK 2*. Google Cloud DevRel Workshop.
   - Lin, C., Willie, & Call, D. (2026). *How to Win: All Things Agentic Hackathon Judging Criteria*. Google Cloud.

---

## Traceability to Implementation
- **Detection & State Machine:** Grounded in `bandler-nlp-thinking-partners.md` $\rightarrow$ [`02_map/meta-model.md`](../../02_map/meta-model.md) $\rightarrow$ [`src/thinking_partner/agent/classifier.py`](../../src/thinking_partner/agent/classifier.py)
- **Fluid Socratic Generation:** Grounded in EMMI, CARE, PST-MI, & Strategic Discourse $\rightarrow$ [`02_map/conversational-dynamics.md`](../../02_map/conversational-dynamics.md) $\rightarrow$ [`src/thinking_partner/agent/orchestrator.py`](../../src/thinking_partner/agent/orchestrator.py)
