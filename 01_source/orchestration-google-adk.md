The source **"Architecting Multi-Agent Teams: Mastering the Three Orchestration Patterns of ADK 2"** outlines a technical Google Cloud workshop led by Google DevRel engineers (Annie Wang, Christina Lin, and Romin Irani). 

Rather than treating every multi-agent problem with a single simplistic approach ("handing you a hammer and calling everything a nail"), the curriculum teaches developers how to choose, structure, and compose multi-agent architectures using Google ADK 2.

---

### 1. The Three ADK 2 Orchestration Patterns
The workshop breaks down multi-agent orchestration into three core patterns:

* **Graph Workflows**: Structured, deterministic routing and topology. This pattern uses explicit nodes and graphs to handle flow control—such as executing tasks in parallel and aggregating them, or branching logic deterministically without wasting extra LLM calls.
* **Collaborative Agent Teams**: Peer-based or concierge-driven coordination where specialized sub-agents work together. A primary agent (like a concierge) coordinates a dynamic subset of specialist sub-agents running concurrently.
* **Dynamic (LLM-Shaped) Workflows**: Workflows where the execution path and depth are shaped dynamically by the model at runtime, enabling complex behaviors like recursive research.

---

### 2. Practical Project: The "Marathon Race-Day Coach"
To demonstrate these patterns in practice, the workshop guides developers through building a single unified project—a **Marathon Race-Day Coach**—that evolves across **eight runnable levels (L0 → L5)**:

1. **Parallel Fan-Out (`JoinNode`)**: Running multiple worker agents simultaneously and combining their outputs cleanly at a join node.
2. **Deterministic Routing**: Branching logic conditionally without triggering an extra LLM generation call, saving latency and token cost.
3. **Collaborative Concierge**: Managing multiple specialist sub-agents dynamically in parallel based on real-time user context.
4. **Recursive Deep-Research**: Triggering recursive investigation loops where sub-agents dig deeper into unstructured data until constraints are met.

---

### 3. The Pattern Decision Tree
The session concludes by equipping developers with a **decision tree** to evaluate system requirements and select (or combine) the right pattern based on factors like latency, state complexity, security boundaries, and token efficiency.

---

🎯 *If you're considering the **Fortified Enterprise Fleet** track for the hackathon, integrating one of these graph or collaborative concierge patterns is a great way to showcase multi-agent discipline to the judges. Would you like to map out how a concierge or fan-out architecture could fit your system design?*