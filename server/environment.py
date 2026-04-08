"""
DocForge Environment — Structured document extraction with realistic corruption.

Key features:
- Corruption engine with global + targeted noise (OCR, redaction, field damage)
- Iterative feedback loop (5 attempts with P/R/F1 per-field feedback)
- Improvement-based reward shaping
- Seed-based reproducible corruption for consistent evaluation
"""
from __future__ import annotations
import random
from typing import Any, Dict, Tuple
from models import DataExtractAction, DataExtractObservation, DataExtractState
from grader import grade
from corruption import corrupt_document
from tasks import TASKS


class DataExtractEnvironment:

    def __init__(self):
        self.state = DataExtractState()
        self._tasks = list(TASKS)
        self._task_index = 0
        self._episode_count = 0
        self._cumulative_scores: Dict[str, list] = {}  # task_id -> [scores]

    def reset(self, task_id=None, difficulty=None, seed=None):
        pool = self._tasks
        if task_id:
            pool = [t for t in pool if t["task_id"] == task_id]
        elif difficulty:
            pool = [t for t in pool if t["difficulty"] == difficulty]
        if not pool:
            pool = self._tasks

        if task_id:
            task = pool[0]
        elif difficulty:
            task = random.choice(pool)
        else:
            task = self._tasks[self._task_index % len(self._tasks)]
            self._task_index += 1

        # Reproducible corruption: seed from task_id hash if not provided
        corruption_seed = seed if seed is not None else hash(task["task_id"]) % 2**31
        corrupted_text = corrupt_document(task["raw_text"], task["difficulty"], corruption_seed)

        self.state = DataExtractState(
            task_id=task["task_id"], difficulty=task["difficulty"],
            raw_text=corrupted_text, schema_description=task["schema_description"],
            gold_labels=task["gold_labels"],
            best_score=0.0, current_step=0, max_steps=5, done=False,
        )
        self._episode_count += 1

        return self._obs("New episode. Extract the requested fields as a JSON object."), 0.0, False, {
            "task_id": task["task_id"], "difficulty": task["difficulty"],
            "num_fields": len(task["gold_labels"]),
            "corruption_applied": task["difficulty"] != "easy",
            "corruption_seed": corruption_seed,
        }

    def step(self, action: DataExtractAction):
        if self.state.done:
            return self._obs("Episode ended."), 0.0, True, {}

        self.state.current_step += 1
        score, feedback = grade(self.state.gold_labels, action.extracted_json)

        improvement = max(0.0, score - self.state.best_score)
        json_valid = "Invalid JSON" not in feedback
        validity_bonus = 0.01 if json_valid and self.state.current_step == 1 else 0.0
        reward = improvement + validity_bonus
        self.state.best_score = max(self.state.best_score, score)

        done = self.state.current_step >= self.state.max_steps or score >= 0.99
        self.state.done = done

        # Track for metrics
        if done:
            tid = self.state.task_id
            if tid not in self._cumulative_scores:
                self._cumulative_scores[tid] = []
            self._cumulative_scores[tid].append(self.state.best_score)

        return self._obs(feedback), round(reward, 4), done, {
            "raw_score": score, "best_score": self.state.best_score,
            "improvement": improvement, "perfect": score >= 0.99,
            "step": self.state.current_step,
        }

    def get_state(self):
        return {
            "task_id": self.state.task_id, "difficulty": self.state.difficulty,
            "current_step": self.state.current_step, "max_steps": self.state.max_steps,
            "best_score": self.state.best_score, "done": self.state.done,
        }

    def get_metrics(self):
        """Aggregate performance metrics across all completed episodes."""
        if not self._cumulative_scores:
            return {"episodes": 0, "message": "No completed episodes yet."}

        all_scores = []
        per_task = {}
        per_difficulty = {"easy": [], "medium": [], "hard": []}

        for tid, scores in self._cumulative_scores.items():
            all_scores.extend(scores)
            per_task[tid] = {
                "episodes": len(scores),
                "mean_score": round(sum(scores) / len(scores), 4),
                "best_score": round(max(scores), 4),
            }
            # Find difficulty
            task = next((t for t in self._tasks if t["task_id"] == tid), None)
            if task:
                per_difficulty[task["difficulty"]].extend(scores)

        difficulty_summary = {}
        for diff, scores in per_difficulty.items():
            if scores:
                difficulty_summary[diff] = {
                    "episodes": len(scores),
                    "mean_score": round(sum(scores) / len(scores), 4),
                }

        return {
            "total_episodes": self._episode_count,
            "completed_episodes": len(all_scores),
            "overall_mean_score": round(sum(all_scores) / len(all_scores), 4),
            "by_difficulty": difficulty_summary,
            "by_task": per_task,
        }

    def _obs(self, feedback):
        return DataExtractObservation(
            task_id=self.state.task_id, difficulty=self.state.difficulty,
            raw_text=self.state.raw_text, schema_description=self.state.schema_description,
            feedback=feedback, score=self.state.best_score,
            steps_remaining=self.state.max_steps - self.state.current_step,
        )
