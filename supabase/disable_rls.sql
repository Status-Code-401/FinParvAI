-- ============================================================
-- FinParvai — Disable RLS for single-tenant seeding
-- Run this in Supabase SQL Editor BEFORE running seed.py
-- (You can re-enable RLS later once you add auth)
-- ============================================================

ALTER TABLE businesses             DISABLE ROW LEVEL SECURITY;
ALTER TABLE ledger_summaries       DISABLE ROW LEVEL SECURITY;
ALTER TABLE monthly_summaries      DISABLE ROW LEVEL SECURITY;
ALTER TABLE transactions           DISABLE ROW LEVEL SECURITY;
ALTER TABLE clients                DISABLE ROW LEVEL SECURITY;
ALTER TABLE receivables            DISABLE ROW LEVEL SECURITY;
ALTER TABLE payables               DISABLE ROW LEVEL SECURITY;
ALTER TABLE overheads              DISABLE ROW LEVEL SECURITY;
ALTER TABLE vendors                DISABLE ROW LEVEL SECURITY;
ALTER TABLE inventory_items        DISABLE ROW LEVEL SECURITY;
ALTER TABLE procurement_orders     DISABLE ROW LEVEL SECURITY;
ALTER TABLE daily_production       DISABLE ROW LEVEL SECURITY;
ALTER TABLE collection_predictions DISABLE ROW LEVEL SECURITY;
