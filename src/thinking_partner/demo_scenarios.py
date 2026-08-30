"""Automated terminal walkthrough of gold-standard demo scenarios."""

import time
import sys
from thinking_partner.agent.orchestrator import ThinkingPartnerOrchestrator
from thinking_partner.agent.models import ProblemGraph, StatePhase


def run_scenario(name: str, dialogue_turns: list):
    print(f"\n{'='*70}")
    print(f"  DEMO SCENARIO: {name}")
    print(f"{'='*70}\n")

    orchestrator = ThinkingPartnerOrchestrator()
    graph = ProblemGraph()

    for i, user_msg in enumerate(dialogue_turns, 1):
        print(f"\n[Turn {i}] USER ─────────")
        print(f"\"{user_msg}\"\n")

        resp, graph, art = orchestrator.process_turn(graph, user_msg)

        print(f"[Turn {i}] THINKING PARTNER (Phase: {graph.current_phase.value}) ─────────")
        print(resp)
        print(f"\n>>> [Live ADR Mutated] Version: v{art.version} | Detections Resolved: {len([d for d in graph.detections if d.resolved])}")
        print(f"{'-'*70}")

    print(f"\n✅ Scenario '{name}' Completed Successfully in Phase: {graph.current_phase.value}\n")


if __name__ == "__main__":
    leadership_dialogue = [
        "They don't think I'm leadership material because I'm not loud in executive meetings.",
        "that's the only thing",  # Shallow Closure 1 -> triggers Cycle 1 Observation Split
        "I don't know",          # Shallow Closure 2 -> triggers Cycle 2 Metacognitive Nudge
        "Alex told me directly after the review that the VP was looking for someone who commands the room.",  # Concrete fact
        "I want to lead the infrastructure migration project with clear authority.",
        "Yes, by defining the technical roadmap and scheduling the kickoff myself.",
        "The team approves the RFC with zero unaddressed blocks and the VP signs off on the sprint backlog.",
        "The observer would see that quiet precision delivers better architecture than loud posturing.",
        "The cost is 10 hours a week of stakeholder communication that I usually spend on deep code.",
    ]

    run_scenario("Leadership Validation (Variant B Double Deepening)", leadership_dialogue)
