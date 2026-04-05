## **FinParvai – Financial Decision Intelligence System**

---

# **1. Problem Statement**

Small businesses (SMEs), especially in industries like garments, lack visibility into:

- Upcoming financial obligations
- Payment timelines
- Trade-offs between competing expenses

As a result:

- Cash shortfalls occur
- Payments get delayed
- Decisions are reactive instead of proactive

Existing tools only **record and report data**, but do not provide:

*“What should I do now?”*

---

# **2. Product Vision**

To build a **semi-autonomous financial copilot** that:

- Understands fragmented financial data
- Predicts risks and opportunities
- Recommends **clear, actionable decisions**
- Continuously improves using feedback (confidence scoring)

---

# **3. Core Features**

# **3.1 Multimodal Data Ingestion, Normalization & Operational Structuring**

---

## **Objective**

To ingest fragmented financial and operational data from multiple sources and transform it into a **comprehensive, structured financial-operational model** that includes:

- Cash balance and transaction history
- Accounts Payable (AP) and Receivable (AR)
- Vendor-level obligations and payment timelines
- Inventory procurement and production data
- Cost breakdown (internal + external)
- Timing insights (lead time, payment cycles)

This structured model will act as the **core input for the deterministic decision engine**, enabling precise scheduling, cost optimization, and cash flow management.

---

# 🧩 **Input Sources**

---

## 1. Bank Statements

- Format: CSV / PDF
- Data extracted:
    - Transaction history
    - Credits (income)
    - Debits (expenses)
    - Running balance

---

## 2. Digital Invoices

- Format: PDF / Image
- Data extracted:
    - Vendor / Client
    - Amount
    - Due date
    - Payment terms

---

## 3. Receipts (Physical / Handwritten)

- Format: Image
- Data extracted:
    - Expense type
    - Amount
    - Date
    - Category (inferred)

---

## 4. Ledger Data (Direct Input / DB)

- Contains:
    - Historical income
    - Vendor payments
    - Client payments
- Used for:
    - Validation
    - Pattern detection
    - Payment cycle analysis

---

## 5. Inventory & Procurement Data (Mock API)

### Contains:

- Vendor name
- Material type
- Quantity
- Unit cost
- Order date
- Delivery date

---

## 🏭 6. Production Data

- Units produced per day
- Cost per unit
- Material usage

---

# **End-to-End Processing Pipeline**

---

## **Step 1: Data Upload & Storage**

### Tech Stack:

- Frontend: **React + TypeScript**
- Backend: **FastAPI**
- Storage:
    - **Supabase Storage / AWS S3**

### Function:

- Upload and store:
    - PDFs, images, CSVs
- Assign document IDs

---

## 🪜 **Step 2: Document Classification**

### 🔧 Tools:

- Rule-based (MVP)
- Optional: HuggingFace classifier

### Output:

- Document type:
    - Bank / Invoice / Receipt

---

## 🪜 **Step 3: OCR & Data Extraction**

### 🔧 Tools:

### Primary:

- **Google Vision API / AWS Textract**

### Fallback:

- **Tesseract OCR**

---

### Output:

- Raw text
- Semi-structured key-value pairs

---

## **Step 4: Intelligent Parsing & Structuring**

---

### 🔧 Core Tools:

- **LangChain + LLM (Gemini/OpenAI)**
- **spaCy (NER)**
- **Regex (rule-based extraction)**

---

### Responsibilities:

- Extract:
    - Amount
    - Date
    - Vendor / Client
- Classify:
    - Income
    - Expense
    - Payable
    - Receivable

---

## **Step 5: Ledger Integration Layer**

---

### Function:

- Merge parsed data with ledger

### Output:

- Verified:
    - Income history
    - Payment cycles
    - Vendor relationships

---

## **Step 6: Inventory & Procurement Structuring**

---

### 🔧 Tools:

- FastAPI (API integration)
- Python processing

---

### Extract:

- Vendor-wise purchases
- Order timelines
- Material cost

---

### Compute:

- Lead time
- Purchase frequency
- Vendor reliability

---

## 🪜 **Step 7: Production & Cost Modeling**

---

### Compute:

### Internal Costs:

- Production cost = unit cost × units

### External Costs:

- Vendor payments
- Logistics
- Marketing

---

## **Step 8: Data Normalization**

---

### Objective:

Unify all data into a **single schema**

---

# **FINAL STRUCTURED OUTPUT (COMPLETE MODEL)**

---

```
{
  "cash_balance": 45000,

  "transactions": [],

  "payables": [
    {
      "vendor": "ABC Textiles",
      "amount": 15000,
      "due_date": "2026-03-25",
      "penalty": "medium",
      "type": "external",
      "linked_orders": ["order_101"],
      "priority_score": 0.7
    }
  ],

  "receivables": [
    {
      "client": "XYZ Retail",
      "amount": 30000,
      "expected_date": "2026-03-28",
      "collection_probability": 0.8
    }
  ],

  "overheads": [
    {
      "type": "ads",
      "amount": 5000,
      "essential": false
    },
    {
      "type": "electricity",
      "amount": 3000,
      "essential": true
    }
  ],

  "ledger_summary": {
    "monthly_income": 120000,
    "monthly_expense": 100000,
    "avg_payment_cycle_days": 7
  },

  "inventory_procurement": [
    {
      "order_id": "order_101",
      "vendor": "ABC Textiles",
      "material": "Fabric",
      "quantity": 500,
      "unit_cost": 50,
      "total_cost": 25000,
      "order_date": "2026-03-10",
      "delivery_date": "2026-03-13",
      "lead_time": 3,
      "status": "pending"
    }
  ],

  "inventory_status": [
    {
      "item": "fabric",
      "available_quantity": 500,
      "required_quantity": 300,
      "shortage": 0,
      "excess": 200
    }
  ],

  "vendor_insights": [
    {
      "vendor": "ABC Textiles",
      "total_orders": 5,
      "avg_lead_time": 3,
      "payment_delay_avg": 2,
      "reliability_score": 0.85,
      "cost_efficiency_score": 0.7
    }
  ],

  "production": {
    "daily_output": {
      "monday": 120,
      "tuesday": 100
    },
    "cost_per_unit": 100
  },

  "cost_breakdown": {
    "internal": 10000,
    "external": 25000
  }
}
```

---

# **Key Outputs Generated**

 Financial Layer:

---

- Cash balance
- Transaction history
- AP / AR

---

## Operational Layer:

- Inventory lifecycle
- Vendor insights
- Production costs

---

## Temporal Layer:

- Payment cycles
- Lead times
- Cash flow timing

---

# **Tech Stack Summary**

| Layer | Tools |  |
| --- | --- | --- |
| Frontend | React + TypeScript |  |
| Backend | FastAPI |  |
| OCR | Google Vision / Textract |  |
| Parsing | LangChain + LLM |  |
| NLP | spaCy |  |
| Processing | Python |  |
| DB | Supabase |  |
| Vector DB | Pinecone |  |
| Storage | Supabase Storage |  |
|  |  |  |

# **DETERMINISTIC DECISION ENGINE – PRD**

---

## **1. Objective**

Design a **fully deterministic financial decision engine** that:

- Tracks **cash, receivables (AR), payables (AP), overheads, inventory**
- Simulates **future cash position**
- Detects **cash shortages before they occur**
- Prioritizes and allocates **payments optimally**
- Applies **guaranteed fallback strategies** to prevent failure
- Generates **actionable outputs (plans, emails, explanations)**

---

## **2. Design Principles (CRITICAL)**

- **Deterministic:** Same input → same output
- **Constraint-first:** Survival (no negative cash) > optimization
- **Priority-driven:** Critical obligations always handled first
- **Fallback-safe:** Always provides a recovery plan
- **Explainable:** Every decision must have a reason

---

## **3. Core Inputs**

```
{
  "cash":10000,
  "receivables": [
    {"client":"A", "amount":15000, "due":"2026-03-28"}
  ],
  "payables": [
    {"vendor":"X", "amount":8000, "due":"2026-03-26", "type":"critical"},
    {"vendor":"Y", "amount":12000, "due":"2026-03-27", "type":"flexible"}
  ],
  "overheads": [
    {"type":"ads", "amount":5000, "essential":false},
    {"type":"electricity", "amount":3000, "essential":true}
  ],
  "inventory": [
    {"item":"fabric", "quantity":100, "required":60}
  ]
}
```

---

# 🔧 **4. Engine Components**

---

## 🔹 **4.1 Cash Flow Simulator**

### 🎯 Purpose:

Simulate future liquidity across a time window (e.g., 7–30 days)

### 🧮 Logic:

```
For each day:
    cash += receivables_due_today
    cash -= payables_due_today
    cash -= overheads_due_today
```

### 📤 Output:

- Daily cash projection
- First negative day (if any)

---

## 🔹 **4.2 Runway Calculator**

### 🎯 Purpose:

Determine **days to zero cash**

```
If cash < 0:
    return day_index
Else:
    return "safe"
```

---

## 🔹 **4.3 Obligation Scoring Model**

### 🎯 Purpose:

Rank payables deterministically

---

### 📊 Factors:

| Factor | Meaning |
| --- | --- |
| Urgency | Days until due |
| Penalty | Cost of missing payment |
| Flexibility | Ability to delay |
| Type | Critical vs non-critical |

---

### 🧮 Score:

```
score = (W1 * urgency) + (W2 * penalty) + (W3 * type_priority) - (W4 * flexibility)
```

---

### 🔒 Deterministic Rules:

- Critical payments always get top priority
- Equal scores → earlier due date wins

---

## 🔹 **4.4 Payment Allocation Engine (CORE)**

### 🎯 Purpose:

Allocate available cash safely

---

### 🧠 Algorithm:

```
Sort payables by score DESC

For each payable:
    If cash >= amount:
        pay fully
        cash -= amount
    Else if cash > 0:
        partial payment (if allowed)
        mark remaining as delayed
        cash = 0
    Else:
        mark as delayed
```

---

### 🔒 Guarantees:

- No overspending
- No negative cash
- Critical obligations handled first

---

## 🔹 **4.5 Shortfall Handling Engine**

### 🎯 Trigger:

```
If projected_cash < 0:
```

---

### 🧠 Recovery Strategy (STRICT ORDER)

---

### ✅ 1. Pull Receivables Early

```
Sort receivables by amount DESC

For each:
    suggest early payment incentive (e.g., 5%)
    reduce shortfall
```

---

### ✅ 2. Delay Flexible Payables

```
If flexibility > threshold:
    reschedule payment
```

---

### ✅ 3. Reduce Overheads

```
For overhead:
    If non-essential:
        reduce or pause
```

---

### ✅ 4. Inventory Optimization (JIT + Liquidation)

### a. Delay Purchases (JIT)

```
If inventory not immediately required:
    delay procurement
```

### b. Reduce Excess Inventory

```
If quantity > required:
    mark as excess
    suggest liquidation
```

### c. Adjust Production

```
If low cash:
    reduce production temporarily
```

---

### ✅ 5. Partial Payments

```
If unavoidable:
    allocate partial funds to high-priority obligations
```

---

### 🔒 Final Guarantee:

System **must always return a feasible plan** combining above strategies

---

## 🔹 **4.6 Overhead Optimization Engine**

### 🎯 Purpose:

Minimize cash outflow

---

### 🧠 Rules:

| Type | Action |
| --- | --- |
| Ads | Reduce |
| Travel | Delay |
| Utilities | Keep |
| Salaries | Keep |

---

---

## 🔹 **4.7 Inventory Optimization Engine**

### 🎯 Purpose:

Unlock cash from inventory

---

### 🧠 Rules:

- Apply **Just-In-Time (JIT)** purchasing
- Identify **dead stock**
- Prioritize **essential materials only**

---

### 📤 Outputs:

- “Delay raw material purchase by 4 days”
- “Liquidate excess inventory worth ₹10,000”

---

## 🔹 **4.8 Action Generator**

### 🎯 Convert decisions into actions

---

### 📤 Outputs:

### Payment Plan:

```
{
  "pay_now": ["Electricity"],
  "delay": ["Vendor Y"],
  "partial": ["Vendor X"]
}
```

---

### Emails:

- Client → early payment request
- Vendor → delay request

---

## 🔹 **4.9 Explainability Layer**

### 🎯 Purpose:

Provide reasoning

---

### Example:

> “Electricity bill prioritized due to high penalty. Vendor Y delayed due to flexibility. Inventory purchase postponed to conserve cash.”
> 

---

---

# ⚠️ **5. EDGE CASE HANDLING**

---

### ❗ No Receivables

→ Use delay + overhead + inventory strategies

---

### ❗ All Payables Critical

→ Partial payments + cost reduction

---

### ❗ High Future Inflow

→ Delay safely until inflow

---

### ❗ Zero Cash Scenario

→ Full fallback:

- Delay all flexible payments
- Stop non-essential overhead
- Trigger emergency receivable collection

---

---

# 🔄 **6. FULL EXECUTION FLOW**

```
Input Financial Data
        ↓
Normalize Data
        ↓
Simulate Cash Flow
        ↓
Detect Shortfall
        ↓
Score Payables
        ↓
Allocate Payments
        ↓
Apply Recovery Strategies
        ↓
Generate Actions
        ↓
Generate Explanation
```

---

# 🎯 **7. OUTPUT TO USER**

---

### 📊 Dashboard:

- Cash balance
- Days to zero
- Risk level

---

### 💡 Recommendations:

- Early collection suggestions
- Payment delays
- Cost reductions
- Inventory optimization

---

### ✉️ Actions:

- Email drafts
- Payment scheduling

---

---

# **Predictive (Non-Deterministic) Engine**

## **Objective**

The Predictive Engine provides **forward-looking financial insights** by combining historical financial data with external contextual signals.

It acts as an **advisory layer** that forecasts future states (revenue, demand, cash flow) and recommends strategic actions, without overriding the deterministic decision engine.

---

## **Inputs**

### **1. Internal Financial Data**

- Historical transactions (debits/credits)
- Accounts Receivable (AR) history
- Accounts Payable (AP) history
- Cash balance trends
- Sales and revenue data
- Inventory levels and usage patterns

### **2. External Contextual Data (via Web Crawling Agent)**

- Festival calendars (e.g., Diwali, Pongal)
- Market demand indicators
- Industry-specific trends (garment sector)
- News and macroeconomic signals

### **3. Current State Snapshot**

- Current cash balance
- Active obligations (payables)
- Expected receivables
- Inventory position

---

## **Data Processing Pipeline**

### **Step 1: Data Aggregation**

- Combine structured financial data with unstructured external signals
- Align all inputs on a **common time axis (daily granularity)**

### **Step 2: Feature Engineering**

- Generate features such as:
    - Daily/weekly revenue trends
    - Seasonality indicators (festival flags, periodic spikes)
    - Cash flow volatility
    - Payment delays and collection patterns
- Encode external signals into **quantifiable variables** (e.g., demand multipliers)

---

## **Modeling Approach**

### **1. Time-Series Forecasting Models**

- **LSTM (Long Short-Term Memory)**
    - Captures sequential dependencies in revenue, demand, and cash flow
- **SARIMAX**
    - Models seasonality and incorporates exogenous variables (external signals)

### **2. Statistical Enhancements**

- Moving averages, trend decomposition
- Lag-based features (previous day/week/month behavior)

### **3. Explainability**

- **SHAP (SHapley Additive exPlanations)** used to:
    - Identify feature contribution to predictions
    - Provide human-readable reasoning (e.g., “festival demand increased forecast by 18%”)

---

## **Agent-Based Context Enrichment**

### **1. Web Crawling Agent**

- Continuously retrieves external signals (festivals, trends, news)

### **2. Context Analysis Agent**

- Processes crawled data and identifies:
    - Seasonal patterns
    - Demand shifts
    - Market signals relevant to the garment industry

### **3. Integration Layer**

- Converts extracted insights into structured inputs for forecasting models
- Example:
    - “Festival upcoming” → demand multiplier = 1.3

---

## **Forecast Outputs**

The engine generates the following projections (time horizon: configurable, default 30 days):

- **Revenue Forecast**
- **Demand Forecast**
- **Inventory Requirement Forecast**
- **Accounts Receivable (AR) Forecast**
- **Accounts Payable (AP) Forecast**
- **Cash Flow Projection (daily timeline)**

---

## **Derived Financial Insights**

From the forecasts, the system computes:

- Expected **cash surplus or shortfall periods**
- Projected **liquidity runway changes**
- Inventory sufficiency vs demand
- Risk indicators (e.g., high dependency on uncertain receivables)

---

## **Action Recommendation Layer**

Based on predicted scenarios, the system generates **advisory recommendations**, such as:

- Increase procurement before expected demand surge
- Reduce discretionary spending during low-revenue periods
- Accelerate receivables collection to avoid projected shortfall
- Defer non-critical expenses

Each recommendation includes:

- Context (why the action is suggested)
- Expected impact (e.g., improved cash position)

---

## **System Features**

### **1. Retrieval-Augmented Generation (RAG)**

- Uses **Vector Database** to store:
    - Historical financial patterns
    - Past forecasts and outcomes
- Enables contextual retrieval for improved reasoning and explanations

### **2. Multi-Agent Orchestration**

- Modular agents for:
    - Data collection (web crawling)
    - Context analysis
    - Forecast generation
- Coordinated via pipeline (e.g., LangChain-based orchestration)

### **3. Model Execution**

- ML models consume:
    - Processed financial data
    - Agent-derived contextual features
- Outputs are stored in a structured database

---

## **Output Delivery**

- Predictions and insights are:
    - Stored in the system database
    - Displayed on the dashboard
    - Accompanied by **clear explanations (via SHAP + contextual reasoning)**

---

## **Key Characteristics**

- **Advisory in nature** (does not override deterministic decisions)
- **Explainable** (transparent reasoning for predictions)
- **Context-aware** (integrates external signals)
- **Industry-adapted** (tailored for garment business patterns)

---

## **Outcome**

The Predictive Engine enables users to:

- Anticipate financial risks before they occur
- Align operations (inventory, spending) with future demand
- Transition from reactive decisions to **proactive financial planning**
