import { BrowserRouter, Routes, Route, NavLink, useLocation } from 'react-router-dom';
import {
  LayoutDashboard, TrendingUp, CreditCard, Users, Package,
  Mail, Upload, BookOpen, BarChart3, Landmark
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

const navItems = [
  { to: '/', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/cash-flow', icon: TrendingUp, label: 'Cash Flow' },
  { to: '/obligations', icon: CreditCard, label: 'Obligations' },
  { to: '/receivables', icon: Users, label: 'Receivables' },
  { to: '/inventory', icon: Package, label: 'Inventory' },
];

const actionItems = [
  { to: '/actions', icon: Mail, label: 'Actions & Emails' },
  { to: '/forecast', icon: BarChart3, label: 'Forecast' },
  { to: '/transactions', icon: Landmark, label: 'Transactions' },
  { to: '/ingest', icon: Upload, label: 'Upload Data' },
];

function Sidebar() {
  return (
    <nav className="sidebar">
      <div className="sidebar-logo">
        <div className="logo-mark">FinParvai</div>
        <div className="logo-sub">Financial Intelligence System</div>
      </div>
      <div className="sidebar-section-label">Overview</div>
      {navItems.map(({ to, icon: Icon, label }) => (
        <NavLink key={to} to={to} end className={({ isActive }) => `nav-item${isActive ? ' active' : ''}`}>
          <Icon className="nav-icon" strokeWidth={1.8} />
          {label}
        </NavLink>
      ))}
      <div className="sidebar-section-label">Tools</div>
      {actionItems.map(({ to, icon: Icon, label }) => (
        <NavLink key={to} to={to} className={({ isActive }) => `nav-item${isActive ? ' active' : ''}`}>
          <Icon className="nav-icon" strokeWidth={1.8} />
          {label}
        </NavLink>
      ))}
    </nav>
  );
}

function Topbar() {
  const location = useLocation();
  const all = [...navItems, ...actionItems];
  const current = all.find(n => {
    if (n.to === '/') return location.pathname === '/';
    return location.pathname.startsWith(n.to);
  });

  return (
    <div className="topbar">
      <div style={{ flex: 1 }}>
        <span style={{ fontWeight: 700, fontSize: 15, color: 'var(--text-primary)' }}>
          {current?.label || 'FinParvai'}
        </span>
        <span style={{ marginLeft: 12, fontSize: 12, color: 'var(--text-muted)' }}>
          Sri Lakshmi Garments · Chennai
        </span>
      </div>
      <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>
        {new Date().toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' })}
      </span>
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <div className="app-shell">
        <Sidebar />
        <div className="main-area">
          <Topbar />
          <div className="page-content">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/cash-flow" element={<CashFlow />} />
              <Route path="/obligations" element={<Obligations />} />
              <Route path="/receivables" element={<Receivables />} />
              <Route path="/inventory" element={<Inventory />} />
              <Route path="/actions" element={<Actions />} />
              <Route path="/forecast" element={<Forecast />} />
              <Route path="/transactions" element={<Transactions />} />
              <Route path="/ingest" element={<Ingest />} />
            </Routes>
          </div>
        </div>
      </div>
    </BrowserRouter>
  );
}
