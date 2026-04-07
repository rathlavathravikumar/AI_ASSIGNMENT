"""
Baseline inference script for the Email Triage OpenEnv.

Uses the OpenAI-compatible client (pointed at Hugging Face's inference API)
to evaluate a language model on all three tasks.

Usage:
    HF_TOKEN=your_token python inference.py [--model meta-llama/Llama-3.1-8B-Instruct] [--task all]

Environment variables:
    HF_TOKEN   — Hugging Face API token (required)
    HF_MODEL   — model to evaluate (optional, overridden by --model)
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from typing import Any, Dict, List, Optional

try:
    from openai import OpenAI
except ImportError:
    print("ERROR: 'openai' package not installed. Run: pip install openai")
    sys.exit(1)

from env import EmailTriageEnv, Action, ActionType, TASKS


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

DEFAULT_MODEL = "meta-llama/Llama-3.1-8B-Instruct"
HF_BASE_URL = "https://api-inference.huggingface.co/v1"

SYSTEM_PROMPT = """You are an expert email triage AI assistant. Process inbox emails by taking structured actions.

Available actions — return ONLY valid JSON (no markdown, no explanation):

{"action_type": "classify", "email_id": "<id>", "priority": "urgent|normal|low", "category": "work|personal|spam|newsletter|finance|support"}
{"action_type": "archive", "email_id": "<id>"}
{"action_type": "delete", "email_id": "<id>"}
{"action_type": "flag", "email_id": "<id>", "flag_type": "urgent|follow_up|waiting|action_required"}
{"action_type": "reply", "email_id": "<id>", "reply_body": "<reply text>"}
{"action_type": "done"}

Triage rules:
1. SPAM: delete it
2. Newsletters / automated digests: archive
3. Urgent work matters (outages, deadline today, security breach): flag as "urgent"
4. Action needed but not time-critical: flag as "action_required" and classify
5. Informational work emails: classify + archive
6. Personal low-priority: classify + archive
7. Always classify every email (priority + category)
8. When inbox is fully processed, call done

Return ONLY the JSON object."""


def build_user_prompt(obs: Dict[str, Any]) -> str:
    inbox = obs.get("inbox", [])
    classified = set(obs.get("classifications", {}).keys())
    archived = set(obs.get("archived", []))
    deleted = set(obs.get("deleted", []))
    flagged = set(obs.get("flagged", {}).keys())

    processed = classified | archived | deleted | flagged
    unprocessed = [e for e in inbox if e["id"] not in processed]

    lines = [
        f"TASK: {obs.get('task_description', '')[:200]}",
        f"Step {obs.get('step_count', 0)}/{obs.get('max_steps', 50)} | "
        f"Reward: {obs.get('total_reward', 0.0):.3f} | "
        f"Remaining: {len(unprocessed)}/{len(inbox)} emails",
        "",
    ]

    if not unprocessed:
        lines.append("All emails processed. Call: {\"action_type\": \"done\"}")
    else:
        lines.append("Next emails to process:")
        for email in unprocessed[:4]:  # 4 at a time for context efficiency
            lines.append(f"\n[{email['id']}] FROM: {email['sender']} <{email['sender_email']}>")
            lines.append(f"SUBJECT: {email['subject']}")
            body_preview = email['body'][:250] + ("..." if len(email['body']) > 250 else "")
            lines.append(f"BODY: {body_preview}")
            if email.get("attachments"):
                lines.append(f"ATTACHMENTS: {', '.join(email['attachments'])}")

        lines.append(f"\nPick ONE action for ONE email and return ONLY the JSON.")

    return "\n".join(lines)


def parse_action(text: str) -> Optional[Action]:
    text = text.strip()
    # Strip markdown code fences
    text = re.sub(r'^```[a-z]*\n?', '', text)
    text = re.sub(r'\n?```$', '', text)
    text = text.strip()

    # Direct parse
    try:
        return Action(**json.loads(text))
    except Exception:
        pass

    # Extract first JSON object
    match = re.search(r'\{[^{}]*\}', text, re.DOTALL)
    if match:
        try:
            return Action(**json.loads(match.group()))
        except Exception:
            pass

    return None


def run_task(
    client: OpenAI,
    model: str,
    task_id: str,
    verbose: bool = True,
) -> Dict[str, Any]:
    env = EmailTriageEnv()
    obs = env.reset(task_id=task_id)
    obs_dict = obs.dict()

    cfg = TASKS[task_id]
    if verbose:
        print(f"\n{'='*60}")
        print(f"TASK: {cfg['name']} [{cfg['difficulty'].upper()}]")
        print(f"Emails: {len(cfg['emails'])} | Max steps: {cfg['max_steps']}")
        print("="*60)

    messages: List[Dict[str, str]] = [{"role": "system", "content": SYSTEM_PROMPT}]
    step_count = 0
    done = False
    total_reward = 0.0

    while not done and step_count < cfg["max_steps"]:
        user_msg = build_user_prompt(obs_dict)
        messages.append({"role": "user", "content": user_msg})

        action: Optional[Action] = None
        for attempt in range(3):
            try:
                resp = client.chat.completions.create(
                    model=model,
                    messages=messages,
                    max_tokens=300,
                    temperature=0.05,
                )
                reply_text = resp.choices[0].message.content or ""
                action = parse_action(reply_text)
                messages.append({"role": "assistant", "content": reply_text})
                if action:
                    break
                messages.append({"role": "user", "content": "Invalid JSON. Return ONLY a valid JSON action."})
            except Exception as exc:
                wait = 2 ** attempt
                if verbose:
                    print(f"  [API ERROR attempt {attempt+1}] {exc} — retrying in {wait}s")
                time.sleep(wait)

        if action is None:
            action = Action(action_type=ActionType.DONE)

        obs, reward, done, info = env.step(action)
        obs_dict = obs.dict()
        total_reward = obs_dict.get("total_reward", 0.0)
        step_count += 1

        if verbose:
            eid = action.email_id or "—"
            print(f"  Step {step_count:3d} | {action.action_type:<12} | {eid:<4} | "
                  f"r={reward.value:+.3f} | cumul={total_reward:.3f}")

        if done:
            break

    # Force done if loop ended without it
    if not done:
        obs, reward, done, info = env.step(Action(action_type=ActionType.DONE))
        step_count += 1
        total_reward = obs.total_reward

    try:
        scores = env.evaluate()
    except Exception:
        scores = {"total_score": 0.0}

    if verbose:
        print(f"\n  Final Score : {scores.get('total_score', 0.0):.4f}")
        for k, v in scores.items():
            if k != "total_score":
                print(f"  {k:<30} {v:.4f}")

    return {
        "task_id": task_id,
        "task_name": cfg["name"],
        "difficulty": cfg["difficulty"],
        "steps_used": step_count,
        "total_reward": round(total_reward, 4),
        "scores": scores,
    }


def main() -> float:
    parser = argparse.ArgumentParser(description="Email Triage OpenEnv — Baseline Inference")
    parser.add_argument("--model", type=str, default=None)
    parser.add_argument("--task", type=str, default="all",
                        choices=["all", "task_1", "task_2", "task_3"])
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()

    hf_token = os.environ.get("HF_TOKEN")
    if not hf_token:
        print("ERROR: HF_TOKEN environment variable not set.")
        sys.exit(1)

    model = args.model or os.environ.get("HF_MODEL", DEFAULT_MODEL)
    verbose = not args.quiet

    print(f"\nEmail Triage OpenEnv — Baseline Inference")
    print(f"Model : {model}")
    print(f"Tasks : {args.task}")

    client = OpenAI(base_url=HF_BASE_URL, api_key=hf_token)

    tasks_to_run = list(TASKS.keys()) if args.task == "all" else [args.task]
    all_results = []

    for task_id in tasks_to_run:
        result = run_task(client, model, task_id, verbose=verbose)
        all_results.append(result)
        time.sleep(1)

    # Summary
    print(f"\n{'='*60}")
    print("FINAL SUMMARY")
    print(f"{'='*60}")
    total = 0.0
    for r in all_results:
        s = r["scores"].get("total_score", 0.0)
        total += s
        print(f"  {r['task_id']:<8} [{r['difficulty']:<6}] Score: {s:.4f} | Steps: {r['steps_used']}")
    avg = total / len(all_results) if all_results else 0.0
    print(f"\n  AVERAGE SCORE : {avg:.4f}")
    print("="*60)

    output = {
        "model": model,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "average_score": round(avg, 4),
        "results": all_results,
    }
    with open("baseline_results.json", "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nResults saved to baseline_results.json")
    return avg


if __name__ == "__main__":
    main()
