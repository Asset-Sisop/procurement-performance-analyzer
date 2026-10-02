"""Dashboard data preparation for the Procurement Performance Analyzer."""
from collections import defaultdict


def build_dashboard(events, markers=None):
    markers = markers or []
    total = sum(float(e.get("duration_ms", 0)) for e in events)

    waterfall = []
    for e in sorted(events, key=lambda x: x.get("start_ms", 0)):
        start = float(e.get("start_ms", 0))
        duration = float(e.get("duration_ms", 0))
        waterfall.append({
            "url": e.get("url", ""),
            "method": e.get("method", ""),
            "status": e.get("status"),
            "resource_type": e.get("resource_type", "unknown"),
            "start_ms": round(start, 2),
            "duration_ms": round(duration, 2),
            "end_ms": round(start + duration, 2),
            "share_pct": round(duration / total * 100, 2) if total else 0,
        })

    stages = []
    for marker in markers:
        related = [
            e for e in events
            if e.get("start_ms", 0) <= marker["end_ms"]
            and e.get("end_ms", e.get("start_ms", 0)) >= marker["start_ms"]
        ]
        stages.append({
            "name": marker["name"],
            "start_ms": marker["start_ms"],
            "end_ms": marker["end_ms"],
            "duration_ms": round(marker["end_ms"] - marker["start_ms"], 2),
            "request_count": len(related),
        })

    return {
        "total_request_time_ms": round(total, 2),
        "request_count": len(events),
        "waterfall": waterfall,
        "stages": stages,
        "slowest": sorted(
            waterfall, key=lambda x: x["duration_ms"], reverse=True
        )[:10],
    }
