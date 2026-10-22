import { startOfWeek } from "./calendar.js";
import { esc } from "./shared.js";

const $ = (id) => document.getElementById(id);
const icon = (name) => `<svg class="icon"><use href="assets/icons.svg#${name}"/></svg>`;

export function fmtDuration(ms) {
  const minutes = Math.floor(ms / 60000);
  if (ms > 0 && minutes === 0) return "<1m";
  return minutes < 60 ? `${minutes}m` : `${Math.floor(minutes / 60)}h ${minutes % 60}m`;
}

const clock = (ms) => {
  const s = Math.floor(ms / 1000);
  return [Math.floor(s / 3600), Math.floor(s / 60) % 60, s % 60].map((n) => String(n).padStart(2, "0")).join(":");
};

const startOfToday = () => new Date().setHours(0, 0, 0, 0);

// Time tracked since `since` (ms), counting only the part of each session after it.
export function trackedSince(local, since) {
  const sessions = local.running ? [...local.entries, { ...local.running, end: Date.now() }] : local.entries;
  return sessions.reduce((sum, e) => sum + Math.max(0, e.end - Math.max(e.start, since)), 0);
}

export function renderTime(tasks, local) {
  const open = tasks.filter((t) => t.status !== "completed");
  const select = $("timer-task");
  const running = local.running;
  const options = running && !open.some((t) => t.id === running.taskId)
    ? [...open, tasks.find((t) => t.id === running.taskId) ?? { id: running.taskId, title: "Deleted task" }]
    : open;
  const selected = running ? running.taskId : Number(select.value) || options[0]?.id;

  select.innerHTML = options.length
    ? options.map((t) => `<option value="${t.id}"${t.id === selected ? " selected" : ""}>${esc(t.title)}</option>`).join("")
    : `<option value="">No open tasks yet</option>`;
  select.disabled = Boolean(running) || !options.length;

  $("timer-display").textContent = clock(running ? Date.now() - running.start : 0);
  $("timer-display").classList.toggle("live", Boolean(running));
  const toggle = $("timer-toggle");
  toggle.innerHTML = running ? `${icon("pause")} Stop` : `${icon("play")} Start timer`;
  toggle.classList.toggle("btn-primary", !running);
  toggle.disabled = !running && !options.length;

  $("time-today").textContent = fmtDuration(trackedSince(local, startOfToday()));
  $("time-week").textContent = fmtDuration(trackedSince(local, startOfWeek(new Date()).getTime()));

  const titles = new Map(tasks.map((t) => [t.id, t.title]));
  const today = local.entries.filter((e) => e.end >= startOfToday()).reverse();
  const hhmm = (ms) => new Date(ms).toLocaleTimeString(undefined, { hour: "2-digit", minute: "2-digit" });
  $("time-entries").innerHTML = today.length
    ? today.map((e) => `<li>
        <span class="ring solid tone-orange">${icon("timer")}</span>
        <div class="grow"><p class="title" title="${esc(titles.get(e.taskId) ?? "Deleted task")}">${esc(titles.get(e.taskId) ?? "Deleted task")}</p><p class="meta">${hhmm(e.start)} – ${hhmm(e.end)}</p></div>
        <b>${fmtDuration(e.end - e.start)}</b>
      </li>`).join("")
    : `<li class="empty">No sessions yet today. Pick a task and start the timer.</li>`;
}
