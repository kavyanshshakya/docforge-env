"""
DocForge — FastAPI server for the document extraction environment.
Exposes HTTP + WebSocket endpoints compatible with the OpenEnv protocol.
"""
from __future__ import annotations
import uvicorn
from dataclasses import asdict
from typing import Any, Dict, List, Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
try:
    from server.environment import DataExtractEnvironment
    from server.models import DataExtractAction
    from server.tasks import ALL_TASKS as TASKS
except ImportError:
    from environment import DataExtractEnvironment
    from models import DataExtractAction
    from tasks import ALL_TASKS as TASKS

app = FastAPI(
    title="DocForge Environment",
    description="Structured document extraction benchmark with corruption engine",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

_envs: Dict[str, DataExtractEnvironment] = {}


def _get_env(sid: str = "default") -> DataExtractEnvironment:
    if sid not in _envs:
        _envs[sid] = DataExtractEnvironment()
    return _envs[sid]


# ── Request / Response models ──

class ResetRequest(BaseModel):
    task_id: Optional[str] = None
    difficulty: Optional[str] = None
    seed: Optional[int] = None
    category: Optional[str] = None

class StepRequest(BaseModel):
    extracted_json: str
    confidence_json: Optional[str] = None

class EnvResponse(BaseModel):
    observation: Dict[str, Any]
    reward: float
    done: bool
    info: Dict[str, Any] = {}

class TaskInfo(BaseModel):
    task_id: str
    difficulty: str
    num_fields: int
    document_type: str
    schema_preview: str


# ── Endpoints ──

@app.get("/", response_class=HTMLResponse)
def root():
    return HTMLResponse('<!DOCTYPE html>\n<html lang="en">\n<head>\n<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">\n<title>DocForge</title>\n<link rel="preconnect" href="https://fonts.googleapis.com">\n<link href="https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700;1,9..40,400&family=IBM+Plex+Mono:wght@400;500;600&display=swap" rel="stylesheet">\n<style>\n:root {\n  --bg: #0c0e14;\n  --bg-card: rgba(255,255,255,0.03);\n  --bg-card-hover: rgba(255,255,255,0.05);\n  --bg-inset: rgba(0,0,0,0.3);\n  --border: rgba(255,255,255,0.06);\n  --border-hover: rgba(255,255,255,0.12);\n  --text-primary: #f0f0f3;\n  --text-secondary: #9ca3af;\n  --text-tertiary: #6b7280;\n  --accent: #f59e0b;\n  --accent-dim: rgba(245,158,11,0.12);\n  --blue: #3b82f6;\n  --green: #22c55e;\n  --red: #ef4444;\n  --purple: #a78bfa;\n  --radius: 16px;\n  --radius-sm: 10px;\n  --font: \'DM Sans\', system-ui, sans-serif;\n  --mono: \'IBM Plex Mono\', \'Menlo\', monospace;\n}\n* { margin:0; padding:0; box-sizing:border-box; }\nbody {\n  font-family: var(--font);\n  background: var(--bg);\n  color: var(--text-secondary);\n  min-height: 100vh;\n  font-size: 16px;\n  line-height: 1.6;\n  -webkit-font-smoothing: antialiased;\n}\n/* Subtle gradient mesh background */\nbody::before {\n  content: \'\';\n  position: fixed; top: 0; left: 0; right: 0; bottom: 0;\n  background:\n    radial-gradient(ellipse 60% 50% at 20% 10%, rgba(59,130,246,0.06) 0%, transparent 70%),\n    radial-gradient(ellipse 50% 40% at 80% 80%, rgba(168,85,247,0.04) 0%, transparent 70%),\n    radial-gradient(ellipse 40% 30% at 50% 50%, rgba(245,158,11,0.03) 0%, transparent 70%);\n  pointer-events: none;\n  z-index: 0;\n}\n.wrap { position: relative; z-index: 1; max-width: 800px; margin: 0 auto; padding: 48px 24px 64px; }\n\n/* Header */\n.header { margin-bottom: 40px; }\n.logo {\n  font-size: 0.75rem;\n  font-family: var(--mono);\n  font-weight: 500;\n  color: var(--accent);\n  letter-spacing: 2px;\n  text-transform: uppercase;\n  margin-bottom: 12px;\n}\nh1 {\n  font-size: 2.25rem;\n  font-weight: 700;\n  color: var(--text-primary);\n  letter-spacing: -0.75px;\n  line-height: 1.15;\n  margin-bottom: 8px;\n}\n.header p {\n  font-size: 1rem;\n  color: var(--text-tertiary);\n  max-width: 520px;\n}\n.pills { display: flex; gap: 6px; flex-wrap: wrap; margin-top: 16px; }\n.pill {\n  font-size: 0.6875rem;\n  font-family: var(--mono);\n  font-weight: 500;\n  padding: 5px 12px;\n  border-radius: 100px;\n  background: var(--bg-card);\n  border: 1px solid var(--border);\n  color: var(--text-tertiary);\n  letter-spacing: 0.3px;\n}\n\n/* Cards */\n.card {\n  background: var(--bg-card);\n  backdrop-filter: blur(20px);\n  -webkit-backdrop-filter: blur(20px);\n  border: 1px solid var(--border);\n  border-radius: var(--radius);\n  padding: 24px;\n  margin-bottom: 12px;\n  transition: border-color 0.25s ease, background 0.25s ease;\n}\n.card:hover {\n  border-color: var(--border-hover);\n  background: var(--bg-card-hover);\n}\n.card-label {\n  font-size: 0.6875rem;\n  font-family: var(--mono);\n  font-weight: 600;\n  color: var(--text-tertiary);\n  letter-spacing: 1.5px;\n  text-transform: uppercase;\n  margin-bottom: 16px;\n}\n\n/* Stats */\n.stats { display: grid; grid-template-columns: repeat(4,1fr); gap: 8px; }\n@media(max-width:600px) { .stats { grid-template-columns: repeat(2,1fr); } }\n.stat {\n  background: var(--bg-inset);\n  border-radius: var(--radius-sm);\n  padding: 20px 16px;\n  text-align: center;\n}\n.stat-num {\n  font-size: 2rem;\n  font-weight: 700;\n  color: var(--text-primary);\n  line-height: 1;\n  font-variant-numeric: tabular-nums;\n}\n.stat-label {\n  font-size: 0.6875rem;\n  font-family: var(--mono);\n  color: var(--text-tertiary);\n  margin-top: 6px;\n  text-transform: uppercase;\n  letter-spacing: 0.5px;\n}\n\n/* Corruption demo */\n.demo {\n  background: var(--bg-inset);\n  border-radius: var(--radius-sm);\n  padding: 20px;\n  font-family: var(--mono);\n  font-size: 0.8125rem;\n  line-height: 1.9;\n  white-space: pre-wrap;\n  color: var(--text-tertiary);\n  margin-bottom: 12px;\n}\n.demo .hi { color: var(--text-primary); }\n.demo mark {\n  background: rgba(239,68,68,0.12);\n  color: #fca5a5;\n  border-radius: 3px;\n  padding: 1px 5px;\n  font-weight: 600;\n}\n.modes { display: flex; gap: 6px; flex-wrap: wrap; }\n.mode {\n  font-size: 0.6875rem;\n  font-family: var(--mono);\n  padding: 4px 10px;\n  border-radius: 6px;\n  background: var(--bg-inset);\n  color: var(--text-tertiary);\n}\n\n/* Tasks */\n.task-row {\n  display: flex;\n  align-items: center;\n  padding: 14px 0;\n  border-bottom: 1px solid var(--border);\n  font-size: 0.9375rem;\n}\n.task-row:last-child { border-bottom: none; }\n.task-name { flex: 1; color: var(--text-primary); font-weight: 500; }\n.task-meta { color: var(--text-tertiary); font-size: 0.8125rem; font-family: var(--mono); margin-left: 12px; }\n.badge {\n  display: inline-block;\n  padding: 2px 10px;\n  border-radius: 100px;\n  font-size: 0.625rem;\n  font-family: var(--mono);\n  font-weight: 600;\n  letter-spacing: 0.5px;\n  text-transform: uppercase;\n  margin-left: 12px;\n}\n.badge-easy   { background: rgba(34,197,94,0.1);  color: #4ade80; border: 1px solid rgba(34,197,94,0.2); }\n.badge-medium { background: rgba(245,158,11,0.1); color: #fbbf24; border: 1px solid rgba(245,158,11,0.2); }\n.badge-hard   { background: rgba(239,68,68,0.1);  color: #fca5a5; border: 1px solid rgba(239,68,68,0.2); }\n\n/* Grading grid */\n.grade-grid { display: grid; grid-template-columns: repeat(4,1fr); gap: 8px; }\n@media(max-width:600px) { .grade-grid { grid-template-columns: repeat(2,1fr); } }\n.grade-item {\n  background: var(--bg-inset);\n  border-radius: var(--radius-sm);\n  padding: 16px;\n  text-align: center;\n}\n.grade-label {\n  font-size: 0.625rem;\n  font-family: var(--mono);\n  color: var(--text-tertiary);\n  text-transform: uppercase;\n  letter-spacing: 0.5px;\n  margin-bottom: 6px;\n}\n.grade-value {\n  font-size: 0.875rem;\n  color: var(--text-primary);\n  font-weight: 600;\n}\n\n/* API endpoints */\n.ep-row {\n  display: flex;\n  align-items: center;\n  gap: 12px;\n  padding: 9px 0;\n  border-bottom: 1px solid var(--border);\n  font-family: var(--mono);\n  font-size: 0.8125rem;\n}\n.ep-row:last-child { border-bottom: none; }\n.ep-method {\n  font-size: 0.6875rem;\n  font-weight: 600;\n  width: 40px;\n}\n.mc-get { color: var(--green); }\n.mc-post { color: var(--blue); }\n.mc-ws { color: var(--purple); }\n.ep-path { color: var(--text-primary); font-weight: 500; }\n.ep-desc { margin-left: auto; color: var(--text-tertiary); font-family: var(--font); font-size: 0.8125rem; }\n\n/* Try It */\n.try-bar { display: flex; gap: 8px; flex-wrap: wrap; align-items: center; margin-bottom: 16px; }\nselect {\n  font-family: var(--mono);\n  font-size: 0.8125rem;\n  background: var(--bg-inset);\n  color: var(--text-secondary);\n  border: 1px solid var(--border);\n  border-radius: var(--radius-sm);\n  padding: 10px 14px;\n  min-height: 44px;\n  cursor: pointer;\n  transition: border-color 0.2s ease;\n}\nselect:focus { outline: 2px solid var(--accent); outline-offset: 2px; border-color: var(--accent); }\n.btn {\n  font-family: var(--font);\n  font-size: 0.8125rem;\n  font-weight: 600;\n  border: none;\n  border-radius: var(--radius-sm);\n  padding: 10px 20px;\n  min-height: 44px;\n  cursor: pointer;\n  color: #fff;\n  transition: all 0.2s ease;\n}\n.btn:hover { transform: translateY(-1px); filter: brightness(1.1); }\n.btn:active { transform: translateY(0); }\n.btn:focus-visible { outline: 2px solid var(--text-primary); outline-offset: 2px; }\n.btn-load { background: var(--blue); }\n.btn-submit { background: var(--green); }\n\n.doc-meta { display: flex; align-items: center; gap: 8px; margin-bottom: 12px; }\n.doc-meta span { font-size: 0.8125rem; color: var(--text-secondary); font-weight: 500; }\n.schema-hint { font-size: 0.8125rem; color: var(--text-tertiary); margin-bottom: 8px; line-height: 1.6; }\n.schema-hint strong { color: var(--text-secondary); }\n.doc-box {\n  background: var(--bg-inset);\n  border-radius: var(--radius-sm);\n  padding: 16px;\n  font-family: var(--mono);\n  font-size: 0.8125rem;\n  white-space: pre-wrap;\n  max-height: 240px;\n  overflow-y: auto;\n  margin-bottom: 12px;\n  color: var(--text-secondary);\n  line-height: 1.7;\n}\n.doc-box::-webkit-scrollbar { width: 5px; }\n.doc-box::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 3px; }\ntextarea {\n  width: 100%;\n  font-family: var(--mono);\n  font-size: 0.8125rem;\n  background: var(--bg-inset);\n  color: var(--text-primary);\n  border: 1px solid var(--border);\n  border-radius: var(--radius-sm);\n  padding: 14px;\n  resize: vertical;\n  line-height: 1.6;\n  transition: border-color 0.2s ease;\n}\ntextarea:focus { outline: 2px solid var(--accent); outline-offset: 2px; border-color: var(--accent); }\n.hint { font-size: 0.8125rem; color: var(--text-tertiary); margin-top: 8px; }\n\n.fb-box {\n  margin-top: 12px;\n  padding: 16px;\n  background: var(--bg-inset);\n  border-radius: var(--radius-sm);\n  display: none;\n}\n.fb-score { font-size: 1.25rem; font-weight: 700; font-variant-numeric: tabular-nums; }\n.fb-detail { font-size: 0.8125rem; color: var(--text-tertiary); margin-top: 6px; line-height: 1.6; }\n\n/* Footer */\nfooter {\n  text-align: center;\n  margin-top: 40px;\n  padding-top: 24px;\n  border-top: 1px solid var(--border);\n  font-size: 0.8125rem;\n  color: var(--text-tertiary);\n}\nfooter a { color: var(--accent); text-decoration: none; }\nfooter a:hover { text-decoration: underline; }\nfooter a:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }\n\n/* Entrance animation */\n@keyframes fadeUp {\n  from { opacity: 0; transform: translateY(12px); }\n  to { opacity: 1; transform: translateY(0); }\n}\n.card, .header { animation: fadeUp 0.5s ease-out both; }\n.card:nth-child(2) { animation-delay: 0.05s; }\n.card:nth-child(3) { animation-delay: 0.1s; }\n.card:nth-child(4) { animation-delay: 0.15s; }\n.card:nth-child(5) { animation-delay: 0.2s; }\n.card:nth-child(6) { animation-delay: 0.25s; }\n.card:nth-child(7) { animation-delay: 0.3s; }\n\n@media (prefers-reduced-motion: reduce) {\n  .card, .header { animation: none; }\n}\n</style>\n</head>\n<body>\n<div class="wrap">\n\n<div class="header">\n  <div class="logo">DocForge</div>\n  <h1>Document Understanding<br>with Corruption Engine</h1>\n  <p>Extract structured data from realistically corrupted documents. 31 tasks across 9 capabilities including multilingual, cross-doc reconciliation, and PII detection with seed-reproducible noise.</p>\n  <div class="pills" role="list">\n    <span class="pill" role="listitem">OpenEnv</span>\n    <span class="pill" role="listitem">31 Tasks</span>\n    <span class="pill" role="listitem">9 Capabilities</span>\n    <span class="pill" role="listitem">Seed-Reproducible</span>\n    <span class="pill" role="listitem">P / R / F1</span>\n  </div>\n</div>\n\n<div class="card">\n  <div class="card-label">Overview</div>\n  <div class="stats">\n    <div class="stat"><div class="stat-num">31</div><div class="stat-label">Tasks</div></div>\n    <div class="stat"><div class="stat-num">9</div><div class="stat-label">Capabilities</div></div>\n    <div class="stat"><div class="stat-num">3</div><div class="stat-label">Tiers</div></div>\n    <div class="stat"><div class="stat-num">9</div><div class="stat-label">Corruption</div></div>\n  </div>\n</div>\n\n<div class="card">\n  <div class="card-label">Corruption Engine</div>\n  <div class="demo"><span class="hi">Original:</span>  Thornfield &amp; Associates LLP, Invoice TF/2026/0339\n<span class="hi">Corrupted:</span> <mark>Thornfie1d</mark> &amp; Associates LLP, Invoice TF/<mark>Z0Z6</mark>/<mark>O</mark>339\n           <mark>[REDACTED]</mark> attention of: James Whit<mark>rn</mark>ore</div>\n  <div class="modes" role="list">\n    <span class="mode" role="listitem">OCR swaps</span>\n    <span class="mode" role="listitem">Redaction</span>\n    <span class="mode" role="listitem">Whitespace</span>\n    <span class="mode" role="listitem">Line breaks</span>\n    <span class="mode" role="listitem">Contradictions</span>\n    <span class="mode" role="listitem">Phone digits</span>\n    <span class="mode" role="listitem">Email OCR</span>\n    <span class="mode" role="listitem">Amount shift</span>\n    <span class="mode" role="listitem">Seeded</span>\n  </div>\n</div>\n\n<div class="card">\n  <div class="card-label">Tasks</div>\n  <div role="list">\n    <div class="task-row" role="listitem"><span class="task-name">Contact Extraction</span><span class="badge badge-easy">Easy</span><span class="task-meta">4 &middot; 6 fields</span></div>\n    <div class="task-row" role="listitem"><span class="task-name">Support Tickets</span><span class="badge badge-easy">Easy</span><span class="task-meta">2 &middot; 10 fields</span></div>\n    <div class="task-row" role="listitem"><span class="task-name">Job Postings</span><span class="badge badge-medium">Medium</span><span class="task-meta">4 &middot; 12 fields</span></div>\n    <div class="task-row" role="listitem"><span class="task-name">Receipts</span><span class="badge badge-medium">Medium</span><span class="task-meta">3 &middot; 13 fields</span></div>\n    <div class="task-row" role="listitem"><span class="task-name">Invoices / POs</span><span class="badge badge-hard">Hard</span><span class="task-meta">4 &middot; 15+ fields</span></div>\n    <div class="task-row" role="listitem"><span class="task-name">Multilingual</span><span class="badge badge-medium">Medium</span><span class="task-meta">3 tasks</span></div>\n    <div class="task-row" role="listitem"><span class="task-name">Cross-Doc Reconciliation</span><span class="badge badge-hard">Hard</span><span class="task-meta">2 tasks</span></div>\n    <div class="task-row" role="listitem"><span class="task-name">Confidence Calibration</span><span class="badge badge-medium">Medium</span><span class="task-meta">1 task</span></div>\n    <div class="task-row" role="listitem"><span class="task-name">Schema-Free</span><span class="badge badge-hard">Hard</span><span class="task-meta">1 task</span></div>\n    <div class="task-row" role="listitem"><span class="task-name">Temporal Reasoning</span><span class="badge badge-hard">Hard</span><span class="task-meta">2 tasks</span></div>\n    <div class="task-row" role="listitem"><span class="task-name">Adversarial</span><span class="badge badge-hard">Hard</span><span class="task-meta">2 tasks</span></div>\n    <div class="task-row" role="listitem"><span class="task-name">Table Reconstruction</span><span class="badge badge-hard">Hard</span><span class="task-meta">1 task</span></div>\n    <div class="task-row" role="listitem"><span class="task-name">PII Detection</span><span class="badge badge-medium">Medium</span><span class="task-meta">1 task</span></div>\n    <div class="task-row" role="listitem"><span class="task-name">Hierarchical</span><span class="badge badge-hard">Hard</span><span class="task-meta">1 task</span></div>\n  </div>\n</div>\n\n<div class="card">\n  <div class="card-label">Grading</div>\n  <div class="grade-grid">\n    <div class="grade-item"><div class="grade-label">Strings</div><div class="grade-value">Jaccard + Levenshtein</div></div>\n    <div class="grade-item"><div class="grade-label">Metrics</div><div class="grade-value">P / R / F1</div></div>\n    <div class="grade-item"><div class="grade-label">Nested</div><div class="grade-value">Greedy Alignment</div></div>\n    <div class="grade-item"><div class="grade-label">Attempts</div><div class="grade-value">5 with Feedback</div></div>\n  </div>\n</div>\n\n<div class="card">\n  <div class="card-label">API</div>\n  <div role="list">\n    <div class="ep-row" role="listitem"><span class="ep-method mc-get">GET</span><span class="ep-path">/health</span><span class="ep-desc">Health check</span></div>\n    <div class="ep-row" role="listitem"><span class="ep-method mc-get">GET</span><span class="ep-path">/tasks</span><span class="ep-desc">List all tasks</span></div>\n    <div class="ep-row" role="listitem"><span class="ep-method mc-get">GET</span><span class="ep-path">/metrics</span><span class="ep-desc">Performance stats</span></div>\n    <div class="ep-row" role="listitem"><span class="ep-method mc-post">POST</span><span class="ep-path">/reset</span><span class="ep-desc">Reset episode</span></div>\n    <div class="ep-row" role="listitem"><span class="ep-method mc-post">POST</span><span class="ep-path">/step</span><span class="ep-desc">Submit extraction</span></div>\n    <div class="ep-row" role="listitem"><span class="ep-method mc-get">GET</span><span class="ep-path">/state</span><span class="ep-desc">Episode state</span></div>\n    <div class="ep-row" role="listitem"><span class="ep-method mc-ws">WS</span><span class="ep-path">/ws</span><span class="ep-desc">OpenEnv protocol</span></div>\n  </div>\n</div>\n\n<div class="card">\n  <div class="card-label">Try It Live</div>\n  <div class="try-bar">\n    <label for="ts" style="position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0,0,0,0)">Select task</label>\n    <select id="ts" aria-label="Select a task">\n      <option value="">Random</option>\n      <option value="contact_01">contact_01 — Easy</option>\n      <option value="ticket_01">ticket_01 — Easy</option>\n      <option value="job_01">job_01 — Medium</option>\n      <option value="receipt_01">receipt_01 — Medium</option>\n      <option value="invoice_01">invoice_01 — Hard</option>\\n      <option value="multi_de_01">multi_de_01 — Multilingual</option>\\n      <option value="crossdoc_01">crossdoc_01 — Cross-Doc</option>\\n      <option value="confidence_01">confidence_01 — Confidence</option>\\n      <option value="temporal_01">temporal_01 — Temporal</option>\\n      <option value="pii_01">pii_01 — PII</option>\\n      <option value="hierarchical_01">hierarchical_01 — Hierarchical</option>\\n    </select>\n    <button class="btn btn-load" onclick="doR()" aria-label="Load selected task">Load Task</button>\n    <button class="btn btn-submit" onclick="doS()" aria-label="Submit JSON extraction">Submit</button>\n  </div>\n  <div id="dp" style="display:none">\n    <div class="doc-meta"><span class="badge" id="db"></span><span id="tl"></span></div>\n    <p class="schema-hint"><strong>Schema:</strong> <span id="st"></span></p>\n    <div class="doc-box" id="rt" role="region" aria-label="Document text" tabindex="0"></div>\n    <label for="ji" style="position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0,0,0,0)">JSON extraction</label>\n    <textarea id="ji" rows="5" placeholder=\'{"name": "...", "email": "..."}\' aria-label="Enter your JSON extraction"></textarea>\n    <p class="hint">Paste your JSON extraction above and click Submit.</p>\n    <div id="fb" class="fb-box" role="status" aria-live="polite">\n      <div id="fs" class="fb-score"></div>\n      <div id="ft2" class="fb-detail"></div>\n    </div>\n  </div>\n</div>\n\n<footer>DocForge &mdash; Built for the <a href="https://meta-pytorch.org/OpenEnv/">OpenEnv</a> Hackathon</footer>\n\n</div>\n<script>\nasync function doR(){\n  const t=document.getElementById(\'ts\').value, b=t?{task_id:t}:{};\n  try {\n    const r=await fetch(\'/reset\',{method:\'POST\',headers:{\'Content-Type\':\'application/json\'},body:JSON.stringify(b)});\n    const d=await r.json(), o=d.observation;\n    document.getElementById(\'dp\').style.display=\'block\';\n    document.getElementById(\'rt\').textContent=o.raw_text;\n    document.getElementById(\'st\').textContent=o.schema_description;\n    document.getElementById(\'tl\').textContent=o.task_id+\' \\u2022 \'+o.steps_remaining+\' steps\';\n    const e=document.getElementById(\'db\');\n    e.textContent=o.difficulty[0].toUpperCase()+o.difficulty.slice(1);\n    e.className=\'badge badge-\'+o.difficulty;\n    document.getElementById(\'fb\').style.display=\'none\';\n    document.getElementById(\'ji\').value=\'\';\n  } catch(e){ alert(e.message); }\n}\nasync function doS(){\n  const j=document.getElementById(\'ji\').value;\n  if(!j) return alert(\'Enter JSON first\');\n  try {\n    const r=await fetch(\'/step\',{method:\'POST\',headers:{\'Content-Type\':\'application/json\'},body:JSON.stringify({extracted_json:j})});\n    const d=await r.json();\n    if(d.detail) return alert(d.detail);\n    const o=d.observation, f=document.getElementById(\'fb\');\n    f.style.display=\'block\';\n    const s=document.getElementById(\'fs\');\n    s.textContent=(o.score*100).toFixed(1)+\'%\';\n    s.style.color=o.score>0.8?\'var(--green)\':o.score>0.5?\'var(--accent)\':\'var(--red)\';\n    document.getElementById(\'ft2\').textContent=o.feedback;\n    document.getElementById(\'tl\').textContent=o.task_id+\' \\u2022 \'+o.steps_remaining+\' steps\'+(d.done?\' \\u2022 Done\':\'\');\n  } catch(e){ alert(e.message); }\n}\n</script>\n</body>\n</html>\n')

@app.get("/health")
def health():
    return {"status": "ok", "environment": "docforge", "tasks_loaded": len(TASKS)}

@app.get("/tasks", response_model=List[TaskInfo])
def list_tasks():
    """List all available tasks with metadata."""
    result = []
    for t in TASKS:
        tid = t["task_id"]
        if tid.startswith("contact") or tid.startswith("ticket"):
            doc_type = "support_ticket" if tid.startswith("ticket") else "contact"
        elif tid.startswith("job"):
            doc_type = "job_posting"
        elif tid.startswith("receipt"):
            doc_type = "receipt"
        else:
            doc_type = "invoice"
        result.append(TaskInfo(
            task_id=tid,
            difficulty=t["difficulty"],
            num_fields=len(t["gold_labels"]),
            document_type=doc_type,
            schema_preview=t["schema_description"][:100] + "...",
        ))
    return result

@app.post("/reset", response_model=EnvResponse)
def reset(req: ResetRequest = ResetRequest()):
    env = _get_env()
    obs, reward, done, info = env.reset(task_id=req.task_id, difficulty=req.difficulty, seed=req.seed, category=req.category)
    return EnvResponse(observation=asdict(obs), reward=reward, done=done, info=info)

@app.post("/step", response_model=EnvResponse)
def step(req: StepRequest):
    env = _get_env()
    if not env.state.task_id:
        raise HTTPException(status_code=400, detail="Call /reset before /step")
    if len(req.extracted_json) > 50000:
        raise HTTPException(status_code=400, detail="Payload too large (max 50KB)")
    obs, reward, done, info = env.step(DataExtractAction(extracted_json=req.extracted_json, confidence_json=req.confidence_json))
    return EnvResponse(observation=asdict(obs), reward=reward, done=done, info=info)

@app.get("/state")
def state():
    return _get_env().get_state()

@app.get("/metrics")
def metrics():
    """Aggregate performance metrics across all completed episodes."""
    return _get_env().get_metrics()

@app.websocket("/ws")
async def ws_endpoint(ws: WebSocket):
    await ws.accept()
    env = DataExtractEnvironment()
    try:
        while True:
            data = await ws.receive_json()
            act = data.get("action", "")
            if act == "reset":
                obs, r, d, info = env.reset(task_id=data.get("task_id"), difficulty=data.get("difficulty"))
                await ws.send_json({"observation": asdict(obs), "reward": r, "done": d, "info": info})
            elif act == "step":
                obs, r, d, info = env.step(DataExtractAction(extracted_json=data.get("extracted_json", "{}")))
                await ws.send_json({"observation": asdict(obs), "reward": r, "done": d, "info": info})
            elif act == "state":
                await ws.send_json(env.get_state())
            elif act == "tasks":
                await ws.send_json({"tasks": [t["task_id"] for t in TASKS]})
            else:
                await ws.send_json({"error": f"Unknown action: {act}"})
    except WebSocketDisconnect:
        pass

def main():
    """Entry point for multi-mode deployment."""
    uvicorn.run(app, host="0.0.0.0", port=7860)

if __name__ == "__main__":
    main()
