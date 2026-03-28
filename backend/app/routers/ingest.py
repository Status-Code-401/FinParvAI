from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from app.services.data_ingestion import parse_bank_statement_csv, parse_invoices_json
from app.services.intelligent_parser import extract_text_from_image, extract_text_from_pdf, parse_financial_document
from app.services.database import db  # Import our SupabaseDB service
import json
import os
import uuid
from datetime import datetime

BUSINESS_ID = 1  # Demo single business ID
MOCK_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "..", "mock_data")

router = APIRouter(prefix="/api/ingest", tags=["ingest"])


# ── Mock-JSON persistence helpers ─────────────────────────────────────────────
# These ensure dashboards update immediately even when DB is not connected.

def _append_to_mock_state(key: str, items: list[dict]):
    """Append items to a list inside normalized_financial_state.json."""
    path = os.path.join(MOCK_DATA_DIR, "normalized_financial_state.json")
    try:
        with open(path, "r", encoding="utf-8") as f:
            state = json.load(f)
        existing = state.get(key, [])
        existing.extend(items)
        state[key] = existing
        with open(path, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Mock state append [{key}] failed: {e}")


def _append_to_mock_ledger(key: str, items: list[dict]):
    """Append items to a list inside ledger_data.json."""
    path = os.path.join(MOCK_DATA_DIR, "ledger_data.json")
    try:
        with open(path, "r", encoding="utf-8") as f:
            ledger = json.load(f)
        existing = ledger.get(key, [])
        existing.extend(items)
        ledger[key] = existing
        with open(path, "w", encoding="utf-8") as f:
            json.dump(ledger, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Mock ledger append [{key}] failed: {e}")


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _today() -> str:
    return datetime.now().strftime("%Y-%m-%d")


def _make_transaction_from_payable(structured: dict) -> dict:
    """
    Convert a vendor invoice / bill / receipt into a debit Transaction so it
    appears in the ledger, calendar and cash-flow projection.
    """
    return {
        "date": structured.get("date") or structured.get("due_date") or _today(),
        "description": (
            f"Bill from {structured.get('vendor', 'Unknown Vendor')}"
            + (f" – {structured.get('category', '')}" if structured.get("category") else "")
        ),
        "debit": float(structured.get("amount", 0.0)),
        "credit": 0.0,
        "balance": None,
        "category": structured.get("category") or "expense",
    }


def _make_transaction_from_receivable(structured: dict) -> dict:
    """
    Convert a client invoice into a *pending* credit Transaction so it
    shows up in the calendar and cash-flow projection.
    """
    return {
        "date": structured.get("date") or structured.get("due_date") or _today(),
        "description": (
            f"Invoice to {structured.get('client', 'Unknown Client')}"
            + (f" – {structured.get('category', '')}" if structured.get("category") else "")
        ),
        "debit": 0.0,
        "credit": float(structured.get("amount", 0.0)),
        "balance": None,
        "category": structured.get("category") or "income",
    }


def _check_and_alert_disruptions():
    """
    Runs the deterministic engine to check if recent ingests caused a cash flow shock.
    Sends a Twilio/SendGrid email alert if true.
    """
    try:
        import os
        from app.routers.financial import _load_state
        from app.services.decision_engine import run_engine
        from app.services.notifications import send_cashflow_alert
        
        state = _load_state()
        decision = run_engine(state)
        
        # Determine if there's a huge disruption
        if decision.get("risk_level") in ["critical", "high"]:
            shortfall = decision.get("shortfall", {})
            runway = decision.get("runway", {})
            gap = shortfall.get("gap", 0)
            
            # Use configured address or fallback
            user_email = os.getenv("NOTIFY_USER_EMAIL", "owner@finparvai.demo")
            biz_name = state.business_name or "Sri Lakshmi Garments"
            summary_msg = f"Your latest document uploads have triggered a cashflow shortfall of ₹{gap:,.0f}."
            if not runway.get("is_safe"):
                summary_msg += f" Your cash balance is projected to fall below zero in {runway.get('days_to_zero')} days."
                
            send_cashflow_alert(user_email, biz_name, gap, summary_msg)
    except Exception as exc:
        print(f"Failed disruption alert sequence: {exc}")


# ─── Endpoints ────────────────────────────────────────────────────────────────

@router.post("/bank-statement")
async def ingest_bank_statement(files: list[UploadFile] = File(...)):
    """Upload and parse multiple CSV bank statements."""
    total_parsed = 0
    all_txn_dicts: list[dict] = []
    for file in files:
        if not file.filename.endswith(".csv"):
            continue
        content = (await file.read()).decode("utf-8")
        transactions = parse_bank_statement_csv(content)
        for t in transactions:
            td = t.dict()
            db.upsert_transaction(BUSINESS_ID, td)
            all_txn_dicts.append(td)
        total_parsed += len(transactions)

    # Persist to mock JSON so dashboards refresh immediately
    if all_txn_dicts:
        _append_to_mock_state("transactions", all_txn_dicts)

    _check_and_alert_disruptions()

    return {
        "status": "success",
        "message": f"Parsed {total_parsed} transactions across {len(files)} bank statements.",
        "transactions_parsed": total_parsed,
        "persisted": True,
    }


@router.post("/invoices")
async def ingest_invoices(files: list[UploadFile] = File(...)):
    """Upload and parse multiple JSON invoice files."""
    total_payables = 0
    total_receivables = 0
    new_payables: list[dict] = []
    new_receivables: list[dict] = []
    new_txns: list[dict] = []

    for file in files:
        if not file.filename.endswith(".json"):
            continue
        content = (await file.read()).decode("utf-8")
        result = parse_invoices_json(content)

        # Persist payables + a matching debit transaction
        for p in result["payables"]:
            pd = p.dict()
            db.upsert_payable(BUSINESS_ID, pd)
            txn = {
                "date": p.due_date or _today(),
                "description": f"Bill from {p.vendor}",
                "debit": p.amount,
                "credit": 0.0,
                "balance": None,
                "category": "expense",
            }
            db.upsert_transaction(BUSINESS_ID, txn)
            new_payables.append(pd)
            new_txns.append(txn)

        # Persist receivables + a matching credit transaction
        for r in result["receivables"]:
            rd = r.dict()
            db.upsert_receivable(BUSINESS_ID, rd)
            txn = {
                "date": r.expected_date or _today(),
                "description": f"Invoice to {r.client}",
                "debit": 0.0,
                "credit": r.amount,
                "balance": None,
                "category": "income",
            }
            db.upsert_transaction(BUSINESS_ID, txn)
            new_receivables.append(rd)
            new_txns.append(txn)
        total_payables += len(result["payables"])
        total_receivables += len(result["receivables"])

    # Persist to mock JSON so dashboards refresh
    if new_payables:
        _append_to_mock_state("payables", new_payables)
        _append_to_mock_ledger("active_payables", new_payables)
    if new_receivables:
        _append_to_mock_state("receivables", new_receivables)
        _append_to_mock_ledger("active_receivables", new_receivables)
    if new_txns:
        _append_to_mock_state("transactions", new_txns)

    _check_and_alert_disruptions()

    return {
        "status": "success",
        "payables_persisted": total_payables,
        "receivables_persisted": total_receivables,
        "payables_found": total_payables,
        "receivables_found": total_receivables,
    }


@router.post("/financial-state")
async def ingest_financial_state(file: UploadFile = File(...)):
    """Upload a normalized financial state JSON."""
    if not file.filename.endswith(".json"):
        raise HTTPException(status_code=400, detail="Only JSON files are accepted.")
    content = (await file.read()).decode("utf-8")
    data = json.loads(content)
    return {
        "status": "success",
        "filename": file.filename,
        "cash_balance": data.get("cash_balance", 0),
        "payables_count": len(data.get("payables", [])),
        "receivables_count": len(data.get("receivables", [])),
    }


@router.post("/upload")
async def legacy_upload(file: UploadFile = File(...)):
    """Legacy alias for document ingestion (supports single file)."""
    return await ingest_document([file])


@router.post("/document")
async def ingest_document(files: list[UploadFile] = File(...)):
    """
    Batch upload multiple unstructured documents (Image/PDF/Text) for OCR + LLM.
    """
    results = []
    
    for file in files:
        ext = file.filename.lower()
        if not ext.endswith((".png", ".jpg", ".jpeg", ".pdf", ".txt", ".csv", ".json")):
            continue

        file_bytes = await file.read()

        # ── 1. Extraction layer ──────────────────────────────────────────────────
        if ext.endswith(".pdf"):
            raw_text = extract_text_from_pdf(file_bytes)
        elif ext.endswith((".png", ".jpg", ".jpeg")):
            raw_text = extract_text_from_image(file_bytes)
        else:
            raw_text = file_bytes.decode("utf-8", errors="ignore")

        # ── 2. Intelligent parsing ───────────────────────────────────────────────
        structured_data = parse_financial_document(raw_text)
        
        db.save_document_parse(BUSINESS_ID, {
            "filename": file.filename,
            "doc_type": structured_data.get("type", "unknown"),
            "extracted_text": raw_text,
            "structured_data": structured_data,
            "confidence": structured_data.get("confidence", 0.8)
        })

        doc_type = structured_data.get("type", "").lower()
        amount = float(structured_data.get("amount", 0.0))
        date_str = structured_data.get("date") or structured_data.get("due_date") or _today()
        due_date_str = structured_data.get("due_date") or date_str
        category = structured_data.get("category") or "misc"
        persisted_as = []

        # ── 3a. Vendor invoice / bill / receipt → Payable + debit Transaction ───
        if any(k in doc_type for k in ("invoice", "bill", "receipt")) and structured_data.get("vendor"):
            payable_id = structured_data.get("payable_id") or f"PAY-{str(uuid.uuid4())[:8].upper()}"

            payable_payload = {
                "payable_id": payable_id,
                "vendor": structured_data.get("vendor", "Unknown Vendor"),
                "amount": amount,
                "due_date": due_date_str,
                "type": "flexible",
                "status": "unpaid",
                "priority_score": 0.5,
                "description": structured_data.get("description") or category,
            }
            db.upsert_payable(BUSINESS_ID, payable_payload)
            persisted_as.append("payable")

            txn = _make_transaction_from_payable(structured_data)
            db.upsert_transaction(BUSINESS_ID, txn)
            persisted_as.append("transaction(debit)")

            # Mock-JSON persistence
            _append_to_mock_state("payables", [payable_payload])
            _append_to_mock_ledger("active_payables", [payable_payload])
            _append_to_mock_state("transactions", [txn])

        # ── 3b. Client invoice → Receivable + credit Transaction ─────────────────
        elif any(k in doc_type for k in ("invoice", "bill")) and structured_data.get("client"):
            invoice_id = structured_data.get("invoice_id") or f"INV-{str(uuid.uuid4())[:8].upper()}"

            receivable_payload = {
                "invoice_id": invoice_id,
                "client": structured_data.get("client", "Unknown Client"),
                "amount": amount,
                "expected_date": due_date_str,
                "status": "upcoming",
                "collection_probability": 0.8,
            }
            db.upsert_receivable(BUSINESS_ID, receivable_payload)
            persisted_as.append("receivable")

            txn = _make_transaction_from_receivable(structured_data)
            db.upsert_transaction(BUSINESS_ID, txn)
            persisted_as.append("transaction(credit)")

            # Mock-JSON persistence
            _append_to_mock_state("receivables", [receivable_payload])
            _append_to_mock_ledger("active_receivables", [receivable_payload])
            _append_to_mock_state("transactions", [txn])

        # ── 3c. Generic / ambiguous document → Transaction only ──────────────────
        else:
            is_expense = any(k in doc_type for k in ("expense", "receipt", "payment", "bill"))
            txn = {
                "date": date_str,
                "description": (
                    f"{structured_data.get('vendor') or structured_data.get('client') or 'Unknown'}"
                    + (f" – {category}" if category else "")
                ),
                "debit": amount if is_expense else 0.0,
                "credit": 0.0 if is_expense else amount,
                "balance": None,
                "category": category,
            }
            db.upsert_transaction(BUSINESS_ID, txn)
            persisted_as.append("transaction")

            # Mock-JSON persistence
            _append_to_mock_state("transactions", [txn])

        results.append({
            "filename": file.filename,
            "type": doc_type,
            "vendor_client": structured_data.get("vendor") or structured_data.get("client"),
            "amount": amount,
            "persisted_as": persisted_as
        })

    _check_and_alert_disruptions()

    return {
        "status": "success",
        "message": f"Successfully parsed {len(results)} structured documents.",
        "documents_parsed": len(results),
        "results": results,
    }