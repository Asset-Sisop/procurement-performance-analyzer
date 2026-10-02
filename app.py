from __future__ import annotations

import json
import statistics
from pathlib import Path
from typing import Any

from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse
from pydantic import BaseModel, Field

app = FastAPI(
    title="Procurement Performance Analyzer",
    version="1.0.0",
    description="Performance audit and bottleneck analysis for authorized procurement workflows.",
)

BASE_DIR = Path(__file__).resolve().parent


class Stage(BaseModel):
    name: str
    category: str = "unknown"
    duration_ms: float = Field(ge=0)
    blocking: bool = False
    parallelizable: bool = False


class Benchmark(BaseModel):
    stages: list[Stage]


def percentile(values: list[float], p: float) -> float:
    if not values:
        return 0.0
    values = sorted(values)
    index = (len(values) - 1) * p
    low = int(index)
    high = min(low + 1, len(values) - 1)
    if low == high:
        return values[low]
    return values[low] + (values[high] - values[low]) * (index - low)


def stage_analysis(stages: list[Stage]) -> dict[str, Any]:
    total = sum(s.duration_ms for s in stages)
    rows = []
    for s in sorted(stages, key=lambda x: x.duration_ms, reverse=True):
        rows.append({
            "name": s.name,
            "category": s.category,
            "duration_ms": round(s.duration_ms, 2),
            "share_pct": round((s.duration_ms / total * 100) if total else 0, 2),
            "blocking": s.blocking,
            "parallelizable": s.parallelizable,
        })
    return {"total_ms": round(total, 2), "stages": rows}


def optimization_model(stages: list[Stage]) -> list[dict[str, Any]]:
    result = []
    for s in stages:
        before = s.duration_ms
        factor = 1.0
        hypothesis = "Без моделируемого изменения"
        if s.parallelizable:
            factor = 0.55
            hypothesis = "Гипотеза: допустимая параллелизация независимой операции"
        elif s.category == "data" and before > 1000:
            factor = 0.75
            hypothesis = "Гипотеза: предварительная подготовка и оптимизация payload"
        elif s.category == "network" and before > 1000:
            factor = 0.85
            hypothesis = "Гипотеза: оптимизация клиентской сетевой части"
        elif s.category == "browser" and before > 1000:
            factor = 0.70
            hypothesis = "Гипотеза: сокращение клиентских операций"
        after = before * factor
        result.append({
            "name": s.name,
            "before_ms": round(before, 2),
            "after_ms": round(after, 2),
            "saving_ms": round(before - after, 2),
            "hypothesis": hypothesis,
        })
    return result


def demo_stages() -> list[Stage]:
    return [
        Stage(name="Авторизация", category="browser", duration_ms=820, blocking=True),
        Stage(name="GET данных участника", category="backend", duration_ms=1450, blocking=True, parallelizable=True),
        Stage(name="Получение справочных данных", category="backend", duration_ms=1850, blocking=True, parallelizable=True),
        Stage(name="Валидация документов", category="data", duration_ms=2100, blocking=True, parallelizable=True),
        Stage(name="Загрузка документа №1", category="network", duration_ms=3200, blocking=True),
        Stage(name="Загрузка документа №2", category="network", duration_ms=2750, blocking=True),
        Stage(name="Подготовка данных для ЭЦП", category="data", duration_ms=1100, blocking=True),
        Stage(name="Криптографическая операция ЭЦП", category="eds", duration_ms=2900, blocking=True),
        Stage(name="Отправка заявки", category="network", duration_ms=2600, blocking=True),
        Stage(name="Server-side обработка", category="backend", duration_ms=3600, blocking=True),
        Stage(name="Получение подтверждения", category="network", duration_ms=1700, blocking=True),
    ]


def analyze_events(data: dict[str, Any]) -> dict[str, Any]:
    events = data.get("events", [])
    clean = []
    for event in events:
        try:
            duration = max(0.0, float(event.get("duration_ms", 0)))
        except (TypeError, ValueError):
            continue
        clean.append({
            "url": str(event.get("url", ""))[:2000],
            "method": str(event.get("method", ""))[:20],
            "resource_type": str(event.get("resource_type", "unknown"))[:40],
            "status": event.get("status"),
            "start_ms": float(event.get("start_ms", 0) or 0),
            "duration_ms": duration,
            "response_size": event.get("response_size"),
        })

    durations = [e["duration_ms"] for e in clean]
    by_type: dict[str, list[float]] = {}
    for event in clean:
        by_type.setdefault(event["resource_type"], []).append(event["duration_ms"])

    by_resource = {}
    for kind, values in by_type.items():
        by_resource[kind] = {
            "count": len(values),
            "median_ms": round(statistics.median(values), 2),
            "mean_ms": round(statistics.mean(values), 2),
            "p95_ms": round(percentile(values, 0.95), 2),
            "max_ms": round(max(values), 2),
        }

    waterfall = sorted(
        [{
            **event,
            "end_ms": round(event["start_ms"] + event["duration_ms"], 2),
        } for event in clean],
        key=lambda x: x["start_ms"],
    )

    return {
        "request_count": len(clean),
        "navigation_duration_ms": data.get("navigation_duration_ms"),
        "waterfall": waterfall,
        "overall": {
            "min_ms": round(min(durations), 2) if durations else 0,
            "median_ms": round(statistics.median(durations), 2) if durations else 0,
            "mean_ms": round(statistics.mean(durations), 2) if durations else 0,
            "p95_ms": round(percentile(durations, 0.95), 2) if durations else 0,
            "max_ms": round(max(durations), 2) if durations else 0,
        },
        "by_resource_type": by_resource,
        "slowest_requests": sorted(clean, key=lambda x: x["duration_ms"], reverse=True)[:10],
    }


def report_markdown(analysis: dict[str, Any], title="Procurement Performance Report") -> str:
    overall = analysis.get("overall", {})
    lines = [
        f"# {title}",
        "",
        "> Generated by Procurement Performance Analyzer.",
        "> Validate all findings on an authorized and reproducible test scenario.",
        "",
        "## Executive metrics",
        "",
        f"- Requests: **{analysis.get('request_count', 0)}**",
        f"- Navigation duration: **{analysis.get('navigation_duration_ms') or 0} ms**",
        f"- Median request latency: **{overall.get('median_ms', 0)} ms**",
        f"- P95 request latency: **{overall.get('p95_ms', 0)} ms**",
        f"- Maximum request latency: **{overall.get('max_ms', 0)} ms**",
        "",
        "## Resource types",
        "",
        "| Type | Count | Median | P95 | Max |",
        "|---|---:|---:|---:|---:|",
    ]
    for kind, stats in analysis.get("by_resource_type", {}).items():
        lines.append(
            f"| {kind} | {stats['count']} | {stats['median_ms']:.0f} ms | "
            f"{stats['p95_ms']:.0f} ms | {stats['max_ms']:.0f} ms |"
        )

    lines += [
        "",
        "## Slowest requests",
        "",
        "| Duration | Status | Method | Resource | URL |",
        "|---:|---:|---|---|---|",
    ]
    for event in analysis.get("slowest_requests", []):
        url = event.get("url", "").replace("|", "%7C")
        lines.append(
            f"| {event['duration_ms']:.0f} ms | {event.get('status', '')} | "
            f"{event.get('method', '')} | {event.get('resource_type', '')} | {url} |"
        )

    lines += [
        "",
        "## Security boundary",
        "",
        "Telemetry should be collected only from an authorized scenario. Do not store passwords, session tokens, EDS private keys or unnecessary personal/document data.",
        "",
    ]
    return "\n".join(lines)


@app.get("/", response_class=HTMLResponse)
def home():
    return HTMLResponse(DASHBOARD_HTML)


@app.get("/dashboard", response_class=HTMLResponse)
def dashboard():
    return HTMLResponse(DASHBOARD_HTML)


@app.get("/health")
def health():
    return {"status": "ok", "service": "procurement-performance-analyzer", "version": "1.0.0"}


@app.get("/api/demo")
def demo():
    stages = demo_stages()
    before = stage_analysis(stages)
    optimization = optimization_model(stages)
    after = sum(x["after_ms"] for x in optimization)
    saving = before["total_ms"] - after
    return {
        "mode": "synthetic_demo",
        "total_before": before["total_ms"],
        "total_after": round(after, 2),
        "saving_ms": round(saving, 2),
        "saving_pct": round((saving / before["total_ms"] * 100) if before["total_ms"] else 0, 2),
        "bottlenecks": before["stages"],
        "optimization": optimization,
        "notice": "Synthetic demonstration. Not a measurement of a production procurement platform.",
    }


@app.post("/api/analyze")
def analyze(benchmark: Benchmark):
    if not benchmark.stages:
        return JSONResponse({"error": "stages must not be empty"}, status_code=400)
    result = stage_analysis(benchmark.stages)
    optimization = optimization_model(benchmark.stages)
    after = sum(x["after_ms"] for x in optimization)
    saving = result["total_ms"] - after
    return {
        "mode": "custom_benchmark",
        **result,
        "model_total_after_ms": round(after, 2),
        "model_saving_pct": round((saving / result["total_ms"] * 100) if result["total_ms"] else 0, 2),
        "optimization": optimization,
        "notice": "Optimization figures are hypotheses and require validation.",
    }


@app.post("/api/analyze-telemetry")
async def analyze_telemetry(file: UploadFile = File(...)):
    if not file.filename or not file.filename.lower().endswith(".json"):
        return JSONResponse({"error": "Upload a JSON telemetry file."}, status_code=400)
    raw = await file.read()
    if len(raw) > 10 * 1024 * 1024:
        return JSONResponse({"error": "Telemetry file exceeds 10 MB."}, status_code=413)
    try:
        data = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return JSONResponse({"error": "Invalid UTF-8 JSON telemetry file."}, status_code=400)
    return {"mode": "real_telemetry", "analysis": analyze_events(data)}


@app.post("/api/report")
async def generate_report(file: UploadFile = File(...)):
    if not file.filename or not file.filename.lower().endswith(".json"):
        return PlainTextResponse("Upload a JSON telemetry file.", status_code=400)
    raw = await file.read()
    try:
        data = json.loads(raw.decode("utf-8"))
        analysis = analyze_events(data)
    except (UnicodeDecodeError, json.JSONDecodeError):
        return PlainTextResponse("Invalid telemetry JSON.", status_code=400)
    return PlainTextResponse(report_markdown(analysis), media_type="text/markdown")


DASHBOARD_HTML = r"""<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Procurement Performance Analyzer</title>
<style>
:root{--bg:#f5f7fa;--card:#fff;--text:#17202a;--muted:#667085;--line:#e5e7eb;--accent:#111827;--soft:#eef2ff}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--text);font-family:Inter,Segoe UI,Arial,sans-serif}
.wrap{max-width:1320px;margin:auto;padding:28px}.hero{display:flex;justify-content:space-between;gap:20px;align-items:end;margin-bottom:20px}
h1{font-size:30px;margin:0 0 6px}.muted{color:var(--muted)}.badge{display:inline-block;padding:4px 9px;border-radius:999px;background:var(--soft);font-size:12px}
.card{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:20px;margin:14px 0;box-shadow:0 2px 10px #00000008}
.grid{display:grid;grid-template-columns:repeat(4,1fr);gap:14px}.metric{margin:0}.metric b{font-size:28px;display:block;margin-top:7px}
.actions{display:flex;gap:10px;flex-wrap:wrap}button{border:0;border-radius:9px;padding:11px 16px;background:var(--accent);color:#fff;cursor:pointer}
button.secondary{background:#fff;color:var(--text);border:1px solid var(--line)}input[type=file]{max-width:320px}
table{width:100%;border-collapse:collapse;font-size:14px}th,td{padding:10px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}
.bar{height:15px;background:#edf0f3;border-radius:9px;overflow:hidden;min-width:120px}.fill{height:100%;background:#475467}
.notice{padding:13px 15px;background:#f8fafc;border-left:4px solid #475467;border-radius:7px}
.waterfall{overflow:auto;border:1px solid var(--line);border-radius:10px;padding:10px}.wfrow{height:31px;white-space:nowrap}.wflabel{display:inline-block;width:270px;overflow:hidden;text-overflow:ellipsis;vertical-align:middle}.track{display:inline-block;width:720px;height:18px;vertical-align:middle;background:#f1f3f5;position:relative}.block{position:absolute;height:18px;border-radius:4px;background:#475467}
.small{font-size:12px}.hidden{display:none}
@media(max-width:900px){.grid{grid-template-columns:1fr 1fr}.hero{display:block}.track{width:520px}.wflabel{width:200px}}
</style>
</head>
<body><div class="wrap">
<div class="hero"><div><h1>Procurement Performance Analyzer</h1><div class="muted">Инструментальный аудит процесса подачи заявки · v1.0</div></div><span class="badge">Customer-ready MVP</span></div>

<div class="card">
<div class="actions">
<button onclick="runDemo()">Запустить демонстрационный benchmark</button>
<label><input id="file" type="file" accept=".json"> Загрузить telemetry.json</label>
<button class="secondary" onclick="analyzeFile()">Анализ telemetry</button>
<button class="secondary" onclick="reportFile()">Сформировать отчёт</button>
</div>
<p id="status" class="muted small">Демонстрационный режим использует синтетические данные.</p>
</div>

<div id="out"></div>
</div>
<script>
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
function metric(a,b){return '<div class="card metric"><span class="muted">'+esc(a)+'</span><b>'+esc(b)+'</b></div>'}
function render(d,real=false){
 let html='<div class="grid">';
 if(real){
  const a=d.analysis; html+=metric('Requests',a.request_count);html+=metric('Navigation',((a.navigation_duration_ms||0)/1000).toFixed(2)+' s');html+=metric('Median request',a.overall.median_ms.toFixed(0)+' ms');html+=metric('P95 request',a.overall.p95_ms.toFixed(0)+' ms');html+='</div>';
  html+='<div class="card"><h2>HTTP waterfall</h2>'+waterfall(a.waterfall)+'</div>';
  html+='<div class="card"><h2>Slowest requests</h2>'+tableSlow(a.slowest_requests)+'</div>';
  html+='<div class="card"><h2>Resource types</h2><table><tr><th>Type</th><th>Count</th><th>Median</th><th>P95</th><th>Max</th></tr>';
  Object.entries(a.by_resource_type).forEach(([k,v])=>html+='<tr><td>'+esc(k)+'</td><td>'+v.count+'</td><td>'+v.median_ms+' ms</td><td>'+v.p95_ms+' ms</td><td>'+v.max_ms+' ms</td></tr>');
  html+='</table></div>';
  html+='<div class="card"><div class="notice">Это фактическая browser telemetry из загруженного JSON. Для production-вывода дополнительно требуется корреляция с бизнес-этапами заявки.</div></div>';
 } else {
  html+=metric('Baseline',(d.total_before/1000).toFixed(2)+' s');html+=metric('Model after optimization',(d.total_after/1000).toFixed(2)+' s');html+=metric('Model saving',d.saving_pct.toFixed(1)+'%');html+=metric('Top bottleneck',d.bottlenecks[0]?.name||'-');html+='</div>';
  html+='<div class="card"><h2>Business-stage bottlenecks</h2>'+tableStages(d.bottlenecks)+'</div>';
  html+='<div class="card"><h2>Optimization hypotheses</h2><table><tr><th>Operation</th><th>Before</th><th>Model</th><th>Saving</th><th>Hypothesis</th></tr>';
  d.optimization.forEach(x=>html+='<tr><td>'+esc(x.name)+'</td><td>'+x.before_ms.toFixed(0)+' ms</td><td>'+x.after_ms.toFixed(0)+' ms</td><td>'+x.saving_ms.toFixed(0)+' ms</td><td>'+esc(x.hypothesis)+'</td></tr>');html+='</table></div>';
  html+='<div class="card"><div class="notice">'+esc(d.notice)+'</div></div>';
 }
 document.getElementById('out').innerHTML=html;
}
function tableStages(rows){let h='<table><tr><th>Stage</th><th>Category</th><th>Duration</th><th>Share</th><th>Flags</th></tr>';rows.forEach(x=>h+='<tr><td>'+esc(x.name)+'</td><td><span class="badge">'+esc(x.category)+'</span></td><td>'+x.duration_ms.toFixed(0)+' ms</td><td>'+x.share_pct.toFixed(1)+'%<div class="bar"><div class="fill" style="width:'+Math.min(x.share_pct,100)+'%"></div></div></td><td>'+esc((x.blocking?'blocking ':'')+(x.parallelizable?'parallelization candidate':''))+'</td></tr>');return h+'</table>'}
function waterfall(rows){
 if(!rows.length)return '<div class="muted">Нет telemetry events.</div>';
 const max=Math.max(...rows.map(x=>x.end_ms),1);
 let h='<div class="waterfall">';
 rows.slice(0,80).forEach(x=>{
   const left=Math.max(0,x.start_ms/max*100), width=Math.max(0.4,x.duration_ms/max*100);
   h+='<div class="wfrow"><span class="wflabel" title="'+esc(x.url)+'">'+esc(x.method+' '+x.resource_type+' '+x.url)+'</span><span class="track"><span class="block" style="left:'+left+'%;width:'+width+'%"></span></span> <span class="small">'+x.duration_ms.toFixed(0)+' ms</span></div>';
 });
 return h+'</div><p class="muted small">Показаны первые 80 событий по времени начала. Шкала нормирована на максимальный end timestamp.</p>';
}
function tableSlow(rows){let h='<table><tr><th>Duration</th><th>Status</th><th>Method</th><th>Type</th><th>URL</th></tr>';rows.forEach(x=>h+='<tr><td>'+x.duration_ms.toFixed(0)+' ms</td><td>'+esc(x.status)+'</td><td>'+esc(x.method)+'</td><td>'+esc(x.resource_type)+'</td><td class="small">'+esc(x.url)+'</td></tr>');return h+'</table>'}
async function runDemo(){document.getElementById('status').textContent='Выполняется...';const r=await fetch('/api/demo');render(await r.json());document.getElementById('status').textContent='Готово: synthetic benchmark';}
async function analyzeFile(){const f=document.getElementById('file').files[0];if(!f){alert('Выберите telemetry.json');return}const fd=new FormData();fd.append('file',f);document.getElementById('status').textContent='Загрузка telemetry...';const r=await fetch('/api/analyze-telemetry',{method:'POST',body:fd});const d=await r.json();if(!r.ok){alert(d.error||'Ошибка');return}render(d,true);document.getElementById('status').textContent='Готово: real telemetry';}
async function reportFile(){const f=document.getElementById('file').files[0];if(!f){alert('Выберите telemetry.json');return}const fd=new FormData();fd.append('file',f);const r=await fetch('/api/report',{method:'POST',body:fd});const text=await r.text();if(!r.ok){alert(text);return}const blob=new Blob([text],{type:'text/markdown'});const a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download='performance_report.md';a.click();URL.revokeObjectURL(a.href);}
runDemo();
</script></body></html>"""


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
