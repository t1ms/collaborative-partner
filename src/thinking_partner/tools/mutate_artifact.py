"""Tool for live mutation and diff generation of the Problem Architecture Decision Record (ADR)."""

import difflib
from typing import Optional
from ..agent.models import ProblemGraph, ArtifactVersion, OutcomePredicateKey, StatePhase


class ArtifactMutationTool:
    """Generates and mutates the live Problem Architecture Decision Record (ADR)."""

    def render_adr(self, graph: ProblemGraph) -> str:
        """Renders the current Problem Graph state into an Architectural Decision Record markdown document."""
        unresolved = [d for d in graph.detections if not d.resolved]
        resolved = [d for d in graph.detections if d.resolved]

        pos_wfo = graph.outcome_predicates.get(OutcomePredicateKey.POSITIVE)
        self_wfo = graph.outcome_predicates.get(OutcomePredicateKey.SELF_INITIATED)
        sens_wfo = graph.outcome_predicates.get(OutcomePredicateKey.SENSORY)

        lines = [
            f"# Problem Architecture Record: Session `{graph.session_id}`",
            f"**Current State:** `{graph.current_phase.value}` | **Layers Peeled:** {len(resolved)} | **Pending:** {len(unresolved)}",
            "",
            "## 1. Deconstructed Cognitive Layers (Meta-Model Detections)",
        ]

        if not graph.detections:
            lines.append("*Awaiting initial problem statement ingestion...*")
        else:
            for det in graph.detections:
                status_icon = "✅ RESOLVED" if det.resolved else "⏳ ACTIVE PROBE"
                deepen_tag = f" (Deepening Cycle {det.deepen_count}/2)" if det.deepen_count > 0 else ""
                lines.append(
                    f"- **[{status_icon}] `{det.pattern.value}`** ({det.layer.value}){deepen_tag}"
                )
                lines.append(f"  - *Surface Phrase:* \"{det.surface}\"")
                lines.append(f"  - *Confidence:* {det.confidence:.2f}")

        lines.extend([
            "",
            "## 2. Bedrock & Well-Formed Outcome (WFO)",
        ])

        if pos_wfo and pos_wfo.status != "missing":
            lines.append(f"- **Target Outcome (Positive):** {pos_wfo.statement}")
        else:
            lines.append("- **Target Outcome (Positive):** *Pending bedrock descent...*")

        if self_wfo and self_wfo.status != "missing":
            lines.append(f"- **Agency & Locus of Control:** {self_wfo.statement}")
        else:
            lines.append("- **Agency & Locus of Control:** *Unverified*")

        if sens_wfo and sens_wfo.status != "missing":
            lines.append(f"- **Sensory Evidence Milestone:** {sens_wfo.statement}")
        else:
            lines.append("- **Sensory Evidence Milestone:** *Unverified*")

        lines.extend([
            "",
            "## 3. Alternative Perspectives & Reframes",
        ])

        if not graph.perspectives:
            lines.append("*Exploration triggers at Phase S4_ANGLE.*")
        else:
            for p in graph.perspectives:
                lines.append(f"- **{p.title} ({p.position}):** {p.content}")

        lines.extend([
            "",
            "## 4. Ecological Constraints & Trade-Offs",
        ])

        if not graph.constraints:
            lines.append("*Stress-tested at Phase S5_ECOLOGY.*")
        else:
            for c in graph.constraints:
                lines.append(f"- **[{c.severity.upper()}] Constraint:** {c.text}")
                if c.positive_intent:
                    lines.append(f"  - *Positive Intent:* {c.positive_intent}")

        return "\n".join(lines)

    def mutate(self, graph: ProblemGraph) -> ArtifactVersion:
        """Renders new ADR markdown, computes unified diff from prior version, and registers artifact."""
        new_content = self.render_adr(graph)
        new_version_num = len(graph.artifacts) + 1

        prev_content = graph.artifacts[-1].content if graph.artifacts else ""
        diff_lines = list(
            difflib.unified_diff(
                prev_content.splitlines(keepends=True),
                new_content.splitlines(keepends=True),
                fromfile=f"ADR_v{new_version_num - 1}.md" if new_version_num > 1 else "empty",
                tofile=f"ADR_v{new_version_num}.md",
                n=2,
            )
        )
        diff_text = "".join(diff_lines) if diff_lines else "+ Initialized ADR Canvas"

        artifact = ArtifactVersion(
            version=new_version_num,
            title=f"Problem ADR (v{new_version_num})",
            content=new_content,
            diff=diff_text,
            trigger_node_id=graph.active_detection_id,
        )
        graph.artifacts.append(artifact)
        return artifact
