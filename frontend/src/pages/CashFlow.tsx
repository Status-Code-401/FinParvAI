import { useEffect, useState } from 'react';
import { getCashFlow } from '../services/api';
import {
  AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer,
  CartesianGrid, BarChart, Bar, Legend, ReferenceLine
} from 'recharts';
import { TrendingDown, TrendingUp, Info } from 'lucide-react';

const fmt = (n: number) => `₹${Number(n)?.toLocaleString('en-IN') ?? 0}`;

export default function CashFlow() {
  const [data, setData] = useState<any>(null);
  const [days, setDays] = useState(30);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    getCashFlow(days).then(setData).finally(() => setLoading(false));
  }, [days]);

  if (loading) return <div className="loading-center"><div className="spinner" /><span>Simulating cash flow…</span></div>;
  if (!data) return null;

  const { projection, runway } = data;
  const chartData = projection.map((d: any) => ({
    date: d.date.slice(5),
    Cash: Math.round(d.cash),
    Inflows: Math.round(d.inflows),
    Outflows: Math.round(d.outflows),
    events: d.events
  }));

  const minCash = Math.min(...projection.map((d: any) => d.cash));
  const maxCash = Math.max(...projection.map((d: any) => d.cash));

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">Money In & Out</h1>
        <p className="page-subtitle">See exactly how much cash you'll have each day for the next {days} days</p>
      </div>

      {/* Runway summary cards */}
      <div className="kpi-grid" style={{ gridTemplateColumns: 'repeat(4, 1fr)', marginBottom: 24 }}>
        <div className="card">
          <div className="card-title">Money You Have Now</div>
          <div className="card-value">{fmt(data.cash_balance)}</div>
        </div>
        <div className="card">
          <div className="card-title">Days Until Cash Runs Out</div>
          <div className="card-value" style={{ color: runway.is_safe ? 'var(--success)' : 'var(--danger)' }}>
            {runway.is_safe ? `${days}+` : runway.days_to_zero}
          </div>
          <div className="card-sub">{runway.is_safe ? 'Safe' : `Negative on ${runway.first_negative_date}`}</div>
        </div>
        <div className="card">
          <div className="card-title">Min Cash</div>
          <div className="card-value" style={{ color: minCash < 0 ? 'var(--danger)' : 'var(--warning)' }}>
            {fmt(Math.round(minCash))}
          </div>
        </div>
        <div className="card">
          <div className="card-title">Max Cash</div>
          <div className="card-value" style={{ color: 'var(--success)' }}>{fmt(Math.round(maxCash))}</div>
        </div>
      </div>

      {/* Runway alert */}
      {!runway.is_safe && (
        <div className="alert alert-danger">
          <TrendingDown size={18} />
          <div>Your cash may run out on <strong>Day {runway.days_to_zero}</strong> ({runway.first_negative_date}). Check "What To Do Next" for immediate steps.</div>
        </div>
      )}
      {runway.is_safe && (
        <div className="alert alert-success">
          <TrendingUp size={18} />
          You're in good shape! Cash stays positive for the next {days} days.
        </div>
      )}

      {/* Controls */}
      <div style={{ display: 'flex', gap: 8, marginBottom: 20 }}>
        {[7, 14, 30, 45].map(d => (
          <button key={d} className={`btn btn-sm ${days === d ? 'btn-primary' : 'btn-ghost'}`}
            onClick={() => setDays(d)}>{d} days</button>
        ))}
      </div>

      {/* Area chart */}
      <div className="card" style={{ marginBottom: 20 }}>
        <div style={{ fontWeight: 700, fontSize: 15, marginBottom: 16 }}>Your Cash Balance Day by Day</div>
        <ResponsiveContainer width="100%" height={280}>
          <AreaChart data={chartData}>
            <defs>
              <linearGradient id="posGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="var(--accent)" stopOpacity={0.4} />
                <stop offset="95%" stopColor="var(--accent)" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
            <XAxis dataKey="date" tick={{ fill: 'var(--text-muted)', fontSize: 11 }} interval={Math.floor(days / 7)} />
            <YAxis tick={{ fill: 'var(--text-muted)', fontSize: 11 }} tickFormatter={v => `₹${(v / 1000).toFixed(0)}K`} />
            <Tooltip
              contentStyle={{ background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 8, fontSize: 12 }}
              formatter={(v: any) => [fmt(v)]}
            />
            <ReferenceLine y={0} stroke="var(--danger)" strokeDasharray="4 4" label={{ value: 'Zero', fill: 'var(--danger)', fontSize: 11 }} />
            <Area type="monotone" dataKey="Cash" stroke="var(--accent)" fill="url(#posGrad)" strokeWidth={2.5} />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      {/* Bar chart */}
      <div className="card">
        <div style={{ fontWeight: 700, fontSize: 15, marginBottom: 16 }}>Daily Money Coming In vs Going Out</div>
        <ResponsiveContainer width="100%" height={220}>
          <BarChart data={chartData} barGap={2}>
            <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
            <XAxis dataKey="date" tick={{ fill: 'var(--text-muted)', fontSize: 11 }} interval={Math.floor(days / 7)} />
            <YAxis tick={{ fill: 'var(--text-muted)', fontSize: 11 }} tickFormatter={v => `₹${(v / 1000).toFixed(0)}K`} />
            <Tooltip
              contentStyle={{ background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 8, fontSize: 12 }}
              formatter={(v: any) => [fmt(v)]}
            />
            <Legend />
            <Bar dataKey="Inflows" fill="var(--success)" radius={[3, 3, 0, 0]} />
            <Bar dataKey="Outflows" fill="var(--danger)" radius={[3, 3, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Event log */}
      <div className="card section-gap">
        <div style={{ fontWeight: 700, fontSize: 15, marginBottom: 16 }}>Important Dates & Events</div>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Date</th>
                <th>Cash After</th>
                <th>Events</th>
              </tr>
            </thead>
            <tbody>
              {projection.filter((d: any) => d.events?.length > 0).map((d: any) => (
                <tr key={d.date}>
                  <td>{d.date}</td>
                  <td style={{ color: d.cash < 0 ? 'var(--danger)' : 'var(--success)', fontWeight: 700 }}>{fmt(Math.round(d.cash))}</td>
                  <td>{d.events.join(' · ')}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
