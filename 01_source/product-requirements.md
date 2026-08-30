In the live Q&A build session **"How to Win the All Things Agentic Hackathon: Judging Criteria"**, Google DevRel Engineering Manager Christina Lin, Google Product Marketing Manager Willie, and Devpost host Darliss Call broke down exactly what judges are looking for and how to structure a winning submission.

Here are the main points and insider takeaways covered in the session:

---

### 1. Clarifications on the Three Tracks
* **Taskmaster**: Focuses on **taking action to solve real friction** rather than just generating text or conversing like a standard chatbot. It rewards agents that handle multi-step background chores across extended timelines (hours, days, or weeks) to do the heavy lifting for humans.
* **Collaborative Partner**: Focuses on **smart data lifecycles, active data synthesis/mutation, and autonomous self-improvement**. Christina explicitly warned against submitting a basic retrieval system (like a standard RAG/vector query wrapper)—winning entries actively transform data and adapt how they interact based on user feedback.
* **Fortified Enterprise Fleet**: Focuses on **multi-agent swarms working securely**. Judges look for enterprise security controls, audit trails, persistent memory, zero-trust delegation between agents, and guardrails like Model Armor.

---

### 2. Submission Blueprint & Video Strategy
* **The 4-Minute Video Rule**: Judges strictly **cut off watching after the 4-minute mark**. 
* **Hook Judges in the First 30 Seconds**: Christina advised developers to **wow the judges immediately** with a clear problem statement and live action.
* **Show Live Action & Backend GCP Proof**: The video must show an unedited live demo (UI updates, terminal logs, or DB changes) alongside **visual proof that the backend runs on Google Cloud** (e.g., Cloud Run dashboard, Google Cloud Console, or Vertex AI logs).
* **How to Demo Long-Running Agents**: If your agent takes days to run, you don't need a multi-day video recording. Explain the problem, show the final completed state, and scroll through execution/terminal logs to prove asynchronous execution.
* **Use Authentic Voiceovers**: Avoid AI-generated synthetic voices for video narrations—judges find human developer walkthroughs much more genuine and engaging.

---

### 3. Documentation Essentials
* **Clean Architecture Diagram**: Don't turn your architecture diagram into a wordy essay. Keep it visual, clean, and easily consumable so judges can instantly see how Gemini, your agent framework, database, and GCP hosting connect.
* **Informative `README.md`**: Provide clear setup/spin-up instructions, folder layout details, and technical insights or trade-offs you were proud of. If judges want to verify your code or claims, a well-structured `README.md` helps them evaluate your engineering quickly.

---

### 4. Judging Mechanics & Strategic Advice
* **Multi-Judge Scoring**: Every submission is evaluated across the weighted criteria—**Innovation & Operational Utility (40%)**, **Architectural Discipline (30%)**, and **Demo Readiness (30%)**—by multiple judges whose scores are averaged for fairness.
* **Quality Over Breadth**: When deciding between showing multiple simple workflows or one complex workflow, Christina recommended **focusing on one high-value, "wow-inducing" workflow** that highlights true agent autonomy.
* **Don't Worry About Speed**: Fast execution won't hurt your score—judges care about **clever operational design and task completion**, not making an agent run unnecessarily long on the clock.
* **Submit & Have Fun**: Christina and Willie emphasized that developers shouldn't get bogged down in minor details—finish your core build, submit before the deadline, and have fun building!
