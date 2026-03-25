import { useEffect, useState } from 'react';
import { getPayables } from '../services/api';
import { AlertTriangle, CheckCircle, Clock } from 'lucide-react';

const fmt = (n: number) => `₹${Number(n)?.toLocaleString('en-IN') ?? 0}`;

const typeTag = (type: string) => <span className={`tag tag-${type}`}>{type}</span>;
const penaltyBadge = (p: string) => {
  const map: any = { none: 'badge-info', low: 'badge-success', medium: 'badge-warning', high: 'badge-danger', very_high: 'badge-danger' };
  return <span className={`badge ${map[p] || 'badge-info'}`}>{p}</span>;
};

export default function Obligations() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');

  useEffect(() => {
    getPayables().then(setData).finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="loading-center"><div className="spinner" /><span>Scoring obligations…</span></div>;
  if (!data) return null;

  const payables = data.payables.filter((p: any) =>
    filter === 'all' ? true :
    filter === 'critical' ? p.type === 'critical' :
    filter === 'flexible' ? p.type === 'flexible' : true
  );

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">Obligations & Payables</h1>
        <p className="page-subtitle">Scored and ranked by priority · {data.payables.length} total obligations</p>
      </div>

      {/* Summary */}
      <div className="kpi-grid" style={{ gridTemplateColumns: 'repeat(3, 1fr)', marginBottom: 20 }}>
        <div className="card">
          <div className="card-title">Total Due</div>
          <div className="card-value">{fmt(data.total_amount)}</div>
        </div>
        <div className="card">
          <div className="card-title">Critical</div>
          <div className="card-value" style={{ color: 'var(--danger)' }}>{data.critical_count}</div>
        </div>
        <div className="card">
          <div className="card-title">Flexible</div>
          <div className="card-value" style={{ color: 'var(--warning)' }}>{data.flexible_count}</div>
        </div>
      </div>

      {/* Filter */}
      <div style={{ display: 'flex', gap: 8, marginBottom: 16 }}>
        {['all', 'critical', 'flexible'].map(f => (
          <button key={f} className={`btn btn-sm ${filter === f ? 'btn-primary' : 'btn-ghost'}`}
            onClick={() => setFilter(f)} style={{ textTransform: 'capitalize' }}>{f}</button>
        ))}
      </div>

      <div className="card">
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>#</th>
                <th>Vendor / Obligation</th>
                <th>Amount</th>
                <th>Due Date</th>
                <th>Days Left</th>
                <th>Type</th>
                <th>Penalty</th>
                <th>Flexibility</th>
                <th>Priority Score</th>
              </tr>
            </thead>
            <tbody>
              {payables.map((p: any, i: number) => (
                <tr key={p.payable_id}>
                  <td style={{ color: 'var(--text-muted)', fontWeight: 700 }}>{i + 1}</td>
                  <td>
                    <div style={{ fontWeight: 600 }}>{p.vendor}</div>
                    {p.description && <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>{p.description}</div>}
                  </td>
                  <td style={{ fontWeight: 700 }}>{fmt(p.amount)}</td>
                  <td>{p.due_date}</td>
                  <td>
                    <span style={{
                      color: p.days_until_due <= 0 ? 'var(--danger)' :
                             p.days_until_due <= 3 ? 'var(--warning)' : 'var(--text-primary)',
                      fontWeight: 700
                    }}>
                      {p.days_until_due <= 0 ? 'OVERDUE' : `${p.days_until_due}d`}
                    </span>
                  </td>
                  <td>{typeTag(p.type)}</td>
                  <td>{penaltyBadge(p.penalty)}</td>
                  <td>
                    <span style={{ color: p.flexibility === 'none' ? 'var(--danger)' : 'var(--text-secondary)', fontSize: 12 }}>
                      {p.flexibility}
                    </span>
                  </td>
                  <td>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                      <div style={{ width: 60 }}>
                        <div className="progress-bar" style={{ height: 4 }}>
                          <div className="progress-fill" style={{
                            width: `${p.priority_score * 100}%`,
                            background: p.priority_score > 0.8 ? 'var(--danger)' : p.priority_score > 0.5 ? 'var(--warning)' : 'var(--accent)'
                          }} />
                        </div>
                      </div>
                      <span style={{ fontSize: 12, fontWeight: 700 }}>{(p.priority_score * 100).toFixed(0)}%</span>
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
