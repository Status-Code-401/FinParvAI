import { useEffect, useState } from 'react';
import { getCostIntelligence, approveAction, executeAction, toggleAutoExecute } from '../services/api';
import './CostIntelligence.css';

/* ─── Types ─────────────────────────────────────────────── */
interface Impact { amount: number; type: string; confidence: number; breakdown: Record<string, any>; }
interface Leakage { type: string; description: string; impact: number; severity: string; recommendation: string; }
interface Signal { signal: string; type: string; description: string; impact: number; severity: string; recommendation: string; formula?: string; }
interface ExecAction { action_id: string; action: string; status: string; confidence: number; auto_eligible: boolean; impact: Impact; execution_result?: any; }

const fmt = (n: number) => n.toLocaleString('en-IN', { maximumFractionDigits: 0 });

/* ═══════════════════════════════════════════════════════════
   MAIN PAGE
   ═══════════════════════════════════════════════════════════ */
export default function CostIntelligence() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [tab, setTab] = useState<'overview' | 'leakage' | 'signals' | 'impact' | 'execution'>('overview');
  const [autoExec, setAutoExec] = useState(false);
  const [executingId, setExecutingId] = useState<string | null>(null);
  const [toastMsg, setToastMsg] = useState('');

  const load = async () => {
    setLoading(true); setError('');
    try {
      const r = await getCostIntelligence();
      setData(r); setAutoExec(r?.execution?.auto_execute_enabled || false);
    } catch (e: any) { setError(e.message || 'Failed to load'); }
    finally { setLoading(false); }
  };

  useEffect(() => { load(); }, []);

  const toast = (m: string) => { setToastMsg(m); setTimeout(() => setToastMsg(''), 3000); };

  const handleApprove = async (id: string) => {
    try { await approveAction(id); toast('Action approved'); load(); } catch { toast('Failed to approve'); }
  };
  const handleExecute = async (id: string) => {
    setExecutingId(id);
    try { await executeAction(id); toast('Action executed successfully'); load(); } catch { toast('Execution failed'); }
    finally { setExecutingId(null); }
  };
  const handleAutoToggle = async () => {
    const next = !autoExec;
    try { await toggleAutoExecute(next); setAutoExec(next); toast(next ? 'Auto-execute enabled' : 'Auto-execute disabled'); } catch { toast('Toggle failed'); }
  };

  /* ── Loading ── */
  if (loading) return (
    <div className="ci-loading">
      <div className="ci-loader"><div /><div /><div /></div>
      <p>Running cost intelligence analysis…</p>
    </div>
  );

  if (error) return (
    <div className="ci-error">
      <span>⚠</span> {error}
      <button onClick={load}>Retry</button>
    </div>
  );

  if (!data) return null;

  const s = data.combined_summary || {};
  const impact = data.impact || {};
  const leakage = data.leakage || {};
  const signals = data.signals || {};
  const execution = data.execution || {};

  const tabs = [
    { key: 'overview', icon: '◎', label: 'Overview' },
    { key: 'leakage', icon: '⬡', label: 'Leakage' },
    { key: 'signals', icon: '◈', label: 'Signals' },
    { key: 'impact', icon: '◆', label: 'Impact' },
    { key: 'execution', icon: '⚡', label: 'Execution' },
  ] as const;

  return (
    <div className="ci">
      {/* ── Toast ── */}
      {toastMsg && (
        <div className="ci-toast">
          <span className="ci-toast-dot" />
          {toastMsg}
        </div>
      )}

      {/* ── Hero ── */}
      <header className="ci-hero">
        <div className="ci-hero-glow" />
        <p className="ci-hero-eyebrow">Autonomous Finance · Real-time</p>
        <div className="ci-hero-top">
          <div>
            <h1 className="ci-hero-h1">Cost Intelligence</h1>
            <p className="ci-hero-p">Detection · Quantification · Autonomous Execution</p>
          </div>
          <span className={`ci-badge-risk ci-risk-${s.risk_level || 'unknown'}`}>
            <span className="ci-risk-pulse" />
            {(s.risk_level || 'unknown').toUpperCase()} RISK
          </span>
        </div>

        <div className="ci-kpi-row">
          <KpiCard accent="green" label="Total Savings" value={`₹${fmt(s.grand_total_financial_impact || 0)}`} sub="potential recovery" />
          <KpiCard accent="danger" label="Leakage Detected" value={`₹${fmt(s.total_leakage_detected || 0)}`} sub={`${s.leakages_count || 0} issues found`} />
          <KpiCard accent="blue" label="Enterprise Signals" value={String(s.signals_count || 0)} sub={`₹${fmt(s.total_signal_impact || 0)} impact`} />
          <KpiCard accent="orange" label="Execution Ready" value={`${s.execution_ready_count || 0} / ${s.actions_count || 0}`} sub="auto-eligible actions" />
        </div>
      </header>

      {/* ── Tab Nav ── */}
      <nav className="ci-nav">
        {tabs.map(t => (
          <button
            key={t.key}
            className={`ci-nav-btn ${tab === t.key ? 'on' : ''}`}
            onClick={() => setTab(t.key)}
          >
            <span className="ci-nav-icon">{t.icon}</span>
            {t.label}
          </button>
        ))}
      </nav>

      {/* ── Content ── */}
      <section className="ci-body">
        {tab === 'overview' && <OverviewTab leakage={leakage} signals={signals} impact={impact} execution={execution} />}
        {tab === 'leakage' && <LeakageTab data={leakage} />}
        {tab === 'signals' && <SignalsTab data={signals} />}
        {tab === 'impact' && <ImpactTab data={impact} />}
        {tab === 'execution' && (
          <ExecutionTab
            data={execution} autoExec={autoExec} executingId={executingId}
            onApprove={handleApprove} onExecute={handleExecute} onAutoToggle={handleAutoToggle}
          />
        )}
      </section>
    </div>
  );
}

/* ─── KPI Card ─────────────────────────────────────────── */
function KpiCard({ accent, label, value, sub }: { accent: string; label: string; value: string; sub: string }) {
  return (
    <div className={`ci-kpi ci-kpi-${accent}`}>
      <span className="ci-kpi-label">{label}</span>
      <span className="ci-kpi-value">{value}</span>
      <span className="ci-kpi-sub">{sub}</span>
    </div>
  );
}

/* ─── Severity primitives ──────────────────────────────── */
function SevDot({ level }: { level: string }) {
  return <span className={`ci-dot ci-dot-${level}`} />;
}
function SevBadge({ level }: { level: string }) {
  return <span className={`ci-sev-pill ci-sev-${level}`}>{level.toUpperCase()}</span>;
}

/* ─── Pagination Component ─────────────────────────────── */
function Pagination({ total, current, onChange, pageSize = 5 }: { total: number, current: number, onChange: (p: number) => void, pageSize?: number }) {
  const pages = Math.ceil(total / pageSize);
  if (pages <= 1) return null;
  const start = (current - 1) * pageSize + 1;
  const end = Math.min(current * pageSize, total);
  
  return (
    <div className="ci-pagination">
      <div className="ci-page-info">Showing {start}-{end} of {total}</div>
      <div className="ci-page-controls">
        <button className="ci-page-btn" disabled={current === 1} onClick={() => onChange(current - 1)}>Prev</button>
        <div className="ci-page-numbers">
          {Array.from({length: pages}, (_, i) => i + 1).map(p => (
            <button key={p} className={`ci-page-num ${p === current ? 'active' : ''}`} onClick={() => onChange(p)}>
              {p}
            </button>
          ))}
        </div>
        <button className="ci-page-btn" disabled={current === pages} onClick={() => onChange(current + 1)}>Next</button>
      </div>
    </div>
  );
}

/* ═══════════════════════════════════════════════════════════
   OVERVIEW TAB
   ═══════════════════════════════════════════════════════════ */
function OverviewTab({ leakage, signals, impact, execution }: any) {
  return (
    <div className="ci-overview">
      <div className="ci-mod-grid">
        <ModuleCard icon="⚠" title="Cost Leakage" accent="red"
          primary={`₹${fmt(leakage.total_leakage_amount || 0)}`}
          secondary={`${leakage.leakage_count || 0} issues detected`}
          badges={[
            { n: leakage.by_severity?.high, l: 'high' },
            { n: leakage.by_severity?.medium, l: 'medium' },
            { n: leakage.by_severity?.low, l: 'low' },
          ]}
        />
        <ModuleCard icon="◈" title="Signals" accent="blue"
          primary={`₹${fmt(signals.total_impact || 0)}`}
          secondary={`${signals.total_signals || 0} signals active`}
          badges={[
            { n: signals.by_severity?.high, l: 'high' },
            { n: signals.by_severity?.medium, l: 'medium' },
          ]}
        />
        <ModuleCard icon="◆" title="Impact" accent="green"
          primary={`₹${fmt(impact.total_potential_savings || 0)}`}
          secondary={`${impact.summary?.actions_analyzed || 0} actions quantified`}
          badges={[{ n: Math.round((impact.summary?.avg_confidence || 0) * 100), l: 'conf', suffix: '% conf' }]}
        />
        <ModuleCard icon="⚡" title="Execution" accent="orange"
          primary={`${execution.auto_eligible_count || 0} ready`}
          secondary={`${execution.manual_review_count || 0} need approval`}
          badges={[]}
        />
      </div>

      <div className="ci-split">
        <div className="ci-card">
          <h3 className="ci-card-h">
            <span className="ci-card-h-icon">⚠</span>
            Top Leakages
          </h3>
          <div className="ci-items">
            {(leakage.leakages || []).slice(0, 3).map((l: Leakage, i: number) => (
              <IssueRow key={i} severity={l.severity} type={l.type} desc={l.description} impact={l.impact} rec={l.recommendation} />
            ))}
            {(leakage.leakages || []).length === 0 && <p className="ci-empty-msg">No leakages found ✓</p>}
          </div>
        </div>
        <div className="ci-card">
          <h3 className="ci-card-h">
            <span className="ci-card-h-icon">◈</span>
            Top Signals
          </h3>
          <div className="ci-items">
            {(signals.signals || []).slice(0, 3).map((s: Signal, i: number) => (
              <IssueRow key={i} severity={s.severity} type={s.signal} desc={s.description} impact={s.impact} rec={s.recommendation} formula={s.formula} />
            ))}
            {(signals.signals || []).length === 0 && <p className="ci-empty-msg">No signals found</p>}
          </div>
        </div>
      </div>
    </div>
  );
}

function ModuleCard({ icon, title, accent, primary, secondary, badges }: any) {
  return (
    <div className={`ci-mod ci-mod-${accent}`}>
      <div className="ci-mod-top">
        <span className="ci-mod-icon">{icon}</span>
        <span className="ci-mod-title">{title}</span>
      </div>
      <span className="ci-mod-primary">{primary}</span>
      <span className="ci-mod-secondary">{secondary}</span>
      {badges.length > 0 && (
        <div className="ci-mod-badges">
          {badges.filter((b: any) => b.n > 0).map((b: any, i: number) => (
            <span key={i} className={`ci-mod-badge ci-mb-${b.l}`}>{b.n}{b.suffix ?? ` ${b.l}`}</span>
          ))}
        </div>
      )}
    </div>
  );
}

function IssueRow({ severity, type, desc, impact, rec, formula }: {
  severity: string; type: string; desc: string; impact: number; rec: string; formula?: string;
}) {
  return (
    <div className={`ci-issue ci-issue-${severity}`}>
      <div className="ci-issue-top">
        <SevDot level={severity} />
        <span className="ci-issue-type">{type.replace(/_/g, ' ')}</span>
        <span className="ci-issue-amt">₹{fmt(impact || 0)}</span>
      </div>
      <p className="ci-issue-desc">{desc}</p>
      {formula && <p className="ci-issue-formula">{formula}</p>}
      <p className="ci-issue-rec">{rec}</p>
    </div>
  );
}

/* ═══════════════════════════════════════════════════════════
   LEAKAGE TAB
   ═══════════════════════════════════════════════════════════ */
function LeakageTab({ data }: { data: any }) {
  const items: Leakage[] = data.leakages || [];
  const bt = data.by_type || {};
  const [page, setPage] = useState(1);
  const pageSize = 5;
  const visible = items.slice((page - 1) * pageSize, page * pageSize);

  return (
    <div className="ci-card ci-card-flush">
      <div className="ci-panel-top">
        <h2 className="ci-panel-h">Cost Leakage Detection</h2>
        <div className="ci-pill-row">
          <Pill color="red" label="Duplicates" n={bt.duplicate_payments || 0} />
          <Pill color="orange" label="Vendor" n={bt.vendor_anomalies || 0} />
          <Pill color="yellow" label="Inventory" n={bt.idle_inventory || 0} />
          <Pill color="blue" label="Receivables" n={bt.receivable_risks || 0} />
        </div>
      </div>
      <div className="ci-items ci-items-padded">
        {visible.map((l, i) => (
          <div key={i} className={`ci-issue ci-issue-${l.severity}`}>
            <div className="ci-issue-top">
              <SevBadge level={l.severity} />
              <span className="ci-issue-type">{l.type.replace(/_/g, ' ')}</span>
              <span className="ci-issue-amt">₹{fmt(l.impact || 0)}</span>
            </div>
            <p className="ci-issue-desc">{l.description}</p>
            <p className="ci-issue-rec">{l.recommendation}</p>
          </div>
        ))}
        {items.length === 0 && <p className="ci-empty-msg">No leakages — finances look clean ✓</p>}
      </div>
      <Pagination total={items.length} current={page} onChange={setPage} pageSize={pageSize} />
    </div>
  );
}

/* ═══════════════════════════════════════════════════════════
   SIGNALS TAB
   ═══════════════════════════════════════════════════════════ */
function SignalsTab({ data }: { data: any }) {
  const items: Signal[] = data.signals || [];
  const bt = data.by_type || {};
  const [page, setPage] = useState(1);
  const pageSize = 5;
  const visible = items.slice((page - 1) * pageSize, page * pageSize);

  return (
    <div className="ci-card ci-card-flush">
      <div className="ci-panel-top">
        <h2 className="ci-panel-h">Enterprise Signal Layer</h2>
        <div className="ci-pill-row">
          <Pill color="red" label="SLA" n={bt.sla_risks || 0} />
          <Pill color="orange" label="Vendor" n={bt.vendor_benchmarks || 0} />
          <Pill color="yellow" label="Inventory" n={bt.inventory_signals || 0} />
          <Pill color="blue" label="Cash" n={bt.cash_velocity || 0} />
        </div>
      </div>
      <div className="ci-items ci-items-padded">
        {visible.map((s, i) => (
          <div key={i} className={`ci-issue ci-issue-${s.severity}`}>
            <div className="ci-issue-top">
              <SevBadge level={s.severity} />
              <span className="ci-issue-type">{s.signal.replace(/_/g, ' ')}</span>
              <span className="ci-issue-amt">₹{fmt(s.impact || 0)}</span>
            </div>
            <p className="ci-issue-desc">{s.description}</p>
            {s.formula && <p className="ci-issue-formula">{s.formula}</p>}
            <p className="ci-issue-rec">{s.recommendation}</p>
          </div>
        ))}
        {items.length === 0 && <p className="ci-empty-msg">No signals found</p>}
      </div>
      <Pagination total={items.length} current={page} onChange={setPage} pageSize={pageSize} />
    </div>
  );
}

/* ═══════════════════════════════════════════════════════════
   IMPACT TAB
   ═══════════════════════════════════════════════════════════ */
function ImpactTab({ data }: { data: any }) {
  const actions = (data.actions_with_impact || []).filter((a: any) => a.impact?.amount > 0);
  const [page, setPage] = useState(1);
  const pageSize = 5;
  const visible = actions.slice((page - 1) * pageSize, page * pageSize);

  return (
    <div className="ci-card ci-card-flush">
      <div className="ci-panel-top">
        <h2 className="ci-panel-h">Cost Impact Quantification</h2>
        <div className="ci-pill-row">
          <Pill color="green" label="Total" n={0} text={`₹${fmt(data.total_potential_savings || 0)}`} />
          <Pill color="blue" label="Confidence" n={0} text={`${Math.round((data.summary?.avg_confidence || 0) * 100)}%`} />
        </div>
      </div>
      <div className="ci-impact-list">
        {visible.map((a: any, i: number) => (
          <div key={i} className="ci-impact-row">
            <div className="ci-impact-row-top">
              <span className={`ci-pri ci-pri-${(a.priority || 'low').toLowerCase()}`}>{a.priority || '—'}</span>
              <span className="ci-impact-row-action">{a.action}</span>
              <span className="ci-impact-row-amt">₹{fmt(a.impact?.amount || 0)}</span>
            </div>
            <div className="ci-impact-row-meta">
              <span>{(a.impact?.type || '').replace(/_/g, ' ')}</span>
              <span className="ci-conf-bar">
                <span className="ci-conf-fill" style={{ width: `${(a.impact?.confidence || 0) * 100}%` }} />
              </span>
              <span>{Math.round((a.impact?.confidence || 0) * 100)}%</span>
            </div>
          </div>
        ))}
        {actions.length === 0 && <p className="ci-empty-msg">No impactful actions quantified</p>}
      </div>
      <Pagination total={actions.length} current={page} onChange={setPage} pageSize={pageSize} />
    </div>
  );
}

/* ═══════════════════════════════════════════════════════════
   EXECUTION TAB
   ═══════════════════════════════════════════════════════════ */
function ExecutionTab({ data, autoExec, executingId, onApprove, onExecute, onAutoToggle }: any) {
  const allActions: ExecAction[] = data.registered_actions || [];
  const autoEligible = allActions.filter(a => a.auto_eligible);
  const manual = allActions.filter(a => !a.auto_eligible);
  
  const [page, setPage] = useState(1);
  const pageSize = 6;
  const visibleManual = manual.slice((page - 1) * pageSize, page * pageSize);
  
  const logs = data.execution_logs || [];
  const [logPage, setLogPage] = useState(1);
  const logPageSize = 5;
  const visibleLogs = logs.slice((logPage - 1) * logPageSize, logPage * logPageSize);

  return (
    <div>
      <div className="ci-card ci-exec-ctrl">
        <div className="ci-exec-ctrl-row">
          <div>
            <h2 className="ci-exec-ctrl-title">Autonomous Execution</h2>
            <p className="ci-exec-ctrl-sub">
              {allActions.length} actions registered · {autoEligible.length} auto-eligible · {manual.length} need review
            </p>
          </div>
          <label className="ci-switch">
            <input type="checkbox" checked={autoExec} onChange={onAutoToggle} />
            <span className="ci-switch-track"><span className="ci-switch-thumb" /></span>
            <span className="ci-switch-label">Auto-Execute</span>
          </label>
        </div>
      </div>

      {autoEligible.length > 0 && (
        <div className="ci-card">
          <h3 className="ci-card-h">
            <span className="ci-card-h-icon ci-glow-green">⚡</span>
            Auto-Eligible Actions
            <span className="ci-card-h-count">{autoEligible.length}</span>
          </h3>
          <div className="ci-exec-cards">
            {autoEligible.map(a => (
              <ExecCard key={a.action_id} a={a} executingId={executingId} onApprove={onApprove} onExecute={onExecute} />
            ))}
          </div>
        </div>
      )}

      {manual.length > 0 && (
        <div className="ci-card ci-card-flush" style={{marginBottom: '2rem'}}>
          <div className="ci-panel-top">
            <h3 className="ci-card-h" style={{margin: 0}}>
              <span className="ci-card-h-icon">◎</span>
              Manual Review
              <span className="ci-card-h-count">{manual.length}</span>
            </h3>
          </div>
          <div className="ci-exec-cards" style={{padding: '1.5rem 2rem'}}>
            {visibleManual.map(a => (
              <ExecCard key={a.action_id} a={a} executingId={executingId} onApprove={onApprove} onExecute={onExecute} />
            ))}
          </div>
          <Pagination total={manual.length} current={page} onChange={setPage} pageSize={pageSize} />
        </div>
      )}

      {logs.length > 0 && (
        <div className="ci-card ci-card-flush">
          <div className="ci-panel-top">
            <h3 className="ci-card-h" style={{margin: 0}}>
              <span className="ci-card-h-icon">◷</span>
              Audit Log
            </h3>
          </div>
          <div className="ci-log-list">
            {visibleLogs.map((l: any, i: number) => (
              <div key={i} className="ci-log-row">
                <span className="ci-log-ts">{new Date(l.timestamp).toLocaleTimeString('en-IN', { hour12: false })}</span>
                <span className={`ci-sev-pill ci-sev-${l.status === 'executed' ? 'low' : l.status === 'rejected' ? 'high' : 'medium'}`}>
                  {l.status}
                </span>
                <span className="ci-log-txt">{l.action}</span>
              </div>
            ))}
          </div>
          <Pagination total={logs.length} current={logPage} onChange={setLogPage} pageSize={logPageSize} />
        </div>
      )}
    </div>
  );
}

function ExecCard({ a, executingId, onApprove, onExecute }: {
  a: ExecAction; executingId: string | null;
  onApprove: (id: string) => void; onExecute: (id: string) => void;
}) {
  const isRunning = executingId === a.action_id;
  return (
    <div className={`ci-xcard ci-xcard-${a.status}`}>
      <div className="ci-xcard-top">
        <span className={`ci-sev-pill ci-sev-${a.status === 'pending' ? 'medium' : a.status === 'executed' ? 'low' : 'high'}`}>
          {a.status}
        </span>
        {a.auto_eligible && <span className="ci-xcard-auto">⚡ auto</span>}
        <span className="ci-xcard-conf">{Math.round(a.confidence * 100)}%</span>
      </div>
      <p className="ci-xcard-action">{a.action}</p>
      {a.impact?.amount > 0 && <span className="ci-xcard-impact">₹{fmt(a.impact.amount)} savings</span>}
      {a.status === 'pending' && (
        <div className="ci-xcard-btns">
          <button className="ci-xbtn ci-xbtn-approve" onClick={() => onApprove(a.action_id)}>Approve</button>
          <button className="ci-xbtn ci-xbtn-exec" onClick={() => onExecute(a.action_id)} disabled={isRunning}>
            {isRunning ? 'Running…' : 'Execute'}
          </button>
        </div>
      )}
      {a.status === 'executed' && a.execution_result && (
        <div className="ci-xcard-result">{a.execution_result.message}</div>
      )}
    </div>
  );
}

function Pill({ color, label, n, text }: { color: string; label: string; n: number; text?: string }) {
  return (
    <span className={`ci-pill ci-pill-${color}`}>
      {label}: {text ?? n}
    </span>
  );
}