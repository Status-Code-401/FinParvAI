-- ============================================================
-- FinParvai — Supabase Schema
-- Run this in the Supabase SQL Editor (Dashboard → SQL Editor)
-- ============================================================

-- ── businesses ───────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS businesses (
    id                      BIGSERIAL PRIMARY KEY,
    name                    TEXT NOT NULL DEFAULT 'Sri Lakshmi Garments',
    owner                   TEXT,
    gstin                   TEXT,
    industry                TEXT,
    location                TEXT,
    established             DATE,
    cash_balance            NUMERIC(14,2) NOT NULL DEFAULT 0,
    cost_per_unit           NUMERIC(10,2) DEFAULT 95,
    selling_price_per_unit  NUMERIC(10,2) DEFAULT 185,
    monthly_target          INT DEFAULT 2200,
    -- Added fields for cost_breakdown and production summaries
    internal_monthly_obligation  NUMERIC(14,2) DEFAULT 0,
    external_monthly_obligation  NUMERIC(14,2) DEFAULT 0,
    total_monthly_obligation     NUMERIC(14,2) DEFAULT 0,
    production_avg_per_day       INT DEFAULT 0,
    production_yesterday         INT DEFAULT 0,
    production_today_estimate    INT DEFAULT 0,
    created_at              TIMESTAMPTZ DEFAULT NOW(),
    updated_at              TIMESTAMPTZ DEFAULT NOW()
);

-- ── ledger_summaries ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS ledger_summaries (
    id                      BIGSERIAL PRIMARY KEY,
    business_id             BIGINT NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    period                  TEXT,
    total_income            NUMERIC(14,2) DEFAULT 0,
    total_expense           NUMERIC(14,2) DEFAULT 0,
    net_profit              NUMERIC(14,2) DEFAULT 0,
    monthly_avg_income      NUMERIC(14,2) DEFAULT 0,
    monthly_avg_expense     NUMERIC(14,2) DEFAULT 0,
    monthly_income          NUMERIC(14,2) DEFAULT 0,
    monthly_expense         NUMERIC(14,2) DEFAULT 0,
    avg_payment_cycle_days  NUMERIC(5,1)  DEFAULT 7,
    avg_collection_days     NUMERIC(5,1)  DEFAULT 9.8,
    created_at              TIMESTAMPTZ DEFAULT NOW()
);

-- ── monthly_summaries ────────────────────────────────────────
CREATE TABLE IF NOT EXISTS monthly_summaries (
    id              BIGSERIAL PRIMARY KEY,
    business_id     BIGINT NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    month           CHAR(7) NOT NULL,           -- e.g. '2026-01'
    income          NUMERIC(14,2) DEFAULT 0,
    expense         NUMERIC(14,2) DEFAULT 0,
    net             NUMERIC(14,2) DEFAULT 0,
    opening_balance NUMERIC(14,2) DEFAULT 0,
    closing_balance NUMERIC(14,2) DEFAULT 0,
    UNIQUE (business_id, month)
);

-- ── transactions (bank statement) ────────────────────────────
CREATE TABLE IF NOT EXISTS transactions (
    id          BIGSERIAL PRIMARY KEY,
    business_id BIGINT NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    date        DATE NOT NULL,
    description TEXT,
    debit       NUMERIC(14,2) DEFAULT 0,
    credit      NUMERIC(14,2) DEFAULT 0,
    balance     NUMERIC(14,2),
    category    TEXT,
    type        TEXT
);

-- ── clients ──────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS clients (
    id                      BIGSERIAL PRIMARY KEY,
    business_id             BIGINT NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    client_id               TEXT NOT NULL,
    client                  TEXT NOT NULL,
    contact                 TEXT,
    phone                   TEXT,
    email                   TEXT,
    relationship_months     INT DEFAULT 0,
    total_billed            NUMERIC(14,2) DEFAULT 0,
    total_collected         NUMERIC(14,2) DEFAULT 0,
    outstanding             NUMERIC(14,2) DEFAULT 0,
    avg_payment_days        NUMERIC(5,1)  DEFAULT 0,
    on_time_payment_rate    NUMERIC(4,2)  DEFAULT 0,
    risk_level              TEXT DEFAULT 'low',
    notes                   TEXT,
    payment_history         JSONB DEFAULT '[]'::jsonb, -- Store full audit trail
    UNIQUE (business_id, client_id)
);

-- ── receivables ───────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS receivables (
    id                      BIGSERIAL PRIMARY KEY,
    business_id             BIGINT NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    invoice_id              TEXT NOT NULL,
    client                  TEXT NOT NULL,
    client_id               TEXT,
    amount                  NUMERIC(14,2) NOT NULL,
    invoice_date            DATE,
    due_date                DATE,
    expected_date           DATE,
    days_overdue            INT DEFAULT 0,
    collection_probability  NUMERIC(4,2) DEFAULT 0.8,
    status                  TEXT DEFAULT 'upcoming',
    action_required         TEXT DEFAULT 'none',
    UNIQUE (business_id, invoice_id)
);

-- ── payables ─────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS payables (
    id              BIGSERIAL PRIMARY KEY,
    business_id     BIGINT NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    payable_id      TEXT NOT NULL,
    vendor          TEXT NOT NULL,
    vendor_id       TEXT,
    description     TEXT,
    amount          NUMERIC(14,2) NOT NULL,
    invoice_date    DATE,
    due_date        DATE NOT NULL,
    days_until_due  INT DEFAULT 0,
    type            TEXT DEFAULT 'flexible',
    penalty         TEXT DEFAULT 'none',
    penalty_amount  NUMERIC(14,2) DEFAULT 0,
    flexibility     TEXT DEFAULT 'medium',
    priority_score  NUMERIC(4,2) DEFAULT 0.5,
    status          TEXT DEFAULT 'unpaid',
    linked_orders   TEXT[] DEFAULT '{}', -- Store array of PO IDs
    UNIQUE (business_id, payable_id)
);

-- ── overheads ────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS overheads (
    id          BIGSERIAL PRIMARY KEY,
    business_id BIGINT NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    type        TEXT NOT NULL,
    amount      NUMERIC(14,2) DEFAULT 0,
    monthly_avg NUMERIC(14,2) DEFAULT 0,
    essential   BOOLEAN DEFAULT TRUE,
    can_reduce  BOOLEAN DEFAULT FALSE,
    reducible_by NUMERIC(4,2) DEFAULT 0,
    UNIQUE (business_id, type)
);

-- ── vendors ───────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS vendors (
    id                          BIGSERIAL PRIMARY KEY,
    business_id                 BIGINT NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    vendor_id                   TEXT NOT NULL,
    vendor                      TEXT NOT NULL,
    contact_person              TEXT,
    phone                       TEXT,
    email                       TEXT,
    total_orders                INT DEFAULT 0,
    total_spend                 NUMERIC(14,2) DEFAULT 0,
    avg_lead_time_days          NUMERIC(5,1) DEFAULT 3,
    min_lead_time_days          INT DEFAULT 2,
    max_lead_time_days          INT DEFAULT 5,
    on_time_delivery_rate       NUMERIC(4,2) DEFAULT 0.9,
    payment_delay_avg_days      NUMERIC(5,1) DEFAULT 0,
    reliability_score           NUMERIC(4,2) DEFAULT 0.8,
    cost_efficiency_score       NUMERIC(4,2) DEFAULT 0.8,
    preferred_payment_terms     TEXT DEFAULT 'NET-7',
    allows_credit               BOOLEAN DEFAULT FALSE,
    credit_limit                NUMERIC(14,2) DEFAULT 0,
    relationship_duration_months INT DEFAULT 0,
    negotiation_flexibility     TEXT DEFAULT 'medium',
    UNIQUE (business_id, vendor_id)
);

-- ── inventory_items ───────────────────────────────────────────
CREATE TABLE IF NOT EXISTS inventory_items (
    id                  BIGSERIAL PRIMARY KEY,
    business_id         BIGINT NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    item_id             TEXT,
    item                TEXT NOT NULL,
    unit                TEXT,
    available_quantity  NUMERIC(12,2) DEFAULT 0,
    required_quantity   NUMERIC(12,2) DEFAULT 0,
    reorder_level       NUMERIC(12,2) DEFAULT 0,
    unit_cost           NUMERIC(10,2),
    total_value         NUMERIC(14,2),
    shortage            NUMERIC(12,2) DEFAULT 0,
    excess              NUMERIC(12,2) DEFAULT 0,
    last_updated        DATE,
    UNIQUE (business_id, item_id)
);

-- ── procurement_orders ────────────────────────────────────────
CREATE TABLE IF NOT EXISTS procurement_orders (
    id                  BIGSERIAL PRIMARY KEY,
    business_id         BIGINT NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    order_id            TEXT NOT NULL,
    vendor_id           TEXT,
    vendor              TEXT NOT NULL,
    material            TEXT NOT NULL,
    item_id             TEXT,
    quantity            NUMERIC(12,2) DEFAULT 0,
    unit_cost           NUMERIC(10,2) DEFAULT 0,
    total_cost          NUMERIC(14,2) DEFAULT 0,
    order_date          DATE,
    expected_delivery   DATE,
    actual_delivery     DATE,
    lead_time_days      INT DEFAULT 3,
    status              TEXT DEFAULT 'pending',
    payment_status      TEXT DEFAULT 'unpaid',
    payment_due         DATE,
    UNIQUE (business_id, order_id)
);

-- ── daily_production ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS daily_production (
    id          BIGSERIAL PRIMARY KEY,
    business_id BIGINT NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    date        DATE NOT NULL,
    units       INT DEFAULT 0,
    UNIQUE (business_id, date)
);

-- ── collection_predictions ────────────────────────────────────
CREATE TABLE IF NOT EXISTS collection_predictions (
    id              BIGSERIAL PRIMARY KEY,
    business_id     BIGINT NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    client          TEXT NOT NULL,
    amount          NUMERIC(14,2) DEFAULT 0,
    expected_date   DATE,
    probability     NUMERIC(4,2) DEFAULT 0.8
);

-- ── Row Level Security (enable but keep open for anon key reads) ──────────────
ALTER TABLE businesses           ENABLE ROW LEVEL SECURITY;
ALTER TABLE ledger_summaries     ENABLE ROW LEVEL SECURITY;
ALTER TABLE monthly_summaries    ENABLE ROW LEVEL SECURITY;
ALTER TABLE transactions         ENABLE ROW LEVEL SECURITY;
ALTER TABLE clients              ENABLE ROW LEVEL SECURITY;
ALTER TABLE receivables          ENABLE ROW LEVEL SECURITY;
ALTER TABLE payables             ENABLE ROW LEVEL SECURITY;
ALTER TABLE overheads            ENABLE ROW LEVEL SECURITY;
ALTER TABLE vendors              ENABLE ROW LEVEL SECURITY;
ALTER TABLE inventory_items      ENABLE ROW LEVEL SECURITY;
ALTER TABLE procurement_orders   ENABLE ROW LEVEL SECURITY;
ALTER TABLE daily_production     ENABLE ROW LEVEL SECURITY;
ALTER TABLE collection_predictions ENABLE ROW LEVEL SECURITY;

-- Allow anon reads (the backend uses the anon key) ────────────────────────────
CREATE POLICY "anon_read_businesses"           ON businesses           FOR SELECT USING (true);
CREATE POLICY "anon_read_ledger_summaries"     ON ledger_summaries     FOR SELECT USING (true);
CREATE POLICY "anon_read_monthly_summaries"    ON monthly_summaries    FOR SELECT USING (true);
CREATE POLICY "anon_read_transactions"         ON transactions         FOR SELECT USING (true);
CREATE POLICY "anon_read_clients"              ON clients              FOR SELECT USING (true);
CREATE POLICY "anon_read_receivables"          ON receivables          FOR SELECT USING (true);
CREATE POLICY "anon_read_payables"             ON payables             FOR SELECT USING (true);
CREATE POLICY "anon_read_overheads"            ON overheads            FOR SELECT USING (true);
CREATE POLICY "anon_read_vendors"              ON vendors              FOR SELECT USING (true);
CREATE POLICY "anon_read_inventory_items"      ON inventory_items      FOR SELECT USING (true);
CREATE POLICY "anon_read_procurement_orders"   ON procurement_orders   FOR SELECT USING (true);
CREATE POLICY "anon_read_daily_production"     ON daily_production     FOR SELECT USING (true);
CREATE POLICY "anon_read_collection_predictions" ON collection_predictions FOR SELECT USING (true);

-- Allow writes via anon key (backend ingest endpoints) ────────────────────────
CREATE POLICY "anon_write_transactions"  ON transactions  FOR INSERT WITH CHECK (true);
CREATE POLICY "anon_write_receivables"   ON receivables   FOR INSERT WITH CHECK (true);
CREATE POLICY "anon_write_payables"      ON payables      FOR INSERT WITH CHECK (true);
CREATE POLICY "anon_write_prod"          ON daily_production FOR INSERT WITH CHECK (true);
CREATE POLICY "anon_upsert_transactions" ON transactions  FOR UPDATE USING (true);
CREATE POLICY "anon_upsert_receivables"  ON receivables   FOR UPDATE USING (true);
CREATE POLICY "anon_upsert_payables"     ON payables      FOR UPDATE USING (true);

-- ── document_parses ──────────────────────────────────────────
CREATE TABLE IF NOT EXISTS document_parses (
    id              BIGSERIAL PRIMARY KEY,
    business_id     BIGINT NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    filename        TEXT,
    doc_type        TEXT,
    extracted_text  TEXT,
    structured_data JSONB,
    confidence      NUMERIC(4,2),
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

ALTER TABLE document_parses ENABLE ROW LEVEL SECURITY;
CREATE POLICY "anon_read_document_parses"  ON document_parses FOR SELECT USING (true);
CREATE POLICY "anon_write_document_parses" ON document_parses FOR INSERT WITH CHECK (true);
