import { avatarGroup, avatarMarkup } from "./photo.js";
import { esc, parseDate, timeAgo } from "./shared.js";

const $ = (id) => document.getElementById(id);
const name = (p) => [p.first_name, p.last_name].filter(Boolean).join(" ") || p.email.split("@")[0];
const day = (iso) => parseDate(iso).toLocaleDateString(undefined, { month: "short", day: "numeric", year: "numeric" });

function invitesForMe(invites, inTeam) {
  if (!invites.length) return "";
  return `<div class="card">
    <h3 class="card-title">Invitations for you</h3>
    <ul class="list">${invites.map((i) => `<li>
      <span class="ring solid tone-orange"><svg class="icon"><use href="assets/icons.svg#users"/></svg></span>
      <div class="grow"><p class="title" title="${esc(i.team_name)}">${esc(i.team_name)}</p>
        <p class="meta">Invited by ${esc(i.invited_by)} · ${timeAgo(i.created_at)}</p></div>
      ${inTeam
        ? `<span class="muted small">Leave your team to join</span>`
        : `<button class="btn btn-primary btn-sm" data-action="invite-accept" data-id="${i.id}">Accept</button>`}
      <button class="btn btn-ghost btn-sm" data-action="invite-decline" data-id="${i.id}">Decline</button>
    </li>`).join("")}</ul>
  </div>`;
}

function createCard() {
  return `<div class="card team-create">
    <span class="welcome-icon"><svg class="icon"><use href="assets/icons.svg#users"/></svg></span>
    <h3>Create your team</h3>
    <p class="muted">Invite teammates by email and chat together in Messages. Your tasks stay private.</p>
    <form class="team-inline" data-form="team-create">
      <label class="sr-only" for="team-create-name">Team name</label>
      <input class="input" id="team-create-name" name="name" maxlength="60" placeholder="Team name, e.g. Product" required>
      <button class="btn btn-primary" type="submit">Create team</button>
    </form>
  </div>`;
}

function memberRow(m, team, me) {
  const isMe = m.user_id === me.id;
  const canRemove = team.owner_id === me.id && !isMe;
  return `<li>
    ${avatarMarkup(m)}
    <div class="grow">
      <p class="title" title="${esc(name(m))}">${esc(name(m))}${isMe ? ` <span class="muted">(you)</span>` : ""}</p>
      <p class="meta" title="${esc(m.email)}">${esc(m.email)} · Joined ${day(m.joined_at)}</p>
    </div>
    <span class="pill ${m.role === "owner" ? "tone-orange" : "tone-gray"}">${m.role === "owner" ? "Owner" : "Member"}</span>
    ${canRemove ? `<button class="btn btn-ghost btn-sm" data-action="member-remove" data-id="${m.user_id}" data-name="${esc(name(m))}">Remove</button>` : ""}
  </li>`;
}

export function renderTeam({ team, invites, me }) {
  if (!team) {
    $("team-root").innerHTML = invitesForMe(invites, false) + createCard();
    return;
  }

  const isOwner = team.owner_id === me.id;
  const header = `<div class="card team-head">
    <div class="team-title">
      ${isOwner
        ? `<form class="team-inline" data-form="team-rename">
            <label class="sr-only" for="team-rename-name">Team name</label>
            <input class="input team-name-input" id="team-rename-name" name="name" maxlength="60" value="${esc(team.name)}" required>
            <button class="btn btn-sm" type="submit">Rename</button>
          </form>`
        : `<h3>${esc(team.name)}</h3>`}
      <p class="muted small">${team.members.length} member${team.members.length === 1 ? "" : "s"} · Created ${day(team.created_at)}</p>
      ${avatarGroup(team.members)}
    </div>
    <button class="btn" data-view="messages"><svg class="icon"><use href="assets/icons.svg#message"/></svg> Open team chat</button>
  </div>`;

  const members = `<div class="card">
    <h3 class="card-title">Members</h3>
    <ul class="list">${team.members.map((m) => memberRow(m, team, me)).join("")}</ul>
  </div>`;

  const inviteCard = isOwner
    ? `<div class="card">
        <h3 class="card-title">Invite people</h3>
        <form class="team-inline" data-form="team-invite">
          <label class="sr-only" for="team-invite-email">Email address</label>
          <input class="input" id="team-invite-email" name="email" type="email" maxlength="254" placeholder="name@company.com" required>
          <button class="btn btn-primary" type="submit">Send invite</button>
        </form>
        <p class="muted small team-note">They'll see the invite under Team when they sign in, or after they create an account with that email.</p>
        <h4 class="team-sub">Pending invites</h4>
        <ul class="list">${team.invites.length
          ? team.invites.map((i) => `<li>
              <span class="ring tone-gray"><svg class="icon"><use href="assets/icons.svg#clock"/></svg></span>
              <div class="grow"><p class="title" title="${esc(i.email)}">${esc(i.email)}</p><p class="meta">Sent ${timeAgo(i.created_at)}</p></div>
              <button class="btn btn-ghost btn-sm" data-action="invite-cancel" data-id="${i.id}">Cancel</button>
            </li>`).join("")
          : `<li class="empty">No pending invites.</li>`}</ul>
      </div>`
    : "";

  const danger = `<div class="card danger-card team-danger">
    <div><h3 class="card-title">${isOwner ? "Delete team" : "Leave team"}</h3>
      <p class="muted small">${isOwner
        ? "Removes everyone from the team and deletes its chat history. Your tasks are not affected."
        : "You'll lose access to the team chat. Your tasks are not affected."}</p></div>
    <button class="btn btn-danger btn-sm" data-action="${isOwner ? "team-delete" : "team-leave"}">${isOwner ? "Delete team" : "Leave team"}</button>
  </div>`;

  $("team-root").innerHTML = header + invitesForMe(invites, true) + `<div class="page-grid">${members}${inviteCard}</div>` + danger;
}
