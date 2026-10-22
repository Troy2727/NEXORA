import { api, clearToken, getToken } from "./api.js";
import { renderBoard } from "./board.js";
import { renderCalendar, startOfWeek } from "./calendar.js";
import { renderChat, unreadCount } from "./chat.js";
import { renderGoals } from "./goals.js";
import { clearLocal, loadLocal, saveLocal, useAccount } from "./local.js";
import { renderOverview } from "./overview.js";
import { paintAvatars, toAvatarDataUrl } from "./photo.js";
import { exportCsv, renderReports } from "./reports.js";
import { fillAccount, fullName, initSettings } from "./settings.js";
import { parseDate } from "./shared.js";
import { renderTeam } from "./team.js";
import { renderTime } from "./time.js";

const $ = (id) => document.getElementById(id);
const now = new Date();
const state = {
  tasks: [],
  view: "overview",
  query: "",
  editing: null,
  loaded: false,
  cal: { week: startOfWeek(now), month: new Date(now.getFullYear(), now.getMonth(), 1), query: "" },
  local: loadLocal(),
  team: null,
  invites: [],
  messages: [],
};

const RENDERERS = {
  overview: () => renderOverview(state.tasks),
  board: () => renderBoard($("board"), state.tasks, state.query),
  calendar: () => renderCalendar(state.tasks, state.cal),
  time: () => renderTime(state.tasks, state.local),
  goals: () => renderGoals(state.tasks, state.local),
  reports: () => renderReports(state.tasks),
  team: () => renderTeam({ team: state.team, invites: state.invites, me: state.user }),
  messages: () => {
    renderChat({ team: state.team, messages: state.messages, me: state.user });
    markRead();
  },
  settings: () => {},
};

function toggleTimer() {
  const local = state.local;
  if (local.running) {
    local.entries.push({ ...local.running, end: Date.now() });
    local.running = null;
    toast("Time saved");
  } else {
    const taskId = Number($("timer-task").value);
    if (!taskId) return;
    local.running = { taskId, start: Date.now() };
  }
  saveLocal(local);
  render();
}

// Charts are drawn at the on-screen width, so redraw them when it changes.
let resizeTimer;
window.addEventListener("resize", () => {
  clearTimeout(resizeTimer);
  resizeTimer = setTimeout(() => state.loaded && render(), 150);
});

// Keep a running timer's clock (and anything built on it) live.
setInterval(() => {
  if (state.local.running && (state.view === "time" || state.view === "goals")) render();
}, 1000);

function signOut() {
  clearToken();
  location.replace("auth.html");
}

// Any expired or missing session sends the user back to sign in.
async function call(promise) {
  try {
    return await promise;
  } catch (err) {
    // 403 also means "not your team's" (e.g. a member trying an owner action); only
    // a missing/invalid login should sign you out.
    if (err.status === 401 || (err.status === 403 && err.message === "Not authenticated")) signOut();
    throw err;
  }
}

let toastTimer;
function toast(text, isError = false) {
  const el = $("toast");
  el.textContent = text;
  el.classList.toggle("error", isError);
  el.hidden = false;
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => { el.hidden = true; }, 2600);
}

function render() {
  const open = state.tasks.filter((t) => t.status !== "completed").length;
  $("nav-count").textContent = open;
  $("nav-count").hidden = open === 0;
  $("nav-timer").hidden = !state.local.running;

  // New accounts get a welcome screen instead of empty charts.
  const welcome = state.loaded && state.view === "overview" && !state.tasks.length;
  $("welcome").hidden = !welcome;
  for (const section of document.querySelectorAll("main > .view")) {
    section.hidden = welcome || section.id !== `view-${state.view}`;
  }
  RENDERERS[state.view]();

  const unread = state.team && state.user ? unreadCount(state.messages, state.local.lastRead ?? 0, state.user.id) : 0;
  $("nav-unread").textContent = unread > 99 ? "99+" : unread;
  $("nav-unread").hidden = unread === 0;
  $("nav-invites").textContent = state.invites.length;
  $("nav-invites").hidden = !state.invites.length;
}

/* Team + messages */

// Everything you've looked at in the chat counts as read.
function markRead() {
  const last = state.messages.at(-1);
  if (!last || document.visibilityState !== "visible" || (state.local.lastRead ?? 0) >= last.id) return;
  state.local.lastRead = last.id;
  saveLocal(state.local);
}

async function loadTeam() {
  const [team, invites] = await Promise.all([call(api.getTeam()), call(api.myInvites())]);
  state.team = team;
  state.invites = invites;
  state.messages = team ? await call(api.messages()) : [];
  // First visit: existing history counts as read, so only new messages show as unread.
  if (state.local.lastRead === undefined) {
    state.local.lastRead = state.messages.at(-1)?.id ?? 0;
    saveLocal(state.local);
  }
}

// New messages every 5 s; team details and invites every 30 s.
let pollTick = 0;
setInterval(async () => {
  if (!state.loaded || !state.user) return;
  pollTick += 1;
  try {
    if (pollTick % 6 === 0) {
      await loadTeam();
    } else if (state.team) {
      const fresh = await call(api.messages(state.messages.at(-1)?.id));
      if (!fresh.length) return;
      state.messages = [...state.messages, ...fresh];
    } else {
      return;
    }
    render();
  } catch (err) {
    if (err.status === 404) await loadTeam().then(render, () => {}); // removed from the team
  }
}, 5000);

async function teamAction(work, done) {
  try {
    await work();
    await loadTeam();
    render();
    if (done) toast(done);
  } catch (err) {
    toast(err.message, true);
  }
}

const TEAM_FORMS = {
  "team-create": (f) => teamAction(() => call(api.createTeam(f.name.value)), "Team created"),
  "team-rename": (f) => teamAction(() => call(api.renameTeam(f.name.value)), "Team renamed"),
  "team-invite": (f) => teamAction(async () => {
    await call(api.invite(f.email.value));
    f.reset();
  }, "Invite sent"),
};

async function sendMessage() {
  const input = $("chat-input");
  const body = input.value.trim();
  if (!body) return;
  input.disabled = true;
  try {
    const sent = await call(api.sendMessage(body));
    // A poll may already have added it.
    if (!state.messages.some((m) => m.id === sent.id)) state.messages = [...state.messages, sent];
    input.value = "";
    $("chat-log").dataset.ready = ""; // jump to your new message
    render();
  } catch (err) {
    toast(err.message, true);
  } finally {
    input.disabled = false;
    input.focus();
  }
}

function setView(view) {
  state.view = view;
  for (const item of document.querySelectorAll(".nav-item[data-view]")) {
    item.classList.toggle("active", item.dataset.view === view);
  }
  // On phones the nav scrolls sideways; keep the current page's tab in sight.
  document.querySelector(".nav-item.active")?.scrollIntoView({ block: "nearest", inline: "nearest" });
  render();
}

function moveCalendar(action, date) {
  const cal = state.cal;
  if (action === "prev" || action === "next") {
    cal.week = new Date(cal.week.getFullYear(), cal.week.getMonth(), cal.week.getDate() + (action === "next" ? 7 : -7));
  } else if (action === "today") {
    cal.week = startOfWeek(new Date());
  } else if (action === "day") {
    cal.week = startOfWeek(new Date(`${date}T00:00`));
  } else {
    cal.month = new Date(cal.month.getFullYear(), cal.month.getMonth() + (action === "mini-next" ? 1 : -1), 1);
    render();
    return;
  }
  cal.month = new Date(cal.week.getFullYear(), cal.week.getMonth(), 1);
  render();
}

function openSearch() {
  setView("board");
  $("search").focus();
}

function replaceTask(updated) {
  state.tasks = state.tasks.map((t) => (t.id === updated.id ? updated : t));
  render();
}

/* Task dialog */

const dialog = $("task-dialog");
const form = $("task-form");

// datetime-local wants local "YYYY-MM-DDTHH:mm"; the API speaks UTC.
function toLocalInput(iso) {
  if (!iso) return "";
  const d = parseDate(iso);
  return new Date(d.getTime() - d.getTimezoneOffset() * 60000).toISOString().slice(0, 16);
}

function openDialog(task = null) {
  state.editing = task;
  $("dialog-title").textContent = task ? "Edit task" : "New task";
  $("task-title").value = task?.title ?? "";
  $("task-description").value = task?.description ?? "";
  $("task-due").value = toLocalInput(task?.due_at);
  $("task-delete").hidden = !task;
  $("dialog-error").hidden = true;
  dialog.showModal();
  $("task-title").focus();
}

function dialogError(err) {
  $("dialog-error").textContent = err.message;
  $("dialog-error").hidden = false;
}

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const title = $("task-title").value.trim();
  const description = $("task-description").value.trim();
  const dueValue = $("task-due").value;
  const due_at = dueValue ? new Date(dueValue).toISOString() : null;
  if (!title) {
    dialogError(new Error("Give the task a title."));
    return;
  }

  $("task-save").disabled = true;
  try {
    if (state.editing) {
      // Sending null would leave the old description in place, so clear it with "".
      // due_at: null does clear the due date.
      replaceTask(await call(api.updateTask(state.editing.id, { title, description, due_at })));
      toast("Task updated");
    } else {
      const created = await call(api.createTask({ title, description: description || null, due_at }));
      state.tasks = [...state.tasks, created];
      render();
      toast("Task created");
    }
    dialog.close();
  } catch (err) {
    dialogError(err);
  } finally {
    $("task-save").disabled = false;
  }
});

$("task-cancel").addEventListener("click", () => dialog.close());

$("task-delete").addEventListener("click", async () => {
  const task = state.editing;
  if (!task || !confirm(`Delete "${task.title}"? This can't be undone.`)) return;
  try {
    await call(api.deleteTask(task.id));
    state.tasks = state.tasks.filter((t) => t.id !== task.id);
    render();
    dialog.close();
    toast("Task deleted");
  } catch (err) {
    dialogError(err);
  }
});

/* Clicks across the page */

document.addEventListener("click", async (e) => {
  const target = e.target.closest("[data-action], [data-view], [data-cal]");
  if (!target) return;

  if (target.dataset.view) {
    setView(target.dataset.view);
    return;
  }
  if (target.dataset.cal) {
    moveCalendar(target.dataset.cal, target.dataset.date);
    return;
  }

  const { action, id, status } = target.dataset;
  if (action === "new") openDialog();
  if (action === "search") openSearch();
  if (action === "edit") openDialog(state.tasks.find((t) => t.id === Number(id)));
  if (action === "move") {
    target.disabled = true;
    try {
      replaceTask(await call(api.setStatus(Number(id), status)));
    } catch (err) {
      toast(err.message, true);
      target.disabled = false;
    }
  }
  if (action === "photo") $("photo-input").click();
  if (action === "photo-remove") {
    try {
      applyUser(await call(api.removeAvatar()));
      toast("Photo removed");
    } catch (err) {
      toast(err.message, true);
    }
  }
  if (action === "invite-accept") teamAction(() => call(api.acceptInvite(Number(id))), "Welcome to the team!");
  if (action === "invite-decline") teamAction(() => call(api.declineInvite(Number(id))), "Invite declined");
  if (action === "invite-cancel") teamAction(() => call(api.cancelInvite(Number(id))), "Invite cancelled");
  if (action === "member-remove" && confirm(`Remove ${target.dataset.name} from the team?`)) {
    teamAction(() => call(api.removeMember(Number(id))), "Member removed");
  }
  if (action === "team-leave" && confirm("Leave this team? You'll lose access to its chat.")) {
    teamAction(() => call(api.leaveTeam()), "You left the team");
  }
  if (action === "team-delete" && confirm("Delete this team for everyone, including its chat history?")) {
    teamAction(() => call(api.deleteTeam()), "Team deleted");
  }
  if (action === "timer-toggle") toggleTimer();
  if (action === "export") exportCsv(state.tasks);
  if (action === "signout") signOut();
  if (action === "clear-local" && confirm("Clear all time entries, goal targets and preferences saved in this browser?")) {
    clearLocal();
    state.local = loadLocal();
    $("set-start").value = state.local.prefs.startView;
    render();
    toast("Cleared");
  }
  if (action === "complete") {
    target.disabled = true;
    try {
      replaceTask(await call(api.setStatus(Number(id), "completed")));
      toast("Task completed");
    } catch (err) {
      toast(err.message, true);
      target.checked = false;
      target.disabled = false;
    }
  }
});

$("search").addEventListener("input", (e) => {
  state.query = e.target.value;
  render();
});

$("photo-input").addEventListener("change", async (e) => {
  const [file] = e.target.files;
  e.target.value = ""; // so picking the same file again still fires "change"
  if (!file) return;
  try {
    applyUser(await call(api.setAvatar(await toAvatarDataUrl(file))));
    toast("Photo updated");
  } catch (err) {
    toast(err.message, true);
  }
});

$("cal-search").addEventListener("input", (e) => {
  state.cal.query = e.target.value;
  render();
});

document.addEventListener("submit", (e) => {
  const teamForm = TEAM_FORMS[e.target.dataset.form];
  if (teamForm) {
    e.preventDefault();
    teamForm(e.target);
    return;
  }
  if (e.target.id === "chat-form") {
    e.preventDefault();
    sendMessage();
    return;
  }
  const goal = e.target.dataset.goal;
  if (!goal) return;
  e.preventDefault();
  const value = Number(e.target.querySelector("input").value);
  state.local.goals[goal] = value;
  saveLocal(state.local);
  e.target.querySelector("input").blur();
  render();
  toast("Goal saved");
});

$("signout").addEventListener("click", signOut);

// Enter sends; Shift+Enter adds a new line.
$("chat-input").addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey && !e.isComposing) {
    e.preventDefault();
    sendMessage();
  }
});

// Catch up on what arrived while the tab was in the background.
document.addEventListener("visibilitychange", () => {
  if (document.visibilityState === "visible" && state.view === "messages") render();
});

// N = new task, / = search. Ignored while typing or when a dialog is open.
document.addEventListener("keydown", (e) => {
  if (e.ctrlKey || e.metaKey || e.altKey || dialog.open) return;
  // A closed dialog can leave focus on its hidden input, which isn't typing.
  if (e.target.closest("input, textarea") && e.target.offsetParent) return;
  if (e.key === "n" || e.key === "N") {
    e.preventDefault();
    openDialog();
  } else if (e.key === "/") {
    e.preventDefault();
    openSearch();
  }
});

/* Start */

// Shows the account's name, email and photo everywhere on the page.
function applyUser(user) {
  state.user = user;
  const full = fullName(user);
  $("greeting").textContent = full;
  $("profile-name").textContent = $("profile-name").title = full;
  $("profile-email").textContent = $("profile-email").title = user.email;
  fillAccount(user);
  paintAvatars(user);
}

async function start() {
  if (!getToken()) {
    signOut();
    return;
  }
  $("today").textContent = new Date().toLocaleDateString(undefined, {
    weekday: "long",
    month: "long",
    day: "numeric",
  });
  try {
    const [user, tasks] = await Promise.all([call(api.me()), call(api.listTasks())]);
    applyUser(user);
    useAccount(user.email);
    state.local = loadLocal();
    initSettings({
      call,
      onUser: applyUser,
      onDeleted: () => {
        clearLocal();
        clearToken();
        location.replace("index.html");
      },
      prefs: () => state.local.prefs,
      savePrefs: (prefs) => {
        Object.assign(state.local.prefs, prefs);
        saveLocal(state.local);
        toast("Preference saved");
      },
    });
    state.tasks = tasks;
    await loadTeam();
    state.loaded = true;
    setView(state.local.prefs.startView in RENDERERS ? state.local.prefs.startView : "overview");
  } catch (err) {
    $("load-error").textContent = err.message;
    $("load-error").hidden = false;
  } finally {
    document.body.classList.remove("is-loading");
  }
}

start();
