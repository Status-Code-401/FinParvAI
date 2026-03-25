import React, { useState } from 'react';
import { FinancialState, ActionPlan } from '../types';
import { generateActions } from '../utils/api';

interface Props { state: FinancialState | null; }
const fmtINR = (n: number) => `₹${Math.round(n).toLocaleString('en-IN')}`;

export default function ActionsPage({ state }: Props) {
  const [result, setResult] = useState<{ decision_summary: any; action_plan: ActionPlan } | null>(null);
  const [loading, setLoading] = useState(false);
  const [activeEmail, setActiveEmail] = useState<number | null>(null);
  const [copied, setCopied]   = useState<number | null>(null);

  const run = async () => {
    if (!state) return;
    setLoading(true);
    try {
      const d = await generateActions(state);
      setResult(d);
    } finally { setLoading(false); }
  };

  const copyEmail = (body: string, idx: number) => {
    navigator.clipboard.writeText(body).then(() => {
      setCopied(idx);
      setTimeout(() => setCopied(null), 2000);
    });
  };

  const riskColors: Record<string, string> = {
    low: '#00e5a0', medium: '#ffb800', high: '#ff6b35', critical: '#ff3b5c'
  };

  return (
    <div>
      <div className="page-header flex-between">
        <div>
          <div className="page-title">Action Centre</div>
          <div className="page-subtitle">Payment scheduling · Email drafts · Negotiation templates</div>
        </div>
        <button className="btn btn-primary" onClick={run} disabled={!state || loading}>
          {loading ? '✦ Generating...' : '✦ Generate Action Plan'}
        </button>
      </div>

      {!result && !loading && (
        <div className="card empty-state">
          <div className="empty-state-icon">✦</div>
          <div className="empty-state-text">Generate an action plan to get payment schedules, email drafts, and renegotiation templates.</div>
        </div>
      )}

      {result && (
        <>
          {/* Summary box */}
          <div className="card section-gap" style={{borderColor: riskColors[result.decision_summary.risk_level] + '40'}}>
            <div className="card-title">Decision Summary</div>
            <div className="explanation-box">{result.decision_summary.summary || result.decision_summary.explanation}</div>
          </div>

          {/* Payment Schedule */}
          <div className="card section-gap">
            <div className="card-title flex-between" style={{display:'flex',justifyContent:'space-between',alignItems:'center'}}>
              <span>Payment Schedule</span>
              <span className="tag">{result.action_plan.payment_schedule.length} payments</span>
            </div>
            <table className="data-table">
              <thead>
                <tr>
                  <th>Date</th>
                  <th>Vendor</th>
                  <th>Amount</th>
                  <th>Priority</th>
                  <th>Notes</th>
                </tr>
              </thead>
              <tbody>
                {result.action_plan.payment_schedule.map((ps, i) => (
                  <tr key={i}>
                    <td className="mono">{ps.date}</td>
                    <td style={{fontWeight:500}}>{ps.vendor}</td>
                    <td className={`mono ${ps.priority === 'high' ? 'text-danger' : 'text-dim'}`}>{fmtINR(ps.amount)}</td>
                    <td>
                      <span className={`action-chip ${ps.priority === 'high' ? 'chip-pay' : ps.priority === 'medium' ? 'chip-part' : 'chip-delay'}`}>
                        {ps.priority}
                      </span>
                    </td>
                    <td style={{fontSize:11,color:'#7a8090',maxWidth:280}}>{ps.notes}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Email Drafts */}
          <div className="card">
            <div className="card-title flex-between" style={{display:'flex',justifyContent:'space-between',alignItems:'center'}}>
              <span>Email Drafts</span>
              <span className="tag">{result.action_plan.email_drafts.length} drafts</span>
            </div>

            {result.action_plan.email_drafts.length === 0 && (
              <div className="empty-state" style={{padding:'24px'}}>
                <div className="empty-state-text">No emails needed — cash flow is healthy.</div>
              </div>
            )}

            {result.action_plan.email_drafts.map((email, i) => (
              <div key={i} className="email-card">
                <div className="email-header">
                  <div>
                    <div className="email-subject">{email.subject}</div>
                    <div className="email-meta">
                      To: {email.recipient_name} ({email.recipient_type}) · Tone: {email.tone}
                    </div>
                  </div>
                  <div className="flex-gap">
                    <button
                      className="btn btn-outline"
                      style={{padding:'6px 14px',fontSize:12}}
                      onClick={() => setActiveEmail(activeEmail === i ? null : i)}
                    >
                      {activeEmail === i ? 'Hide' : 'Preview'}
                    </button>
                    <button
                      className="btn btn-primary"
                      style={{padding:'6px 14px',fontSize:12}}
                      onClick={() => copyEmail(email.body, i)}
                    >
                      {copied === i ? '✓ Copied' : 'Copy'}
                    </button>
                  </div>
                </div>
                {activeEmail === i && (
                  <div className="email-body">{email.body}</div>
                )}
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
