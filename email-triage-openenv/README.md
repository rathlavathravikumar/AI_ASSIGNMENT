---
title: Email Triage OpenEnv
emoji: 📧
colorFrom: blue
colorTo: indigo
sdk: docker
pinned: true
tags:
  - openenv
  - email
  - triage
  - agent-evaluation
  - nlp
  - reinforcement-learning
license: mit
---

<div align="center">

# 📧 Email Triage OpenEnv

**A real-world email triage environment for evaluating AI agents**

[![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![OpenEnv](https://img.shields.io/badge/OpenEnv-Compliant-orange)](https://github.com/openenv)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Gradio](https://img.shields.io/badge/Gradio-Demo-FF7C00?logo=gradio)](https://gradio.app)
[![HF Space](https://img.shields.io/badge/HuggingFace-Space-yellow?logo=huggingface)](https://huggingface.co/spaces)

*Built for the **Meta OpenEnv Hackathon***

</div>

---

## Overview

**Email Triage OpenEnv** simulates the real-world challenge of professional inbox management — one of the most universal, high-stakes tasks humans perform daily. AI agents must classify priority, detect spam, flag urgent issues, archive newsletters, handle email threads, and draft replies — exactly as a skilled professional would.

```
┌─────────────────────────────────────────────────────────────┐
│                    Email Triage OpenEnv                     │
│                                                             │
│  Agent ──► Action ──► Environment ──► Observation          │
│                            │                               │
│                            ▼                               │
│                     Reward Signal                          │
│              (incremental, step-by-step)                   │
│                            │                               │
│                            ▼                               │
│                 Grader (0.0 – 1.0 score)                   │
└─────────────────────────────────────────────────────────────┘
```

---

## Why Email Triage?

| Challenge | Real-World Impact |
|-----------|-----------------|
| Missing an urgent email | Production outage, SLA breach |
| Deleting a client email | Lost revenue, legal risk |
| Ignoring a security alert | Data breach |
| Poor thread management | Executive time wasted |

This makes email triage a **meaningful, reproducible benchmark** — agents can be measured on correctness, and humans understand what the right answer looks like.

---

## Tasks

### Task 1 — Priority Inbox Classifier `[Easy]`

> 10 emails · Max 40 steps

Classify each email with the correct **priority** (`urgent`/`normal`/`low`) and **category** (`work`/`personal`/`spam`/`newsletter`/`finance`/`support`). Identify emails that need flagging and those that require replies.

**Scoring weights:**
| Criterion | Weight |
|-----------|--------|
| Priority accuracy | 30% |
| Category accuracy | 35% |
| Flag accuracy | 20% |
| Reply identification | 15% |

**Baseline score:** `0.41`

---

### Task 2 — Inbox Zero Challenge `[Medium]`

> 20 emails · Max 80 steps

Process all 20 emails to achieve **Inbox Zero**. Take the correct action per email: delete spam, archive newsletters and digests, flag urgent work items, classify everything.

**Scoring weights:**
| Criterion | Weight |
|-----------|--------|
| Action correctness | 40% |
| Category accuracy | 25% |
| Priority accuracy | 20% |
| Coverage (% processed) | 15% |

**Baseline score:** `0.35`

---

### Task 3 — Executive Assistant Email Management `[Hard]`

> 20 emails · Max 100 steps

Act as a CEO's AI executive assistant. Handle **email threads** coherently, detect **duplicate/FYI emails**, flag executive-action items with correct urgency, identify emails needing **drafted replies**, and classify everything accurately.

**Scoring weights:**
| Criterion | Weight |
|-----------|--------|
| Action correctness | 40% |
| Thread management | 20% |
| Reply identification | 15% |
| Classification accuracy | 15% |
| Duplicate detection | 10% |

**Baseline score:** `0.28`

---

## Observation Space

Each step, the agent receives a structured `Observation` object:

```python
class Observation(BaseModel):
    task_id: str                          # "task_1" | "task_2" | "task_3"
    task_description: str                 # Natural language objective
    difficulty: str                       # "easy" | "medium" | "hard"
    inbox: List[Email]                    # All emails in the inbox
    step_count: int                       # Steps taken so far
    max_steps: int                        # Step budget
    classifications: Dict[str, Any]       # Agent's classifications so far
    flagged: Dict[str, str]               # email_id → flag_type
    archived: List[str]                   # Archived email IDs
    deleted: List[str]                    # Deleted email IDs
    replies: Dict[str, str]               # email_id → reply body
    total_reward: float                   # Cumulative reward
    done: bool                            # Episode complete?
    message: str                          # Feedback from last action
```

---

## Action Space

```python
class Action(BaseModel):
    action_type: ActionType               # Required

    # Target email (most actions)
    email_id: Optional[str]

    # classify
    priority: Optional[Priority]          # urgent | normal | low
    category: Optional[Category]          # work | personal | spam | newsletter | finance | support

    # flag
    flag_type: Optional[FlagType]         # urgent | follow_up | waiting | action_required

    # reply
    reply_body: Optional[str]             # min 10 chars

    # search
    search_query: Optional[str]
```

| Action | Required Params | Description |
|--------|----------------|-------------|
| `classify` | `email_id`, `priority`, `category` | Label email priority and category |
| `archive` | `email_id` | Archive low-value email |
| `delete` | `email_id` | Delete spam / junk |
| `flag` | `email_id`, `flag_type` | Flag urgent or action-required email |
| `reply` | `email_id`, `reply_body` | Draft a reply |
| `mark_read` | `email_id` | Mark as read |
| `search` | `search_query` | Search inbox by keyword |
| `done` | — | Signal task completion |

---

## Reward Function

Dense, incremental feedback at **every step** — not just at completion:

| Event | Reward |
|-------|--------|
| Correct primary action (archive/delete/flag) | `+0.08` |
| Correct priority in classify | `+0.02` |
| Correct category in classify | `+0.02` |
| Correct flag type | `+0.02` |
| Reply drafted for email that needs it | `+0.06` |
| Invalid / malformed action | `−0.02` |
| Repeated identical action (loop detection) | `−0.05` |
| Deleting an important non-spam email | `−0.05` |
| Max steps exceeded | `−0.10` |
| Task completion bonus | `+0.10 + 0.20 × final_score` |

---

## Baseline Performance

Evaluated using `meta-llama/Llama-3.1-8B-Instruct` via Hugging Face Inference API:

| Task | Difficulty | Score |
|------|-----------|-------|
| Task 1 — Priority Inbox Classifier | Easy | `0.41` |
| Task 2 — Inbox Zero Challenge | Medium | `0.35` |
| Task 3 — Executive Assistant | Hard | `0.28` |
| **Average** | — | **`0.35`** |

---

## Setup & Usage

### Local Development

```bash
# Clone
git clone https://github.com/rathlavathravikumar/AI_ASSIGNMENT.git
cd AI_ASSIGNMENT/email-triage-openenv

# Install
pip install -r requirements.txt

# Run server (Gradio UI + REST API)
python app.py
# → http://localhost:7860
# → API docs at http://localhost:7860/api/docs
```

### Docker

```bash
# Build
docker build -t email-triage-openenv .

# Run
docker run -p 7860:7860 email-triage-openenv
```

### Python SDK

```python
from env import EmailTriageEnv, Action, ActionType, Priority, Category, FlagType

env = EmailTriageEnv()

# Reset to any task
obs = env.reset(task_id="task_1")  # or task_2, task_3
print(f"Inbox: {len(obs.inbox)} emails")

# Take actions
obs, reward, done, info = env.step(Action(
    action_type=ActionType.CLASSIFY,
    email_id="e01",
    priority=Priority.URGENT,
    category=Category.WORK,
))
print(f"Reward: {reward.value:+.4f} — {reward.reason}")

obs, reward, done, info = env.step(Action(
    action_type=ActionType.FLAG,
    email_id="e01",
    flag_type=FlagType.URGENT,
))

# Finish and evaluate
env.step(Action(action_type=ActionType.DONE))
scores = env.evaluate()
print(f"Final score: {scores['total_score']:.4f}")
```

### REST API

```bash
# Reset
curl -X POST http://localhost:7860/api/reset \
  -H "Content-Type: application/json" \
  -d '{"task_id": "task_1"}'

# Step
curl -X POST http://localhost:7860/api/step \
  -H "Content-Type: application/json" \
  -d '{"action": {"action_type": "classify", "email_id": "e01", "priority": "urgent", "category": "work"}}'

# Evaluate
curl -X POST http://localhost:7860/api/evaluate
```

### Baseline Inference

```bash
export HF_TOKEN=your_huggingface_token

# All tasks
python inference.py

# Specific task
python inference.py --task task_2

# Custom model
python inference.py --model meta-llama/Llama-3.1-70B-Instruct

# Results → baseline_results.json
```

### Run Tests

```bash
pip install pytest
pytest tests/ -v
```

---

## OpenEnv Compliance Checklist

- [x] `reset(task_id)` → `Observation`
- [x] `step(action)` → `(Observation, Reward, done, info)`
- [x] `state()` → `dict`
- [x] Typed `Observation`, `Action`, `Reward` models via Pydantic
- [x] `openenv.yaml` metadata file
- [x] Minimum 3 tasks with programmatic graders
- [x] Scores in `[0.0, 1.0]`
- [x] Incremental reward function (feedback every step)
- [x] Loop / destructive-action penalties
- [x] Baseline inference script using OpenAI API client
- [x] `HF_TOKEN` read from environment variable
- [x] Reproducible baseline scores
- [x] Deployable Dockerfile (HF Spaces Docker compatible)
- [x] Tagged with `openenv`
- [x] Interactive demo (Gradio)
- [x] Full test suite

---

## Project Structure

```
email-triage-openenv/
├── app.py              # FastAPI + Gradio server (HF Spaces entry point)
├── inference.py        # Baseline inference script (OpenAI client + HF_TOKEN)
├── openenv.yaml        # OpenEnv specification metadata
├── Dockerfile          # Container definition (HF Spaces compatible)
├── requirements.txt    # Python dependencies
├── LICENSE             # MIT License
├── README.md           # This file
├── tests/
│   └── test_env.py     # Unit test suite (pytest)
└── env/
    ├── __init__.py     # Package exports
    ├── models.py       # Pydantic models: Action, Observation, Reward, Email, ...
    ├── tasks.py        # Task definitions, email datasets, graders
    └── environment.py  # EmailTriageEnv class (full OpenEnv interface)
```

---

## License

MIT License — see [LICENSE](LICENSE) for details.
