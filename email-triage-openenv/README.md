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
license: mit
---

# Email Triage OpenEnv

> A real-world email triage environment for evaluating AI agents — built for the **Meta OpenEnv Hackathon**.

AI agents must process realistic workplace emails: classifying priority, detecting spam, flagging urgent issues, archiving newsletters, and drafting replies — exactly as a human professional would.

---

## Motivation

Email management is one of the most universal, high-stakes, real-world tasks. A missed urgent email or a wrongly-deleted message can cost thousands of dollars or violate SLAs. This environment tests whether AI agents can:

- Understand email context and intent
- Prioritize correctly under time pressure
- Take the right action (archive vs. delete vs. flag vs. reply)
- Handle complex multi-email threads and duplicates

---

## Environment Overview

### Observation Space

Each step, the agent receives:

| Field | Type | Description |
|---|---|---|
| `inbox` | `List[Email]` | All emails in the inbox |
| `task_description` | `str` | Natural language task objective |
| `step_count` / `max_steps` | `int` | Step budget tracking |
| `classifications` | `dict` | Agent's classification results so far |
| `flagged` | `dict` | Flagged emails and their flag types |
| `archived` / `deleted` | `list` | Processed email IDs |
| `replies` | `dict` | Drafted reply bodies |
| `total_reward` | `float` | Cumulative reward |
| `message` | `str` | Feedback from last action |

### Action Space

| Action | Required Parameters | Description |
|---|---|---|
| `classify` | `email_id`, `priority`, `category` | Classify an email's priority and category |
| `archive` | `email_id` | Archive low-value email |
| `delete` | `email_id` | Delete spam / junk |
| `flag` | `email_id`, `flag_type` | Flag urgent or action-required email |
| `reply` | `email_id`, `reply_body` | Draft a reply (min 10 chars) |
| `mark_read` | `email_id` | Mark email as read |
| `search` | `search_query` | Search inbox by keyword |
| `done` | — | Signal task completion |

**Priority values:** `urgent` · `normal` · `low`

**Category values:** `work` · `personal` · `spam` · `newsletter` · `finance` · `support`

**Flag types:** `urgent` · `follow_up` · `waiting` · `action_required`

---

## Tasks

### Task 1 — Priority Inbox Classifier `[Easy]`

**Emails:** 10 | **Max steps:** 40

Classify each of 10 diverse emails with the correct priority and category. Identify which emails need flagging and which require replies.

**Scoring:**
- Priority accuracy: 30%
- Category accuracy: 35%
- Flag accuracy: 20%
- Reply identification: 15%

**Baseline score:** 0.41

---

### Task 2 — Inbox Zero Challenge `[Medium]`

**Emails:** 20 | **Max steps:** 80

Process all 20 emails to achieve Inbox Zero. Take the correct action for each: delete spam, archive newsletters, flag urgent work emails, and classify every message.

**Scoring:**
- Action correctness: 40%
- Category accuracy: 25%
- Priority accuracy: 20%
- Coverage (% processed): 15%

**Baseline score:** 0.35

---

### Task 3 — Executive Assistant Email Management `[Hard]`

**Emails:** 20 | **Max steps:** 100

Act as a CEO's AI executive assistant. Handle email threads coherently, detect duplicate/FYI emails, flag items requiring executive action, identify emails needing drafted replies, and classify all messages correctly.

**Scoring:**
- Action correctness: 40%
- Thread management: 20%
- Reply identification: 15%
- Classification accuracy: 15%
- Duplicate detection: 10%

**Baseline score:** 0.28

---

## Reward Function

The reward function provides **incremental feedback at every step**:

| Event | Reward |
|---|---|
| Correct action (archive/delete/flag right email) | `+0.08` |
| Correct priority in classify | `+0.02` |
| Correct category in classify | `+0.02` |
| Correct flag type | `+0.02` |
| Reply drafted for email that needs it | `+0.06` |
| Invalid action or missing parameters | `-0.02` |
| Repeated identical action (loop) | `-0.05` |
| Deleting an important email | `-0.05` |
| Max steps exceeded | `-0.10` |
| Task completion (DONE) | `+0.10 + 0.20 × final_score` |

---

## Baseline Performance

Evaluated using `meta-llama/Llama-3.1-8B-Instruct` via Hugging Face Inference API:

| Task | Difficulty | Score |
|---|---|---|
| Task 1 — Priority Inbox Classifier | Easy | 0.41 |
| Task 2 — Inbox Zero Challenge | Medium | 0.35 |
| Task 3 — Executive Assistant | Hard | 0.28 |
| **Average** | — | **0.35** |

---

## Setup & Usage

### Local Development

```bash
# Clone the repo
git clone <your-repo-url>
cd email-triage-openenv

# Install dependencies
pip install -r requirements.txt

# Start the server
python app.py
# Server runs at http://localhost:7860
```

### Docker

```bash
# Build
docker build -t email-triage-openenv .

# Run
docker run -p 7860:7860 email-triage-openenv

# With HF token for inference
docker run -p 7860:7860 -e HF_TOKEN=your_token email-triage-openenv
```

### API Usage

```python
import requests

BASE = "http://localhost:7860"

# 1. Reset environment
obs = requests.post(f"{BASE}/reset", json={"task_id": "task_1"}).json()

# 2. Classify an email
step = requests.post(f"{BASE}/step", json={
    "action": {
        "action_type": "classify",
        "email_id": "e01",
        "priority": "urgent",
        "category": "work"
    }
}).json()
print(step["reward"])  # {"value": 0.04, "reason": "..."}

# 3. Flag it
step = requests.post(f"{BASE}/step", json={
    "action": {"action_type": "flag", "email_id": "e01", "flag_type": "urgent"}
}).json()

# 4. Call done
step = requests.post(f"{BASE}/step", json={"action": {"action_type": "done"}}).json()

# 5. Evaluate
score = requests.post(f"{BASE}/evaluate").json()
print(score)  # {"final_score": 0.82, "scores": {...}}
```

### Run Baseline Inference

```bash
export HF_TOKEN=your_huggingface_token

# Run on all tasks
python inference.py

# Run on a specific task
python inference.py --task task_1

# Use a specific model
python inference.py --model meta-llama/Llama-3.1-70B-Instruct

# Results saved to baseline_results.json
```

### Direct Python Usage

```python
from env import EmailTriageEnv, Action, ActionType, Priority, Category, FlagType

env = EmailTriageEnv()

# Easy task
obs = env.reset(task_id="task_1")
print(obs.task_description)

# Take actions
action = Action(
    action_type=ActionType.CLASSIFY,
    email_id="e01",
    priority=Priority.URGENT,
    category=Category.WORK,
)
obs, reward, done, info = env.step(action)
print(f"Reward: {reward.value} — {reward.reason}")

# Get score
scores = env.evaluate()
print(f"Score: {scores['total_score']:.4f}")
```

---

## OpenEnv Compliance

This environment implements the full OpenEnv interface:

- [x] `reset(task_id)` → `Observation`
- [x] `step(action)` → `(Observation, Reward, done, info)`
- [x] `state()` → `dict`
- [x] Typed `Observation`, `Action`, `Reward` models via Pydantic
- [x] `openenv.yaml` metadata file
- [x] Minimum 3 tasks with graders (scores in [0, 1])
- [x] Incremental reward function
- [x] Baseline inference script using OpenAI API client + `HF_TOKEN`
- [x] Deployable Dockerfile (HF Spaces compatible)
- [x] Tagged with `openenv`

---

## Project Structure

```
email-triage-openenv/
├── app.py              # FastAPI server (HF Spaces entry point)
├── inference.py        # Baseline inference script
├── openenv.yaml        # OpenEnv metadata
├── Dockerfile          # Container definition
├── requirements.txt    # Python dependencies
├── README.md           # This file
└── env/
    ├── __init__.py     # Package exports
    ├── models.py       # Pydantic models (Action, Observation, Reward, ...)
    ├── tasks.py        # Task definitions, email datasets, graders
    └── environment.py  # EmailTriageEnv class (OpenEnv interface)
```

---

## License

MIT License — see [LICENSE](LICENSE) for details.
