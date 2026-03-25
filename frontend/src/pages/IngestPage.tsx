import React, { useState, useRef, DragEvent } from 'react';
import { FinancialState } from '../types';
import { uploadDocument, getDemoState } from '../utils/api';

interface Props { state: FinancialState | null; onStateChange: (s: FinancialState) => void; }

export default function IngestPage({ state, onStateChange }: Props) {
  const [uploadResult, setUploadResult] = useState<any>(null);
  const [uploading, setUploading]       = useState(false);
  const [dragOver, setDragOver]         = useState(false);
  const [loadingDemo, setLoadingDemo]   = useState(false);
  const fileRef = useRef<HTMLInputElement>(null);

  const handleFile = async (file: File) => {
    setUploading(true);
    try {
      const r = await uploadDocument(file);
      setUploadResult(r);
    } catch(e: any) {
      setUploadResult({ error: e.message || 'Upload failed. Is the backend running?' });
    } finally { setUploading(false); }
  };

  const onDrop = (e: DragEvent) => {
    e.preventDefault(); setDragOver(false);
    const file = e.dataTransfer.files[0];
    if (file) handleFile(file);
  };

  const loadDemo = async () => {
    setLoadingDemo(true);
    try {
      const s = await getDemoState();
      onStateChange(s);
    } catch(e) {
      // fallback: use hardcoded demo
      onStateChange(DEMO_STATE as FinancialState);
    } finally { setLoadingDemo(false); }
  };

  return (
    <div>
      <div className="page-header">
        <div className="page-title">Data Ingest</div>
        <div className="page-subtitle">Upload financial documents · Multi-source normalisation · OCR extraction</div>
      </div>

      <div className="grid-2">
        {/* Upload Zone */}
        <div>
          <div className="card section-gap">
            <div className="card-title">Document Upload</div>
            <div
              className={`upload-zone ${dragOver ? 'drag-over' : ''}`}
              onClick={() => fileRef.current?.click()}
              onDragOver={e => { e.preventDefault(); setDragOver(true); }}
              onDragLeave={() => setDragOver(false)}
              onDrop={onDrop}
            >
              <div className="upload-icon">📄</div>
              <div className="upload-title">{uploading ? 'Processing...' : 'Drop files here or click to upload'}</div>
              <div className="upload-sub">Bank statements (CSV), Invoices (PDF/Image), Receipts (Image)</div>
            </div>
            <input
              ref={fileRef}
              type="file"
              style={{display:'none'}}
              accept=".csv,.pdf,.png,.jpg,.jpeg"
              onChange={e => e.target.files?.[0] && handleFile(e.target.files[0])}
            />
          </div>

          {/* Upload result */}
          {uploadResult && (
            <div className="card">
              <div className="card-title">Extraction Result</div>
              {uploadResult.error ? (
                <div style={{color:'#ff3b5c',fontSize:13}}>{uploadResult.error}</div>
              ) : (
                <>
                  <div style={{marginBottom:12}}>
                    <span className="tag">{uploadResult.classified_as}</span>
                    <span className="tag" style={{marginLeft:6}}>OCR {Math.round((uploadResult.ocr_confidence??0)*100)}%</span>
                  </div>
                  <pre style={{
                    fontFamily:'DM Mono,monospace', fontSize:11, color:'#7a8090',
                    background:'#0a0c10', borderRadius:8, padding:16,
                    overflow:'auto', maxHeight:300
                  }}>
                    {JSON.stringify(uploadResult.extracted_data, null, 2)}
                  </pre>
                </>
              )}
            </div>
          )}
        </div>

        {/* Pipeline Info + Demo State */}
        <div>
          <div className="card section-gap">
            <div className="card-title">Processing Pipeline</div>
            {[
              { icon: '⬆️', step: 'Upload & Storage',    desc: 'Files stored in Supabase/S3, document ID assigned' },
              { icon: '🔍', step: 'Classification',       desc: 'Rule-based: Bank / Invoice / Receipt' },
              { icon: '📝', step: 'OCR Extraction',       desc: 'Google Vision / Textract → raw text + key-values' },
              { icon: '🧠', step: 'Intelligent Parsing',  desc: 'LangChain + LLM extracts amounts, dates, vendors' },
              { icon: '🔗', step: 'Ledger Integration',   desc: 'Merge with historical ledger data for validation' },
              { icon: '✅', step: 'Normalisation',        desc: 'Unified financial state schema output' },
            ].map((s, i) => (
              <div key={i} style={{display:'flex',gap:12,padding:'10px 0',borderBottom:'1px solid #1e2330'}}>
                <div style={{fontSize:18,width:24,textAlign:'center',flexShrink:0}}>{s.icon}</div>
                <div>
                  <div style={{fontWeight:600,fontSize:13}}>{s.step}</div>
                  <div style={{fontSize:11,color:'#7a8090',marginTop:2}}>{s.desc}</div>
                </div>
              </div>
            ))}
          </div>

          <div className="card">
            <div className="card-title">Demo Financial State</div>
            <p style={{fontSize:13,color:'#7a8090',marginBottom:16,lineHeight:1.6}}>
              Load a realistic garment SME financial state with payables, receivables, inventory and vendor data to explore the full system.
            </p>
            <button className="btn btn-primary" onClick={loadDemo} disabled={loadingDemo} style={{width:'100%',justifyContent:'center'}}>
              {loadingDemo ? '⟳ Loading...' : '⚡ Load Demo State'}
            </button>
            {state && (
              <div style={{marginTop:16,padding:12,background:'#00e5a008',border:'1px solid #00e5a025',borderRadius:8}}>
                <div style={{fontSize:12,color:'#00e5a0',fontWeight:600,marginBottom:6}}>✓ State Loaded</div>
                <div style={{fontSize:11,color:'#7a8090',fontFamily:'DM Mono,monospace'}}>
                  Cash: ₹{state.cash_balance.toLocaleString('en-IN')} ·
                  Payables: {state.payables?.length ?? 0} ·
                  Receivables: {state.receivables?.length ?? 0}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Current State Preview */}
      {state && (
        <div className="card mt24">
          <div className="card-title">Current Financial State (Raw)</div>
          <pre style={{
            fontFamily:'DM Mono,monospace', fontSize:11, color:'#7a8090',
            background:'#0a0c10', borderRadius:8, padding:16,
            overflow:'auto', maxHeight:400
          }}>
            {JSON.stringify(state, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
}

const DEMO_STATE = {
  cash_balance: 45000,
  payables: [
    { vendor: "ABC Textiles",    amount: 15000, due_date: "2026-03-27", penalty: "high",   type: "critical",  linked_orders: [], priority_score: 0.9 },
    { vendor: "Fabric House",    amount: 12000, due_date: "2026-03-29", penalty: "medium", type: "flexible",  linked_orders: [], priority_score: 0.6 },
    { vendor: "Logistics Co",   amount: 5000,  due_date: "2026-04-02", penalty: "low",    type: "flexible",  linked_orders: [], priority_score: 0.3 },
    { vendor: "Marketing Agency",amount: 8000,  due_date: "2026-04-05", penalty: "low",    type: "flexible",  linked_orders: [], priority_score: 0.2 },
  ],
  receivables: [
    { client: "XYZ Retail",    amount: 30000, expected_date: "2026-03-28", collection_probability: 0.85 },
    { client: "Patel Exports", amount: 18000, expected_date: "2026-04-01", collection_probability: 0.70 },
  ],
  overheads: [
    { type: "electricity", amount: 3000,  essential: true  },
    { type: "ads",         amount: 5000,  essential: false },
    { type: "salaries",    amount: 35000, essential: true  },
    { type: "rent",        amount: 8000,  essential: true  },
    { type: "travel",      amount: 2000,  essential: false },
  ],
  ledger_summary: { monthly_income: 120000, monthly_expense: 100000, avg_payment_cycle_days: 7 },
  inventory_status: [
    { item: "Cotton Fabric",   available_quantity: 500, required_quantity: 300, shortage: 0, excess: 200 },
    { item: "Synthetic Blend", available_quantity: 100, required_quantity: 300, shortage: 200, excess: 0 },
    { item: "Thread",          available_quantity: 50,  required_quantity: 50,  shortage: 0,  excess: 0  },
  ],
  vendor_insights: [
    { vendor: "ABC Textiles", total_orders: 8, avg_lead_time: 3, payment_delay_avg: 1, reliability_score: 0.92, cost_efficiency_score: 0.78 },
    { vendor: "Fabric House", total_orders: 5, avg_lead_time: 4, payment_delay_avg: 2, reliability_score: 0.80, cost_efficiency_score: 0.72 },
  ],
  cost_breakdown: { internal: 10000, external: 25000 },
};
