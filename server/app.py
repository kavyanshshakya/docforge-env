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
    from server.tasks import TASKS
except ImportError:
    from environment import DataExtractEnvironment
    from models import DataExtractAction
    from tasks import TASKS

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

class StepRequest(BaseModel):
    extracted_json: str

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
    return HTMLResponse('<!DOCTYPE html>\n<html lang="en">\n<head>\n<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">\n<title>DocForge</title>\n<style>\n*{margin:0;padding:0;box-sizing:border-box}\nbody{font-family:\'Inter\',-apple-system,BlinkMacSystemFont,sans-serif;background:#09090b;color:#d4d4d8;min-height:100vh;line-height:1.6;font-size:16px}\n.bar{height:3px;background:linear-gradient(90deg,#3b82f6,#8b5cf6,#ec4899)}\n.c{max-width:860px;margin:0 auto;padding:32px 20px 48px}\nh1{font-size:1.875rem;color:#fafafa;margin-bottom:2px;letter-spacing:-0.5px}\nh1 span{background:linear-gradient(135deg,#60a5fa,#a78bfa);-webkit-background-clip:text;-webkit-text-fill-color:transparent}\n.sub{color:#a1a1aa;margin-bottom:6px;font-size:0.875rem}\n.tags{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:28px}\n.tag{font-size:0.75rem;padding:4px 12px;border-radius:20px;background:#18181b;border:1px solid #27272a;color:#a1a1aa;font-weight:500;letter-spacing:0.3px}\n.card{background:#18181b;border:1px solid #27272a;border-radius:14px;padding:22px;margin-bottom:14px;transition:border-color 0.2s}\n.card:hover{border-color:#3f3f46}\n.card h2{font-size:1rem;color:#fafafa;margin-bottom:14px;font-weight:700}\n.sg{display:grid;grid-template-columns:repeat(4,1fr);gap:10px}\n@media(max-width:600px){.sg{grid-template-columns:repeat(2,1fr)}}\n.s{background:#09090b;border:1px solid #27272a;border-radius:10px;padding:16px;text-align:center}\n.s .n{font-size:2rem;font-weight:800;background:linear-gradient(135deg,#60a5fa,#818cf8);-webkit-background-clip:text;-webkit-text-fill-color:transparent}\n.s .l{font-size:0.75rem;color:#a1a1aa;margin-top:2px;text-transform:uppercase;letter-spacing:0.5px}\n.badge{display:inline-block;padding:3px 10px;border-radius:20px;font-size:0.6875rem;font-weight:700;letter-spacing:0.5px}\n.badge-easy{background:rgba(74,222,128,0.12);color:#4ade80;border:1px solid rgba(74,222,128,0.25)}\n.badge-medium{background:rgba(250,204,21,0.12);color:#fde047;border:1px solid rgba(250,204,21,0.25)}\n.badge-hard{background:rgba(248,113,113,0.12);color:#fca5a5;border:1px solid rgba(248,113,113,0.25)}\n.tl{display:grid;gap:6px}\n.tk{display:flex;align-items:center;padding:12px 14px;background:#09090b;border:1px solid #27272a;border-radius:8px;font-size:0.875rem;transition:background 0.15s}\n.tk:hover{background:#1a1a2e}\n.tk .nm{color:#d4d4d8;flex:1;font-weight:500}\n.tk .fl{color:#a1a1aa;font-size:0.75rem}\n.cx{background:#09090b;border:1px solid #27272a;border-radius:10px;padding:16px;margin-top:10px;font-family:\'Courier New\',monospace;font-size:0.8125rem;line-height:1.8;white-space:pre-wrap;color:#a1a1aa}\n.cx mark{background:rgba(239,68,68,0.18);color:#fca5a5;border-radius:3px;padding:1px 4px;font-weight:600}\n.ms{margin-top:12px;display:flex;gap:6px;flex-wrap:wrap}\n.m{font-size:0.75rem;padding:4px 10px;border-radius:6px;background:#27272a;color:#a1a1aa}\n.eps{display:grid;gap:5px}\n.ep{display:flex;align-items:center;gap:10px;padding:8px 12px;background:#09090b;border:1px solid #27272a;border-radius:7px;font-size:0.8125rem;font-family:\'Courier New\',monospace}\n.ep b{width:42px;font-size:0.75rem}\n.mc-get{color:#4ade80}.mc-post{color:#60a5fa}.mc-ws{color:#c084fc}\n.ep .pa{color:#e4e4e7;font-weight:500}\n.ep .de{color:#a1a1aa;margin-left:auto;font-family:\'Inter\',sans-serif;font-size:0.75rem}\n.gf{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:8px;margin-top:8px}\n.gi{background:#09090b;border:1px solid #27272a;border-radius:8px;padding:14px;text-align:center}\n.gi .gl{font-size:0.75rem;color:#a1a1aa;text-transform:uppercase;letter-spacing:0.4px;margin-bottom:4px}\n.gi .gv{font-size:0.875rem;color:#d4d4d8;font-weight:600}\nselect{background:#09090b;color:#d4d4d8;border:1px solid #3f3f46;border-radius:8px;padding:10px 14px;font-size:0.8125rem;cursor:pointer;min-height:44px}\nselect:focus{outline:2px solid #60a5fa;outline-offset:2px;border-color:#60a5fa}\n.btn{border:none;border-radius:8px;padding:10px 20px;min-height:44px;min-width:44px;cursor:pointer;font-size:0.8125rem;font-weight:600;transition:all 0.2s;color:#fff}\n.btn:hover{transform:translateY(-1px);filter:brightness(1.12)}\n.btn:active{transform:translateY(0)}\n.btn:focus-visible{outline:2px solid #fafafa;outline-offset:2px}\n.bb{background:#2563eb}.bg{background:#16a34a}\n.rtb{background:#09090b;border:1px solid #27272a;border-radius:8px;padding:14px;font-family:\'Courier New\',monospace;font-size:0.8125rem;white-space:pre-wrap;max-height:220px;overflow-y:auto;margin:8px 0;color:#a1a1aa;line-height:1.6}\n.rtb::-webkit-scrollbar{width:6px}.rtb::-webkit-scrollbar-thumb{background:#3f3f46;border-radius:3px}\ntextarea{width:100%;background:#09090b;color:#d4d4d8;border:1px solid #3f3f46;border-radius:8px;padding:12px;font-family:\'Courier New\',monospace;font-size:0.8125rem;resize:vertical;line-height:1.5;transition:border-color 0.2s}\ntextarea:focus{outline:2px solid #60a5fa;outline-offset:2px;border-color:#60a5fa}\n.fb{margin-top:10px;padding:14px;background:#09090b;border-radius:8px;border:1px solid #27272a;display:none}\n.fbs{font-weight:800;font-size:1.125rem}\n.fbt{color:#a1a1aa;font-size:0.8125rem;margin-top:6px;line-height:1.6}\n.ft{text-align:center;margin-top:32px;padding-top:20px;border-top:1px solid #27272a;color:#a1a1aa;font-size:0.75rem}\n.ft a{color:#60a5fa;text-decoration:none}\n.ft a:focus-visible{outline:2px solid #60a5fa;outline-offset:2px}\n.hint{color:#a1a1aa;font-size:0.75rem;font-style:italic;margin-top:8px}\n</style>\n<link rel="preconnect" href="https://fonts.googleapis.com">\n<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">\n</head>\n<body>\n<div class="bar" role="presentation"></div>\n<div class="c">\n<h1><span>DocForge</span></h1>\n<p class="sub">Document Understanding Benchmark with Corruption Engine</p>\n<div class="tags" role="list"><span class="tag" role="listitem">OpenEnv</span><span class="tag" role="listitem">17 Tasks</span><span class="tag" role="listitem">5 Doc Types</span><span class="tag" role="listitem">Seed-Reproducible</span><span class="tag" role="listitem">P / R / F1 Grading</span></div>\n\n<div class="card">\n<h2>Overview</h2>\n<div class="sg">\n<div class="s"><div class="n">17</div><div class="l">Tasks</div></div>\n<div class="s"><div class="n">5</div><div class="l">Doc Types</div></div>\n<div class="s"><div class="n">3</div><div class="l">Tiers</div></div>\n<div class="s"><div class="n">9</div><div class="l">Corruption Modes</div></div>\n</div>\n</div>\n\n<div class="card">\n<h2>Corruption Engine</h2>\n<p style="color:#a1a1aa;font-size:0.8125rem">Global + targeted field corruption. Scales with difficulty. Seed-reproducible.</p>\n<div class="cx" role="figure" aria-label="Corruption example showing OCR artifacts"><span style="color:#71717a">Original:</span>  Thornfield &amp; Associates LLP, Invoice TF/2026/0339\n<span style="color:#a1a1aa">Corrupted:</span> <mark>Thornfie1d</mark> &amp; Associates LLP, Invoice TF/<mark>Z0Z6</mark>/<mark>O</mark>339\n           <mark>[REDACTED]</mark> attention of: James Whit<mark>rn</mark>ore</div>\n<div class="ms" role="list"><span class="m" role="listitem">OCR swaps</span><span class="m" role="listitem">Redaction</span><span class="m" role="listitem">Whitespace</span><span class="m" role="listitem">Line breaks</span><span class="m" role="listitem">Contradictions</span><span class="m" role="listitem">Phone digits</span><span class="m" role="listitem">Email OCR</span><span class="m" role="listitem">Amount shift</span><span class="m" role="listitem">Seeded</span></div>\n</div>\n\n<div class="card">\n<h2>Tasks</h2>\n<div class="tl" role="list">\n<div class="tk" role="listitem"><span class="nm">Contact Extraction</span><span class="badge badge-easy">Easy</span><span class="fl">4 tasks · 6 fields</span></div>\n<div class="tk" role="listitem"><span class="nm">Support Tickets</span><span class="badge badge-easy">Easy</span><span class="fl">2 tasks · 10 fields</span></div>\n<div class="tk" role="listitem"><span class="nm">Job Postings</span><span class="badge badge-medium">Medium</span><span class="fl">4 tasks · 12 fields</span></div>\n<div class="tk" role="listitem"><span class="nm">Receipts</span><span class="badge badge-medium">Medium</span><span class="fl">3 tasks · 13 fields</span></div>\n<div class="tk" role="listitem"><span class="nm">Invoices / POs</span><span class="badge badge-hard">Hard</span><span class="fl">4 tasks · 15+ fields</span></div>\n</div>\n</div>\n\n<div class="card">\n<h2>Grading</h2>\n<div class="gf">\n<div class="gi"><div class="gl">Strings</div><div class="gv">Jaccard + Levenshtein</div></div>\n<div class="gi"><div class="gl">Metrics</div><div class="gv">P / R / F1</div></div>\n<div class="gi"><div class="gl">Nested</div><div class="gv">Greedy Alignment</div></div>\n<div class="gi"><div class="gl">Attempts</div><div class="gv">5 with Feedback</div></div>\n</div>\n</div>\n\n<div class="card">\n<h2>API</h2>\n<div class="eps" role="list">\n<div class="ep" role="listitem"><b class="mc-get">GET</b><span class="pa">/health</span><span class="de">Health check</span></div>\n<div class="ep" role="listitem"><b class="mc-get">GET</b><span class="pa">/tasks</span><span class="de">List all tasks</span></div>\n<div class="ep" role="listitem"><b class="mc-get">GET</b><span class="pa">/metrics</span><span class="de">Performance stats</span></div>\n<div class="ep" role="listitem"><b class="mc-post">POST</b><span class="pa">/reset</span><span class="de">Reset episode</span></div>\n<div class="ep" role="listitem"><b class="mc-post">POST</b><span class="pa">/step</span><span class="de">Submit extraction</span></div>\n<div class="ep" role="listitem"><b class="mc-get">GET</b><span class="pa">/state</span><span class="de">Episode state</span></div>\n<div class="ep" role="listitem"><b class="mc-ws">WS</b><span class="pa">/ws</span><span class="de">OpenEnv protocol</span></div>\n</div>\n</div>\n\n<div class="card">\n<h2>Try It Live</h2>\n<div style="display:flex;gap:8px;margin-bottom:14px;flex-wrap:wrap;align-items:center">\n<label for="ts" class="sr-only" style="position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0,0,0,0)">Select task</label>\n<select id="ts" aria-label="Select a task to load"><option value="">Random</option><option value="contact_01">contact_01 (Easy)</option><option value="ticket_01">ticket_01 (Easy)</option><option value="job_01">job_01 (Medium)</option><option value="receipt_01">receipt_01 (Medium)</option><option value="invoice_01">invoice_01 (Hard)</option></select>\n<button class="btn bb" onclick="doR()" aria-label="Load selected task">Load Task</button>\n<button class="btn bg" onclick="doS()" aria-label="Submit JSON extraction">Submit</button>\n</div>\n<div id="dp" style="display:none">\n<div style="display:flex;align-items:center;gap:8px;margin-bottom:10px"><span class="badge" id="db"></span><span style="color:#a1a1aa;font-size:0.8125rem;font-weight:500" id="tl"></span></div>\n<p style="color:#a1a1aa;font-size:0.8125rem;margin-bottom:6px"><strong style="color:#d4d4d8">Schema:</strong> <span id="st"></span></p>\n<div class="rtb" id="rt" role="region" aria-label="Document text" tabindex="0"></div>\n<label for="ji" style="position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0,0,0,0)">JSON extraction input</label>\n<textarea id="ji" rows="5" placeholder=\'{"name": "...", "email": "..."}\' aria-label="Enter your JSON extraction"></textarea>\n<p class="hint">Paste JSON and click Submit to see field-level scores.</p>\n<div id="fb" class="fb" role="status" aria-live="polite"><div id="fs" class="fbs"></div><div id="ft2" class="fbt"></div></div>\n</div>\n</div>\n\n<footer class="ft">DocForge &mdash; Built for the <a href="https://meta-pytorch.org/OpenEnv/">OpenEnv</a> Hackathon</footer>\n</div>\n<script>\nasync function doR(){const t=document.getElementById(\'ts\').value,b=t?{task_id:t}:{};try{const r=await fetch(\'/reset\',{method:\'POST\',headers:{\'Content-Type\':\'application/json\'},body:JSON.stringify(b)}),d=await r.json(),o=d.observation;document.getElementById(\'dp\').style.display=\'block\';document.getElementById(\'rt\').textContent=o.raw_text;document.getElementById(\'st\').textContent=o.schema_description;document.getElementById(\'tl\').textContent=o.task_id+\' \\u2022 \'+o.steps_remaining+\' steps\';const e=document.getElementById(\'db\');e.textContent=o.difficulty[0].toUpperCase()+o.difficulty.slice(1);e.className=\'badge badge-\'+o.difficulty;document.getElementById(\'fb\').style.display=\'none\';document.getElementById(\'ji\').value=\'\';}catch(e){alert(e.message);}}\nasync function doS(){const j=document.getElementById(\'ji\').value;if(!j)return alert(\'Enter JSON\');try{const r=await fetch(\'/step\',{method:\'POST\',headers:{\'Content-Type\':\'application/json\'},body:JSON.stringify({extracted_json:j})}),d=await r.json();if(d.detail)return alert(d.detail);const o=d.observation,f=document.getElementById(\'fb\');f.style.display=\'block\';const s=document.getElementById(\'fs\');s.textContent=(o.score*100).toFixed(1)+\'%\';s.style.color=o.score>.8?\'#4ade80\':o.score>.5?\'#fde047\':\'#fca5a5\';document.getElementById(\'ft2\').textContent=o.feedback;document.getElementById(\'tl\').textContent=o.task_id+\' \\u2022 \'+o.steps_remaining+\' steps\'+(d.done?\' \\u2022 DONE\':\'\');}catch(e){alert(e.message);}}\n</script>\n</body>\n</html>')

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
    obs, reward, done, info = env.reset(task_id=req.task_id, difficulty=req.difficulty, seed=req.seed)
    return EnvResponse(observation=asdict(obs), reward=reward, done=done, info=info)

@app.post("/step", response_model=EnvResponse)
def step(req: StepRequest):
    env = _get_env()
    if not env.state.task_id:
        raise HTTPException(status_code=400, detail="Call /reset before /step")
    if len(req.extracted_json) > 50000:
        raise HTTPException(status_code=400, detail="Payload too large (max 50KB)")
    obs, reward, done, info = env.step(DataExtractAction(extracted_json=req.extracted_json))
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
