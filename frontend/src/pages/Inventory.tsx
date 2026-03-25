import { useEffect, useState } from 'react';
import { getInventory } from '../services/api';
import { Package, AlertTriangle, CheckCircle, TrendingDown } from 'lucide-react';

const fmt = (n: number) => `₹${Number(n)?.toLocaleString('en-IN') ?? 0}`;

export default function Inventory() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getInventory().then(setData).finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="loading-center"><div className="spinner" /><span>Loading inventory…</span></div>;
  if (!data) return null;

  const { inventory_status, procurement_orders, optimization, total_inventory_value } = data;

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">Inventory & Procurement</h1>
        <p className="page-subtitle">Stock levels, shortages, and procurement orders</p>
      </div>

      <div className="kpi-grid" style={{ gridTemplateColumns: 'repeat(3, 1fr)', marginBottom: 20 }}>
        <div className="card">
          <div className="card-title">Total Inventory Value</div>
          <div className="card-value">{fmt(total_inventory_value)}</div>
        </div>
        <div className="card">
          <div className="card-title">Shortage Items</div>
          <div className="card-value" style={{ color: optimization.shortage_alerts?.length > 0 ? 'var(--danger)' : 'var(--success)' }}>
            {optimization.shortage_alerts?.length ?? 0}
          </div>
        </div>
        <div className="card">
          <div className="card-title">Liquidation Potential</div>
          <div className="card-value" style={{ color: 'var(--warning)' }}>{fmt(optimization.total_liquidation_value)}</div>
        </div>
      </div>

      {/* Shortage Alerts */}
      {optimization.shortage_alerts?.length > 0 && (
        <div className="card section-gap">
          <div style={{ fontWeight: 700, fontSize: 15, marginBottom: 12 }}>⚠️ Shortage Alerts</div>
          {optimization.shortage_alerts.map((a: any) => (
            <div key={a.item} className="alert alert-warning" style={{ marginBottom: 8 }}>
              <AlertTriangle size={16} />
              <strong>{a.item}</strong>: Shortage of {a.shortage} units ·{' '}
              <span className={`badge badge-${a.urgency === 'HIGH' ? 'danger' : 'warning'}`}>{a.urgency}</span>
            </div>
          ))}
        </div>
      )}

      {/* Inventory Table */}
      <div className="card section-gap">
        <div style={{ fontWeight: 700, fontSize: 15, marginBottom: 16 }}>Stock Status</div>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Item</th>
                <th>Available</th>
                <th>Required</th>
                <th>Status</th>
                <th>Shortage / Excess</th>
                <th>Unit Cost</th>
                <th>Total Value</th>
              </tr>
            </thead>
            <tbody>
              {inventory_status.map((item: any) => {
                const isShort = item.shortage > 0;
                const isExcess = item.excess > 0;
                return (
                  <tr key={item.item_id}>
                    <td>
                      <div style={{ fontWeight: 600 }}>{item.item}</div>
                      <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>{item.unit}</div>
                    </td>
                    <td style={{ fontWeight: 700 }}>{item.available_quantity?.toLocaleString()}</td>
                    <td>{item.required_quantity?.toLocaleString()}</td>
                    <td>
                      {isShort && <span className="badge badge-danger">Shortage</span>}
                      {isExcess && <span className="badge badge-warning">Excess</span>}
                      {!isShort && !isExcess && <span className="badge badge-success">OK</span>}
                    </td>
                    <td>
                      {isShort && <span style={{ color: 'var(--danger)', fontWeight: 700 }}>-{item.shortage}</span>}
                      {isExcess && <span style={{ color: 'var(--warning)', fontWeight: 700 }}>+{item.excess}</span>}
                      {!isShort && !isExcess && <span style={{ color: 'var(--success)' }}>—</span>}
                    </td>
                    <td>₹{item.unit_cost}</td>
                    <td>{fmt(item.total_value)}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Procurement Orders */}
      <div className="card section-gap">
        <div style={{ fontWeight: 700, fontSize: 15, marginBottom: 16 }}>Procurement Orders</div>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Order ID</th>
                <th>Vendor</th>
                <th>Material</th>
                <th>Qty</th>
                <th>Total Cost</th>
                <th>Expected Delivery</th>
                <th>Status</th>
                <th>Payment</th>
              </tr>
            </thead>
            <tbody>
              {procurement_orders.map((po: any) => (
                <tr key={po.order_id}>
                  <td style={{ fontFamily: 'monospace', fontSize: 12 }}>{po.order_id}</td>
                  <td style={{ fontWeight: 600 }}>{po.vendor}</td>
                  <td>{po.material}</td>
                  <td>{po.quantity?.toLocaleString()}</td>
                  <td style={{ fontWeight: 700 }}>{fmt(po.total_cost)}</td>
                  <td>{po.expected_delivery || po.actual_delivery || '—'}</td>
                  <td>
                    <span className={`badge ${po.status === 'delivered' ? 'badge-success' : po.status === 'in_transit' ? 'badge-warning' : 'badge-info'}`}>
                      {po.status}
                    </span>
                  </td>
                  <td>
                    <span className={`badge ${po.payment_status === 'paid' ? 'badge-success' : 'badge-danger'}`}>
                      {po.payment_status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Liquidation */}
      {optimization.liquidation_candidates?.length > 0 && (
        <div className="card section-gap">
          <div style={{ fontWeight: 700, fontSize: 15, marginBottom: 12 }}>💰 Liquidation Opportunities</div>
          {optimization.liquidation_candidates.map((item: any) => (
            <div key={item.item} style={{
              display: 'flex', justifyContent: 'space-between', alignItems: 'center',
              padding: '10px 0', borderBottom: '1px solid var(--border)'
            }}>
              <div>
                <div style={{ fontWeight: 600 }}>{item.item}</div>
                <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>{item.excess} excess units</div>
              </div>
              <div style={{ textAlign: 'right' }}>
                <div style={{ fontWeight: 700, color: 'var(--warning)' }}>{fmt(item.liquidation_value)}</div>
                <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>potential recovery</div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
