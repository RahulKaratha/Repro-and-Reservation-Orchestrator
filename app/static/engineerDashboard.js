/* =====================================================
   RRO Engineer Dashboard
===================================================== */

const API_BASE = "";

/* =====================================================
   State
===================================================== */

let currentUser = null;
let workgroups = [];

/* =====================================================
   Helpers
===================================================== */

const $ = (selector) => document.querySelector(selector);

/* =====================================================
   DOM Elements
===================================================== */

const dom = {

    userName: $("#userName"),
    userAvatar: $("#userAvatar"),
    profileEmail: $("#profileEmail"),
    welcomeHeading: $("#welcomeHeading"),

    statAssigned: $("#statAssigned"),
    statActive: $("#statActive"),
    statCompleted: $("#statCompleted"),

    workgroupsList: $("#workgroupsList"),
    workgroupsLoading: $("#workgroupsLoading"),
    emptyState: $("#emptyState"),

    btnLogout: $("#btnLogout"),

    profileDropdown: $("#profileDropdown"),
    profileTrigger: $("#profileDropdownTrigger")

};

/* =====================================================
   API Helper
===================================================== */

async function apiFetch(path, options = {}) {

    const response = await fetch(`${API_BASE}${path}`, {
        credentials: "include",
        headers: {
            "Content-Type": "application/json"
        },
        ...options
    });

    return await response.json();
}

/* =====================================================
   Load User
===================================================== */

async function loadCurrentUser() {

    const data = await apiFetch("/api/auth/me");

    currentUser = data;

    const initials = data.fullName
        .split(" ")
        .map(n => n[0])
        .join("")
        .toUpperCase();

    dom.userAvatar.classList.remove("loading-pulse");
    dom.userAvatar.textContent = initials;

    dom.userName.classList.remove("loading-text");
    dom.userName.textContent = data.fullName;

    dom.profileEmail.textContent = data.email;

    dom.welcomeHeading.classList.remove("loading-text");
    dom.welcomeHeading.textContent = `Welcome back, ${data.name}!`;
}

/* =====================================================
   Load Stats
===================================================== */

async function loadStats() {

    const stats = await apiFetch("/api/engineer/stats");

    dom.statAssigned.textContent = stats.assigned;
    dom.statActive.textContent = stats.active;
    dom.statCompleted.textContent = stats.completed;
}

/* =====================================================
   Load Workgroups
===================================================== */

async function loadWorkgroups() {

    const data = await apiFetch("/api/engineer/workgroups");

    workgroups = data || [];

    dom.workgroupsLoading.classList.add("hidden");

    renderWorkgroups();
}

/* =====================================================
   Render Workgroups
===================================================== */

function renderWorkgroups() {

    dom.workgroupsList.innerHTML = "";

    if (workgroups.length === 0) {

        dom.emptyState.classList.remove("hidden");
        return;
    }

    dom.emptyState.classList.add("hidden");

    workgroups.forEach(wg => {

        const card = document.createElement("div");
        card.className = "workgroup-card";

        const status = wg.is_completed ? "Completed" : "Active";

        const date = new Date(wg.created_at)
            .toLocaleDateString();

        card.innerHTML = `
            <div class="wg-card-top-bar"></div>

            <div class="wg-card-header">

                <div class="wg-card-header-left">

                    <span class="wg-card-initials">
                        ${wg.name.substring(0,2)}
                    </span>

                    <h4 class="wg-card-name">
                        ${wg.name}
                    </h4>

                </div>

                <span class="status-badge">
                    ${status}
                </span>

            </div>

            <div class="wg-card-release">

                <span class="wg-release-badge">
                    Release
                </span>

                <span class="wg-release-version">
                    ${wg.release_version}
                </span>

            </div>

            <div class="wg-card-footer">

                <span class="wg-card-date">
                    Created ${date}
                </span>

            </div>
        `;

        dom.workgroupsList.appendChild(card);
    });
}

/* =====================================================
   Logout
===================================================== */

async function logout() {

    await fetch("/api/auth/logout", {
        method: "POST",
        credentials: "include"
    });

    window.location.href = "/";
}

function toggleProfileDropdown() {

    dom.profileDropdown.classList.toggle("hidden");

}

function closeDropdownOnOutsideClick(event) {

    if (!dom.profileTrigger.contains(event.target)) {

        dom.profileDropdown.classList.add("hidden");

    }

}

/* =====================================================
   Event Listeners
===================================================== */

function setupEvents() {

    dom.btnLogout.addEventListener("click", logout);

    dom.profileTrigger.addEventListener("click", toggleProfileDropdown);

    document.addEventListener("click", closeDropdownOnOutsideClick);

}

/* =====================================================
   Initialize Dashboard
===================================================== */

async function init() {

    await loadCurrentUser();

    await Promise.all([
        loadStats(),
        loadWorkgroups()
    ]);

    setupEvents();
}

init();