import { API_BASE, api } from "./api.js";
import { esc, parseDate } from "./shared.js";

const $ = (id) => document.getElementById(id);
const date = (iso) => (iso ? parseDate(iso).toLocaleString(undefined, { dateStyle: "medium", timeStyle: "short" }) : "Not yet");

// First and last name, falling back to the email's name part when neither is set.
export const fullName = (user) => [user.first_name, user.last_name].filter(Boolean).join(" ") || user.email.split("@")[0];

// Fills everything on the page that shows account details.
export function fillAccount(user) {
  $("settings-profile").innerHTML = [
    ["Member since", date(user.created_at)],
    ["Last sign-in", date(user.last_login)],
  ].map(([k, v]) => `<dt>${k}</dt><dd>${esc(v)}</dd>`).join("");
  $("settings-api").textContent = API_BASE;
  $("set-first").value = user.first_name ?? "";
  $("set-last").value = user.last_name ?? "";
  $("set-email").value = user.email;
}

function say(form, text, ok) {
  const alert = form.querySelector(".alert");
  alert.textContent = text;
  alert.classList.toggle("ok", ok);
  alert.hidden = false;
}

async function submitting(form, work) {
  const button = form.querySelector("button[type=submit]");
  button.disabled = true;
  form.querySelector(".alert").hidden = true;
  try {
    await work();
  } catch (err) {
    say(form, err.message, false);
  } finally {
    button.disabled = false;
  }
}

// `call` wraps API calls (signs out on an expired session); `onUser` receives the updated account.
export function initSettings({ call, onUser, onDeleted, prefs, savePrefs }) {
  $("profile-form").addEventListener("submit", (e) => {
    e.preventDefault();
    const form = e.target;
    submitting(form, async () => {
      const user = await call(api.updateMe({ first_name: $("set-first").value, last_name: $("set-last").value }));
      onUser(user);
      say(form, "Profile saved.", true);
    });
  });

  $("password-form").addEventListener("submit", (e) => {
    e.preventDefault();
    const form = e.target;
    if ($("set-new").value !== $("set-confirm").value) {
      say(form, "The new passwords don't match.", false);
      return;
    }
    submitting(form, async () => {
      await call(api.changePassword($("set-current").value, $("set-new").value));
      form.reset();
      say(form, "Password changed.", true);
    });
  });

  $("set-start").value = prefs().startView;
  $("set-start").addEventListener("change", (e) => savePrefs({ startView: e.target.value }));

  $("delete-form").addEventListener("submit", (e) => {
    e.preventDefault();
    const form = e.target;
    if (!confirm("Delete your account and all your tasks? This can't be undone.")) return;
    submitting(form, async () => {
      await call(api.deleteMe($("set-delete-pass").value));
      onDeleted();
    });
  });
}
