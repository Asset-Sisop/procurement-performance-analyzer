from fastapi.testclient import TestClient
from app import app


client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_demo():
    response = client.get("/api/demo")
    assert response.status_code == 200
    data = response.json()
    assert data["mode"] == "synthetic_demo"
    assert data["total_before"] > data["total_after"]
    assert len(data["bottlenecks"]) > 0


def test_custom_benchmark():
    payload = {
        "stages": [
            {"name": "A", "category": "network", "duration_ms": 1000, "blocking": True},
            {"name": "B", "category": "data", "duration_ms": 500, "blocking": False},
        ]
    }
    response = client.post("/api/analyze", json=payload)
    assert response.status_code == 200
    assert response.json()["total_ms"] == 1500


def test_telemetry_analysis():
    payload = {
        "events": [
            {"url": "https://test/a", "method": "GET", "resource_type": "xhr", "status": 200, "duration_ms": 100},
            {"url": "https://test/b", "method": "GET", "resource_type": "xhr", "status": 200, "duration_ms": 300},
        ],
        "navigation_duration_ms": 400,
    }
    response = client.post(
        "/api/analyze-telemetry",
        files={"file": ("telemetry.json", json_bytes(payload), "application/json")},
    )
    assert response.status_code == 200
    assert response.json()["analysis"]["request_count"] == 2


def json_bytes(value):
    import json
    return json.dumps(value).encode("utf-8")
