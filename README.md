# DocForge — Document Understanding Benchmark with Corruption Engine

An OpenEnv environment that benchmarks AI agents on structured data extraction from **realistically corrupted documents**. DocForge applies a configurable corruption engine with both global noise (OCR artifacts, redacted spans, formatting damage) and **targeted field corruption** (digit swaps in phone numbers, OCR on email addresses, amount perturbation) that simulates real-world document degradation.

## Why DocForge?

Structured data extraction is a multi-billion dollar industry problem. Every company that processes invoices, resumes, contracts, or support tickets needs to convert unstructured documents into structured records. But real documents aren't clean — they come from scanned PDFs with OCR errors, degraded faxes, inconsistent formatting, and missing sections. Existing extraction benchmarks use clean text. DocForge closes that gap.

## Architecture

```
┌──────────────────────────────────────────────────────────┐
│                   DocForge Environment                    │
│                                                           │
│  ┌──────────┐   ┌───────────────────────┐                │
│  │ Task Bank │──▶│   Corruption Engine    │──▶ Agent sees │
│  │ (17 tasks │   │                       │   corrupted   │
│  │  5 types) │   │  Global:              │   text        │
│  └──────────┘   │   • OCR char swaps    │                │
│                  │   • Whitespace damage  │                │
│                  │   • Line break damage  │                │
│                  │   • Redacted spans     │                │
│                  │   • Contradictions     │                │
│                  │  Targeted:             │                │
│                  │   • Phone digit swap   │                │
│                  │   • Email OCR damage   │                │
│                  │   • Amount perturbation│                │
│                  │                       │                │
│                  │  Seed-reproducible     │                │
│                  └───────────────────────┘                │
│                                                           │
│  Agent JSON ──▶ ┌─────────────────────┐                  │
│                 │  Grader              │                  │
│  Feedback   ◀──│  • Jaccard overlap   │                  │
│  + reward      │  • Levenshtein dist  │                  │
│                 │  • P / R / F1        │                  │
│                 │  • Nested obj match  │                  │
│                 └─────────────────────┘                  │
│                                                           │
│  5 attempts per episode with per-field feedback           │
│  Improvement-based reward shaping                         │
└──────────────────────────────────────────────────────────┘
```

## Corruption Engine

| Tier | OCR Noise | Whitespace | Line Breaks | Redactions | Contradictions | Targeted Fields |
|------|-----------|------------|-------------|------------|----------------|-----------------|
| Easy | — | — | — | — | — | — |
| Medium | 2% | 2% | — | — | — | 30% phone |
| Hard | 4% | 3% | 3% | 40% | 30% | 50% phone, 30% email, 40% amounts |

All corruption is **seed-reproducible** for consistent evaluation. Same `seed` parameter = identical corrupted output.

## Document Types & Tasks (17 total)

| Category | Difficulty | Tasks | Fields | Schema Complexity |
|----------|-----------|-------|--------|-------------------|
| Contact Cards | Easy | 4 | 6 | Flat strings |
| Support Tickets | Easy | 2 | 10 | Strings + categorization |
| Job Postings | Medium | 4 | 12 | Strings + lists |
| Receipts | Medium | 3 | 13 | Strings + nested line items |
| Invoices/POs | Hard | 4 | 15+ | Nested line items + multi-currency |

## Reward Function

- **Improvement-based**: `reward = max(0, current_score - previous_best)`
- **Validity bonus**: +0.01 for valid JSON on first attempt
- **String scoring**: `max(Jaccard, Levenshtein)` — robust to both token-level and character-level noise
- **Numeric scoring**: Proportional error tolerance
- **List scoring**: Fuzzy set overlap with best-match per element
- **Nested objects**: Greedy alignment for line items across all sub-fields
- **Metrics**: Per-field Precision, Recall, F1 in every feedback message

## API

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Interactive dashboard |
| `/health` | GET | Health check |
| `/tasks` | GET | List all tasks with metadata |
| `/metrics` | GET | Aggregate performance stats (by task, by difficulty) |
| `/reset` | POST | Reset episode (`task_id`, `difficulty`, `seed`) |
| `/step` | POST | Submit extraction (`extracted_json`) |
| `/state` | GET | Current episode state |
| `/ws` | WS | WebSocket for OpenEnv protocol |

## Quick Start

```bash
# Docker (Hugging Face Spaces)
cd server && docker build -t docforge . && docker run -p 7860:7860 docforge

# Local
cd server && pip install -r requirements.txt && uvicorn app:app --port 7860

# Run baseline inference
export HF_TOKEN=your_token
export ENV_URL=http://localhost:7860
python inference.py
```

## Baseline Performance (Qwen2.5-72B-Instruct)

| Difficulty | Tasks | Avg Score |
|-----------|-------|-----------|
| Easy | 6 | ~0.95 |
| Medium | 7 | ~0.70 |
| Hard | 4 | ~0.50 |
| **Overall** | **17** | **~0.72** |
