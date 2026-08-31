# Engineering & SRE Overlay Pack (se.md)

## Domain Metadata
- **Domain:** se
- **Title:** Software Engineering & Site Reliability Engineering
- **Artifact Title:** Problem Architecture Decision Record (ADR)

## Trigger Keywords
p95, p99, latency, replica, replicas, pagerduty, grafana, checkout api, queue, queues, 3x load, load test, throughput, rps, database, postgres, redis, kafka, deadlock, timeout, retry, failover, bottleneck, telemetry, trace, traces, span, oom, memory leak, cpu spike, deploy, incident, sla, slo, rfc, microservice, cluster, kubernetes, k8s, code, vibe code, script, app, software, scanner, driver, hardware, tooling, build-vs-buy, automation, batch, open source, library, cli, sdk, integration, ocr, api

## Framing Angles
- **Primary Observer (3rd Position):** SRE / telemetry observer with only metrics, traces, and black-box logs.
- **Counterparty (2nd Position):** Downstream service caller or upstream dependencies with hard timeout contracts.
- **Evidence Sources:** p95 dashboard panel, distributed trace waterfall, load test run, queue depth graph.
- **Orientation Rationale:** Let's look at this purely from the service telemetry and queue dynamics.

## S4 Perspectives
- **1st Position (Direct Owner):** Service on-call / owner managing resource limits, capacity, and SLO budgets.
- **2nd Position (Counterparty):** Upstream client service expecting strict contract SLAs without latency degradation.
- **3rd Position (Objective Data):** Distributed telemetry black box — measuring only exact timestamps, queue depth, and error codes.
- **Reframe:** Systemic Bottleneck Reframe — treating latency not as bad code, but as unbuffered I/O or mismatched concurrency models.

## Depth Policy
- **Max Deepen Cycles:** 1 (shallow by design for observable infrastructure/code problems)
- **Ecology Caps:** 1 (single operational failover/trade-off check)

## Forbidden for Domain
psychological distance, filtering out, metacognitive label, emotional reaction, inner feeling, emotional charge, therapeutic
