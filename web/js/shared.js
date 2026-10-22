export const STATUS = {
  created: { label: "To do", tone: "gray" },
  in_progress: { label: "In progress", tone: "orange" },
  completed: { label: "Completed", tone: "green" },
};

// Mirrors TaskStatus.transitions in enums/task.py; the API still enforces them.
export const TRANSITIONS = {
  created: ["in_progress", "completed"],
  in_progress: ["created", "completed"],
  completed: ["created"],
};

const ESCAPES = { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" };

export const esc = (value) => String(value ?? "").replace(/[&<>"']/g, (c) => ESCAPES[c]);

// The API returns naive UTC timestamps; treat them as UTC.
export const parseDate = (s) => new Date(/[zZ]|[+-]\d\d:?\d\d$/.test(s) ? s : `${s}Z`);

export function timeAgo(s) {
  const minutes = Math.max(0, (Date.now() - parseDate(s)) / 60000);
  if (minutes < 1) return "just now";
  if (minutes < 60) return `${Math.floor(minutes)}m ago`;
  const hours = minutes / 60;
  if (hours < 24) return `${Math.floor(hours)}h ago`;
  const days = hours / 24;
  if (days < 7) return `${Math.floor(days)}d ago`;
  return parseDate(s).toLocaleDateString();
}
