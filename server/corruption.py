"""
DocForge Corruption Engine
Simulates real-world document noise at two levels:
  1. Global corruption: OCR artifacts, whitespace damage, line breaks, redactions
  2. Targeted corruption: specifically degrades key extraction fields (phone, email, numbers)

Corruption intensity scales with difficulty tier.
Seed-based for reproducible episodes.
"""
from __future__ import annotations
import random
import re
from typing import Any, Dict, Optional


# ── OCR character confusion matrix ──
OCR_SWAPS = {
    "l": ["1", "I", "|"], "1": ["l", "I"], "0": ["O", "o"], "O": ["0"],
    "o": ["0"], "S": ["5", "$"], "5": ["S"], "B": ["8"], "8": ["B"],
    "rn": ["m"], "m": ["rn"], "cl": ["d"], "vv": ["w"],
    "g": ["q"], "q": ["g"], "I": ["l", "1"], "Z": ["2"], "2": ["Z"],
}

ARTIFACTS = ["\u00a0", "\u200b", "  ", "\t"]


def _ocr_corrupt(text: str, intensity: float, rng: random.Random) -> str:
    chars = list(text)
    i = 0
    while i < len(chars):
        if rng.random() < intensity:
            if i + 1 < len(chars):
                bigram = chars[i] + chars[i + 1]
                if bigram in OCR_SWAPS:
                    chars[i] = rng.choice(OCR_SWAPS[bigram])
                    chars[i + 1] = ""
                    i += 2
                    continue
            if chars[i] in OCR_SWAPS:
                chars[i] = rng.choice(OCR_SWAPS[chars[i]])
        i += 1
    return "".join(chars)


def _whitespace_damage(text: str, intensity: float, rng: random.Random) -> str:
    words = text.split(" ")
    result = []
    for w in words:
        result.append(w)
        if rng.random() < intensity:
            result.append(rng.choice(ARTIFACTS))
    return " ".join(result)


def _line_break_damage(text: str, intensity: float, rng: random.Random) -> str:
    result = []
    for ch in text:
        result.append(ch)
        if ch == " " and rng.random() < intensity:
            result.append("\n")
    return "".join(result)


def _redact_spans(text: str, num_redactions: int, rng: random.Random) -> str:
    words = text.split()
    if len(words) < 10:
        return text
    for _ in range(num_redactions):
        start = rng.randint(0, max(0, len(words) - 4))
        span_len = rng.randint(1, 3)
        marker = rng.choice(["[REDACTED]", "\u2588\u2588\u2588\u2588", "[ILLEGIBLE]", "???"])
        for j in range(start, min(start + span_len, len(words))):
            words[j] = ""
        words[start] = marker
    return " ".join(w for w in words if w)


def _duplicate_field(text: str, rng: random.Random) -> str:
    lines = text.split("\n")
    if len(lines) < 3:
        return text
    idx = rng.randint(0, len(lines) - 1)
    original = lines[idx]
    if not original.strip():
        return text
    numbers = re.findall(r'\d+', original)
    if numbers:
        target = rng.choice(numbers)
        new_num = str(int(target) + rng.choice([-1, 1, 2, -2]))
        modified = original.replace(target, new_num, 1)
        lines.insert(idx + 1, f"[correction: {modified.strip()}]")
    return "\n".join(lines)


# ── Targeted field corruption ──

def _corrupt_phone(text: str, rng: random.Random) -> str:
    """Swap 1-2 digits in phone numbers."""
    def _swap_digit(m):
        digits = list(m.group(0))
        if len(digits) > 2 and rng.random() < 0.5:
            i = rng.randint(0, len(digits) - 1)
            while not digits[i].isdigit():
                i = rng.randint(0, len(digits) - 1)
            digits[i] = str(rng.randint(0, 9))
        return "".join(digits)
    return re.sub(r'[\d\(\)\-\+\s]{7,}', _swap_digit, text, count=1)


def _corrupt_email(text: str, rng: random.Random) -> str:
    """Apply OCR noise to email addresses."""
    def _damage(m):
        email = m.group(0)
        return _ocr_corrupt(email, 0.15, rng)
    return re.sub(r'[\w\.\-]+@[\w\.\-]+\.\w+', _damage, text, count=1)


def _corrupt_amounts(text: str, rng: random.Random) -> str:
    """Slightly alter one monetary amount."""
    def _nudge(m):
        if rng.random() < 0.3:
            val = m.group(0)
            # Swap two adjacent chars
            chars = list(val)
            if len(chars) > 3:
                i = rng.randint(1, len(chars) - 2)
                chars[i], chars[i-1] = chars[i-1], chars[i]
            return "".join(chars)
        return m.group(0)
    return re.sub(r'[\$\£\¥€][\d,]+\.?\d*', _nudge, text, count=1)


# ── Main entry point ──

def corrupt_document(text: str, difficulty: str, seed: Optional[int] = None) -> str:
    """
    Apply corruption based on difficulty tier.
    
    easy:   Clean text, no corruption
    medium: Light global OCR + minor artifacts + light targeted corruption
    hard:   Heavy global + redactions + contradictions + targeted field damage
    
    Seed makes corruption reproducible for consistent evaluation.
    """
    rng = random.Random(seed)

    if difficulty == "easy":
        return text

    if difficulty == "medium":
        text = _ocr_corrupt(text, 0.02, rng)
        text = _whitespace_damage(text, 0.02, rng)
        # Light targeted corruption
        if rng.random() < 0.3:
            text = _corrupt_phone(text, rng)
        return text

    if difficulty == "hard":
        # Global corruption
        text = _ocr_corrupt(text, 0.04, rng)
        text = _whitespace_damage(text, 0.03, rng)
        text = _line_break_damage(text, 0.03, rng)
        if rng.random() < 0.4:
            text = _redact_spans(text, 1, rng)
        if rng.random() < 0.3:
            text = _duplicate_field(text, rng)
        # Targeted field corruption
        if rng.random() < 0.5:
            text = _corrupt_phone(text, rng)
        if rng.random() < 0.3:
            text = _corrupt_email(text, rng)
        if rng.random() < 0.4:
            text = _corrupt_amounts(text, rng)
        return text

    return text
