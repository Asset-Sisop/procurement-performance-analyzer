# Scenario Analysis

## Goal

Move from raw HTTP timing to business-level performance analysis.

A procurement workflow can be represented as explicit stages:

1. Authorization
2. Participant data
3. Reference data
4. Document validation
5. Document upload
6. EDS preparation
7. EDS cryptographic operation
8. Application submission
9. Server-side processing
10. Confirmation

Each stage can have a start/end marker. The analyzer then correlates network events whose timestamps overlap the stage.

## Why this matters

A slow HTTP request is only evidence of a technical symptom. The business-stage correlation answers the more useful question:

> Which part of the application-submission process consumes the most time, and which technical requests contribute to it?

This enables a technical conclusion with traceable evidence.

## Benchmark protocol

For each scenario:

- execute the same workflow under the same test conditions;
- capture telemetry;
- repeat multiple times;
- calculate median and P95;
- compare baseline and optimized runs;
- document any environmental differences.

Do not compare a single fast run with a single slow run and call it an optimization result.

## Privacy

Telemetry should be sanitized before sharing. Avoid storing credentials, authentication tokens, EDS private material, personal data or document contents. Prefer metadata such as timing, status, resource type and payload size.
