import { useEffect, useState } from 'react';
import { getTransactions } from '../services/api';
import { ArrowUpRight, ArrowDownRight } from 'lucide-react';

const fmt = (n: number) => `₹${Number(n || 0)?.toLocaleString('en-IN')}`;
const categoryColor: any = {
  receivable_collection: 'var(--success)',
  vendor_payment: 'var(--danger)',
  salary: 'var(--danger)',
  utility: 'var(--warning)',
  marketing: 'var(--warning)',
  logistics: 'var(--text-muted)',
  rent: 'var(--danger)',
  misc: 'var(--text-muted)'
};

export default function Transactions() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [catFilter, setCatFilter] = useState('all');

  useEffect(() => {
    getTransactions().then(setData).finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="loading-center"><div className="spinner" /></div>;
  if (!data) return null;

  const categories = ['all', ...Array.from(new Set(data.transactions.map((t: any) => t.category).filter(Boolean)))];
  const filtered = data.transactions.filter((t: any) => {
    const matchSearch = !search || t.description?.toLowerCase().includes(search.toLowerCase());
    const matchCat = catFilter === 'all' || t.category === catFilter;
    return matchSearch && matchCat;
  });

  const totalCredits = data.transactions.reduce((s: number, t: any) => s + (t.credit || 0), 0);
  const totalDebits = data.transactions.reduce((s: number, t: any) => s + (t.debit || 0), 0);

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">Transaction History</h1>
        <p className="page-subtitle">{data.total} transactions from bank statement</p>
      </div>

      <div className="kpi-grid" style={{ gridTemplateColumns: 'repeat(3, 1fr)', marginBottom: 20 }}>
        <div className="card">
          <div className="card-title">Total Credits</div>
          <div className="card-value" style={{ color: 'var(--success)' }}>{fmt(totalCredits)}</div>
        </div>
        <div className="card">
          <div className="card-title">Total Debits</div>
          <div className="card-value" style={{ color: 'var(--danger)' }}>{fmt(totalDebits)}</div>
        </div>
        <div className="card">
          <div className="card-title">Net Flow</div>
          <div className="card-value" style={{ color: totalCredits - totalDebits >= 0 ? 'var(--success)' : 'var(--danger)' }}>
            {fmt(Math.abs(totalCredits - totalDebits))}
          </div>
        </div>
      </div>

      {/* Controls */}
      <div style={{ display: 'flex', gap: 12, marginBottom: 16, flexWrap: 'wrap' }}>
        <input
          placeholder="Search transactions…"
          value={search}
          onChange={e => setSearch(e.target.value)}
          style={{
            background: 'var(--bg-card)', border: '1px solid var(--border)',
            borderRadius: 'var(--radius-sm)', padding: '8px 14px',
            color: 'var(--text-primary)', fontSize: 13, width: 240
          }}
        />
        <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
          {categories.slice(0, 6).map((c: any) => (
            <button key={String(c)} className={`btn btn-sm ${catFilter === c ? 'btn-primary' : 'btn-ghost'}`}
              onClick={() => setCatFilter(String(c))} style={{ textTransform: 'capitalize', fontSize: 11 }}>
              {String(c).replace(/_/g, ' ')}
            </button>
          ))}
        </div>
      </div>

      <div className="card">
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Date</th>
                <th>Description</th>
                <th>Category</th>
                <th style={{ textAlign: 'right' }}>Debit</th>
                <th style={{ textAlign: 'right' }}>Credit</th>
                <th style={{ textAlign: 'right' }}>Balance</th>
              </tr>
            </thead>
            <tbody>
              {filtered.slice(0, 60).map((t: any, i: number) => (
                <tr key={i}>
                  <td style={{ color: 'var(--text-muted)', fontSize: 12 }}>{t.date}</td>
                  <td style={{ fontWeight: 500, maxWidth: 280 }}>{t.description}</td>
                  <td>
                    <span style={{
                      fontSize: 11, color: categoryColor[t.category] || 'var(--text-muted)',
                      textTransform: 'capitalize', fontWeight: 600
                    }}>
                      {t.category?.replace(/_/g, ' ') || '—'}
                    </span>
                  </td>
                  <td style={{ textAlign: 'right', color: 'var(--danger)', fontWeight: 600 }}>
                    {t.debit ? fmt(t.debit) : '—'}
                  </td>
                  <td style={{ textAlign: 'right', color: 'var(--success)', fontWeight: 600 }}>
                    {t.credit ? fmt(t.credit) : '—'}
                  </td>
                  <td style={{ textAlign: 'right', fontWeight: 700 }}>
                    {t.balance ? fmt(t.balance) : '—'}
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
