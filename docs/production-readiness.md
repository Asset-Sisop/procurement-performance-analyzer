# Production Readiness

The repository is a technical demonstration MVP, not a production procurement bot.

## Implemented

- FastAPI demonstration service;
- synthetic benchmark;
- Playwright telemetry collector;
- request/response timing;
- min/median/mean/P95/max statistics;
- business-stage correlation primitives;
- repeated benchmark aggregation;
- Markdown report generation;
- dashboard data preparation;
- automated tests.

## Required before production use

### Platform integration
Implement only through officially permitted APIs, documented interfaces or an authorized browser workflow.

### Scenario automation
Define deterministic test steps and explicit business-stage markers.

### Data protection
Sanitize telemetry and prohibit storage of:

- passwords;
- session tokens;
- EDS private keys;
- document contents unless explicitly required and authorized;
- unnecessary personal data.

### Reliability
Add:

- retry classification;
- timeout classification;
- failed-run detection;
- environment metadata;
- benchmark history;
- regression thresholds.

### Storage
Move benchmark history to PostgreSQL or another approved data store.

### Reporting
Add signed/exportable technical reports and evidence references.

## Acceptance criteria

A production pilot should be able to answer:

1. How long does each business stage take?
2. Which operations contribute most to total time?
3. What is the P95 latency?
4. Which operations are sequential?
5. Which operations may be parallelized without changing platform semantics?
6. What changed after optimization?
7. Is the measured improvement reproducible?
