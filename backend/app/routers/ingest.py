from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from app.services.data_ingestion import parse_bank_statement_csv, parse_invoices_json
from app.services.intelligent_parser import extract_text_from_image, extract_text_from_pdf, parse_financial_document
import json

router = APIRouter(prefix="/api/ingest", tags=["ingest"])


@router.post("/bank-statement")
async def ingest_bank_statement(file: UploadFile = File(...)):
    """Upload and parse a CSV bank statement."""
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported for bank statements.")
    content = (await file.read()).decode("utf-8")
    transactions = parse_bank_statement_csv(content)
    return {
        "status": "success",
        "filename": file.filename,
        "transactions_parsed": len(transactions),
        "transactions": [t.dict() for t in transactions]
    }


@router.post("/invoices")
async def ingest_invoices(file: UploadFile = File(...)):
    """Upload and parse a JSON invoices file."""
    if not file.filename.endswith(".json"):
        raise HTTPException(status_code=400, detail="Only JSON files are supported for invoices.")
    content = (await file.read()).decode("utf-8")
    result = parse_invoices_json(content)
    return {
        "status": "success",
        "filename": file.filename,
        "payables_found": len(result["payables"]),
        "receivables_found": len(result["receivables"]),
        "payables": [p.dict() for p in result["payables"]],
        "receivables": [r.dict() for r in result["receivables"]]
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
        "receivables_count": len(data.get("receivables", []))
    }
@router.post("/document")
async def ingest_document(file: UploadFile = File(...)):
    """Upload unstructured document (Image/PDF/Text) for OCR and LLM structuring."""
    ext = file.filename.lower()
    if not ext.endswith(('.png', '.jpg', '.jpeg', '.pdf', '.txt', '.csv', '.json')):
        raise HTTPException(status_code=400, detail="Unsupported file format. Please upload PDF, Image, or Text.")
    
    file_bytes = await file.read()
    
    # 1. Extraction Layer
    if ext.endswith('.pdf'):
        raw_text = extract_text_from_pdf(file_bytes)
    elif ext.endswith(('.png', '.jpg', '.jpeg')):
        raw_text = extract_text_from_image(file_bytes)
    else:
        raw_text = file_bytes.decode("utf-8", errors="ignore")
    
    # 2. Intelligent Parsing
    structured_data = parse_financial_document(raw_text)
    
    return {
        "status": "success",
        "filename": file.filename,
        "extracted_text_snippet": raw_text[:100] + "...",
        "structured_data": structured_data
    }
