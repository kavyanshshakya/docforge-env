"""
DocForge Grader — field-level scoring with P/R/F1 + confidence calibration.
Supports strings, numbers, lists, nested objects, and confidence scores.
"""
from __future__ import annotations
import json, re, math
from typing import Any, Dict, List, Optional, Tuple


def _normalize(val):
    if val is None: return None
    if isinstance(val, str): return re.sub(r"\s+", " ", val.strip().lower())
    if isinstance(val, (int, float)): return float(val)
    if isinstance(val, bool): return val
    if isinstance(val, list): return [_normalize(v) for v in val]
    if isinstance(val, dict): return {k: _normalize(v) for k, v in val.items()}
    return val


def _jaccard(a: str, b: str) -> float:
    at, bt = set(a.lower().split()), set(b.lower().split())
    if not at and not bt: return 1.0
    if not at or not bt: return 0.0
    return len(at & bt) / len(at | bt)


def _levenshtein_ratio(a: str, b: str) -> float:
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
    if isinstance(gold, bool) and isinstance(pred, bool):
        return 1.0 if gold == pred else 0.0
    if isinstance(gold, bool) or isinstance(pred, bool):
        return 1.0 if bool(gold) == bool(pred) else 0.0
    if gold is None and pred is None: return 1.0
    if gold is None or pred is None: return 0.0
    if isinstance(gold, (int, float)) and isinstance(pred, (int, float)):
        if gold == 0: return 1.0 if pred == 0 else 0.0
        return max(0.0, 1.0 - abs(float(pred) - float(gold)) / abs(float(gold)))
    if isinstance(gold, str) and isinstance(pred, str):
        ng, np_ = _normalize(gold), _normalize(pred)
        if ng == np_: return 1.0
        return max(_jaccard(ng, np_), _levenshtein_ratio(ng, np_))
    if isinstance(gold, list) and isinstance(pred, list):
        if not gold: return 1.0 if not pred else 0.0
        if gold and isinstance(gold[0], dict): return _score_dicts(gold, pred)
        if gold and isinstance(gold[0], str) and pred and isinstance(pred[0], str):
            gn = [_normalize(g) for g in gold]
            pn = [_normalize(p) for p in pred]
            if not pn: return 0.0
            matched = sum(max((max(_jaccard(g, p), _levenshtein_ratio(g, p)) for p in pn), default=0.0) for g in gn)
            return matched / len(gn)
        # List of non-string non-dict (numbers, bools, etc.)
        if not pred: return 0.0
        matched = 0
        for g in gold:
            best = max((_score_value(g, p) for p in pred), default=0.0)
            matched += best
        return matched / len(gold)
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


def _score_confidence(field_scores: Dict[str, float], confidence_json: Optional[str]) -> Tuple[float, str]:
    """
    Feature 9: Confidence calibration scoring.
    Rewards accurate confidence — high confidence on correct fields,
    low confidence on uncertain ones. Penalizes overconfident wrong answers.

    Returns (calibration_bonus, feedback_string)
    """
    if not confidence_json:
        return 0.0, ""

    try:
        confidences = json.loads(confidence_json)
    except (json.JSONDecodeError, TypeError):
        return 0.0, "Invalid confidence JSON"

    if not isinstance(confidences, dict) or not confidences:
        return 0.0, ""

    # Compute Expected Calibration Error (ECE) style metric
    calibration_scores = []
    for field, accuracy in field_scores.items():
        conf = confidences.get(field)
        if conf is None:
            continue
        conf = max(0.0, min(1.0, float(conf)))
        # Penalty for miscalibration: |confidence - accuracy|
        # Bonus for well-calibrated: 1 - |confidence - accuracy|
        cal = 1.0 - abs(conf - accuracy)
        # Extra penalty for overconfident wrong answers
        if conf > 0.8 and accuracy < 0.3:
            cal -= 0.2  # harsh penalty
        calibration_scores.append(cal)

    if not calibration_scores:
        return 0.0, ""

    avg_cal = sum(calibration_scores) / len(calibration_scores)
    # Scale to a small bonus (max 0.05)
    bonus = max(0.0, avg_cal * 0.05)

    return round(bonus, 4), f"Calibration: {avg_cal:.0%}"


def grade(gold_labels: Dict[str, Any], prediction_json: str,
          confidence_json: Optional[str] = None) -> Tuple[float, str]:
    """
    Grade a prediction. Returns (score, feedback).
    Score in [0.0, 1.0]. Feedback includes P/R/F1 + optional calibration.
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

    # Precision / Recall / F1
    gold_keys = set(gold_labels.keys())
    pred_keys = set(pred.keys())
    true_pos = sum(field_scores.get(k, 0.0) for k in gold_keys & pred_keys)
    precision = true_pos / len(pred_keys) if pred_keys else 0.0
    recall = sum(field_scores.values()) / len(gold_keys) if gold_keys else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0

    total_score = recall

    # Confidence calibration bonus
    cal_bonus, cal_fb = _score_confidence(field_scores, confidence_json)
    total_score = min(total_score + cal_bonus, 1.0)

    # Build feedback
    perfect = [k for k, v in field_scores.items() if v >= 0.99]
    partial = [f"{k}({v:.0%})" for k, v in field_scores.items() if 0.01 < v < 0.99]
    missing = [k for k, v in field_scores.items() if v < 0.01]
    extra = [k for k in pred_keys - gold_keys]

    parts = []
    if perfect: parts.append(f"OK: {', '.join(perfect)}")
    if partial: parts.append(f"Partial: {', '.join(partial)}")
    if missing: parts.append(f"Missing: {', '.join(missing)}")
    if extra: parts.append(f"Extra: {', '.join(extra[:3])}")
    parts.append(f"P={precision:.0%} R={recall:.0%} F1={f1:.0%}")
    if cal_fb: parts.append(cal_fb)

    return round(total_score, 4), " | ".join(parts)


def grade_confidence(gold_labels, prediction_json):
    """Grade confidence-calibrated extraction."""
    try:
        pred = json.loads(prediction_json)
    except (json.JSONDecodeError, TypeError) as e:
        return 0.0, f"Invalid JSON: {e}"
    if not isinstance(pred, dict):
        return 0.0, "Prediction must be a JSON object."

    scores = []
    details = []
    for field, gold_info in gold_labels.items():
        if isinstance(gold_info, dict) and "value" in gold_info:
            expected_val = gold_info.get("value")
            conf_tier = gold_info.get("confidence_expected", "high")
        else:
            expected_val = gold_info
            conf_tier = "high"

        pred_field = pred.get(field, {})
        if isinstance(pred_field, dict) and "value" in pred_field:
            pred_val = pred_field.get("value")
            pred_conf = float(pred_field.get("confidence", 0.5))
        else:
            pred_val = pred_field
            pred_conf = 0.5

        # Score the value extraction
        val_score = _score_value(expected_val, pred_val)

        # Score confidence calibration
        if conf_tier == "high":
            ideal_conf = 0.9
        elif conf_tier == "medium":
            ideal_conf = 0.6
        else:
            ideal_conf = 0.3

        conf_error = abs(float(pred_conf) - ideal_conf)
        conf_score = max(0.0, 1.0 - conf_error * 2)

        combined = 0.6 * val_score + 0.4 * conf_score
        scores.append(combined)
        details.append(f"{field}: val={val_score:.0%} conf={pred_conf:.1f}({'OK' if conf_error < 0.3 else 'BAD'})")

    total = sum(scores) / max(len(scores), 1)
    return round(total, 4), " | ".join(details[:5]) + f" | Score: {total:.2%}"


def grade_pii(gold_labels, prediction_json):
    """Grade PII detection accuracy."""
    try:
        pred = json.loads(prediction_json)
    except (json.JSONDecodeError, TypeError) as e:
        return 0.0, f"Invalid JSON: {e}"
    if not isinstance(pred, dict):
        return 0.0, "Prediction must be a JSON object."

    gold_extracted = gold_labels.get("extracted", {})
    gold_pii = set(gold_labels.get("pii_fields", []))

    pred_extracted = pred.get("extracted", {})
    if not pred_extracted and "pii_fields" not in pred:
        pred_extracted = pred  # flat prediction without nesting
    pred_pii_raw = pred.get("pii_fields", [])
    pred_pii = set(pred_pii_raw) if isinstance(pred_pii_raw, list) else set()

    # Score extraction (60% weight)
    ext_scores = {}
    for k, gv in gold_extracted.items():
        ext_scores[k] = _score_value(gv, pred_extracted.get(k))
    ext_total = sum(ext_scores.values()) / max(len(ext_scores), 1)

    # Score PII detection (40% weight)
    if gold_pii:
        pii_recall = len(gold_pii & pred_pii) / len(gold_pii)
        pii_precision = len(gold_pii & pred_pii) / len(pred_pii) if pred_pii else 0.0
        pii_f1 = 2 * pii_precision * pii_recall / (pii_precision + pii_recall) if (pii_precision + pii_recall) > 0 else 0.0
    else:
        pii_f1 = 1.0 if not pred_pii else 0.0

    total = 0.6 * ext_total + 0.4 * pii_f1
    missed = gold_pii - pred_pii
    extra = pred_pii - gold_pii
    fb = f"Extraction: {ext_total:.0%} | PII F1: {pii_f1:.0%}"
    if missed:
        fb += f" | Missed PII: {', '.join(list(missed)[:3])}"
    if extra:
        fb += f" | Extra PII: {', '.join(list(extra)[:3])}"
    return round(total, 4), fb


def grade_schema_free(gold_labels, prediction_json):
    """Grade schema-free extraction. More lenient on field names."""
    try:
        pred = json.loads(prediction_json)
    except (json.JSONDecodeError, TypeError) as e:
        return 0.0, f"Invalid JSON: {e}"
    if not isinstance(pred, dict):
        return 0.0, "Prediction must be a JSON object."

    # For each gold field, find the best matching pred field by value
    matched = 0
    total_gold = len(gold_labels)
    details = []

    for gold_key, gold_val in gold_labels.items():
        best_score = 0.0
        best_pred_key = None

        # First try exact key match
        if gold_key in pred:
            s = _score_value(gold_val, pred[gold_key])
            if s > best_score:
                best_score = s
                best_pred_key = gold_key

        # Then try fuzzy key match
        for pred_key, pred_val in pred.items():
            key_sim = _jaccard(gold_key.lower().replace("_", " "), pred_key.lower().replace("_", " "))
            if key_sim > 0.15:
                s = _score_value(gold_val, pred_val)
                if s > best_score:
                    best_score = s
                    best_pred_key = pred_key

        matched += best_score
        if best_score < 0.5:
            details.append(f"Missing: {gold_key}")

    total = matched / max(total_gold, 1)
    found = sum(1 for _ in gold_labels if True) - len(details)
    fb = f"Found {found}/{total_gold} fields | Score: {total:.0%}"
    if details:
        fb += " | " + ", ".join(details[:4])
    return round(total, 4), fb


def grade_dispatch(gold_labels, prediction_json, task_type="basic"):
    """Route to the appropriate grading function based on task_type."""
    if task_type == "confidence":
        return grade_confidence(gold_labels, prediction_json)
    elif task_type == "pii":
        return grade_pii(gold_labels, prediction_json)
    elif task_type == "schema_free":
        return grade_schema_free(gold_labels, prediction_json)
    else:
        return grade(gold_labels, prediction_json)
