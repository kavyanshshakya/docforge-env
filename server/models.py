"""Typed models for the DataExtract environment."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass
class DataExtractAction:
    extracted_json: str


@dataclass
class DataExtractObservation:
    task_id: str
    difficulty: str
    raw_text: str
    schema_description: str
    feedback: str
    score: float
    steps_remaining: int


@dataclass
class DataExtractState:
    task_id: str = ""
    difficulty: str = ""
    raw_text: str = ""
    schema_description: str = ""
    gold_labels: Dict[str, Any] = field(default_factory=dict)
    best_score: float = 0.0
    current_step: int = 0
    max_steps: int = 5
    done: bool = False
