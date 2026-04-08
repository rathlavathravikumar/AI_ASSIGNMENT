"""
Unit tests for the Email Triage OpenEnv.
Run with: pytest tests/
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from env import (
    EmailTriageEnv,
    Action,
    ActionType,
    Category,
    FlagType,
    Priority,
    TASKS,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def env():
    return EmailTriageEnv()


@pytest.fixture
def env_task1(env):
    env.reset("task_1")
    return env


@pytest.fixture
def env_task2(env):
    env.reset("task_2")
    return env


@pytest.fixture
def env_task3(env):
    env.reset("task_3")
    return env


# ---------------------------------------------------------------------------
# Reset tests
# ---------------------------------------------------------------------------

class TestReset:
    def test_reset_task1_returns_observation(self, env):
        obs = env.reset("task_1")
        assert obs.task_id == "task_1"
        assert obs.difficulty == "easy"
        assert len(obs.inbox) == 10
        assert obs.step_count == 0
        assert obs.max_steps == 40

    def test_reset_task2_returns_observation(self, env):
        obs = env.reset("task_2")
        assert obs.task_id == "task_2"
        assert obs.difficulty == "medium"
        assert len(obs.inbox) == 20

    def test_reset_task3_returns_observation(self, env):
        obs = env.reset("task_3")
        assert obs.task_id == "task_3"
        assert obs.difficulty == "hard"
        assert len(obs.inbox) == 20

    def test_reset_clears_state(self, env):
        env.reset("task_1")
        env.step(Action(action_type=ActionType.CLASSIFY, email_id="e01",
                        priority=Priority.URGENT, category=Category.WORK))
        obs = env.reset("task_1")
        assert obs.step_count == 0
        assert len(obs.classifications) == 0
        assert len(obs.archived) == 0

    def test_reset_unknown_task_raises(self, env):
        with pytest.raises(ValueError, match="Unknown task_id"):
            env.reset("task_99")


# ---------------------------------------------------------------------------
# Step tests
# ---------------------------------------------------------------------------

class TestStep:
    def test_step_before_reset_raises(self, env):
        with pytest.raises(RuntimeError, match="reset"):
            env.step(Action(action_type=ActionType.DONE))

    def test_classify_correct_returns_positive_reward(self, env_task1):
        action = Action(action_type=ActionType.CLASSIFY, email_id="e01",
                        priority=Priority.URGENT, category=Category.WORK)
        obs, reward, done, info = env_task1.step(action)
        assert reward.value > 0
        assert not done
        assert "e01" in obs.classifications

    def test_classify_wrong_priority_lower_reward(self, env_task1):
        # e01 is urgent/work — wrong priority
        action = Action(action_type=ActionType.CLASSIFY, email_id="e01",
                        priority=Priority.LOW, category=Category.WORK)
        _, reward1, _, _ = env_task1.step(action)

        env_task1.reset("task_1")
        action2 = Action(action_type=ActionType.CLASSIFY, email_id="e01",
                         priority=Priority.URGENT, category=Category.WORK)
        _, reward2, _, _ = env_task1.step(action2)
        assert reward2.value > reward1.value

    def test_classify_invalid_email_id_penalty(self, env_task1):
        action = Action(action_type=ActionType.CLASSIFY, email_id="INVALID",
                        priority=Priority.URGENT, category=Category.WORK)
        _, reward, done, _ = env_task1.step(action)
        assert reward.value < 0
        assert not done

    def test_archive_newsletter_correct(self, env_task1):
        # e02 is a newsletter — archiving is correct
        action = Action(action_type=ActionType.ARCHIVE, email_id="e02")
        _, reward, done, _ = env_task1.step(action)
        assert reward.value >= 0.08

    def test_delete_spam_correct(self, env_task1):
        # e04 is spam — deleting is correct
        action = Action(action_type=ActionType.DELETE, email_id="e04")
        _, reward, done, _ = env_task1.step(action)
        assert reward.value >= 0.08

    def test_delete_important_email_penalized(self, env_task1):
        # e01 is urgent/work — deleting should penalize
        action = Action(action_type=ActionType.DELETE, email_id="e01")
        _, reward, done, _ = env_task1.step(action)
        assert reward.value < 0

    def test_flag_urgent_email_correct(self, env_task1):
        action = Action(action_type=ActionType.FLAG, email_id="e01",
                        flag_type=FlagType.URGENT)
        obs, reward, done, _ = env_task1.step(action)
        assert reward.value >= 0.08
        assert "e01" in obs.flagged

    def test_flag_missing_flag_type_penalty(self, env_task1):
        action = Action(action_type=ActionType.FLAG, email_id="e01")
        _, reward, done, _ = env_task1.step(action)
        assert reward.value < 0

    def test_reply_too_short_penalty(self, env_task1):
        action = Action(action_type=ActionType.REPLY, email_id="e01", reply_body="ok")
        _, reward, _, _ = env_task1.step(action)
        assert reward.value < 0

    def test_reply_valid_body_reward(self, env_task1):
        action = Action(action_type=ActionType.REPLY, email_id="e01",
                        reply_body="Thank you for the alert. I am looking into this immediately.")
        obs, reward, _, _ = env_task1.step(action)
        assert reward.value > 0
        assert "e01" in obs.replies

    def test_search_returns_results(self, env_task1):
        action = Action(action_type=ActionType.SEARCH, search_query="urgent")
        _, reward, _, _ = env_task1.step(action)
        assert reward.value > 0

    def test_loop_detection_penalized(self, env_task1):
        action = Action(action_type=ActionType.ARCHIVE, email_id="e02")
        env_task1.step(action)
        _, reward, _, _ = env_task1.step(action)  # repeat
        assert reward.value < 0

    def test_done_ends_episode(self, env_task1):
        _, _, done, _ = env_task1.step(Action(action_type=ActionType.DONE))
        assert done

    def test_step_count_increments(self, env_task1):
        for _ in range(3):
            obs, _, _, _ = env_task1.step(
                Action(action_type=ActionType.CLASSIFY, email_id="e01",
                       priority=Priority.URGENT, category=Category.WORK)
            )
        assert obs.step_count == 3


# ---------------------------------------------------------------------------
# State tests
# ---------------------------------------------------------------------------

class TestState:
    def test_state_returns_dict(self, env_task1):
        s = env_task1.state()
        assert isinstance(s, dict)
        assert "task_id" in s
        assert "step_count" in s
        assert "classifications" in s
        assert "flagged" in s
        assert "archived" in s
        assert "deleted" in s
        assert "replies" in s

    def test_state_reflects_actions(self, env_task1):
        env_task1.step(Action(action_type=ActionType.ARCHIVE, email_id="e02"))
        s = env_task1.state()
        assert "e02" in s["archived"]


# ---------------------------------------------------------------------------
# Grader tests
# ---------------------------------------------------------------------------

class TestGraders:
    def test_evaluate_before_reset_raises(self, env):
        with pytest.raises(RuntimeError):
            env.evaluate()

    def test_perfect_task1_score(self, env):
        """Simulate a perfect agent on task_1 and verify high score."""
        from env.tasks import TASK1_GROUND_TRUTH
        env.reset("task_1")

        for eid, gt in TASK1_GROUND_TRUTH.items():
            pri = gt.priority if isinstance(gt.priority, str) else gt.priority.value
            cat = gt.category if isinstance(gt.category, str) else gt.category.value

            env.step(Action(
                action_type=ActionType.CLASSIFY,
                email_id=eid,
                priority=Priority(pri),
                category=Category(cat),
            ))

            gt_flag = gt.flag if hasattr(gt, "flag") else None
            if gt_flag:
                flag_val = gt_flag if isinstance(gt_flag, str) else gt_flag.value
                env.step(Action(
                    action_type=ActionType.FLAG,
                    email_id=eid,
                    flag_type=FlagType(flag_val),
                ))

            gt_cat = cat
            if gt_cat == "spam":
                env.step(Action(action_type=ActionType.DELETE, email_id=eid))
            elif gt_cat in ("newsletter",):
                env.step(Action(action_type=ActionType.ARCHIVE, email_id=eid))

        scores = env.evaluate()
        assert scores["total_score"] >= 0.70

    def test_score_between_0_and_1(self, env_task1):
        env_task1.step(Action(action_type=ActionType.DONE))
        scores = env_task1.evaluate()
        assert 0.0 <= scores["total_score"] <= 1.0

    def test_all_tasks_graders_work(self, env):
        for task_id in ["task_1", "task_2", "task_3"]:
            env.reset(task_id)
            env.step(Action(action_type=ActionType.DONE))
            scores = env.evaluate()
            assert "total_score" in scores
            assert 0.0 <= scores["total_score"] <= 1.0


# ---------------------------------------------------------------------------
# Task registry tests
# ---------------------------------------------------------------------------

class TestTasks:
    def test_three_tasks_exist(self):
        assert len(TASKS) == 3

    def test_task_difficulties(self):
        diffs = {t["difficulty"] for t in TASKS.values()}
        assert diffs == {"easy", "medium", "hard"}

    def test_each_task_has_emails_and_ground_truth(self):
        for task_id, cfg in TASKS.items():
            assert len(cfg["emails"]) > 0, f"{task_id} has no emails"
            assert len(cfg["ground_truth"]) > 0, f"{task_id} has no ground truth"

    def test_email_ids_unique_per_task(self):
        for task_id, cfg in TASKS.items():
            ids = [e.id for e in cfg["emails"]]
            assert len(ids) == len(set(ids)), f"{task_id} has duplicate email IDs"
