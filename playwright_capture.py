"""Minimal Playwright telemetry runner.

Use only against an authorized test environment/account and permitted workflow.
Example:
    python playwright_capture.py https://example.test
"""
import asyncio
import json
import sys
import time
from telemetry import TelemetryCollector, RequestEvent


async def capture(url: str, output="telemetry.json"):
    from playwright.async_api import async_playwright

    collector = TelemetryCollector()
    pending = {}

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        async def on_request(request):
            pending[id(request)] = (
                time.perf_counter(),
                request.method,
                request.resource_type,
            )

        async def on_response(response):
            key = id(response.request)
            started = pending.pop(key, None)
            if not started:
                return

            start, method, resource_type = started
            end = time.perf_counter()
            size = None
            try:
                size = int(response.headers.get("content-length", "0")) or None
            except ValueError:
                pass

            collector.add(RequestEvent(
                url=response.url,
                method=method,
                resource_type=resource_type,
                status=response.status,
                start_ms=start * 1000,
                end_ms=end * 1000,
                duration_ms=(end - start) * 1000,
                response_size=size,
            ))

        page.on("request", on_request)
        page.on("response", on_response)

        started = time.perf_counter()
        await page.goto(url, wait_until="domcontentloaded")
        load_ms = (time.perf_counter() - started) * 1000

        # Allow late requests to complete.
        await page.wait_for_timeout(1500)
        collector.save(output)

        await browser.close()

    result = collector.export()
    result["navigation_duration_ms"] = round(load_ms, 2)
    with open(output, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(json.dumps({
        "output": output,
        "navigation_duration_ms": round(load_ms, 2),
        "requests": len(result["events"]),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit("Usage: python playwright_capture.py https://example.test")
    asyncio.run(capture(sys.argv[1]))
