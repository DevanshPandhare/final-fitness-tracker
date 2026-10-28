import './index.css'

const API = 'http://localhost:8000/api/v1'

// ── State ──────────────────────────────────────────────────────────────────────
let token: string | null = localStorage.getItem('np_token')
let currentUser: any = JSON.parse(localStorage.getItem('np_user') || 'null')
let currentPage = 'dashboard'
let sidebarCollapsed = false
let selectedDate = new Date().toISOString().split('T')[0]

// ── API Helpers ─────────────────────────────────────────────────────────────────
async function apiFetch(path: string, opts: RequestInit = {}) {
  const headers: any = { 'Content-Type': 'application/json', ...opts.headers }
  if (token) headers['Authorization'] = `Bearer ${token}`
  const res = await fetch(`${API}${path}`, { ...opts, headers })
  if (res.status === 401) { logout(); return null }
  if (res.status === 204) return null
  return res.ok ? res.json() : res.json().then((e: any) => { throw new Error(e.detail || 'API Error') })
}

// ── Auth Helpers ─────────────────────────────────────────────────────────────────
function setAuth(data: any) {
  token = data.access_token
  currentUser = data.user
  localStorage.setItem('np_token', token!)
  localStorage.setItem('np_user', JSON.stringify(currentUser))
}

function logout() {
  token = null
  currentUser = null
  localStorage.removeItem('np_token')
  localStorage.removeItem('np_user')
  currentPage = 'dashboard'
  renderApp()
}

// ── Toast ──────────────────────────────────────────────────────────────────────
function toast(msg: string, type: 'success' | 'error' | 'info' = 'success') {
  const t = document.createElement('div')
  t.className = `toast toast-${type}`
  t.innerHTML = `<span class="toast-icon">${type === 'success' ? '✓' : type === 'error' ? '✕' : 'ℹ'}</span><span>${msg}</span>`
  document.body.appendChild(t)
  setTimeout(() => t.classList.add('toast-show'), 10)
  setTimeout(() => { t.classList.remove('toast-show'); setTimeout(() => t.remove(), 300) }, 3500)
}

// ── Router ─────────────────────────────────────────────────────────────────────
function navigate(page: string) {
  currentPage = page
  renderApp()
}

// ── Render App ─────────────────────────────────────────────────────────────────
function renderApp() {
  const app = document.getElementById('app')!
  if (!token) {
    app.innerHTML = renderAuthPage()
    attachAuthListeners()
    return
  }
  app.innerHTML = renderLayout()
  attachLayoutListeners()
  renderPage()
}

// ── Layout ─────────────────────────────────────────────────────────────────────
function renderLayout(): string {
  const initials = (currentUser?.full_name || currentUser?.username || 'U').substring(0, 2).toUpperCase()
  const navItems = [
    { id: 'dashboard', icon: '⊞', label: 'Dashboard' },
    { id: 'workouts', icon: '💪', label: 'Workouts' },
    { id: 'meals', icon: '🥗', label: 'Nutrition' },
    { id: 'ai-coach', icon: '🤖', label: 'AI Coach', ai: true },
    { id: 'profile', icon: '👤', label: 'Profile' },
  ]

  return `
  <div class="app-layout">
    <aside class="sidebar ${sidebarCollapsed ? 'collapsed' : ''}" id="sidebar">
      <div class="sidebar-logo">
        <div class="sidebar-logo-icon">🏃</div>
        <span class="sidebar-logo-text">Nutri<span>Pulse</span></span>
      </div>
      <nav class="sidebar-nav">
        <div class="nav-section-label">Main</div>
        ${navItems.filter(n => !n.ai).map(n => `
          <a class="nav-item ${currentPage === n.id ? 'active' : ''}" data-page="${n.id}" id="nav-${n.id}">
            <span class="nav-icon">${n.icon}</span>
            <span class="nav-label">${n.label}</span>
          </a>`).join('')}
        <div class="nav-section-label" style="margin-top:12px">AI Features</div>
        ${navItems.filter(n => n.ai).map(n => `
          <a class="nav-item ai-item ${currentPage === n.id ? 'active' : ''}" data-page="${n.id}" id="nav-${n.id}">
            <span class="nav-icon">${n.icon}</span>
            <span class="nav-label">${n.label}</span>
          </a>`).join('')}
      </nav>
      <div class="sidebar-footer">
        <button class="sidebar-collapse-btn" id="collapseBtn">
          ${sidebarCollapsed ? '→' : '←'}
        </button>
      </div>
    </aside>

    <div class="main-content ${sidebarCollapsed ? 'sidebar-collapsed' : ''}" id="mainContent">
      <header class="topbar ${sidebarCollapsed ? 'sidebar-collapsed' : ''}" id="topbar">
        <div class="topbar-left">
          <span class="topbar-title" id="topbarTitle">${getPageTitle()}</span>
        </div>
        <div class="topbar-right">
          <div class="date-display" id="datePickerToggle">
            📅 <span id="dateLabel">${formatDateShort(selectedDate)}</span>
          </div>
          <input type="date" class="date-input" id="datePicker" value="${selectedDate}" style="display:none">
          <div class="topbar-avatar" id="topbarAvatar" title="${currentUser?.username}">${initials}</div>
          <button class="btn btn-ghost btn-sm" id="logoutBtn">Sign out</button>
        </div>
      </header>

      <main class="page-container page-enter" id="pageContent"></main>
    </div>

    <!-- Mobile Bottom Nav -->
    <nav class="bottom-nav" id="bottomNav">
      <div class="bottom-nav-item ${currentPage === 'dashboard' ? 'active' : ''}" data-page="dashboard">⊞<br>Home</div>
      <div class="bottom-nav-item ${currentPage === 'workouts' ? 'active' : ''}" data-page="workouts">💪<br>Workouts</div>
      <div class="bottom-nav-item ${currentPage === 'meals' ? 'active' : ''}" data-page="meals">🥗<br>Meals</div>
      <div class="bottom-nav-item ${currentPage === 'ai-coach' ? 'active' : ''}" data-page="ai-coach">🤖<br>AI</div>
      <div class="bottom-nav-item ${currentPage === 'profile' ? 'active' : ''}" data-page="profile">👤<br>Profile</div>
    </nav>
  </div>`
}

function getPageTitle(): string {
  const titles: Record<string, string> = {
    dashboard: 'Dashboard', workouts: 'Workout Log', meals: 'Nutrition Tracker',
    'ai-coach': 'AI Health Coach', profile: 'Profile & Settings'
  }
  return titles[currentPage] || 'NutriPulse AI'
}

function formatDateShort(d: string): string {
  return new Date(d + 'T00:00:00').toLocaleDateString('en-IN', { day: 'numeric', month: 'short' })
}

function attachLayoutListeners() {
  // Nav items
  document.querySelectorAll('[data-page]').forEach(el => {
    el.addEventListener('click', () => navigate((el as HTMLElement).dataset.page!))
  })

  // Sidebar collapse
  document.getElementById('collapseBtn')?.addEventListener('click', () => {
    sidebarCollapsed = !sidebarCollapsed
    renderApp()
  })

  // Logout
  document.getElementById('logoutBtn')?.addEventListener('click', () => logout())

  // Date picker
  document.getElementById('datePickerToggle')?.addEventListener('click', () => {
    const p = document.getElementById('datePicker')!
    p.style.display = p.style.display === 'none' ? 'inline-block' : 'none'
  })
  document.getElementById('datePicker')?.addEventListener('change', (e) => {
    selectedDate = (e.target as HTMLInputElement).value
    const dp = document.getElementById('datePicker')!
    dp.style.display = 'none'
    document.getElementById('dateLabel')!.textContent = formatDateShort(selectedDate)
    renderPage()
  })
}

function renderPage() {
  const content = document.getElementById('pageContent')
  if (!content) return
  content.innerHTML = '<div class="loading-center"><div class="spinner"></div><span>Loading...</span></div>'

  switch (currentPage) {
    case 'dashboard': renderDashboard(content); break
    case 'workouts': renderWorkouts(content); break
    case 'meals': renderMeals(content); break
    case 'ai-coach': renderAICoach(content); break
    case 'profile': renderProfile(content); break
  }
}

// ── AUTH PAGE ─────────────────────────────────────────────────────────────────
function renderAuthPage(): string {
  return `
  <div class="auth-page">
    <div class="auth-bg-glow emerald"></div>
    <div class="auth-bg-glow violet"></div>
    <div class="auth-card">
      <div class="auth-logo">
        <div class="auth-logo-icon">🏃</div>
        <h1>Nutri<span>Pulse</span> AI</h1>
        <p>Your intelligent Indian fitness & nutrition coach</p>
      </div>
      <div class="auth-tabs">
        <button class="auth-tab active" id="tabLogin" onclick="switchAuthTab('login')">Sign In</button>
        <button class="auth-tab" id="tabRegister" onclick="switchAuthTab('register')">Register</button>
      </div>
      <div id="authForm">
        ${renderLoginForm()}
      </div>
    </div>
  </div>`
}

function renderLoginForm(): string {
  return `
  <form id="loginForm">
    <div class="form-group">
      <label class="form-label">Username</label>
      <input class="form-input" type="text" id="loginUsername" placeholder="Enter your username" required>
    </div>
    <div class="form-group">
      <label class="form-label">Password</label>
      <input class="form-input" type="password" id="loginPassword" placeholder="Enter your password" required>
    </div>
    <div id="authError" class="form-error" style="margin-bottom:12px;display:none"></div>
    <button class="btn btn-primary w-full btn-lg" type="submit" id="loginBtn">
      Sign In
    </button>
  </form>`
}

function renderRegisterForm(): string {
  return `
  <form id="registerForm">
    <div class="form-row">
      <div class="form-group">
        <label class="form-label">Username *</label>
        <input class="form-input" type="text" id="regUsername" placeholder="username" required>
      </div>
      <div class="form-group">
        <label class="form-label">Full Name</label>
        <input class="form-input" type="text" id="regFullName" placeholder="Your name">
      </div>
    </div>
    <div class="form-group">
      <label class="form-label">Email *</label>
      <input class="form-input" type="email" id="regEmail" placeholder="you@email.com" required>
    </div>
    <div class="form-group">
      <label class="form-label">Password *</label>
      <input class="form-input" type="password" id="regPassword" placeholder="Min 6 characters" required>
    </div>
    <div class="form-row">
      <div class="form-group">
        <label class="form-label">Age</label>
        <input class="form-input" type="number" id="regAge" placeholder="25" min="10" max="100">
      </div>
      <div class="form-group">
        <label class="form-label">Gender</label>
        <select class="form-select" id="regGender">
          <option value="">Select</option>
          <option value="male">Male</option>
          <option value="female">Female</option>
          <option value="other">Other</option>
        </select>
      </div>
    </div>
    <div class="form-row">
      <div class="form-group">
        <label class="form-label">Weight (kg)</label>
        <input class="form-input" type="number" id="regWeight" placeholder="70" step="0.1">
      </div>
      <div class="form-group">
        <label class="form-label">Height (cm)</label>
        <input class="form-input" type="number" id="regHeight" placeholder="170">
      </div>
    </div>
    <div class="form-row">
      <div class="form-group">
        <label class="form-label">Activity Level</label>
        <select class="form-select" id="regActivity">
          <option value="sedentary">Sedentary</option>
          <option value="light">Light</option>
          <option value="moderate" selected>Moderate</option>
          <option value="active">Active</option>
          <option value="very_active">Very Active</option>
        </select>
      </div>
      <div class="form-group">
        <label class="form-label">Goal</label>
        <select class="form-select" id="regGoal">
          <option value="lose_fat">Lose Fat</option>
          <option value="maintain" selected>Maintain</option>
          <option value="build_muscle">Build Muscle</option>
          <option value="endurance">Endurance</option>
        </select>
      </div>
    </div>
    <div class="form-group">
      <label class="form-label">Dietary Preference</label>
      <select class="form-select" id="regDiet">
        <option value="Vegetarian" selected>Vegetarian</option>
        <option value="Non-Veg">Non-Vegetarian</option>
        <option value="High-Protein">High-Protein</option>
        <option value="Vegan">Vegan</option>
      </select>
    </div>
    <div id="authError" class="form-error" style="margin-bottom:12px;display:none"></div>
    <button class="btn btn-primary w-full btn-lg" type="submit" id="registerBtn">
      Create Account
    </button>
  </form>`
}

;(window as any).switchAuthTab = function(tab: string) {
  const tabLogin = document.getElementById('tabLogin')!
  const tabReg = document.getElementById('tabRegister')!
  const form = document.getElementById('authForm')!
  if (tab === 'login') {
    tabLogin.classList.add('active'); tabReg.classList.remove('active')
    form.innerHTML = renderLoginForm()
    attachLoginListener()
  } else {
    tabReg.classList.add('active'); tabLogin.classList.remove('active')
    form.innerHTML = renderRegisterForm()
    attachRegisterListener()
  }
}

function attachAuthListeners() {
  attachLoginListener()
}

function attachLoginListener() {
  document.getElementById('loginForm')?.addEventListener('submit', async (e) => {
    e.preventDefault()
    const btn = document.getElementById('loginBtn') as HTMLButtonElement
    const err = document.getElementById('authError')!
    btn.disabled = true; btn.textContent = 'Signing in...'
    try {
      const data = await apiFetch('/auth/login', {
        method: 'POST',
        body: JSON.stringify({
          username: (document.getElementById('loginUsername') as HTMLInputElement).value,
          password: (document.getElementById('loginPassword') as HTMLInputElement).value,
        })
      })
      if (data) { setAuth(data); toast('Welcome back, ' + (data.user.full_name || data.user.username) + '! 👋'); renderApp() }
    } catch (ex: any) {
      err.textContent = ex.message; err.style.display = 'block'
    } finally {
      btn.disabled = false; btn.textContent = 'Sign In'
    }
  })
}

function attachRegisterListener() {
  document.getElementById('registerForm')?.addEventListener('submit', async (e) => {
    e.preventDefault()
    const btn = document.getElementById('registerBtn') as HTMLButtonElement
    const err = document.getElementById('authError')!
    btn.disabled = true; btn.textContent = 'Creating account...'
    const payload: any = {
      username: (document.getElementById('regUsername') as HTMLInputElement).value,
      email: (document.getElementById('regEmail') as HTMLInputElement).value,
      password: (document.getElementById('regPassword') as HTMLInputElement).value,
      full_name: (document.getElementById('regFullName') as HTMLInputElement).value || null,
      age: parseInt((document.getElementById('regAge') as HTMLInputElement).value) || null,
      weight_kg: parseFloat((document.getElementById('regWeight') as HTMLInputElement).value) || null,
      height_cm: parseFloat((document.getElementById('regHeight') as HTMLInputElement).value) || null,
      gender: (document.getElementById('regGender') as HTMLSelectElement).value || null,
      activity_level: (document.getElementById('regActivity') as HTMLSelectElement).value,
      fitness_goal: (document.getElementById('regGoal') as HTMLSelectElement).value,
      dietary_preference: (document.getElementById('regDiet') as HTMLSelectElement).value,
    }
    try {
      const data = await apiFetch('/auth/register', { method: 'POST', body: JSON.stringify(payload) })
      if (data) { setAuth(data); toast('Account created! Welcome to NutriPulse AI 🎉'); renderApp() }
    } catch (ex: any) {
      err.textContent = ex.message; err.style.display = 'block'
    } finally {
      btn.disabled = false; btn.textContent = 'Create Account'
    }
  })
}

// ── DASHBOARD PAGE ─────────────────────────────────────────────────────────────
async function renderDashboard(el: HTMLElement) {
  try {
    const [summary, weekly, macros] = await Promise.all([
      apiFetch(`/dashboard/summary?log_date=${selectedDate}`),
      apiFetch('/dashboard/weekly-chart'),
      apiFetch(`/dashboard/macro-breakdown?log_date=${selectedDate}`),
    ])

    const s = summary || {}
    const targetCal = s.target_calories || 2000
    const calPct = Math.min(100, Math.round((s.today_calories / targetCal) * 100))
    const proteinPct = s.target_protein ? Math.min(100, Math.round((s.today_protein / s.target_protein) * 100)) : 0
    const waterPct = s.target_water_ml ? Math.min(100, Math.round((s.today_water_ml / s.target_water_ml) * 100)) : 0

    const weekData = (weekly?.chart_data || []) as any[]

    el.innerHTML = `
    <div class="section-header">
      <div>
        <h1 class="section-title">Good ${getGreeting()}, ${currentUser?.full_name?.split(' ')[0] || currentUser?.username}! 👋</h1>
        <p class="section-subtitle">${new Date(selectedDate + 'T00:00:00').toLocaleDateString('en-IN', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}</p>
      </div>
      ${!s.target_calories ? `<button class="btn btn-violet btn-sm" id="setGoalsBtn">🤖 Set AI Goals</button>` : ''}
    </div>

    <!-- Stat Cards -->
    <div class="stat-grid">
      <div class="stat-card emerald">
        <div class="stat-card-icon emerald">🔥</div>
        <div class="stat-label">Calories Consumed</div>
        <div class="stat-value">${Math.round(s.today_calories || 0)}</div>
        <div class="stat-sub">of ${Math.round(targetCal)} kcal target</div>
        <div class="stat-progress-bar"><div class="stat-progress-fill emerald" style="width:${calPct}%"></div></div>
      </div>
      <div class="stat-card violet">
        <div class="stat-card-icon violet">💪</div>
        <div class="stat-label">Protein</div>
        <div class="stat-value">${Math.round(s.today_protein || 0)}g</div>
        <div class="stat-sub">${s.target_protein ? `of ${Math.round(s.target_protein)}g target` : 'No target set'}</div>
        ${s.target_protein ? `<div class="stat-progress-bar"><div class="stat-progress-fill violet" style="width:${proteinPct}%"></div></div>` : ''}
      </div>
      <div class="stat-card amber">
        <div class="stat-card-icon amber">🏃</div>
        <div class="stat-label">Calories Burned</div>
        <div class="stat-value">${Math.round(s.today_calories_burned || 0)}</div>
        <div class="stat-sub">${s.today_workouts || 0} workout${s.today_workouts !== 1 ? 's' : ''} today</div>
      </div>
      <div class="stat-card sky">
        <div class="stat-card-icon sky">💧</div>
        <div class="stat-label">Hydration</div>
        <div class="stat-value">${Math.round((s.today_water_ml || 0) / 1000 * 10) / 10}L</div>
        <div class="stat-sub">${s.target_water_ml ? `of ${Math.round(s.target_water_ml / 1000 * 10) / 10}L target` : 'No target set'}</div>
        ${s.target_water_ml ? `<div class="stat-progress-bar"><div class="stat-progress-fill sky" style="width:${waterPct}%"></div></div>` : ''}
      </div>
    </div>

    <div class="grid-2">
      <!-- Weekly Chart -->
      <div class="card">
        <div class="card-title">📊 7-Day Trend</div>
        <div class="chart-wrapper">
          ${renderBarChart(weekData)}
        </div>
      </div>

      <!-- Macro Ring + Water -->
      <div class="card">
        <div class="card-title">🥧 Today's Macros</div>
        ${renderMacroPie(macros?.macros || { protein: s.today_protein || 0, carbs: s.today_carbs || 0, fat: s.today_fat || 0 })}
        <div class="divider"></div>
        <div class="card-title">💧 Water Intake</div>
        ${renderWaterTracker(s.today_water_ml || 0, s.target_water_ml || 2500)}
      </div>
    </div>

    <!-- Net Calories -->
    <div class="card" style="margin-top:20px">
      <div class="card-title">⚡ Daily Balance</div>
      <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:20px;text-align:center">
        <div>
          <div class="stat-value text-emerald">${Math.round(s.today_calories || 0)}</div>
          <div class="stat-sub">Consumed</div>
        </div>
        <div>
          <div class="stat-value text-rose">${Math.round(s.today_calories_burned || 0)}</div>
          <div class="stat-sub">Burned</div>
        </div>
        <div>
          <div class="stat-value" style="color:${((s.today_calories||0)-(s.today_calories_burned||0)) > 0 ? 'var(--amber-400)' : 'var(--emerald-400)'}">
            ${Math.round((s.today_calories||0) - (s.today_calories_burned||0))}
          </div>
          <div class="stat-sub">Net</div>
        </div>
      </div>
      ${s.bmi ? `
        <div class="divider"></div>
        <div style="display:flex;align-items:center;gap:16px">
          <div>
            <div class="stat-label">BMI</div>
            <div class="stat-value">${s.bmi}</div>
          </div>
          <div class="bmi-badge ${getBMICategory(s.bmi).cls}">${getBMICategory(s.bmi).label}</div>
          <div style="flex:1;font-size:12px;color:var(--text-muted)">
            ${currentUser?.weight_kg ? `Weight: ${currentUser.weight_kg}kg` : ''} 
            ${currentUser?.height_cm ? `• Height: ${currentUser.height_cm}cm` : ''}
          </div>
        </div>` : ''}
    </div>`

    document.getElementById('setGoalsBtn')?.addEventListener('click', async () => {
      const btn = document.getElementById('setGoalsBtn') as HTMLButtonElement
      btn.disabled = true; btn.textContent = '🤖 Calculating...'
      try {
        await apiFetch('/ai/set-goals', { method: 'POST', body: JSON.stringify({}) })
        toast('AI Goals set! 🎯'); renderDashboard(el)
      } catch (ex: any) { toast(ex.message, 'error'); btn.disabled = false; btn.textContent = '🤖 Set AI Goals' }
    })

    // Water tracker buttons
    document.querySelectorAll('.water-btn').forEach(btn => {
      btn.addEventListener('click', async () => {
        const ml = parseInt((btn as HTMLElement).dataset.ml!)
        const current = s.today_water_ml || 0
        try {
          await apiFetch(`/dashboard/water?log_date=${selectedDate}`, {
            method: 'PATCH', body: JSON.stringify({ water_ml: current + ml })
          })
          toast(`+${ml}ml water logged! 💧`); renderDashboard(el)
        } catch (ex: any) { toast(ex.message, 'error') }
      })
    })

  } catch (ex: any) {
    el.innerHTML = `<div class="empty-state"><div class="empty-state-icon">⚠️</div><h3>Error loading dashboard</h3><p>${ex.message}</p></div>`
  }
}

function getGreeting(): string {
  const h = new Date().getHours()
  if (h < 12) return 'morning'
  if (h < 17) return 'afternoon'
  return 'evening'
}

function getBMICategory(bmi: number): { label: string, cls: string } {
  if (bmi < 18.5) return { label: 'Underweight', cls: 'badge-sky' }
  if (bmi < 25) return { label: 'Healthy', cls: 'badge-emerald' }
  if (bmi < 30) return { label: 'Overweight', cls: 'badge-amber' }
  return { label: 'Obese', cls: 'badge-rose' }
}

function renderBarChart(data: any[]): string {
  if (!data.length) return '<div class="empty-state"><p>No chart data</p></div>'
  const maxVal = Math.max(...data.map(d => Math.max(d.calories_consumed, d.calories_burned)), 1)
  return `
  <div class="bar-chart">
    ${data.map(d => `
    <div class="bar-group">
      <div class="bar-pair">
        <div class="bar bar-consumed" style="height:${Math.round((d.calories_consumed/maxVal)*120)}px" title="${Math.round(d.calories_consumed)} kcal consumed"></div>
        <div class="bar bar-burned" style="height:${Math.round((d.calories_burned/maxVal)*120)}px" title="${Math.round(d.calories_burned)} kcal burned"></div>
      </div>
      <div class="bar-label">${d.day}</div>
    </div>`).join('')}
  </div>
  <div class="chart-legend">
    <span class="legend-dot consumed"></span><span>Consumed</span>
    <span class="legend-dot burned" style="margin-left:16px"></span><span>Burned</span>
  </div>`
}

function renderMacroPie(macros: any): string {
  const p = macros.protein || 0, c = macros.carbs || 0, f = macros.fat || 0
  const total = p + c + f || 1
  const pPct = Math.round((p / total) * 100)
  const cPct = Math.round((c / total) * 100)
  const fPct = 100 - pPct - cPct
  return `
  <div class="macro-bars">
    <div class="macro-row">
      <span class="macro-name">Protein</span>
      <div class="macro-bar-bg"><div class="macro-bar-fill" style="width:${pPct}%;background:var(--violet-500)"></div></div>
      <span class="macro-val">${Math.round(p)}g</span>
    </div>
    <div class="macro-row">
      <span class="macro-name">Carbs</span>
      <div class="macro-bar-bg"><div class="macro-bar-fill" style="width:${cPct}%;background:var(--amber-500)"></div></div>
      <span class="macro-val">${Math.round(c)}g</span>
    </div>
    <div class="macro-row">
      <span class="macro-name">Fat</span>
      <div class="macro-bar-bg"><div class="macro-bar-fill" style="width:${fPct}%;background:var(--rose-400)"></div></div>
      <span class="macro-val">${Math.round(f)}g</span>
    </div>
  </div>`
}

function renderWaterTracker(current: number, target: number): string {
  const glasses = Math.round(current / 250)
  const targetGlasses = Math.round(target / 250)
  return `
  <div class="water-tracker">
    <div class="water-glasses">
      ${Array.from({ length: 8 }, (_, i) => `<div class="water-glass ${i < glasses ? 'filled' : ''}">💧</div>`).join('')}
    </div>
    <div style="font-size:12px;color:var(--text-muted);margin-top:8px">${glasses} / ${targetGlasses} glasses (${Math.round(current)}ml)</div>
    <div style="display:flex;gap:8px;margin-top:10px;flex-wrap:wrap">
      <button class="btn btn-ghost btn-sm water-btn" data-ml="250">+250ml</button>
      <button class="btn btn-ghost btn-sm water-btn" data-ml="500">+500ml</button>
      <button class="btn btn-ghost btn-sm water-btn" data-ml="1000">+1L</button>
    </div>
  </div>`
}

// ── WORKOUTS PAGE ─────────────────────────────────────────────────────────────
async function renderWorkouts(el: HTMLElement) {
  try {
    const workouts = await apiFetch(`/workouts/?limit=50`) || []
    const types = ['Cardio', 'Strength', 'Yoga', 'HIIT', 'Sports', 'Other']

    el.innerHTML = `
    <div class="section-header">
      <div>
        <h1 class="section-title">Workout Log</h1>
        <p class="section-subtitle">${workouts.length} total sessions</p>
      </div>
      <button class="btn btn-primary" id="addWorkoutBtn">+ Log Workout</button>
    </div>

    <!-- Add Workout Modal (hidden) -->
    <div class="modal-overlay" id="workoutModal" style="display:none">
      <div class="modal">
        <div class="modal-header">
          <span class="modal-title">Log New Workout 💪</span>
          <button class="modal-close" id="closeWorkoutModal">✕</button>
        </div>
        <form id="workoutForm">
          <div class="form-group">
            <label class="form-label">Exercise Name *</label>
            <input class="form-input" id="wExercise" placeholder="e.g. Running, Bench Press" required>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label class="form-label">Type *</label>
              <select class="form-select" id="wType">
                ${types.map(t => `<option value="${t}">${t}</option>`).join('')}
              </select>
            </div>
            <div class="form-group">
              <label class="form-label">Duration (min) *</label>
              <input class="form-input" type="number" id="wDuration" placeholder="30" min="1" required>
            </div>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label class="form-label">Sets</label>
              <input class="form-input" type="number" id="wSets" placeholder="3">
            </div>
            <div class="form-group">
              <label class="form-label">Reps</label>
              <input class="form-input" type="number" id="wReps" placeholder="12">
            </div>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label class="form-label">Weight (kg)</label>
              <input class="form-input" type="number" id="wWeight" placeholder="60" step="0.5">
            </div>
            <div class="form-group">
              <label class="form-label">Calories Burned</label>
              <input class="form-input" type="number" id="wCalories" placeholder="Auto-calculated">
            </div>
          </div>
          <div class="form-group">
            <label class="form-label">Notes</label>
            <textarea class="form-textarea" id="wNotes" placeholder="How did it go?"></textarea>
          </div>
          <div id="workoutFormError" class="form-error" style="display:none"></div>
          <div style="display:flex;gap:12px">
            <button class="btn btn-ghost flex-1" type="button" id="cancelWorkoutBtn">Cancel</button>
            <button class="btn btn-primary flex-1" type="submit" id="submitWorkoutBtn">Log Workout</button>
          </div>
        </form>
      </div>
    </div>

    ${workouts.length === 0 ? `
      <div class="empty-state">
        <div class="empty-state-icon">🏋️</div>
        <h3>No workouts logged yet</h3>
        <p>Click "Log Workout" to add your first session!</p>
      </div>` : `
    <div class="workout-list">
      ${workouts.map((w: any) => `
      <div class="workout-card" data-id="${w.id}">
        <div class="workout-card-left">
          <div class="workout-type-badge ${getWorkoutTypeClass(w.workout_type)}">${getWorkoutTypeEmoji(w.workout_type)}</div>
          <div>
            <div class="workout-name">${w.exercise_name}</div>
            <div class="workout-meta">
              ${w.workout_type} • ${w.duration_minutes}min
              ${w.sets ? ` • ${w.sets}×${w.reps || '?'}` : ''}
              ${w.weight_kg ? ` • ${w.weight_kg}kg` : ''}
            </div>
            <div class="workout-date">${new Date(w.workout_date).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' })}</div>
          </div>
        </div>
        <div class="workout-card-right">
          <div class="workout-calories">${Math.round(w.calories_burned || 0)} <span>kcal</span></div>
          <button class="btn btn-danger btn-sm delete-workout-btn" data-id="${w.id}">✕</button>
        </div>
      </div>`).join('')}
    </div>`}
    `

    // Attach modal listeners
    document.getElementById('addWorkoutBtn')?.addEventListener('click', () => {
      document.getElementById('workoutModal')!.style.display = 'flex'
    })
    document.getElementById('closeWorkoutModal')?.addEventListener('click', () => {
      document.getElementById('workoutModal')!.style.display = 'none'
    })
    document.getElementById('cancelWorkoutBtn')?.addEventListener('click', () => {
      document.getElementById('workoutModal')!.style.display = 'none'
    })

    document.getElementById('workoutForm')?.addEventListener('submit', async (e) => {
      e.preventDefault()
      const btn = document.getElementById('submitWorkoutBtn') as HTMLButtonElement
      const err = document.getElementById('workoutFormError')!
      btn.disabled = true; btn.textContent = 'Logging...'
      const payload: any = {
        exercise_name: (document.getElementById('wExercise') as HTMLInputElement).value,
        workout_type: (document.getElementById('wType') as HTMLSelectElement).value,
        duration_minutes: parseInt((document.getElementById('wDuration') as HTMLInputElement).value),
        sets: parseInt((document.getElementById('wSets') as HTMLInputElement).value) || null,
        reps: parseInt((document.getElementById('wReps') as HTMLInputElement).value) || null,
        weight_kg: parseFloat((document.getElementById('wWeight') as HTMLInputElement).value) || null,
        calories_burned: parseFloat((document.getElementById('wCalories') as HTMLInputElement).value) || null,
        notes: (document.getElementById('wNotes') as HTMLTextAreaElement).value || null,
      }
      try {
        await apiFetch('/workouts/', { method: 'POST', body: JSON.stringify(payload) })
        toast('Workout logged! 💪')
        document.getElementById('workoutModal')!.style.display = 'none'
        renderWorkouts(el)
      } catch (ex: any) {
        err.textContent = ex.message; err.style.display = 'block'
      } finally {
        btn.disabled = false; btn.textContent = 'Log Workout'
      }
    })

    document.querySelectorAll('.delete-workout-btn').forEach(btn => {
      btn.addEventListener('click', async () => {
        if (!confirm('Delete this workout?')) return
        const id = (btn as HTMLElement).dataset.id
        try {
          await apiFetch(`/workouts/${id}`, { method: 'DELETE' })
          toast('Workout deleted'); renderWorkouts(el)
        } catch (ex: any) { toast(ex.message, 'error') }
      })
    })

  } catch (ex: any) {
    el.innerHTML = `<div class="empty-state"><div class="empty-state-icon">⚠️</div><h3>Error loading workouts</h3><p>${ex.message}</p></div>`
  }
}

function getWorkoutTypeEmoji(type: string): string {
  const map: Record<string, string> = { Cardio: '🏃', Strength: '🏋️', Yoga: '🧘', HIIT: '⚡', Sports: '⚽', Other: '💪' }
  return map[type] || '💪'
}

function getWorkoutTypeClass(type: string): string {
  const map: Record<string, string> = { Cardio: 'emerald', Strength: 'violet', Yoga: 'sky', HIIT: 'amber', Sports: 'emerald', Other: 'violet' }
  return map[type] || 'violet'
}

// ── MEALS PAGE ─────────────────────────────────────────────────────────────────
async function renderMeals(el: HTMLElement) {
  try {
    const todayData = await apiFetch(`/meals/today`) || { meals_by_category: {}, totals: {} }
    const categories = ['Breakfast', 'Lunch', 'Dinner', 'Snack']
    const catEmojis: Record<string, string> = { Breakfast: '🌅', Lunch: '☀️', Dinner: '🌙', Snack: '🍎' }

    el.innerHTML = `
    <div class="section-header">
      <div>
        <h1 class="section-title">Nutrition Tracker</h1>
        <p class="section-subtitle">Today: ${Math.round(todayData.totals?.calories || 0)} kcal • ${Math.round(todayData.totals?.protein_g || 0)}g protein</p>
      </div>
      <button class="btn btn-primary" id="addMealBtn">+ Log Meal</button>
    </div>

    <!-- Macro Summary Bar -->
    <div class="card mb-4">
      <div class="macro-summary-row">
        <div class="macro-stat"><span class="macro-stat-val text-emerald">${Math.round(todayData.totals?.calories || 0)}</span><span class="macro-stat-label">Calories</span></div>
        <div class="macro-stat"><span class="macro-stat-val text-violet">${Math.round(todayData.totals?.protein_g || 0)}g</span><span class="macro-stat-label">Protein</span></div>
        <div class="macro-stat"><span class="macro-stat-val text-amber">${Math.round(todayData.totals?.carbs_g || 0)}g</span><span class="macro-stat-label">Carbs</span></div>
        <div class="macro-stat"><span class="macro-stat-val text-rose">${Math.round(todayData.totals?.fat_g || 0)}g</span><span class="macro-stat-label">Fat</span></div>
      </div>
    </div>

    <!-- Add Meal Modal -->
    <div class="modal-overlay" id="mealModal" style="display:none">
      <div class="modal" style="max-width:520px">
        <div class="modal-header">
          <span class="modal-title">Log Meal 🥗</span>
          <button class="modal-close" id="closeMealModal">✕</button>
        </div>
        <form id="mealForm">
          <div class="form-group" style="position:relative">
            <label class="form-label">Search Indian Food Database</label>
            <input class="form-input" id="foodSearch" placeholder="Search paneer, dal, roti..." autocomplete="off">
            <div class="food-search-results" id="foodResults" style="display:none"></div>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label class="form-label">Food Name *</label>
              <input class="form-input" id="mFoodName" placeholder="Food item" required>
            </div>
            <div class="form-group">
              <label class="form-label">Category *</label>
              <select class="form-select" id="mCategory">
                ${categories.map(c => `<option value="${c}">${c}</option>`).join('')}
              </select>
            </div>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label class="form-label">Serving Size</label>
              <input class="form-input" type="number" id="mServing" placeholder="100" step="0.1">
            </div>
            <div class="form-group">
              <label class="form-label">Unit</label>
              <select class="form-select" id="mUnit">
                <option>g</option><option>ml</option><option>piece</option><option>bowl</option><option>roti</option><option>cup</option>
              </select>
            </div>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label class="form-label">Calories (kcal) *</label>
              <input class="form-input" type="number" id="mCalories" placeholder="250" step="0.1" required>
            </div>
            <div class="form-group">
              <label class="form-label">Protein (g)</label>
              <input class="form-input" type="number" id="mProtein" placeholder="10" step="0.1">
            </div>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label class="form-label">Carbs (g)</label>
              <input class="form-input" type="number" id="mCarbs" placeholder="30" step="0.1">
            </div>
            <div class="form-group">
              <label class="form-label">Fat (g)</label>
              <input class="form-input" type="number" id="mFat" placeholder="8" step="0.1">
            </div>
          </div>
          <div id="mealFormError" class="form-error" style="display:none"></div>
          <div style="display:flex;gap:12px">
            <button class="btn btn-ghost flex-1" type="button" id="cancelMealBtn">Cancel</button>
            <button class="btn btn-primary flex-1" type="submit" id="submitMealBtn">Log Meal</button>
          </div>
        </form>
      </div>
    </div>

    <!-- Meal Categories -->
    ${categories.map(cat => {
      const meals = todayData.meals_by_category?.[cat] || []
      const catCals = meals.reduce((s: number, m: any) => s + m.calories, 0)
      return `
      <div class="card mb-4">
        <div class="meal-cat-header">
          <div style="display:flex;align-items:center;gap:10px">
            <span style="font-size:20px">${catEmojis[cat]}</span>
            <div>
              <div class="section-title" style="font-size:16px">${cat}</div>
              <div class="section-subtitle">${meals.length} items • ${Math.round(catCals)} kcal</div>
            </div>
          </div>
          <button class="btn btn-ghost btn-sm add-cat-meal" data-cat="${cat}">+ Add</button>
        </div>
        ${meals.length > 0 ? `
        <div class="timeline" style="margin-top:12px">
          ${meals.map((m: any) => `
          <div class="timeline-item">
            <div class="timeline-dot emerald"></div>
            <div class="timeline-content">
              <div class="timeline-title">${m.food_item_name}</div>
              <div class="timeline-sub">${m.serving_size}${m.serving_unit} • ${Math.round(m.protein_g || 0)}g P • ${Math.round(m.carbs_g || 0)}g C • ${Math.round(m.fat_g || 0)}g F</div>
            </div>
            <span class="timeline-badge badge-emerald">${Math.round(m.calories)} kcal</span>
            <button class="btn btn-danger btn-sm delete-meal-btn" data-id="${m.id}" style="margin-left:8px">✕</button>
          </div>`).join('')}
        </div>` : `<div class="empty-state" style="padding:20px 0"><p>No ${cat.toLowerCase()} logged</p></div>`}
      </div>`
    }).join('')}
    `

    // Attach meal modal listeners
    const openMealModal = (cat: string = 'Breakfast') => {
      ;(document.getElementById('mCategory') as HTMLSelectElement).value = cat
      document.getElementById('mealModal')!.style.display = 'flex'
    }

    document.getElementById('addMealBtn')?.addEventListener('click', () => openMealModal())
    document.querySelectorAll('.add-cat-meal').forEach(btn => {
      btn.addEventListener('click', () => openMealModal((btn as HTMLElement).dataset.cat!))
    })
    document.getElementById('closeMealModal')?.addEventListener('click', () => {
      document.getElementById('mealModal')!.style.display = 'none'
    })
    document.getElementById('cancelMealBtn')?.addEventListener('click', () => {
      document.getElementById('mealModal')!.style.display = 'none'
    })

    // Food Search
    let searchTimeout: any
    document.getElementById('foodSearch')?.addEventListener('input', (e) => {
      clearTimeout(searchTimeout)
      const q = (e.target as HTMLInputElement).value.trim()
      if (!q || q.length < 2) { document.getElementById('foodResults')!.style.display = 'none'; return }
      searchTimeout = setTimeout(async () => {
        try {
          const foods = await apiFetch(`/meals/search-food?q=${encodeURIComponent(q)}&limit=8`) || []
          const resultsEl = document.getElementById('foodResults')!
          if (!foods.length) { resultsEl.style.display = 'none'; return }
          resultsEl.innerHTML = foods.map((f: any) => `
            <div class="food-result-item" data-food='${JSON.stringify(f).replace(/'/g, "&#39;")}'>
              <div>
                <div class="food-result-name">${f.food_name} ${f.is_vegetarian ? '🌿' : '🍖'}</div>
                <div class="food-result-meta">${f.serving_unit} • P:${f.protein_g}g C:${f.carbs_g}g F:${f.fat_g}g</div>
              </div>
              <div class="food-result-calories">${Math.round(f.calories)} kcal</div>
            </div>`).join('')
          resultsEl.style.display = 'block'

          resultsEl.querySelectorAll('.food-result-item').forEach(item => {
            item.addEventListener('click', () => {
              const f = JSON.parse((item as HTMLElement).dataset.food!)
              ;(document.getElementById('mFoodName') as HTMLInputElement).value = f.food_name
              ;(document.getElementById('mServing') as HTMLInputElement).value = f.serving_size_g || 100
              ;(document.getElementById('mCalories') as HTMLInputElement).value = f.calories
              ;(document.getElementById('mProtein') as HTMLInputElement).value = f.protein_g
              ;(document.getElementById('mCarbs') as HTMLInputElement).value = f.carbs_g
              ;(document.getElementById('mFat') as HTMLInputElement).value = f.fat_g
              ;(document.getElementById('foodSearch') as HTMLInputElement).value = f.food_name
              resultsEl.style.display = 'none'
            })
          })
        } catch {}
      }, 300)
    })

    document.getElementById('mealForm')?.addEventListener('submit', async (e) => {
      e.preventDefault()
      const btn = document.getElementById('submitMealBtn') as HTMLButtonElement
      const err = document.getElementById('mealFormError')!
      btn.disabled = true; btn.textContent = 'Logging...'
      const payload = {
        food_item_name: (document.getElementById('mFoodName') as HTMLInputElement).value,
        meal_category: (document.getElementById('mCategory') as HTMLSelectElement).value,
        serving_size: parseFloat((document.getElementById('mServing') as HTMLInputElement).value) || 100,
        serving_unit: (document.getElementById('mUnit') as HTMLSelectElement).value,
        calories: parseFloat((document.getElementById('mCalories') as HTMLInputElement).value),
        protein_g: parseFloat((document.getElementById('mProtein') as HTMLInputElement).value) || null,
        carbs_g: parseFloat((document.getElementById('mCarbs') as HTMLInputElement).value) || null,
        fat_g: parseFloat((document.getElementById('mFat') as HTMLInputElement).value) || null,
      }
      try {
        await apiFetch('/meals/', { method: 'POST', body: JSON.stringify(payload) })
        toast('Meal logged! 🥗')
        document.getElementById('mealModal')!.style.display = 'none'
        renderMeals(el)
      } catch (ex: any) {
        err.textContent = ex.message; err.style.display = 'block'
      } finally {
        btn.disabled = false; btn.textContent = 'Log Meal'
      }
    })

    document.querySelectorAll('.delete-meal-btn').forEach(btn => {
      btn.addEventListener('click', async () => {
        const id = (btn as HTMLElement).dataset.id
        try {
          await apiFetch(`/meals/${id}`, { method: 'DELETE' })
          toast('Meal removed'); renderMeals(el)
        } catch (ex: any) { toast(ex.message, 'error') }
      })
    })

  } catch (ex: any) {
    el.innerHTML = `<div class="empty-state"><div class="empty-state-icon">⚠️</div><h3>Error loading meals</h3><p>${ex.message}</p></div>`
  }
}

// ── AI COACH PAGE ─────────────────────────────────────────────────────────────
async function renderAICoach(el: HTMLElement) {
  let targets: any = null
  try { targets = await apiFetch('/ai/targets') } catch {}

  const chatHistory: { role: 'user' | 'ai', text: string, foods?: string[] }[] = []
  const suggestedQuestions = [
    'What should I eat for breakfast?',
    'How many calories in 2 rotis with dal?',
    'Best high-protein Indian vegetarian foods?',
    'Is my diet good for weight loss?',
    'What to eat post-workout?',
  ]

  el.innerHTML = `
  <div class="section-header">
    <div>
      <h1 class="section-title">AI Health Coach</h1>
      <p class="section-subtitle">Powered by Gemini AI + Indian Food Database</p>
    </div>
    <button class="btn btn-violet btn-sm" id="setGoalsBtnAI">🎯 Recalculate Goals</button>
  </div>

  ${targets ? `
  <div class="card mb-4" style="border-color:rgba(139,92,246,0.3);background:var(--violet-glow)">
    <div class="card-title text-violet">🎯 Your AI-Generated Targets</div>
    <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(120px,1fr));gap:16px;margin-bottom:12px">
      ${[
        { label: 'Calories', val: Math.round(targets.target_calories || 0) + ' kcal', color: 'emerald' },
        { label: 'Protein', val: Math.round(targets.target_protein_g || 0) + 'g', color: 'violet' },
        { label: 'Carbs', val: Math.round(targets.target_carbs_g || 0) + 'g', color: 'amber' },
        { label: 'Fat', val: Math.round(targets.target_fat_g || 0) + 'g', color: 'rose' },
        { label: 'Water', val: Math.round((targets.target_water_ml || 0) / 1000 * 10) / 10 + 'L', color: 'sky' },
      ].map(t => `<div><div class="stat-label">${t.label}</div><div class="stat-value text-${t.color}" style="font-size:20px">${t.val}</div></div>`).join('')}
    </div>
    ${targets.explanation ? `<div style="font-size:13px;color:var(--text-secondary);padding:12px;background:var(--bg-card);border-radius:var(--radius-md)">${targets.explanation}</div>` : ''}
  </div>` : `
  <div class="card mb-4" style="border-color:rgba(139,92,246,0.3)">
    <div style="text-align:center;padding:8px">
      <p class="text-secondary">No AI targets set yet. Click below to let Gemini calculate your personalized nutrition targets.</p>
      <button class="btn btn-violet" style="margin-top:12px" id="calcGoalsBtn">🤖 Calculate My Goals</button>
    </div>
  </div>`}

  <div class="card chat-card">
    <div class="chat-messages" id="chatMessages">
      <div class="chat-message">
        <div class="chat-avatar ai">🤖</div>
        <div class="chat-bubble ai">
          Namaste! 🙏 I'm your NutriPulse AI coach. I can help you with Indian nutrition advice, meal planning, and fitness tips.<br><br>
          Try asking me something like:
          <div class="suggested-questions">
            ${suggestedQuestions.map(q => `<button class="suggested-q" data-q="${q}">${q}</button>`).join('')}
          </div>
        </div>
      </div>
    </div>
    <div class="chat-input-area">
      <textarea class="chat-input" id="chatInput" placeholder="Ask about Indian food, nutrition, or fitness..." rows="1"></textarea>
      <button class="btn btn-violet" id="chatSendBtn">Send ↗</button>
    </div>
  </div>`

  // Set goals buttons
  const handleSetGoals = async () => {
    const btn = document.getElementById('setGoalsBtnAI') || document.getElementById('calcGoalsBtn')
    if (btn) { (btn as HTMLButtonElement).disabled = true; btn.textContent = '⏳ Calculating...' }
    try {
      await apiFetch('/ai/set-goals', { method: 'POST', body: JSON.stringify({}) })
      toast('AI Goals calculated! 🎯'); renderAICoach(el)
    } catch (ex: any) { toast(ex.message, 'error'); if (btn) { (btn as HTMLButtonElement).disabled = false } }
  }

  document.getElementById('setGoalsBtnAI')?.addEventListener('click', handleSetGoals)
  document.getElementById('calcGoalsBtn')?.addEventListener('click', handleSetGoals)

  // Suggested questions
  document.querySelectorAll('.suggested-q').forEach(btn => {
    btn.addEventListener('click', () => {
      ;(document.getElementById('chatInput') as HTMLTextAreaElement).value = (btn as HTMLElement).dataset.q!
      sendChat()
    })
  })

  // Chat
  async function sendChat() {
    const inputEl = document.getElementById('chatInput') as HTMLTextAreaElement
    const msg = inputEl.value.trim()
    if (!msg) return
    inputEl.value = ''

    const messagesEl = document.getElementById('chatMessages')!
    chatHistory.push({ role: 'user', text: msg })

    messagesEl.innerHTML += `
    <div class="chat-message user">
      <div class="chat-avatar user">👤</div>
      <div class="chat-bubble user">${escapeHtml(msg)}</div>
    </div>`

    const thinkingEl = document.createElement('div')
    thinkingEl.className = 'chat-message'
    thinkingEl.innerHTML = `<div class="chat-avatar ai">🤖</div><div class="chat-bubble ai"><div class="typing-dots"><span></span><span></span><span></span></div></div>`
    messagesEl.appendChild(thinkingEl)
    messagesEl.scrollTop = messagesEl.scrollHeight

    const sendBtn = document.getElementById('chatSendBtn') as HTMLButtonElement
    sendBtn.disabled = true

    try {
      const res = await apiFetch('/ai/chat', { method: 'POST', body: JSON.stringify({ message: msg }) })
      thinkingEl.remove()
      const reply = res?.reply || 'Sorry, I could not generate a response.'
      const foods = res?.retrieved_foods || []
      chatHistory.push({ role: 'ai', text: reply, foods })
      messagesEl.innerHTML += `
      <div class="chat-message">
        <div class="chat-avatar ai">🤖</div>
        <div class="chat-bubble ai">
          ${formatChatReply(reply)}
          ${foods.length ? `<div class="chat-foods">📚 Referenced: ${foods.slice(0,3).join(', ')}</div>` : ''}
        </div>
      </div>`
    } catch (ex: any) {
      thinkingEl.remove()
      messagesEl.innerHTML += `<div class="chat-message"><div class="chat-avatar ai">🤖</div><div class="chat-bubble ai text-rose">⚠️ ${ex.message}</div></div>`
    } finally {
      sendBtn.disabled = false
      messagesEl.scrollTop = messagesEl.scrollHeight
    }
  }

  document.getElementById('chatSendBtn')?.addEventListener('click', sendChat)
  document.getElementById('chatInput')?.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendChat() }
  })
}

function formatChatReply(text: string): string {
  return text
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/\n\n/g, '</p><p>')
    .replace(/\n/g, '<br>')
    .replace(/^/, '<p>').replace(/$/, '</p>')
}

function escapeHtml(text: string): string {
  return text.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
}

// ── PROFILE PAGE ─────────────────────────────────────────────────────────────
async function renderProfile(el: HTMLElement) {
  try {
    const user = await apiFetch('/auth/me') || currentUser

    el.innerHTML = `
    <div class="section-header">
      <div>
        <h1 class="section-title">Profile & Settings</h1>
        <p class="section-subtitle">Manage your account and fitness goals</p>
      </div>
    </div>

    <div class="card" style="margin-bottom:20px">
      <div class="profile-header">
        <div class="profile-avatar">${(user.full_name || user.username || 'U').substring(0, 2).toUpperCase()}</div>
        <div class="profile-info">
          <h2>${user.full_name || user.username}</h2>
          <p>@${user.username} • ${user.email}</p>
          <p>Member since ${new Date(user.created_at).toLocaleDateString('en-IN', { month: 'long', year: 'numeric' })}</p>
        </div>
      </div>
    </div>

    <div class="card">
      <div class="card-title">✏️ Edit Profile</div>
      <form id="profileForm">
        <div class="form-row">
          <div class="form-group">
            <label class="form-label">Full Name</label>
            <input class="form-input" id="pFullName" value="${user.full_name || ''}">
          </div>
          <div class="form-group">
            <label class="form-label">Age</label>
            <input class="form-input" type="number" id="pAge" value="${user.age || ''}">
          </div>
        </div>
        <div class="form-row">
          <div class="form-group">
            <label class="form-label">Weight (kg)</label>
            <input class="form-input" type="number" id="pWeight" value="${user.weight_kg || ''}" step="0.1">
          </div>
          <div class="form-group">
            <label class="form-label">Height (cm)</label>
            <input class="form-input" type="number" id="pHeight" value="${user.height_cm || ''}">
          </div>
        </div>
        <div class="form-row">
          <div class="form-group">
            <label class="form-label">Gender</label>
            <select class="form-select" id="pGender">
              <option value="">Select</option>
              <option value="male" ${user.gender === 'male' ? 'selected' : ''}>Male</option>
              <option value="female" ${user.gender === 'female' ? 'selected' : ''}>Female</option>
              <option value="other" ${user.gender === 'other' ? 'selected' : ''}>Other</option>
            </select>
          </div>
          <div class="form-group">
            <label class="form-label">Activity Level</label>
            <select class="form-select" id="pActivity">
              ${['sedentary', 'light', 'moderate', 'active', 'very_active'].map(a =>
                `<option value="${a}" ${user.activity_level === a ? 'selected' : ''}>${a.charAt(0).toUpperCase() + a.slice(1).replace('_', ' ')}</option>`
              ).join('')}
            </select>
          </div>
        </div>
        <div class="form-row">
          <div class="form-group">
            <label class="form-label">Fitness Goal</label>
            <select class="form-select" id="pGoal">
              ${[['lose_fat','Lose Fat'],['maintain','Maintain'],['build_muscle','Build Muscle'],['endurance','Endurance']].map(([v, l]) =>
                `<option value="${v}" ${user.fitness_goal === v ? 'selected' : ''}>${l}</option>`
              ).join('')}
            </select>
          </div>
          <div class="form-group">
            <label class="form-label">Dietary Preference</label>
            <select class="form-select" id="pDiet">
              ${['Vegetarian','Non-Veg','High-Protein','Vegan'].map(d =>
                `<option value="${d}" ${user.dietary_preference === d ? 'selected' : ''}>${d}</option>`
              ).join('')}
            </select>
          </div>
        </div>
        <div id="profileFormMsg" style="display:none;margin-bottom:12px"></div>
        <div style="display:flex;gap:12px">
          <button class="btn btn-primary" type="submit" id="saveProfileBtn">Save Changes</button>
          <button class="btn btn-violet" type="button" id="recalcGoalsBtn">🤖 Recalculate AI Goals</button>
        </div>
      </form>
    </div>

    <div class="card" style="margin-top:20px;border-color:rgba(244,63,94,0.2)">
      <div class="card-title text-rose">⚠️ Danger Zone</div>
      <button class="btn btn-danger" id="logoutBtnProfile">Sign Out</button>
    </div>`

    document.getElementById('profileForm')?.addEventListener('submit', async (e) => {
      e.preventDefault()
      const btn = document.getElementById('saveProfileBtn') as HTMLButtonElement
      const msg = document.getElementById('profileFormMsg')!
      btn.disabled = true; btn.textContent = 'Saving...'
      const payload: any = {
        full_name: (document.getElementById('pFullName') as HTMLInputElement).value || null,
        age: parseInt((document.getElementById('pAge') as HTMLInputElement).value) || null,
        weight_kg: parseFloat((document.getElementById('pWeight') as HTMLInputElement).value) || null,
        height_cm: parseFloat((document.getElementById('pHeight') as HTMLInputElement).value) || null,
        gender: (document.getElementById('pGender') as HTMLSelectElement).value || null,
        activity_level: (document.getElementById('pActivity') as HTMLSelectElement).value,
        fitness_goal: (document.getElementById('pGoal') as HTMLSelectElement).value,
        dietary_preference: (document.getElementById('pDiet') as HTMLSelectElement).value,
      }
      try {
        const updated = await apiFetch('/auth/me', { method: 'PUT', body: JSON.stringify(payload) })
        if (updated) {
          currentUser = { ...currentUser, ...updated }
          localStorage.setItem('np_user', JSON.stringify(currentUser))
        }
        msg.className = 'form-success'; msg.textContent = '✓ Profile saved!'; msg.style.display = 'block'
        toast('Profile updated! ✓')
        setTimeout(() => msg.style.display = 'none', 3000)
      } catch (ex: any) {
        msg.className = 'form-error'; msg.textContent = ex.message; msg.style.display = 'block'
      } finally {
        btn.disabled = false; btn.textContent = 'Save Changes'
      }
    })

    document.getElementById('recalcGoalsBtn')?.addEventListener('click', async () => {
      const btn = document.getElementById('recalcGoalsBtn') as HTMLButtonElement
      btn.disabled = true; btn.textContent = '⏳ Calculating...'
      try {
        await apiFetch('/ai/set-goals', { method: 'POST', body: JSON.stringify({}) })
        toast('AI Goals recalculated! 🎯')
      } catch (ex: any) { toast(ex.message, 'error') } finally {
        btn.disabled = false; btn.textContent = '🤖 Recalculate AI Goals'
      }
    })

    document.getElementById('logoutBtnProfile')?.addEventListener('click', () => logout())

  } catch (ex: any) {
    el.innerHTML = `<div class="empty-state"><div class="empty-state-icon">⚠️</div><h3>Error loading profile</h3><p>${ex.message}</p></div>`
  }
}

// ── Bootstrap ─────────────────────────────────────────────────────────────────
renderApp()
