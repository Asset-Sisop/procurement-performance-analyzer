from dashboard import build_dashboard


def test_dashboard_orders_events_by_start():
    events = [
        {"url": "b", "start_ms": 200, "duration_ms": 50},
        {"url": "a", "start_ms": 0, "duration_ms": 100},
    ]

    result = build_dashboard(events)

    assert result["request_count"] == 2
    assert result["waterfall"][0]["url"] == "a"
    assert result["waterfall"][1]["url"] == "b"
