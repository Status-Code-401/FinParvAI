import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ingestBankCSV, ingestInvoices } from '../services/api';
import { Upload, FileText, CheckCircle, AlertCircle, ArrowRight, Banknote, ReceiptText, ScanText, Sparkles, Unlock } from 'lucide-react';

type UploadResult = {
  status: 'success' | 'error';
  message: string;
  details?: Record<string, string | number>;
};

// ─── Reusable Upload Card ────────────────────────────────────────────────────
function UploadCard({
  icon: Icon,
  title,
  description,
  accept,
  accentColor,
  onUpload,
}: {
  icon: React.ElementType;
  title: string;
  description: string;
  accept: string;
  accentColor: string;
  onUpload: (files: File[]) => Promise<UploadResult>;
}) {
  const [result, setResult] = useState<UploadResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [dragOver, setDragOver] = useState(false);

  const handle = async (files: File[]) => {
    if (!files.length) return;
    setLoading(true);
    setResult(null);
    try {
      const res = await onUpload(files);
      setResult(res);
    } catch (e: any) {
      setResult({ status: 'error', message: e.response?.data?.detail || e.message });
    } finally {
      setLoading(false);
    }
  };

  const openPicker = () => {
    const inp = document.createElement('input');
    inp.type = 'file';
    inp.accept = accept;
    inp.multiple = true;
    inp.onchange = (e: any) => handle(Array.from(e.target.files));
    inp.click();
  };

  return (
    <div className="card upload-card" style={{ borderTop: `2px solid ${accentColor}` }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'flex-start', gap: 14, marginBottom: 16 }}>
        <div style={{
          width: 40, height: 40, borderRadius: 10,
          background: `color-mix(in srgb, ${accentColor} 15%, transparent)`,
          border: `1px solid color-mix(in srgb, ${accentColor} 30%, transparent)`,
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          color: accentColor, flexShrink: 0
        }}>
          <Icon size={18} strokeWidth={1.8} />
        </div>
        <div>
          <div style={{ fontWeight: 700, fontSize: 15, color: 'var(--text-primary)' }}>{title}</div>
          <div style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 2 }}>{description}</div>
        </div>
      </div>

      {/* Drop zone */}
      <div
        className="upload-zone"
        style={{
          borderColor: dragOver ? accentColor : undefined,
          background: dragOver ? `color-mix(in srgb, ${accentColor} 8%, transparent)` : undefined,
          padding: '32px 16px',
        }}
        onDragOver={e => { e.preventDefault(); setDragOver(true); }}
        onDragLeave={() => setDragOver(false)}
        onDrop={e => { e.preventDefault(); setDragOver(false); handle(Array.from(e.dataTransfer.files)); }}
        onClick={openPicker}
      >
        {loading ? (
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 10 }}>
            <div className="spinner" style={{ borderTopColor: accentColor }} />
            <span style={{ fontSize: 13, color: 'var(--text-muted)' }}>Analysing your document…</span>
          </div>
        ) : result?.status === 'success' ? (
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 8 }}>
            <CheckCircle size={32} color="var(--success)" />
            <div style={{ fontWeight: 600, color: 'var(--success)', fontSize: 14 }}>Upload successful!</div>
            <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>Data parsed & dashboards updated.</div>
          </div>
        ) : (
          <>
            <div className="upload-zone-icon">📂</div>
            <div className="upload-zone-title">Drop your file here or click to browse</div>
            <div className="upload-zone-sub">Accepted formats: {accept}</div>
          </>
        )}
      </div>

      {/* Result */}
      {result && (
        <div className={`alert alert-${result.status === 'success' ? 'success' : 'danger'}`} style={{ marginTop: 14 }}>
          {result.status === 'success' ? <CheckCircle size={15} /> : <AlertCircle size={15} />}
          <div>
            <div style={{ fontWeight: 600 }}>{result.message}</div>
            {result.details && (
              <div style={{ marginTop: 6, fontSize: 11.5, display: 'flex', flexWrap: 'wrap', gap: 8 }}>
                {Object.entries(result.details).filter(([, v]) => v !== undefined && v !== null).map(([k, v]) => (
                  <span key={k} style={{ background: 'rgba(0,0,0,0.2)', borderRadius: 4, padding: '2px 7px' }}>
                    <strong>{k}:</strong> {String(v)}
                  </span>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

// ─── Step indicator ──────────────────────────────────────────────────────────
const STEPS = [
  { emoji: '📤', label: 'You upload', desc: 'Drop your bank statement, invoice, or receipt' },
  { emoji: '🤖', label: 'We read it', desc: 'AI extracts amounts, dates, and vendor names automatically' },
  { emoji: '📊', label: 'Dashboard updates', desc: 'Your cash flow, bills, and forecasts refresh instantly' },
  { emoji: '✅', label: 'You get answers', desc: 'See what to pay, what to collect, and how much you have' },
];

// ─── Main page ───────────────────────────────────────────────────────────────
export default function Ingest() {
  const navigate = useNavigate();
  const [anySuccess, setAnySuccess] = useState(false);
  const dataReady = sessionStorage.getItem('fp_data_ready') === 'true';

  /** Called when any upload card succeeds — unlocks all other pages. */
  const markDataReady = () => {
    sessionStorage.setItem('fp_data_ready', 'true');
    setAnySuccess(true);
  };

  return (
    <div>
      {/* Welcome header */}
      <div className="page-header">
        <h1 className="page-title">Welcome — Let's Get Your Data In</h1>
        <p className="page-subtitle">
          Upload your bank statements or invoices and FinParvai will do the rest. No manual entry needed.
        </p>
      </div>

      {/* "Dashboards unlocked" banner */}
      {(anySuccess || dataReady) && (
        <div className="card" style={{
          marginBottom: 20, background: 'rgba(34,197,94,0.08)', border: '1px solid rgba(34,197,94,0.3)',
          display: 'flex', alignItems: 'center', gap: 14, padding: '14px 20px'
        }}>
          <Unlock size={20} color="var(--success)" />
          <div style={{ flex: 1 }}>
            <div style={{ fontWeight: 700, fontSize: 14, color: 'var(--success)' }}>All dashboards unlocked!</div>
            <div style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 2 }}>
              Your data has been parsed and stored. All pages are now accessible.
            </div>
          </div>
          <button
            className="btn btn-primary"
            style={{ fontSize: 13, padding: '8px 20px' }}
            onClick={() => navigate('/')}
          >
            View Dashboard →
          </button>
        </div>
      )}

      {/* How it works */}
      <div className="card" style={{ marginBottom: 28, background: 'var(--accent-dim)', border: '1px solid rgba(79,142,247,0.2)' }}>
        <div style={{ fontWeight: 700, fontSize: 14, marginBottom: 16, display: 'flex', alignItems: 'center', gap: 8, color: 'var(--accent)' }}>
          <Sparkles size={16} /> How it works
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: 12 }}>
          {STEPS.map((s, i) => (
            <div key={i} style={{ display: 'flex', alignItems: 'flex-start', gap: 12 }}>
              <div style={{ fontSize: 22, flexShrink: 0, lineHeight: 1 }}>{s.emoji}</div>
              <div>
                <div style={{ fontWeight: 700, fontSize: 13, color: 'var(--text-primary)' }}>{s.label}</div>
                <div style={{ fontSize: 11.5, color: 'var(--text-muted)', marginTop: 3 }}>{s.desc}</div>
              </div>
              {i < STEPS.length - 1 && (
                <ArrowRight size={14} color="var(--text-muted)" style={{ marginTop: 3, flexShrink: 0 }} />
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Upload zones */}
      <div className="grid-3" style={{ marginBottom: 28, gap: 16 }}>
        <UploadCard
          icon={Banknote}
          title="Bank Statement"
          description="Your bank's CSV export — shows all payments in and out of your account."
          accept=".csv"
          accentColor="var(--accent)"
          onUpload={async (files) => {
            const res = await ingestBankCSV(files);
            markDataReady();
            return {
              status: 'success',
              message: `Processed ${files.length} bank statements and found ${res.transactions_parsed} transactions.`,
              details: { Transactions: res.transactions_parsed, Files: files.length },
            };
          }}
        />

        <UploadCard
          icon={ReceiptText}
          title="Invoices & Bills"
          description="Your sales invoices or purchase bills — in JSON format from your accounting app."
          accept=".json"
          accentColor="var(--success)"
          onUpload={async (files) => {
            const res = await ingestInvoices(files);
            markDataReady();
            return {
              status: 'success',
              message: `Processed ${files.length} invoice files. Found ${res.payables_found} bills to pay and ${res.receivables_found} invoices to collect`,
              details: { 'Bills to Pay': res.payables_found, 'To Collect': res.receivables_found },
            };
          }}
        />

        <UploadCard
          icon={ScanText}
          title="Any Document"
          description="Photo, PDF, or receipt — scan any document and AI will extract the details for you."
          accept=".pdf,.png,.jpg,.jpeg,.txt,.csv,.json"
          accentColor="var(--purple)"
          onUpload={async (files) => {
            const { ingestDocument } = await import('../services/api');
            const res = await ingestDocument(files);
            markDataReady();
            return {
              status: 'success',
              message: `Successfully read ${files.length} document(s).`,
              details: {
                Processed: res.documents_parsed,
              },
            };
          }}
        />
      </div>

      {/* Tips box */}
      <div className="card" style={{ borderLeft: '3px solid var(--warning)' }}>
        <div style={{ fontWeight: 700, fontSize: 14, marginBottom: 12, color: 'var(--warning)' }}>
          💡 Tips for best results
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: 10 }}>
          {[
            { q: 'Bank Statement', a: 'Export a CSV from your bank portal (SBI, HDFC, etc). Usually under "Download Statement".' },
            { q: 'Invoices', a: 'If you use Tally or Zoho, export your invoices as JSON. Or ask your accountant.' },
            { q: 'Receipts & PDFs', a: 'Take a clear photo or scan a PDF receipt. AI reads it automatically.' },
            { q: 'How often?', a: 'Upload once a week for the most accurate forecasts and action plans.' },
          ].map(tip => (
            <div key={tip.q} style={{ display: 'flex', gap: 10 }}>
              <FileText size={14} color="var(--text-muted)" style={{ marginTop: 2, flexShrink: 0 }} />
              <div>
                <div style={{ fontWeight: 600, fontSize: 12, color: 'var(--text-primary)' }}>{tip.q}</div>
                <div style={{ fontSize: 11.5, color: 'var(--text-muted)', marginTop: 2 }}>{tip.a}</div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
