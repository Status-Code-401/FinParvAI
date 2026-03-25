import React, { useState } from 'react';
import { FinancialState, Prediction } from '../types';
import { getForecast } from '../utils/api';
import {
  AreaChart, Area, LineChart, Line,
  XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Legend
} from 'recharts';

interface Props { state: FinancialState | null; }
const fmtINR = (n: number) => `₹${Math.round(n).toLocaleString('en-IN')}`;

export default function ForecastPage({ state }: Props) {
  const [result, setResult] = useState<Prediction | null>(null);
  const [loading, setLoading] = useState(false);
  const [horizon, setHorizon] = useState(30);

  const run = async () => {
    if (!state) return;
    setLoading(true);
    try {
      const d = await getForecast(state, horizon);
      setResult(d);
    } finally { setLoading(false); }
  };

  const revData = result?.revenue_forecast.map(d => ({
    date: d.date.slice(5),
    value: d.value,
    lower: d.lower_bound,
    upper: d.upper_bound,
  })) ?? [];

  const cashData = result?.cash_flow_forecast.map(d => ({
    date: d.date.slice(5),
    value: d.value,
    lower: d.lower_bound,
    upper: d.upper_bound,
  })) ?? [];

  const shapEntries = result
    ? Object.entries(result.shap_explanations).sort((a,b) => Math.abs(Number(b[1])) - Math.abs(Number(a[1])))
    : [];
  const maxShap = shapEntries.length > 0 ? Math.max(...shapEntries.map(([,v]) => Math.abs(Number(v)))) : 1;

  return (
    <div>
      <div className="page-header flex-between">
        <div>
          <div className="page-title">Predictive Forecast</div>
          <div className="page-subtitle">Revenue & cash flow projections · Festival demand signals · SHAP explanations</div>
        </div>
        <div className="flex-gap">
          <select
            value={horizon}
            onChange={e => setHorizon(Number(e.target.value))}
            style={{background:'#111318',border:'1px solid #2a3040',color:'#e8eaf0',borderRadius:8,padding:'8px 12px',fontSize:13}}
          >
            <option value={7}>7 days</option>
            <option value={14}>14 days</option>
            <option value={30}>30 days</option>
          </select>
          <button className="btn btn-primary" onClick={run} disabled={!state || loading}>
            {loading ? '◎ Forecasting...' : '◎ Generate Forecast'}
          </button>
        </div>
      </div>

      {!result && !loading && (
        <div className="card empty-state">
          <div className="empty-state-icon">◎</div>
          <div className="empty-state-text">Click "Generate Forecast" to project revenue, demand, and cash flow.</div>
        </div>
      )}

      {result && (
        <>
          {/* Festival Banner */}
          {result.festival_impact && (
            <div style={{background:'#ffb80012',border:'1px solid #ffb80030',borderRadius:12,padding:'16px 20px',marginBottom:24,display:'flex',alignItems:'center',gap:12}}>
              <span style={{fontSize:24}}>🎉</span>
              <div>
                <div style={{fontWeight:600,color:'#ffb800'}}>Festival Demand Signal: {result.festival_impact}</div>
                <div style={{fontSize:12,color:'#7a8090',marginTop:2}}>
                  Demand multiplier: <strong style={{color:'#ffb800'}}>{result.demand_multiplier}×</strong> — consider increasing inventory procurement.
                </div>
              </div>
            </div>
          )}

          {/* Stats */}
          <div className="stats-grid">
            <div className="stat-card">
              <div className="stat-label">Demand Multiplier</div>
              <div className="stat-value accent">{result.demand_multiplier}×</div>
              <div className="stat-sub">{result.festival_impact ?? 'No festival signal'}</div>
            </div>
            <div className="stat-card">
              <div className="stat-label">Avg Daily Revenue (forecast)</div>
              <div className="stat-value accent">
                {result.revenue_forecast.length > 0
                  ? fmtINR(result.revenue_forecast.reduce((s,d)=>s+d.value,0) / result.revenue_forecast.length)
                  : '—'}
              </div>
              <div className="stat-sub">Over {horizon}-day horizon</div>
            </div>
            <div className="stat-card">
              <div className="stat-label">Forecast Horizon</div>
              <div className="stat-value accent">{horizon}d</div>
              <div className="stat-sub">Projection window</div>
            </div>
          </div>

          {/* Revenue Forecast Chart */}
          <div className="card section-gap">
            <div className="card-title">Revenue Forecast (with confidence bands)</div>
            <ResponsiveContainer width="100%" height={220}>
              <AreaChart data={revData} margin={{top:4,right:4,bottom:0,left:0}}>
                <defs>
                  <linearGradient id="revGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#00e5a0" stopOpacity={0.3} />
                    <stop offset="100%" stopColor="#00e5a0" stopOpacity={0.02} />
                  </linearGradient>
                  <linearGradient id="bandGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#3d7fff" stopOpacity={0.1} />
                    <stop offset="100%" stopColor="#3d7fff" stopOpacity={0.02} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e2330" />
                <XAxis dataKey="date" tick={{fill:'#7a8090',fontSize:10}} tickLine={false} axisLine={false}
                  interval={Math.floor(revData.length / 6)} />
                <YAxis tick={{fill:'#7a8090',fontSize:10}} tickLine={false} axisLine={false}
                  tickFormatter={v=>`₹${(v/1000).toFixed(1)}k`} />
                <Tooltip
                  contentStyle={{background:'#111318',border:'1px solid #1e2330',borderRadius:'8px',fontSize:'12px'}}
                  formatter={(v:any) => [fmtINR(v)]}
                />
                <Area type="monotone" dataKey="upper" stroke="none" fill="url(#bandGrad)" name="Upper" />
                <Area type="monotone" dataKey="value" stroke="#00e5a0" strokeWidth={2} fill="url(#revGrad)" name="Revenue" />
                <Area type="monotone" dataKey="lower" stroke="none" fill="transparent" name="Lower" />
              </AreaChart>
            </ResponsiveContainer>
          </div>

          {/* Cash Forecast Chart */}
          <div className="card section-gap">
            <div className="card-title">Cash Flow Forecast</div>
            <ResponsiveContainer width="100%" height={200}>
              <AreaChart data={cashData} margin={{top:4,right:4,bottom:0,left:0}}>
                <defs>
                  <linearGradient id="cashFGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#3d7fff" stopOpacity={0.3} />
                    <stop offset="100%" stopColor="#3d7fff" stopOpacity={0.02} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e2330" />
                <XAxis dataKey="date" tick={{fill:'#7a8090',fontSize:10}} tickLine={false} axisLine={false}
                  interval={Math.floor(cashData.length / 6)} />
                <YAxis tick={{fill:'#7a8090',fontSize:10}} tickLine={false} axisLine={false}
                  tickFormatter={v=>`₹${(v/1000).toFixed(0)}k`} />
                <Tooltip
                  contentStyle={{background:'#111318',border:'1px solid #1e2330',borderRadius:'8px',fontSize:'12px'}}
                  formatter={(v:any) => [fmtINR(v)]}
                />
                <Area type="monotone" dataKey="value" stroke="#3d7fff" strokeWidth={2} fill="url(#cashFGrad)" name="Cash" />
              </AreaChart>
            </ResponsiveContainer>
          </div>

          <div className="grid-2">
            {/* SHAP Explanations */}
            <div className="card">
              <div className="card-title">Feature Attribution (SHAP)</div>
              {shapEntries.map(([key, val], i) => (
                <div key={i} className="shap-row">
                  <div className="shap-label">{key.replace(/_/g,' ')}</div>
                  <div className="shap-bar-wrap">
                    <div className="shap-bar-fill" style={{width:`${(Math.abs(Number(val)) / maxShap) * 100}%`}} />
                  </div>
                  <div className="shap-val">{Number(val).toFixed(2)}</div>
                </div>
              ))}
            </div>

            {/* Recommendations */}
            <div className="card">
              <div className="card-title">AI Recommendations</div>
              <div className="rec-list">
                {result.recommendations.map((r, i) => (
                  <div key={i} className="rec-item">
                    <div className="rec-icon">{r.split(' ')[0]}</div>
                    <div style={{fontSize:13}}>{r.slice(r.indexOf(' ')+1)}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
