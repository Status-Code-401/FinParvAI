"""
Document ingestion service — classifies, extracts, and normalizes financial documents.
In production: integrates Google Vision / AWS Textract.
For MVP: uses rule-based extraction + LLM parsing simulation.
"""
import re
import io
from typing import Optional
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from models.schemas import Payable, Receivable, Transaction


def classify_document(filename: str, text_preview: str = "") -> str:
    """Rule-based document classification."""
    fname = filename.lower()
    if any(k in fname for k in ["bank", "statement", "account"]):
        return "bank_statement"
    if any(k in fname for k in ["invoice", "inv", "bill"]):
        return "invoice"
    if any(k in fname for k in ["receipt", "rcpt"]):
        return "receipt"
    # Fallback: text-based
    if "invoice" in text_preview.lower() or "due date" in text_preview.lower():
        return "invoice"
    if "balance" in text_preview.lower() or "credit" in text_preview.lower():
        return "bank_statement"
    return "unknown"


def extract_amount(text: str) -> Optional[float]:
    """Extract monetary amount from text."""
    patterns = [
        r"₹\s*([\d,]+(?:\.\d{2})?)",
        r"Rs\.?\s*([\d,]+(?:\.\d{2})?)",
        r"INR\s*([\d,]+(?:\.\d{2})?)",
        r"Amount[:\s]+([\d,]+(?:\.\d{2})?)",
        r"Total[:\s]+([\d,]+(?:\.\d{2})?)",
        r"([\d,]+(?:\.\d{2})?)",
    ]
    for pat in patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            return float(m.group(1).replace(",", ""))
    return None


def extract_date(text: str) -> Optional[str]:
    """Extract dates in various formats."""
    patterns = [
        r"(\d{4}-\d{2}-\d{2})",
        r"(\d{2}/\d{2}/\d{4})",
        r"(\d{2}-\d{2}-\d{4})",
        r"Due\s+Date[:\s]+(\w+\s+\d{1,2},?\s+\d{4})",
    ]
    from datetime import datetime
    for pat in patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            raw = m.group(1)
            for fmt in ["%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"]:
                try:
                    return datetime.strptime(raw, fmt).strftime("%Y-%m-%d")
                except ValueError:
                    pass
    return None


def extract_vendor_client(text: str) -> Optional[str]:
    """Extract vendor or client name."""
    patterns = [
        r"(?:Vendor|From|Bill From|Supplier)[:\s]+([A-Za-z\s&.]+?)(?:\n|,|$)",
        r"(?:Client|To|Bill To|Customer)[:\s]+([A-Za-z\s&.]+?)(?:\n|,|$)",
        r"(?:Pay to)[:\s]+([A-Za-z\s&.]+?)(?:\n|,|$)",
    ]
    for pat in patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            return m.group(1).strip()
    return None


def parse_invoice(text: str) -> dict:
    amount = extract_amount(text)
    due    = extract_date(text)
    entity = extract_vendor_client(text)

    # Determine payable vs receivable
    is_payable = any(k in text.lower() for k in ["pay", "due", "payable", "bill from", "vendor"])

    result = {
        "doc_type": "payable" if is_payable else "receivable",
        "amount":   amount or 0,
        "date":     due or "2026-04-01",
        "entity":   entity or "Unknown",
        "raw_text": text[:500],
    }
    return result


def parse_bank_statement_csv(csv_text: str) -> list:
    """Parse CSV bank statement into transactions."""
    import csv, io
    transactions = []
    reader = csv.DictReader(io.StringIO(csv_text))
    for row in reader:
        # Flexible column detection
        date_val   = row.get("Date") or row.get("date") or ""
        desc_val   = row.get("Description") or row.get("desc") or row.get("Narration") or ""
        debit_val  = row.get("Debit") or row.get("debit") or "0"
        credit_val = row.get("Credit") or row.get("credit") or "0"
        bal_val    = row.get("Balance") or row.get("balance") or "0"

        try:
            debit  = float(str(debit_val).replace(",", "") or 0)
            credit = float(str(credit_val).replace(",", "") or 0)
            bal    = float(str(bal_val).replace(",", "") or 0)
        except (ValueError, TypeError):
            continue

        if credit > 0:
            transactions.append(Transaction(
                date=date_val, description=desc_val,
                amount=credit, type="credit", balance=bal
            ))
        if debit > 0:
            transactions.append(Transaction(
                date=date_val, description=desc_val,
                amount=debit, type="debit", balance=bal
            ))
    return transactions


def mock_ocr_extract(filename: str, file_bytes: bytes) -> str:
    """
    Mock OCR extraction.
    In production: call Google Vision API / AWS Textract here.
    Returns raw text extracted from document.
    """
    fname = filename.lower()

    if "invoice" in fname or "bill" in fname:
        return """
INVOICE #INV-2026-001
From: ABC Textiles Ltd
To: My Garments Co.
Date: 2026-03-20
Due Date: 2026-04-05
Amount: ₹15,000
Description: Fabric supply - 500m cotton
Payment Terms: Net 15
"""
    elif "receipt" in fname:
        return """
RECEIPT
Date: 2026-03-22
Category: Electricity
Amount: ₹3,200
Paid to: TNEB
Reference: REC-20260322
"""
    elif "bank" in fname or "statement" in fname:
        return """Date,Description,Debit,Credit,Balance
2026-03-01,Opening Balance,,,45000
2026-03-05,Client XYZ Payment,,30000,75000
2026-03-10,Vendor ABC Textiles,15000,,60000
2026-03-15,Electricity Bill,3200,,56800
2026-03-18,Ad Campaign,5000,,51800
"""
    else:
        return f"Document: {filename}\n[Content extracted via OCR]"
