import React, { useState } from 'react';
import { FinancialState, DecisionOutput } from '../types';
import { runDecision } from '../utils/api';
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Cell
} from 'recharts';

interface Props { state: FinancialState | null; }
const fmtINR = (n: number) => `₹${Math.round(n).toLocaleString('en-IN')}`;

export default function DecisionPage({ state }: Props) {
  const [result, setResult] = useState<DecisionOutput | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError]   = useState('');

  const run = async () => {
    if (!state) return;
    setLoading(true); setError('');
    try {
      const d = await runDecision(state);
      setResult(d);
    } catch(e: any) {
      setError(e.message || 'Engine failed');
    } finally {
      setLoading(false);
    }
  };

  const chartData = result?.cash_flow_projection.map(d => ({
    date: d.date.slice(5),
    cash: Math.max(d.closing_cash, 0),
    negative: d.closing_cash < 0 ? Math.abs(d.closing_cash) : 0,
    inflows: d.inflows,
    outflows: d.outflows,
  })) ?? [];

  const actionColors: Record<string, string> = {
    pay_now: '#00e5a0',
    partial: '#3d7fff',
    delay:   '#ffb800',
  };

  return (
    <div>
      <div className="page-header flex-between">
        <div>
          <div className="page-title">Decision Engine</div>
          <div className="page-subtitle">Deterministic obligation scoring · Payment allocation · Recovery strategies</div>
        </div>
        <button className="btn btn-primary" onClick={run} disabled={!state || loading}>
          {loading ? '⚙️ Running...' : '⚡ Run Engine'}
        </button>
      </div>

      {error && <div style={{background:'#ff3b5c15',border:'1px solid #ff3b5c30',borderRadius:8,padding:14,marginBottom:20,color:'#ff3b5c',fontSize:13}}>{error}</div>}

      {!result && !loading && (
        <div className="card empty-state">
          <div className="empty-state-icon">⚡</div>
          <div className="empty-state-text">Click "Run Engine" to analyse your financial state and generate a decision plan.</div>
        </div>
      )}

      {result && (
        <>
          {/* Summary stats */}
          <div className="stats-grid">
            <div className={`stat-card ${result.risk_level === 'low' ? '' : result.risk_level}`}>
              <div className="stat-label">Risk Level</div>
              <div className={`stat-value ${result.risk_level === 'low' ? 'accent' : result.risk_level === 'medium' ? 'warn' : 'danger'}`}>
                {result.risk_level.toUpperCase()}
              </div>
              <div className="stat-sub">{result.is_safe ? 'Cash flow stable' : 'Action required'}</div>
            </div>
            <div className="stat-card">
              <div className="stat-label">Runway</div>
              <div className={`stat-value ${result.runway_days >= 10 ? 'accent' : result.runway_days >= 5 ? 'warn' : 'danger'}`}>
                {result.runway_days}d
              </div>
              <div className="stat-sub">Days before zero</div>
            </div>
            <div className="stat-card">
              <div className="stat-label">Pay Now</div>
              <div className="stat-value accent">{result.pay_now.length}</div>
              <div className="stat-sub">Immediate payments</div>
            </div>
            <div className="stat-card warn">
              <div className="stat-label">Delayed</div>
              <div className="stat-value warn">{result.delay.length}</div>
              <div className="stat-sub">Rescheduled obligations</div>
            </div>
            <div className="stat-card info">
              <div className="stat-label">Partial</div>
              <div className="stat-value" style={{color:'#3d7fff'}}>{result.partial.length}</div>
              <div className="stat-sub">Partial allocations</div>
            </div>
            <div className="stat-card">
              <div className="stat-label">Confidence</div>
              <div className="stat-value accent">{Math.round(result.confidence_score * 100)}%</div>
              <div className="stat-sub">Engine certainty</div>
            </div>
          </div>

          {/* Cash flow chart */}
          <div className="card section-gap">
            <div className="card-title">14-Day Cash Flow Simulation</div>
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={chartData} margin={{top:4,right:4,bottom:0,left:0}}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e2330" />
                <XAxis dataKey="date" tick={{fill:'#7a8090',fontSize:10}} tickLine={false} axisLine={false} />
                <YAxis tick={{fill:'#7a8090',fontSize:10}} tickLine={false} axisLine={false} tickFormatter={v=>`₹${(v/1000).toFixed(0)}k`} />
                <Tooltip
                  contentStyle={{background:'#111318',border:'1px solid #1e2330',borderRadius:'8px',fontSize:'12px'}}
                  formatter={(v:any) => [fmtINR(v)]}
                />
                <Bar dataKey="cash" radius={[4,4,0,0]} name="Cash">
                  {chartData.map((d, i) => (
                    <Cell key={i} fill={d.cash > 0 ? '#00e5a0' : '#ff3b5c'} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div className="grid-2">
            {/* Scored payables */}
            <div className="card">
              <div className="card-title">Obligation Scoring & Allocation</div>
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Vendor</th>
                    <th>Amount</th>
                    <th>Score</th>
                    <th>Action</th>
                  </tr>
                </thead>
                <tbody>
                  {result.scored_payables.map((sp, i) => (
                    <tr key={i} title={sp.reason}>
                      <td style={{fontWeight:500}}>{sp.vendor}</td>
                      <td className="mono">{fmtINR(sp.partial_amount ?? sp.amount)}</td>
                      <td>
                        <div className="score-bar-wrap">
                          <div className="score-bar"><div className="score-bar-fill" style={{width:`${sp.score*100}%`}} /></div>
                          <div className="score-num">{sp.score.toFixed(2)}</div>
                        </div>
                      </td>
                      <td>
                        <span className={`action-chip ${sp.action === 'pay_now' ? 'chip-pay' : sp.action === 'partial' ? 'chip-part' : 'chip-delay'}`}>
                          {sp.action.replace('_',' ')}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Recovery strategies */}
            <div className="card">
              <div className="card-title">Recovery Strategies</div>
              {result.recovery_strategies.length > 0 ? (
                <div className="rec-list">
                  {result.recovery_strategies.map((rs, i) => (
                    <div key={i} className="rec-item">
                      <div className="rec-icon">{
                        rs.type === 'early_collection' ? '📥' :
                        rs.type === 'delay_flexible'   ? '⏳' :
                        rs.type === 'cut_overheads'    ? '✂️' : '📦'
                      }</div>
                      <div>
                        <div style={{fontWeight:500,marginBottom:4}}>{rs.description}</div>
                        <div className="mono text-accent">+{fmtINR(rs.estimated_impact)} estimated recovery</div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="empty-state" style={{padding:'24px'}}>
                  <div className="empty-state-icon">✅</div>
                  <div className="empty-state-text">No recovery needed – cash flow is healthy.</div>
                </div>
              )}
            </div>
          </div>

          {/* Overhead & Inventory Actions */}
          <div className="grid-2">
            <div className="card">
              <div className="card-title">Overhead Actions</div>
              {result.overhead_actions.map((a, i) => (
                <div key={i} style={{padding:'8px 0', borderBottom:'1px solid #1e2330', fontSize:13, lineHeight:1.5}}>
                  {a}
                </div>
              ))}
            </div>
            <div className="card">
              <div className="card-title">Inventory Actions</div>
              {result.inventory_actions.map((a, i) => (
                <div key={i} style={{padding:'8px 0', borderBottom:'1px solid #1e2330', fontSize:13, lineHeight:1.5}}>
                  {a}
                </div>
              ))}
            </div>
          </div>

          {/* Explanation */}
          <div className="card">
            <div className="card-title">Chain-of-Thought Explanation</div>
            <div className="explanation-box">{result.explanation}</div>
          </div>

          {/* Daily Cash Flow Table */}
          <div className="card mt24">
            <div className="card-title">Daily Cash Flow Detail</div>
            <table className="data-table">
              <thead>
                <tr>
                  <th>Date</th>
                  <th>Opening</th>
                  <th>Inflows</th>
                  <th>Outflows</th>
                  <th>Closing</th>
                  <th>Events</th>
                </tr>
              </thead>
              <tbody>
                {result.cash_flow_projection.map((d, i) => (
                  <tr key={i}>
                    <td className="mono">{d.date}</td>
                    <td className="mono">{fmtINR(d.opening_cash)}</td>
                    <td className="mono text-accent">{d.inflows > 0 ? `+${fmtINR(d.inflows)}` : '—'}</td>
                    <td className="mono text-danger">{d.outflows > 0 ? `-${fmtINR(d.outflows)}` : '—'}</td>
                    <td className={`mono ${d.closing_cash < 0 ? 'text-danger' : 'text-accent'}`} style={{fontWeight:600}}>
                      {fmtINR(d.closing_cash)}
                    </td>
                    <td style={{fontSize:11,color:'#7a8090'}}>{d.events.join(' · ') || '—'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}
    </div>
  );
}
