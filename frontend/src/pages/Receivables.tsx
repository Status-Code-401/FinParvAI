import { useEffect, useState } from 'react';
import { getReceivables } from '../services/api';
import { Phone, Mail, AlertCircle, CheckCircle } from 'lucide-react';

const fmt = (n: number) => `₹${Number(n)?.toLocaleString('en-IN') ?? 0}`;

const riskColor = (risk: string) => ({
  low: 'var(--success)', medium: 'var(--warning)', high: 'var(--danger)'
}[risk] || 'var(--text-muted)');

const statusBadge = (status: string, overdue: number) => {
  if (overdue > 0) return <span className="badge badge-danger">Overdue {overdue}d</span>;
  if (status === 'due_soon') return <span className="badge badge-warning">Due Soon</span>;
  return <span className="badge badge-info">Upcoming</span>;
};

export default function Receivables() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getReceivables().then(setData).finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="loading-center"><div className="spinner" /><span>Loading receivables…</span></div>;
  if (!data) return null;

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">Receivables (AR)</h1>
        <p className="page-subtitle">Accounts receivable with collection probability and client risk</p>
      </div>

      <div className="kpi-grid" style={{ gridTemplateColumns: 'repeat(3, 1fr)', marginBottom: 20 }}>
        <div className="card">
          <div className="card-title">Total Outstanding</div>
          <div className="card-value">{fmt(data.total_outstanding)}</div>
        </div>
        <div className="card">
          <div className="card-title">Expected Collection</div>
          <div className="card-value" style={{ color: 'var(--success)' }}>{fmt(data.total_expected)}</div>
          <div className="card-sub">probability-weighted</div>
        </div>
        <div className="card">
          <div className="card-title">Overdue Count</div>
          <div className="card-value" style={{ color: data.overdue_count > 0 ? 'var(--danger)' : 'var(--success)' }}>
            {data.overdue_count}
          </div>
        </div>
      </div>

      <div className="card">
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Client</th>
                <th>Amount</th>
                <th>Due / Expected</th>
                <th>Status</th>
                <th>Collection Prob.</th>
                <th>Risk</th>
                <th>Relationship</th>
                <th>Contact</th>
              </tr>
            </thead>
            <tbody>
              {data.receivables.map((r: any) => (
                <tr key={r.invoice_id}>
                  <td>
                    <div style={{ fontWeight: 600 }}>{r.client}</div>
                    <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>{r.invoice_id}</div>
                  </td>
                  <td style={{ fontWeight: 700 }}>{fmt(r.amount)}</td>
                  <td>
                    <div style={{ fontSize: 12 }}>{r.expected_date}</div>
                    {r.avg_payment_days && <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>avg {r.avg_payment_days}d to pay</div>}
                  </td>
                  <td>{statusBadge(r.status, r.days_overdue)}</td>
                  <td>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                      <div style={{ width: 60 }}>
                        <div className="progress-bar" style={{ height: 4 }}>
                          <div className="progress-fill" style={{
                            width: `${r.collection_probability * 100}%`,
                            background: r.collection_probability > 0.8 ? 'var(--success)' : r.collection_probability > 0.6 ? 'var(--warning)' : 'var(--danger)'
                          }} />
                        </div>
                      </div>
                      <span style={{ fontSize: 12, fontWeight: 700 }}>{Math.round(r.collection_probability * 100)}%</span>
                    </div>
                  </td>
                  <td>
                    <span style={{ color: riskColor(r.risk_level), fontWeight: 700, fontSize: 12, textTransform: 'uppercase' }}>
                      {r.risk_level}
                    </span>
                  </td>
                  <td style={{ fontSize: 12, color: 'var(--text-muted)' }}>
                    {r.relationship_months ? `${r.relationship_months}mo` : '—'}
                  </td>
                  <td>
                    <div style={{ fontSize: 11, color: 'var(--text-secondary)' }}>
                      {r.contact && <div>{r.contact}</div>}
                      {r.phone && (
                        <a href={`tel:${r.phone}`} style={{ color: 'var(--accent)', display: 'flex', alignItems: 'center', gap: 4 }}>
                          <Phone size={10} />{r.phone}
                        </a>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
