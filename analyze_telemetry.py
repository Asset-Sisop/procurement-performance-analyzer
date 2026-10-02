"""Analyze telemetry.json and produce a performance report."""
import json
import statistics
import sys
from collections import defaultdict


def percentile(values, p):
    if not values:
        return 0
    values = sorted(values)
    k = (len(values) - 1) * p
    f = int(k)
    c = min(f + 1, len(values) - 1)
    if f == c:
        return values[f]
    return values[f] + (values[c] - values[f]) * (k - f)


def analyze(data):
    events = data.get("events", [])
    by_type = defaultdict(list)
    for event in events:
        by_type[event.get("resource_type", "unknown")].append(event["duration_ms"])

    durations = [e["duration_ms"] for e in events]
    slowest = sorted(events, key=lambda e: e["duration_ms"], reverse=True)[:10]

    report = {
        "request_count": len(events),
        "navigation_duration_ms": data.get("navigation_duration_ms"),
        "overall": {
            "min_ms": min(durations) if durations else 0,
            "median_ms": statistics.median(durations) if durations else 0,
            "mean_ms": statistics.mean(durations) if durations else 0,
            "p95_ms": percentile(durations, 0.95),
            "max_ms": max(durations) if durations else 0,
        },
        "by_resource_type": {},
        "slowest_requests": slowest,
    }

    for resource_type, values in sorted(by_type.items()):
        report["by_resource_type"][resource_type] = {
            "count": len(values),
            "mean_ms": round(statistics.mean(values), 2),
            "median_ms": round(statistics.median(values), 2),
            "p95_ms": round(percentile(values, 0.95), 2),
            "max_ms": round(max(values), 2),
        }

    return report


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "telemetry.json"
    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    report = analyze(data)
    print(json.dumps(report, ensure_ascii=False, indent=2))

    with open("telemetry_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
