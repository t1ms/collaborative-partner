let currentSessionId = null;

// DOM Elements
const chatHistory = document.getElementById("chatHistory");
const chatForm = document.getElementById("chatForm");
const messageInput = document.getElementById("messageInput");
const sendBtn = document.getElementById("sendBtn");
const newSessionBtn = document.getElementById("newSessionBtn");
const scenarioSelect = document.getElementById("scenarioSelect");
const currentPhaseBadge = document.getElementById("currentPhaseBadge");
const depthGaugeFill = document.getElementById("depthGaugeFill");

const adrContent = document.getElementById("adrContent");
const nodeCount = document.getElementById("nodeCount");
const versionBadge = document.getElementById("versionBadge");
const diffContent = document.getElementById("diffContent");

const statDetections = document.getElementById("statDetections");
const statResolved = document.getElementById("statResolved");
const statDeepen = document.getElementById("statDeepen");
const statWfo = document.getElementById("statWfo");
const nodeTree = document.getElementById("nodeTree");

// Tab Switching
document.querySelectorAll(".tab-btn").forEach((btn) => {
  btn.addEventListener("click", () => {
    document.querySelectorAll(".tab-btn").forEach((b) => b.classList.remove("active"));
    document.querySelectorAll(".tab-content").forEach((c) => c.classList.remove("active"));

    btn.classList.add("active");
    const target = document.getElementById(btn.dataset.tab);
    if (target) target.classList.add("active");
  });
});

// Initialize
window.addEventListener("DOMContentLoaded", async () => {
  await loadScenarios();
  await createNewSession();

  // Enter to send, Shift+Enter for newline
  messageInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      chatForm.dispatchEvent(new Event("submit"));
    }
  });

  scenarioSelect.addEventListener("change", (e) => {
    const val = e.target.value;
    if (val) {
      messageInput.value = val;
      messageInput.focus();
    }
  });

  newSessionBtn.addEventListener("click", () => {
    createNewSession();
  });

  chatForm.addEventListener("submit", handleSendMessage);
});

async function loadScenarios() {
  try {
    const res = await fetch("/api/demo-scenarios");
    if (!res.ok) return;
    const scenarios = await res.json();
    scenarios.forEach((s) => {
      const opt = document.createElement("option");
      opt.value = s.initial_prompt;
      opt.textContent = `${s.title}`;
      scenarioSelect.appendChild(opt);
    });
  } catch (err) {
    console.error("Failed to load scenarios:", err);
  }
}

async function createNewSession() {
  try {
    const res = await fetch("/api/session/new", { method: "POST" });
    const data = await res.json();
    currentSessionId = data.session_id;

    // Reset UI
    chatHistory.innerHTML = `
      <div class="message-card agent-card intro-card">
        <div class="message-header">
          <span class="sender-tag">Thinking Partner</span>
          <span class="badge badge-subtle">Method: Socratic</span>
        </div>
        <div class="message-body">
          <p><strong>Session initialized (<code>${currentSessionId}</code>).</strong> I do not give generic advice or canned answers. We deconstruct the assumptions and distortions in your problem statement together.</p>
          <p class="bedrock-hint"><em>"Problems stack — each one rests on an assumption beneath it. Let's descend together to the load-bearing one."</em></p>
          <p>Type your problem statement below or choose a scenario from the dropdown above to begin.</p>
        </div>
      </div>
    `;
    updatePhaseBadge("S0_IDLE");
    depthGaugeFill.style.width = "0%";
    adrContent.innerHTML = `
      <div class="empty-state">
        <p>No Problem Architecture Record generated yet.</p>
        <p class="sub">Send your first message to initialize the live ADR canvas.</p>
      </div>
    `;
    versionBadge.textContent = "v0";
    nodeCount.textContent = "0";
    diffContent.textContent = "// Session started. Awaiting first turn...";
    statDetections.textContent = "0";
    statResolved.textContent = "0";
    statDeepen.textContent = "0";
    statWfo.textContent = "0/5";
    nodeTree.innerHTML = "";
  } catch (err) {
    console.error("Failed to create new session:", err);
  }
}

async function handleSendMessage(e) {
  e.preventDefault();
  const text = messageInput.value.trim();
  if (!text) return;

  // Append user card
  appendUserMessage(text);
  messageInput.value = "";
  messageInput.disabled = true;
  sendBtn.disabled = true;

  try {
    const res = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        session_id: currentSessionId,
        message: text,
      }),
    });

    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();

    // Render agent response
    appendAgentMessage(data.response, data.graph);

    // Update Right Pane (ADR, Graph, Diff)
    updateArtifactView(data.latest_artifact);
    updateGraphView(data.graph);
    updatePhaseBadge(data.current_phase);
  } catch (err) {
    console.error("Chat error:", err);
    appendAgentMessage("An error occurred during processing. Please try again.", null);
  } finally {
    messageInput.disabled = false;
    sendBtn.disabled = false;
    messageInput.focus();
  }
}

function appendUserMessage(text) {
  const card = document.createElement("div");
  card.className = "message-card user-card";
  card.innerHTML = `
    <div class="message-header">
      <span class="sender-tag">You</span>
    </div>
    <div class="message-body">
      <p>${escapeHtml(text)}</p>
    </div>
  `;
  chatHistory.appendChild(card);
  chatHistory.scrollTop = chatHistory.scrollHeight;
}

function appendAgentMessage(text, graph) {
  const card = document.createElement("div");
  card.className = "message-card agent-card";

  let badgeHtml = '<span class="badge badge-subtle">Method: Socratic</span>';

  // If there's an active detection, show badge
  if (graph && graph.questions && graph.questions.length > 0) {
    const lastQ = graph.questions[graph.questions.length - 1];
    if (lastQ.deepen_cycle > 0) {
      badgeHtml = `<span class="badge badge-deepen">Deepening Cycle ${lastQ.deepen_cycle}/2 (${lastQ.technique || 'descend'})</span>`;
    } else if (lastQ.socratic_intent) {
      badgeHtml = `<span class="badge badge-pattern">${lastQ.socratic_intent}</span>`;
    }
  }

  // Convert paragraphs
  const paragraphs = text.split("\n\n").map((p) => `<p>${escapeHtml(p)}</p>`).join("");

  card.innerHTML = `
    <div class="message-header">
      <span class="sender-tag">Thinking Partner</span>
      ${badgeHtml}
    </div>
    <div class="message-body">
      ${paragraphs}
    </div>
  `;
  chatHistory.appendChild(card);
  chatHistory.scrollTop = chatHistory.scrollHeight;
}

function updateArtifactView(artifact) {
  if (!artifact) return;
  versionBadge.textContent = `v${artifact.version}`;

  // Simple Markdown to HTML renderer for ADR
  let html = artifact.content
    .replace(/^# (.*$)/gim, '<h1>$1</h1>')
    .replace(/^## (.*$)/gim, '<h2>$1</h2>')
    .replace(/^### (.*$)/gim, '<h3>$1</h3>')
    .replace(/^\- (.*$)/gim, '<li>$1</li>')
    .replace(/\*\*(.*?)\*\*/gim, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/gim, '<em>$1</em>')
    .replace(/`(.*?)`/gim, '<code>$1</code>');

  html = html.replace(/(<li>.*<\/li>)/gims, '<ul>$1</ul>');
  adrContent.innerHTML = html;

  // Update diff tab
  if (artifact.diff) {
    diffContent.textContent = artifact.diff;
  }
}

function updateGraphView(graph) {
  if (!graph) return;
  const dets = graph.detections || [];
  const resolved = dets.filter((d) => d.resolved);
  const totalNodes = (graph.utterances?.length || 0) + dets.length + (graph.questions?.length || 0) + (graph.answers?.length || 0);

  nodeCount.textContent = totalNodes;
  statDetections.textContent = dets.length;
  statResolved.textContent = resolved.length;

  const totalDeepen = dets.reduce((sum, d) => sum + (d.deepen_count || 0), 0);
  statDeepen.textContent = totalDeepen;

  const wfoKeys = Object.keys(graph.outcome_predicates || {});
  const wfoDrafted = Object.values(graph.outcome_predicates || {}).filter((w) => w.status !== "missing").length;
  statWfo.textContent = `${wfoDrafted}/5`;

  // Update Bedrock Gauge
  let progressPct = 0;
  if (graph.current_phase === "S1_INGEST") progressPct = 20;
  else if (graph.current_phase === "S2_CLARIFY") progressPct = 25 + (resolved.length * 15);
  else if (graph.current_phase === "S3_OUTCOME") progressPct = 70;
  else if (graph.current_phase === "S4_ANGLE") progressPct = 85;
  else if (graph.current_phase === "S5_ECOLOGY") progressPct = 95;
  else if (graph.current_phase === "S6_DONE") progressPct = 100;
  depthGaugeFill.style.width = `${Math.min(progressPct, 100)}%`;

  // Render node tree cards
  nodeTree.innerHTML = "";
  dets.forEach((d) => {
    const card = document.createElement("div");
    card.className = `node-card ${d.resolved ? "resolved" : "pending"}`;
    card.innerHTML = `
      <div style="display:flex; justify-content:space-between; margin-bottom:4px;">
        <strong style="color:var(--text-primary); font-family:var(--font-mono); font-size:12px;">${d.pattern}</strong>
        <span style="font-size:11px; color:${d.resolved ? "var(--accent-emerald)" : "var(--accent-amber)"}; font-weight:600;">
          ${d.resolved ? "RESOLVED" : `IN PROGRESS (Cycle ${d.deepen_count}/2)`}
        </span>
      </div>
      <div style="font-size:12px; color:var(--text-secondary); margin-bottom:4px;">Surface: <em>"${escapeHtml(d.surface)}"</em></div>
      <div style="font-size:11px; color:var(--text-muted);">Layer: <code>${d.layer}</code> | Confidence: ${(d.confidence * 100).toFixed(0)}%</div>
    `;
    nodeTree.appendChild(card);
  });
}

function updatePhaseBadge(phase) {
  currentPhaseBadge.textContent = phase;
  if (phase === "S6_DONE") {
    currentPhaseBadge.style.color = "var(--accent-emerald)";
  } else if (phase === "S2_CLARIFY") {
    currentPhaseBadge.style.color = "var(--accent-indigo)";
  } else {
    currentPhaseBadge.style.color = "var(--accent-cyan)";
  }
}

function escapeHtml(str) {
  if (!str) return "";
  return str
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}
