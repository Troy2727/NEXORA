import { startOfWeek } from "./calendar.js";
import { parseDate } from "./shared.js";
import { fmtDuration, trackedSince } from "./time.js";

const $ = (id) => document.getElementById(id);

function setInput(id, value) {
  // Don't overwrite what the user is typing.
  if (document.activeElement !== $(id)) $(id).value = value;
}

export function renderGoals(tasks, local) {
  const weekStart = startOfWeek(new Date());
  // The API has no completion timestamp, so a completed task counts in the week it was last updated.
  const done = tasks.filter((t) => t.status === "completed" && parseDate(t.updated_at) >= weekStart).length;
  const { weekly, focus } = local.goals;

  $("goal-week-done").textContent = done;
  $("goal-week-target").textContent = weekly;
  $("goal-week-bar").style.width = `${Math.min(100, (done / weekly) * 100)}%`;
  $("goal-week-note").textContent = done >= weekly ? "Goal reached. Nice work!" : `${weekly - done} more to reach your goal.`;
  setInput("goal-week-input", weekly);

  const focused = trackedSince(local, new Date().setHours(0, 0, 0, 0));
  $("goal-focus-done").textContent = fmtDuration(focused);
  $("goal-focus-target").textContent = fmtDuration(focus * 60000);
  $("goal-focus-bar").style.width = `${Math.min(100, (focused / (focus * 60000)) * 100)}%`;
  setInput("goal-focus-input", focus);
}
