# MVP 0.2 Roadmap

## Completed

- synthetic benchmark;
- bottleneck model;
- FastAPI demo;
- Playwright browser telemetry;
- request/response timing capture;
- telemetry JSON export;
- automatic min/median/mean/P95/max analysis.

## Next implementation stages

### 1. Scenario instrumentation
Create explicit markers for business operations:

```text
AUTH
PARTICIPANT_DATA
REFERENCE_DATA
DOCUMENT_VALIDATION
DOCUMENT_UPLOAD
EDS_PREPARATION
EDS_OPERATION
APPLICATION_SUBMISSION
SERVER_PROCESSING
CONFIRMATION
```

### 2. Repeated benchmark
Run the same authorized scenario multiple times and aggregate:

- median;
- P95;
- variability;
- failed requests;
- retries;
- timeout frequency.

### 3. Dependency graph
Build a request dependency graph to identify:

- unnecessary sequential calls;
- duplicate requests;
- calls that can be cached;
- calls that may be parallelized if platform behavior permits.

### 4. Customer-facing report
Generate a technical conclusion containing:

1. baseline;
2. bottlenecks;
3. evidence;
4. optimization hypotheses;
5. constraints;
6. measured post-optimization result;
7. recommended architecture.

### 5. Production-grade storage

Move telemetry from JSON to PostgreSQL and expose a dashboard for benchmark comparison.

## Principle

Do not claim an optimization before measuring it. Every proposed improvement must be validated against an authorized and reproducible scenario.
