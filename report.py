"""Generate a concise Markdown technical performance report."""
import json
import sys
from pathlib import Path


def generate(telemetry_path="telemetry_report.json", output="performance_report.md"):
    report = json.loads(Path(telemetry_path).read_text(encoding="utf-8"))

    lines = [
        "# Procurement Performance — Technical Performance Report",
        "",
        "> Automatically generated from browser telemetry. Validate all findings on an authorized test scenario.",
        "",
        "## Executive metrics",
        "",
        f"- Requests: **{report['request_count']}**",
        f"- Navigation duration: **{report.get('navigation_duration_ms', 0):.0f} ms**",
        f"- Median request latency: **{report['overall']['median_ms']:.0f} ms**",
        f"- P95 request latency: **{report['overall']['p95_ms']:.0f} ms**",
        f"- Maximum request latency: **{report['overall']['max_ms']:.0f} ms**",
        "",
        "## Resource types",
        "",
        "| Type | Count | Median | P95 | Max |",
        "|---|---:|---:|---:|---:|",
    ]

    for kind, stats in report.get("by_resource_type", {}).items():
        lines.append(
            f"| {kind} | {stats['count']} | "
            f"{stats['median_ms']:.0f} ms | {stats['p95_ms']:.0f} ms | "
            f"{stats['max_ms']:.0f} ms |"
        )

    lines += [
        "",
        "## Slowest requests",
        "",
        "| Duration | Status | Method | Resource | URL |",
        "|---:|---:|---|---|---|",
    ]

    for event in report.get("slowest_requests", []):
        url = event.get("url", "").replace("|", "%7C")
        lines.append(
            f"| {event['duration_ms']:.0f} ms | {event.get('status','')} | "
            f"{event.get('method','')} | {event.get('resource_type','')} | {url} |"
        )

    Path(output).write_text("
".join(lines) + "
", encoding="utf-8")
    print(f"Report written to {output}")


if __name__ == "__main__":
    generate(sys.argv[1] if len(sys.argv) > 1 else "telemetry_report.json")
