"""
Inference script for DataExtract environment.
Runs baseline evaluation across all tasks (easy/medium/hard).
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
    "contact_01", "contact_02", "contact_03", "contact_04",
    "ticket_01", "ticket_02",
    "job_01", "job_02", "job_03", "job_04",
    "receipt_01", "receipt_02", "receipt_03",
    "invoice_01", "invoice_02", "invoice_03", "invoice_04",
]

SYSTEM_PROMPT = textwrap.dedent("""
You are a structured data extraction agent. Given unstructured text and a target schema,
output ONLY a valid JSON object with the requested fields. No explanation, no markdown.

Rules:
- Output raw JSON only. Never wrap in ```json blocks or add commentary.
- Match field names exactly as specified in the schema.
- For lists of strings, use JSON arrays: ["item1", "item2"]
- For lists of objects (like line_items), use: [{"field": "value"}, ...]
- For null/unknown values, use null (not "null", not "N/A", not "").
- Numbers must be numeric types, not strings. 140000 not "140,000".
- Copy proper nouns, emails, phone numbers exactly from the text.
- For line items: quantity=1 for flat fees/lump sums; unit_price=total for single items.

Example input:
  TEXT: "Invoice #A-99, from Acme Corp, 1 Widget @ $5 = $5, Tax 10%: $0.50, Total: $5.50"
  SCHEMA: "Extract: invoice_number, vendor_name, line_items (description, quantity, unit_price, total), subtotal, tax_rate, tax_amount, total_due"

Example output:
  {"invoice_number":"A-99","vendor_name":"Acme Corp","line_items":[{"description":"Widget","quantity":1,"unit_price":5.0,"total":5.0}],"subtotal":5.0,"tax_rate":10.0,"tax_amount":0.5,"total_due":5.5}
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
        user_msg += f"\n\nFEEDBACK FROM PREVIOUS ATTEMPT:\n{feedback}\n\nFix the issues above and output the corrected JSON."

    resp = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_msg},
        ],
        temperature=0.0,
        max_tokens=2000,
    )
    text = (resp.choices[0].message.content or "").strip()
    # Strip markdown fences if model adds them
    if text.startswith("```"):
        text = text.split("\n", 1)[-1]
    if text.endswith("```"):
        text = text.rsplit("```", 1)[0]
    return text.strip()


def run_task(client, task_id):
    log_start(task=task_id, env=BENCHMARK, model=MODEL_NAME)
    rewards, steps, best_score = [], 0, 0.0

    try:
        resp = requests.post(f"{ENV_URL}/reset", json={"task_id": task_id}, timeout=30)
        data = resp.json()
        obs = data["observation"]
        feedback = ""

        for step in range(1, MAX_STEPS + 1):
            extraction = call_model(client, obs["raw_text"], obs["schema_description"], feedback)
            resp = requests.post(f"{ENV_URL}/step", json={"extracted_json": extraction}, timeout=30)
            data = resp.json()
            obs = data["observation"]
            reward, done = data["reward"], data["done"]

            rewards.append(reward)
            steps = step
            best_score = obs["score"]
            feedback = obs["feedback"]

            log_step(step=step, action=f"extract({task_id})", reward=reward, done=done, error=None)
            if done:
                break

    except Exception as e:
        print(f"[DEBUG] Error in task {task_id}: {e}", flush=True)

    score = min(max(best_score, 0.0), 1.0)
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
            scores.append(0.0)

    avg = sum(scores) / len(scores) if scores else 0.0
    easy = [s for s, t in zip(scores, TASK_IDS) if t.startswith("contact") or t.startswith("ticket")]
    med = [s for s, t in zip(scores, TASK_IDS) if t.startswith("job") or t.startswith("receipt")]
    hard = [s for s, t in zip(scores, TASK_IDS) if t.startswith("invoice")]

    print(f"\n[SUMMARY] Overall: {avg:.3f} | Easy: {sum(easy)/max(len(easy),1):.3f} | Medium: {sum(med)/max(len(med),1):.3f} | Hard: {sum(hard)/max(len(hard),1):.3f}", flush=True)


if __name__ == "__main__":
    main()
