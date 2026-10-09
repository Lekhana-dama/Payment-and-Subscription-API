import React, { useEffect, useMemo, useState } from "react";
import {
  Activity, ArrowDownLeft, ArrowUpRight, BadgeCheck, CreditCard,
  FileText, Gauge, Layers3, LogIn, LogOut, RefreshCw, ShieldCheck,
  Sparkles, UserPlus, WalletCards
} from "lucide-react";

const API_BASE = (import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000").replace(/\/$/, "");

async function api(path, { token, ...options } = {}) {
  const headers = new Headers(options.headers || {});
  if (token) headers.set("Authorization", `Bearer ${token}`);
  if (options.body && !(options.body instanceof URLSearchParams) && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }
  const response = await fetch(`${API_BASE}${path}`, { ...options, headers });
  const text = await response.text();
  let data = null;
  try { data = text ? JSON.parse(text) : null; } catch { data = text; }
  if (!response.ok) {
    const detail = data?.detail || data?.message || `Request failed (${response.status})`;
    throw new Error(typeof detail === "string" ? detail : JSON.stringify(detail));
  }
  return data;
}

function money(value) {
  const n = Number(value);
  return Number.isFinite(n) ? new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR", maximumFractionDigits: 2 }).format(n) : "—";
}
function statusClass(value) {
  const v = String(value || "unknown").toLowerCase();
  if (["success", "active", "paid"].includes(v)) return "success";
  if (["pending", "processing"].includes(v)) return "pending";
  if (["failed", "cancelled", "inactive"].includes(v)) return "danger";
  return "neutral";
}
function Status({ value }) {
  return <span className={`status ${statusClass(value)}`}><span />{value || "Unknown"}</span>;
}
function Field({ label, ...props }) {
  return <label className="field"><span>{label}</span><input {...props} /></label>;
}
function Notice({ notice, onClose }) {
  if (!notice) return null;
  return <div className={`notice ${notice.type}`} role="status">
    <span>{notice.message}</span><button className="notice-close" onClick={onClose}>×</button>
  </div>;
}
function Empty({ title, detail }) {
  return <div className="empty"><div className="empty-icon"><Layers3 size={20}/></div><strong>{title}</strong><span>{detail}</span></div>;
}

export default function App() {
  const [token, setToken] = useState(() => sessionStorage.getItem("paymentapi_token") || "");
  const [userEmail, setUserEmail] = useState(() => sessionStorage.getItem("paymentapi_email") || "");
  const [authMode, setAuthMode] = useState("login");
  const [active, setActive] = useState("overview");
  const [notice, setNotice] = useState(null);
  const [busy, setBusy] = useState(false);
  const [plans, setPlans] = useState([]);
  const [payments, setPayments] = useState([]);
  const [subscriptions, setSubscriptions] = useState([]);
  const [invoices, setInvoices] = useState([]);
  const [invoiceLookupId, setInvoiceLookupId] = useState("");
  const [invoiceLookup, setInvoiceLookup] = useState(null);
  const [subscriptionLookupId, setSubscriptionLookupId] = useState("");
  const [subscriptionLookup, setSubscriptionLookup] = useState(null);
  const [register, setRegister] = useState({ username: "", email: "", password: "" });
  const [login, setLogin] = useState({ email: "", password: "" });
  const [paymentForm, setPaymentForm] = useState({ subscription_id: "", idempotency_key: "" });
  const [invoicePaymentId, setInvoicePaymentId] = useState("");
  const [selectedPlan, setSelectedPlan] = useState("");
  const [apiHealth, setApiHealth] = useState("checking");

  const authed = Boolean(token);
  const pendingPayments = useMemo(() => payments.filter(p => String(p.status).toLowerCase() === "pending").length, [payments]);
  const successfulPayments = useMemo(() => payments.filter(p => String(p.status).toLowerCase() === "success").length, [payments]);
  const totalPaid = useMemo(() => payments.filter(p => String(p.status).toLowerCase() === "success").reduce((sum, p) => sum + Number(p.amount || 0), 0), [payments]);

  const flash = (type, message) => {
    setNotice({ type, message });
    window.setTimeout(() => setNotice(null), 5500);
  };

  useEffect(() => {
    api("/").then(() => setApiHealth("online")).catch(() => setApiHealth("offline"));
    loadPlans();
  }, []);

  async function loadPlans() {
    try {
      const data = await api("/plans");
      setPlans(Array.isArray(data) ? data : []);
    } catch (e) {
      setPlans([]);
      setApiHealth("offline");
    }
  }

  async function refreshData() {
    if (!token) return;
    setBusy(true);
    try {
      const [pays] = await Promise.all([api("/payments/", { token })]);
      setPayments(Array.isArray(pays) ? pays : []);
      flash("success", "Payment history refreshed.");
    } catch (e) {
      flash("error", e.message);
    } finally {
      setBusy(false);
    }
  }

  async function submitRegister(e) {
    e.preventDefault(); setBusy(true);
    try {
      await api("/auth/register", { method: "POST", body: JSON.stringify(register) });
      flash("success", "Account created. Sign in with your email and password.");
      setAuthMode("login");
      setLogin({ email: register.email, password: "" });
    } catch (err) { flash("error", err.message); }
    finally { setBusy(false); }
  }

  async function submitLogin(e) {
    e.preventDefault(); setBusy(true);
    try {
      // OAuth2PasswordRequestForm expects form-urlencoded data. The backend maps "username" to email.
      const form = new URLSearchParams();
      form.set("username", login.email);
      form.set("password", login.password);
      const data = await api("/auth/login", {
        method: "POST",
        body: form,
        headers: { "Content-Type": "application/x-www-form-urlencoded" }
      });
      setToken(data.access_token);
      setUserEmail(login.email);
      sessionStorage.setItem("paymentapi_token", data.access_token);
      sessionStorage.setItem("paymentapi_email", login.email);
      flash("success", "Signed in successfully.");
      setActive("overview");
    } catch (err) { flash("error", err.message); }
    finally { setBusy(false); }
  }

  function logout() {
    setToken(""); setUserEmail("");
    sessionStorage.removeItem("paymentapi_token");
    sessionStorage.removeItem("paymentapi_email");
    setPayments([]); setSubscriptions([]); setInvoices([]);
    setActive("overview");
    flash("success", "You have been signed out.");
  }

  async function createSubscription(planId) {
    if (!token) { setActive("account"); flash("info", "Sign in first to create a subscription."); return; }
    setBusy(true);
    try {
      // SubscriptionCreate is expected to accept plan_id; adjust this body if your schema differs.
      const data = await api("/subscriptions", { token, method: "POST", body: JSON.stringify({ plan_id: Number(planId) }) });
      setSubscriptions(prev => [data, ...prev]);
      setSubscriptionLookup(data);
      setSubscriptionLookupId(String(data.id ?? ""));
      setPaymentForm(prev => ({ ...prev, subscription_id: String(data.id ?? ""), idempotency_key: crypto.randomUUID() }));
      flash("success", `Subscription created${data.id ? ` (#${data.id})` : ""}. Create a demo payment next.`);
      setActive("subscriptions");
    } catch (e) { flash("error", `Subscription request failed: ${e.message}. Check your SubscriptionCreate schema.`); }
    finally { setBusy(false); }
  }

  async function createPayment(e) {
    e.preventDefault(); setBusy(true);
    try {
      const key = paymentForm.idempotency_key.trim() || crypto.randomUUID();
      const data = await api("/payments", { token, method: "POST", body: JSON.stringify({
        subscription_id: Number(paymentForm.subscription_id),
        idempotency_key: key
      })});
      setPayments(prev => [data, ...prev.filter(p => p.id !== data.id)]);
      setPaymentForm(prev => ({ ...prev, idempotency_key: key }));
      flash("success", `Demo payment created${data.id ? ` (#${data.id})` : ""}. Use the success/fail controls to test the payment lifecycle.`);
      setActive("payments");
    } catch (e) { flash("error", e.message); }
    finally { setBusy(false); }
  }

  async function updatePayment(paymentId, outcome) {
    setBusy(true);
    try {
      const data = await api(`/payments/${paymentId}/${outcome}`, { token, method: "PATCH" });
      setPayments(prev => prev.map(p => p.id === paymentId ? data : p));
      flash("success", `Payment marked ${outcome}.`);
    } catch (e) { flash("error", e.message); }
    finally { setBusy(false); }
  }

  async function loadPayments() {
    setBusy(true);
    try {
      const data = await api("/payments/", { token });
      setPayments(Array.isArray(data) ? data : []);
    } catch (e) { flash("error", e.message); }
    finally { setBusy(false); }
  }

  async function lookupSubscription(e) {
    e.preventDefault(); setBusy(true);
    try {
      const data = await api(`/subscriptions/${Number(subscriptionLookupId)}`, { token });
      setSubscriptionLookup(data);
      setSubscriptions(prev => [data, ...prev.filter(x => x.id !== data.id)]);
    } catch (e) { setSubscriptionLookup(null); flash("error", e.message); }
    finally { setBusy(false); }
  }

  async function createInvoice(e) {
    e.preventDefault(); setBusy(true);
    try {
      const data = await api("/invoices/", { token, method: "POST", body: JSON.stringify({ payment_id: Number(invoicePaymentId) }) });
      setInvoiceLookup(data);
      setInvoices(prev => [data, ...prev.filter(x => x.id !== data.id)]);
      flash("success", `Invoice created${data.id ? ` (#${data.id})` : ""}.`);
    } catch (e) { flash("error", e.message); }
    finally { setBusy(false); }
  }

  async function lookupInvoice(e) {
    e.preventDefault(); setBusy(true);
    try {
      const data = await api(`/invoices/${Number(invoiceLookupId)}`, { token });
      setInvoiceLookup(data);
      setInvoices(prev => [data, ...prev.filter(x => x.id !== data.id)]);
    } catch (e) { setInvoiceLookup(null); flash("error", e.message); }
    finally { setBusy(false); }
  }

  const nav = [
    { id: "overview", label: "Overview", icon: Gauge },
    { id: "plans", label: "Plans", icon: Layers3 },
    { id: "subscriptions", label: "Subscriptions", icon: WalletCards },
    { id: "payments", label: "Payments", icon: CreditCard },
    { id: "invoices", label: "Invoices", icon: FileText },
    { id: "account", label: authed ? "Account" : "Sign in", icon: authed ? ShieldCheck : LogIn }
  ];

  return <div className="app-shell">
    <aside className="sidebar">
      <div className="brand"><div className="brand-mark"><Sparkles size={19}/></div><div><strong>PayPilot</strong><span>PAYMENTS PLATFORM</span></div></div>
      <div className="workspace-label">WORKSPACE</div>
      <nav>{nav.map(item => {
        const Icon = item.icon;
        return <button key={item.id} className={`nav-item ${active === item.id ? "active" : ""}`} onClick={() => {
          setActive(item.id);
          if (item.id === "payments" && token) loadPayments();
        }}><Icon size={18}/><span>{item.label}</span>{item.id === "payments" && payments.length > 0 && <small>{payments.length}</small>}</button>;
      })}</nav>
      <div className="sidebar-bottom">
        <div className="api-status"><span className={`pulse ${apiHealth}`}/><div><strong>Backend API</strong><span>{apiHealth === "online" ? "Connected" : apiHealth === "checking" ? "Checking connection…" : "Not reachable"}</span></div></div>
        <div className="api-url">API · {API_BASE}</div>
      </div>
    </aside>

    <main className="main">
      <header className="topbar">
        <div className="breadcrumb">Workspace <span>/</span> <strong>{nav.find(n => n.id === active)?.label || "Overview"}</strong></div>
        <div className="top-actions">
          <span className={`connection-chip ${apiHealth}`}><span/> {apiHealth === "online" ? "API online" : apiHealth === "checking" ? "Connecting" : "API offline"}</span>
          {authed ? <button className="user-chip" onClick={logout}><span className="avatar">{(userEmail || "U")[0].toUpperCase()}</span><span className="user-email">{userEmail}</span><LogOut size={15}/></button> : <button className="button button-primary button-small" onClick={() => setActive("account")}><LogIn size={15}/> Sign in</button>}
        </div>
      </header>

      <div className="content">
        <Notice notice={notice} onClose={() => setNotice(null)}/>

        {active === "overview" && <section>
          <div className="hero">
            <div><div className="eyebrow"><span className="eyebrow-dot"/> PAYMENT & SUBSCRIPTION API</div>
              <h1>Billing, without<br/><span>the busywork.</span></h1>
              <p>A clean control center for plans, subscriptions, demo payments, and invoices — powered by your FastAPI backend.</p>
              <div className="hero-actions"><button className="button button-primary" onClick={() => setActive("plans")}>Explore plans <ArrowUpRight size={16}/></button><button className="button button-ghost" onClick={() => { if (token) { loadPayments(); setActive("payments"); } else setActive("account"); }}>{token ? "View payments" : "Get started"} <ArrowDownLeft size={16}/></button></div>
            </div>
            <div className="hero-graphic"><div className="orbit orbit-one"/><div className="orbit orbit-two"/><div className="hero-card"><div className="hero-card-top"><span>PAYMENT OVERVIEW</span><span className="mini-dot"/></div><div className="hero-card-amount">{money(totalPaid)}</div><div className="hero-card-caption">Successful demo payments</div><div className="sparkline"><i/><i/><i/><i/><i/><i/><i/><i/><i/><i/><i/><i/></div><div className="hero-card-bottom"><span><BadgeCheck size={14}/> {successfulPayments} successful</span><span>{pendingPayments} pending</span></div></div><div className="floating-icon"><CreditCard size={22}/></div><div className="floating-badge"><Activity size={14}/> Live API</div></div>
          </div>
          <div className="section-heading"><div><div className="eyebrow muted">AT A GLANCE</div><h2>Your workspace</h2></div><button className="button button-light" onClick={() => { loadPlans(); if(token) loadPayments(); }}><RefreshCw size={15}/> Refresh</button></div>
          <div className="stats-grid">
            <Stat icon={Layers3} label="Available plans" value={plans.length} note="From your API" />
            <Stat icon={CreditCard} label="Payments" value={payments.length} note="Your payment history" />
            <Stat icon={BadgeCheck} label="Successful" value={successfulPayments} note="Completed demo payments" />
            <Stat icon={Activity} label="Total paid" value={money(totalPaid)} note="Successful payments only" />
          </div>
          <div className="bottom-grid">
            <div className="panel"><div className="panel-heading"><div><h3>Available plans</h3><p>Choose a plan to start a subscription.</p></div><button className="text-button" onClick={() => setActive("plans")}>View all <ArrowUpRight size={14}/></button></div>
              {plans.length ? <div className="mini-plan-list">{plans.slice(0, 3).map(p => <div className="mini-plan" key={p.id}><div className="plan-symbol"><Layers3 size={17}/></div><div className="mini-plan-name"><strong>{p.name || `Plan ${p.id}`}</strong><span>{p.billing_interval || "Billing interval not supplied"}</span></div><strong className="mini-price">{money(p.price)}</strong></div>)}</div> : <Empty title="No plans loaded" detail="Check that FastAPI is running and GET /plans returns plans."/>}
            </div>
            <div className="panel workflow-panel"><div className="panel-heading"><div><h3>Quick workflow</h3><p>Try the end-to-end demo flow.</p></div><div className="workflow-icon"><Sparkles size={17}/></div></div>
              <WorkflowStep number="01" title="Choose a plan" detail="Select a billing option" onClick={() => setActive("plans")}/>
              <WorkflowStep number="02" title="Create subscription" detail="Requires a signed-in account" onClick={() => setActive("subscriptions")}/>
              <WorkflowStep number="03" title="Test a demo payment" detail="Mark it success or failed" onClick={() => setActive("payments")}/>
              <WorkflowStep number="04" title="Generate invoice" detail="Use a payment ID" onClick={() => setActive("invoices")}/>
            </div>
          </div>
          <div className="footnote"><ShieldCheck size={15}/> Demo environment · No real money is charged.</div>
        </section>}

        {active === "plans" && <section>
          <PageTitle eyebrow="PRICING CATALOG" title="Plans that fit." description="Plans are loaded live from your FastAPI endpoint: GET /plans." action={<button className="button button-light" onClick={loadPlans}><RefreshCw size={15}/> Refresh plans</button>}/>
          {plans.length ? <div className="plans-grid">{plans.map((p, i) => <div className={`plan-card ${i === 1 ? "featured" : ""}`} key={p.id}>
            {i === 1 && <div className="popular-tag">POPULAR</div>}
            <div className="plan-card-icon"><Layers3 size={19}/></div><div className="plan-title">{p.name || `Plan ${p.id}`}</div><p className="plan-description">{p.description || "A subscription plan available through your API."}</p>
            <div className="plan-price">{money(p.price)}<span> / {p.billing_interval || "period"}</span></div>
            <div className="plan-rule"/>
            <div className="plan-feature"><BadgeCheck size={15}/> API-managed subscription</div><div className="plan-feature"><BadgeCheck size={15}/> Payment lifecycle tracking</div>
            <button className={`button ${i === 1 ? "button-primary" : "button-dark"}`} disabled={busy || p.is_active === false} onClick={() => createSubscription(p.id)}>{p.is_active === false ? "Inactive plan" : "Choose this plan"} <ArrowUpRight size={15}/></button>
            <div className="plan-id">PLAN ID · {p.id}</div>
          </div>)}</div> : <div className="panel"><Empty title="No plans found" detail="The frontend called GET /plans. Add a plan in Swagger or check the API connection."/></div>}
        </section>}

        {active === "subscriptions" && <section>
          <PageTitle eyebrow="SUBSCRIPTION MANAGEMENT" title="Your subscriptions." description="Create a subscription from a plan, or look up a subscription by ID."/>
          <div className="two-column">
            <div className="panel"><div className="panel-heading"><div><h3>Start a subscription</h3><p>Choose one of your active plans.</p></div><WalletCards size={20}/></div>
              {!authed ? <AuthPrompt onClick={() => setActive("account")}/> : plans.length ? <div className="subscription-options">{plans.filter(p => p.is_active !== false).map(p => <div className="subscription-option" key={p.id}><div><strong>{p.name || `Plan ${p.id}`}</strong><span>{money(p.price)} · {p.billing_interval || "period"}</span></div><button className="button button-primary button-small" disabled={busy} onClick={() => createSubscription(p.id)}>Subscribe</button></div>)}</div> : <Empty title="No active plans" detail="Load plans first from the Plans section."/>}
              {subscriptionLookup && <div className="result-card"><div className="result-heading"><strong>Subscription #{subscriptionLookup.id}</strong><Status value={subscriptionLookup.status}/></div><pre>{JSON.stringify(subscriptionLookup, null, 2)}</pre><button className="button button-light" onClick={() => {setPaymentForm({subscription_id: String(subscriptionLookup.id), idempotency_key: crypto.randomUUID()}); setActive("payments");}}>Create payment for this subscription</button></div>}
            </div>
            <div className="panel"><div className="panel-heading"><div><h3>Find a subscription</h3><p>Uses GET /subscriptions/{'{subscription_id}'}.</p></div><FileText size={20}/></div>
              {authed ? <form onSubmit={lookupSubscription}><Field label="Subscription ID" type="number" min="1" required value={subscriptionLookupId} onChange={e => setSubscriptionLookupId(e.target.value)} placeholder="e.g. 12"/><button className="button button-dark full" disabled={busy || !subscriptionLookupId}>Look up subscription <ArrowUpRight size={15}/></button></form> : <AuthPrompt onClick={() => setActive("account")}/>}
            </div>
          </div>
          <div className="info-callout"><Activity size={17}/><div><strong>Heads up</strong><span>This frontend sends <code>{'{ "plan_id": number }'}</code> when creating a subscription. If your SubscriptionCreate schema uses different fields, share that schema and we’ll align the request exactly.</span></div></div>
        </section>}

        {active === "payments" && <section>
          <PageTitle eyebrow="PAYMENT OPERATIONS" title="Payments, in control." description="Create a payment with an idempotency key, then test the success or failure lifecycle." action={<button className="button button-light" onClick={loadPayments} disabled={!authed || busy}><RefreshCw size={15}/> Refresh history</button>}/>
          {!authed ? <div className="panel"><AuthPrompt onClick={() => setActive("account")}/></div> : <div className="panel payment-create-panel">
            <div className="panel-heading"><div><h3>Create a demo payment</h3><p>POST /payments · authenticated</p></div><div className="payment-symbol"><CreditCard size={19}/></div></div>
            <form className="payment-form" onSubmit={createPayment}>
              <Field label="Subscription ID" type="number" min="1" required value={paymentForm.subscription_id} onChange={e => setPaymentForm({...paymentForm, subscription_id: e.target.value})} placeholder="ID of your pending subscription"/>
              <Field label="Idempotency key" value={paymentForm.idempotency_key} onChange={e => setPaymentForm({...paymentForm, idempotency_key: e.target.value})} placeholder="Unique key for this payment"/>
              <button className="button button-primary" disabled={busy}>{busy ? "Working…" : "Create payment"} <ArrowUpRight size={15}/></button>
              <button className="button button-light" type="button" onClick={() => setPaymentForm({...paymentForm, idempotency_key: crypto.randomUUID()})}>Generate key</button>
            </form>
            <div className="info-callout compact"><ShieldCheck size={16}/><span>This uses your demo provider. It does not charge a real card.</span></div>
          </div>}
          <div className="panel table-panel"><div className="panel-heading"><div><h3>Payment history</h3><p>{payments.length} payment{payments.length === 1 ? "" : "s"} returned by GET /payments/.</p></div></div>
            {!authed ? <Empty title="Sign in to view payments" detail="Payment history is protected by JWT authentication."/> : payments.length ? <div className="table-wrap"><table><thead><tr><th>Payment</th><th>Subscription</th><th>Amount</th><th>Status</th><th>Actions</th></tr></thead><tbody>{payments.map(p => <tr key={p.id}><td><strong>#{p.id}</strong><span className="cell-muted">{p.provider || "demo provider"}</span></td><td>{p.subscription_id ?? "—"}</td><td className="table-money">{money(p.amount)}</td><td><Status value={p.status}/></td><td><div className="row-actions">{String(p.status).toLowerCase() === "pending" ? <><button className="action-success" disabled={busy} onClick={() => updatePayment(p.id, "success")}>Mark success</button><button className="action-danger" disabled={busy} onClick={() => updatePayment(p.id, "failed")}>Mark failed</button></> : <button className="action-neutral" onClick={() => {setInvoicePaymentId(String(p.id)); setActive("invoices");}}>Create invoice</button>}</div></td></tr>)}</tbody></table></div> : <Empty title="No payments yet" detail="Create a subscription first, then create your first demo payment."/>}
          </div>
        </section>}

        {active === "invoices" && <section>
          <PageTitle eyebrow="BILLING DOCUMENTS" title="Invoices & records." description="Create an invoice from a payment ID, or retrieve an existing invoice."/>
          {!authed ? <div className="panel"><AuthPrompt onClick={() => setActive("account")}/></div> : <div className="two-column">
            <div className="panel"><div className="panel-heading"><div><h3>Generate invoice</h3><p>POST /invoices/</p></div><FileText size={20}/></div>
              <form onSubmit={createInvoice}><Field label="Payment ID" type="number" min="1" required value={invoicePaymentId} onChange={e => setInvoicePaymentId(e.target.value)} placeholder="ID of a payment"/><button className="button button-primary full" disabled={busy || !invoicePaymentId}>Create invoice <ArrowUpRight size={15}/></button></form>
            </div>
            <div className="panel"><div className="panel-heading"><div><h3>Find an invoice</h3><p>GET /invoices/{'{invoice_id}'}.</p></div><FileText size={20}/></div>
              <form onSubmit={lookupInvoice}><Field label="Invoice ID" type="number" min="1" required value={invoiceLookupId} onChange={e => setInvoiceLookupId(e.target.value)} placeholder="e.g. 7"/><button className="button button-dark full" disabled={busy || !invoiceLookupId}>Look up invoice <ArrowUpRight size={15}/></button></form>
            </div>
          </div>}
          {invoiceLookup && <div className="panel invoice-preview"><div className="invoice-paper"><div className="invoice-top"><div className="brand mini"><div className="brand-mark"><Sparkles size={15}/></div><strong>PayPilot</strong></div><span className="invoice-label">INVOICE</span></div><div className="invoice-number">Invoice #{invoiceLookup.id}</div><div className="invoice-subtitle">Generated from your Payment & Subscription API</div><div className="invoice-data">{Object.entries(invoiceLookup).map(([key, value]) => <div key={key}><span>{key.replaceAll("_", " ")}</span><strong>{String(value ?? "—")}</strong></div>)}</div><button className="button button-dark" onClick={() => window.print()}><FileText size={15}/> Print / Save PDF</button></div></div>}
          <div className="footnote"><ShieldCheck size={15}/> Invoice access is scoped to the authenticated user by your backend.</div>
        </section>}

        {active === "account" && <section>
          <PageTitle eyebrow="YOUR ACCOUNT" title={authed ? "You're signed in." : "Welcome back."} description={authed ? "Your JWT is attached to protected API requests from this browser session." : "Sign in or create an account to manage subscriptions, payments, and invoices."}/>
          {authed ? <div className="panel account-card"><div className="account-avatar">{(userEmail || "U")[0].toUpperCase()}</div><div className="account-details"><h3>{userEmail}</h3><p>Authenticated session · Bearer token</p><div className="security-line"><ShieldCheck size={16}/> Token stored in sessionStorage for this browser tab.</div></div><button className="button button-light" onClick={logout}><LogOut size={15}/> Sign out</button></div> :
            <div className="auth-layout"><div className="auth-aside"><div className="auth-emblem"><ShieldCheck size={28}/></div><h2>One account.<br/><span>Your billing hub.</span></h2><p>Authenticate against your existing FastAPI JWT endpoints. No mock login is used.</p><div className="auth-benefit"><BadgeCheck size={16}/> Protected endpoints use Bearer JWT</div><div className="auth-benefit"><BadgeCheck size={16}/> Your existing API handles authorization</div></div>
              <div className="auth-form-panel"><div className="auth-tabs"><button className={authMode === "login" ? "selected" : ""} onClick={() => setAuthMode("login")}><LogIn size={15}/> Sign in</button><button className={authMode === "register" ? "selected" : ""} onClick={() => setAuthMode("register")}><UserPlus size={15}/> Create account</button></div>
                {authMode === "login" ? <form onSubmit={submitLogin}><h3>Sign in to PayPilot</h3><p>Use the email and password registered with your API.</p><Field label="Email address" type="email" autoComplete="email" required value={login.email} onChange={e => setLogin({...login, email: e.target.value})} placeholder="you@example.com"/><Field label="Password" type="password" autoComplete="current-password" required value={login.password} onChange={e => setLogin({...login, password: e.target.value})} placeholder="Your password"/><button className="button button-primary full" disabled={busy}>{busy ? "Signing in…" : "Sign in"} <ArrowUpRight size={15}/></button></form> :
                <form onSubmit={submitRegister}><h3>Create your account</h3><p>Register through POST /auth/register.</p><Field label="Username" required value={register.username} onChange={e => setRegister({...register, username: e.target.value})} placeholder="Choose a username"/><Field label="Email address" type="email" required value={register.email} onChange={e => setRegister({...register, email: e.target.value})} placeholder="you@example.com"/><Field label="Password" type="password" minLength="8" required value={register.password} onChange={e => setRegister({...register, password: e.target.value})} placeholder="Create a password"/><button className="button button-primary full" disabled={busy}>{busy ? "Creating account…" : "Create account"} <ArrowUpRight size={15}/></button></form>}
              </div>
            </div>}
        </section>}
        <footer className="footer"><span>© 2026 PayPilot</span><span><span className={`footer-dot ${apiHealth}`}/> Connected to your FastAPI backend</span><span>Built for the PaymentAPI capstone</span></footer>
      </div>
    </main>
  </div>;
}

function Stat({ icon: Icon, label, value, note }) {
  return <div className="stat-card"><div className="stat-top"><span>{label}</span><div className="stat-icon"><Icon size={17}/></div></div><div className="stat-value">{value}</div><div className="stat-note">{note}</div></div>;
}
function PageTitle({ eyebrow, title, description, action }) {
  return <div className="page-title"><div><div className="eyebrow muted">{eyebrow}</div><h1>{title}</h1><p>{description}</p></div>{action}</div>;
}
function WorkflowStep({ number, title, detail, onClick }) {
  return <button className="workflow-step" onClick={onClick}><span className="step-number">{number}</span><span className="step-copy"><strong>{title}</strong><small>{detail}</small></span><ArrowUpRight size={15}/></button>;
}
function AuthPrompt({ onClick }) {
  return <div className="auth-prompt"><div className="prompt-icon"><ShieldCheck size={20}/></div><strong>Sign in required</strong><span>This operation requires a valid JWT from your FastAPI backend.</span><button className="button button-primary button-small" onClick={onClick}>Go to sign in <ArrowUpRight size={14}/></button></div>;
}
