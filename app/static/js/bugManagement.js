/**
 * RRO Manager Dashboard — JavaScript
 * ─────────────────────────────────────
 * Handles dynamic data loading, modal interactions, and workgroup management.
 * All data is fetched from / sent to backend APIs.
 * Falls back to local mock data when the backend is unavailable, so the
 * page works standalone for development and demo purposes.
 *
 * ┌──────────────────────────────────────────────────────────────────┐
 * │  API ENDPOINTS USED (configure API_BASE below)                  │
 * │                                                                  │
 * │  GET    /api/auth/me         → current logged-in user            │
 * │  GET    /api/stats           → dashboard stat counts             │
 * │  GET    /api/workgroups      → list manager's workgroups         │
 * │  POST   /api/workgroups      → create a new workgroup            │
 * │  PATCH  /api/workgroups/:id  → update a workgroup                │
 * │  DELETE /api/workgroups/:id  → delete a workgroup                │
 * │  GET    /api/engineers       → list registered engineers         │
 * └──────────────────────────────────────────────────────────────────┘
 */

/* =========================================
   Configuration — CHANGE THIS TO YOUR BACKEND URL
   ========================================= */
const API_BASE = ''; // Change this to your backend URL

/* =========================================
   State
   ========================================= */
let currentUser = null;
let workgroups = [];
let engineers = [];
let currentFilter = 'all';

/* =========================================
   DOM References
   ========================================= */
const $ = (sel) => document.querySelector(sel);
const $$ = (sel) => document.querySelectorAll(sel);

const dom = {
    userName: $('#userName'),
    userAvatar: $('#userAvatar'),
    userRoleBadge: $('#userRoleBadge'),
    profileDropdownTrigger: $('#profileDropdownTrigger'),
    profileDropdown: $('#profileDropdown'),
    profileEmail: $('#profileEmail'),
    btnLogout: $('#btnLogout'),
    statTotalBugs: $('#statTotalBugs'),
    statReproBugs: $('#statReproBugs'),
    statTestBugs: $('#statTestBugs'),
    statPendingActions: $('#statPendingActions'),
    reproBugsCount: $('#reproBugsCount'),
    testBugsCount: $('#testBugsCount'),
    reproBugsBody: $('#reproBugsBody'),
    testBugsBody: $('#testBugsBody')
};

/* =========================================
   API Helper
   ========================================= */

/**
 * Generic fetch wrapper. Returns parsed JSON on success, null on failure.
 * Always logs errors to console for debugging.
 */
async function apiFetch(path, options = {}) {
    try {
        const res = await fetch(`${API_BASE}${path}`, {
            headers: { 'Content-Type': 'application/json', ...options.headers },
            credentials: 'include',
            ...options,
        });
        if (!res.ok) throw new Error(`HTTP ${res.status} ${res.statusText}`);
        return await res.json();
    } catch (err) {
        console.warn(`[API] ${options.method || 'GET'} ${path} → ${err.message}`);
        return null;
    }
}

/* =========================================
   Mock / Fallback Data
   (used when backend is not running)
   ========================================= */

function getMockUser() {
    return { id: 1, name: 'Rishi', fullName: 'Rishi N', email: 'rishi@rro.com', role: 'Manager' };
}

function computeLocalStats() {
    return {
        total: workgroups.length,
        active: workgroups.filter(w => !w.is_completed).length,
        completed: workgroups.filter(w => w.is_completed).length,
        engineers: engineers.length,
    };
}

/* =========================================
   Data Loaders — fetch from API, fallback to mock
   ========================================= */

/** GET /api/auth/me → populate user info in navbar + welcome heading */
async function loadCurrentUser() {
    const data = await apiFetch('/api/auth/me');
    currentUser = data || getMockUser();
    renderUserInfo();
}

async function loadBugsData(){
    const data = await apiFetch('/api/bugs');
    const stats = await apiFetch('/api/bugs/stats');
    if(stats){
        renderStats(stats);
    }
    if(data){
        renderBugs(data.repro, data.test);
    }
}

/** Refresh all dynamic data (called after mutations) */
async function refreshAll() {
    await Promise.all([loadBugsData()]);
}

/* =========================================
   Renderers
   ========================================= */

function renderUserInfo() {
    if (!currentUser) return;

    // Remove loading states
    if (dom.userAvatar) dom.userAvatar.classList.remove('loading-pulse');
    if (dom.userName) dom.userName.classList.remove('loading-text');

    const initials = currentUser.fullName
        ? currentUser.fullName.split(' ').map(n => n[0]).join('').toUpperCase()
        : currentUser.name[0].toUpperCase();

    if (dom.userAvatar) dom.userAvatar.textContent = initials;
    if (dom.userName) dom.userName.textContent = currentUser.fullName || currentUser.name;
    if (dom.userRoleBadge) dom.userRoleBadge.textContent = currentUser.role || 'Manager';
    if (dom.profileEmail) dom.profileEmail.textContent = currentUser.email || 'manager@rro.com';
}

function renderStats(stats) {
    animateNumber(dom.statTotalBugs, stats.totalBugs);
    animateNumber(dom.statReproBugs, stats.reproBugs);
    animateNumber(dom.statTestBugs, stats.testBugs);
    animateNumber(dom.statPendingActions, stats.pendingActions);
}

function animateNumber(el, target) {
    const duration = 500;
    const current = el.textContent;
    const start = (current === '—' || current === '') ? 0 : parseInt(current) || 0;
    if (start === target) { el.textContent = target; return; }
    const startTime = performance.now();
    function tick(now) {
        const progress = Math.min((now - startTime) / duration, 1);
        const eased = 1 - Math.pow(1 - progress, 3);
        el.textContent = Math.round(start + (target - start) * eased);
        if (progress < 1) requestAnimationFrame(tick);
    }
    requestAnimationFrame(tick);
}

function generateBadgesHtml(items, type) {
    if (!items || !items.length) return '';
    const badgeClass = type === 'test' ? 'badge--blue' : 'badge--yellow';

    // Display max 2 items
    const MAX_ITEMS = 2;
    const visibleItems = items.slice(0, MAX_ITEMS);
    const hiddenCount = items.length - MAX_ITEMS;

    let html = visibleItems.map(item => `<span class="badge ${badgeClass}">${escapeHtml(item)}</span>`).join('');

    if (hiddenCount > 0) {
        html += `<span class="badge badge--gray">+${hiddenCount}</span>`;
    }

    return html;
}

function generateBugsTableRows(bugs) {
    return bugs.map(bug => `
        <tr class="bug-row" onmouseenter="this.style.backgroundColor='#f1f5f9'" onmouseleave="this.style.backgroundColor=''">
            <td class="bug-id-cell">${escapeHtml(bug.id)}</td>
            <td class="engineer-cell">
                <div class="engineer-avatar" style="background: ${bug.engineer.color}">${escapeHtml(bug.engineer.initials)}</div>
                <span class="engineer-name">${escapeHtml(bug.engineer.name)}</span>
            </td>
            <td>
                <div class="tests-cell">
                    ${generateBadgesHtml(bug.tests, 'test')}
                </div>
            </td>
            <td>
                <div class="stations-cell">
                    ${generateBadgesHtml(bug.stations, 'station')}
                </div>
            </td>
            <td class="config-cell">${escapeHtml(bug.config)}</td>
            <td>
                <input type="text" class="resource-input" placeholder="Enter group..." value="${escapeHtml(bug.resourceGroup)}" />
            </td>
            <td>
                <div class="action-cell">
                    <button class="btn-action btn-run">
                        <svg width="12" height="12" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 3L12 8L4 13V3Z" fill="currentColor" stroke="none"/></svg>
                        Run Now
                    </button>
                    <button class="btn-action btn-later">
                        <svg width="14" height="14" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="8" cy="8" r="7"/><path d="M8 4V8L11 10"/></svg>
                        Run Later
                    </button>
                </div>
            </td>
        </tr>
    `).join('');
}

function renderBugs(reproBugs, testBugs) {
    dom.reproBugsCount.textContent = `${reproBugs.length} bugs`;
    dom.testBugsCount.textContent = `${testBugs.length} bugs`;

    dom.reproBugsBody.innerHTML = generateBugsTableRows(reproBugs);
    dom.testBugsBody.innerHTML = generateBugsTableRows(testBugs);
}

/* =========================================
   Event Listeners
   ========================================= */

function initEventListeners() {
    // Profile Dropdown
    dom.profileDropdownTrigger.addEventListener('click', (e) => {
        e.stopPropagation();
        closeAllDropdowns();
        dom.profileDropdown.classList.toggle('hidden');
    });

    // Logout
    dom.btnLogout.addEventListener('click', async () => {
        await apiFetch('/api/auth/logout', { method: 'POST' });
        // In local mock, simply reset currentUser
        currentUser = null;
        alert('Logged out locally (mock).');
        window.location.href = "/";
    });

    // Section Collapse Toggles
    const bugHeaders = document.querySelectorAll('.bugs-header');
    bugHeaders.forEach(header => {
        header.addEventListener('click', () => {
            const section = header.closest('.bugs-section');
            if (section) {
                section.classList.toggle('collapsed');
            }
        });
    });
}

function closeAllDropdowns() {
    dom.profileDropdown.classList.add('hidden');
}

// Close dropdowns on outside click
document.addEventListener('click', () => closeAllDropdowns());

/* =========================================
   Utilities
   ========================================= */

function escapeHtml(str) {
    if (str == null) return '';
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}

/* =========================================
   Init — runs on page load
   ========================================= */

async function init() {
    initEventListeners();
    await loadCurrentUser();
    await loadBugsData();
}

document.addEventListener('DOMContentLoaded', init);
