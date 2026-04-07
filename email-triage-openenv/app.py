"""
FastAPI application for the Email Triage OpenEnv.
Deployable on Hugging Face Spaces as a Docker Space.

Endpoints:
  POST /reset          — reset environment for a task
  POST /step           — take an action
  GET  /state          — get current internal state
  POST /evaluate       — run the grader and return score
  GET  /tasks          — list available tasks
  GET  /health         — health check
"""

from __future__ import annotations

import os
from typing import Any, Dict, Optional

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from env import EmailTriageEnv, Action, TASKS

# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Email Triage OpenEnv",
    description=(
        "A real-world email triage environment for evaluating AI agents. "
        "Agents classify, prioritize, flag, archive, delete, and reply to emails. "
        "Three tasks of increasing difficulty: easy, medium, hard."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global environment instance
_env = EmailTriageEnv()

# ---------------------------------------------------------------------------
# Request/Response schemas
# ---------------------------------------------------------------------------

class ResetRequest(BaseModel):
    task_id: str = "task_1"


class StepRequest(BaseModel):
    action: Action


class ResetResponse(BaseModel):
    observation: Dict[str, Any]
    message: str


class StepResponse(BaseModel):
    observation: Dict[str, Any]
    reward: Dict[str, Any]
    done: bool
    info: Dict[str, Any]


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/", response_class=HTMLResponse, tags=["UI"])
async def index():
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Email Triage OpenEnv</title>
        <style>
            body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                   max-width: 900px; margin: 60px auto; padding: 0 20px; color: #1a1a2e; }
            h1 { color: #16213e; border-bottom: 3px solid #0f3460; padding-bottom: 10px; }
            h2 { color: #0f3460; margin-top: 30px; }
            .badge { display:inline-block; background:#e94560; color:white;
                     padding:3px 10px; border-radius:12px; font-size:0.8em; margin:2px; }
            .badge.easy { background:#27ae60; }
            .badge.medium { background:#e67e22; }
            .badge.hard { background:#e74c3c; }
            .card { border:1px solid #ddd; border-radius:8px; padding:16px; margin:10px 0;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.06); }
            code { background:#f4f4f8; padding:2px 6px; border-radius:4px; font-family:monospace; }
            a { color:#0f3460; }
            table { border-collapse:collapse; width:100%; margin-top:10px; }
            th, td { border:1px solid #ddd; padding:8px 12px; text-align:left; }
            th { background:#f4f4f8; }
            pre { background:#f4f4f8; padding:16px; border-radius:8px; overflow-x:auto; }
        </style>
    </head>
    <body>
        <h1>Email Triage OpenEnv</h1>
        <p>A <strong>real-world email triage environment</strong> for evaluating AI agents on
        realistic workplace email management tasks. Built for the Meta OpenEnv Hackathon.</p>

        <h2>Tasks</h2>
        <div class="card">
            <span class="badge easy">Easy</span> <strong>Task 1 — Priority Inbox Classifier</strong><br/>
            10 emails &middot; Classify priority + category for each email &middot; Max 40 steps
        </div>
        <div class="card">
            <span class="badge medium">Medium</span> <strong>Task 2 — Inbox Zero Challenge</strong><br/>
            20 emails &middot; Archive / delete / flag every email correctly &middot; Max 80 steps
        </div>
        <div class="card">
            <span class="badge hard">Hard</span> <strong>Task 3 — Executive Assistant Email Management</strong><br/>
            20 emails &middot; Thread management, duplicate detection, reply drafting &middot; Max 100 steps
        </div>

        <h2>Action Space</h2>
        <table>
            <tr><th>Action</th><th>Parameters</th><th>Description</th></tr>
            <tr><td><code>classify</code></td><td>email_id, priority, category</td><td>Classify an email's priority and category</td></tr>
            <tr><td><code>archive</code></td><td>email_id</td><td>Archive a low-value email</td></tr>
            <tr><td><code>delete</code></td><td>email_id</td><td>Delete spam or junk email</td></tr>
            <tr><td><code>flag</code></td><td>email_id, flag_type</td><td>Flag urgent/action-required emails</td></tr>
            <tr><td><code>reply</code></td><td>email_id, reply_body</td><td>Draft a reply to an email</td></tr>
            <tr><td><code>mark_read</code></td><td>email_id</td><td>Mark email as read</td></tr>
            <tr><td><code>search</code></td><td>search_query</td><td>Search inbox by keyword</td></tr>
            <tr><td><code>done</code></td><td>—</td><td>Signal task completion</td></tr>
        </table>

        <h2>Quick Start</h2>
        <pre><code># 1. Reset environment
POST /reset  {"task_id": "task_1"}

# 2. Take actions
POST /step   {"action": {"action_type": "classify", "email_id": "e01",
                          "priority": "urgent", "category": "work"}}

# 3. Evaluate
POST /evaluate</code></pre>

        <p>
            <a href="/docs">Interactive API Docs (Swagger)</a> &middot;
            <a href="/redoc">ReDoc</a> &middot;
            <a href="/tasks">Task List (JSON)</a>
        </p>
    </body>
    </html>
    """
    return HTMLResponse(content=html)


@app.get("/health", tags=["System"])
async def health():
    return {"status": "ok", "version": "1.0.0"}


@app.get("/tasks", tags=["Environment"])
async def list_tasks():
    return {
        task_id: {
            "name": cfg["name"],
            "difficulty": cfg["difficulty"],
            "description": cfg["description"],
            "num_emails": len(cfg["emails"]),
            "max_steps": cfg["max_steps"],
        }
        for task_id, cfg in TASKS.items()
    }


@app.post("/reset", response_model=ResetResponse, tags=["Environment"])
async def reset(request: ResetRequest):
    try:
        obs = _env.reset(task_id=request.task_id)
        return ResetResponse(
            observation=obs.dict(),
            message=f"Environment reset for task '{request.task_id}'.",
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/step", response_model=StepResponse, tags=["Environment"])
async def step(request: StepRequest):
    try:
        obs, reward, done, info = _env.step(request.action)
        return StepResponse(
            observation=obs.dict(),
            reward=reward.dict(),
            done=done,
            info=info,
        )
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/state", tags=["Environment"])
async def get_state():
    return _env.state()


@app.post("/evaluate", tags=["Environment"])
async def evaluate():
    try:
        scores = _env.evaluate()
        return {"scores": scores, "final_score": scores.get("total_score", 0.0)}
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/emails/{task_id}", tags=["Environment"])
async def get_emails(task_id: str):
    if task_id not in TASKS:
        raise HTTPException(status_code=404, detail=f"Task '{task_id}' not found.")
    emails = TASKS[task_id]["emails"]
    return {"task_id": task_id, "emails": [e.dict() for e in emails]}


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=False)
