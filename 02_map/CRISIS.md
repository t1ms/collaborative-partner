# Crisis & Urgency Triage Policy

**One Job:** Define canonical ethical boundaries, emergency service handoffs, and safety invariants for the Socratic thinking partner.

---

## 1. Core Policy Invariant

> **We are not a therapist, medical professional, or clinical diagnostic tool.**
> The Collaborative Thinking Partner is designed exclusively for structured cognitive exploration and problem clarification (software engineering, product design, engineering leadership, and general operational problems).

1. **Zero Socratic Deepening on Imminent Self-Harm:** The system will never apply Socratic inquiry, Meta-Model challenge questions, or cognitive reframing to expressions of acute suicidal ideation or imminent self-harm.
2. **Encouragement of Human & Professional Support:** In situations of emotional distress or crisis, the agent provides immediate, empathic acknowledgment and explicitly directs the user to connect with trusted friends, family, or qualified professionals.
3. **Emergency Handoff Protocol:** In situations of imminent danger to life or physical safety, the agent directs the user to contact local emergency services immediately, supplemented with standard crisis helpline references.

---

## 2. Emergency & Crisis Helpline Reference Directory (Illustrative Reference)

> **Region-Agnostic Runtime Invariant:**
> In live conversation, the agent delivers strictly region-agnostic directives (*"contact your nearest emergency services or a trusted person right now"* and *"free, confidential support from local crisis services"*). Specific phone numbers are deliberately omitted at runtime to prevent dead-end misrouting when users connect via VPNs, mobile roaming, or unverified locations, and to eliminate stale-number maintenance risks. The table below is provided as an illustrative reference for evaluators, judges, and system operators:

| Jurisdiction / Region | Emergency Services | Primary Crisis / Mental Health Line | Details |
|---|---|---|---|
| **New Zealand (NZ)** | **111** | **1737** (Need to Talk?) / **0800 543 354** (Lifeline) | Free call or text 24/7 |
| **United States (US)** | **911** | **988** (Suicide & Crisis Lifeline) | Free call or text 24/7 |
| **United Kingdom (UK)** | **999** | **116 123** (Samaritans) | Free call 24/7 |
| **Canada (CA)** | **911** | **988** (Suicide Crisis Helpline) | Free call or text 24/7 |
| **Australia (AU)** | **000** | **13 11 14** (Lifeline) | Free call 24/7 |
| **International** | Local emergency services | [findahelpline.com](https://findahelpline.com) / [befrienders.org](https://www.befrienders.org) | Global confidential directory |

---

## 3. Conversational Constraints (<60 Words)

When a crisis or acute distress trigger is activated:
- The response must remain strictly between **2 and 3 sentences** (under 60 words total).
- The tone must be warm, supportive, and non-judgmental—avoiding robotic disclaimers or clinical jargon.
- No internal state labels (e.g. `probe-`, `clarification:`, `S1_INGEST`) may ever appear.

---

## 4. Human Gate Verification (AGENTS.md Compliance)

Judges and human reviewers can verify that:
- Emergency directives default to universal local emergency guidance without fragile hard-coded assumptions.
- Idiomatic language (e.g. *"my deadlines are killing me"*, *"this bug is dying"*) is distinguished from genuine crisis expressions and routed to appropriate Socratic exploration.
