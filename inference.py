"""
Inference script for DocForge environment.
Runs baseline evaluation across all 31 tasks including:
- Original extraction (contacts, tickets, jobs, receipts, invoices)
- Multilingual (German, Japanese, Spanish)
- Cross-document reconciliation
- Temporal reasoning
- Adversarial documents
- Table reconstruction
- Schema-free discovery
- PII detection
- Hierarchical documents
+ Confidence calibration on all tasks
"""
import json
import os
import textwrap
from typing import List, Optional

import requests
from openai import OpenAI

# ── Environment variables ──
API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "Qwen/Qwen2.5-72B-Instruct")
HF_TOKEN = os.getenv("HF_TOKEN")
if HF_TOKEN is None:
    raise ValueError("HF_TOKEN environment variable is required")

ENV_URL = os.getenv("ENV_URL", "https://kavyanshshakya-docforge-env.hf.space")
BENCHMARK = "docforge"
MAX_STEPS = 3

TASK_IDS = [
    # Original extraction
    "contact_01", "contact_02", "contact_03", "contact_04",
    "ticket_01", "ticket_02",
    "job_01", "job_02", "job_03", "job_04",
    "receipt_01", "receipt_02", "receipt_03",
    "invoice_01", "invoice_02", "invoice_03", "invoice_04",
    # Multilingual
    "multi_de_01", "multi_ja_01", "multi_es_01",
    # Cross-document reconciliation
    "crossdoc_01", "crossdoc_02",
    # Temporal reasoning
    "temporal_01", "temporal_02",
    # Adversarial
    "adversarial_01", "adversarial_02",
    # Table reconstruction
    "table_01",
    # Confidence calibration
    "confidence_01",
    # Schema-free discovery
    "schemafree_01",
    # PII detection
    "pii_01",
    # Hierarchical documents
    "hierarchical_01",
]

SYSTEM_PROMPT = textwrap.dedent("""
You are a structured data extraction agent. Given unstructured text and a target schema,
output ONLY valid JSON. No explanation, no markdown.

Rules:
- Output raw JSON only. Never wrap in ```json blocks or add commentary.
- Match field names exactly as specified in the schema.
- For lists of strings, use JSON arrays: ["item1", "item2"]
- For lists of objects (like line_items), use: [{"field": "value"}, ...]
- For null/unknown values, use null.
- Numbers must be numeric types, not strings. 140000 not "140,000".
- Booleans must be true/false, not strings.
- Copy proper nouns, emails, phone numbers exactly from the text.
- For line items: quantity=1 for flat fees/lump sums.
- For cross-document tasks: carefully compare both documents and flag discrepancies.
- For temporal tasks: compute dates mathematically from the given rules.
- For adversarial tasks: identify which information is correct vs misleading.
- For schema-free tasks: discover all meaningful fields yourself.
- For PII tasks: identify all personally identifiable information fields.
- For hierarchical tasks: extract from the correct nesting level.
- For multilingual tasks: extract values in the original language unless translating is needed for field names.
""").strip()

CONFIDENCE_PROMPT = textwrap.dedent("""
Additionally, output a second JSON object on a new line with your confidence for each field.
Format: {"field_name": 0.0-1.0, ...}
1.0 = completely certain, 0.0 = pure guess.
Be honest. Low confidence on uncertain fields is rewarded.
High confidence on wrong answers is penalized.

Output format (two lines):
LINE 1: {extraction JSON}
LINE 2: {confidence JSON}
""").strip()


def log_start(task, env, model):
    print(f"[START] task={task} env={env} model={model}", flush=True)

def log_step(step, action, reward, done, error):
    e = error if error else "null"
    print(f"[STEP] step={step} action={action[:100]} reward={reward:.2f} done={str(done).lower()} error={e}", flush=True)

def log_end(success, steps, score, rewards):
    rs = ",".join(f"{r:.2f}" for r in rewards)
    print(f"[END] success={str(success).lower()} steps={steps} score={score:.3f} rewards={rs}", flush=True)


def call_model(client, raw_text, schema, feedback=""):
    user_msg = f"TEXT:\n{raw_text}\n\nSCHEMA:\n{schema}"
    if feedback:
        user_msg += f"\n\nFEEDBACK FROM PREVIOUS ATTEMPT:\n{feedback}\nFix the issues and output corrected JSON."
    user_msg += f"\n\n{CONFIDENCE_PROMPT}"

    resp = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_msg},
        ],
        temperature=0.0,
        max_tokens=3000,
    )
    text = (resp.choices[0].message.content or "").strip()
    # Strip markdown fences
    if text.startswith("```"):
        text = text.split("\n", 1)[-1]
    if text.endswith("```"):
        text = text.rsplit("```", 1)[0]
    text = text.strip()

    # Parse two-line output: extraction + confidence
    lines = text.split("\n")
    extraction = lines[0].strip() if lines else "{}"
    confidence = None
    if len(lines) > 1:
        # Find the second JSON object
        for line in lines[1:]:
            line = line.strip()
            if line.startswith("{"):
                confidence = line
                break

    return extraction, confidence


def run_task(client, task_id):
    log_start(task=task_id, env=BENCHMARK, model=MODEL_NAME)
    rewards, steps, best_score = [], 0, 0.00101

    try:
        resp = requests.post(f"{ENV_URL}/reset", json={"task_id": task_id}, timeout=30)
        data = resp.json()
        obs = data["observation"]
        feedback = ""

        for step in range(1, MAX_STEPS + 1):
            extraction, confidence = call_model(client, obs["raw_text"], obs["schema_description"], feedback)

            step_body = {"extracted_json": extraction}
            if confidence:
                step_body["confidence_json"] = confidence

            resp = requests.post(f"{ENV_URL}/step", json=step_body, timeout=30)
            data = resp.json()
            obs = data["observation"]
            reward, done = data["reward"], data["done"]

            rewards.append(reward)
            steps = step
            best_score = max(best_score, obs["score"])
            feedback = obs["feedback"]

            log_step(step=step, action=f"extract({task_id})", reward=reward, done=done, error=None)
            if done:
                break

    except Exception as e:
        print(f"[DEBUG] Error in task {task_id}: {e}", flush=True)

    score = min(max(best_score, 0.001), 0.999)
    log_end(success=score >= 0.5, steps=steps, score=score, rewards=rewards)
    return score


def main():
    client = OpenAI(base_url=API_BASE_URL, api_key=HF_TOKEN)
    scores = []
    for task_id in TASK_IDS:
        try:
            scores.append(run_task(client, task_id))
        except Exception as e:
            print(f"[DEBUG] Task {task_id} failed: {e}", flush=True)
            scores.append(0.001)

    avg = sum(scores) / len(scores) if scores else 0.0

    # Category breakdown
    categories = {
        "Easy": [s for s, t in zip(scores, TASK_IDS) if t.startswith("contact") or t.startswith("ticket")],
        "Medium": [s for s, t in zip(scores, TASK_IDS) if t.startswith("job") or t.startswith("receipt") or t.startswith("multi")],
        "Hard": [s for s, t in zip(scores, TASK_IDS) if any(t.startswith(p) for p in ["invoice", "crossdoc", "temporal", "adversarial", "table", "schemafree", "pii", "hierarchical"])],
    }

    parts = [f"Overall: {avg:.3f}"]
    for cat, cat_scores in categories.items():
        if cat_scores:
            parts.append(f"{cat}: {sum(cat_scores)/len(cat_scores):.3f}")

    print(f"\n[SUMMARY] {' | '.join(parts)}", flush=True)


if __name__ == "__main__":
    main()
