/**
 * RRO Engineer Dashboard — JavaScript
 * ─────────────────────────────────────
 * Loads user + assigned workgroups via API and renders the dashboard dynamically.
 */

/* =========================================
   Configuration
   ========================================= */
const API_BASE = '';

/* =========================================
   State
   ========================================= */
let currentFilter = new URLSearchParams(window.location.search).get('filter') || 'all';

/* =========================================
   DOM References
   ========================================= */
const dom = {
    userAvatar: document.getElementById('userAvatar'),
    userName: document.getElementById('userName'),
    userRoleBadge: document.getElementById('userRoleBadge'),
    userRoleLabel: document.getElementById('userRoleLabel'),
    welcomeHeading: document.getElementById('welcomeHeading'),
    dropdownName: document.getElementById('dropdownName'),
    dropdownEmail: document.getElementById('dropdownEmail'),
    filterTabs: document.getElementById('filterTabs'),
    resultsCount: document.getElementById('resultsCount'),
    resultsPlural: document.getElementById('resultsPlural'),
    statTotal: document.getElementById('statTotal'),
    statActive: document.getElementById('statActive'),
    statCompleted: document.getElementById('statCompleted'),
    workgroupsList: document.getElementById('workgroupsList'),
    emptyState: document.getElementById('emptyState'),
};

/* =========================================
   API Helpers
   ========================================= */
async function apiFetch(path, options = {}) {
    try {
        const res = await fetch(`${API_BASE}${path}`, {
            credentials: 'include',
            headers: { 'Content-Type': 'application/json', ...options.headers },
            ...options,
        });
        if (!res.ok) throw new Error(`HTTP ${res.status} ${res.statusText}`);
        return await res.json();
    } catch (error) {
        console.warn(`[API] ${options.method || 'GET'} ${path} → ${error.message}`);
        return null;
    }
}

/* =========================================
   Renderers
   ========================================= */
function renderUserInfo(user) {
    if (!user) return;

    const fullName = user.fullName || user.name || 'Engineer';
    const nameParts = fullName.split(' ').filter(Boolean);
    const initials = nameParts.map((p) => p[0]).join('').slice(0, 2).toUpperCase();
    const firstName = nameParts[0] || fullName;

    dom.userAvatar.textContent = initials || '?';
    dom.userName.textContent = fullName;
    dom.userRoleBadge.textContent = user.role || 'Engineer';
    dom.userRoleLabel.textContent = user.role || 'Engineer';
    dom.welcomeHeading.textContent = `Welcome, ${firstName}!`;
    dom.dropdownName.textContent = fullName;
    dom.dropdownEmail.textContent = user.email || '';
}

function renderStats(stats) {
    if (!stats) return;
    dom.statTotal.textContent = stats.total ?? 0;
    dom.statActive.textContent = stats.active ?? 0;
    dom.statCompleted.textContent = stats.completed ?? 0;
}

function renderWorkgroups(workgroups) {
    dom.workgroupsList.innerHTML = '';

    const count = Array.isArray(workgroups) ? workgroups.length : 0;
    dom.resultsCount.textContent = count;
    dom.resultsPlural.textContent = count === 1 ? '' : 's';

    if (count === 0) {
        dom.emptyState.classList.remove('hidden');
        return;
    }

    dom.emptyState.classList.add('hidden');

    workgroups.forEach((wg) => {
        dom.workgroupsList.appendChild(createWorkgroupCard(wg));
    });
}

function createWorkgroupCard(wg) {
    const outer = document.createElement('a');
    outer.href = `/engineer/bug_management?workgroup_id=${wg.id}`;
    outer.className = 'max-w-xs bg-white rounded-2xl shadow-sm border border-slate-100 overflow-hidden relative group block transition-transform hover:scale-[1.02] hover:shadow-md';

    outer.innerHTML = `
        <div class="h-1.5 bg-indigo-500 w-full"></div>
        <div class="p-6">
            <div class="flex items-center justify-between mb-2">
                <h3 class="text-lg font-bold text-slate-900">${escapeHtml(wg.name)}</h3>
                <span class="${wg.is_completed === 'Completed' ? 'bg-emerald-50 text-emerald-600' : 'bg-indigo-50 text-indigo-600'} text-[10px] font-bold px-2 py-0.5 rounded-md">
                    ${wg.is_completed}
                </span>
            </div>
            <div class="flex items-center text-slate-400 mb-6">
                <svg xmlns="http://www.w3.org/2000/svg" class="w-3.5 h-3.5 mr-1.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                </svg>
                <span class="text-xs font-medium">Managed by ${escapeHtml(wg.manager?.first_name || '')} ${escapeHtml(wg.manager?.last_name || '')}</span>
            </div>
            <div class="bg-indigo-50/50 rounded-xl p-3 flex items-center justify-between mb-6 border border-indigo-100/50">
                <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4 mr-2 transform rotate-45" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M4.5 16.5c-1.5 1.26-2 5-2 5s3.74-.5 5-2c.71-.84.7-2.13-.09-2.91a2.18 2.18 0 0 0-2.91-.09z" />
                    <path d="m12 15-3-3a22 22 0 0 1 2-3.95A12.88 12.88 0 0 1 22 2c0 2.72-.78 7.5-6 11a22.35 22.35 0 0 1-4 2z" />
                    <path d="m9 12 2.5-2.5" />
                    <path d="m12 15 2.5-2.5" />
                </svg>
                <span class="text-xs font-bold uppercase tracking-wider">Release</span>
                <span class="text-sm font-black text-indigo-700">${escapeHtml(wg.release_version)}</span>
            </div>
            <div class="space-y-3 pt-2 border-t border-slate-50">
                <div class="text-[10px] font-bold text-slate-500 uppercase">Team (${(wg.engineers || []).length} engineers)</div>
                ${((wg.engineers || []).map((eng) => {
        const initials = `${(eng.first_name || '').charAt(0)}${(eng.last_name || '').charAt(0)}`.toUpperCase();
        return `
                        <div class="flex items-center space-x-2 bg-slate-50 p-1.5 rounded-lg border border-slate-100/50">
                            <div class="w-6 h-6 bg-sky-500 rounded-full flex items-center justify-center text-[8px] font-bold text-white uppercase border border-white">${escapeHtml(initials)}</div>
                            <span class="text-xs font-bold text-slate-700">${escapeHtml(eng.first_name || '')} ${escapeHtml(eng.last_name || '')}</span>
                        </div>`;
    })).join('')}
            </div>
        </div>
    `;

    return outer;
}

function updateFilterUI(filter) {
    const buttons = dom.filterTabs.querySelectorAll('a[data-filter]');
    buttons.forEach((btn) => {
        const isActive = btn.dataset.filter === filter;
        btn.classList.toggle('bg-white', isActive);
        btn.classList.toggle('shadow-sm', isActive);
        btn.classList.toggle('text-indigo-600', isActive);
        btn.classList.toggle('text-slate-500', !isActive);
    });
}

function escapeHtml(str) {
    return String(str || '').replace(/[&<>"]+/g, (match) => {
        const esc = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
        };
        return esc[match] || match;
    });
}

/* =========================================
   Data Loaders
   ========================================= */

async function loadCurrentUser() {
    const data = await apiFetch('/api/auth/me');
    if (data) {
        renderUserInfo(data);
    }
}

async function loadStats() {
    const data = await apiFetch('/api/engineer/stats');
    if (data) {
        renderStats(data);
    }
}

async function loadWorkgroups(filter = 'all') {
    updateFilterUI(filter);
    currentFilter = filter;

    const data = await apiFetch(`/api/engineer/workgroups?filter=${encodeURIComponent(filter)}`);
    if (Array.isArray(data)) {
        renderWorkgroups(data);
    } else {
        renderWorkgroups([]);
    }
}

/* =========================================
   Event Handlers
   ========================================= */

function handleFilterClick(event) {
    const el = event.target.closest('a[data-filter]');
    if (!el) return;
    event.preventDefault();
    const filter = el.dataset.filter;
    if (!filter) return;
    const url = new URL(window.location.href);
    url.searchParams.set('filter', filter);
    window.history.replaceState({}, '', url);
    loadWorkgroups(filter);
}

/* =========================================
   Initialize
   ========================================= */

function init() {
    dom.filterTabs.addEventListener('click', handleFilterClick);
    loadCurrentUser();
    loadStats();
    loadWorkgroups(currentFilter);
}

window.addEventListener('DOMContentLoaded', init);

/* =========================================
   Feature: Dynamic Search & Autocomplete
   ========================================= */
(function () {
    const searchInput = document.getElementById('workgroupSearch');
    const workgroupsList = document.getElementById('workgroupsList');
    const suggestionsBox = document.getElementById('searchSuggestions');
    const resultsCount = document.getElementById('resultsCount');
    const resultsPlural = document.getElementById('resultsPlural');

    if (!searchInput || !workgroupsList || !suggestionsBox) return;

    function getWorkgroupNames() {
        return Array.from(workgroupsList.children).map(card => {
            const h3 = card.querySelector('h3');
            return h3 ? h3.textContent : '';
        }).filter(Boolean);
    }

    function filterCards(query) {
        const cards = workgroupsList.children;
        let visibleCount = 0;
        const lowerQuery = query.toLowerCase().trim();

        for (const card of cards) {
            const title = card.querySelector('h3').textContent.toLowerCase();
            if (title.includes(lowerQuery)) {
                card.classList.remove('hidden');
                visibleCount++;
            } else {
                card.classList.add('hidden');
            }
        }

        if (resultsCount) resultsCount.textContent = visibleCount;
        if (resultsPlural) resultsPlural.textContent = visibleCount === 1 ? '' : 's';
    }

    function showSuggestions(query) {
        const names = getWorkgroupNames();
        const lowerQuery = query.toLowerCase().trim();

        if (!lowerQuery) {
            suggestionsBox.innerHTML = '';
            suggestionsBox.classList.add('hidden');
            return;
        }

        const matches = names.filter(name => name.toLowerCase().includes(lowerQuery));

        if (matches.length > 0) {
            suggestionsBox.innerHTML = matches.map(name => `
                <div class="px-4 py-3 hover:bg-slate-50 cursor-pointer text-sm font-medium text-slate-700 border-b border-slate-50 last:border-0 transition-colors">
                    ${escapeHtml(name)}
                </div>
            `).join('');
            suggestionsBox.classList.remove('hidden');
        } else {
            suggestionsBox.innerHTML = '';
            suggestionsBox.classList.add('hidden');
        }
    }

    searchInput.addEventListener('input', (e) => {
        const query = e.target.value;
        filterCards(query);
        showSuggestions(query);
    });

    suggestionsBox.addEventListener('click', (e) => {
        const item = e.target.closest('div');
        if (!item) return;

        const selectedName = item.textContent.trim();
        searchInput.value = selectedName;
        suggestionsBox.classList.add('hidden');
        filterCards(selectedName);
    });

    // Close suggestions on blur or outside click
    document.addEventListener('click', (e) => {
        if (!searchInput.contains(e.target) && !suggestionsBox.contains(e.target)) {
            suggestionsBox.classList.add('hidden');
        }
    });

    // MutationObserver to fix search when tabs change
    const observer = new MutationObserver(() => {
        filterCards(searchInput.value);
    });
    observer.observe(workgroupsList, { childList: true });
})();

