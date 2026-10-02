"""Repeated benchmark aggregation."""
import json
import statistics
import sys
from pathlib import Path


def percentile(values, p):
    if not values:
        return 0
    values = sorted(values)
    index = (len(values) - 1) * p
    low = int(index)
    high = min(low + 1, len(values) - 1)
    if low == high:
        return values[low]
    return values[low] + (values[high] - values[low]) * (index - low)


def aggregate(paths):
    runs = []
    for path in paths:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        duration = data.get("navigation_duration_ms")
        if duration is not None:
            runs.append(float(duration))

    return {
        "runs": len(runs),
        "min_ms": round(min(runs), 2) if runs else 0,
        "median_ms": round(statistics.median(runs), 2) if runs else 0,
        "mean_ms": round(statistics.mean(runs), 2) if runs else 0,
        "p95_ms": round(percentile(runs, 0.95), 2) if runs else 0,
        "max_ms": round(max(runs), 2) if runs else 0,
        "values_ms": [round(x, 2) for x in runs],
    }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit("Usage: python benchmark.py telemetry*.json")
    print(json.dumps(aggregate(sys.argv[1:]), ensure_ascii=False, indent=2))
