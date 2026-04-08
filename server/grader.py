"""
DocForge Grader — field-level scoring with precision, recall, F1.
Supports strings, numbers, lists, and nested objects (line items).
"""
from __future__ import annotations
import json, re
from typing import Any, Dict, List, Tuple


def _normalize(val):
    if val is None: return None
    if isinstance(val, str): return re.sub(r"\s+", " ", val.strip().lower())
    if isinstance(val, (int, float)): return float(val)
    if isinstance(val, list): return [_normalize(v) for v in val]
    if isinstance(val, dict): return {k: _normalize(v) for k, v in val.items()}
    return val


def _jaccard(a: str, b: str) -> float:
    at, bt = set(a.lower().split()), set(b.lower().split())
    if not at and not bt: return 1.0
    if not at or not bt: return 0.0
    return len(at & bt) / len(at | bt)


def _levenshtein_ratio(a: str, b: str) -> float:
    """Normalized Levenshtein similarity for short strings."""
    if a == b: return 1.0
    n, m = len(a), len(b)
    if n == 0 or m == 0: return 0.0
    d = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(n + 1): d[i][0] = i
    for j in range(m + 1): d[0][j] = j
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            cost = 0 if a[i-1] == b[j-1] else 1
            d[i][j] = min(d[i-1][j] + 1, d[i][j-1] + 1, d[i-1][j-1] + cost)
    return 1.0 - d[n][m] / max(n, m)


def _score_value(gold, pred) -> float:
    if gold is None and pred is None: return 1.0
    if gold is None or pred is None: return 0.0

    # Numbers
    if isinstance(gold, (int, float)) and isinstance(pred, (int, float)):
        if gold == 0: return 1.0 if pred == 0 else 0.0
        return max(0.0, 1.0 - abs(float(pred) - float(gold)) / abs(float(gold)))

    # Strings — combine Jaccard + Levenshtein for robustness
    if isinstance(gold, str) and isinstance(pred, str):
        ng, np_ = _normalize(gold), _normalize(pred)
        if ng == np_: return 1.0
        return max(_jaccard(ng, np_), _levenshtein_ratio(ng, np_))

    # Lists
    if isinstance(gold, list) and isinstance(pred, list):
        if not gold: return 1.0 if not pred else 0.0
        if gold and isinstance(gold[0], dict): return _score_dicts(gold, pred)
        gn = [_normalize(g) for g in gold]
        pn = [_normalize(p) for p in pred]
        if not pn: return 0.0
        matched = sum(max((max(_jaccard(g, p), _levenshtein_ratio(g, p)) for p in pn), default=0.0) for g in gn)
        return matched / len(gn)

    # Coerce to string
    return max(_jaccard(str(gold), str(pred)), _levenshtein_ratio(str(gold).lower(), str(pred).lower()))


def _score_dicts(gold: List[Dict], pred: List[Dict]) -> float:
    if not pred: return 0.0
    avail = list(range(len(pred)))
    total = 0.0
    for g in gold:
        best, bidx = 0.0, -1
        for i in avail:
            p = pred[i] if isinstance(pred[i], dict) else {}
            s = sum(_score_value(g.get(k), p.get(k)) for k in g) / max(len(g), 1)
            if s > best: best, bidx = s, i
        total += best
        if bidx >= 0: avail.remove(bidx)
    return total / len(gold)


def grade(gold_labels: Dict[str, Any], prediction_json: str) -> Tuple[float, str]:
    """
    Grade a prediction. Returns (score, feedback).
    Score in [0.0, 1.0]. Feedback includes precision/recall/F1 breakdown.
    """
    try:
        pred = json.loads(prediction_json)
    except (json.JSONDecodeError, TypeError) as e:
        return 0.0, f"Invalid JSON: {e}"
    if not isinstance(pred, dict):
        return 0.0, "Prediction must be a JSON object."
    if not pred:
        return 0.0, "Empty prediction. Extract the fields listed in the schema."

    # Field-level scores
    field_scores = {}
    for k, gv in gold_labels.items():
        field_scores[k] = _score_value(gv, pred.get(k))

    # Precision: how many predicted fields are correct?
    gold_keys = set(gold_labels.keys())
    pred_keys = set(pred.keys())
    true_pos = sum(field_scores.get(k, 0.0) for k in gold_keys & pred_keys)
    precision = true_pos / len(pred_keys) if pred_keys else 0.0

    # Recall: how many gold fields were found?
    recall = sum(field_scores.values()) / len(gold_keys) if gold_keys else 0.0

    # F1
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0

    # Use recall as main score (penalizes missing fields)
    total_score = recall

    # Build feedback
    perfect = [k for k, v in field_scores.items() if v >= 0.99]
    partial = [f"{k}({v:.0%})" for k, v in field_scores.items() if 0.01 < v < 0.99]
    missing = [k for k, v in field_scores.items() if v < 0.01]
    extra = [k for k in pred_keys - gold_keys]

    parts = []
    if perfect: parts.append(f"OK: {', '.join(perfect)}")
    if partial: parts.append(f"Partial: {', '.join(partial)}")
    if missing: parts.append(f"Missing: {', '.join(missing)}")
    if extra: parts.append(f"Extra keys (ignored): {', '.join(extra[:3])}")
    parts.append(f"P={precision:.0%} R={recall:.0%} F1={f1:.0%}")

    return round(total_score, 4), " | ".join(parts)
