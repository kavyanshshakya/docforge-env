# DocForge — Document Understanding Benchmark with Corruption Engine

An OpenEnv environment that benchmarks AI agents on structured data extraction from realistically corrupted documents. 31 tasks across 9 capabilities with a corruption engine, specialized grading modes, and seed-reproducible noise.

## Architecture

```
                        ┌──────────────────────────┐
  Task Bank (31 tasks) ─┤   Corruption Engine      ├─▶ Agent sees corrupted text
  9 capabilities        │  OCR · Redaction · Phone │
                        │  Email · Amount · Seeded │
                        └──────────────────────────┘
                                    │
  Agent submits JSON ──▶ ┌───────────────────────┐
                         │  Grader (4 modes)     │
  Feedback + reward  ◀── │  basic · confidence   │
                         │  schema_free · pii    │
                         │  P / R / F1 per field │
                         └───────────────────────┘
```

## 9 Capabilities

| # | Capability | Tasks | What it tests |
|---|-----------|-------|---------------|
| 1 | Basic Extraction | 17 | Contacts, tickets, jobs, receipts, invoices |
| 2 | Multilingual | 3 | German invoices, Japanese receipts, Spanish job postings |
| 3 | Cross-Doc Reconciliation | 2 | Compare PO vs Invoice, flag discrepancies |
| 4 | Confidence Calibration | 1 | Extract + rate certainty per field |
| 5 | Schema-Free Discovery | 1 | No schema provided, agent discovers fields |
| 6 | Temporal Reasoning | 2 | Compute deadlines, rent increases, vesting dates |
| 7 | Adversarial | 2 | Misleading context, voided documents |
| 8 | Table Reconstruction | 1 | Mangled text-serialized tables |
| 9 | PII Detection | 1 | Extract + flag HIPAA/GDPR sensitive fields |
| 10 | Hierarchical Parsing | 1 | Email containing forwarded invoice |

## Corruption Engine

Realistic document noise that scales with difficulty. Seed-reproducible.

| Tier | Global | Targeted |
|------|--------|----------|
| Easy | None | None |
| Medium | 2% OCR, 2% whitespace | 30% phone digit swap |
| Hard | 4% OCR, 3% whitespace, 3% line breaks, 40% redaction, 30% contradictions | 50% phone, 30% email, 40% amounts |

## Grading

4 specialized grading modes dispatched by task type:

- **basic**: Jaccard + Levenshtein dual scoring, P/R/F1, nested object alignment
- **confidence**: 60% value accuracy + 40% calibration score
- **schema_free**: Fuzzy key matching (agent invents field names)
- **pii**: 60% extraction + 40% PII detection F1

All modes: 5 iterative attempts with per-field feedback. Improvement-based reward shaping.

## API

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Interactive dashboard |
| `/health` | GET | Health check |
| `/tasks` | GET | List all 31 tasks |
| `/metrics` | GET | Aggregate performance stats |
| `/reset` | POST | Reset episode (task_id, difficulty, seed) |
| `/step` | POST | Submit extraction (extracted_json) |
| `/state` | GET | Current episode state |
| `/ws` | WS | WebSocket for OpenEnv protocol |

## Quick Start

```bash
cd server && pip install -r requirements.txt && uvicorn app:app --port 7860
```

```bash
export HF_TOKEN=your_token
export ENV_URL=http://localhost:7860
python inference.py
```

## Links

- Space: https://huggingface.co/spaces/kavyanshshakya/docforge-env
- GitHub: https://github.com/kavyanshshakya/docforge-env
