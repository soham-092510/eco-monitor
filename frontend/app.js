// ===========================
// ECO MONITOR — APP.JS
// API integration + UI logic
// ===========================

const API = 'http://localhost:8000';
let token = localStorage.getItem('eco_token') || null;
let currentUser = JSON.parse(localStorage.getItem('eco_user') || 'null');

// ===========================
// INIT
// ===========================

document.addEventListener('DOMContentLoaded', () => {
  if (token && currentUser) {
    showDashboard();
  } else {
    showAuth();
  }
});

// ===========================
// AUTH HELPERS
// ===========================

function showAuth() {
  document.getElementById('auth-page').classList.remove('hidden');
  document.getElementById('dashboard-page').classList.add('hidden');
}

function showDashboard() {
  document.getElementById('auth-page').classList.add('hidden');
  document.getElementById('dashboard-page').classList.remove('hidden');

  // Set user info
  const name = currentUser?.username || currentUser?.name || 'User';
  document.getElementById('topbar-username').textContent = name;
  document.getElementById('user-initial').textContent = name[0].toUpperCase();

  // Load default section
loadSection("overview");

if (!window.dashboardRefresh) {

    window.dashboardRefresh = setInterval(() => {

        loadOverview();

    },30000);

}
}

function switchTab(tab) {
  document.getElementById('login-form').classList.toggle('hidden', tab !== 'login');
  document.getElementById('register-form').classList.toggle('hidden', tab !== 'register');
  document.getElementById('login-tab').classList.toggle('active', tab === 'login');
  document.getElementById('register-tab').classList.toggle('active', tab === 'register');
}

// ===========================
// Logout current user
// Clears local storage and redirects
// ===========================

function logout() {

    localStorage.removeItem("eco_token");
    localStorage.removeItem("eco_user");

    token = null;
    currentUser = null;

    showToast("Logged out successfully.");

    showAuth();

}

// ===========================
// AUTH: LOGIN
// ===========================

async function handleLogin(e) {
  e.preventDefault();
  const btn = document.getElementById('login-btn');
  const errEl = document.getElementById('login-error');
  errEl.classList.add('hidden');
  // Show loading state while login request is in progress
btn.innerHTML = "⏳ Logging in...";
btn.disabled = true;

  const username = document.getElementById('login-username').value;
  const password = document.getElementById('login-password').value;

  try {
    // FastAPI OAuth2 form login
    const formData = new FormData();
    formData.append('username', username);
    formData.append('password', password);

    const res = await fetch(`${API}/auth/login`, {
      method: 'POST',
      body: formData
    });

    const data = await res.json();

    if (!res.ok) {
      throw new Error(data.detail || 'Login failed');
    }

    token = data.access_token;
    currentUser = { username };
    localStorage.setItem('eco_token', token);
    localStorage.setItem('eco_user', JSON.stringify(currentUser));
    showDashboard();

showToast("Login successful.");

  } catch(err){

errEl.textContent=err.message;

errEl.classList.remove("hidden");

showToast(err.message,"error");

} finally {
    btn.innerHTML = "Login";
    btn.disabled = false;
  }
}

// ===========================
// AUTH: REGISTER
// ===========================

async function handleRegister(e) {
  e.preventDefault();
  const btn = document.getElementById('register-btn');
  const errEl = document.getElementById('register-error');
  errEl.classList.add('hidden');
  btn.innerHTML = "⏳ Creating Account...";
  btn.disabled = true;

  try {
    const res = await fetch(`${API}/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        name: document.getElementById('reg-name').value,
        username: document.getElementById('reg-username').value,
        email: document.getElementById('reg-email').value,
        password: document.getElementById('reg-password').value
      })
    });

    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Registration failed');

    // Auto-login after register
    currentUser = { username: document.getElementById('reg-username').value };
    if (data.access_token) {

    token = data.access_token;

    localStorage.setItem("eco_token", token);

    localStorage.setItem("eco_user", JSON.stringify(currentUser));

    showToast("Registration successful.");

    showDashboard();

} else {
      // Switch to login tab
      switchTab('login');
      document.getElementById('login-username').value = currentUser.username;
    }

  } catch (err) {
    errEl.textContent = err.message;
    errEl.classList.remove('hidden');
  } finally {
    btn.innerHTML = "Create Account";
    btn.disabled = false;
  }
}

// ===========================
// NAVIGATION
// ===========================

function showSection(name, el) {
  // Update active nav
  document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
  if (el) el.classList.add('active');

  // Hide all sections
  document.querySelectorAll('.section').forEach(s => s.classList.add('hidden'));
  document.getElementById(`section-${name}`).classList.remove('hidden');

  // Update title
  const titles = {
    overview:  ['Overview', "Welcome back! Here's your sustainability summary."],
    carbon:    ['Carbon Tracker', 'Track and log your carbon emission records.'],
    credits:   ['Carbon Credits', 'Manage and view your carbon credit balance.'],
    ledger:    ['Transaction Ledger', 'View all financial and carbon transactions.'],
    portfolio: ['Portfolio', 'Your complete sustainability portfolio.']
  };
  document.getElementById('section-title').textContent = titles[name][0];
  document.getElementById('section-subtitle').textContent = titles[name][1];

  loadSection(name);
}

function loadSection(name) {
  switch(name) {
    case 'overview':  loadOverview(); break;
    case 'carbon':    loadCarbon(); break;
    case 'credits':   loadCredits(); break;
    case 'ledger':    loadLedger(); break;
    case 'portfolio': loadPortfolio(); break;
  }
}

// ===========================
// API HELPER
// ===========================

async function apiFetch(endpoint, options = {}) {
  const res = await fetch(`${API}${endpoint}`, {
    ...options,
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
      ...(options.headers || {})
    }
  });
  if (res.status === 401) {
    logout();
    throw new Error('Session expired. Please login again.');
  }
  // Convert API response to JSON
const data = await res.json();

if(!res.ok){

    throw new Error(data.detail || "Something went wrong.");

}

return data;
}

// ===========================
// OVERVIEW
// ===========================

let emissionsChartInstance = null;
let creditsChartInstance = null;

async function loadOverview() {
  try {
    const [portfolio, carbon, credits] = await Promise.allSettled([
      apiFetch('/portfolio'),
      apiFetch('/carbon'),
      apiFetch('/credits')
    ]);

    const portData  = portfolio.status === 'fulfilled' ? portfolio.value : {};
    const carbonData = carbon.status === 'fulfilled'  ? (Array.isArray(carbon.value) ? carbon.value : []) : [];
    const creditData = credits.status === 'fulfilled' ? (Array.isArray(credits.value) ? credits.value : []) : [];

    // Stat cards
    const totalEmissions = carbonData.reduce((s, r) => s + (r.amount || r.emission_amount || 0), 0);
    const totalCredits   = creditData.reduce((s, r) => s + (r.amount || r.credit_amount || 0), 0);

    document.getElementById('stat-emissions').textContent    = totalEmissions.toFixed(1);
    document.getElementById('stat-credits').textContent      = totalCredits.toFixed(1);
    document.getElementById('stat-transactions').textContent = carbonData.length + creditData.length;
    document.getElementById('stat-balance').textContent      = (totalCredits - totalEmissions).toFixed(1);

    // Charts
    renderEmissionsChart(carbonData);
    renderCreditsChart(creditData, totalEmissions);

  } catch (err) {
    console.error("Overview loading failed:",err);
  }
}

function renderEmissionsChart(data) {
  const ctx = document.getElementById('emissionsChart').getContext('2d');
  if (emissionsChartInstance) emissionsChartInstance.destroy();

  // Display placeholder chart when no emission data exists
if(data.length===0){

data=[{

amount:0,

created_at:null

}];

}

  // Group by month or use last 6 records
  const labels = data.slice(-6).map((r, i) => r.created_at
    ? new Date(r.created_at).toLocaleDateString('en', { month: 'short', day: 'numeric' })
    : `Record ${i + 1}`);
  const values = data.slice(-6).map(r => r.amount || r.emission_amount || 0);

  emissionsChartInstance = new Chart(ctx, {
    type: 'line',
    data: {
      labels: labels.length ? labels : ['No data'],
      datasets: [{
        label: 'CO₂ (kg)',
        data: values.length ? values : [0],
        borderColor: '#2d6a4f',
        backgroundColor: 'rgba(45,106,79,0.08)',
        borderWidth: 2,
        fill: true,
        tension: 0.3,
        pointRadius: 4,
        pointBackgroundColor: '#2d6a4f'
      }]
    },
    options: {
      responsive: true,
      plugins: { legend: { display: false } },
      scales: {
        y: { beginAtZero: true, grid: { color: '#f3f4f6' } },
        x: { grid: { display: false } }
      }
    }
  });
}

function renderCreditsChart(creditData, emissions) {
  const ctx = document.getElementById('creditsChart').getContext('2d');
  if (creditsChartInstance) creditsChartInstance.destroy();

  const totalCredits = creditData.reduce((s, r) => s + (r.amount || r.credit_amount || 0), 0);


  creditsChartInstance = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: ['Credits Earned', 'Emissions'],
      datasets: [{
        data: [totalCredits || 1, emissions || 1],
        backgroundColor: ['#2d6a4f', '#fbbf24'],
        borderWidth: 0,
        hoverOffset: 4
      }]
    },
    options: {
      responsive: true,
      cutout: '65%',
      plugins: {
        legend: { position: 'bottom', labels: { padding: 16, font: { size: 12 } } }
      }
    }
  });
}

// ===========================
// CARBON TRACKER
// ===========================

async function loadCarbon() {
  const tbody = document.getElementById('carbon-table-body');
  tbody.innerHTML = '<tr><td colspan="6" class="empty-row">Loading...</td></tr>';

  try {
    const data = await apiFetch('/carbon');
    const records = Array.isArray(data) ? data : (data.records || data.data || []);

    if (!records.length) {
      tbody.innerHTML = '<tr><td colspan="6" class="empty-row">No carbon records found. Add your first record!</td></tr>';
      return;
    }

    tbody.innerHTML = records.map((r, i) => `
      <tr>
        <td>${i + 1}</td>
        <td>${r.activity_type || r.category || 'General'}</td>
        <td><strong>${(r.amount || r.emission_amount || 0).toFixed(2)}</strong> kg</td>
        <td>${r.description || r.notes || '—'}</td>
        <td>${formatDate(r.created_at || r.date)}</td>
        <td><span class="badge badge-green">Tracked</span></td>
      </tr>
    `).join('');
  } catch (err) {
    tbody.innerHTML = `<tr><td colspan="6" class="empty-row">Could not load records: ${err.message}</td></tr>`;
  }
}

function toggleAddCarbon() {
  const form = document.getElementById('add-carbon-form');
  form.classList.toggle('hidden');
}

async function handleAddCarbon(e) {
  e.preventDefault();
  try {
    await apiFetch('/carbon', {
      method: 'POST',
      body: JSON.stringify({
        activity_type: document.getElementById('carbon-activity').value,
        amount: parseFloat(document.getElementById('carbon-amount').value),
        description: document.getElementById('carbon-desc').value
      })
    });
    toggleAddCarbon();

// Reload dashboard statistics
loadCarbon();

loadOverview();

// Show success notification
showToast("Carbon record added successfully.");
  } catch (err) {
    showToast(err.message,"error");
  }
}

// ===========================
// CREDITS
// ===========================

async function loadCredits() {
  const tbody = document.getElementById('credits-table-body');
  tbody.innerHTML = '<tr><td colspan="6" class="empty-row">Loading...</td></tr>';

  try {
    const data = await apiFetch('/credits');
    const records = Array.isArray(data) ? data : (data.credits || data.data || []);

    if (!records.length) {
      tbody.innerHTML = '<tr><td colspan="6" class="empty-row">No carbon credits found yet.</td></tr>';
      return;
    }

    tbody.innerHTML = records.map((r, i) => {
      const isActive = (r.status || '').toLowerCase() === 'active';
      const actionsHtml = isActive
        ? `<button class="action-btn btn-transfer-action" onclick="openTransferModal('${r.id}')">Transfer</button>
           <button class="action-btn btn-retire-action" onclick="openRetireModal('${r.id}')">Retire</button>`
        : `—`;
      return `
        <tr>
          <td>${i + 1}</td>
          <td>${r.credit_type || r.type || 'Standard'}</td>
          <td><strong>${(r.amount || r.credit_amount || 0).toFixed(2)}</strong></td>
          <td>${r.source || r.origin || '—'}</td>
          <td>${formatDate(r.created_at || r.date)}</td>
          <td><span class="badge ${isActive ? 'badge-blue' : 'badge-green'}">${(r.status || 'Active').toUpperCase()}</span></td>
          <td>${actionsHtml}</td>
        </tr>
      `;
    }).join('');
  } catch (err) {
    tbody.innerHTML = `<tr><td colspan="6" class="empty-row">Could not load credits: ${err.message}</td></tr>`;
  }
}

// ===========================
// LEDGER
// ===========================

async function loadLedger() {
  const tbody = document.getElementById('ledger-table-body');
  tbody.innerHTML = '<tr><td colspan="6" class="empty-row">Loading...</td></tr>';

  try {
    const data = await apiFetch('/ledger');
    const records = Array.isArray(data) ? data : (data.entries || data.data || []);

    if (!records.length) {
      tbody.innerHTML = '<tr><td colspan="6" class="empty-row">No ledger entries found.</td></tr>';
      return;
    }

    tbody.innerHTML = records.map((r, i) => `
      <tr>
        <td>${i + 1}</td>
        <td><span class="badge ${r.type === 'credit' ? 'badge-green' : 'badge-amber'}">${r.entry_type || r.type || 'Transaction'}</span></td>
        <td>${(r.amount || 0).toFixed(2)}</td>
        <td>${r.description || r.notes || '—'}</td>
        <td>${formatDate(r.created_at || r.date)}</td>
        <td><strong>${(r.balance || r.running_balance || 0).toFixed(2)}</strong></td>
      </tr>
    `).join('');
  } catch (err) {
    tbody.innerHTML = `<tr><td colspan="6" class="empty-row">Could not load ledger: ${err.message}</td></tr>`;
  }
}

// ===========================
// PORTFOLIO
// ===========================

async function loadPortfolio() {
  try {
    const [portRes, carbonRes, creditsRes] = await Promise.allSettled([
      apiFetch('/portfolio'),
      apiFetch('/carbon'),
      apiFetch('/credits')
    ]);

    const portData   = portRes.status === 'fulfilled'   ? portRes.value   : {};
    const carbonData = carbonRes.status === 'fulfilled' ? (Array.isArray(carbonRes.value) ? carbonRes.value : []) : [];
    const creditData = creditsRes.status === 'fulfilled'? (Array.isArray(creditsRes.value)? creditsRes.value : []) : [];

    const totalEmissions = portData.total_emissions ?? carbonData.reduce((s, r) => s + (r.amount || 0), 0);
    const totalCredits   = portData.total_credits   ?? creditData.reduce((s, r) => s + (r.amount || 0), 0);
    const net = totalCredits - totalEmissions;
    const score = portData.sustainability_score ?? Math.max(0, Math.min(100, Math.round(50 + (net / 10))));

    document.getElementById('port-emissions').textContent = totalEmissions.toFixed(1);
    document.getElementById('port-credits').textContent   = totalCredits.toFixed(1);
    document.getElementById('port-net').textContent       = net.toFixed(1);
    document.getElementById('port-score').textContent     = score;

  } catch (err) {
    console.error('Portfolio error:', err);
  }
}

// ===========================
// UTILITIES
// ===========================

function formatDate(dateStr) {
  if (!dateStr) return '—';
  try {
    return new Date(dateStr).toLocaleDateString('en-IN', {
      day: '2-digit', month: 'short', year: 'numeric'
    });
  } catch { return dateStr; }
}

// ===========================
// Toast Notification Function
// Displays success or error messages
// ===========================

function showToast(message, type = "success") {

    const toast = document.createElement("div");

    toast.className = `toast ${type}`;

    toast.innerText = message;

    document.body.appendChild(toast);

    setTimeout(() => {
        toast.classList.add("show");
    }, 100);

    setTimeout(() => {
        toast.classList.remove("show");

        setTimeout(() => {
            toast.remove();
        }, 300);

    }, 3000);
}

function searchCarbon(){

    const value = document.getElementById("carbon-search")
                    .value
                    .toLowerCase();

    const rows = document.querySelectorAll("#carbon-table-body tr");

    rows.forEach(row=>{

        row.style.display =
            row.innerText.toLowerCase().includes(value)
            ? ""
            : "none";

    });

}

// ===========================
// MODALS FOR CREDIT ACTIONS
// ===========================

function openTransferModal(creditId) {
  document.getElementById('transfer-credit-id').value = creditId;
  document.getElementById('transfer-recipient').value = '';
  document.getElementById('transfer-amount').value = '';
  document.getElementById('transfer-modal').classList.remove('hidden');
}

function openRetireModal(creditId) {
  document.getElementById('retire-credit-id').value = creditId;
  document.getElementById('retire-amount').value = '';
  document.getElementById('retire-notes').value = '';
  document.getElementById('retire-modal').classList.remove('hidden');
}

function closeModal(modalId) {
  document.getElementById(modalId).classList.add('hidden');
}

async function handleTransferSubmit(e) {
  e.preventDefault();
  const creditId = document.getElementById('transfer-credit-id').value;
  const recipient = document.getElementById('transfer-recipient').value;
  const amount = parseFloat(document.getElementById('transfer-amount').value);
  try {
    await apiFetch('/credits/transfer', {
      method: 'POST',
      body: JSON.stringify({
        carbon_credit_id: creditId,
        recipient_username: recipient,
        amount: amount
      })
    });
    closeModal('transfer-modal');
    showToast("Carbon credit transferred successfully!");
    loadCredits();
    loadOverview();
  } catch (err) {
    showToast(err.message, "error");
  }
}

async function handleRetireSubmit(e) {
  e.preventDefault();
  const creditId = document.getElementById('retire-credit-id').value;
  const amount = parseFloat(document.getElementById('retire-amount').value);
  const notes = document.getElementById('retire-notes').value;
  try {
    await apiFetch('/credits/retire', {
      method: 'POST',
      body: JSON.stringify({
        carbon_credit_id: creditId,
        amount: amount,
        notes: notes
      })
    });
    closeModal('retire-modal');
    showToast("Carbon credit retired successfully!");
    loadCredits();
    loadOverview();
  } catch (err) {
    showToast(err.message, "error");
  }
}