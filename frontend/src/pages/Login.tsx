import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { LogIn, Eye, EyeOff, Shield, TrendingUp, BarChart3, Zap } from 'lucide-react';

const DEMO_EMAIL = 'demo@finparvai.com';
const DEMO_PASSWORD = 'finparvai2024';

const features = [
  { icon: TrendingUp, label: 'Cash Flow Intelligence', desc: 'Real-time covenant monitoring & alerts' },
  { icon: BarChart3, label: 'Predictive Forecasting', desc: 'AI-driven 90-day rolling projections' },
  { icon: Zap, label: 'Instant Decision Engine', desc: 'Deterministic action plans, instantly' },
];

export default function Login() {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [focusedField, setFocusedField] = useState<string | null>(null);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!email || !password) {
      setError('Please enter your email and password.');
      return;
    }

    setLoading(true);
    await new Promise(r => setTimeout(r, 1200)); // simulate auth

    if (email === DEMO_EMAIL && password === DEMO_PASSWORD) {
      sessionStorage.setItem('fp_auth', 'true');
      navigate('/upload');
    } else {
      setError('Invalid credentials. Use demo@finparvai.com / finparvai2024');
      setLoading(false);
    }
  };

  const fillDemo = () => {
    setEmail(DEMO_EMAIL);
    setPassword(DEMO_PASSWORD);
    setError('');
  };

  return (
    <div className="login-root">
      {/* Animated background orbs */}
      <div className="login-orb login-orb-1" />
      <div className="login-orb login-orb-2" />
      <div className="login-orb login-orb-3" />

      <div className={`login-shell ${mounted ? 'login-mounted' : ''}`}>
        {/* Left panel */}
        <div className="login-left">
          <div className="login-left-inner">
            <div className="login-brand">
              <div className="logo-mark" style={{ fontSize: 28, marginBottom: 6 }}>FinParvai</div>
              <div className="logo-sub" style={{ fontSize: 13 }}>Financial Intelligence System</div>
            </div>

            <div className="login-headline">
              <h1 className="login-title">
                Decision-grade<br />
                <span className="login-title-accent">financial clarity.</span>
              </h1>
              <p className="login-desc">
                AI-powered covenant monitoring, cash flow forecasting, and intelligent action plans — purpose-built for Indian SMEs.
              </p>
            </div>

            <div className="login-features">
              {features.map(({ icon: Icon, label, desc }) => (
                <div key={label} className="login-feature-row">
                  <div className="login-feature-icon">
                    <Icon size={15} strokeWidth={1.8} />
                  </div>
                  <div>
                    <div className="login-feature-label">{label}</div>
                    <div className="login-feature-desc">{desc}</div>
                  </div>
                </div>
              ))}
            </div>

            <div className="login-client-badge">
              <div className="login-client-dot" />
              <span>Sri Lakshmi Garments · Chennai</span>
            </div>
          </div>
        </div>

        {/* Right panel — form */}
        <div className="login-right">
          <div className="login-card glass-card">
            <div className="login-card-header">
              <div className="login-card-icon">
                <Shield size={20} strokeWidth={1.8} />
              </div>
              <div>
                <div style={{ fontWeight: 700, fontSize: 17, color: 'var(--text-primary)' }}>
                  Sign in
                </div>
                <div style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 2 }}>
                  Access your intelligence dashboard
                </div>
              </div>
            </div>

            <form onSubmit={handleLogin} className="login-form" noValidate>
              {/* Email */}
              <div className={`login-field ${focusedField === 'email' ? 'login-field-focused' : ''}`}>
                <label className="login-label" htmlFor="login-email">Email Address</label>
                <input
                  id="login-email"
                  type="email"
                  className="login-input"
                  placeholder="your@email.com"
                  value={email}
                  onChange={e => setEmail(e.target.value)}
                  onFocus={() => setFocusedField('email')}
                  onBlur={() => setFocusedField(null)}
                  autoComplete="email"
                />
              </div>

              {/* Password */}
              <div className={`login-field ${focusedField === 'password' ? 'login-field-focused' : ''}`}>
                <label className="login-label" htmlFor="login-password">Password</label>
                <div className="login-input-wrap">
                  <input
                    id="login-password"
                    type={showPassword ? 'text' : 'password'}
                    className="login-input login-input-padded"
                    placeholder="••••••••"
                    value={password}
                    onChange={e => setPassword(e.target.value)}
                    onFocus={() => setFocusedField('password')}
                    onBlur={() => setFocusedField(null)}
                    autoComplete="current-password"
                  />
                  <button
                    type="button"
                    className="login-eye-btn"
                    onClick={() => setShowPassword(v => !v)}
                    tabIndex={-1}
                    aria-label="Toggle password visibility"
                  >
                    {showPassword ? <EyeOff size={15} /> : <Eye size={15} />}
                  </button>
                </div>
              </div>

              {/* Error */}
              {error && (
                <div className="alert alert-danger" style={{ marginBottom: 0 }}>
                  <Shield size={14} />
                  <span>{error}</span>
                </div>
              )}

              {/* Submit */}
              <button
                id="login-submit"
                type="submit"
                className="btn btn-primary login-submit-btn"
                disabled={loading}
              >
                {loading ? (
                  <>
                    <span className="login-spinner" />
                    Authenticating…
                  </>
                ) : (
                  <>
                    <LogIn size={15} strokeWidth={2} />
                    Sign In
                  </>
                )}
              </button>

              {/* Demo hint */}
              <div className="login-demo-row">
                <span className="login-demo-text">New here?</span>
                <button
                  type="button"
                  className="login-demo-btn"
                  onClick={fillDemo}
                  id="login-demo-fill"
                >
                  Use demo credentials
                </button>
              </div>
            </form>

            <div className="login-card-footer">
              <Shield size={11} style={{ color: 'var(--text-muted)' }} />
              <span>256-bit encrypted · Session-only access · No data stored</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
