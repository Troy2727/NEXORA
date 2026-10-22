import { STATUS, esc, parseDate } from "./shared.js";

const HOUR_PX = 48;
const EVENT_MIN = 50; // events closer than this (minutes) share the row side by side
const DAY_MS = 86400000;

export function startOfWeek(date) {
  const d = new Date(date);
  d.setHours(0, 0, 0, 0);
  d.setDate(d.getDate() - ((d.getDay() + 6) % 7)); // Monday
  return d;
}

const addDays = (date, n) => {
  const d = new Date(date);
  d.setDate(d.getDate() + n);
  return d;
};
const sameDay = (a, b) => a.toDateString() === b.toDateString();
const isoDate = (d) => `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
const time = (d) => d.toLocaleTimeString(undefined, { hour: "2-digit", minute: "2-digit" });
const icon = (name) => `<svg class="icon"><use href="assets/icons.svg#${name}"/></svg>`;

const isOverdue = (t, now) => t.status !== "completed" && parseDate(t.due_at) < now;

function matches(task, query) {
  return !query || `${task.title} ${task.description ?? ""}`.toLowerCase().includes(query);
}

export function dueLabel(task, now = new Date()) {
  const due = parseDate(task.due_at);
  const today = new Date(now);
  today.setHours(0, 0, 0, 0);
  const days = Math.floor((new Date(due).setHours(0, 0, 0, 0) - today) / DAY_MS);
  const day = days === 0 ? "Today" : days === 1 ? "Tomorrow" : due.toLocaleDateString(undefined, { month: "short", day: "numeric" });
  return `${day} · ${time(due)}`;
}

export function renderCalendar(tasks, { week, month, query }) {
  const now = new Date();
  const q = query.trim().toLowerCase();
  const dated = tasks.filter((t) => t.due_at);
  const weekEnd = addDays(week, 7);
  const inWeek = dated.filter((t) => {
    const d = parseDate(t.due_at);
    return d >= week && d < weekEnd && matches(t, q);
  });

  const last = addDays(week, 6);
  document.getElementById("cal-title").textContent =
    `${week.toLocaleDateString(undefined, { month: "long", day: "numeric" })} – ${last.toLocaleDateString(undefined, week.getMonth() === last.getMonth() ? { day: "numeric" } : { month: "long", day: "numeric" })}`;
  document.getElementById("cal-sub").textContent = week.getFullYear();

  renderMiniCal(month, week, dated, now);
  renderNextUp(dated, now);
  renderWeek(inWeek, week, now, q);

  const overdue = dated.filter((t) => isOverdue(t, now)).length;
  const undated = tasks.length - dated.length;
  document.getElementById("cal-footer").innerHTML = `
    <span>${icon("clock")} <b>${inWeek.length}</b> due this week</span>
    <span class="${overdue ? "cal-overdue" : ""}"><b>${overdue}</b> overdue</span>
    <span><b>${undated}</b> without a due date</span>
    ${undated ? `<button class="btn btn-sm" data-view="board">Schedule from board</button>` : ""}`;
}

function renderMiniCal(month, week, dated, now) {
  const first = new Date(month.getFullYear(), month.getMonth(), 1);
  const start = startOfWeek(first);
  const dueDays = new Set(dated.map((t) => parseDate(t.due_at).toDateString()));
  const weekEnd = addDays(week, 7);

  const cells = Array.from({ length: 42 }, (_, i) => {
    const d = addDays(start, i);
    const cls = [
      d.getMonth() !== month.getMonth() && "other",
      sameDay(d, now) && "today",
      d >= week && d < weekEnd && "in-week",
      dueDays.has(d.toDateString()) && "has-due",
    ].filter(Boolean).join(" ");
    return `<button class="mini-day ${cls}" data-cal="day" data-date="${isoDate(d)}">${d.getDate()}</button>`;
  });

  document.getElementById("mini-cal").innerHTML = `
    <div class="mini-head">
      <button class="icon-btn icon-btn-sm" data-cal="mini-prev" aria-label="Previous month">${icon("chevron-left")}</button>
      <b>${month.toLocaleDateString(undefined, { month: "long", year: "numeric" })}</b>
      <button class="icon-btn icon-btn-sm" data-cal="mini-next" aria-label="Next month">${icon("chevron-right")}</button>
    </div>
    <div class="mini-grid mini-labels">${["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"].map((d) => `<span>${d}</span>`).join("")}</div>
    <div class="mini-grid">${cells.join("")}</div>`;
}

function renderNextUp(dated, now) {
  const upcoming = dated
    .filter((t) => t.status !== "completed")
    .sort((a, b) => parseDate(a.due_at) - parseDate(b.due_at))
    .slice(0, 5);

  document.getElementById("next-up").innerHTML = upcoming.length
    ? upcoming.map((t) => `<li>
        <input type="checkbox" data-action="complete" data-id="${t.id}" aria-label="Mark ${esc(t.title)} complete">
        <button class="next-up-text" data-action="edit" data-id="${t.id}">
          <span class="next-up-title" title="${esc(t.title)}">${esc(t.title)}</span>
          <span class="next-up-due ${isOverdue(t, now) ? "cal-overdue" : ""}">${isOverdue(t, now) ? "Overdue · " : ""}${dueLabel(t, now)}</span>
        </button>
      </li>`).join("")
    : `<li class="empty">No upcoming due dates.</li>`;
}

// Puts events that are close in time side by side instead of on top of each other.
function layout(events) {
  const sorted = [...events].sort((a, b) => a.minutes - b.minutes);
  let cluster = [];
  const flush = () => cluster.forEach((e, i) => Object.assign(e, { lane: i, lanes: cluster.length }));
  for (const e of sorted) {
    if (cluster.length && e.minutes - cluster[0].minutes >= EVENT_MIN) {
      flush();
      cluster = [];
    }
    cluster.push(e);
  }
  flush();
  return sorted;
}

function renderWeek(inWeek, week, now, q) {
  const days = Array.from({ length: 7 }, (_, i) => addDays(week, i));
  const head = days.map((d) => `<div class="week-day ${sameDay(d, now) ? "today" : ""}">
      <span>${d.toLocaleDateString(undefined, { weekday: "short" })}</span><b>${d.getDate()}</b></div>`).join("");
  const hours = Array.from({ length: 24 }, (_, h) => `<span style="top:${h * HOUR_PX}px">${String(h).padStart(2, "0")}:00</span>`).join("");

  const columns = days.map((d) => {
    const events = layout(inWeek
      .filter((t) => sameDay(parseDate(t.due_at), d))
      .map((t) => {
        const due = parseDate(t.due_at);
        return { t, due, minutes: due.getHours() * 60 + due.getMinutes() };
      }));
    const nowLine = sameDay(d, now)
      ? `<div class="now-line" style="top:${((now.getHours() * 60 + now.getMinutes()) / 60) * HOUR_PX}px"></div>`
      : "";
    const chips = events.map(({ t, due, minutes, lane, lanes }) => `
      <button class="evt evt-${STATUS[t.status].tone}${isOverdue(t, now) ? " evt-overdue" : ""}${lanes > 1 ? " evt-narrow" : ""}" data-action="edit" data-id="${t.id}"
        style="top:${(minutes / 60) * HOUR_PX}px; left:calc(${(lane / lanes) * 100}% + 3px); width:calc(${100 / lanes}% - 6px)"
        title="${esc(t.title)} · ${time(due)} · ${STATUS[t.status].label}">
        <span class="evt-title">${esc(t.title)}</span><span class="evt-time">${time(due)}</span>
      </button>`).join("");
    return `<div class="week-col ${sameDay(d, now) ? "today" : ""}">${nowLine}${chips}</div>`;
  }).join("");

  const wrap = document.getElementById("week-wrap");
  const weekKey = week.toDateString();
  wrap.innerHTML = `
    <div class="week">
      <div class="week-head"><div></div>${head}</div>
      <div class="week-body" style="height:${24 * HOUR_PX}px">
        <div class="week-hours">${hours}</div>${columns}
      </div>
    </div>
    ${inWeek.length ? "" : `<p class="week-empty">${q ? "No scheduled tasks match your search." : "Nothing due this week. Give a task a due date to see it here."}</p>`}`;

  // Start each newly shown week at 07:00 instead of midnight.
  if (wrap.dataset.week !== weekKey) {
    wrap.scrollTop = 7 * HOUR_PX - 16; // leave room so the 07:00 label isn't under the header
    wrap.dataset.week = weekKey;
  }
}
