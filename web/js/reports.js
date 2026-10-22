import { dueLabel, startOfWeek } from "./calendar.js";
import { STATUS, esc, parseDate } from "./shared.js";

const $ = (id) => document.getElementById(id);
const COLOR = { created: "#8e8e93", in_progress: "#ff8a1f", completed: "#34c759" };
// Validated as a pair against the card surface (dataviz validate_palette, dark mode).
const SERIES = [
  { key: "created", label: "Created", color: "#6070e0" },
  { key: "completed", label: "Completed", color: "#e86a1c" },
];
const WEEKS = 8;
const DAY_MS = 86400000;

const isOverdue = (t, now) => t.due_at && t.status !== "completed" && parseDate(t.due_at) < now;
const icon = (name) => `<svg class="icon"><use href="assets/icons.svg#${name}"/></svg>`;

export function renderReports(tasks) {
  const now = new Date();
  const weekStart = startOfWeek(now);
  const done = tasks.filter((t) => t.status === "completed");
  const overdue = tasks.filter((t) => isOverdue(t, now));
  const weekAhead = new Date(now.getTime() + 7 * DAY_MS);
  const upcoming = tasks
    .filter((t) => t.due_at && t.status !== "completed" && parseDate(t.due_at) >= now && parseDate(t.due_at) < weekAhead)
    .sort((a, b) => parseDate(a.due_at) - parseDate(b.due_at));
  const rate = tasks.length ? Math.round((done.length / tasks.length) * 100) : 0;
  const createdThisWeek = tasks.filter((t) => parseDate(t.created_at) >= weekStart).length;
  const doneThisWeek = done.filter((t) => parseDate(t.updated_at) >= weekStart).length;
  const oldestLate = overdue.length ? Math.max(...overdue.map((t) => Math.floor((now - parseDate(t.due_at)) / DAY_MS))) : 0;

  const kpis = [
    ["Total tasks", tasks.length, "bar-chart", "gray", `+${createdThisWeek} created this week`],
    ["Completed", done.length, "check", "green", `+${doneThisWeek} this week`],
    ["Completion rate", `${rate}%`, "trending-up", "orange", `<span class="kpi-meter"><i style="width:${rate}%"></i></span>`],
    ["Overdue", overdue.length, "clock", overdue.length ? "red" : "gray",
      overdue.length ? `Oldest is ${oldestLate || "<1"} day${oldestLate === 1 ? "" : "s"} late` : "Nothing late"],
    ["Due next 7 days", upcoming.length, "timer", "gray", upcoming.length ? `Next: ${dueLabel(upcoming[0], now)}` : "Nothing scheduled"],
  ];
  $("report-kpis").innerHTML = kpis.map(([label, value, name, tone, sub]) => `
    <div class="kpi report-kpi card">
      <div class="kpi-top"><span class="kpi-icon tone-${tone}">${icon(name)}</span><span class="kpi-label">${label}</span></div>
      <b>${value}</b>
      <div class="kpi-sub">${sub}</div>
    </div>`).join("");

  renderWeekly(tasks);
  renderStatus(tasks);

  $("report-overdue").innerHTML = overdue.length
    ? overdue.sort((a, b) => parseDate(a.due_at) - parseDate(b.due_at)).map((t) => `<li>
        <div class="grow"><button class="link-btn title" data-action="edit" data-id="${t.id}" title="${esc(t.title)}">${esc(t.title)}</button>
        <p class="meta cal-overdue">Due ${dueLabel(t, now)}</p></div>
        <span class="pill tone-${STATUS[t.status].tone}">${STATUS[t.status].label}</span>
      </li>`).join("")
    : `<li class="empty">Nothing overdue. You're on top of it.</li>`;
}

// Column with a 4px rounded top and a square base.
function column(x, y, w, h) {
  const r = Math.min(4, h, w / 2);
  return `M${x},${y + h} V${y + r} Q${x},${y} ${x + r},${y} H${x + w - r} Q${x + w},${y} ${x + w},${y + r} V${y + h} Z`;
}

function renderWeekly(tasks) {
  const thisWeek = startOfWeek(new Date());
  const weeks = Array.from({ length: WEEKS }, (_, i) => {
    const start = new Date(thisWeek);
    start.setDate(start.getDate() - (WEEKS - 1 - i) * 7);
    return { start, created: 0, completed: 0 };
  });
  const tally = (date, key) => {
    const slot = weeks.find((w) => w.start.getTime() === startOfWeek(date).getTime());
    if (slot) slot[key] += 1;
  };
  for (const t of tasks) {
    tally(parseDate(t.created_at), "created");
    // There is no completed_at column; a completed task's last update is when it was finished.
    if (t.status === "completed") tally(parseDate(t.updated_at), "completed");
  }

  const totals = Object.fromEntries(SERIES.map((s) => [s.key, weeks.reduce((n, w) => n + w[s.key], 0)]));
  $("report-legend").innerHTML = SERIES.map((s) =>
    `<li><span class="dot" style="background:${s.color}"></span>${s.label}<b>${totals[s.key]}</b></li>`).join("");

  // Draw at the real on-screen width so labels keep their CSS size at any screen size.
  const W = Math.max(300, $("report-weekly").clientWidth || 1000);
  const H = Math.round(Math.min(300, Math.max(220, W * 0.28)));
  const padL = 28, padT = 20, padB = 28;
  const max = Math.max(1, ...weeks.flatMap((w) => [w.created, w.completed]));
  const step = Math.max(1, Math.ceil(max / 4));
  const top = step * Math.ceil(max / step);
  const ticks = Array.from({ length: top / step + 1 }, (_, i) => i * step);
  const y = (v) => padT + (1 - v / top) * (H - padT - padB);
  const band = (W - padL) / WEEKS;
  const barW = Math.min(22, band * 0.3);
  const short = band < 64;
  const fmt = (d) => d.toLocaleDateString(undefined, short ? { month: "numeric", day: "numeric" } : { month: "short", day: "numeric" });

  $("report-weekly").innerHTML = `
    <svg class="bars" viewBox="0 0 ${W} ${H}" role="img" aria-label="Tasks created and completed per week, last ${WEEKS} weeks">
      ${ticks.map((v) => `<line class="${v ? "grid-line" : "base-line"}" x1="${padL}" x2="${W}" y1="${y(v)}" y2="${y(v)}"/>
        <text class="axis" x="0" y="${y(v) + 4}">${v}</text>`).join("")}
      ${weeks.map((w, i) => {
        const cx = padL + band * (i + 0.5);
        const current = i === WEEKS - 1;
        const bars = SERIES.map((s, j) => {
          const x = cx + (j ? 2 : -2 - barW);
          const h = y(0) - y(w[s.key]);
          return `${h ? `<path d="${column(x, y(w[s.key]), barW, h)}" fill="${s.color}"/>` : ""}
            ${current ? `<text class="bar-val" x="${x + barW / 2}" y="${y(w[s.key]) - 6}" text-anchor="middle">${w[s.key]}</text>` : ""}`;
        }).join("");
        return `<g class="week${current ? " current" : ""}" data-i="${i}">
          <rect class="hit" x="${padL + band * i}" y="${padT - 8}" width="${band}" height="${H - padT - padB + 8}" rx="8"/>
          ${bars}
          <text class="axis" x="${cx}" y="${H - 6}" text-anchor="middle">${current ? (short ? "Now" : "This week") : fmt(w.start)}</text>
        </g>`;
      }).join("")}
    </svg>
    <div class="chart-tip" hidden></div>
    <table class="sr-only">
      <caption>Tasks per week</caption>
      <tr><th>Week of</th>${SERIES.map((s) => `<th>${s.label}</th>`).join("")}</tr>
      ${weeks.map((w) => `<tr><td>${fmt(w.start)}</td>${SERIES.map((s) => `<td>${w[s.key]}</td>`).join("")}</tr>`).join("")}
    </table>`;

  const tip = $("report-weekly").querySelector(".chart-tip");
  for (const g of $("report-weekly").querySelectorAll(".week")) {
    g.addEventListener("mouseenter", () => {
      const w = weeks[g.dataset.i];
      tip.innerHTML = `<b>Week of ${w.start.toLocaleDateString(undefined, { month: "short", day: "numeric" })}</b>
        ${SERIES.map((s) => `<span><i class="dot" style="background:${s.color}"></i>${s.label}<b>${w[s.key]}</b></span>`).join("")}`;
      tip.hidden = false;
      const box = g.querySelector(".hit").getBoundingClientRect();
      const host = $("report-weekly").getBoundingClientRect();
      const left = Math.min(Math.max(box.left - host.left + box.width / 2, tip.offsetWidth / 2), host.width - tip.offsetWidth / 2);
      tip.style.left = `${left}px`;
    });
    g.addEventListener("mouseleave", () => { tip.hidden = true; });
  }
}

function renderStatus(tasks) {
  const total = tasks.length;
  const rows = Object.entries(STATUS).map(([s, meta]) => {
    const count = tasks.filter((t) => t.status === s).length;
    return { s, meta, count, pct: total ? Math.round((count / total) * 100) : 0 };
  });
  $("report-status").innerHTML = `
    <div class="stack-bar">${rows.filter((r) => r.count).map((r) => `<i style="width:${r.pct}%;background:${COLOR[r.s]}"></i>`).join("") || "<i></i>"}</div>
    <ul class="legend">${rows.map((r) => `<li><span class="dot tone-${r.meta.tone}"></span>${r.meta.label}<b>${r.count}</b><span class="pct">${r.pct}%</span></li>`).join("")}</ul>`;
}

// Leading = + - @ would make spreadsheets run the cell as a formula.
function csvCell(value) {
  let text = value == null ? "" : String(value);
  if (/^[=+\-@\t\r]/.test(text)) text = `'${text}`;
  return `"${text.replace(/"/g, '""')}"`;
}

export function exportCsv(tasks) {
  const columns = ["id", "title", "description", "status", "due_at", "created_at", "updated_at"];
  const lines = [columns.join(","), ...tasks.map((t) => columns.map((c) => csvCell(t[c])).join(","))];
  const url = URL.createObjectURL(new Blob([lines.join("\r\n")], { type: "text/csv;charset=utf-8" }));
  const a = Object.assign(document.createElement("a"), { href: url, download: `nexora-tasks-${new Date().toISOString().slice(0, 10)}.csv` });
  a.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000); // revoking at once can cancel the download
}
