import { dueLabel } from "./calendar.js";
import { STATUS, TRANSITIONS, esc, parseDate, timeAgo } from "./shared.js";

const MOVE_LABEL = {
  in_progress: "Start",
  completed: "Complete",
  created: "Move to to-do",
};

const ADD_BUTTON = `<button class="icon-btn icon-btn-sm" data-action="new" title="Add task" aria-label="Add task">
  <svg class="icon"><use href="assets/icons.svg#plus"/></svg></button>`;

function matches(task, query) {
  if (!query) return true;
  return `${task.title} ${task.description ?? ""}`.toLowerCase().includes(query);
}

function card(task) {
  const moves = TRANSITIONS[task.status]
    .map((to) => {
      const label = task.status === "completed" ? "Reopen" : MOVE_LABEL[to];
      return `<button class="btn btn-sm" data-action="move" data-id="${task.id}" data-status="${to}">${label}</button>`;
    })
    .join("");

  return `<article class="task${task.status === "completed" ? " done" : ""}" data-action="edit" data-id="${task.id}">
    <h3>${esc(task.title)}</h3>
    ${task.description ? `<p>${esc(task.description)}</p>` : ""}
    ${task.due_at ? `<span class="due${task.status !== "completed" && parseDate(task.due_at) < new Date() ? " overdue" : ""}">Due ${dueLabel(task)}</span>` : ""}
    <div class="task-foot"><span class="meta" title="Updated ${timeAgo(task.updated_at)}">Created ${parseDate(task.created_at).toLocaleDateString(undefined, { month: "short", day: "numeric" })}</span>${moves}</div>
  </article>`;
}

export function renderBoard(root, tasks, query) {
  const q = query.trim().toLowerCase();
  root.innerHTML = Object.entries(STATUS)
    .map(([status, meta]) => {
      const column = tasks
        .filter((t) => t.status === status && matches(t, q))
        .sort((a, b) => parseDate(b.updated_at) - parseDate(a.updated_at));
      return `<section class="column">
        <header class="column-head"><span class="dot tone-${meta.tone}"></span>${meta.label}<span class="column-count">${column.length}</span>${status === "created" ? ADD_BUTTON : ""}</header>
        <div class="column-body">${column.map(card).join("") || `<p class="empty">${q ? "No matches" : "No tasks"}</p>`}</div>
      </section>`;
    })
    .join("");
}
