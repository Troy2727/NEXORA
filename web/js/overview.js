import { STATUS, esc, parseDate, timeAgo } from "./shared.js";

const icon = (name) => `<svg class="icon"><use href="assets/icons.svg#${name}"/></svg>`;
const ICON = { created: icon("clock"), in_progress: icon("play"), completed: icon("check") };
const COLOR = { created: "#8e8e93", in_progress: "#ff8a1f", completed: "#34c759", overdue: "#ff453a" };
const DONUT_ORDER = ["completed", "in_progress", "overdue", "created"];
const SLICE = { ...STATUS, overdue: { label: "Overdue", tone: "red" } };
const isOverdue = (t, now) => t.due_at && t.status !== "completed" && parseDate(t.due_at) < now;

const $ = (id) => document.getElementById(id);

function note(id, text, tone) {
  $(id).textContent = text;
  $(id).className = `stat-note ${tone}`;
}

export function renderOverview(tasks) {
  const counts = { created: 0, in_progress: 0, completed: 0 };
  for (const t of tasks) counts[t.status] += 1;
  const total = tasks.length;
  const left = counts.created + counts.in_progress;
  const rate = total ? Math.round((counts.completed / total) * 100) : 0;

  $("stat-left").textContent = left;
  $("stat-progress").textContent = counts.in_progress;
  $("stat-rate").textContent = `${rate}%`;
  note("note-left", left ? "Keep going!" : "All clear", "muted");
  note("note-progress", counts.in_progress ? "Active now" : "Nothing started", counts.in_progress ? "up" : "muted");
  if (rate >= 75) note("note-rate", "Excellent!", "up");
  else if (rate >= 40) note("note-rate", "On track", "warn");
  else note("note-rate", "Just getting started", "muted");

  $("goal-pct").textContent = `${rate}%`;
  $("goal-sub").textContent = `${counts.completed} of ${total} tasks completed`;
  $("goal-bar").style.width = `${rate}%`;

  renderFocusNote(tasks);
  // Overdue gets its own slice, so those tasks leave their To do / In progress slice.
  const now = new Date();
  const slices = { ...counts, overdue: 0 };
  for (const t of tasks.filter((t) => isOverdue(t, now))) {
    slices.overdue += 1;
    slices[t.status] -= 1;
  }
  renderDonut(slices, total);
  renderTrend(tasks);
  renderList($("recent"), byNewest(tasks).slice(0, 5), "No activity yet. Create your first task.");
  renderList($("upnext"), byOldest(tasks.filter((t) => t.status === "created")).slice(0, 5), "Nothing waiting. Nice work.");
}

const byNewest = (tasks) => [...tasks].sort((a, b) => parseDate(b.updated_at) - parseDate(a.updated_at));
const byOldest = (tasks) => [...tasks].sort((a, b) => parseDate(a.created_at) - parseDate(b.created_at));

function renderFocusNote(tasks) {
  const [oldest] = byOldest(tasks.filter((t) => t.status !== "completed"));
  $("focus-note").innerHTML = oldest
    ? `<span class="muted">Oldest open task</span>
       <b class="focus-title" title="${esc(oldest.title)}">${esc(oldest.title)}</b>
       <span class="muted">· created ${timeAgo(oldest.created_at)}</span>
       <button class="btn btn-sm" data-action="edit" data-id="${oldest.id}">Open</button>`
    : `<span class="muted">Nothing open. You're all caught up.</span>`;
}

function renderDonut(counts, total) {
  // r = 15.9155 gives a circumference of 100, so dash lengths are percentages.
  let offset = 0;
  const arcs = DONUT_ORDER.filter((s) => counts[s]).map((s) => {
    const pct = (counts[s] / total) * 100;
    const arc = `<circle r="15.9155" cx="21" cy="21" fill="none" stroke="${COLOR[s]}" stroke-width="6.5"
      stroke-dasharray="${pct} ${100 - pct}" stroke-dashoffset="${-offset}"/>`;
    offset += pct;
    return arc;
  });

  $("donut").innerHTML = `
    <svg viewBox="0 0 42 42" role="img" aria-label="Tasks by status">
      <circle r="15.9155" cx="21" cy="21" fill="none" stroke="#26262c" stroke-width="6.5"/>
      ${arcs.join("")}
    </svg>
    <div class="donut-center"><b>${total}</b><span>Total</span></div>`;

  $("legend").innerHTML = DONUT_ORDER.map((s) => {
    const pct = total ? Math.round((counts[s] / total) * 100) : 0;
    return `<li><span class="dot tone-${SLICE[s].tone}"></span>${SLICE[s].label}<b>${counts[s]}</b><span class="pct">${pct}%</span></li>`;
  }).join("");
}

// Tasks whose last update fell on each of the last `n` days, oldest first.
function dailyCounts(tasks, n) {
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const days = Array.from({ length: n }, (_, i) => {
    const day = new Date(today);
    day.setDate(today.getDate() - (n - 1 - i));
    return { day, count: 0 };
  });
  for (const t of tasks) {
    const d = parseDate(t.updated_at);
    d.setHours(0, 0, 0, 0);
    const slot = days.find((x) => x.day.getTime() === d.getTime());
    if (slot) slot.count += 1;
  }
  return days;
}

function renderTrend(tasks) {
  const fortnight = dailyCounts(tasks, 14);
  const days = fortnight.slice(7);
  const sum = (list) => list.reduce((n, d) => n + d.count, 0);
  const thisWeek = sum(days);
  const diff = thisWeek - sum(fortnight.slice(0, 7));

  $("trend-total").textContent = thisWeek;
  $("trend-delta").className = `delta ${diff > 0 ? "up" : diff < 0 ? "down" : "flat"}`;
  const arrow = diff > 0 ? icon("arrow-up") : diff < 0 ? icon("arrow-down") : "";
  $("trend-delta").innerHTML = `${arrow}${diff > 0 ? "+" : ""}${diff} vs last week`;

  // Draw at the real on-screen width so axis text stays its CSS size on phones.
  const W = Math.max(300, $("trend-chart").clientWidth || 600), H = 200, padL = 28, padB = 26, padT = 34;
  const step = Math.max(1, Math.ceil(Math.max(...days.map((d) => d.count)) / 4));
  const top = step * Math.max(1, Math.ceil(Math.max(...days.map((d) => d.count)) / step));
  const ticks = Array.from({ length: top / step + 1 }, (_, i) => i * step);
  const x = (i) => padL + (i * (W - padL - 10)) / 6;
  const y = (v) => padT + (1 - v / top) * (H - padT - padB);
  const pts = days.map((d, i) => [x(i), y(d.count)]);

  // Horizontal-tangent cubic segments: smooth, and never dips below zero.
  let line = `M${pts[0][0]},${pts[0][1]}`;
  for (let i = 1; i < pts.length; i += 1) {
    const [x0, y0] = pts[i - 1];
    const [x1, y1] = pts[i];
    const mx = (x0 + x1) / 2;
    line += ` C${mx},${y0} ${mx},${y1} ${x1},${y1}`;
  }
  const area = `${line} L${x(6)},${y(0)} L${x(0)},${y(0)} Z`;

  const peak = days.reduce((best, d, i) => (d.count > days[best].count ? i : best), 0);
  const peakLabel = days[peak].count
    ? `<g class="peak">
        <rect x="${pts[peak][0] - 18}" y="${pts[peak][1] - 32}" width="36" height="22" rx="7"/>
        <text x="${pts[peak][0]}" y="${pts[peak][1] - 17}" text-anchor="middle">${days[peak].count}</text>
      </g>`
    : "";

  $("trend-chart").innerHTML = `
    <svg viewBox="0 0 ${W} ${H}" role="img" aria-label="Tasks updated per day over the last 7 days">
      <defs>
        <linearGradient id="trend-fill" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stop-color="#ff6a00" stop-opacity="0.55"/>
          <stop offset="1" stop-color="#e5322d" stop-opacity="0.04"/>
        </linearGradient>
      </defs>
      ${ticks.map((v) => `<line class="grid-line" x1="${padL}" x2="${W - 10}" y1="${y(v)}" y2="${y(v)}"/>
        <text class="axis" x="0" y="${y(v) + 4}">${v}</text>`).join("")}
      <path d="${area}" fill="url(#trend-fill)"/>
      <path d="${line}" fill="none" stroke="#ff8a1f" stroke-width="2.5"/>
      ${pts.map(([px, py], i) => `<circle cx="${px}" cy="${py}" r="4" fill="#ffb020" stroke="#131316" stroke-width="2">
        <title>${days[i].count} updated</title></circle>`).join("")}
      ${peakLabel}
      ${days.map((d, i) => `<text class="axis" x="${x(i)}" y="${H - 4}" text-anchor="middle">${d.day.toLocaleDateString(undefined, { weekday: "short" })}</text>`).join("")}
    </svg>`;
}

function renderList(root, tasks, emptyText) {
  if (!tasks.length) {
    root.innerHTML = `<li class="empty">${esc(emptyText)}</li>`;
    return;
  }
  root.innerHTML = tasks.map((t) => {
    const meta = STATUS[t.status];
    return `<li>
      <span class="ring solid tone-${meta.tone}">${ICON[t.status]}</span>
      <div class="grow"><p class="title" title="${esc(t.title)}">${esc(t.title)}</p><p class="meta">${meta.label} · ${timeAgo(t.updated_at)}</p></div>
      <span class="pill tone-${meta.tone}">${meta.label}</span>
    </li>`;
  }).join("");
}
