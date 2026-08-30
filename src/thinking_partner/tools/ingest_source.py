"""Tool for ingesting unstructured source context (transcripts, code context, markdown notes)."""

from typing import Dict, Any
from ..agent.models import ProblemGraph, UtteranceNode, GraphEdge


class SourceIngestionTool:
    """Ingests unstructured documents, Slack threads, or GitHub context into the Problem Graph."""

    def ingest_text_source(self, graph: ProblemGraph, source_name: str, raw_text: str) -> UtteranceNode:
        """Packs unstructured input into a grounded source node for Socratic deconstruction."""
        clean_text = raw_text.strip()
        formatted_utterance = f"[{source_name}] {clean_text}"

        node = UtteranceNode(text=formatted_utterance, speaker="user")
        graph.utterances.append(node)
        return node
