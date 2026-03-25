import { useEffect, useState } from 'react';
import { getForecast } from '../services/api';
import {
  LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer,
  CartesianGrid, BarChart, Bar, Legend
} from 'recharts';

const fmt = (n: number) => `₹${Number(n)?.toLocaleString('en-IN') ?? 0}`;

export default function Forecast() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getForecast().then(setData).finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="loading-center"><div className="spinner" /><span>Running forecast models…</span></div>;
  if (!data) return null;

  const { revenue_forecast, seasonal_insights, monthly_summary, demand_forecast, key_insights } = data;

  const monthlyChart = monthly_summary?.map((m: any) => ({
    month: m.month?.slice(0, 7),
    Income: m.income,
    Expense: m.expense,
    Net: m.net
  })) || [];

  const forecastChart = [
    ...monthly_summary?.map((m: any) => ({ month: m.month?.slice(0, 7), Income: m.income, isForecast: false })) || [],
    ...revenue_forecast.forecast?.map((v: number, i: number) => ({
      month: `Forecast ${i + 1}`,
      Income: v,
      isForecast: true
    })) || []
  ];

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">Predictive Forecast</h1>
        <p className="page-subtitle">Statistical revenue & demand forecasting · {revenue_forecast.trend} trend</p>
      </div>

      {/* Trend KPIs */}
      <div className="kpi-grid" style={{ gridTemplateColumns: 'repeat(4, 1fr)', marginBottom: 20 }}>
        <div className="card">
          <div className="card-title">Avg Monthly Income</div>
          <div className="card-value">{fmt(seasonal_insights.avg_monthly_income)}</div>
        </div>
        <div className="card">
          <div className="card-title">Avg Monthly Expense</div>
          <div className="card-value">{fmt(seasonal_insights.avg_monthly_expense)}</div>
        </div>
        <div className="card">
          <div className="card-title">Revenue Trend</div>
          <div className="card-value" style={{
            color: revenue_forecast.trend === 'up' ? 'var(--success)' :
                   revenue_forecast.trend === 'down' ? 'var(--danger)' : 'var(--warning)',
            fontSize: 20
          }}>
            {revenue_forecast.trend === 'up' ? '↑ Growing' : revenue_forecast.trend === 'down' ? '↓ Declining' : '→ Stable'}
          </div>
        </div>
        <div className="card">
          <div className="card-title">Daily Avg Production</div>
          <div className="card-value">{demand_forecast?.avg_daily_units} units</div>
          <div className="card-sub">{demand_forecast?.trend}</div>
        </div>
      </div>

      {/* Key Insights */}
      {key_insights?.length > 0 && (
        <div className="card" style={{ marginBottom: 20 }}>
          <div style={{ fontWeight: 700, fontSize: 15, marginBottom: 12 }}>💡 Key Insights</div>
          {key_insights.map((ins: string, i: number) => (
            <div key={i} style={{ display: 'flex', gap: 10, padding: '6px 0', borderBottom: '1px solid var(--border)' }}>
              <span style={{ color: 'var(--accent)', fontWeight: 700 }}>{i + 1}.</span>
              <span style={{ fontSize: 13, color: 'var(--text-secondary)' }}>{ins}</span>
            </div>
          ))}
        </div>
      )}

      {/* Monthly P&L */}
      <div className="card" style={{ marginBottom: 20 }}>
        <div style={{ fontWeight: 700, fontSize: 15, marginBottom: 16 }}>Monthly P&L History</div>
        <ResponsiveContainer width="100%" height={240}>
          <BarChart data={monthlyChart} barGap={4}>
            <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
            <XAxis dataKey="month" tick={{ fill: 'var(--text-muted)', fontSize: 11 }} />
            <YAxis tick={{ fill: 'var(--text-muted)', fontSize: 11 }} tickFormatter={v => `₹${(v / 1000).toFixed(0)}K`} />
            <Tooltip
              contentStyle={{ background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 8, fontSize: 12 }}
              formatter={(v: any) => [fmt(v)]}
            />
            <Legend />
            <Bar dataKey="Income" fill="var(--success)" radius={[3, 3, 0, 0]} />
            <Bar dataKey="Expense" fill="var(--danger)" radius={[3, 3, 0, 0]} />
            <Bar dataKey="Net" fill="var(--accent)" radius={[3, 3, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Revenue Forecast */}
      <div className="card" style={{ marginBottom: 20 }}>
        <div style={{ fontWeight: 700, fontSize: 15, marginBottom: 16 }}>
          Revenue Forecast (Historical + Predicted)
        </div>
        <ResponsiveContainer width="100%" height={220}>
          <LineChart data={forecastChart}>
            <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
            <XAxis dataKey="month" tick={{ fill: 'var(--text-muted)', fontSize: 11 }} />
            <YAxis tick={{ fill: 'var(--text-muted)', fontSize: 11 }} tickFormatter={v => `₹${(v / 1000).toFixed(0)}K`} />
            <Tooltip
              contentStyle={{ background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 8, fontSize: 12 }}
              formatter={(v: any) => [fmt(v)]}
            />
            <Line type="monotone" dataKey="Income" stroke="var(--accent)" strokeWidth={2.5}
              dot={(props) => {
                const { cx, cy, payload } = props;
                return <circle cx={cx} cy={cy} r={4} fill={payload.isForecast ? 'var(--purple)' : 'var(--accent)'} />;
              }}
            />
          </LineChart>
        </ResponsiveContainer>
        <div style={{ display: 'flex', gap: 16, marginTop: 12, fontSize: 12, color: 'var(--text-muted)' }}>
          <span style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
            <span style={{ width: 12, height: 12, borderRadius: '50%', background: 'var(--accent)', display: 'inline-block' }} />
            Historical
          </span>
          <span style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
            <span style={{ width: 12, height: 12, borderRadius: '50%', background: 'var(--purple)', display: 'inline-block' }} />
            Forecast
          </span>
        </div>
      </div>

      {/* Monthly table */}
      <div className="card">
        <div style={{ fontWeight: 700, fontSize: 15, marginBottom: 16 }}>Historical Monthly Summary</div>
        <div className="table-wrap">
          <table>
            <thead>
              <tr><th>Month</th><th>Income</th><th>Expense</th><th>Net</th><th>Opening</th><th>Closing</th></tr>
            </thead>
            <tbody>
              {monthly_summary?.map((m: any) => (
                <tr key={m.month}>
                  <td style={{ fontWeight: 600 }}>{m.month}</td>
                  <td style={{ color: 'var(--success)', fontWeight: 700 }}>{fmt(m.income)}</td>
                  <td style={{ color: 'var(--danger)', fontWeight: 700 }}>{fmt(m.expense)}</td>
                  <td style={{ color: m.net >= 0 ? 'var(--success)' : 'var(--danger)', fontWeight: 700 }}>{fmt(m.net)}</td>
                  <td>{fmt(m.opening_balance)}</td>
                  <td>{fmt(m.closing_balance)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
