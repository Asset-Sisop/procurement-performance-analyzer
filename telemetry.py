"""Browser telemetry collection helpers for authorized test scenarios.

This module records Playwright request/response timing and basic network metadata.
It does not bypass authentication, CAPTCHA, rate limits, or other platform controls.
"""
from dataclasses import dataclass, asdict
from typing import Optional
import json
import time


@dataclass
class RequestEvent:
    url: str
    method: str
    resource_type: str
    status: Optional[int]
    start_ms: float
    end_ms: float
    duration_ms: float
    response_size: Optional[int] = None

    def to_dict(self):
        return asdict(self)


class TelemetryCollector:
    def __init__(self):
        self.started = time.perf_counter()
        self.events = []

    def add(self, event: RequestEvent):
        self.events.append(event)

    def export(self):
        return {
            "captured_at": time.time(),
            "events": [e.to_dict() for e in self.events],
        }

    def save(self, path="telemetry.json"):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.export(), f, ensure_ascii=False, indent=2)
