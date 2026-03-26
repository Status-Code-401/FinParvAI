import { BrowserRouter, Routes, Route, NavLink, Navigate, useLocation, useNavigate } from 'react-router-dom';
import {
  LayoutDashboard, TrendingUp, CreditCard, Users, Package,
  Mail, Upload, BarChart3, Landmark, LogOut, ChevronRight, CalendarDays, Lock
} from 'lucide-react';
import Dashboard from './pages/Dashboard';
import CashFlow from './pages/CashFlow';
import Obligations from './pages/Obligations';
import Receivables from './pages/Receivables';
import Inventory from './pages/Inventory';
import Actions from './pages/Actions';
import Ingest from './pages/Ingest';
import Forecast from './pages/Forecast';
import Transactions from './pages/Transactions';
import CalendarDashboard from './pages/CalendarDashboard';
import Login from './pages/Login';

// ── Navigation structure — plain business English ────────────────────────────
const navItems = [
  { to: '/upload', icon: Upload,          label: 'Upload Documents',  sub: 'Start here',       gated: false },
  { to: '/',       icon: LayoutDashboard, label: 'My Dashboard',      sub: 'Financial health', gated: true },
  { to: '/money',  icon: TrendingUp,      label: 'Money In & Out',    sub: 'Cash flow',        gated: true },
  { to: '/bills',  icon: CreditCard,      label: 'Bills to Pay',      sub: 'Obligations',      gated: true },
  { to: '/owed',   icon: Users,           label: 'Money Owed to Me',  sub: 'Receivables',      gated: true },
  { to: '/stock',  icon: Package,         label: 'My Stock',          sub: 'Inventory',        gated: true },
];

const toolItems = [
  { to: '/actions',  icon: Mail,          label: 'What To Do Next',   sub: 'Actions & emails',   gated: true },
  { to: '/forecast', icon: BarChart3,     label: 'Money Forecast',    sub: '3-month outlook',    gated: true },
  { to: '/calendar', icon: CalendarDays,  label: 'Cash Calendar',     sub: 'Daily events',       gated: true },
  { to: '/history',  icon: Landmark,      label: 'Transaction Log',   sub: 'All transactions',   gated: true },
];

function isAuthed() {
  return sessionStorage.getItem('fp_auth') === 'true';
}

function isDataReady(): boolean {
  return sessionStorage.getItem('fp_data_ready') === 'true';
}

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  return isAuthed() ? <>{children}</> : <Navigate to="/login" replace />;
}

/** Wraps a gated page — NO LONGER REDIRECTS to allow mock view. */
function GatedRoute({ children }: { children: React.ReactNode }) {
  // Lock removed as per user request to allow dashboard access with mock data initially
  return <>{children}</>;
}

function Sidebar() {
  const navigate = useNavigate();
  const ready = isDataReady();

  const handleLogout = () => {
    sessionStorage.removeItem('fp_auth');
    sessionStorage.removeItem('fp_data_ready');
    navigate('/login');
  };

  const renderItem = (item: typeof navItems[0]) => {
    const { to, icon: Icon, label, sub, gated } = item;
    const locked = gated && !ready;

    if (locked && false) { // Forced false to unlock as per user request
      return (
        <div
          key={to}
          className="nav-item nav-item-locked"
          title="Upload your data first to unlock"
          style={{ cursor: 'not-allowed', opacity: 0.4, pointerEvents: 'none' }}
        >
          <Icon className="nav-icon" strokeWidth={1.8} />
          <div style={{ flex: 1, minWidth: 0 }}>
            <div style={{ lineHeight: 1.2 }}>{label}</div>
            <div style={{ fontSize: 10, color: 'var(--text-muted)', marginTop: 1 }}>{sub}</div>
          </div>
          <Lock size={12} color="var(--text-muted)" />
        </div>
      );
    }

    return (
      <NavLink
        key={to}
        to={to}
        end={to === '/'}
        className={({ isActive }) => `nav-item${isActive ? ' active' : ''}`}
      >
        <Icon className="nav-icon" strokeWidth={1.8} />
        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={{ lineHeight: 1.2 }}>{label}</div>
          <div style={{ fontSize: 10, color: 'var(--text-muted)', marginTop: 1 }}>{sub}</div>
        </div>
      </NavLink>
    );
  };

  return (
    <nav className="sidebar">
      <div className="sidebar-logo">
        <div className="logo-mark">FinParvai</div>
        <div className="logo-sub">Financial Intelligence</div>
      </div>

      <div className="sidebar-section-label">My Business</div>
      {navItems.map(renderItem)}

      <div className="sidebar-section-label">Tools</div>
      {toolItems.map(renderItem)}

      {/* {!ready && (
        <div style={{
          margin: '16px 12px', padding: '10px 12px', borderRadius: 8,
          background: 'rgba(79,142,247,0.08)', border: '1px solid rgba(79,142,247,0.2)',
          fontSize: 11, color: 'var(--accent)', lineHeight: 1.45, textAlign: 'center'
        }}>
          <Lock size={14} style={{ marginBottom: 4 }} /><br />
          Upload at least one document to unlock all dashboards
        </div>
      )} */}

      <div style={{ marginTop: 'auto', padding: '16px 8px 8px' }}>
        <button className="nav-item btn-ghost" style={{ width: '100%', border: 'none', cursor: 'pointer', background: 'none' }} onClick={handleLogout}>
          <LogOut className="nav-icon" strokeWidth={1.8} size={16} />
          <span style={{ fontSize: 13, fontWeight: 500, color: 'var(--text-secondary)' }}>Sign Out</span>
        </button>
      </div>
    </nav>
  );
}

function Topbar() {
  const location = useLocation();
  const all = [...navItems, ...toolItems];
  const current = all.find(n => {
    if (n.to === '/') return location.pathname === '/';
    return location.pathname.startsWith(n.to);
  });

  // Breadcrumb trail
  const isUpload = location.pathname === '/upload' || location.pathname === '/upload/';

  return (
    <div className="topbar">
      <div style={{ flex: 1, display: 'flex', alignItems: 'center', gap: 8 }}>
        <span style={{ fontWeight: 700, fontSize: 15, color: 'var(--text-primary)' }}>
          {current?.label || 'FinParvai'}
        </span>
        {current?.sub && (
          <>
            <ChevronRight size={14} color="var(--text-muted)" />
            <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>{current.sub}</span>
          </>
        )}
        {isUpload && (
          <span className="badge badge-info" style={{ marginLeft: 8, fontSize: 10 }}>Get Started Here</span>
        )}
      </div>
      <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
        <span style={{ fontSize: 12, color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: 6 }}>
          <span style={{ width: 6, height: 6, borderRadius: '50%', background: 'var(--success)', display: 'inline-block', boxShadow: '0 0 4px var(--success)' }} />
          Sri Lakshmi Garments · Chennai
        </span>
        <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>
          {new Date().toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' })}
        </span>
      </div>
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route
          path="/*"
          element={
            <ProtectedRoute>
              <div className="app-shell">
                <Sidebar />
                <div className="main-area">
                  <Topbar />
                  <div className="page-content">
                    <Routes>
                      <Route path="/upload"   element={<Ingest />} />
                      <Route path="/"         element={<GatedRoute><Dashboard /></GatedRoute>} />
                      <Route path="/money"    element={<GatedRoute><CashFlow /></GatedRoute>} />
                      <Route path="/bills"    element={<GatedRoute><Obligations /></GatedRoute>} />
                      <Route path="/owed"     element={<GatedRoute><Receivables /></GatedRoute>} />
                      <Route path="/stock"    element={<GatedRoute><Inventory /></GatedRoute>} />
                      <Route path="/actions"  element={<GatedRoute><Actions /></GatedRoute>} />
                      <Route path="/forecast" element={<GatedRoute><Forecast /></GatedRoute>} />
                      <Route path="/calendar" element={<GatedRoute><CalendarDashboard /></GatedRoute>} />
                      <Route path="/history"  element={<GatedRoute><Transactions /></GatedRoute>} />
                      {/* legacy aliases */}
                      <Route path="/cash-flow"    element={<Navigate to="/money"   replace />} />
                      <Route path="/obligations"  element={<Navigate to="/bills"   replace />} />
                      <Route path="/receivables"  element={<Navigate to="/owed"    replace />} />
                      <Route path="/inventory"    element={<Navigate to="/stock"   replace />} />
                      <Route path="/ingest"       element={<Navigate to="/upload"  replace />} />
                      <Route path="/transactions" element={<Navigate to="/history" replace />} />
                    </Routes>
                  </div>
                </div>
              </div>
            </ProtectedRoute>
          }
        />
      </Routes>
    </BrowserRouter>
  );
}
