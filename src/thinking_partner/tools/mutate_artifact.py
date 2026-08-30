import difflib
from typing import Optional
from ..agent.models import ProblemGraph, ArtifactVersion, OutcomePredicateKey, StatePhase
from ..agent.overlays import get_domain_pack


class ArtifactMutationTool:
    """Generates and mutates the live Problem Architecture Decision Record (ADR) or Journey/WFO Canvas."""

    def render_adr(self, graph: ProblemGraph) -> str:
        """Renders the current Problem Graph state into an Architectural Decision Record markdown document."""
        pack = get_domain_pack(graph.current_domain)
        unresolved = [d for d in graph.detections if not d.resolved]
        resolved = [d for d in graph.detections if d.resolved]

        pos_wfo = graph.outcome_predicates.get(OutcomePredicateKey.POSITIVE)
        self_wfo = graph.outcome_predicates.get(OutcomePredicateKey.SELF_INITIATED)
        sens_wfo = graph.outcome_predicates.get(OutcomePredicateKey.SENSORY)

        # Domain-tailored section names
        if graph.current_domain == "se":
            sec1_title = "1. Deconstructed Service Anomalies & Telemetry Assumptions"
            sec2_title = "2. Bedrock SLO & Well-Formed Outcome (WFO)"
            sec3_title = "3. Telemetry Perspectives & Bottleneck Reframes"
            sec4_title = "4. Operational Constraints & Failover Costs"
        elif graph.current_domain == "design":
            sec1_title = "1. Deconstructed Journey Friction & User Assumptions"
            sec2_title = "2. Bedrock User Experience & Well-Formed Outcome (WFO)"
            sec3_title = "3. User Journey Perspectives & Affordance Reframes"
            sec4_title = "4. Usability Constraints & Cognitive Trade-Offs"
        elif graph.current_domain == "leadership":
            sec1_title = "1. Deconstructed Stakeholder Distortions & Assumptions"
            sec2_title = "2. Bedrock Objective & Well-Formed Outcome (WFO)"
            sec3_title = "3. Multi-Stakeholder Perspectives & Incentive Reframes"
            sec4_title = "4. Organizational Ecology & Alignment Trade-Offs"
        else:
            sec1_title = "1. Deconstructed Cognitive Layers (Meta-Model Detections)"
            sec2_title = "2. Bedrock & Well-Formed Outcome (WFO)"
            sec3_title = "3. Alternative Perspectives & Reframes"
            sec4_title = "4. Ecological Constraints & Trade-Offs"

        blend_tag = f" | **Blend Context:** `{graph.blend_with}`" if graph.blend_with else ""
        lines = [
            f"# {pack.artifact_title}: Session `{graph.session_id}`",
            f"**Domain Lens:** `{graph.current_domain.upper()}`{blend_tag} | **Current State:** `{graph.current_phase.value}` | **Layers Peeled:** {len(resolved)} | **Pending:** {len(unresolved)}",
            "",
            f"## {sec1_title}",
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
            f"## {sec2_title}",
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
            f"## {sec3_title}",
        ])

        if not graph.perspectives:
            lines.append("*Exploration triggers at Phase S4_ANGLE.*")
        else:
            for p in graph.perspectives:
                lines.append(f"- **{p.title} ({p.position}):** {p.content}")

        lines.extend([
            "",
            f"## {sec4_title}",
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
        pack = get_domain_pack(graph.current_domain)
        new_content = self.render_adr(graph)
        new_version_num = len(graph.artifacts) + 1

        prev_content = graph.artifacts[-1].content if graph.artifacts else ""
        diff_lines = list(
            difflib.unified_diff(
                prev_content.splitlines(keepends=True),
                new_content.splitlines(keepends=True),
                fromfile=f"Artifact_v{new_version_num - 1}.md" if new_version_num > 1 else "empty",
                tofile=f"Artifact_v{new_version_num}.md",
                n=2,
            )
        )
        diff_text = "".join(diff_lines) if diff_lines else f"+ Initialized {pack.artifact_title}"

        artifact = ArtifactVersion(
            version=new_version_num,
            title=f"{pack.artifact_title} (v{new_version_num})",
            content=new_content,
            diff=diff_text,
            domain=graph.current_domain,
            trigger_node_id=graph.active_detection_id,
        )
        graph.artifacts.append(artifact)
        return artifact
