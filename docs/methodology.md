# Methodology

## 1. Baseline

Run the same authorized submission scenario repeatedly and record the duration of each operation. Report at least:

- minimum;
- average;
- median;
- P95;
- maximum.

A single run is insufficient for a reliable performance conclusion.

## 2. Instrumentation

Measure the observable parts of the workflow.

### Browser / API
- DNS resolution;
- TCP connection;
- TLS handshake;
- request and response time;
- payload size;
- retries and timeouts;
- repeated or redundant requests;
- request sequence.

### Network
- RTT;
- packet loss;
- route characteristics;
- upload/download throughput;
- variability between runs.

### Data processing
- document preparation;
- serialization/deserialization;
- validation;
- payload construction;
- upload preparation.

### EDS / cryptography
- preparation of data to be signed;
- hand-off to the cryptographic component;
- cryptographic operation;
- return of the result;
- transfer of signed data to the platform.

### Server-side processing
Where the platform exposes suitable observable timestamps, distinguish client-side waiting from server-side processing.

## 3. Bottleneck analysis

For each stage calculate its absolute duration and share of total time. Then classify it as:

- blocking;
- potentially parallelizable;
- network-bound;
- data-bound;
- browser/client-bound;
- cryptography-bound;
- server-bound.

## 4. Optimization hypotheses

Potential optimization classes include:

1. **Low risk:** client-side preparation, caching of permissible reference data, payload preparation, connection reuse, local workflow simplification.
2. **Medium:** reducing unnecessary sequential dependencies and automating repetitive authorized operations.
3. **Integration:** use of official APIs or documented integration interfaces where the platform provides them.

Every optimization must be validated against the platform's functional, security and legal constraints.

## 5. Validation

Repeat the same benchmark after each change. Compare distributions, not only one best-case result.

A valid conclusion should state:

- measured baseline;
- identified bottleneck;
- intervention;
- measured post-change result;
- statistical variability;
- remaining constraints.
