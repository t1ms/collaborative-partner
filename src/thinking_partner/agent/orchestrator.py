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
import subprocess
from typing import Optional, Dict, Any, Tuple
from .models import ProblemGraph, StatePhase, QuestionNode, ArtifactVersion
from .classifier import MetaModelClassifier
from .state_machine import StateMachineEngine
from .overlays import get_domain_pack
from .socratic import sanitize_domain_output
from ..config import GEMINI_API_KEY, GEMINI_MODEL, USE_MOCK_LLM, GCP_PROJECT_ID, GCP_REGION, USE_VERTEX_AI
from ..tools.mutate_artifact import ArtifactMutationTool

try:
    from google import genai
    from google.genai import types
    import google.auth
    from google.auth.exceptions import DefaultCredentialsError
    from google.oauth2.credentials import Credentials
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
        self.client = None

        if self.use_real_llm:
            if self.use_vertex and GCP_PROJECT_ID:
                # 1. Try standard ADC (Cloud Run & production)
                try:
                    google.auth.default()
                    self.client = genai.Client(vertexai=True, project=GCP_PROJECT_ID, location=GCP_REGION)
                except DefaultCredentialsError:
                    # 2. Local dev fallback: use active gcloud CLI token
                    try:
                        tok = subprocess.check_output(['gcloud', 'auth', 'print-access-token'], stderr=subprocess.DEVNULL).decode('utf-8').strip()
                        if tok:
                            creds = Credentials(tok)
                            self.client = genai.Client(
                                vertexai=True,
                                project=GCP_PROJECT_ID,
                                location=GCP_REGION,
                                credentials=creds,
                                http_options={'headers': {'x-goog-user-project': GCP_PROJECT_ID}},
                            )
                    except Exception:
                        pass
            
            # 3. Fallback to API Key if Vertex AI failed or was not requested
            if not self.client and self.api_key:
                try:
                    self.client = genai.Client(api_key=self.api_key)
                except Exception:
                    self.client = None

            if not self.client:
                self.use_real_llm = False

    def process_turn(self, graph: ProblemGraph, user_input: str, source_type: Optional[str] = None) -> Tuple[str, ProblemGraph, Optional[ArtifactVersion]]:
        """
        Executes a complete agentic turn:
        1. Advances state machine (deterministic router + deepening loop + domain hysteresis)
        2. Optionally polishes tone via Gemini (preserving immutable triples & domain grounding)
        3. Mutates live Problem Architecture Decision Record (ADR)
        4. Returns (response_text, updated_graph, updated_artifact)
        """
        # Advance state machine
        new_phase, next_q, base_response = self.state_machine.advance(graph, user_input, source_type=source_type)

        # Enforce No-LaTeX invariant and domain forbidden word sanitization
        clean_response = sanitize_domain_output(clean_latex(base_response), graph.current_domain)

        # Polish tone with Gemini if available and configured
        final_response = clean_response
        if self.use_real_llm and next_q and self.client:
            try:
                pack = get_domain_pack(graph.current_domain)
                forbidden_str = ", ".join(pack.forbidden) if pack.forbidden else "none"
                blend_note = f" (blending context with {graph.blend_with})" if graph.blend_with else ""

                system_instruction = (
                    "You are an expert Socratic Thinking Partner collaborating with a peer. You do NOT give advice or lecture.\n"
                    f"Current Domain Context: {graph.current_domain.upper()}{blend_note} ({pack.title}).\n"
                    f"Domain Vocabulary Target: Use natural {pack.vocab_summary}.\n"
                    f"Strictly Forbidden Phrases for this domain: {forbidden_str}.\n"
                    "Your tone is natural, concise, and collaborative — like a sharp colleague at a whiteboard, never a rigid script or robotic therapist.\n"
                    "Conversational Rules (EMMI, CARE & Strategic Discourse):\n"
                    "1. Seamlessly integrate a brief reflection using the user's verbatim words, the orienting descent rationale, and the target Socratic question into EXACTLY 2 to 3 fluid sentences.\n"
                    "2. Strict Brevity Invariant: Maximum 3 sentences total. Never produce multi-paragraph essays, lectures, or preamble.\n"
                    "3. Adopt the 'You-Attitude' and oscillate Hayakawa's Ladder of Abstraction (tie the user's high-level goal directly to the concrete evidence/word at hand).\n"
                    "4. Avoid disjointed template blocks, robotic headers, or canned filler ('Thank you for sharing', 'That must be hard').\n"
                    "5. Ask exactly ONE crisp Socratic question at the end.\n"
                    "6. Strictly return clean markdown with NO LaTeX ($ or \\)."
                )
                prompt = (
                    f"User utterance: \"{user_input}\"\n"
                    f"Core Socratic Question: \"{next_q.text}\"\n"
                    f"Orienting Framing Rationale: \"{next_q.framing_string}\"\n\n"
                    f"Domain Guidance: You are in {graph.current_domain} context. Speak naturally using domain concepts ({pack.vocab_summary}). Do NOT use {forbidden_str}.\n"
                    "Synthesize a natural, fluid 2-to-3 sentence response (under 60 words total) that smoothly transitions from acknowledgment to orienting rationale to the Socratic question."
                )
                # Configure generation with sufficient token headroom for Gemini 3.7 Flash thinking
                gen_config_kwargs = {
                    "system_instruction": system_instruction,
                    "temperature": 0.35,
                    "max_output_tokens": 2048,
                }
                if hasattr(types, "ThinkingConfig"):
                    gen_config_kwargs["thinking_config"] = types.ThinkingConfig(thinking_budget=256)

                response = self.client.models.generate_content(
                    model=GEMINI_MODEL,
                    contents=prompt,
                    config=types.GenerateContentConfig(**gen_config_kwargs),
                )
                if response and response.text:
                    raw_text = clean_latex(response.text.strip())
                    final_response = sanitize_domain_output(raw_text, graph.current_domain)
            except Exception:
                # Fallback directly to deterministic clean response
                final_response = clean_response

        # Mutate live ADR artifact
        artifact = self.mutation_tool.mutate(graph)

        return final_response, graph, artifact
