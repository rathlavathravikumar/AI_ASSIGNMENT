"""
Email Triage OpenEnv — Main Application
Runs a FastAPI REST API + Gradio interactive demo on a single server.
Compatible with Hugging Face Spaces (Docker).
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional, Tuple

import gradio as gr
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from env import EmailTriageEnv, Action, ActionType, Category, FlagType, Priority, TASKS

# ---------------------------------------------------------------------------
# FastAPI backend
# ---------------------------------------------------------------------------

api = FastAPI(
    title="Email Triage OpenEnv API",
    description="OpenEnv-compliant REST API for the Email Triage environment.",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

api.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)

_env = EmailTriageEnv()


class ResetRequest(BaseModel):
    task_id: str = "task_1"


class StepRequest(BaseModel):
    action: Action


@api.get("/api/health")
async def health():
    return {"status": "ok", "version": "1.0.0"}


@api.get("/api/tasks")
async def list_tasks():
    return {
        tid: {
            "name": cfg["name"],
            "difficulty": cfg["difficulty"],
            "description": cfg["description"],
            "num_emails": len(cfg["emails"]),
            "max_steps": cfg["max_steps"],
        }
        for tid, cfg in TASKS.items()
    }


@api.post("/api/reset")
async def reset(req: ResetRequest):
    try:
        obs = _env.reset(task_id=req.task_id)
        return {"observation": obs.dict(), "message": f"Reset to {req.task_id}"}
    except ValueError as e:
        raise HTTPException(400, str(e))


@api.post("/api/step")
async def step(req: StepRequest):
    try:
        obs, reward, done, info = _env.step(req.action)
        return {"observation": obs.dict(), "reward": reward.dict(), "done": done, "info": info}
    except RuntimeError as e:
        raise HTTPException(400, str(e))


@api.get("/api/state")
async def get_state():
    return _env.state()


@api.post("/api/evaluate")
async def evaluate():
    try:
        scores = _env.evaluate()
        return {"scores": scores, "final_score": scores.get("total_score", 0.0)}
    except RuntimeError as e:
        raise HTTPException(400, str(e))


@api.get("/api/emails/{task_id}")
async def get_emails(task_id: str):
    if task_id not in TASKS:
        raise HTTPException(404, f"Task '{task_id}' not found.")
    return {"task_id": task_id, "emails": [e.dict() for e in TASKS[task_id]["emails"]]}


# ---------------------------------------------------------------------------
# Gradio interactive demo
# ---------------------------------------------------------------------------

# Per-session environment for Gradio (stateful)
_demo_env = EmailTriageEnv()
_demo_obs: Dict[str, Any] = {}


def _inbox_to_rows(obs: Dict[str, Any]) -> List[List[str]]:
    """Convert inbox emails to table rows for display."""
    inbox = obs.get("inbox", [])
    classified = obs.get("classifications", {})
    flagged = obs.get("flagged", {})
    archived = set(obs.get("archived", []))
    deleted = set(obs.get("deleted", []))
    replies = obs.get("replies", {})

    rows = []
    for e in inbox:
        eid = e["id"]
        status_parts = []
        if eid in deleted:
            status_parts.append("DELETED")
        elif eid in archived:
            status_parts.append("ARCHIVED")
        if eid in flagged:
            status_parts.append(f"FLAGGED:{flagged[eid]}")
        if eid in classified:
            c = classified[eid]
            status_parts.append(f"{c.get('priority','?')}/{c.get('category','?')}")
        if eid in replies:
            status_parts.append("REPLIED")
        status = " | ".join(status_parts) if status_parts else "Unprocessed"

        rows.append([
            eid,
            e["sender"],
            e["subject"][:55] + ("..." if len(e["subject"]) > 55 else ""),
            e["timestamp"][:10],
            status,
        ])
    return rows


def demo_reset(task_id: str):
    global _demo_obs
    obs = _demo_env.reset(task_id)
    _demo_obs = obs.dict()
    rows = _inbox_to_rows(_demo_obs)
    info = (
        f"**Task:** {_demo_obs['task_description'][:120]}...\n\n"
        f"**Emails:** {len(_demo_obs['inbox'])} | "
        f"**Max Steps:** {_demo_obs['max_steps']} | "
        f"**Difficulty:** {_demo_obs['difficulty'].upper()}"
    )
    return rows, info, "0", "0.0000", "", _inbox_email_ids()


def _inbox_email_ids() -> List[str]:
    return [e["id"] for e in _demo_obs.get("inbox", [])]


def demo_step(action_type: str, email_id: str, priority: str, category: str,
              flag_type: str, reply_body: str, search_query: str):
    global _demo_obs

    if not _demo_obs:
        return [], "Please reset the environment first.", "0", "0.0000", "No action taken.", []

    # Build action
    atype = ActionType(action_type)
    kwargs: Dict[str, Any] = {"action_type": atype}

    if atype in (ActionType.CLASSIFY, ActionType.ARCHIVE, ActionType.DELETE,
                 ActionType.FLAG, ActionType.REPLY, ActionType.MARK_READ):
        kwargs["email_id"] = email_id or None

    if atype == ActionType.CLASSIFY:
        if priority:
            kwargs["priority"] = Priority(priority)
        if category:
            kwargs["category"] = Category(category)

    if atype == ActionType.FLAG and flag_type:
        kwargs["flag_type"] = FlagType(flag_type)

    if atype == ActionType.REPLY:
        kwargs["reply_body"] = reply_body

    if atype == ActionType.SEARCH:
        kwargs["search_query"] = search_query

    try:
        action = Action(**kwargs)
        obs, reward, done, info = _demo_env.step(action)
        _demo_obs = obs.dict()
    except Exception as exc:
        return (
            _inbox_to_rows(_demo_obs),
            f"**Error:** {exc}",
            str(_demo_obs.get("step_count", 0)),
            f"{_demo_obs.get('total_reward', 0.0):.4f}",
            f"Error: {exc}",
            _inbox_email_ids(),
        )

    rows = _inbox_to_rows(_demo_obs)
    task_info = (
        f"**Step {_demo_obs['step_count']}/{_demo_obs['max_steps']}** | "
        f"**Done:** {'Yes' if done else 'No'}"
    )

    feedback = (
        f"**Reward:** `{reward.value:+.4f}`\n\n"
        f"**Message:** {reward.reason}\n\n"
        f"**Cumulative Reward:** `{_demo_obs['total_reward']:.4f}`"
    )

    if done:
        try:
            scores = _demo_env.evaluate()
            feedback += (
                f"\n\n---\n**FINAL SCORE: `{scores['total_score']:.4f}`**\n\n"
                + "\n".join(
                    f"- {k.replace('_', ' ').title()}: `{v:.4f}`"
                    for k, v in scores.items()
                    if k != "total_score"
                )
            )
        except Exception:
            pass

    return (
        rows,
        task_info,
        str(_demo_obs["step_count"]),
        f"{_demo_obs['total_reward']:.4f}",
        feedback,
        _inbox_email_ids(),
    )


def demo_evaluate():
    if not _demo_obs:
        return "Reset the environment first."
    try:
        scores = _demo_env.evaluate()
        lines = [f"### Final Score: `{scores['total_score']:.4f}`\n"]
        for k, v in scores.items():
            if k != "total_score":
                lines.append(f"- **{k.replace('_', ' ').title()}:** `{v:.4f}`")
        return "\n".join(lines)
    except Exception as exc:
        return f"Error: {exc}"


CSS = """
.header { text-align: center; margin-bottom: 20px; }
.score-box { font-size: 1.4em; font-weight: bold; color: #2563eb; }
.feedback-box { background: #f8fafc; border-left: 4px solid #2563eb;
                padding: 12px; border-radius: 4px; }
footer { display: none !important; }
"""

TASK_OPTIONS = [
    ("Task 1 — Priority Inbox Classifier [Easy]", "task_1"),
    ("Task 2 — Inbox Zero Challenge [Medium]", "task_2"),
    ("Task 3 — Executive Assistant [Hard]", "task_3"),
]

ACTION_OPTIONS = [a.value for a in ActionType]
PRIORITY_OPTIONS = ["", "urgent", "normal", "low"]
CATEGORY_OPTIONS = ["", "work", "personal", "spam", "newsletter", "finance", "support"]
FLAG_OPTIONS = ["", "urgent", "follow_up", "waiting", "action_required"]


def build_gradio_app() -> gr.Blocks:
    with gr.Blocks(css=CSS, title="Email Triage OpenEnv") as demo:

        gr.Markdown(
            """
# Email Triage OpenEnv
**Real-world email management environment for AI agent evaluation**

---
            """,
            elem_classes="header",
        )

        with gr.Tabs():

            # ----------------------------------------------------------------
            # Tab 1: Interactive Demo
            # ----------------------------------------------------------------
            with gr.Tab("Interactive Demo"):
                with gr.Row():
                    task_dropdown = gr.Dropdown(
                        choices=TASK_OPTIONS, value="task_1",
                        label="Select Task", scale=3,
                    )
                    reset_btn = gr.Button("Reset Environment", variant="primary", scale=1)

                task_info_md = gr.Markdown("_Select a task and click Reset to start._")

                inbox_table = gr.Dataframe(
                    headers=["ID", "From", "Subject", "Date", "Status"],
                    datatype=["str", "str", "str", "str", "str"],
                    label="Inbox",
                    interactive=False,
                    wrap=True,
                )

                gr.Markdown("### Take an Action")
                with gr.Row():
                    action_type_dd = gr.Dropdown(
                        choices=ACTION_OPTIONS, value="classify",
                        label="Action Type", scale=2,
                    )
                    email_id_dd = gr.Dropdown(
                        choices=[], label="Email ID", scale=2,
                    )
                    priority_dd = gr.Dropdown(
                        choices=PRIORITY_OPTIONS, value="",
                        label="Priority", scale=1,
                    )
                    category_dd = gr.Dropdown(
                        choices=CATEGORY_OPTIONS, value="",
                        label="Category", scale=1,
                    )
                    flag_type_dd = gr.Dropdown(
                        choices=FLAG_OPTIONS, value="",
                        label="Flag Type", scale=1,
                    )

                with gr.Row():
                    reply_body_tb = gr.Textbox(
                        label="Reply Body (for reply action)", lines=2, scale=3,
                    )
                    search_query_tb = gr.Textbox(
                        label="Search Query (for search action)", lines=2, scale=2,
                    )

                with gr.Row():
                    step_btn = gr.Button("Submit Action", variant="primary", scale=2)
                    evaluate_btn = gr.Button("Evaluate Final Score", scale=1)

                with gr.Row():
                    step_count_box = gr.Textbox(label="Steps Used", value="0",
                                                interactive=False, scale=1)
                    total_reward_box = gr.Textbox(label="Total Reward", value="0.0000",
                                                  interactive=False, scale=1)

                feedback_md = gr.Markdown(
                    "_Action feedback will appear here._",
                    elem_classes="feedback-box",
                )
                score_md = gr.Markdown("", label="Score")

            # ----------------------------------------------------------------
            # Tab 2: API Reference
            # ----------------------------------------------------------------
            with gr.Tab("API Reference"):
                gr.Markdown("""
## REST API Endpoints

The environment also exposes a full REST API at `/api/`:

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/health` | Health check |
| `GET` | `/api/tasks` | List all tasks |
| `POST` | `/api/reset` | Reset environment for a task |
| `POST` | `/api/step` | Take an action |
| `GET` | `/api/state` | Get full internal state |
| `POST` | `/api/evaluate` | Run grader, get score |
| `GET` | `/api/emails/{task_id}` | List emails for a task |

**Interactive Swagger docs:** [/api/docs](/api/docs)

---

## Example Usage

```python
import requests

BASE = "https://your-hf-space.hf.space"

# Reset
obs = requests.post(f"{BASE}/api/reset", json={"task_id": "task_1"}).json()

# Classify an email
step = requests.post(f"{BASE}/api/step", json={
    "action": {
        "action_type": "classify",
        "email_id": "e01",
        "priority": "urgent",
        "category": "work"
    }
}).json()
print(step["reward"])  # {"value": 0.06, "reason": "..."}

# Flag it
requests.post(f"{BASE}/api/step", json={
    "action": {"action_type": "flag", "email_id": "e01", "flag_type": "urgent"}
})

# Get final score
score = requests.post(f"{BASE}/api/evaluate").json()
print(score["final_score"])
```

---

## Baseline Inference

```bash
export HF_TOKEN=your_huggingface_token
python inference.py --task all --model meta-llama/Llama-3.1-8B-Instruct
```
                """)

            # ----------------------------------------------------------------
            # Tab 3: About
            # ----------------------------------------------------------------
            with gr.Tab("About"):
                gr.Markdown("""
## About This Environment

**Email Triage OpenEnv** is a real-world AI agent evaluation environment built for the
**Meta OpenEnv Hackathon**. It simulates the daily email management challenge faced by
professionals, where correct prioritization, filtering, and response directly impacts
business outcomes.

---

## Why Email Triage?

Email is one of the most **universal, high-stakes** real-world tasks:
- A missed urgent email can cause production outages or SLA breaches
- A mislabeled spam filter can delete important client communications
- Poor thread management wastes executive time

---

## Tasks at a Glance

| Task | Difficulty | Emails | Max Steps | Key Challenge |
|------|-----------|--------|-----------|---------------|
| Priority Inbox Classifier | Easy | 10 | 40 | Correct priority + category classification |
| Inbox Zero Challenge | Medium | 20 | 80 | Right action for every email (archive/delete/flag) |
| Executive Assistant | Hard | 20 | 100 | Thread management, duplicate detection, replies |

---

## Reward Design

The reward function provides **dense, incremental feedback** at every step — not just
at episode end. This enables credit assignment for RL training:

- **+0.08** — Correct primary action (archive/delete/flag)
- **+0.02** — Correct priority in classify
- **+0.02** — Correct category in classify
- **+0.02** — Correct flag type
- **+0.06** — Reply drafted for email that genuinely needs it
- **−0.02** — Invalid / malformed action
- **−0.05** — Repeated identical action (loop detection)
- **−0.05** — Deleting an important (non-spam) email

---

## Baseline Performance

Evaluated with `meta-llama/Llama-3.1-8B-Instruct` via HF Inference API:

| Task | Score |
|------|-------|
| Task 1 (Easy) | 0.41 |
| Task 2 (Medium) | 0.35 |
| Task 3 (Hard) | 0.28 |
| **Average** | **0.35** |

---

*Built with FastAPI · Gradio · Pydantic · Python 3.11*
                """)

        # --------------------------------------------------------------------
        # Event wiring
        # --------------------------------------------------------------------

        reset_btn.click(
            fn=demo_reset,
            inputs=[task_dropdown],
            outputs=[inbox_table, task_info_md, step_count_box, total_reward_box,
                     feedback_md, email_id_dd],
        )

        step_btn.click(
            fn=demo_step,
            inputs=[action_type_dd, email_id_dd, priority_dd, category_dd,
                    flag_type_dd, reply_body_tb, search_query_tb],
            outputs=[inbox_table, task_info_md, step_count_box, total_reward_box,
                     feedback_md, email_id_dd],
        )

        evaluate_btn.click(
            fn=demo_evaluate,
            inputs=[],
            outputs=[score_md],
        )

    return demo


# ---------------------------------------------------------------------------
# Mount Gradio onto FastAPI and run
# ---------------------------------------------------------------------------

gradio_app = build_gradio_app()
app = gr.mount_gradio_app(api, gradio_app, path="/")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=False, log_level="info")
