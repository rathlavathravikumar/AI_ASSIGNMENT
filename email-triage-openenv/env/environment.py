"""
EmailTriageEnv — OpenEnv-compliant environment for email triage.

Interface:
  reset(task_id)  → Observation
  step(action)    → (Observation, Reward, done, info)
  state()         → dict (full internal state)
"""

from __future__ import annotations

import copy
import time
from typing import Any, Dict, Optional, Tuple

from .models import (
    Action,
    ActionType,
    Category,
    Email,
    EmailClassification,
    EnvState,
    FlagType,
    Observation,
    Priority,
    Reward,
)
from .tasks import TASKS, run_grader


class EmailTriageEnv:
    """
    Real-world email triage environment where an agent must classify,
    prioritize, flag, archive, delete, and reply to emails correctly.

    Implements the OpenEnv interface:
      - reset(task_id="task_1") → Observation
      - step(action: Action) → (Observation, Reward, bool, dict)
      - state() → dict
    """

    PENALTY_LOOP = -0.05          # penalty per repeated identical action
    PENALTY_INVALID = -0.02       # penalty per invalid action
    REWARD_CORRECT_ACTION = 0.08  # incremental reward for correct action
    REWARD_CORRECT_CLASS = 0.04   # incremental reward for correct classification
    REWARD_DONE_BONUS = 0.10      # bonus for calling DONE

    def __init__(self) -> None:
        self._state: Optional[EnvState] = None
        self._task_cfg: Optional[Dict[str, Any]] = None
        self._emails: Dict[str, Email] = {}

    # ------------------------------------------------------------------
    # Public OpenEnv interface
    # ------------------------------------------------------------------

    def reset(self, task_id: str = "task_1") -> Observation:
        """Reset the environment for the given task and return initial observation."""
        if task_id not in TASKS:
            raise ValueError(f"Unknown task_id '{task_id}'. Choose from: {list(TASKS.keys())}")

        cfg = TASKS[task_id]
        self._task_cfg = cfg
        self._emails = {e.id: e for e in cfg["emails"]}

        self._state = EnvState(
            task_id=task_id,
            step_count=0,
            max_steps=cfg["max_steps"],
            done=False,
            total_reward=0.0,
        )

        return self._build_observation(message=f"Task loaded: {cfg['name']}. {cfg['description']}")

    def step(self, action: Action) -> Tuple[Observation, Reward, bool, Dict[str, Any]]:
        """
        Apply an action and return (observation, reward, done, info).

        Rewards:
          +0.08  correct action (archive spam, flag urgent, etc.)
          +0.04  correct classification (priority + category match)
          -0.02  invalid action (unknown email_id, missing params)
          -0.05  repeated identical action (loop detection)
          +0.10  DONE action (bonus, applied once)
        """
        if self._state is None:
            raise RuntimeError("Call reset() before step().")

        state = self._state
        state.step_count += 1
        reward = Reward()
        info: Dict[str, Any] = {"step": state.step_count}

        # Auto-terminate if max steps reached
        if state.step_count > state.max_steps:
            state.done = True
            reward.value = -0.10
            reward.reason = "Max steps exceeded — task terminated."
            obs = self._build_observation(message=reward.reason)
            return obs, reward, True, info

        # Loop detection
        action_sig = f"{action.action_type}:{action.email_id}:{action.priority}:{action.category}"
        if action_sig in [a.get("sig") for a in state.action_history[-5:]]:
            reward.value = self.PENALTY_LOOP
            reward.reason = "Repeated action detected — penalty applied."
            state.total_reward += reward.value
            obs = self._build_observation(message=reward.reason)
            return obs, reward, state.done, info

        # Record action
        state.action_history.append({"sig": action_sig, "step": state.step_count})

        # Dispatch
        atype = action.action_type
        if atype == ActionType.CLASSIFY:
            reward, msg = self._handle_classify(action)
        elif atype == ActionType.ARCHIVE:
            reward, msg = self._handle_archive(action)
        elif atype == ActionType.DELETE:
            reward, msg = self._handle_delete(action)
        elif atype == ActionType.FLAG:
            reward, msg = self._handle_flag(action)
        elif atype == ActionType.REPLY:
            reward, msg = self._handle_reply(action)
        elif atype == ActionType.MARK_READ:
            reward, msg = self._handle_mark_read(action)
        elif atype == ActionType.SEARCH:
            reward, msg = self._handle_search(action)
        elif atype == ActionType.DONE:
            reward, msg = self._handle_done()
        else:
            reward = Reward(value=self.PENALTY_INVALID, reason="Unknown action type.")
            msg = reward.reason

        state.total_reward = round(state.total_reward + reward.value, 4)
        info["total_reward"] = state.total_reward
        info["score_breakdown"] = self._score_snapshot()

        obs = self._build_observation(message=msg)
        return obs, reward, state.done, info

    def state(self) -> Dict[str, Any]:
        """Return full internal state as a dictionary (for inspection/logging)."""
        if self._state is None:
            return {}
        s = self._state
        return {
            "task_id": s.task_id,
            "step_count": s.step_count,
            "max_steps": s.max_steps,
            "done": s.done,
            "total_reward": s.total_reward,
            "classifications": {k: v.dict() for k, v in s.classifications.items()},
            "flagged": s.flagged,
            "archived": s.archived,
            "deleted": s.deleted,
            "replies": s.replies,
            "action_history": s.action_history,
        }

    def evaluate(self) -> Dict[str, float]:
        """Run the task grader and return the full score breakdown."""
        if self._state is None:
            raise RuntimeError("Call reset() before evaluate().")
        snap = self._score_snapshot()
        return run_grader(self._state.task_id, snap)

    # ------------------------------------------------------------------
    # Action handlers
    # ------------------------------------------------------------------

    def _handle_classify(self, action: Action) -> Tuple[Reward, str]:
        state = self._state
        eid = action.email_id

        if not eid or eid not in self._emails:
            return Reward(value=self.PENALTY_INVALID, reason=f"Email '{eid}' not found."), f"Invalid email_id: {eid}"
        if not action.priority or not action.category:
            return Reward(value=self.PENALTY_INVALID, reason="classify requires priority and category."), "Missing priority or category."

        classification = EmailClassification(
            email_id=eid,
            priority=action.priority,
            category=action.category,
            flag=action.flag_type,
            requires_reply=False,
        )
        state.classifications[eid] = classification

        # Score against ground truth if available
        r_val = 0.02  # base reward for any classification (coverage)
        gt = (self._task_cfg or {}).get("ground_truth", {}).get(eid)
        msg_parts = [f"Classified {eid}: {action.priority}/{action.category}."]

        if gt:
            gt_pri = gt.priority if isinstance(gt.priority, str) else (gt.get("priority") if isinstance(gt, dict) else gt.priority.value)
            gt_cat = gt.category if isinstance(gt.category, str) else (gt.get("category") if isinstance(gt, dict) else gt.category.value)
            act_pri = str(action.priority.value if hasattr(action.priority, "value") else action.priority)
            act_cat = str(action.category.value if hasattr(action.category, "value") else action.category)

            if act_pri == str(gt_pri):
                r_val += 0.02
                msg_parts.append("Priority correct.")
            else:
                msg_parts.append(f"Priority incorrect (expected: {gt_pri}).")
            if act_cat == str(gt_cat):
                r_val += 0.02
                msg_parts.append("Category correct.")
            else:
                msg_parts.append(f"Category incorrect (expected: {gt_cat}).")

        return Reward(value=round(r_val, 4), reason=" ".join(msg_parts)), " ".join(msg_parts)

    def _handle_archive(self, action: Action) -> Tuple[Reward, str]:
        state = self._state
        eid = action.email_id
        if not eid or eid not in self._emails:
            return Reward(value=self.PENALTY_INVALID, reason=f"Email '{eid}' not found."), f"Invalid email_id: {eid}"
        if eid in state.archived:
            return Reward(value=self.PENALTY_LOOP, reason=f"{eid} already archived."), f"{eid} already archived."

        state.archived.append(eid)
        r_val = 0.02  # base
        gt = (self._task_cfg or {}).get("ground_truth", {}).get(eid)
        msg = f"Archived {eid}."
        if gt:
            expected = gt.get("action") if isinstance(gt, dict) else "archive"
            if expected == "archive":
                r_val = self.REWARD_CORRECT_ACTION
                msg += " Correct action!"
            else:
                r_val = -0.03
                msg += f" Suboptimal — expected '{expected}'."
        return Reward(value=r_val, reason=msg), msg

    def _handle_delete(self, action: Action) -> Tuple[Reward, str]:
        state = self._state
        eid = action.email_id
        if not eid or eid not in self._emails:
            return Reward(value=self.PENALTY_INVALID, reason=f"Email '{eid}' not found."), f"Invalid email_id: {eid}"
        if eid in state.deleted:
            return Reward(value=self.PENALTY_LOOP, reason=f"{eid} already deleted."), f"{eid} already deleted."

        state.deleted.append(eid)
        r_val = 0.02
        gt = (self._task_cfg or {}).get("ground_truth", {}).get(eid)
        msg = f"Deleted {eid}."
        if gt:
            if isinstance(gt, dict):
                expected = gt.get("action")
                gt_cat = gt.get("category", "")
            else:
                # EmailClassification object (task_1): infer expected action from category
                gt_cat = gt.category if isinstance(gt.category, str) else gt.category.value
                expected = "delete" if gt_cat == "spam" else "flag"

            if expected == "delete" or gt_cat == "spam":
                r_val = self.REWARD_CORRECT_ACTION
                msg += " Correct action — spam removed!"
            elif expected in ("flag", "archive") or gt_cat != "spam":
                r_val = -0.05  # deleting something important is bad
                msg += f" WARNING: Expected '{expected}'. Deleting may lose important email."
        return Reward(value=r_val, reason=msg), msg

    def _handle_flag(self, action: Action) -> Tuple[Reward, str]:
        state = self._state
        eid = action.email_id
        if not eid or eid not in self._emails:
            return Reward(value=self.PENALTY_INVALID, reason=f"Email '{eid}' not found."), f"Invalid email_id: {eid}"
        if not action.flag_type:
            return Reward(value=self.PENALTY_INVALID, reason="flag requires flag_type."), "Missing flag_type."

        flag_val = action.flag_type.value if hasattr(action.flag_type, "value") else str(action.flag_type)
        state.flagged[eid] = flag_val
        r_val = 0.02
        gt = (self._task_cfg or {}).get("ground_truth", {}).get(eid)
        msg = f"Flagged {eid} as {flag_val}."
        if gt:
            expected_action = gt.get("action") if isinstance(gt, dict) else "flag"
            expected_flag = gt.get("flag_type") if isinstance(gt, dict) else None
            if expected_action == "flag":
                r_val = self.REWARD_CORRECT_ACTION
                msg += " Correct action!"
                if expected_flag and str(expected_flag) == str(flag_val):
                    r_val += 0.02
                    msg += " Flag type also correct!"
            else:
                r_val = -0.02
                msg += f" Suboptimal — expected '{expected_action}'."
        return Reward(value=round(r_val, 4), reason=msg), msg

    def _handle_reply(self, action: Action) -> Tuple[Reward, str]:
        state = self._state
        eid = action.email_id
        if not eid or eid not in self._emails:
            return Reward(value=self.PENALTY_INVALID, reason=f"Email '{eid}' not found."), f"Invalid email_id: {eid}"
        body = (action.reply_body or "").strip()
        if len(body) < 10:
            return Reward(value=self.PENALTY_INVALID, reason="Reply body too short (< 10 chars)."), "Reply body too short."

        state.replies[eid] = body
        r_val = 0.04
        gt = (self._task_cfg or {}).get("ground_truth", {}).get(eid)
        msg = f"Reply drafted for {eid} ({len(body)} chars)."
        if gt:
            needs_reply = gt.get("requires_reply") if isinstance(gt, dict) else getattr(gt, "requires_reply", False)
            if needs_reply:
                r_val = 0.06
                msg += " Reply correctly identified as needed!"
            else:
                r_val = 0.01
                msg += " Note: reply not required for this email."
        return Reward(value=r_val, reason=msg), msg

    def _handle_mark_read(self, action: Action) -> Tuple[Reward, str]:
        eid = action.email_id
        if not eid or eid not in self._emails:
            return Reward(value=self.PENALTY_INVALID, reason=f"Email '{eid}' not found."), f"Invalid email_id: {eid}"
        self._emails[eid] = self._emails[eid].copy(update={"is_read": True})
        return Reward(value=0.01, reason=f"Marked {eid} as read."), f"Marked {eid} as read."

    def _handle_search(self, action: Action) -> Tuple[Reward, str]:
        query = (action.search_query or "").lower().strip()
        if not query:
            return Reward(value=self.PENALTY_INVALID, reason="search requires search_query."), "Missing search_query."
        results = [
            e for e in self._emails.values()
            if query in e.subject.lower() or query in e.body.lower() or query in e.sender.lower()
        ]
        # Store last search in a temp attribute (not in state for simplicity)
        self._last_search = results
        return Reward(value=0.01, reason=f"Search '{query}' returned {len(results)} results."), f"Found {len(results)} emails for '{query}'."

    def _handle_done(self) -> Tuple[Reward, str]:
        state = self._state
        if state.done:
            return Reward(value=self.PENALTY_LOOP, reason="Already done."), "Already done."
        state.done = True
        final = run_grader(state.task_id, self._score_snapshot())
        r_val = round(self.REWARD_DONE_BONUS + final["total_score"] * 0.2, 4)
        msg = (
            f"Task complete! Final score: {final['total_score']:.4f}. "
            f"Breakdown: {final}"
        )
        return Reward(value=r_val, reason=msg, breakdown=final), msg

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _build_observation(self, message: str = "") -> Observation:
        state = self._state
        cfg = self._task_cfg or {}
        search_results = getattr(self, "_last_search", None)

        cls_dict: Dict[str, Any] = {}
        for k, v in state.classifications.items():
            cls_dict[k] = v.dict() if hasattr(v, "dict") else v

        return Observation(
            task_id=state.task_id,
            task_description=cfg.get("description", ""),
            difficulty=cfg.get("difficulty", ""),
            inbox=list(self._emails.values()),
            step_count=state.step_count,
            max_steps=state.max_steps,
            classifications=cls_dict,
            flagged=state.flagged,
            archived=state.archived,
            deleted=state.deleted,
            replies=state.replies,
            search_results=search_results,
            message=message,
            done=state.done,
            total_reward=state.total_reward,
        )

    def _score_snapshot(self) -> Dict[str, Any]:
        state = self._state
        cls_dict: Dict[str, Any] = {}
        for k, v in state.classifications.items():
            cls_dict[k] = v.dict() if hasattr(v, "dict") else v
        return {
            "classifications": cls_dict,
            "flagged": state.flagged,
            "archived": state.archived,
            "deleted": state.deleted,
            "replies": state.replies,
            "step_count": state.step_count,
            "max_steps": state.max_steps,
        }
