from analyze_telemetry import analyze


def test_analyze_basic_metrics():
    data = {
        "navigation_duration_ms": 1000,
        "events": [
            {"url": "https://test/a", "duration_ms": 100, "resource_type": "xhr"},
            {"url": "https://test/b", "duration_ms": 300, "resource_type": "xhr"},
            {"url": "https://test/c", "duration_ms": 500, "resource_type": "document"},
        ],
    }

    result = analyze(data)

    assert result["request_count"] == 3
    assert result["overall"]["min_ms"] == 100
    assert result["overall"]["max_ms"] == 500
    assert result["overall"]["median_ms"] == 300
    assert result["overall"]["p95_ms"] >= 300
