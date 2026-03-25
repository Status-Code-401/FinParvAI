import { useState } from 'react';
import { ingestBankCSV, ingestInvoices } from '../services/api';
import { Upload, FileText, CheckCircle, AlertCircle } from 'lucide-react';

type UploadResult = {
  status: 'success' | 'error';
  message: string;
  details?: any;
};

function UploadZone({ label, accept, onUpload }: {
  label: string; accept: string; onUpload: (file: File) => Promise<UploadResult>;
}) {
  const [result, setResult] = useState<UploadResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [dragOver, setDragOver] = useState(false);

  const handle = async (file: File) => {
    setLoading(true);
    setResult(null);
    try {
      const res = await onUpload(file);
      setResult(res);
    } catch (e: any) {
      setResult({ status: 'error', message: e.response?.data?.detail || e.message });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card">
      <div style={{ fontWeight: 700, fontSize: 15, marginBottom: 16 }}>{label}</div>
      <div
        className="upload-zone"
        style={{ borderColor: dragOver ? 'var(--accent)' : undefined, background: dragOver ? 'var(--accent-dim)' : undefined }}
        onDragOver={e => { e.preventDefault(); setDragOver(true); }}
        onDragLeave={() => setDragOver(false)}
        onDrop={e => { e.preventDefault(); setDragOver(false); const f = e.dataTransfer.files[0]; if (f) handle(f); }}
        onClick={() => { const inp = document.createElement('input'); inp.type = 'file'; inp.accept = accept; inp.onchange = (e: any) => handle(e.target.files[0]); inp.click(); }}
      >
        {loading ? (
          <div><div className="spinner" style={{ margin: '0 auto' }} /></div>
        ) : (
          <>
            <div className="upload-zone-icon">📂</div>
            <div className="upload-zone-title">Drop file here or click to browse</div>
            <div className="upload-zone-sub">Accepted: {accept}</div>
          </>
        )}
      </div>

      {result && (
        <div className={`alert alert-${result.status === 'success' ? 'success' : 'danger'}`} style={{ marginTop: 16 }}>
          {result.status === 'success' ? <CheckCircle size={16} /> : <AlertCircle size={16} />}
          <div>
            <div style={{ fontWeight: 600 }}>{result.message}</div>
            {result.details && (
              <div style={{ marginTop: 8, fontSize: 12 }}>
                {Object.entries(result.details).map(([k, v]: any) => (
                  <div key={k}><strong>{k}:</strong> {String(v)}</div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default function Ingest() {
  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">Upload Financial Data</h1>
        <p className="page-subtitle">Ingest bank statements, invoices, and receipts for automated processing</p>
      </div>

      <div className="alert alert-info" style={{ marginBottom: 24 }}>
        Documents are parsed, classified, and merged into the unified financial state. The decision engine updates automatically.
      </div>

      <div className="grid-2">
        <UploadZone
          label="🏦 Bank Statement (CSV)"
          accept=".csv"
          onUpload={async (file) => {
            const res = await ingestBankCSV(file);
            return {
              status: 'success',
              message: `Parsed ${res.transactions_parsed} transactions from ${file.name}`,
              details: { Transactions: res.transactions_parsed, File: file.name }
            };
          }}
        />

        <UploadZone
          label="📄 Invoices (JSON)"
          accept=".json"
          onUpload={async (file) => {
            const res = await ingestInvoices(file);
            return {
              status: 'success',
              message: `Found ${res.payables_found} payables and ${res.receivables_found} receivables`,
              details: { Payables: res.payables_found, Receivables: res.receivables_found, File: file.name }
            };
          }}
        />
<<<<<<< HEAD

        <UploadZone
          label="🧾 Multimodal Document (PDF/Image/Text)"
          accept=".pdf,.png,.jpg,.jpeg,.txt,.csv,.json"
          onUpload={async (file) => {
            const { ingestDocument } = await import('../services/api');
            const res = await ingestDocument(file);
            return {
              status: 'success',
              message: `AI successfully analyzed ${file.name}`,
              details: { 
                Vendor: res.structured_data?.vendor, 
                Amount: res.structured_data?.amount, 
                Category: res.structured_data?.category 
              }
            };
          }}
        />
=======
>>>>>>> 8a75da474f1dede6cb8e19bd9cc9c818e7322948
      </div>

      <div className="card section-gap">
        <div style={{ fontWeight: 700, fontSize: 15, marginBottom: 16 }}>📋 Data Pipeline Overview</div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 0 }}>
          {[
            { step: '1', title: 'Upload', desc: 'CSV / JSON / PDF / Image uploaded and stored', color: 'var(--accent)' },
            { step: '2', title: 'Classify', desc: 'Document type detected: Bank Statement / Invoice / Receipt', color: 'var(--cyan)' },
            { step: '3', title: 'OCR & Extract', desc: 'Text extracted using Google Vision / Tesseract fallback', color: 'var(--purple)' },
            { step: '4', title: 'Parse & Structure', desc: 'LLM + Regex extracts amount, date, vendor, type', color: 'var(--warning)' },
            { step: '5', title: 'Normalize', desc: 'All data unified into single FinancialState schema', color: 'var(--success)' },
            { step: '6', title: 'Decision Engine', desc: 'Deterministic engine scores, projects, and allocates', color: 'var(--danger)' },
          ].map((s, i, arr) => (
            <div key={s.step} style={{ display: 'flex', gap: 16, paddingBottom: i < arr.length - 1 ? 20 : 0 }}>
              <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                <div style={{
                  width: 32, height: 32, borderRadius: '50%', background: s.color,
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  fontWeight: 800, fontSize: 13, color: 'white', flexShrink: 0
                }}>{s.step}</div>
                {i < arr.length - 1 && <div style={{ width: 2, flex: 1, background: 'var(--border)', marginTop: 4 }} />}
              </div>
              <div style={{ paddingTop: 6, paddingBottom: i < arr.length - 1 ? 16 : 0 }}>
                <div style={{ fontWeight: 700, marginBottom: 2 }}>{s.title}</div>
                <div style={{ fontSize: 12.5, color: 'var(--text-muted)' }}>{s.desc}</div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
