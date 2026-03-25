# FinParvai – Financial Decision Intelligence System

> Semi-autonomous financial copilot for SMEs. Track obligations, predict shortfalls, allocate payments, generate actions.

---

## Architecture

```
finparvai/
├── backend/          # FastAPI (Python)
│   ├── main.py
│   ├── models/schemas.py
│   ├── routers/
│   │   ├── ingest.py      # Document upload, OCR, normalization
│   │   ├── decision.py    # Deterministic decision engine
│   │   ├── predict.py     # Predictive forecast engine
│   │   └── actions.py     # Action plan + email generation
│   └── services/
│       ├── decision_engine.py   # Core deterministic logic
│       ├── predict_engine.py    # Revenue/cash forecasting + SHAP
│       ├── ingest_service.py    # OCR + document parsing
│       └── action_service.py   # Email drafts + payment scheduling
│
└── frontend/         # React + TypeScript
    └── src/
        ├── App.tsx
        ├── styles.css
        ├── types/index.ts
        ├── utils/api.ts
        └── pages/
            ├── Dashboard.tsx    # Financial overview + charts
            ├── IngestPage.tsx   # Document upload + demo state
            ├── DecisionPage.tsx # Decision engine + scoring
            ├── ForecastPage.tsx # Predictive forecasts + SHAP
            └── ActionsPage.tsx  # Payment schedule + email drafts
```

---

## Quick Start

### 1. Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

API docs: http://localhost:8000/docs

### 2. Frontend

```bash
cd frontend
npm install
npm start
```

App: http://localhost:3000

---

## API Endpoints

| Method | Path                         | Description                            |
|--------|------------------------------|----------------------------------------|
| GET    | /api/ingest/demo-state       | Get realistic demo financial state     |
| POST   | /api/ingest/upload           | Upload document (PDF/CSV/Image)        |
| POST   | /api/ingest/normalize        | Normalize & validate financial state   |
| POST   | /api/decision/run            | Run full deterministic decision engine |
| POST   | /api/decision/simulate       | Simulate cash flow projection          |
| POST   | /api/decision/score-payables | Score and rank payables by priority    |
| POST   | /api/predict/forecast        | Generate revenue + cash flow forecast  |
| POST   | /api/actions/generate        | Generate action plan + email drafts    |
| GET    | /health                      | Health check                           |

---

## Core Financial State Schema

```json
{
  "cash_balance": 45000,
  "payables":     [{ "vendor": "...", "amount": 15000, "due_date": "2026-03-27", "type": "critical" }],
  "receivables":  [{ "client": "...", "amount": 30000, "expected_date": "2026-03-28", "collection_probability": 0.85 }],
  "overheads":    [{ "type": "electricity", "amount": 3000, "essential": true }],
  "inventory_status": [{ "item": "Cotton Fabric", "available_quantity": 500, "required_quantity": 300, "shortage": 0, "excess": 200 }]
}
```

---

## Decision Engine Logic

1. **Cash Flow Simulation** – Simulate 14-day cash position day-by-day
2. **Runway Calculator** – Days until cash goes negative
3. **Obligation Scoring** – Score = (0.35×urgency) + (0.30×penalty) + (0.25×type) − (0.10×flexibility)
4. **Payment Allocation** – Greedy allocation by score, no overspending
5. **Shortfall Recovery** – Pull AR early → delay flexible AP → cut overheads → liquidate inventory
6. **Explanation** – Chain-of-Thought reasoning for every decision

---

## Tech Stack

| Layer      | Technology                               |
|------------|------------------------------------------|
| Frontend   | React 18, TypeScript, Recharts           |
| Backend    | FastAPI, Pydantic v2, Uvicorn            |
| OCR        | Mock (plug in Google Vision / Textract)  |
| Parsing    | Rule-based + regex (plug in LangChain)   |
| Forecasting| Deterministic wave model (plug in LSTM)  |
| DB         | Supabase (configure via env vars)        |

---

## Environment Variables (backend)

```env
GOOGLE_VISION_API_KEY=...      # For production OCR
OPENAI_API_KEY=...             # For LLM parsing
SUPABASE_URL=...
SUPABASE_KEY=...
```

---

## Evaluation Criteria Coverage

| Criterion              | Implementation                                        |
|------------------------|-------------------------------------------------------|
| Decision Integrity     | Deterministic scoring + greedy allocation algorithm   |
| Strategic Reasoning    | COT explanation + recovery strategy cascade           |
| Data Robustness        | OCR pipeline, CSV parsing, multi-format support       |
| System Architecture    | Separated decision logic from AI output generation    |
| Actionable Usability   | Email drafts, payment schedules, one-click UI         |
| Reliability            | Deterministic engine, SHAP explanations, confidence % |
