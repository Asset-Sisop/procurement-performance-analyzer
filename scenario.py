"""Business-stage correlation for authorized browser scenarios."""
from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class ScenarioMarker:
    name: str
    start_ms: float
    end_ms: float
    source: str = "manual"
    notes: Optional[str] = None

    @property
    def duration_ms(self):
        return max(0, self.end_ms - self.start_ms)

    def to_dict(self):
        d = asdict(self)
        d["duration_ms"] = round(self.duration_ms, 2)
        return d


def correlate_requests(events, markers):
    """Attach requests to business stages by timestamp overlap."""
    result = []
    for marker in markers:
        related = []
        for event in events:
            start = event.get("start_ms", 0)
            end = event.get("end_ms", start)
            if start <= marker.end_ms and end >= marker.start_ms:
                related.append(event)

        result.append({
            **marker.to_dict(),
            "request_count": len(related),
            "requests": related,
            "total_request_time_ms": round(
                sum(x.get("duration_ms", 0) for x in related), 2
            ),
        })
    return result
