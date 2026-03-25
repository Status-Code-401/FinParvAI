from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from models.schemas import FinancialState
from services.ingest_service import (
    classify_document, mock_ocr_extract, parse_invoice,
    parse_bank_statement_csv
)

router = APIRouter()


@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """Upload and process a financial document (PDF, image, CSV)."""
    content = await file.read()
    filename = file.filename or "document"

    # Step 1: Mock OCR
    extracted_text = mock_ocr_extract(filename, content)

    # Step 2: Classify
    doc_type = classify_document(filename, extracted_text)

    # Step 3: Parse
    parsed = {}
    if doc_type == "invoice":
        parsed = parse_invoice(extracted_text)
    elif doc_type == "bank_statement":
        try:
            text_content = content.decode("utf-8")
            transactions = parse_bank_statement_csv(text_content)
            parsed = {
                "doc_type": "bank_statement",
                "transactions": [t.dict() for t in transactions],
                "transaction_count": len(transactions),
            }
        except Exception:
            parsed = {"doc_type": "bank_statement", "raw_text": extracted_text[:300]}
    else:
        parsed = {
            "doc_type": doc_type,
            "raw_text": extracted_text[:300],
        }

    return {
        "filename": filename,
        "file_size_bytes": len(content),
        "classified_as": doc_type,
        "extracted_data": parsed,
        "ocr_confidence": 0.91,
        "status": "processed",
    }


@router.post("/normalize")
async def normalize_data(state: FinancialState):
    """Normalize and validate a FinancialState object."""
    # Compute derived fields
    total_payables   = sum(p.amount for p in (state.payables or []))
    total_receivables= sum(r.amount for r in (state.receivables or []))
    total_overheads  = sum(o.amount for o in (state.overheads or []))
    net_position     = state.cash_balance + total_receivables - total_payables - total_overheads

    return {
        "status": "normalized",
        "summary": {
            "cash_balance":       state.cash_balance,
            "total_payables":     total_payables,
            "total_receivables":  total_receivables,
            "total_overheads":    total_overheads,
            "net_position":       round(net_position, 2),
            "payable_count":      len(state.payables or []),
            "receivable_count":   len(state.receivables or []),
        },
        "normalized_state": state.dict(),
    }


@router.get("/demo-state")
def get_demo_state():
    """Return a realistic demo financial state for testing."""
    from datetime import datetime, timedelta
    today = datetime.today().date()
    fmt   = lambda d: d.strftime("%Y-%m-%d")

    return {
        "cash_balance": 45000,
        "transactions": [
            {"date": fmt(today - timedelta(days=5)), "description": "Client XYZ Payment", "amount": 30000, "type": "credit", "balance": 75000},
            {"date": fmt(today - timedelta(days=3)), "description": "ABC Textiles Invoice", "amount": 15000, "type": "debit",  "balance": 60000},
            {"date": fmt(today - timedelta(days=1)), "description": "Electricity Bill",    "amount": 3200,  "type": "debit",  "balance": 56800},
        ],
        "payables": [
            {"vendor": "ABC Textiles",    "amount": 15000, "due_date": fmt(today + timedelta(days=1)),  "penalty": "high",   "type": "critical",  "linked_orders": ["order_101"], "priority_score": 0.9},
            {"vendor": "Fabric House",    "amount": 12000, "due_date": fmt(today + timedelta(days=3)),  "penalty": "medium", "type": "flexible",  "linked_orders": [],            "priority_score": 0.6},
            {"vendor": "Logistics Co",   "amount": 5000,  "due_date": fmt(today + timedelta(days=7)),  "penalty": "low",    "type": "flexible",  "linked_orders": [],            "priority_score": 0.3},
            {"vendor": "Marketing Agency","amount": 8000,  "due_date": fmt(today + timedelta(days=10)), "penalty": "low",    "type": "flexible",  "linked_orders": [],            "priority_score": 0.2},
        ],
        "receivables": [
            {"client": "XYZ Retail",    "amount": 30000, "expected_date": fmt(today + timedelta(days=2)),  "collection_probability": 0.85},
            {"client": "Patel Exports", "amount": 18000, "expected_date": fmt(today + timedelta(days=6)),  "collection_probability": 0.70},
        ],
        "overheads": [
            {"type": "electricity",  "amount": 3000,  "essential": True},
            {"type": "ads",          "amount": 5000,  "essential": False},
            {"type": "salaries",     "amount": 35000, "essential": True},
            {"type": "rent",         "amount": 8000,  "essential": True},
            {"type": "travel",       "amount": 2000,  "essential": False},
        ],
        "ledger_summary": {
            "monthly_income":           120000,
            "monthly_expense":          100000,
            "avg_payment_cycle_days":   7,
        },
        "inventory_procurement": [
            {
                "order_id": "order_101", "vendor": "ABC Textiles", "material": "Cotton Fabric",
                "quantity": 500, "unit_cost": 50, "total_cost": 25000,
                "order_date": fmt(today - timedelta(days=10)), "delivery_date": fmt(today - timedelta(days=7)),
                "lead_time": 3, "status": "delivered",
            },
            {
                "order_id": "order_102", "vendor": "Fabric House", "material": "Synthetic Blend",
                "quantity": 300, "unit_cost": 40, "total_cost": 12000,
                "order_date": fmt(today), "delivery_date": fmt(today + timedelta(days=4)),
                "lead_time": 4, "status": "pending",
            },
        ],
        "inventory_status": [
            {"item": "Cotton Fabric",  "available_quantity": 500, "required_quantity": 300, "shortage": 0, "excess": 200},
            {"item": "Synthetic Blend","available_quantity": 100, "required_quantity": 300, "shortage": 200, "excess": 0},
            {"item": "Thread",         "available_quantity": 50,  "required_quantity": 50,  "shortage": 0,  "excess": 0},
        ],
        "vendor_insights": [
            {"vendor": "ABC Textiles",  "total_orders": 8, "avg_lead_time": 3, "payment_delay_avg": 1, "reliability_score": 0.92, "cost_efficiency_score": 0.78},
            {"vendor": "Fabric House",  "total_orders": 5, "avg_lead_time": 4, "payment_delay_avg": 2, "reliability_score": 0.80, "cost_efficiency_score": 0.72},
            {"vendor": "Logistics Co",  "total_orders": 12,"avg_lead_time": 1, "payment_delay_avg": 0, "reliability_score": 0.95, "cost_efficiency_score": 0.65},
        ],
        "production": {
            "daily_output": {"monday": 120, "tuesday": 100, "wednesday": 115, "thursday": 110, "friday": 90},
            "cost_per_unit": 100,
        },
        "cost_breakdown": {"internal": 10000, "external": 25000},
    }
