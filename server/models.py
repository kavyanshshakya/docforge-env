"""Typed models for the DocForge environment."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class DataExtractAction:
    extracted_json: str
    confidence_json: Optional[str] = None  # Feature 9: per-field confidence scores {"field": 0.0-1.0}


@dataclass
class DataExtractObservation:
    task_id: str
    difficulty: str
    raw_text: str
    schema_description: str
    feedback: str
    score: float
    steps_remaining: int
    category: str = "extraction"  # extraction, cross_document, schema_free, etc.


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
    task_type: str = "basic"
    category: str = "extraction"
