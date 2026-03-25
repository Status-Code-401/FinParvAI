import { useEffect, useState } from 'react';
import { getDashboard, getCashFlow, getForecast } from '../services/api';
import {
  AlertTriangle, TrendingUp, TrendingDown, Shield,
  Clock, DollarSign, ArrowUpRight, ArrowDownRight, Activity, Cpu, Sparkles, Target
} from 'lucide-react';
import {
  AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid
} from 'recharts';

function useData<T>(fn: () => Promise<T>) {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fn().then(setData).catch(e => setError(e.message)).finally(() => setLoading(false));
  }, []);

  return { data, loading, error };
}

const fmt = (n: number) => `₹${n?.toLocaleString('en-IN') ?? 0}`;
const fmtK = (n: number) => n >= 100000 ? `₹${(n / 100000).toFixed(1)}L` : n >= 1000 ? `₹${(n / 1000).toFixed(1)}K` : `₹${n}`;

// Lightweight custom markdown renderer to format explanations beautifully
const renderExplanation = (text: string) => {
  return text.split('\n').map((line, i) => {
    // Header 3
    if (line.startsWith('### ')) return <h3 key={i} style={{ marginTop: 24, marginBottom: 12, fontSize: 14, color: 'var(--accent)', display: 'flex', alignItems: 'center', gap: 6 }}><Target size={14}/> {line.replace('### ', '')}</h3>;
    // Header 2
    if (line.startsWith('## ')) return <h2 key={i} style={{ marginTop: 16, marginBottom: 8, fontSize: 16, fontWeight: 800 }}>{line.replace('## ', '')}</h2>;
    
    // List item with strong extraction
    if (line.startsWith('- ')) {
      const parts = line.split('**');
      const bolded = parts.map((part, j) => j % 2 === 1 ? <strong key={j} style={{ color: 'var(--text-main)' }}>{part}</strong> : part);
      return (
        <div key={i} style={{ marginLeft: 16, marginBottom: 8, display: 'flex', alignItems: 'flex-start', gap: 8, fontSize: 13, lineHeight: 1.5, color: 'var(--text-muted)' }}>
          <span style={{ color: 'var(--accent)' }}>•</span>
          <span>{bolded}</span>
        </div>
      );
    }
    
    // Empty line spacer
    if (!line.trim()) return <div key={i} style={{ height: 12 }} />;
    
    // Standard paragraph with strong extraction
    const parts = line.split('**');
    const bolded = parts.map((part, j) => j % 2 === 1 ? <strong key={j} style={{ color: 'var(--text-main)' }}>{part}</strong> : part);
    return <div key={i} style={{ marginBottom: 6, fontSize: 13.5, lineHeight: 1.6 }}>{bolded}</div>;
  });
};

const RiskBadge = ({ level }: { level: string }) => {
  const map: any = {
    low: ['badge-success', '✅ Safe'],
    medium: ['badge-info', '⚡ Medium'],
    high: ['badge-warning', '⚠️ High'],
    critical: ['badge-danger', '🔴 Critical']
  };
  const [cls, label] = map[level] || ['badge-info', level];
  return <span className={`badge ${cls}`}>{label}</span>;
};

export default function Dashboard() {
  const { data: dash, loading: dl } = useData(getDashboard);
  const { data: cf } = useData(() => getCashFlow(14));
  const { data: forecastData } = useData(getForecast);

  if (dl) return <div className="loading-center"><div className="spinner" /><span>Analyzing finances…</span></div>;
  if (!dash) return null;

  const chartData = cf?.projection?.slice(0, 14).map((d: any) => ({
    date: d.date.slice(5),
    cash: d.cash,
    inflows: d.inflows,
    outflows: d.outflows
  })) || [];

  const netPos = dash.net_position;
  const prodPct = dash.production_target > 0
    ? Math.min(100, Math.round((dash.production_units_month / dash.production_target) * 100))
    : 0;

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">Financial Dashboard</h1>
        <p className="page-subtitle">Real-time cash intelligence for {dash.business_name}</p>
      </div>

      {/* Alert banner */}
      {!dash.is_safe && (
        <div className="alert alert-danger" style={{ marginBottom: 20 }}>
          <AlertTriangle size={18} />
          <div>
            <strong>Cash Shortfall Alert:</strong> Cash turns negative on Day {dash.days_to_zero} ({dash.first_negative_date}).
            Immediate action required.
          </div>
        </div>
      )}
      {dash.shortfall_detected && dash.is_safe && (
        <div className="alert alert-warning" style={{ marginBottom: 20 }}>
          <AlertTriangle size={18} />
          <strong>Potential shortfall detected.</strong>&nbsp;Obligations may exceed available liquidity. Review recommendations.
        </div>
      )}

      {/* KPI Row */}
      <div className="kpi-grid">
        <div className="card" style={{ borderTop: '2px solid var(--accent)' }}>
          <div className="card-header">
            <span className="card-title">Cash Balance</span>
            <Activity size={16} color="var(--accent)" />
          </div>
          <div className="card-value">{fmtK(dash.cash_balance)}</div>
          <div className="card-sub">Current liquidity</div>
        </div>

        <div className="card" style={{ borderTop: `2px solid ${dash.is_safe ? 'var(--success)' : 'var(--danger)'}` }}>
          <div className="card-header">
            <span className="card-title">Days to Zero</span>
            <Clock size={16} color={dash.is_safe ? 'var(--success)' : 'var(--danger)'} />
          </div>
          <div className="card-value" style={{ color: dash.is_safe ? 'var(--success)' : 'var(--danger)' }}>
            {dash.is_safe ? '30+' : dash.days_to_zero}
          </div>
          <div className="card-sub">{dash.is_safe ? 'No shortfall in 30 days' : `Negative on ${dash.first_negative_date}`}</div>
        </div>

        <div className="card" style={{ borderTop: '2px solid var(--danger)' }}>
          <div className="card-header">
            <span className="card-title">Total Obligations</span>
            <ArrowDownRight size={16} color="var(--danger)" />
          </div>
          <div className="card-value">{fmtK(dash.total_payables)}</div>
          <div className="card-sub">{dash.critical_payables} critical · {dash.payables_count} total payables</div>
        </div>

        <div className="card" style={{ borderTop: '2px solid var(--success)' }}>
          <div className="card-header">
            <span className="card-title">Expected Receivables</span>
            <ArrowUpRight size={16} color="var(--success)" />
          </div>
          <div className="card-value">{fmtK(dash.total_receivables_expected)}</div>
          <div className="card-sub">{dash.overdue_receivables} overdue · {dash.receivables_count} total</div>
        </div>

        <div className="card">
          <div className="card-header">
            <span className="card-title">Net Position</span>
            {netPos >= 0 ? <TrendingUp size={16} color="var(--success)" /> : <TrendingDown size={16} color="var(--danger)" />}
          </div>
          <div className="card-value" style={{ color: netPos >= 0 ? 'var(--success)' : 'var(--danger)' }}>
            {fmtK(Math.abs(netPos))}
          </div>
          <div className="card-sub">{netPos >= 0 ? 'Surplus' : 'Deficit'} after obligations</div>
        </div>

        <div className="card">
          <div className="card-header">
            <span className="card-title">Risk Level</span>
            <Shield size={16} color="var(--warning)" />
          </div>
          <div style={{ marginTop: 8 }}><RiskBadge level={dash.risk_level} /></div>
          <div className="card-sub" style={{ marginTop: 8 }}>
            Monthly: {fmtK(dash.monthly_income)} in · {fmtK(dash.monthly_expense)} out
          </div>
        </div>
      </div>
      {/* Cash Flow Mini Chart */}
      <div className="card section-gap">
        <div className="card-header">
          <span style={{ fontWeight: 700, fontSize: 15 }}>14-Day Cash Projection</span>
          <span className="badge badge-info">Live</span>
        </div>
        <ResponsiveContainer width="100%" height={200}>
          <AreaChart data={chartData}>
            <defs>
              <linearGradient id="cashGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="var(--accent)" stopOpacity={0.3} />
                <stop offset="95%" stopColor="var(--accent)" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
            <XAxis dataKey="date" tick={{ fill: 'var(--text-muted)', fontSize: 11 }} />
            <YAxis tick={{ fill: 'var(--text-muted)', fontSize: 11 }} tickFormatter={v => `₹${(v/1000).toFixed(0)}K`} />
            <Tooltip
              contentStyle={{ background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 8 }}
              formatter={(v: any) => [fmt(v), '']}
            />
            <Area type="monotone" dataKey="cash" stroke="var(--accent)" fill="url(#cashGrad)" strokeWidth={2} />
          </AreaChart>
        </ResponsiveContainer>
      </div>
      {/* Discriminative Model & Recommended Covenants */}
      <div className="card section-gap" style={{ borderLeft: '4px solid var(--accent)' }}>
        <div className="card-header" style={{ marginBottom: 16 }}>
          <span style={{ fontWeight: 800, fontSize: 16, display: 'flex', alignItems: 'center', gap: 8, color: 'var(--text-main)' }}>
            <Shield size={20} color="var(--accent)" /> Discriminative Strategy & Active Covenants
          </span>
        </div>
        <div style={{ background: 'var(--bg-body)', padding: '20px', borderRadius: 8, border: '1px solid var(--border)' }}>
          {dash.explanation ? renderExplanation(dash.explanation) : <span className="text-muted">No deterministic constraints identified.</span>}
        </div>
      </div>

      {/* AI Intelligence & Explainability Panel */}
      {forecastData && (
        <div className="card section-gap" style={{ border: '1px solid var(--accent)' }}>
          <div className="card-header" style={{ marginBottom: 16 }}>
            <span style={{ fontWeight: 800, fontSize: 16, display: 'flex', alignItems: 'center', gap: 8, color: 'var(--accent)' }}>
              <Cpu size={20} /> AI Agent Observability (Chain of Thought & SHAP)
            </span>
          </div>
          
          <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
            {/* Chain of Thought Block */}
            <div style={{ background: 'var(--bg-body)', padding: 16, borderRadius: 8, borderLeft: '4px solid var(--purple)' }}>
              <div style={{ fontWeight: 700, fontSize: 13, marginBottom: 8, color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: 6 }}>
                <Sparkles size={14} color="var(--purple)" /> LangChain Context Agent Reasoning
              </div>
              <div style={{ fontSize: 13.5, fontStyle: 'italic', lineHeight: 1.5 }}>
                "{forecastData.key_insights[forecastData.key_insights.length - 1]}"
              </div>
            </div>

            {/* SHAP Explainability Block */}
            <div className="grid-2" style={{ gap: 16 }}>
              <div style={{ background: 'var(--bg-body)', padding: 16, borderRadius: 8, borderLeft: '4px solid var(--cyan)' }}>
                <div style={{ fontWeight: 700, fontSize: 13, marginBottom: 8, color: 'var(--text-muted)' }}>
                  SARIMAX Revenue SHAP Explainability
                </div>
                <div style={{ fontSize: 13, lineHeight: 1.5 }}>
                  {forecastData.revenue_forecast?.explanation || "Base trend unchanged."}
                </div>
              </div>

              <div style={{ background: 'var(--bg-body)', padding: 16, borderRadius: 8, borderLeft: '4px solid var(--warning)' }}>
                <div style={{ fontWeight: 700, fontSize: 13, marginBottom: 8, color: 'var(--text-muted)' }}>
                  LSTM Demand SHAP Explainability
                </div>
                <div style={{ fontSize: 13, lineHeight: 1.5 }}>
                  {forecastData.demand_forecast?.explanation || "Base trend unchanged."}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Bottom row */}
      <div className="grid-2 section-gap">
        {/* Production */}
        <div className="card">
          <div style={{ fontWeight: 700, fontSize: 15, marginBottom: 16 }}>Production This Month</div>
          <div className="countdown-wrap" style={{ marginBottom: 16 }}>
            <span className="countdown-number" style={{ color: 'var(--cyan)', fontSize: 36 }}>
              {dash.production_units_month?.toLocaleString()}
            </span>
            <span className="countdown-label">units produced</span>
          </div>
          <div style={{ marginBottom: 8, fontSize: 12, color: 'var(--text-muted)' }}>
            Target: {dash.production_target?.toLocaleString()} units · {prodPct}% achieved
          </div>
          <div className="progress-bar">
            <div className="progress-fill" style={{
              width: `${prodPct}%`,
              background: prodPct >= 80 ? 'var(--success)' : prodPct >= 50 ? 'var(--warning)' : 'var(--danger)'
            }} />
          </div>
        </div>

        {/* Financial Health */}
        <div className="card">
          <div style={{ fontWeight: 700, fontSize: 15, marginBottom: 16 }}>Financial Health</div>
          <div className="stat-row">
            <span className="stat-key">Monthly Income Avg</span>
            <span className="stat-val" style={{ color: 'var(--success)' }}>{fmtK(dash.monthly_income)}</span>
          </div>
          <div className="stat-row">
            <span className="stat-key">Monthly Expense Avg</span>
            <span className="stat-val" style={{ color: 'var(--danger)' }}>{fmtK(dash.monthly_expense)}</span>
          </div>
          <div className="stat-row">
            <span className="stat-key">Avg Payment Cycle</span>
            <span className="stat-val">{dash.avg_payment_cycle} days</span>
          </div>
          <div className="stat-row">
            <span className="stat-key">Overdue Receivables</span>
            <span className="stat-val" style={{ color: dash.overdue_receivables > 0 ? 'var(--danger)' : 'var(--success)' }}>
              {dash.overdue_receivables}
            </span>
          </div>
          <div className="stat-row">
            <span className="stat-key">Critical Payables</span>
            <span className="stat-val" style={{ color: 'var(--warning)' }}>{dash.critical_payables}</span>
          </div>
        </div>
      </div>
    </div>
  );
}
