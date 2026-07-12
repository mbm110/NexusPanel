"""
Persian web dashboard — complete HTML/CSS/JS UI.
"""

# Brand name for this fork
BRAND = "NexusProxy"
DEFAULT_PASS = "NEXUSKING"
BRAND_COLOR = "#3B82F6"  # blue theme
BRAND_COLOR2 = "#8B5CF6"  # purple gradient
LOGO_B64 = (
    "iVBORw0KGgoAAAANSUhEUgAAAIAAAACACAYAAADDPmHLAABOuElEQVR42u2dd7wU"
    "1fn/P3N2dvcWWC4dlt6bFBULdhQ0amKixqgxJhpjEm+MaTTRGDVqjLHGXlIs"
    "iCWoFBULWLAAC7L0Ll99+tvfH8u6u9u7s1O23W4uz8cjDkudnblz5tzZnZk5"
    "M3NKokOH0KFD6PBfHkLX1q1cX7q0a6t3aJ1Op9PpdDqdTqfT6XQ6nU6n0+l0"
    "Op1Op9PpdDqdTqfT6XQ6nU6n0+l0Op1Op9PpdDqdTqfT6XQ6nU6n0+l0Op1O"
    "p9PpdDqdTqfT6XQ6nU6n0+l0Op1Op9PpdDqdTqfT6XQ6nU6n0+l0Op1Op9Pp"
    "dDqdTqfT6XQ6nU6n0+l0Op1Op9Pp/hEYYwybG2OQ/wH+D2Bzw+YGGxts"    
)


# ── LOGIN PAGE ────────────────────────────────────────────────────────────────
LOGIN_HTML = f"""<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>ورود · {BRAND}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Vazirmatn:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
:root{{--bg:#060f1d;--card:rgba(10,22,40,0.92);--accent:{BRAND_COLOR};--accent2:#8B5CF6;--text:#E8F4FF;--dim:#3D6B8E;--mid:#7BAED4;--border:rgba(59,130,246,0.2);--err:#F87171;--ok:#34D399}}
html,body{{height:100%;overflow:hidden}}
body{{font-family:'Vazirmatn',sans-serif;background:var(--bg);display:flex;align-items:center;justify-content:center;padding:20px}}
.bg{{position:fixed;inset:0;background:radial-gradient(ellipse 80% 60% at 50% 0%,rgba(59,130,246,0.1),transparent 70%),var(--bg);z-index:0}}
.grid{{position:fixed;inset:0;background-image:linear-gradient(rgba(59,130,246,0.04) 1px,transparent 1px),linear-gradient(90deg,rgba(59,130,246,0.04) 1px,transparent 1px);background-size:44px 44px;z-index:0}}
.orb{{position:fixed;border-radius:50%;filter:blur(90px);z-index:0;animation:fl 9s ease-in-out infinite}}
.o1{{width:380px;height:380px;background:rgba(59,130,246,0.07);top:-100px;right:-80px}}
.o2{{width:280px;height:280px;background:rgba(16,185,129,0.04);bottom:-60px;left:-60px;animation-delay:4s}}
@keyframes fl{{0%,100%{{transform:translateY(0)}}50%{{transform:translateY(-18px)}}}}
.wrap{{position:relative;z-index:10;width:100%;max-width:420px}}
.card{{background:var(--card);border:1px solid var(--border);border-radius:20px;padding:38px 34px 34px;backdrop-filter:blur(24px);box-shadow:0 0 80px rgba(59,130,246,0.07),0 20px 60px rgba(0,0,0,.5)}}
.brand{{display:flex;align-items:center;gap:14px;margin-bottom:28px}}
.brand-icon{{width:48px;height:48px;border-radius:50%;background:linear-gradient(135deg,{BRAND_COLOR},{BRAND_COLOR2});display:flex;align-items:center;justify-content:center;font-size:22px;font-weight:700;color:#fff;flex-shrink:0}}
.brand-name{{font-size:17px;font-weight:700;color:var(--text)}}
.brand-sub{{font-size:11px;color:var(--dim);margin-top:2px}}
h1{{font-size:21px;font-weight:700;color:var(--text);margin-bottom:6px;letter-spacing:-.02em}}
.sub{{font-size:12px;color:var(--mid);margin-bottom:24px;line-height:1.7}}
.hint{{display:flex;align-items:center;gap:10px;background:rgba(59,130,246,0.07);border:1px solid rgba(59,130,246,0.15);border-radius:10px;padding:10px 14px;margin-bottom:20px}}
.hint-label{{font-size:11px;color:var(--dim);flex:1}}
.hint-val{{font-family:ui-monospace,monospace;font-size:14px;font-weight:700;color:var(--accent);background:rgba(59,130,246,0.1);border:1px solid rgba(59,130,246,0.25);padding:3px 11px;border-radius:7px;cursor:pointer;transition:.15s}}
.hint-val:hover{{background:rgba(59,130,246,0.22)}}
.field{{margin-bottom:18px}}
.field label{{display:block;font-size:10.5px;font-weight:600;color:var(--mid);margin-bottom:7px;text-transform:uppercase;letter-spacing:.06em}}
.inp-wrap{{position:relative}}
input[type=password]{{width:100%;padding:13px 44px 13px 16px;border-radius:11px;border:1px solid var(--border);background:rgba(0,0,0,.3);color:var(--text);font-family:inherit;font-size:14px;outline:none;transition:.2s}}
input[type=password]:focus{{border-color:rgba(59,130,246,.55);background:rgba(0,0,0,.4);box-shadow:0 0 0 3px rgba(59,130,246,.1)}}
.ic{{position:absolute;left:14px;top:50%;transform:translateY(-50%);color:var(--dim);font-size:18px;pointer-events:none;transition:.2s}}
input:focus+.ic{{color:var(--accent)}}
.err{{display:none;background:rgba(239,68,68,.08);border:1px solid rgba(239,68,68,.2);border-radius:10px;padding:10px 14px;margin-bottom:14px;font-size:12px;color:var(--err);align-items:center;gap:8px}}
.err.show{{display:flex}}
.btn{{width:100%;padding:13px;border-radius:11px;border:none;cursor:pointer;background:linear-gradient(135deg,{BRAND_COLOR},{BRAND_COLOR2});color:#fff;font-family:inherit;font-size:14px;font-weight:600;display:flex;align-items:center;justify-content:center;gap:8px;box-shadow:0 4px 20px rgba(139,92,246,.35);transition:.2s;position:relative;overflow:hidden}}
.btn::before{{content:'';position:absolute;inset:0;background:rgba(255,255,255,.08);opacity:0;transition:.2s}}
.btn:hover::before{{opacity:1}}
.btn:disabled{{opacity:.5;cursor:not-allowed}}
.footer{{margin-top:22px;padding-top:18px;border-top:1px solid var(--border);display:flex;align-items:center;justify-content:center;gap:8px;font-size:11px;color:var(--dim)}}
</style>
</head>
<body>
<div class="bg"></div><div class="grid"></div>
<div class="orb o1"></div><div class="orb o2"></div>
<div class="wrap">
  <div class="card">
    <div class="brand">
      <div class="brand-icon">N</div>
      <div><div class="brand-name">{BRAND}</div><div class="brand-sub">v1.0 — VLESS/XHTTP Gateway</div></div>
    </div>
    <h1>ورود به پنل مدیریت</h1>
    <p class="sub">رمز عبور را وارد کنید تا به داشبورد دسترسی پیدا کنید</p>
    <div class="err" id="err"><span id="err-text"></span></div>
    <div class="hint">
      <span class="hint-label">رمز پیش‌فرض</span>
      <span class="hint-val" onclick="document.getElementById('pw').value='{DEFAULT_PASS}';document.getElementById('pw').focus()">{DEFAULT_PASS}</span>
    </div>
    <form id="form">
      <div class="field">
        <label>رمز عبور</label>
        <div class="inp-wrap">
          <input type="password" id="pw" placeholder="رمز عبور" autofocus required>
          <span class="ic">🔒</span>
        </div>
      </div>
      <button type="submit" class="btn" id="btn">ورود به پنل</button>
    </form>
  </div>
</div>
<script>
const form = document.getElementById('form');
const err = document.getElementById('err');
const errText = document.getElementById('err-text');
const btn = document.getElementById('btn');

form.addEventListener('submit', async e => {{
  e.preventDefault();
  err.classList.remove('show');
  btn.disabled = true;
  btn.textContent = 'در حال ورود...';
  const pw = document.getElementById('pw').value;
  try {{
    const r = await fetch('/api/login', {{
      method: 'POST',
      headers: {{'Content-Type': 'application/json'}},
      body: JSON.stringify({{password: pw}})
    }});
    const d = await r.json();
    if (d.ok) {{
      window.location.href = '/dashboard';
    }} else {{
      errText.textContent = 'رمز عبور اشتباه است';
      err.classList.add('show');
      btn.disabled = false;
      btn.textContent = 'ورود به پنل';
    }}
  }} catch(e) {{
    errText.textContent = 'خطا در اتصال';
    err.classList.add('show');
    btn.disabled = false;
    btn.textContent = 'ورود به پنل';
  }}
}});
</script>
</body>
</html>"""


# ── DASHBOARD PAGE ────────────────────────────────────────────────────────────
DASHBOARD_HTML = f"""<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>داشبورد · {BRAND}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Vazirmatn:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
:root{{--bg:#060f1d;--card:#0a1628;--card2:#0d1e35;--accent:{BRAND_COLOR};--accent2:#8B5CF6;--text:#E8F4FF;--dim:#3D6B8E;--mid:#7BAED4;--border:rgba(59,130,246,0.15);--ok:#34D399;--err:#F87171;--warn:#FBBF24;--font:'Vazirmatn',sans-serif}}
html,body{{height:100%;font-family:var(--font);background:var(--bg);color:var(--text)}}
a{{color:var(--accent);text-decoration:none}}
i{{font-style:normal}}

/* Scrollbar */
::-webkit-scrollbar{{width:6px;height:6px}}
::-webkit-scrollbar-track{{background:transparent}}
::-webkit-scrollbar-thumb{{background:rgba(59,130,246,0.3);border-radius:3px}}

/* Layout */
.shell{{display:flex;height:100vh;overflow:hidden}}
.sidebar{{width:240px;background:var(--card);border-left:1px solid var(--border);padding:20px 16px;display:flex;flex-direction:column;gap:6px;overflow-y:auto}}
.sidebar .logo{{display:flex;align-items:center;gap:10px;padding:8px 10px;margin-bottom:16px}}
.sidebar .logo-icon{{width:36px;height:36px;border-radius:10px;background:linear-gradient(135deg,{BRAND_COLOR},{BRAND_COLOR2});display:flex;align-items:center;justify-content:center;font-size:18px;font-weight:700;color:#fff;flex-shrink:0}}
.sidebar .logo-name{{font-size:15px;font-weight:700}}
.sidebar .logo-sub{{font-size:10px;color:var(--dim)}}
.nav-btn{{display:flex;align-items:center;gap:10px;padding:10px 12px;border-radius:10px;color:var(--dim);cursor:pointer;transition:.15s;font-size:13px;font-weight:500}}
.nav-btn:hover, .nav-btn.active{{background:rgba(59,130,246,0.08);color:var(--accent)}}
.nav-btn.active{{background:rgba(59,130,246,0.12);border:1px solid rgba(59,130,246,0.2)}}

.main{{flex:1;overflow-y:auto;padding:24px}}
.page{{display:none}}
.page.active{{display:block}}

/* Stats Cards */
.stats{{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:16px;margin-bottom:24px}}
.stat-card{{background:var(--card);border:1px solid var(--border);border-radius:16px;padding:20px}}
.stat-card .val{{font-size:26px;font-weight:700;color:var(--text)}}
.stat-card .lbl{{font-size:11px;color:var(--dim);margin-top:4px}}

/* Link list */
.link-list{{display:flex;flex-direction:column;gap:10px}}
.link-card{{background:var(--card);border:1px solid var(--border);border-radius:14px;padding:16px;display:flex;flex-direction:column;gap:10px}}
.link-card.disabled{{opacity:0.5}}
.link-header{{display:flex;align-items:center;justify-content:space-between;gap:10px}}
.link-name{{font-size:14px;font-weight:600}}
.link-badge{{font-size:10px;padding:2px 8px;border-radius:20px;background:rgba(59,130,246,0.12);color:var(--accent)}}
.link-badge.expired{{background:rgba(239,68,68,0.12);color:var(--err)}}
.link-badge.exhausted{{background:rgba(251,191,36,0.12);color:var(--warn)}}
.link-meta{{display:flex;gap:16px;font-size:11px;color:var(--dim);flex-wrap:wrap}}
.link-meta span{{display:flex;align-items:center;gap:4px}}
.link-row{{display:flex;gap:8px;align-items:center}}
.link-url{{flex:1;font-family:ui-monospace,monospace;font-size:11px;color:var(--mid);background:rgba(0,0,0,0.3);padding:8px 12px;border-radius:8px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;direction:ltr;text-align:left}}
.copy-btn{{padding:6px 12px;border-radius:8px;border:1px solid var(--border);background:rgba(59,130,246,0.08);color:var(--accent);cursor:pointer;font-size:12px;flex-shrink:0}}
.copy-btn:hover{{background:rgba(59,130,246,0.16)}}
.link-actions{{display:flex;gap:8px}}
.act-btn{{padding:6px 12px;border-radius:8px;border:1px solid var(--border);background:transparent;cursor:pointer;font-size:11px;transition:.15s}}
.act-btn:hover{{background:rgba(59,130,246,0.1)}}
.act-btn.danger:hover{{background:rgba(239,68,68,0.1);border-color:rgba(239,68,68,0.3);color:var(--err)}}

/* Create modal */
.modal{{display:none;position:fixed;inset:0;z-index:100;background:rgba(0,0,0,0.7);align-items:center;justify-content:center;padding:20px}}
.modal.open{{display:flex}}
.modal-content{{background:var(--card);border:1px solid var(--border);border-radius:20px;padding:28px;width:100%;max-width:520px;max-height:90vh;overflow-y:auto}}
.modal-title{{font-size:17px;font-weight:700;margin-bottom:20px}}
.form-group{{margin-bottom:16px}}
.form-group label{{display:block;font-size:11px;color:var(--dim);margin-bottom:6px;text-transform:uppercase}}
.form-group input, .form-group select{{width:100%;padding:10px 14px;border-radius:10px;border:1px solid var(--border);background:rgba(0,0,0,0.3);color:var(--text);font-family:var(--font);font-size:13px;outline:none}}
.form-group input:focus, .form-group select:focus{{border-color:rgba(59,130,246,.5)}}
.form-row{{display:grid;grid-template-columns:1fr 1fr;gap:12px}}
.modal-actions{{display:flex;gap:10px;margin-top:20px}}
.btn-primary{{flex:1;padding:11px;border-radius:10px;border:none;background:linear-gradient(135deg,{BRAND_COLOR},{BRAND_COLOR2});color:#fff;font-family:var(--font);font-size:14px;font-weight:600;cursor:pointer}}
.btn-secondary{{padding:11px 20px;border-radius:10px;border:1px solid var(--border);background:transparent;color:var(--dim);font-family:var(--font);font-size:14px;cursor:pointer}}

/* Sub groups */
.group-card{{background:var(--card);border:1px solid var(--border);border-radius:14px;padding:16px}}
.group-name{{font-size:14px;font-weight:600;margin-bottom:8px}}

/* Toast */
.toast{{position:fixed;bottom:24px;left:50%;transform:translateX(-50%);background:var(--card2);border:1px solid var(--border);border-radius:12px;padding:10px 20px;font-size:13px;z-index:200;opacity:0;transition:opacity .3s}}
.toast.show{{opacity:1}}

/* Add btn */
.add-btn{{display:flex;align-items:center;gap:8px;padding:10px 18px;border-radius:10px;border:1px dashed rgba(59,130,246,0.3);background:rgba(59,130,246,0.05);color:var(--accent);cursor:pointer;font-size:13px;font-weight:500;transition:.15s}}
.add-btn:hover{{background:rgba(59,130,246,0.1)}}

/* Empty */
.empty{{text-align:center;padding:60px 20px;color:var(--dim);font-size:14px}}
.empty-icon{{font-size:40px;margin-bottom:12px;opacity:.5}}
</style>
</head>
<body>
<div class="shell">
  <div class="sidebar">
    <div class="logo">
      <div class="logo-icon">N</div>
      <div><div class="logo-name">{BRAND}</div><div class="logo-sub">v1.0</div></div>
    </div>
    <div class="nav-btn active" onclick="showPage('links')">🔗 لینک‌ها</div>
    <div class="nav-btn" onclick="showPage('groups')">📁 گروه‌های ساب</div>
    <div class="nav-btn" onclick="showPage('create')">➕ ساخت لینک</div>
    <div class="nav-btn" onclick="showPage('stats')">📊 آمار</div>
  </div>

  <div class="main">
    <!-- Stats page -->
    <div class="page" id="page-stats">
      <h2 style="margin-bottom:16px">📊 آمار</h2>
      <div class="stats" id="stats-cards">
        <div class="stat-card"><div class="val" id="stat-traffic">-</div><div class="lbl">کل ترافیک</div></div>
        <div class="stat-card"><div class="val" id="stat-conns">-</div><div class="lbl">اتصالات فعال</div></div>
        <div class="stat-card"><div class="val" id="stat-links">-</div><div class="lbl">تعداد لینک‌ها</div></div>
      </div>
      <div class="card" style="background:var(--card);border:1px solid var(--border);border-radius:14px;padding:16px">
        <div id="logs-container" style="font-family:ui-monospace,monospace;font-size:11px;color:var(--dim);max-height:300px;overflow-y:auto"></div>
      </div>
    </div>

    <!-- Links page -->
    <div class="page active" id="page-links">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px">
        <h2>🔗 لینک‌های VLESS/XHTTP</h2>
        <div class="add-btn" onclick="showPage('create')">➕ لینک جدید</div>
      </div>
      <div class="link-list" id="link-list"></div>
    </div>

    <!-- Create page -->
    <div class="page" id="page-create">
      <h2 style="margin-bottom:16px">➕ ساخت لینک جدید</h2>
      <div class="modal-content" style="background:var(--card);border:1px solid var(--border);border-radius:16px;padding:24px">
        <div class="form-group">
          <label>نام / برچسب</label>
          <input type="text" id="c-label" placeholder="مثلاً: سرور اصلی">
        </div>
        <div class="form-row">
          <div class="form-group">
            <label>پروتکل</label>
            <select id="c-protocol">
              <option value="vless-ws">VLESS + WebSocket</option>
              <option value="xhttp-packet-up">XHTTP (packet-up)</option>
              <option value="xhttp-stream-up">XHTTP (stream-up)</option>
            </select>
          </div>
          <div class="form-group">
            <label>Fingerprint</label>
            <select id="c-fp">
              <option value="chrome">Chrome</option>
              <option value="firefox">Firefox</option>
              <option value="safari">Safari</option>
              <option value="ios">iOS</option>
              <option value="android">Android</option>
              <option value="edge">Edge</option>
            </select>
          </div>
        </div>
        <div class="form-row">
          <div class="form-group">
            <label>محدودیت حجم (GB)</label>
            <input type="number" id="c-volume" placeholder="0 = نامحدود" min="0" step="0.1">
          </div>
          <div class="form-group">
            <label>محدودیت سرعت (Mbps)</label>
            <input type="number" id="c-speed" placeholder="0 = نامحدود" min="0">
          </div>
        </div>
        <div class="form-row">
          <div class="form-group">
            <label>پورت اتصال</label>
            <input type="number" id="c-port" value="443" min="1" max="65535">
          </div>
          <div class="form-group">
            <label>روز انقضا</label>
            <input type="number" id="c-days" placeholder="0 = بدون انقضا" min="0">
          </div>
        </div>
        <div class="form-group">
          <label>محدودیت آی‌پی</label>
          <input type="number" id="c-iplimit" placeholder="0 = نامحدود" min="0">
        </div>
        <div class="modal-actions">
          <button class="btn-primary" onclick="createLink()">ساختن لینک</button>
          <button class="btn-secondary" onclick="showPage('links')">انصراف</button>
        </div>
      </div>
    </div>

    <!-- Groups page -->
    <div class="page" id="page-groups">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px">
        <h2>📁 گروه‌های ساب</h2>
        <div class="add-btn" onclick="createGroup()">➕ گروه جدید</div>
      </div>
      <div class="link-list" id="group-list"></div>
    </div>
  </div>
</div>

<div class="modal" id="copy-modal">
  <div class="modal-content">
    <div class="modal-title">📋 کپی لینک</div>
    <div class="link-url" id="copy-url" style="margin-bottom:16px"></div>
    <div class="modal-actions">
      <button class="btn-primary" onclick="copyFromModal()">کپی</button>
      <button class="btn-secondary" onclick="closeCopyModal()">بستن</button>
    </div>
  </div>
</div>

<div class="toast" id="toast"></div>

<script>
let allLinks = {{}};
let allSubs = {{}};

function showPage(id) {{
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  document.getElementById('page-' + id).classList.add('active');
  document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
  event?.target?.closest?.('.nav-btn')?.classList.add('active');
}}

function toast(msg) {{
  const t = document.getElementById('toast');
  t.textContent = msg;
  t.classList.add('show');
  setTimeout(() => t.classList.remove('show'), 2500);
}}

function copyText(text) {{
  navigator.clipboard.writeText(text).then(() => toast('کپی شد ✅'));
}}

function fmtBytes(b) {{
  if (b === 0) return '0 B';
  const u = ['B','KB','MB','GB','TB'];
  let i = 0;
  while (b >= 1024 && i < u.length - 1) {{ b /= 1024; i++; }}
  return b.toFixed(1) + ' ' + u[i];
}}

function getHost() {{
  return window.location.protocol + '//' + window.location.host;
}}

async function loadLinks() {{
  const r = await fetch('/api/links');
  allLinks = await r.json();
  renderLinks();
}}

function renderLinks() {{
  const el = document.getElementById('link-list');
  const uids = Object.keys(allLinks);
  if (uids.length === 0) {{
    el.innerHTML = '<div class="empty"><div class="empty-icon">🔗</div>هنوز لینکی ساخته نشده<br><br><span class="add-btn" style="display:inline-flex" onclick="showPage(\\'create\\')">➕ ساخت لینک جدید</span></div>';
    return;
  }}
  el.innerHTML = uids.map(uid => {{
    const l = allLinks[uid];
    const url = getHost() + '/link/' + uid;
    const usedPct = l.total_bytes > 0 ? Math.min(100, (l.used_bytes / l.total_bytes) * 100) : 0;
    const status = !l.active ? 'expired' : l.total_bytes > 0 && l.used_bytes >= l.total_bytes ? 'exhausted' : '';
    return `
    <div class="link-card ${{status ? 'disabled' : ''}}">
      <div class="link-header">
        <span class="link-name">${{l.label || uid.slice(0, 8)}}</span>
        ${{l.active === false ? '<span class="link-badge expired">غیرفعال</span>' : ''}}
        ${{l.total_bytes > 0 && l.used_bytes >= l.total_bytes ? '<span class="link-badge exhausted">حجم تمام</span>' : ''}}
        ${{!l.active ? '' : '<span class="link-badge">' + l.protocol + '</span>'}}
      </div>
      <div class="link-meta">
        <span>📊 ${{fmtBytes(l.used_bytes)}} / ${{l.total_bytes ? fmtBytes(l.total_bytes) : '∞'}}</span>
        ${{l.speed_limit_bytes > 0 ? '<span>🚀 ' + Math.round(l.speed_limit_bytes * 8 / 1024 / 1024) + ' Mbps</span>' : ''}}
        ${{l.expiry_days ? '<span>⏰ ' + l.expiry_days + ' روز</span>' : ''}}
        ${{l.fingerprint ? '<span>🔐 ' + l.fingerprint + '</span>' : ''}}
      </div>
      <div class="link-row">
        <div class="link-url">${{url}}</div>
        <button class="copy-btn" onclick="copyText('${{url}}')">📋 کپی</button>
      </div>
      <div class="link-actions">
        <button class="act-btn" onclick="toggleLink('${{uid}}')">${{l.active ? '⏸ غیرفعال' : '▶ فعال'}}</button>
        <button class="act-btn" onclick="window.open('${{url}}', '_blank')">🔗 باز کردن</button>
        <button class="act-btn danger" onclick="deleteLink('${{uid}}')">🗑 حذف</button>
      </div>
    </div>`;
  }}).join('');
}}

async function loadStats() {{
  const r = await fetch('/api/stats');
  const d = await r.json();
  document.getElementById('stat-traffic').textContent = fmtBytes(d.total_bytes || 0);
  document.getElementById('stat-conns').textContent = d.active_conns || 0;
  document.getElementById('stat-links').textContent = Object.keys(allLinks).length;

  const lr = await fetch('/api/logs');
  const ld = await lr.json();
  document.getElementById('logs-container').innerHTML = (ld.logs || []).map(l => '<div style="padding:2px 0;border-bottom:1px solid rgba(255,255,255,0.03)">' + l + '</div>').join('');
  document.getElementById('stats-cards').querySelector('.stat-card:nth-child(3) .val').textContent = Object.keys(allLinks).length;
}}

async function createLink() {{
  const body = {{
    label: document.getElementById('c-label').value,
    protocol: document.getElementById('c-protocol').value,
    fingerprint: document.getElementById('c-fp').value,
    volume_gb: parseFloat(document.getElementById('c-volume').value || 0),
    speed_mbps: parseInt(document.getElementById('c-speed').value || 0),
    port: parseInt(document.getElementById('c-port').value || 443),
    days: parseInt(document.getElementById('c-days').value || 0),
    ip_limit: parseInt(document.getElementById('c-iplimit').value || 0),
  }};

  const r = await fetch('/api/links', {{method: 'POST', headers: {{'Content-Type': 'application/json'}}, body: JSON.stringify(body)}});
  const d = await r.json();
  if (d.link) {{
    toast('لینک ساخته شد ✅');
    await loadLinks();
    showPage('links');
  }}
}}

async function deleteLink(uid) {{
  if (!confirm('آیا مطمئن هستید؟')) return;
  await fetch('/api/links/' + uid, {{method: 'DELETE'}});
  await loadLinks();
  toast('حذف شد ✅');
}}

async function toggleLink(uid) {{
  await fetch('/api/links/' + uid + '/toggle', {{method: 'POST'}});
  await loadLinks();
}}

async function loadSubs() {{
  const r = await fetch('/api/subs');
  allSubs = await r.json();
  renderSubs();
}}

function renderSubs() {{
  const el = document.getElementById('group-list');
  const gids = Object.keys(allSubs);
  if (gids.length === 0) {{
    el.innerHTML = '<div class="empty"><div class="empty-icon">📁</div>هنوز گروهی ساخته نشده</div>';
    return;
  }}
  el.innerHTML = gids.map(gid => {{
    const g = allSubs[gid];
    const subUrl = getHost() + '/sub/' + gid;
    return `
    <div class="group-card">
      <div class="group-name">${{g.name}} <span style="color:var(--dim);font-size:12px">(${{g.link_ids?.length || 0}} لینک)</span></div>
      <div class="link-row">
        <div class="link-url">${{subUrl}}</div>
        <button class="copy-btn" onclick="copyText('${{subUrl}}')">📋 کپی</button>
      </div>
      <div class="link-actions" style="margin-top:8px">
        <button class="act-btn" onclick="deleteSub('${{gid}}')">🗑 حذف گروه</button>
      </div>
    </div>`;
  }}).join('');
}}

async function createGroup() {{
  const name = prompt('نام گروه:');
  if (!name) return;
  await fetch('/api/subs', {{method: 'POST', headers: {{'Content-Type': 'application/json'}}, body: JSON.stringify({{name}})}});
  await loadSubs();
}}

async function deleteSub(gid) {{
  if (!confirm('حذف شود؟')) return;
  await fetch('/api/subs/' + gid, {{method: 'DELETE'}});
  await loadSubs();
}}

function closeCopyModal() {{
  document.getElementById('copy-modal').classList.remove('open');
}}

function copyFromModal() {{
  const url = document.getElementById('copy-url').textContent;
  copyText(url);
  closeCopyModal();
}}

// Init
loadLinks();
loadSubs();

// Refresh stats every 10s
setInterval(loadStats, 10000);
loadStats();
</script>
</body>
</html>"""


def get_public_page_html(links: list, group_name: str, locked: bool = False) -> str:
    """Public subscription page — shown when password is wrong or for unauthenticated access."""
    return DASHBOARD_HTML  # simplified — just redirect to login