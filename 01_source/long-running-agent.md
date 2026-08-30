Building a **long-running agent with persistent workflows** using the Google Agent Development Kit (ADK) centers on creating **durable, crash-resilient systems** capable of handling multi-step processes, surviving system failures, and integrating human approvals.

---

### 1. The Core Engineering Challenge: The "Duplicate Execution" Trap
In real-world applications (such as employee onboarding or procurement), workflows span extended timelines and face server restarts or human wait states. 

The primary trap when building long-running agents is that a system configured to auto-resume after a crash might blindly repeat non-idempotent tasks—such as ordering two laptops or processing the same request twice.

---

### 2. Key Architectural Components in Google ADK
The curriculum outlines a 6-level (L0→L5) technical progression for persistent ADK workflows:

* **Explicit State Machine**: Designing the workflow as an explicit state machine so every stage and transition is strictly tracked.
* **Durable Session Persistence (`DatabaseSessionService` → Cloud SQL)**: Transitioning session state from in-memory storage to persistent databases like Cloud SQL so progress survives server restarts.
* **Crash Recovery (`ResumabilityConfig`)**: Configuring ADK's resumability settings so the system automatically detects interruptions and resumes from the precise step where it stopped.
* **Human-in-the-Loop Pauses (`LongRunningFunctionTool`)**: Leveraging long-running tools that safely pause execution while waiting for human interaction (such as manager approvals) before resuming the workflow.
* **Idempotency Guards**: Implementing custom guards to verify whether an action has already occurred before executing external API calls upon resumption.
* **Deployment & Monitoring**: Deploying to **Agent Runtime** and leveraging **Cloud Trace** to audit reasoning steps and trace system behavior.

---

### 3. Advice for Hackathon Demonstration & Judging
* **Handling Asynchronous Time Gaps in Demos**: For tasks that span hours or days, you do not need to show the full real-time wait in your 4-minute submission video. Judges recommend showing the initial triggering state, demonstrating the completed state, and scrolling through Cloud Run or terminal logs to prove asynchronous execution.
* **Judging Evaluation**: Judges heavily evaluate failure tolerance and state architecture, looking closely at how well your system isolates tools, manages persistent memory, and handles crash recovery without looping or wasting tokens.

---

🛠️ *Would you like to design an idempotency strategy or state machine flow for a long-running process in your proposed project?*