import { useEffect, useState } from 'react';
import { getRecommendations, getEmailDrafts } from '../services/api';
import { Mail, CheckCircle, Clock, TrendingDown, Zap, X, Copy, ExternalLink } from 'lucide-react';

const fmt = (n: number) => `₹${Number(n)?.toLocaleString('en-IN') ?? 0}`;

function EmailModal({ email, onClose }: { email: any; onClose: () => void }) {
  const [copied, setCopied] = useState(false);

  const copy = () => {
    navigator.clipboard.writeText(`Subject: ${email.subject}\n\n${email.body}`);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-box" onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <div>
            <div className="modal-title">{email.subject}</div>
            <div style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 4 }}>
              To: {email.to} · <span style={{ textTransform: 'capitalize' }}>{email.type.replace(/_/g, ' ')}</span>
            </div>
          </div>
          <div style={{ display: 'flex', gap: 8 }}>
            <button className="btn btn-ghost btn-sm" onClick={copy}>
              <Copy size={14} />{copied ? 'Copied!' : 'Copy'}
            </button>
            <button className="btn btn-ghost btn-sm" onClick={onClose}><X size={14} /></button>
          </div>
        </div>
        <div className="email-body">{email.body}</div>
        <div style={{ marginTop: 16, display: 'flex', gap: 8, alignItems: 'center' }}>
          <span className={`badge ${email.priority === 'HIGH' ? 'badge-danger' : 'badge-warning'}`}>{email.priority}</span>
          <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>Tone: {email.tone?.replace(/_/g, ' ')}</span>
        </div>
      </div>
    </div>
  );
}

const actionIcon = (type: string) => {
  const map: any = {
    payment: <CheckCircle size={16} color="var(--success)" />,
    partial_payment: <Clock size={16} color="var(--warning)" />,
    negotiate_delay: <Clock size={16} color="var(--warning)" />,
    cost_reduction: <TrendingDown size={16} color="var(--accent)" />,
    inventory_action: <Zap size={16} color="var(--purple)" />,
  };
  return map[type] || <Zap size={16} />;
};

export default function Actions() {
  const [recs, setRecs] = useState<any>(null);
  const [emails, setEmails] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [selectedEmail, setSelectedEmail] = useState<any>(null);
  const [tab, setTab] = useState<'actions' | 'emails'>('actions');

  useEffect(() => {
    Promise.all([getRecommendations(), getEmailDrafts()]).then(([r, e]) => {
      setRecs(r); setEmails(e);
    }).finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="loading-center"><div className="spinner" /><span>Generating actions & emails…</span></div>;

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">What To Do Next</h1>
        <p className="page-subtitle">Your personalised action list and ready-to-send emails — based on your latest data</p>
      </div>

      {/* Tabs */}
      <div style={{ display: 'flex', gap: 8, marginBottom: 20 }}>
        <button className={`btn ${tab === 'actions' ? 'btn-primary' : 'btn-ghost'}`} onClick={() => setTab('actions')}>
          My Action Plan ({recs?.actions?.length || 0})
        </button>
        <button className={`btn ${tab === 'emails' ? 'btn-primary' : 'btn-ghost'}`} onClick={() => setTab('emails')}>
          Ready-to-Send Emails ({emails?.total || 0})
        </button>
      </div>



      {tab === 'actions' && recs && (
        <>
          {/* Actions list */}
          <div className="card" style={{ marginBottom: 20 }}>
            <div style={{ fontWeight: 700, fontSize: 15, marginBottom: 16 }}>Your Prioritised Action Plan</div>
            {recs.actions.map((a: any, i: number) => (
              <div key={a.id} style={{
                display: 'flex', gap: 14, padding: '14px 0',
                borderBottom: '1px solid var(--border)', alignItems: 'flex-start'
              }}>
                <div style={{ paddingTop: 2 }}>{actionIcon(a.type)}</div>
                <div style={{ flex: 1 }}>
                  <div style={{ fontWeight: 600, marginBottom: 4 }}>{a.action}</div>
                  <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>{a.reason}</div>
                </div>
                <span className={`badge ${a.priority === 'HIGH' ? 'badge-danger' : a.priority === 'MEDIUM' ? 'badge-warning' : 'badge-info'}`}>
                  {a.priority}
                </span>
              </div>
            ))}
          </div>

          {/* Overhead */}
          {recs.overhead_optimization?.total_savings > 0 && (
            <div className="card" style={{ marginBottom: 20 }}>
              <div style={{ fontWeight: 700, fontSize: 15, marginBottom: 12 }}>
                💸 You Could Save {fmt(recs.overhead_optimization.total_savings)}
              </div>
              <div style={{ display: 'flex', gap: 16, flexWrap: 'wrap' }}>
                {[...recs.overhead_optimization.pause, ...recs.overhead_optimization.reduce].map((o: any) => (
                  <div key={o.type} className="card" style={{ width: 200, padding: 14 }}>
                    <div style={{ fontWeight: 600, textTransform: 'capitalize' }}>{o.type.replace(/_/g, ' ')}</div>
                    <div style={{ fontSize: 14, fontWeight: 800, color: 'var(--warning)', margin: '4px 0' }}>{fmt(o.saving)}</div>
                    <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>{o.action}</div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Shortfall */}
          {recs.shortfall?.shortfall_detected && (
            <div className="card">
              <div style={{ fontWeight: 700, fontSize: 15, marginBottom: 12 }}>🔧 How to Recover From a Cash Shortfall</div>
              <div className="alert alert-warning">{recs.shortfall.summary}</div>
              {recs.shortfall.strategies.map((s: any) => (
                <div key={s.strategy} style={{ marginBottom: 16 }}>
                  <div style={{ fontWeight: 600, color: 'var(--accent)', marginBottom: 8 }}>{s.strategy}</div>
                  {s.actions?.slice(0, 3).map((a: any, i: number) => (
                    <div key={i} style={{ fontSize: 12, color: 'var(--text-secondary)', padding: '4px 0 4px 16px' }}>
                      • {a.client || a.vendor || a.type || a.item} –{' '}
                      {a.amount ? fmt(a.amount) : a.saving ? fmt(a.saving) : a.liquidation_value ? fmt(a.liquidation_value) : ''}
                      {a.incentive && ` (${a.incentive})`}
                    </div>
                  ))}
                  <div style={{ fontSize: 12, color: 'var(--success)', marginTop: 4, paddingLeft: 16 }}>
                    Est. recovery: {fmt(s.estimated_recovery)}
                  </div>
                </div>
              ))}
            </div>
          )}
        </>
      )}

      {tab === 'emails' && emails && (
        <div>
          <div style={{ display: 'flex', gap: 12, marginBottom: 20, flexWrap: 'wrap' }}>
            <div className="card" style={{ padding: '12px 20px' }}>
              <div className="card-title">Total Drafts</div>
              <div style={{ fontSize: 24, fontWeight: 800 }}>{emails.total}</div>
            </div>
            <div className="card" style={{ padding: '12px 20px' }}>
              <div className="card-title">Collection Emails</div>
              <div style={{ fontSize: 24, fontWeight: 800, color: 'var(--accent)' }}>{emails.ar_emails}</div>
            </div>
            <div className="card" style={{ padding: '12px 20px' }}>
              <div className="card-title">Payment Delay Requests</div>
              <div style={{ fontSize: 24, fontWeight: 800, color: 'var(--warning)' }}>{emails.ap_emails}</div>
            </div>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
            {emails.emails.map((email: any) => (
              <div key={email.email_id} className="card" style={{ cursor: 'pointer' }}
                onClick={() => setSelectedEmail(email)}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                  <div style={{ display: 'flex', gap: 12, alignItems: 'flex-start', flex: 1 }}>
                    <Mail size={18} color={email.type === 'receivable_collection' ? 'var(--success)' : 'var(--warning)'} style={{ marginTop: 2 }} />
                    <div>
                      <div style={{ fontWeight: 700, marginBottom: 4 }}>{email.subject}</div>
                      <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>To: {email.to}</div>
                      <div style={{ fontSize: 12, color: 'var(--text-secondary)', marginTop: 6, lineHeight: 1.5 }}>
                        {email.body?.slice(0, 120)}…
                      </div>
                    </div>
                  </div>
                  <div style={{ display: 'flex', gap: 8, alignItems: 'center', flexShrink: 0 }}>
                    <span className={`badge ${email.priority === 'HIGH' ? 'badge-danger' : 'badge-warning'}`}>{email.priority}</span>
                    <ExternalLink size={14} color="var(--text-muted)" />
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {selectedEmail && <EmailModal email={selectedEmail} onClose={() => setSelectedEmail(null)} />}
    </div>
  );
}
