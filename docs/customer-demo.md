# Customer Demonstration Script

## 5-minute demonstration

### Step 1 — Dashboard

Open:

```text
http://127.0.0.1:8000/dashboard
```

Click **Запустить демонстрационный benchmark**.

Explain that the screen demonstrates the target analytical workflow using synthetic data.

### Step 2 — Explain the bottleneck

Show the ranked business stages and explain that the production version will replace synthetic durations with measured telemetry.

### Step 3 — Explain real telemetry

Generate `telemetry.json` with Playwright against an authorized test environment and upload it using **Загрузить telemetry.json**.

The dashboard will show actual browser request metrics.

### Step 4 — Generate report

Click **Сформировать отчёт**.

The downloaded Markdown report contains the evidence needed for a technical performance conclusion.

## What the customer receives

- reproducible telemetry collection;
- measurable baseline;
- bottleneck evidence;
- P95/median statistics;
- optimization hypotheses;
- before/after benchmark methodology;
- technical report.

## Important wording

Do not promise a percentage of speed improvement before measurement. The synthetic demo percentage is illustrative only.
