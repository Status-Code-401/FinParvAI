# FinParvAI (நிதிப் பார்வை) — Financial Decision Intelligence

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-007ACC?style=for-the-badge&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![Supabase](https://img.shields.io/badge/Supabase-3ECF8E?style=for-the-badge&logo=supabase&logoColor=white)](https://supabase.com/)


## The Challenge
Small and medium businesses (SMEs), particularly in industries like garment manufacturing, operate with fragmented visibility into upcoming financial obligations, payment timelines, and production-cost trade-offs. Existing tools function merely as static ledgers—they excel at recording historical data but fail to answer the critical operational question: "What exact action should I take today to survive and optimize?"

## Our Solution: A Semi-Autonomous Financial Copilot
FinParvai transforms finance from reactive tracking to proactive decision-making. We don't just show SMEs their finances—we tell them exactly what to do next, how to do it, and how confident they should be in that decision. 

By continuously modeling a user's short-term financial state, monitoring inventory, and projecting liquidity runways, FinParvai acts as a semi-autonomous copilot that identifies risks *before* they occur and generates ready-to-execute recovery actions.

---

## 🚀 NEW: Cost Intelligence v2 (Advanced Financial Guardrails)

We have recently expanded FinParvAI from a "Decision Engine" into a full-scale **Cost Intelligence Suite**. These new modules focus on deep-tissue cost optimization and autonomous risk management:

### 1. Cost Impact Engine (M1)
Beyond identifying a shortfall, the Impact Engine quantifies the **Return on Action**. For every recommendation (e.g., "Delay Vendor X"), it calculates:
*   **Liquidity Benefit:** Exact ₹ improvement to the 14-day runway.
*   **Strategic Weight:** Dynamic adjustment of importance based on the current "Survival Threshold".

### 2. Cost Leakage Detection Engine (M2)
An automated forensic layer that scans transaction history and procurement data to identify hidden losses:
*   **Duplicate Detection:** Identifies double-billing from vendors.
*   **Phantom Subscriptions:** Flags inactive software or utility subscriptions that no longer match operational scale.
*   **Rate Variance:** Alerts when a vendor charges significantly more than the historical average for the same material.

### 3. Enterprise Signal Layer (M4)
FinParvAI now listens to the "Heartbeat" of the factory. It ingests non-financial signals to predict financial volatility:
*   **Production Latency:** If production units drop, the system automatically predicts a revenue shortfall 15 days earlier than bank statements would.
*   **Supply Chain Chokepoints:** Maps vendor lead-time variance to cash-flow predictability.

### 4. Autonomous Execution Layer (M3)
Moving toward full autonomy, this layer categorizes recommendations into:
*   **Auto-Eligible:** Low-risk actions (e.g., "Request early AR collection") that can be executed with one click.
*   **Human-in-the-Loop:** High-impact strategic shifts that require owner review.

---

## Innovation and Uniqueness

FinParvai distinguishes itself through rigorous engineering, combining exact constraint satisfaction with forward-looking intelligence.

### 1. Dual-Model Intelligence (Rare & Powerful)
We architected a distinct separation between survival logic and growth forecasting:
*   **Deterministic Engine:** Provides exact, rule-based actions for current financial constraints. It allocates cash safely, ensuring critical obligations are met without mathematical hallucination.
*   **Predictive Layer:** Utilizes LSTM/SARIMAX time-series forecasting combined with a **Web-Crawling Agent** that ingests external trends (e.g., upcoming festivals, market demand shifts, supply chain news).
*   **The Result:** Impeccable immediate decision accuracy combined with intelligent forward-looking planning.

### 2. Confidence Score for AI Predictions (Trust-Builder)
Financial systems require absolute trust. FinParvai features a self-evaluating feedback loop. Every month, the system automatically compares its previous predictions against the actual recorded financial flow of that month. It then generates a clear **Confidence Score** that is displayed to the user.

### 3. Action-Oriented System
Instead of presenting a dashboard of raw data and leaving the user to deduce a strategy, FinParvai provides clear, prioritized actions. If a cash shortfall is detected, the system outputs explicit directives: "Negotiate a 7-day payment delay with Vendor X," "Pull receivable from Client Y with a 3% incentive," or "Pause non-essential marketing spend."

### 4. Context-Aware Auto Negotiation
Action requires communication. When FinParvai determines a payment must be delayed, it automatically drafts the vendor negotiation email. The strategic approach and linguistic tone dynamically adapt based on the financial context and vendor relationship.

### 5. Smart Financial Calendar View
Financial data is complex; visualizing it shouldn't be. 
*   **Unified Daily Snapshot:** Tracks expenses, income, production costs, and net cash position in a single interface.
*   **Forward Visibility:** Highlights upcoming bills, expected collections, and procurement deliveries perfectly on the timeline.

---

## 📂 Full Project Structure

```text
FinParvAI/
├── backend/                        # FastAPI Core
│   ├── app/                        # Application Source logic
│   │   ├── main.py                 # API Entry and routing
│   │   ├── models/                 # Data schemas & DB interface
│   │   │   ├── schemas.py          # Unified Financial Schema
│   │   │   └── database.py         # Mock-DB & Supabase layer
│   │   ├── routers/                # API Endpoints
│   │   │   ├── financial.py        # Cost Intelligence & Dashboard
│   │   │   └── ingest.py           # Document processing routes
│   │   └── services/               # Modular Intelligence Engines
│   │       ├── decision_engine.py  # M1: Deterministic allocation
│   │       ├── predictive_engine.py# SARIMAX & LSTM Forecasting
│   │       ├── impact_engine.py    # M2: Impact calculation
│   │       ├── leakage_engine.py   # M3: Cost leakage detection
│   │       ├── signal_engine.py    # M4: Operational signals
│   │       ├── execution_engine.py # M5: Autonomous actions
│   │       ├── context_agents.py   # Web crawlers & agents
│   │       ├── data_ingestion.py   # OCR & NLP normalize
│   │       └── email_generator.py  # LLM-based negotiation
│   ├── render.yaml                 # Deployment configuration
│   ├── Dockerfile                  # API containerization
│   └── requirements.txt            # Python dependencies
│
├── frontend/                       # React 18 + TypeScript
│   ├── src/                        # Source Code
│   │   ├── pages/                  # Route-level views
│   │   │   ├── Dashboard.tsx       # KPI Overview
│   │   │   ├── CostIntelligence.tsx# v2 Strategic hub
│   │   │   ├── ForecastPage.tsx    # Predictive analytics
│   │   │   ├── DecisionPage.tsx    # Deterministic insights
│   │   │   ├── ActionsPage.tsx     # Payment negotiation
│   │   │   ├── IngestPage.tsx      # Document upload center
│   │   │   └── Transactions.tsx    # Historical audit trail
│   │   ├── components/             # Reusable UI components
│   │   ├── services/               # Axios/Fetch API client
│   │   ├── styles/                 # Glassmorphism & Global CSS
│   │   ├── types/                  # Shared TS interfaces
│   │   └── App.tsx                 # Root component
│   ├── package.json                # Node dependencies
│   ├── tsconfig.json               # TypeScript config
│   └── vite.config.ts              # Vite build settings
│
├── mock_data/                      # Realistic SME financial datasets
│   ├── financial_state.json        # Unified core state
│   ├── inventory_procurement.json  # Supply chain data
│   └── ledger_summary.json         # Bank transaction history
│
├── supabase/                       # Database migrations & Edge functions
├── docker-compose.yml              # Local orchestration
└── README.md                       # Entry documentation
```

---

## 🛠️ Technology Stack

| Layer | Component | Details |
| :--- | :--- | :--- |
| **Frontend** | UI Framework | React 18, TypeScript, Vite |
| **Frontend** | Visuals | Recharts, Lucide Icons, Glassmorphism CSS |
| **Backend** | API Framework | FastAPI, Pydantic, Python 3.10 |
| **AI/ML** | Forecasting | SARIMAX (Statsmodels), LSTM (PyTorch) |
| **AI/ML** | Explainability | SHAP (Shapley Additive Explanations) |
| **Intelligence** | NLP & Search | LangChain, Gemini Pro, BeautifulSoup4 Spiders |
| **Database** | Core DB | Supabase (PostgreSQL), Edge Functions |

---

## 🔧 Decision Engine Logic (Deterministic)

1. **Cash Flow Simulation** – Simulate 14-day cash position day-by-day.
2. **Runway Calculator** – Determine days until cash goes negative.
3. **Obligation Scoring** – $Score = (0.35 \times Urgency) + (0.30 \times Penalty) + (0.25 \times Type) - (0.10 \times Flexibility)$.
4. **Payment Allocation** – Greedy allocation by score, ensuring zero negative cash flow.
5. **Shortfall Recovery** – Pull AR early → delay flexible AP → cut overheads → liquidate inventory.
6. **Explanation** – Chain-of-Thought reasoning provided for every system decision.

---

## 🚀 Quick Start

### 1. Backend Setup
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```
*API Docs: [http://localhost:8000/docs](http://localhost:8000/docs)*

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
*App: [http://localhost:5173](http://localhost:5173)*

---

## 🔌 Core API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/ingest/upload` | Processes source documents into structured data |
| `POST` | `/api/decision/run` | Executes the deterministic allocation engine |
| `POST` | `/api/predict/forecast` | Generates 30-day revenue and cash flow projections |
| `POST` | `/api/actions/generate` | Creates action plans and communication drafts |
| `GET`  | `/api/cost-intelligence`| Combined v2 metrics for Impact, Leakage, and Signals |

---

## 📊 Evaluation Criteria Coverage

| Criterion              | Implementation                                        |
|------------------------|-------------------------------------------------------|
| Decision Integrity     | Deterministic scoring + greedy allocation algorithm   |
| Strategic Reasoning    | COT explanation + recovery strategy cascade           |
| Cost Optimization      | Leakage detection + Impact quantification (v2)        |
| Operational Signals    | Factory data ingestion + market spiders               |
| Actionable Usability   | Email drafts, payment schedules, one-click UI         |
| Reliability            | Deterministic engine, SHAP explanations, confidence % |

---
**"Empowering SMEs with the financial foresight of an enterprise CFO."**

<img width="1573" height="902" alt="image" src="https://github.com/user-attachments/assets/e95b9669-cbe7-4410-8a50-e79386f6cfbf" />
<img width="1912" height="898" alt="image" src="https://github.com/user-attachments/assets/3e98ec4d-66a2-4f6b-b7fa-3555f85d24d3" />
<img width="1562" height="844" alt="image" src="https://github.com/user-attachments/assets/c115eef5-1189-44e1-ac16-c7d1d87e8ce8" />
<img width="1571" height="903" alt="image" src="https://github.com/user-attachments/assets/20940688-4f45-4bc3-a708-272a2de662d9" />
<img width="1591" height="914" alt="image" src="https://github.com/user-attachments/assets/94f962f6-0497-4fad-a4ce-ba0a43bbe0f1" />
<img width="1575" height="901" alt="image" src="https://github.com/user-attachments/assets/f5524b9d-c925-471c-9454-e6157e7e2b87" />
<img width="1598" height="897" alt="image" src="https://github.com/user-attachments/assets/b55cc4c9-dd28-4949-8a14-cc773cb07bad" />
<img width="1604" height="899" alt="image" src="https://github.com/user-attachments/assets/9ab26d6f-0585-4b59-9000-72c27654104d" />
<img width="1600" height="913" alt="image" src="https://github.com/user-attachments/assets/d2025647-2c2a-436f-bc72-66e65233f9b8" />
<img width="1893" height="908" alt="image" src="https://github.com/user-attachments/assets/c7416ad9-d644-4ab0-b7a9-7f22b353b78c" />
<img width="1576" height="908" alt="image" src="https://github.com/user-attachments/assets/02127a45-0871-45f2-8dac-18f2988d8fcc" />
<img width="1559" height="891" alt="image" src="https://github.com/user-attachments/assets/893fdca0-7bcb-4bfe-9997-b7857b1a8520" />
<img width="1597" height="911" alt="image" src="https://github.com/user-attachments/assets/453dddaa-95a9-4aa1-b068-9e8db992cc28" />
<img width="1579" height="910" alt="image" src="https://github.com/user-attachments/assets/5e9e6faa-141a-433c-bbf4-1e2a7bdd5035" />
<img width="1594" height="920" alt="image" src="https://github.com/user-attachments/assets/056147b5-8518-4ed8-b092-6fe4f50b1cb5" />
<img width="1602" height="913" alt="image" src="https://github.com/user-attachments/assets/e4194bc0-8c18-4b31-9f7b-c4c08a894268" />
<img width="1602" height="895" alt="image" src="https://github.com/user-attachments/assets/4b74715c-a581-45f1-866d-6e47cdfab72c" />
<img width="1574" height="853" alt="image" src="https://github.com/user-attachments/assets/f7d2b07a-6894-41f6-8019-8ffce0549341" />
<img width="1598" height="915" alt="image" src="https://github.com/user-attachments/assets/08b97f4f-6b81-4945-9e2c-5e5e0586b7cc" />
<img width="1592" height="914" alt="image" src="https://github.com/user-attachments/assets/076ead38-91d4-4591-b550-16ac6a9afbe4" />
<img width="1275" height="801" alt="image" src="https://github.com/user-attachments/assets/95ad6f31-5514-4720-a881-9db24b430e19" />

