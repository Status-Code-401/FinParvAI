import { useEffect, useState, useRef } from 'react';
import { getCalendar } from '../services/api';
import {
  TrendingUp, TrendingDown, Package, ShoppingCart,
  CreditCard, Users, Factory, ChevronLeft, ChevronRight, X
} from 'lucide-react';

// ── Types ──────────────────────────────────────────────────────────────────────
interface CalEvent {
  type: string;
  label: string;
  amount: number;
  flow: 'in' | 'out' | 'neutral';
  badge: string;
  forecast?: boolean;
  units?: number;
  vendor?: string;
  client?: string;
  material?: string;
  quantity?: number;
  status?: string;
  priority?: string;
  probability?: number;
  invoice_id?: string;
  payable_id?: string;
  order_id?: string;
  cost?: number;
}

interface CalDay {
  date: string;
  is_today: boolean;
  is_past: boolean;
  is_future: boolean;
  events: CalEvent[];
  net_flow: number;
  total_inflow: number;
  total_outflow: number;
}

// ── Helpers ────────────────────────────────────────────────────────────────────
const fmt = (n: number) => `₹${Math.abs(n).toLocaleString('en-IN')}`;
const DAY_NAMES = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
const MONTH_NAMES = ['January', 'February', 'March', 'April', 'May', 'June',
                     'July', 'August', 'September', 'October', 'November', 'December'];

function eventIcon(type: string) {
  switch (type) {
    case 'production':
    case 'production_forecast': return <Factory size={10} />;
    case 'payable':             return <CreditCard size={10} />;
    case 'receivable':          return <Users size={10} />;
    case 'procurement':         return <ShoppingCart size={10} />;
    case 'bank_credit':         return <TrendingUp size={10} />;
    case 'bank_debit':          return <TrendingDown size={10} />;
    default:                    return <Package size={10} />;
  }
}

function eventColor(type: string, flow: string) {
  if (type === 'payable')            return 'var(--danger)';
  if (type === 'receivable')         return 'var(--success)';
  if (type === 'procurement')        return 'var(--accent)';
  if (type === 'production')         return 'var(--cyan)';
  if (type === 'production_forecast') return 'rgba(79,142,247,0.5)';
  if (type === 'bank_credit')        return 'var(--success)';
  if (type === 'bank_debit')         return 'var(--danger)';
  return flow === 'in' ? 'var(--success)' : flow === 'out' ? 'var(--danger)' : 'var(--accent)';
}

// ── Event Dot (chip shown on a calendar cell) ─────────────────────────────────
function EventChip({ ev }: { ev: CalEvent }) {
  const color = eventColor(ev.type, ev.flow);
  return (
    <div style={{
      display: 'flex',
      alignItems: 'center',
      gap: 3,
      fontSize: 9,
      color,
      background: `${color}18`,
      borderRadius: 3,
      padding: '2px 4px',
      overflow: 'hidden',
      whiteSpace: 'nowrap',
      textOverflow: 'ellipsis',
      maxWidth: '100%',
      borderLeft: `2px solid ${color}`,
      opacity: ev.forecast ? 0.75 : 1,
    }} title={ev.label}>
      {eventIcon(ev.type)}
      <span style={{ overflow: 'hidden', textOverflow: 'ellipsis' }}>
        {ev.forecast ? '~' : ''}{fmt(ev.amount)}
      </span>
    </div>
  );
}

// ── Tooltip / Event Detail Panel ──────────────────────────────────────────────
function EventDetail({ day, onClose }: { day: CalDay; onClose: () => void }) {
  const d = new Date(day.date + 'T00:00:00');
  const typeLabels: Record<string, string> = {
    production: '🏭 Production',
    production_forecast: '🏭 Expected Production',
    payable: '💸 Bill to Pay',
    receivable: '💰 Money to Collect',
    procurement: '📦 Material Delivery',
    bank_credit: '✅ Payment Received',
    bank_debit: '❌ Payment Made',
  };

  return (
    <div style={{
      position: 'fixed', inset: 0, zIndex: 9999,
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      background: 'rgba(0,0,0,0.55)', backdropFilter: 'blur(4px)',
    }} onClick={onClose}>
      <div style={{
        background: 'var(--bg-card)',
        border: '1px solid var(--border)',
        borderRadius: 16,
        padding: 24,
        maxWidth: 480,
        width: '90%',
        maxHeight: '80vh',
        overflowY: 'auto',
        boxShadow: '0 24px 60px rgba(0,0,0,0.5)',
      }} onClick={e => e.stopPropagation()}>

        {/* Header */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 18 }}>
          <div>
            <div style={{ fontWeight: 800, fontSize: 16 }}>
              {d.getDate()} {MONTH_NAMES[d.getMonth()]} {d.getFullYear()}
              {day.is_today && <span className="badge badge-info" style={{ marginLeft: 8, fontSize: 10 }}>Today</span>}
              {day.is_future && <span className="badge badge-warning" style={{ marginLeft: 8, fontSize: 10 }}>Forecast</span>}
            </div>
            <div style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 2 }}>{DAY_NAMES[d.getDay()]}</div>
          </div>
          <button onClick={onClose} style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--text-muted)' }}>
            <X size={18} />
          </button>
        </div>

        {/* Net flow summary */}
        <div style={{ display: 'flex', gap: 10, marginBottom: 18 }}>
          {day.total_inflow > 0 && (
            <div style={{ flex: 1, background: 'rgba(16,185,129,0.08)', border: '1px solid rgba(16,185,129,0.2)', borderRadius: 8, padding: '10px 14px', textAlign: 'center' }}>
              <div style={{ fontSize: 10, color: 'var(--text-muted)', marginBottom: 4 }}>Money In</div>
              <div style={{ fontWeight: 800, fontSize: 17, color: 'var(--success)' }}>{fmt(day.total_inflow)}</div>
            </div>
          )}
          {day.total_outflow > 0 && (
            <div style={{ flex: 1, background: 'rgba(239,68,68,0.08)', border: '1px solid rgba(239,68,68,0.2)', borderRadius: 8, padding: '10px 14px', textAlign: 'center' }}>
              <div style={{ fontSize: 10, color: 'var(--text-muted)', marginBottom: 4 }}>Money Out</div>
              <div style={{ fontWeight: 800, fontSize: 17, color: 'var(--danger)' }}>{fmt(day.total_outflow)}</div>
            </div>
          )}
          {(day.total_inflow > 0 || day.total_outflow > 0) && (
            <div style={{ flex: 1, background: 'rgba(255,255,255,0.04)', border: '1px solid var(--border)', borderRadius: 8, padding: '10px 14px', textAlign: 'center' }}>
              <div style={{ fontSize: 10, color: 'var(--text-muted)', marginBottom: 4 }}>Net</div>
              <div style={{ fontWeight: 800, fontSize: 17, color: day.net_flow >= 0 ? 'var(--success)' : 'var(--danger)' }}>
                {day.net_flow >= 0 ? '+' : '-'}{fmt(day.net_flow)}
              </div>
            </div>
          )}
        </div>

        {/* Events list */}
        {day.events.length === 0 ? (
          <div style={{ textAlign: 'center', color: 'var(--text-muted)', fontSize: 13, padding: '20px 0' }}>
            No events on this day.
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
            {day.events.map((ev, i) => {
              const color = eventColor(ev.type, ev.flow);
              return (
                <div key={i} style={{
                  background: 'var(--bg-body)',
                  borderRadius: 10,
                  padding: '12px 14px',
                  borderLeft: `3px solid ${color}`,
                }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 6 }}>
                    <span style={{ color, fontSize: 11, fontWeight: 700, display: 'flex', alignItems: 'center', gap: 4 }}>
                      {eventIcon(ev.type)} {typeLabels[ev.type] || ev.type}
                    </span>
                    {ev.forecast && <span className="badge" style={{ fontSize: 9, background: 'var(--accent)', color: '#fff' }}>Projected</span>}
                    {ev.status && <span className="badge" style={{ fontSize: 9, marginLeft: 'auto' }}>{ev.status}</span>}
                  </div>
                  <div style={{ fontSize: 13, color: 'var(--text-secondary)', marginBottom: 8, lineHeight: 1.4 }}>{ev.label}</div>
                  <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
                    {ev.amount > 0 && (
                      <div>
                        <span style={{ fontSize: 10, color: 'var(--text-muted)' }}>Amount</span>
                        <div style={{ fontWeight: 800, fontSize: 15, color }}>{fmt(ev.amount)}</div>
                      </div>
                    )}
                    {ev.units != null && (
                      <div>
                        <span style={{ fontSize: 10, color: 'var(--text-muted)' }}>Units</span>
                        <div style={{ fontWeight: 700, fontSize: 14 }}>{ev.units} pcs</div>
                      </div>
                    )}
                    {ev.quantity != null && (
                      <div>
                        <span style={{ fontSize: 10, color: 'var(--text-muted)' }}>Quantity</span>
                        <div style={{ fontWeight: 700, fontSize: 14 }}>{ev.quantity}</div>
                      </div>
                    )}
                    {ev.probability != null && (
                      <div>
                        <span style={{ fontSize: 10, color: 'var(--text-muted)' }}>Collection probability</span>
                        <div style={{ fontWeight: 700, fontSize: 14, color: ev.probability >= 0.8 ? 'var(--success)' : 'var(--warning)' }}>
                          {Math.round(ev.probability * 100)}%
                        </div>
                      </div>
                    )}
                    {ev.priority && (
                      <div>
                        <span style={{ fontSize: 10, color: 'var(--text-muted)' }}>Priority</span>
                        <div style={{ fontWeight: 700, fontSize: 13, color: ev.priority === 'critical' ? 'var(--danger)' : 'var(--warning)', textTransform: 'capitalize' }}>
                          {ev.priority}
                        </div>
                      </div>
                    )}
                  </div>
                  {(ev.invoice_id || ev.payable_id || ev.order_id) && (
                    <div style={{ marginTop: 8, fontSize: 10, color: 'var(--text-muted)' }}>
                      Ref: {ev.invoice_id || ev.payable_id || ev.order_id}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}

// ── Legend ────────────────────────────────────────────────────────────────────
function Legend() {
  const items = [
    { color: 'var(--cyan)',    label: 'Production (actual)' },
    { color: 'rgba(79,142,247,0.5)', label: 'Production (forecast)' },
    { color: 'var(--success)', label: 'Money In / Receivable' },
    { color: 'var(--danger)',  label: 'Bill Due / Payment Out' },
    { color: 'var(--accent)',  label: 'Procurement Delivery' },
  ];
  return (
    <div style={{ display: 'flex', flexWrap: 'wrap', gap: 12, marginBottom: 18 }}>
      {items.map(({ color, label }) => (
        <span key={label} style={{ display: 'flex', alignItems: 'center', gap: 5, fontSize: 11, color: 'var(--text-muted)' }}>
          <span style={{ width: 10, height: 10, borderRadius: 2, background: color, display: 'inline-block' }} />
          {label}
        </span>
      ))}
    </div>
  );
}

// ── Main Calendar Page ────────────────────────────────────────────────────────
export default function CalendarDashboard() {
  const [data, setData] = useState<{ days: CalDay[]; today: string; summary: any } | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedDay, setSelectedDay] = useState<CalDay | null>(null);
  const [viewDate, setViewDate] = useState(new Date());

  useEffect(() => {
    getCalendar().then(setData).finally(() => setLoading(false));
  }, []);

  if (loading) return (
    <div className="loading-center"><div className="spinner" /><span>Building your cash calendar…</span></div>
  );
  if (!data) return null;

  // Index days by date string for O(1) lookup
  const dayIndex = new Map<string, CalDay>(data.days.map(d => [d.date, d]));

  // Build calendar grid for the current view month
  const year = viewDate.getFullYear();
  const month = viewDate.getMonth();
  const firstDay = new Date(year, month, 1).getDay(); // 0=Sun
  const daysInMonth = new Date(year, month + 1, 0).getDate();

  // Pad at start
  const grid: (CalDay | null)[] = Array(firstDay).fill(null);
  for (let d = 1; d <= daysInMonth; d++) {
    const dateStr = `${year}-${String(month + 1).padStart(2, '0')}-${String(d).padStart(2, '0')}`;
    grid.push(dayIndex.get(dateStr) ?? null);
  }
  // Pad to complete last row
  while (grid.length % 7 !== 0) grid.push(null);

  const today = data.today;
  const { summary } = data;
  const todayData = dayIndex.get(today);

  const prevMonth = () => setViewDate(new Date(year, month - 1, 1));
  const nextMonth = () => setViewDate(new Date(year, month + 1, 1));

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">Cash Calendar</h1>
        <p className="page-subtitle">
          Daily view of your sales, bills, collections and deliveries — past, present and future
        </p>
      </div>

      {/* Summary KPIs */}
      <div className="kpi-grid" style={{ gridTemplateColumns: 'repeat(4, 1fr)', marginBottom: 20 }}>
        <div className="card">
          <div className="card-title">Bills Due (outstanding)</div>
          <div className="card-value" style={{ color: 'var(--danger)' }}>{fmt(summary.total_payables_due)}</div>
          <div className="card-sub">Upcoming payments</div>
        </div>
        <div className="card">
          <div className="card-title">Expected Collections</div>
          <div className="card-value" style={{ color: 'var(--success)' }}>{fmt(summary.total_receivables_expected)}</div>
          <div className="card-sub">Money coming in</div>
        </div>
        <div className="card">
          <div className="card-title">Net Position</div>
          <div className="card-value" style={{ color: summary.total_receivables_expected - summary.total_payables_due >= 0 ? 'var(--success)' : 'var(--danger)' }}>
            {summary.total_receivables_expected - summary.total_payables_due >= 0 ? '+' : ''}{fmt(summary.total_receivables_expected - summary.total_payables_due)}
          </div>
          <div className="card-sub">Collections minus bills</div>
        </div>
        <div className="card">
          <div className="card-title">Procurement Deliveries</div>
          <div className="card-value">{summary.procurement_deliveries}</div>
          <div className="card-sub">Pending orders</div>
        </div>
      </div>

      {/* Today's snapshot */}
      {todayData && todayData.events.length > 0 && (
        <div className="card" style={{ marginBottom: 20, border: '1px solid var(--accent)' }}>
          <div style={{ fontWeight: 800, fontSize: 14, marginBottom: 12, color: 'var(--accent)', display: 'flex', alignItems: 'center', gap: 8 }}>
            📅 Today's Events
            <span className="badge badge-info">Live</span>
          </div>
          <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
            {todayData.events.map((ev, i) => {
              const color = eventColor(ev.type, ev.flow);
              return (
                <div key={i} style={{
                  background: `${color}10`,
                  border: `1px solid ${color}40`,
                  borderRadius: 8,
                  padding: '8px 12px',
                  fontSize: 12,
                  display: 'flex',
                  alignItems: 'center',
                  gap: 6,
                  color,
                }}>
                  {eventIcon(ev.type)}
                  <span style={{ color: 'var(--text-secondary)' }}>{ev.label}</span>
                  <span style={{ fontWeight: 800 }}>{fmt(ev.amount)}</span>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Calendar Navigation */}
      <div className="card">
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 16 }}>
          <button onClick={prevMonth} style={{ background: 'none', border: '1px solid var(--border)', borderRadius: 6, padding: '6px 10px', cursor: 'pointer', color: 'var(--text-secondary)', display: 'flex', alignItems: 'center' }}>
            <ChevronLeft size={16} />
          </button>
          <div style={{ fontWeight: 800, fontSize: 16 }}>
            {MONTH_NAMES[month]} {year}
          </div>
          <button onClick={nextMonth} style={{ background: 'none', border: '1px solid var(--border)', borderRadius: 6, padding: '6px 10px', cursor: 'pointer', color: 'var(--text-secondary)', display: 'flex', alignItems: 'center' }}>
            <ChevronRight size={16} />
          </button>
        </div>

        <Legend />

        {/* Day headers */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(7, 1fr)', gap: 4, marginBottom: 4 }}>
          {DAY_NAMES.map(d => (
            <div key={d} style={{ textAlign: 'center', fontSize: 10, fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', padding: '4px 0' }}>
              {d}
            </div>
          ))}
        </div>

        {/* Calendar cells */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(7, 1fr)', gap: 4 }}>
          {grid.map((day, i) => {
            if (!day) return <div key={i} style={{ minHeight: 90 }} />;

            const d = new Date(day.date + 'T00:00:00');
            const dayNum = d.getDate();
            const hasEvents = day.events.length > 0;
            const isToday = day.is_today;
            const isFuture = day.is_future;
            const isPast = day.is_past;

            // Determine cell background tint from net flow
            let bgTint = 'transparent';
            if (hasEvents) {
              if (day.net_flow > 0)       bgTint = 'rgba(16,185,129,0.06)';
              else if (day.net_flow < 0)  bgTint = 'rgba(239,68,68,0.06)';
              else                         bgTint = 'rgba(79,142,247,0.04)';
            }

            // Dots: up to 3 event chips shown
            const visibleEvents = day.events.slice(0, 3);
            const extraCount = day.events.length - 3;

            return (
              <div
                key={i}
                onClick={() => setSelectedDay(day)}
                style={{
                  minHeight: 90,
                  background: isToday
                    ? 'rgba(79,142,247,0.12)'
                    : isFuture
                    ? bgTint || 'rgba(255,255,255,0.02)'
                    : bgTint || 'rgba(255,255,255,0.01)',
                  border: isToday
                    ? '1.5px solid var(--accent)'
                    : hasEvents
                    ? '1px solid rgba(255,255,255,0.08)'
                    : '1px solid transparent',
                  borderRadius: 8,
                  padding: '6px 5px',
                  cursor: hasEvents ? 'pointer' : 'default',
                  opacity: isPast && !hasEvents ? 0.35 : 1,
                  transition: 'background 0.15s',
                  position: 'relative',
                }}
                onMouseEnter={e => { if (hasEvents) (e.currentTarget as HTMLElement).style.background = isToday ? 'rgba(79,142,247,0.18)' : 'rgba(255,255,255,0.07)'; }}
                onMouseLeave={e => { (e.currentTarget as HTMLElement).style.background = isToday ? 'rgba(79,142,247,0.12)' : bgTint; }}
              >
                {/* Date number */}
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 4 }}>
                  <span style={{
                    fontSize: 12, fontWeight: isToday ? 800 : 500,
                    width: 20, height: 20, borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center',
                    background: isToday ? 'var(--accent)' : 'transparent',
                    color: isToday ? '#fff' : (isPast ? 'var(--text-muted)' : 'var(--text-primary)'),
                  }}>
                    {dayNum}
                  </span>
                  {/* Net flow indicator dot */}
                  {hasEvents && (
                    <span style={{
                      width: 6, height: 6, borderRadius: '50%',
                      background: day.net_flow > 0 ? 'var(--success)' : day.net_flow < 0 ? 'var(--danger)' : 'var(--warning)',
                      boxShadow: `0 0 4px ${day.net_flow > 0 ? 'var(--success)' : day.net_flow < 0 ? 'var(--danger)' : 'var(--warning)'}`,
                    }} />
                  )}
                </div>

                {/* Event chips */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                  {visibleEvents.map((ev, j) => <EventChip key={j} ev={ev} />)}
                  {extraCount > 0 && (
                    <div style={{ fontSize: 9, color: 'var(--text-muted)', paddingLeft: 4 }}>
                      +{extraCount} more
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>

        {/* Net flow bar under calendar */}
        <div style={{ marginTop: 16, paddingTop: 14, borderTop: '1px solid var(--border)' }}>
          <div style={{ fontWeight: 700, fontSize: 13, marginBottom: 10 }}>This month's daily net flow</div>
          <div style={{ display: 'flex', gap: 2, alignItems: 'flex-end', height: 48 }}>
            {Array.from({ length: daysInMonth }, (_, idx) => {
              const dateStr = `${year}-${String(month + 1).padStart(2, '0')}-${String(idx + 1).padStart(2, '0')}`;
              const dayData = dayIndex.get(dateStr);
              if (!dayData || !dayData.total_inflow && !dayData.total_outflow) return (
                <div key={idx} style={{ flex: 1, height: 4, background: 'rgba(255,255,255,0.05)', borderRadius: 2 }} title={`${idx + 1}: No data`} />
              );
              const maxFlow = 200000;
              const inH = Math.max(4, Math.round((dayData.total_inflow / maxFlow) * 44));
              const outH = Math.max(4, Math.round((dayData.total_outflow / maxFlow) * 44));
              const isT = dayData.is_today;
              return (
                <div key={idx} style={{ flex: 1, display: 'flex', alignItems: 'flex-end', gap: 1, cursor: 'pointer' }}
                  onClick={() => setSelectedDay(dayData)}
                  title={`${idx + 1}: In ${fmt(dayData.total_inflow)} | Out ${fmt(dayData.total_outflow)}`}>
                  {dayData.total_inflow > 0 && (
                    <div style={{ flex: 1, height: inH, background: isT ? 'var(--accent)' : 'var(--success)', borderRadius: '2px 2px 0 0', opacity: dayData.is_future ? 0.5 : 1 }} />
                  )}
                  {dayData.total_outflow > 0 && (
                    <div style={{ flex: 1, height: outH, background: 'var(--danger)', borderRadius: '2px 2px 0 0', opacity: dayData.is_future ? 0.5 : 1 }} />
                  )}
                </div>
              );
            })}
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 9, color: 'var(--text-muted)', marginTop: 4 }}>
            <span>1</span><span>{Math.round(daysInMonth / 2)}</span><span>{daysInMonth}</span>
          </div>
        </div>
      </div>

      {/* Event detail modal */}
      {selectedDay && (
        <EventDetail day={selectedDay} onClose={() => setSelectedDay(null)} />
      )}
    </div>
  );
}
