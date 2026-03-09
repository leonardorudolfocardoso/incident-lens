# IncidentLens

AI-powered incident analysis system that helps engineers investigate production incidents by analyzing logs and alerts asynchronously.

## Motivation

Production incidents are a common challenge in modern distributed systems. When a service fails or performance degrades, engineers must quickly understand what happened in order to restore the system.

However, incident investigation typically involves manually reviewing large volumes of logs, alerts, and system signals. This process can take valuable time, especially during high-pressure situations where quick resolution is critical.

IncidentLens explores how backend systems and AI-powered analysis can assist engineers during this process. By automatically analyzing incident data and generating structured summaries, the system helps reduce investigation time and provides engineers with useful starting points for diagnosing issues.

## Key features

- Incident ingestion API
- Asynchronous incident analysis
- Log and alert processing
- AI-generated root cause summaries
- Structured incident reports

For details about the system design, see [Architecture](docs/architecture.md).

### Incident Processing Flow

1. A monitoring system or client sends an incident to the API.
2. The API stores the incident data in the database.
3. The API enqueues an analysis job.
4. A background worker retrieves the job from the queue.
5. The worker analyzes logs and alerts using the analysis engine.
6. The generated analysis is stored in the database.
7. Clients can retrieve the analysis through the API.