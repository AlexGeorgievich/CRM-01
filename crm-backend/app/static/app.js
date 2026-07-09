const apiBase = "/api/v1";

const state = {
  token: localStorage.getItem("crm_token"),
  user: null,
  leads: [],
  statuses: [],
  courses: [],
  sources: [],
  users: [],
  selectedLead: null,
};

const el = {
  loginView: document.querySelector("#loginView"),
  crmView: document.querySelector("#crmView"),
  loginForm: document.querySelector("#loginForm"),
  loginUsername: document.querySelector("#loginUsername"),
  loginPassword: document.querySelector("#loginPassword"),
  loginError: document.querySelector("#loginError"),
  currentUser: document.querySelector("#currentUser"),
  logoutButton: document.querySelector("#logoutButton"),
  filterStatus: document.querySelector("#filterStatus"),
  filterCourse: document.querySelector("#filterCourse"),
  filterSource: document.querySelector("#filterSource"),
  filterManager: document.querySelector("#filterManager"),
  filterSearch: document.querySelector("#filterSearch"),
  resetFiltersButton: document.querySelector("#resetFiltersButton"),
  newLeadButton: document.querySelector("#newLeadButton"),
  leadRows: document.querySelector("#leadRows"),
  leadCount: document.querySelector("#leadCount"),
  emptyDetail: document.querySelector("#emptyDetail"),
  leadDetail: document.querySelector("#leadDetail"),
  detailTitle: document.querySelector("#detailTitle"),
  deleteLeadButton: document.querySelector("#deleteLeadButton"),
  leadForm: document.querySelector("#leadForm"),
  leadId: document.querySelector("#leadId"),
  leadCustomerName: document.querySelector("#leadCustomerName"),
  leadContact: document.querySelector("#leadContact"),
  leadEmail: document.querySelector("#leadEmail"),
  leadCourse: document.querySelector("#leadCourse"),
  leadSource: document.querySelector("#leadSource"),
  leadStatus: document.querySelector("#leadStatus"),
  leadManager: document.querySelector("#leadManager"),
  leadNotes: document.querySelector("#leadNotes"),
  cancelEditButton: document.querySelector("#cancelEditButton"),
  commentList: document.querySelector("#commentList"),
  commentForm: document.querySelector("#commentForm"),
  commentBody: document.querySelector("#commentBody"),
  toast: document.querySelector("#toast"),
};

function authHeaders(extra = {}) {
  return {
    ...extra,
    Authorization: `Bearer ${state.token}`,
  };
}

async function api(path, options = {}) {
  const response = await fetch(`${apiBase}${path}`, options);
  if (response.status === 401) {
    logout();
    throw new Error("Требуется вход");
  }
  const contentType = response.headers.get("content-type") || "";
  const payload = contentType.includes("application/json") ? await response.json() : null;
  if (!response.ok) {
    throw new Error(payload?.detail || "Ошибка запроса");
  }
  return payload;
}

function showToast(message) {
  el.toast.textContent = message;
  el.toast.classList.remove("is-hidden");
  window.setTimeout(() => el.toast.classList.add("is-hidden"), 2800);
}

function switchView(isAuthenticated) {
  el.loginView.classList.toggle("is-hidden", isAuthenticated);
  el.crmView.classList.toggle("is-hidden", !isAuthenticated);
}

function optionList(items, placeholder = "Все") {
  const first = `<option value="">${placeholder}</option>`;
  return first + items.map((item) => `<option value="${item.id}">${item.name}</option>`).join("");
}

function managerOptions(users, placeholder = "Не назначен") {
  const first = `<option value="">${placeholder}</option>`;
  return first + users.map((user) => `<option value="${user.id}">${user.full_name}</option>`).join("");
}

function fillSelects() {
  el.filterStatus.innerHTML = optionList(state.statuses);
  el.filterCourse.innerHTML = optionList(state.courses);
  el.filterSource.innerHTML = optionList(state.sources);
  el.filterManager.innerHTML = managerOptions(state.users, "Все");
  el.leadStatus.innerHTML = optionList(state.statuses, "Выберите статус");
  el.leadCourse.innerHTML = optionList(state.courses, "Не выбран");
  el.leadSource.innerHTML = optionList(state.sources, "Не выбран");
  el.leadManager.innerHTML = managerOptions(state.users);
}

function renderLeads(total = state.leads.length) {
  el.leadCount.textContent = `${total} шт.`;
  if (!state.leads.length) {
    el.leadRows.innerHTML = `<tr><td colspan="6" class="muted">Заявок по текущим фильтрам нет</td></tr>`;
    return;
  }
  el.leadRows.innerHTML = state.leads
    .map(
      (lead) => `
        <tr>
          <td>
            <strong>${escapeHtml(lead.customer_name)}</strong><br />
            <span class="muted">${escapeHtml(lead.contact)}</span><br />
            <span class="muted">${escapeHtml(lead.email || "")}</span>
          </td>
          <td>${escapeHtml(lead.course?.name || "Не выбран")}</td>
          <td><span class="status-pill">${escapeHtml(lead.status?.name || "")}</span></td>
          <td>${escapeHtml(lead.source?.name || "Не выбран")}</td>
          <td>${escapeHtml(lead.assigned_manager?.full_name || "Не назначен")}</td>
          <td><button class="secondary-button" type="button" data-open="${lead.id}">Открыть</button></td>
        </tr>
      `,
    )
    .join("");
}

function openEmptyDetail() {
  state.selectedLead = null;
  el.emptyDetail.classList.remove("is-hidden");
  el.leadDetail.classList.add("is-hidden");
}

function openLeadForm(lead = null) {
  state.selectedLead = lead;
  el.emptyDetail.classList.add("is-hidden");
  el.leadDetail.classList.remove("is-hidden");
  el.detailTitle.textContent = lead ? `Заявка #${lead.id}` : "Новая заявка";
  el.deleteLeadButton.classList.toggle("is-hidden", !lead);
  el.leadId.value = lead?.id || "";
  el.leadCustomerName.value = lead?.customer_name || "";
  el.leadContact.value = lead?.contact || "";
  el.leadEmail.value = lead?.email || "";
  el.leadCourse.value = lead?.course_id || "";
  el.leadSource.value = lead?.source_id || "";
  el.leadStatus.value = lead?.status_id || state.statuses[0]?.id || "";
  el.leadManager.value = lead?.assigned_manager_id || state.user?.id || "";
  el.leadNotes.value = lead?.notes || "";
  renderComments(lead?.comments || []);
}

function renderComments(comments) {
  if (!state.selectedLead) {
    el.commentList.innerHTML = "";
    return;
  }
  if (!comments.length) {
    el.commentList.innerHTML = `<div class="muted">Комментариев пока нет</div>`;
    return;
  }
  el.commentList.innerHTML = comments
    .map(
      (comment) => `
        <article class="comment-item ${comment.is_system ? "system" : ""}">
          <div class="comment-meta">
            <span>${escapeHtml(comment.author?.full_name || "Система")}</span>
            <time>${formatDate(comment.created_at)}</time>
          </div>
          <div>${escapeHtml(comment.body)}</div>
        </article>
      `,
    )
    .join("");
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function formatDate(value) {
  return new Intl.DateTimeFormat("ru-RU", {
    day: "2-digit",
    month: "2-digit",
    year: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(value));
}

function collectFilters() {
  const params = new URLSearchParams();
  for (const [key, value] of [
    ["status_id", el.filterStatus.value],
    ["course_id", el.filterCourse.value],
    ["source_id", el.filterSource.value],
    ["assigned_manager_id", el.filterManager.value],
    ["search", el.filterSearch.value.trim()],
  ]) {
    if (value) params.set(key, value);
  }
  return params.toString();
}

async function loadCurrentUser() {
  state.user = await api("/auth/me", { headers: authHeaders() });
  el.currentUser.textContent = `${state.user.full_name} · ${state.user.role}`;
}

async function loadDictionaries() {
  const [statuses, courses, sources] = await Promise.all([
    api("/dictionaries/statuses", { headers: authHeaders() }),
    api("/dictionaries/courses", { headers: authHeaders() }),
    api("/dictionaries/sources", { headers: authHeaders() }),
  ]);
  state.statuses = statuses;
  state.courses = courses;
  state.sources = sources;
}

async function loadUsers() {
  if (state.user?.role !== "admin") {
    state.users = [state.user];
    return;
  }
  state.users = await api("/users", { headers: authHeaders() });
}

async function loadLeads() {
  const query = collectFilters();
  const result = await api(`/leads${query ? `?${query}` : ""}`, {
    headers: authHeaders(),
  });
  state.leads = result.items;
  renderLeads(result.total);
}

async function openLead(leadId) {
  const lead = await api(`/leads/${leadId}`, { headers: authHeaders() });
  openLeadForm(lead);
}

async function initApp() {
  if (!state.token) {
    switchView(false);
    return;
  }
  try {
    await loadCurrentUser();
    await loadDictionaries();
    await loadUsers();
    fillSelects();
    await loadLeads();
    openEmptyDetail();
    switchView(true);
  } catch (error) {
    logout();
  }
}

function logout() {
  state.token = null;
  localStorage.removeItem("crm_token");
  switchView(false);
}

el.loginForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  el.loginError.textContent = "";
  const body = new URLSearchParams({
    username: el.loginUsername.value.trim(),
    password: el.loginPassword.value,
  });
  try {
    const result = await api("/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body,
    });
    state.token = result.access_token;
    localStorage.setItem("crm_token", state.token);
    await initApp();
  } catch (error) {
    el.loginError.textContent = error.message;
  }
});

el.logoutButton.addEventListener("click", logout);
el.newLeadButton.addEventListener("click", () => openLeadForm());
el.cancelEditButton.addEventListener("click", openEmptyDetail);
el.resetFiltersButton.addEventListener("click", async () => {
  el.filterStatus.value = "";
  el.filterCourse.value = "";
  el.filterSource.value = "";
  el.filterManager.value = "";
  el.filterSearch.value = "";
  await loadLeads();
});

for (const input of [el.filterStatus, el.filterCourse, el.filterSource, el.filterManager]) {
  input.addEventListener("change", loadLeads);
}

el.filterSearch.addEventListener("input", () => {
  window.clearTimeout(el.filterSearch._timer);
  el.filterSearch._timer = window.setTimeout(loadLeads, 350);
});

el.leadRows.addEventListener("click", async (event) => {
  const button = event.target.closest("[data-open]");
  if (!button) return;
  await openLead(button.dataset.open);
});

el.leadForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  try {
    const leadId = el.leadId.value;
    const payload = {
      customer_name: el.leadCustomerName.value.trim(),
      contact: el.leadContact.value.trim(),
      email: el.leadEmail.value.trim() || null,
      notes: el.leadNotes.value.trim() || null,
      course_id: el.leadCourse.value ? Number(el.leadCourse.value) : null,
      source_id: el.leadSource.value ? Number(el.leadSource.value) : null,
      status_id: Number(el.leadStatus.value),
      assigned_manager_id: el.leadManager.value ? Number(el.leadManager.value) : null,
    };
    const saved = await api(leadId ? `/leads/${leadId}` : "/leads", {
      method: leadId ? "PATCH" : "POST",
      headers: authHeaders({ "Content-Type": "application/json" }),
      body: JSON.stringify(payload),
    });
    showToast("Заявка сохранена");
    await loadLeads();
    openLeadForm(saved);
  } catch (error) {
    showToast(error.message);
  }
});

el.deleteLeadButton.addEventListener("click", async () => {
  if (!state.selectedLead) return;
  const confirmed = window.confirm("Удалить заявку из рабочего списка?");
  if (!confirmed) return;
  await api(`/leads/${state.selectedLead.id}`, {
    method: "DELETE",
    headers: authHeaders(),
  });
  showToast("Заявка удалена");
  await loadLeads();
  openEmptyDetail();
});

el.commentForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  if (!state.selectedLead || !el.commentBody.value.trim()) return;
  try {
    await api(`/leads/${state.selectedLead.id}/comments`, {
      method: "POST",
      headers: authHeaders({ "Content-Type": "application/json" }),
      body: JSON.stringify({ body: el.commentBody.value.trim() }),
    });
    el.commentBody.value = "";
    await openLead(state.selectedLead.id);
    showToast("Комментарий добавлен");
  } catch (error) {
    showToast(error.message);
  }
});

initApp();
