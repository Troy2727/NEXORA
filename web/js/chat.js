import { avatarGroup, avatarMarkup } from "./photo.js";
import { esc, parseDate } from "./shared.js";

const $ = (id) => document.getElementById(id);
const GROUP_MS = 5 * 60 * 1000; // same sender within 5 minutes shares one header
const FORMER = { first_name: "Former", last_name: "member", email: "former@member", avatar: null };

const personName = (p) => [p.first_name, p.last_name].filter(Boolean).join(" ") || p.email.split("@")[0];
const clock = (d) => d.toLocaleTimeString(undefined, { hour: "2-digit", minute: "2-digit" });

function dayLabel(d) {
  const today = new Date();
  const yesterday = new Date();
  yesterday.setDate(today.getDate() - 1);
  if (d.toDateString() === today.toDateString()) return "Today";
  if (d.toDateString() === yesterday.toDateString()) return "Yesterday";
  return d.toLocaleDateString(undefined, { weekday: "long", month: "short", day: "numeric" });
}

// Unread = newer than what you've seen, and not sent by you.
export const unreadCount = (messages, lastRead, meId) =>
  messages.filter((m) => m.id > lastRead && m.user_id !== meId).length;

export function renderChat({ team, messages, me }) {
  $("chat-empty").hidden = Boolean(team);
  $("chat").hidden = !team;
  if (!team) return;

  const people = new Map(team.members.map((m) => [m.user_id, m]));
  $("chat-title").textContent = `${team.name} chat`;
  $("chat-sub").textContent = `${team.members.length} member${team.members.length === 1 ? "" : "s"} · visible to everyone in the team`;
  $("chat-faces").innerHTML = avatarGroup(team.members);

  const log = $("chat-log");
  const nearBottom = log.scrollHeight - log.scrollTop - log.clientHeight < 80;

  let html = "";
  let prev = null;
  for (const m of messages) {
    const at = parseDate(m.created_at);
    if (!prev || parseDate(prev.created_at).toDateString() !== at.toDateString()) {
      html += `<div class="chat-day"><span>${dayLabel(at)}</span></div>`;
      prev = null;
    }
    const grouped = prev && prev.user_id === m.user_id && at - parseDate(prev.created_at) < GROUP_MS;
    const sender = people.get(m.user_id) ?? FORMER;
    const mine = m.user_id === me.id;
    html += `<div class="msg${mine ? " mine" : ""}${grouped ? " grouped" : ""}" data-id="${m.id}">
      ${grouped ? `<span class="msg-gap"></span>` : avatarMarkup(sender)}
      <div class="msg-main">
        ${grouped ? "" : `<p class="msg-meta"><b>${esc(mine ? "You" : personName(sender))}</b><span>${clock(at)}</span></p>`}
        <p class="msg-body" title="${clock(at)}">${esc(m.body)}</p>
      </div>
    </div>`;
    prev = m;
  }
  log.innerHTML = html || `<p class="empty chat-empty-log">No messages yet. Say hello to your team!</p>`;
  if (nearBottom || !log.dataset.ready) {
    log.scrollTop = log.scrollHeight;
    log.dataset.ready = "1";
  }
}
