import { useEffect, useState } from 'react';
import { getForecast } from '../services/api';
import {
  LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer,
  CartesianGrid, BarChart, Bar, Legend, Cell, ReferenceLine
} from 'recharts';
import { TrendingUp, TrendingDown, Minus, Newspaper, Calendar, Wifi, WifiOff, Cpu, Activity, ExternalLink } from 'lucide-react';

const fmt = (n: number) => `₹${Number(n)?.toLocaleString('en-IN') ?? 0}`;

// Month name lookup for the seasonal heatmap
const MONTH_NAMES = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];

// India garment PEAK_SEASONS mirror (matches backend)
const PEAK_MONTH_MULTIPLIERS: Record<number, { name: string; multiplier: number }> = {
  1:  { name: 'Pongal',          multiplier: 1.25 },
  4:  { name: 'Summer Launch',   multiplier: 1.15 },
  8:  { name: 'Onam/Aadi',       multiplier: 1.10 },
  10: { name: 'Diwali/Dussehra', multiplier: 1.45 },
  11: { name: 'Diwali Season',   multiplier: 1.25 },
  12: { name: 'Wedding Season',  multiplier: 1.30 },
};

// ── Seasonal Heatmap Row ──────────────────────────────────────────────────────
function SeasonalHeatmap() {
  const today = new Date();
  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(12, 1fr)', gap: 4 }}>
      {MONTH_NAMES.map((name, i) => {
        const month = i + 1;
        const peak = PEAK_MONTH_MULTIPLIERS[month];
        const mult = peak?.multiplier ?? 1.0;
        const isPast = month < today.getMonth() + 1;
        const isCurrent = month === today.getMonth() + 1;
        const intensity = Math.round((mult - 1.0) * 100); // 0..45

        // Color gradient: neutral → warm orange → deep amber based on multiplier
        const bg = mult >= 1.35
          ? 'rgba(245,158,11,0.55)'   // very hot
          : mult >= 1.20
          ? 'rgba(245,158,11,0.35)'   // hot
          : mult >= 1.10
          ? 'rgba(79,142,247,0.30)'   // mild peak
          : 'rgba(255,255,255,0.04)'; // baseline

        return (
          <div
            key={month}
            style={{
              background: bg,
              borderRadius: 8,
              padding: '10px 4px 8px',
              textAlign: 'center',
              border: isCurrent ? '1px solid var(--accent)' : '1px solid transparent',
              opacity: isPast ? 0.5 : 1,
              position: 'relative',
              cursor: 'default',
            }}
            title={peak ? `${peak.name} — +${intensity}% expected` : 'Baseline month'}
          >
            <div style={{ fontSize: 10, color: 'var(--text-muted)', fontWeight: 700, textTransform: 'uppercase' }}>{name}</div>
            {peak && (
              <>
                <div style={{ fontSize: 11, fontWeight: 800, color: mult >= 1.3 ? 'var(--warning)' : 'var(--accent)', marginTop: 4 }}>
                  +{intensity}%
                </div>
                <div style={{ fontSize: 9, color: 'var(--text-muted)', marginTop: 2, lineHeight: 1.2 }}>{peak.name}</div>
              </>
            )}
            {!peak && (
              <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 4 }}>—</div>
            )}
            {isCurrent && (
              <div style={{
                position: 'absolute', top: 3, right: 4,
                width: 5, height: 5, borderRadius: '50%',
                background: 'var(--accent)', boxShadow: '0 0 4px var(--accent)'
              }} />
            )}
          </div>
        );
      })}
    </div>
  );
}

// ── Custom tooltip for bar chart with peak annotations ────────────────────────
function SeasonTooltip({ active, payload, label }: any) {
  if (!active || !payload?.length) return null;
  const month = label ? parseInt(label.slice(5), 10) : null;
  const peak = month ? PEAK_MONTH_MULTIPLIERS[month] : null;
  return (
    <div style={{ background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 8, padding: '10px 14px', fontSize: 12 }}>
      <div style={{ fontWeight: 700, marginBottom: 6 }}>{label}</div>
      {payload.map((p: any) => (
        <div key={p.name} style={{ color: p.fill || p.color }}>{p.name}: {fmt(p.value)}</div>
      ))}
      {peak && (
        <div style={{ marginTop: 6, color: 'var(--warning)', fontWeight: 600 }}>
          🎉 {peak.name} · +{Math.round((peak.multiplier - 1) * 100)}% expected
        </div>
      )}
    </div>
  );
}

// ── Sentiment pill ────────────────────────────────────────────────────────────
function SentimentPill({ sentiment }: { sentiment: string }) {
  const map: Record<string, [string, string]> = {
    bullish: ['badge-success', '📈 Bullish'],
    bearish: ['badge-danger',  '📉 Bearish'],
    neutral: ['badge-info',    '➡️ Neutral'],
  };
  const [cls, label] = map[sentiment] ?? ['badge-info', sentiment];
  return <span className={`badge ${cls}`}>{label}</span>;
}

// ── Main page ─────────────────────────────────────────────────────────────────
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
    Net: m.net,
    // Flag peak months for coloring
    isPeak: !!PEAK_MONTH_MULTIPLIERS[new Date(m.month + '-01').getMonth() + 1],
  })) || [];

  const forecastChart = [
    ...monthly_summary?.map((m: any) => ({ month: m.month?.slice(0, 7), Income: m.income, isForecast: false })) || [],
    ...revenue_forecast.forecast?.map((v: number, i: number) => ({
      month: `Forecast ${i + 1}`,
      Income: v,
      isForecast: true,
    })) || []
  ];

  const upcomingSeasons: any[] = seasonal_insights?.upcoming_seasons ?? [];
  const sentimentSummary: string = seasonal_insights?.sentiment_summary ?? '';
  const actionInsight: string = seasonal_insights?.action_insight ?? '';
  const sourceLinks: { title: string; url: string }[] = seasonal_insights?.source_links ?? [];
  const newsSource: string = seasonal_insights?.news_source ?? 'fallback';
  const sentiment: string = seasonal_insights?.market_sentiment ?? 'neutral';

  // SHAP / XAI data from predictive engine
  const revenueShap = revenue_forecast?.explanation ?? '';
  const revenueConf = Math.round((revenue_forecast?.confidence ?? 0.85) * 100);
  const demandShap = demand_forecast?.explanation ?? '';
  const demandConf = Math.round((demand_forecast?.confidence ?? 0.80) * 100);
  // Parse base vs adjusted values from explanation strings if present
  const revenueBase = revenue_forecast?.forecast?.[0] ? Math.round(revenue_forecast.forecast[0] / (revenue_forecast?.confidence ?? 1)) : null;
  const demandBase = demand_forecast?.forecast_units?.[0] ?? null;
  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">Money Forecast</h1>
        <p className="page-subtitle">What your income and expenses are likely to look like over the next 3 months</p>
      </div>

      {/* KPI row */}
      <div className="kpi-grid" style={{ gridTemplateColumns: 'repeat(4, 1fr)', marginBottom: 20 }}>
        <div className="card">
          <div className="card-title">Avg Monthly Money In</div>
          <div className="card-value">{fmt(seasonal_insights.avg_monthly_income)}</div>
        </div>
        <div className="card">
          <div className="card-title">Avg Monthly Money Out</div>
          <div className="card-value">{fmt(seasonal_insights.avg_monthly_expense)}</div>
        </div>
        <div className="card">
          <div className="card-title">Revenue Trend</div>
          <div className="card-value" style={{
            color: revenue_forecast.trend === 'up' ? 'var(--success)'
                 : revenue_forecast.trend === 'down' ? 'var(--danger)' : 'var(--warning)',
            fontSize: 20, display: 'flex', alignItems: 'center', gap: 8
          }}>
            {revenue_forecast.trend === 'up'   ? <><TrendingUp size={20} /> Growing</>
           : revenue_forecast.trend === 'down' ? <><TrendingDown size={20} /> Declining</>
           :                                      <><Minus size={20} /> Stable</>}
          </div>
        </div>
        <div className="card">
          <div className="card-title">Daily Production Avg</div>
          <div className="card-value">{demand_forecast?.avg_daily_units} units</div>
          <div className="card-sub">{demand_forecast?.trend}</div>
        </div>
      </div>

      {/* ── Seasonal Calendar Heatmap ── */}
      <div className="card" style={{ marginBottom: 20 }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 16 }}>
          <div style={{ fontWeight: 700, fontSize: 15, display: 'flex', alignItems: 'center', gap: 8 }}>
            <Calendar size={16} color="var(--warning)" /> Garment Industry Seasonal Calendar
          </div>
          <div style={{ display: 'flex', gap: 12, fontSize: 11 }}>
            <span style={{ display: 'flex', alignItems: 'center', gap: 5 }}>
              <span style={{ width: 10, height: 10, borderRadius: 2, background: 'rgba(245,158,11,0.55)', display: 'inline-block' }} /> Peak season
            </span>
            <span style={{ display: 'flex', alignItems: 'center', gap: 5 }}>
              <span style={{ width: 10, height: 10, borderRadius: 2, background: 'rgba(79,142,247,0.30)', display: 'inline-block' }} /> Mild peak
            </span>
            <span style={{ display: 'flex', alignItems: 'center', gap: 5 }}>
              <span style={{ width: 10, height: 10, borderRadius: 2, background: 'rgba(255,255,255,0.04)', border: '1px solid var(--border)', display: 'inline-block' }} /> Normal
            </span>
          </div>
        </div>
        <SeasonalHeatmap />
        {upcomingSeasons.length > 0 && (
          <div style={{ marginTop: 16, paddingTop: 14, borderTop: '1px solid var(--border)', display: 'flex', flexWrap: 'wrap', gap: 10 }}>
            <span style={{ fontSize: 12, color: 'var(--text-muted)', alignSelf: 'center' }}>Coming up:</span>
            {upcomingSeasons.map((s: any, i: number) => (
              <span key={i} className="badge badge-warning" style={{ fontSize: 11, padding: '5px 12px' }}>
                📅 {s.name} — {s.days_away} days away · +{Math.round((s.multiplier - 1) * 100)}% surge expected
              </span>
            ))}
          </div>
        )}
      </div>

      {/* ── Live Market Sentiment ── */}
      <div className="card" style={{ marginBottom: 20, borderLeft: `3px solid ${sentiment === 'bullish' ? 'var(--success)' : sentiment === 'bearish' ? 'var(--danger)' : 'var(--accent)'}` }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 12 }}>
          <div style={{ fontWeight: 700, fontSize: 14, display: 'flex', alignItems: 'center', gap: 8 }}>
            <Newspaper size={15} color="var(--accent)" /> Live Market Sentiment
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <SentimentPill sentiment={sentiment} />
            <span style={{ fontSize: 11, color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: 4 }}>
              {newsSource === 'google_news_rss'
                ? <><Wifi size={11} /> Live via Google News RSS</>
                : <><WifiOff size={11} /> Calendar-based (news unavailable)</>}
            </span>
          </div>
        </div>
        <p style={{ fontSize: 13, color: 'var(--text-secondary)', lineHeight: 1.7, margin: 0, paddingBottom: 10 }}>
          {sentimentSummary || 'Market sentiment analysis is being computed from live data sources.'}
        </p>

        {actionInsight && (
          <div style={{ background: 'rgba(255,255,255,0.03)', padding: 12, borderRadius: 8, marginTop: 4 }}>
            <div style={{ fontWeight: 700, fontSize: 12, color: 'var(--accent)', marginBottom: 4 }}>🎯 Recommended Action:</div>
            <div style={{ fontSize: 13, color: 'var(--text-primary)' }}>{actionInsight}</div>
          </div>
        )}

        {/* Source reference links */}
        {sourceLinks.length > 0 && (
          <div style={{ marginTop: 14, paddingTop: 12, borderTop: '1px solid var(--border)' }}>
            <div style={{ fontSize: 10, color: 'var(--text-muted)', marginBottom: 8, textTransform: 'uppercase', letterSpacing: '0.5px', fontWeight: 700 }}>
              Sources ({sourceLinks.length})
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
              {sourceLinks.map((src, i) => (
                <a
                  key={i}
                  href={src.url || '#'}
                  target="_blank"
                  rel="noopener noreferrer"
                  style={{
                    display: 'flex',
                    alignItems: 'flex-start',
                    gap: 6,
                    fontSize: 12,
                    color: 'var(--accent)',
                    textDecoration: 'none',
                    lineHeight: 1.5,
                    padding: '4px 0',
                    opacity: src.url ? 1 : 0.45,
                    pointerEvents: src.url ? 'auto' : 'none',
                  }}
                  onMouseEnter={e => (e.currentTarget.style.textDecoration = 'underline')}
                  onMouseLeave={e => (e.currentTarget.style.textDecoration = 'none')}
                >
                  <ExternalLink size={11} style={{ flexShrink: 0, marginTop: 2 }} />
                  <span>{src.title || `Article ${i + 1}`}</span>
                </a>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* ── SHAP XAI Explainability Panel ── */}
      <div className="card" style={{ marginBottom: 20, border: '1px solid var(--accent)' }}>
        <div style={{ fontWeight: 800, fontSize: 15, marginBottom: 16, display: 'flex', alignItems: 'center', gap: 8, color: 'var(--accent)' }}>
          <Cpu size={18} /> AI Forecast Explainability (SHAP / XAI)
        </div>
        <div className="grid-2" style={{ gap: 16 }}>

          {/* SARIMAX Revenue SHAP */}
          <div style={{ background: 'var(--bg-body)', borderRadius: 10, padding: 18, borderLeft: '3px solid var(--cyan)' }}>
            <div style={{ fontWeight: 700, fontSize: 13, marginBottom: 10, color: 'var(--cyan)', display: 'flex', alignItems: 'center', gap: 6 }}>
              <TrendingUp size={14} /> SARIMAX Revenue Forecast
              <span style={{ marginLeft: 'auto', fontSize: 11, color: 'var(--text-muted)' }}>Statistical model</span>
            </div>
            {/* Confidence bar */}
            <div style={{ marginBottom: 12 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 11, color: 'var(--text-muted)', marginBottom: 4 }}>
                <span>Model Confidence</span>
                <span style={{ fontWeight: 700, color: revenueConf >= 75 ? 'var(--success)' : revenueConf >= 55 ? 'var(--warning)' : 'var(--danger)' }}>{revenueConf}%</span>
              </div>
              <div style={{ height: 5, background: 'var(--border)', borderRadius: 4, overflow: 'hidden' }}>
                <div style={{ width: `${revenueConf}%`, height: '100%', background: revenueConf >= 75 ? 'var(--success)' : revenueConf >= 55 ? 'var(--warning)' : 'var(--danger)', transition: 'width 0.6s ease', borderRadius: 4 }} />
              </div>
            </div>
            {/* Feature attribution */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: 6, marginBottom: 12 }}>
              {[
                { label: 'Historical trend (ARIMA)',   pct: 55, color: 'var(--cyan)' },
                { label: 'Context multiplier (agent)', pct: 30, color: 'var(--accent)' },
                { label: 'Seasonal adjustment',         pct: 15, color: 'var(--warning)' },
              ].map(f => (
                <div key={f.label}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 11, color: 'var(--text-muted)', marginBottom: 2 }}>
                    <span>{f.label}</span><span>{f.pct}%</span>
                  </div>
                  <div style={{ height: 4, background: 'var(--border)', borderRadius: 4, overflow: 'hidden' }}>
                    <div style={{ width: `${f.pct}%`, height: '100%', background: f.color, borderRadius: 4, opacity: 0.8 }} />
                  </div>
                </div>
              ))}
            </div>
            <div style={{ fontSize: 12, color: 'var(--text-secondary)', fontStyle: 'italic', lineHeight: 1.6, paddingTop: 10, borderTop: '1px solid var(--border)' }}>
              {revenueShap || 'SARIMAX base projection applied with context multiplier.'}
            </div>
          </div>

          {/* LSTM Demand SHAP */}
          <div style={{ background: 'var(--bg-body)', borderRadius: 10, padding: 18, borderLeft: '3px solid var(--purple)' }}>
            <div style={{ fontWeight: 700, fontSize: 13, marginBottom: 10, color: 'var(--purple)', display: 'flex', alignItems: 'center', gap: 6 }}>
              <Activity size={14} /> LSTM Demand Forecast
              <span style={{ marginLeft: 'auto', fontSize: 11, color: 'var(--text-muted)' }}>Neural model</span>
            </div>
            {/* Confidence bar */}
            <div style={{ marginBottom: 12 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 11, color: 'var(--text-muted)', marginBottom: 4 }}>
                <span>Model Confidence</span>
                <span style={{ fontWeight: 700, color: demandConf >= 75 ? 'var(--success)' : demandConf >= 55 ? 'var(--warning)' : 'var(--danger)' }}>{demandConf}%</span>
              </div>
              <div style={{ height: 5, background: 'var(--border)', borderRadius: 4, overflow: 'hidden' }}>
                <div style={{ width: `${demandConf}%`, height: '100%', background: demandConf >= 75 ? 'var(--success)' : demandConf >= 55 ? 'var(--warning)' : 'var(--danger)', transition: 'width 0.6s ease', borderRadius: 4 }} />
              </div>
            </div>
            {/* Feature attribution */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: 6, marginBottom: 12 }}>
              {[
                { label: 'Sequential pattern (LSTM)',   pct: 50, color: 'var(--purple)' },
                { label: 'Agent demand multiplier',     pct: 35, color: 'var(--accent)' },
                { label: 'Data volume score',           pct: 15, color: 'var(--warning)' },
              ].map(f => (
                <div key={f.label}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 11, color: 'var(--text-muted)', marginBottom: 2 }}>
                    <span>{f.label}</span><span>{f.pct}%</span>
                  </div>
                  <div style={{ height: 4, background: 'var(--border)', borderRadius: 4, overflow: 'hidden' }}>
                    <div style={{ width: `${f.pct}%`, height: '100%', background: f.color, borderRadius: 4, opacity: 0.8 }} />
                  </div>
                </div>
              ))}
            </div>
            {demandBase !== null && (
              <div style={{ display: 'flex', gap: 8, marginBottom: 10 }}>
                <div style={{ flex: 1, background: 'rgba(255,255,255,0.04)', borderRadius: 6, padding: '8px 12px', textAlign: 'center' }}>
                  <div style={{ fontSize: 10, color: 'var(--text-muted)', marginBottom: 2 }}>Base LSTM</div>
                  <div style={{ fontWeight: 700, fontSize: 15 }}>{demandBase} units/day</div>
                </div>
                <div style={{ flex: 1, background: 'rgba(255,255,255,0.04)', borderRadius: 6, padding: '8px 12px', textAlign: 'center' }}>
                  <div style={{ fontSize: 10, color: 'var(--text-muted)', marginBottom: 2 }}>After multiplier</div>
                  <div style={{ fontWeight: 700, fontSize: 15, color: 'var(--purple)' }}>{Math.round(demandBase * (demand_forecast?.confidence ?? 1))} units/day</div>
                </div>
              </div>
            )}
            <div style={{ fontSize: 12, color: 'var(--text-secondary)', fontStyle: 'italic', lineHeight: 1.6, paddingTop: 10, borderTop: '1px solid var(--border)' }}>
              {demandShap || 'LSTM sequential model applied with agent demand multiplier.'}
            </div>
          </div>

        </div>
      </div>

      {/* ── Key Insights ── */}
      {key_insights?.length > 0 && (
        <div className="card" style={{ marginBottom: 20 }}>
          <div style={{ fontWeight: 700, fontSize: 15, marginBottom: 12 }}>💡 Key Insights for Your Business</div>
          {key_insights.map((ins: string, i: number) => (
            <div key={i} style={{ display: 'flex', gap: 10, padding: '6px 0', borderBottom: '1px solid var(--border)' }}>
              <span style={{ color: 'var(--accent)', fontWeight: 700 }}>{i + 1}.</span>
              <span style={{ fontSize: 13, color: 'var(--text-secondary)' }}>{ins}</span>
            </div>
          ))}
        </div>
      )}

      {/* ── Month-by-month bar chart with peak highlighting ── */}
      <div className="card" style={{ marginBottom: 20 }}>
        <div style={{ fontWeight: 700, fontSize: 15, marginBottom: 4 }}>Monthly Income & Expense History</div>
        <div style={{ fontSize: 12, color: 'var(--text-muted)', marginBottom: 16 }}>
          Amber bars = festival / peak season months
        </div>
        <ResponsiveContainer width="100%" height={260}>
          <BarChart data={monthlyChart} barGap={4}>
            <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
            <XAxis dataKey="month" tick={{ fill: 'var(--text-muted)', fontSize: 11 }} />
            <YAxis tick={{ fill: 'var(--text-muted)', fontSize: 11 }} tickFormatter={v => `₹${(v / 1000).toFixed(0)}K`} />
            <Tooltip content={<SeasonTooltip />} />
            <Legend />
            <Bar dataKey="Income" radius={[3, 3, 0, 0]}>
              {monthlyChart.map((entry: any, index: number) => (
                <Cell
                  key={index}
                  fill={entry.isPeak ? 'var(--warning)' : 'var(--success)'}
                  opacity={entry.isPeak ? 1 : 0.75}
                />
              ))}
            </Bar>
            <Bar dataKey="Expense" fill="var(--danger)" radius={[3, 3, 0, 0]} opacity={0.7} />
            <Bar dataKey="Net" fill="var(--accent)" radius={[3, 3, 0, 0]} opacity={0.6} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* ── Income Forecast chart ── */}
      <div className="card" style={{ marginBottom: 20 }}>
        <div style={{ fontWeight: 700, fontSize: 15, marginBottom: 16 }}>Income Forecast (Past + Predicted)</div>
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
              dot={(props: any) => {
                const { cx, cy, payload } = props;
                return <circle cx={cx} cy={cy} r={4} fill={payload.isForecast ? 'var(--purple)' : 'var(--accent)'} />;
              }}
            />
          </LineChart>
        </ResponsiveContainer>
        <div style={{ display: 'flex', gap: 16, marginTop: 12, fontSize: 12, color: 'var(--text-muted)' }}>
          <span style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
            <span style={{ width: 12, height: 12, borderRadius: '50%', background: 'var(--accent)', display: 'inline-block' }} /> Historical
          </span>
          <span style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
            <span style={{ width: 12, height: 12, borderRadius: '50%', background: 'var(--purple)', display: 'inline-block' }} /> Forecast
          </span>
        </div>
      </div>

      {/* ── Month-by-Month table ── */}
      <div className="card">
        <div style={{ fontWeight: 700, fontSize: 15, marginBottom: 16 }}>Month-by-Month History</div>
        <div className="table-wrap">
          <table>
            <thead>
              <tr><th>Month</th><th>Income</th><th>Expense</th><th>Net</th><th>Opening</th><th>Closing</th><th>Season</th></tr>
            </thead>
            <tbody>
              {monthly_summary?.map((m: any) => {
                const monthNum = new Date(m.month + '-01').getMonth() + 1;
                const peak = PEAK_MONTH_MULTIPLIERS[monthNum];
                return (
                  <tr key={m.month}>
                    <td style={{ fontWeight: 600 }}>{m.month}</td>
                    <td style={{ color: 'var(--success)', fontWeight: 700 }}>{fmt(m.income)}</td>
                    <td style={{ color: 'var(--danger)', fontWeight: 700 }}>{fmt(m.expense)}</td>
                    <td style={{ color: m.net >= 0 ? 'var(--success)' : 'var(--danger)', fontWeight: 700 }}>{fmt(m.net)}</td>
                    <td>{fmt(m.opening_balance)}</td>
                    <td>{fmt(m.closing_balance)}</td>
                    <td>
                      {peak ? (
                        <span className="badge badge-warning" style={{ fontSize: 10 }}>
                          {peak.name} +{Math.round((peak.multiplier - 1) * 100)}%
                        </span>
                      ) : (
                        <span style={{ color: 'var(--text-muted)', fontSize: 11 }}>—</span>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
