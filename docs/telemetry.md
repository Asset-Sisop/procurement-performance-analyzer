# Browser Telemetry

The MVP can now capture basic browser network telemetry for an **authorized** test scenario.

## What is captured

For each observed response:

- URL;
- HTTP method;
- resource type;
- HTTP status;
- request start/end timestamps;
- duration;
- response size when exposed by the server.

The collector also records total navigation duration.

## Run

Install the telemetry dependency:

```bash
pip install -r requirements-telemetry.txt
playwright install chromium
```

Run against an authorized test URL:

```bash
python playwright_capture.py https://example.test
```

The result is written to:

```text
telemetry.json
```

## Important boundary

This component is an observability tool, not a bot for bypassing procurement-platform controls. It must be used only with an authorized account and permitted workflow.

The next step is to correlate browser telemetry with explicit business stages such as authorization, document validation, EDS operation and application submission, then calculate baseline/P95 metrics and bottleneck contribution.
