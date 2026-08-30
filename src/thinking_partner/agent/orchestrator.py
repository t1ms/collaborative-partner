"""ADK / Thinking Partner Orchestrator Agent combining LLM generation with deterministic rules.

Scientific Lineage & Attribution:
- Working Alliance & Brevity Optimization: CARE (Li et al., 2026, arXiv:2602.20648) & EMMI (Galland et al., 2024, arXiv:2406.16478)
- Problem-Solving Therapy Grounding: PST+MI (Wang et al., 2025, arXiv:2506.11376)
- Gricean Pragmatics: H. P. Grice (1975), Maxim of Quantity
- Vertical Navigation: S. I. Hayakawa (1949), Ladder of Abstraction
- Orchestration Architecture: Wang, Lin, & Irani (Google Cloud ADK 2 Multi-Agent Workshop, 2026)
"""

import os
import re
from typing import Optional, Dict, Any, Tuple
from .models import ProblemGraph, StatePhase, QuestionNode, ArtifactVersion
from .classifier import MetaModelClassifier
from .state_machine import StateMachineEngine
from ..config import GEMINI_API_KEY, GEMINI_MODEL, USE_MOCK_LLM, GCP_PROJECT_ID, GCP_REGION, USE_VERTEX_AI
from ..tools.mutate_artifact import ArtifactMutationTool

try:
    from google import genai
    from google.genai import types
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False


def clean_latex(text: str) -> str:
    """Invariant: Strip any accidental LaTeX markup or commands."""
    text = re.sub(r"\$(.*?)\$", r"\1", text)
    text = text.replace(r"\rightarrow", "→")
    text = text.replace(r"\leftarrow", "←")
    text = re.sub(r"\\text\{([^}]+)\}", r"\1", text)
    text = re.sub(r"\\[a-zA-Z]+", "", text)
    return text


class ThinkingPartnerOrchestrator:
    """
    Main Orchestrator Agent for the Collaborative Thinking Partner.
    Combines deterministic state-machine routing with Gemini LLM empathic generation.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or GEMINI_API_KEY
        self.use_vertex = bool(USE_VERTEX_AI or (GCP_PROJECT_ID and not self.api_key))
        self.use_real_llm = bool((self.api_key or self.use_vertex) and GENAI_AVAILABLE and not USE_MOCK_LLM)
        self.classifier = MetaModelClassifier(use_gemini=self.use_real_llm, api_key=self.api_key)
        self.state_machine = StateMachineEngine(self.classifier)
        self.mutation_tool = ArtifactMutationTool()

        if self.use_real_llm:
            try:
                if self.use_vertex and GCP_PROJECT_ID:
                    self.client = genai.Client(vertexai=True, project=GCP_PROJECT_ID, location=GCP_REGION)
                else:
                    self.client = genai.Client(api_key=self.api_key)
            except Exception:
                self.client = None
                self.use_real_llm = False
        else:
            self.client = None

    def process_turn(self, graph: ProblemGraph, user_input: str) -> Tuple[str, ProblemGraph, Optional[ArtifactVersion]]:
        """
        Executes a complete agentic turn:
        1. Advances state machine (deterministic router + deepening loop)
        2. Optionally polishes tone via Gemini (preserving immutable triples)
        3. Mutates live Problem Architecture Decision Record (ADR)
        4. Returns (response_text, updated_graph, updated_artifact)
        """
        # Advance state machine
        new_phase, next_q, base_response = self.state_machine.advance(graph, user_input)

        # Enforce No-LaTeX invariant
        clean_response = clean_latex(base_response)

        # Polish tone with Gemini if available and configured
        final_response = clean_response
        if self.use_real_llm and next_q and self.client:
            try:
                system_instruction = (
                    "You are an expert Socratic Thinking Partner collaborating with a peer. You do NOT give advice or lecture.\n"
                    "Your tone is natural, concise, and collaborative — like a sharp colleague at a whiteboard, never a rigid script or robotic therapist.\n"
                    "Conversational Rules (EMMI, CARE & Strategic Discourse):\n"
                    "1. Seamlessly integrate a brief reflection using the user's verbatim words, the orienting descent rationale, and the target Socratic question into 2-3 fluid sentences.\n"
                    "2. Adopt the 'You-Attitude' and oscillate Hayakawa's Ladder of Abstraction (tie the user's high-level goal directly to the concrete evidence/word at hand).\n"
                    "3. Avoid disjointed template blocks, robotic headers, or canned filler ('Thank you for sharing', 'That must be hard').\n"
                    "4. Ask exactly ONE crisp Socratic question at the end.\n"
                    "5. Strictly return clean markdown with NO LaTeX ($ or \\)."
                )
                prompt = (
                    f"User utterance: \"{user_input}\"\n"
                    f"Core Socratic Question: \"{next_q.text}\"\n"
                    f"Orienting Framing Rationale: \"{next_q.framing_string}\"\n\n"
                    "Synthesize a natural, fluid 2-to-3 sentence response that smoothly transitions from acknowledgment to orienting rationale to the Socratic question."
                )
                response = self.client.models.generate_content(
                    model=GEMINI_MODEL,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=system_instruction,
                        temperature=0.35,
                        max_output_tokens=160,
                    ),
                )
                if response and response.text:
                    final_response = clean_latex(response.text.strip())
            except Exception:
                # Fallback directly to deterministic clean response
                final_response = clean_response

        # Mutate live ADR artifact
        artifact = self.mutation_tool.mutate(graph)

        return final_response, graph, artifact
