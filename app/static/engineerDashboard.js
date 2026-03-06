const API_BASE = ""

let currentUser = null
let workgroups = []
let currentFilter = "all"

const $ = (s) => document.querySelector(s)

const dom = {

    userName: $("#userName"),
    userAvatar: $("#userAvatar"),
    userRoleBadge: $("#userRoleBadge"),
    welcomeHeading: $("#welcomeHeading"),

    statTotal: $("#statTotal"),
    statActive: $("#statActive"),
    statCompleted: $("#statCompleted"),

    workgroupsList: $("#workgroupsList"),
    workgroupsLoading: $("#workgroupsLoading"),
    emptyState: $("#emptyState"),

    profileDropdownTrigger: $("#profileDropdownTrigger"),
    profileDropdown: $("#profileDropdown"),
    profileEmail: $("#profileEmail"),
    btnLogout: $("#btnLogout")

}

async function apiFetch(path, options = {}) {

    const res = await fetch(API_BASE + path, {
    credentials: "include",
    headers: {"Content-Type":"application/json"},
    ...options
    })

    return await res.json()

}


async function loadCurrentUser(){

    const data = await apiFetch("/api/auth/me")

    currentUser = data

    const initials = data.fullName
    .split(" ")
    .map(n=>n[0])
    .join("")
    .toUpperCase()

    dom.userAvatar.textContent = initials
    dom.userName.textContent = data.fullName
    dom.userRoleBadge.textContent = "Engineer"
    dom.profileEmail.textContent = data.email

    dom.welcomeHeading.textContent =
    `Welcome back, ${data.name}!`

}


async function loadStats(){

    const stats = await apiFetch("/api/stats")

    dom.statTotal.textContent = stats.total
    dom.statActive.textContent = stats.active
    dom.statCompleted.textContent = stats.completed

}


async function loadWorkgroups(){

    dom.workgroupsLoading.classList.remove("hidden")

    const data = await apiFetch("/api/workgroups")

    workgroups = data

    dom.workgroupsLoading.classList.add("hidden")

    renderWorkgroups()

}


function renderWorkgroups(){

    dom.workgroupsList.innerHTML=""

    if(workgroups.length===0){

    dom.emptyState.classList.remove("hidden")
    return

    }

    dom.emptyState.classList.add("hidden")

    workgroups.forEach(wg=>{

    const card = document.createElement("div")

    card.className="workgroup-card"

    const statusClass =
    wg.is_completed ?
    "status-badge--completed" :
    "status-badge--active"

    const statusText =
    wg.is_completed ?
    "Completed":
    "Active"

    const date = new Date(wg.created_at)
    .toLocaleDateString()

    const engineers =
    wg.engineers.length

    card.innerHTML=`

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

    <span class="status-badge ${statusClass}">
    ${statusText}
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

    <div class="wg-card-engineers">

    ${engineers} engineer${engineers>1?"s":""} assigned

    </div>

    <div class="wg-card-footer">

    <span class="wg-card-date">
    ${date}
    </span>

    </div>

    `

    dom.workgroupsList.appendChild(card)

    })

}


async function logout(){

    await fetch("/api/auth/logout",{
    method:"POST",
    credentials:"include"
    })

    window.location="/"

}


function setupEvents(){

    dom.btnLogout.addEventListener("click",logout)

    dom.profileDropdownTrigger.addEventListener("click",()=>{

    dom.profileDropdown.classList.toggle("hidden")

    })

}


async function init(){

    await loadCurrentUser()

    await Promise.all([
    loadStats(),
    loadWorkgroups()
    ])

    setupEvents()

}

init()