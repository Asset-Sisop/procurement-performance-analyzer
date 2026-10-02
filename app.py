from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from typing import List

app = FastAPI(title="Procurement Performance Analyzer", version="0.1.0")

class Stage(BaseModel):
    name: str
    category: str
    duration_ms: float
    blocking: bool = False
    parallelizable: bool = False

class Benchmark(BaseModel):
    stages: List[Stage]

def bottlenecks(stages, limit=5):
    total = sum(s.duration_ms for s in stages)
    ranked = sorted(stages, key=lambda x: x.duration_ms, reverse=True)[:limit]
    return [{
        "name": s.name,
        "category": s.category,
        "duration_ms": round(s.duration_ms, 2),
        "share_pct": round(s.duration_ms / total * 100, 2) if total else 0,
        "blocking": s.blocking,
        "parallelizable": s.parallelizable
    } for s in ranked]

def optimize(stages):
    # Demonstration rules only. These are hypotheses to validate against a real platform.
    result = []
    for s in stages:
        d = s.duration_ms
        note = "Без изменения"
        if s.parallelizable:
            d *= 0.55
            note = "Гипотеза: перенос/параллелизация допустимой операции"
        elif s.category == "data" and d > 1000:
            d *= 0.75
            note = "Гипотеза: предварительная подготовка/оптимизация payload"
        elif s.category == "network" and d > 1000:
            d *= 0.85
            note = "Гипотеза: оптимизация клиентской сетевой части"
        elif s.category == "browser" and d > 1000:
            d *= 0.70
            note = "Гипотеза: сокращение клиентских операций"
        result.append({
            "name": s.name,
            "before_ms": round(s.duration_ms, 2),
            "after_ms": round(d, 2),
            "saving_ms": round(s.duration_ms-d, 2),
            "note": note
        })
    return result

@app.get("/", response_class=HTMLResponse)
def index():
    return HTMLResponse("""<!doctype html>
<html lang="ru"><head><meta charset="utf-8">
<title>Procurement Performance Analyzer</title>
<style>
body{font-family:Arial,sans-serif;margin:0;background:#f5f7fa;color:#17202a}
.wrap{max-width:1180px;margin:30px auto;padding:0 20px}
.card{background:white;border-radius:14px;padding:20px;margin:16px 0;box-shadow:0 2px 12px #00000010}
h1{margin-bottom:4px}.muted{color:#667085}
button{background:#111827;color:white;border:0;border-radius:8px;padding:11px 16px;cursor:pointer}
.grid{display:grid;grid-template-columns:repeat(4,1fr);gap:12px}
.metric{padding:16px;border:1px solid #e5e7eb;border-radius:10px}.metric b{font-size:25px;display:block}
table{width:100%;border-collapse:collapse}th,td{padding:10px;border-bottom:1px solid #eee;text-align:left}
.bar{height:18px;background:#e5e7eb;border-radius:10px;overflow:hidden}.fill{height:100%;background:#374151}
pre{background:#111827;color:#e5e7eb;padding:15px;border-radius:10px;overflow:auto}
@media(max-width:800px){.grid{grid-template-columns:1fr 1fr}}
</style></head>
<body><div class="wrap">
<h1>Procurement Performance Analyzer</h1>
<div class="muted">Демонстрационный MVP для инструментального аудита процесса подачи заявки</div>
<div class="card">
<button onclick="run()">Запустить тестовый сценарий</button>
<span id="status" class="muted" style="margin-left:12px">Готов к запуску</span>
</div>
<div id="out"></div>
<script>
async function run(){
 document.getElementById('status').textContent='Выполняется benchmark...';
 const r=await fetch('/api/demo'); const d=await r.json();
 document.getElementById('status').textContent='Готово';
 let html=`<div class="grid">
 <div class="metric"><span>Baseline</span><b>${(d.total_before/1000).toFixed(2)} s</b></div>
 <div class="metric"><span>Модель optimization</span><b>${(d.total_after/1000).toFixed(2)} s</b></div>
 <div class="metric"><span>Экономия</span><b>${(d.saving_pct).toFixed(1)}%</b></div>
 <div class="metric"><span>Bottleneck #1</span><b style="font-size:16px">${d.bottlenecks[0]?.name||'-'}</b></div>
 </div>`;
 html+=`<div class="card"><h2>Timeline</h2><table><tr><th>Операция</th><th>Категория</th><th>Время</th><th>Доля</th></tr>`;
 d.bottlenecks.forEach(x=>html+=`<tr><td>${x.name}</td><td>${x.category}</td><td>${x.duration_ms.toFixed(0)} ms</td><td>${x.share_pct}%<div class="bar"><div class="fill" style="width:${Math.min(x.share_pct,100)}%"></div></div></td></tr>`);
 html+=`</table></div>`;
 html+=`<div class="card"><h2>Предлагаемые оптимизации (гипотезы)</h2><table><tr><th>Операция</th><th>До</th><th>После</th><th>Экономия</th><th>Обоснование</th></tr>`;
 d.optimization.forEach(x=>html+=`<tr><td>${x.name}</td><td>${x.before_ms.toFixed(0)} ms</td><td>${x.after_ms.toFixed(0)} ms</td><td>${x.saving_ms.toFixed(0)} ms</td><td>${x.note}</td></tr>`);
 html+=`</table></div>`;
 html+=`<div class="card"><h2>Важно</h2><p>Расчёт после оптимизации является демонстрационной моделью. На реальной площадке коэффициенты должны быть заменены фактическими измерениями и подтверждены допустимыми способами взаимодействия.</p></div>`;
 document.getElementById('out').innerHTML=html;
}
</script></div></body></html>""")

@app.get("/api/demo")
def demo():
    stages = [
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
    before = sum(s.duration_ms for s in stages)
    opt = optimize(stages)
    after = sum(x["after_ms"] for x in opt)
    return {
        "total_before": before,
        "total_after": after,
        "saving_ms": before-after,
        "saving_pct": (before-after)/before*100,
        "bottlenecks": bottlenecks(stages),
        "optimization": opt,
        "methodology": "Demo model; replace with measured telemetry from an authorized test scenario."
    }

@app.post("/api/analyze")
def analyze(benchmark: Benchmark):
    if not benchmark.stages:
        return JSONResponse({"error": "stages must not be empty"}, status_code=400)
    before = sum(s.duration_ms for s in benchmark.stages)
    opt = optimize(benchmark.stages)
    after = sum(x["after_ms"] for x in opt)
    return {
        "total_before_ms": before,
        "model_total_after_ms": after,
        "model_saving_pct": (before-after)/before*100 if before else 0,
        "bottlenecks": bottlenecks(benchmark.stages),
        "optimization": opt
    }

@app.get("/health")
def health():
    return {"status":"ok","service":"procurement-performance-analyzer"}
