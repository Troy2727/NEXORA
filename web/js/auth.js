import { api, setToken } from "./api.js";

const message = document.getElementById("message");
const panels = ["login", "register", "verify"].map((id) => document.getElementById(id));

// Kept in memory only, so we can sign the user in right after they verify.
let pendingLogin = null;

function show(panelId) {
  for (const panel of panels) panel.hidden = panel.id !== panelId;
  for (const tab of document.querySelectorAll(".tab")) {
    tab.classList.toggle("active", tab.dataset.panel === panelId);
  }
  hideMessage();
}

function say(text, ok = false) {
  message.textContent = text;
  message.classList.toggle("ok", ok);
  message.hidden = false;
}

function hideMessage() {
  message.hidden = true;
}

async function busy(button, work) {
  button.disabled = true;
  try {
    await work();
  } catch (err) {
    say(err.message);
  } finally {
    button.disabled = false;
  }
}

const formData = (form) => Object.fromEntries(new FormData(form));

async function signIn(email, password) {
  const { access_token } = await api.login(email, password);
  setToken(access_token);
  location.href = "app.html";
}

document.querySelectorAll("[data-panel]").forEach((el) => {
  el.addEventListener("click", () => show(el.dataset.panel));
});

panels[0].addEventListener("submit", (e) => {
  e.preventDefault();
  const { email, password } = formData(e.target);
  busy(e.submitter, () => signIn(email, password));
});

panels[1].addEventListener("submit", (e) => {
  e.preventDefault();
  const user = formData(e.target);
  for (const key of ["first_name", "last_name"]) if (!user[key].trim()) delete user[key];

  busy(e.submitter, async () => {
    await api.register(user);
    pendingLogin = { email: user.email, password: user.password };
    document.getElementById("verify-email").value = user.email;
    show("verify");
    await api.sendCode(user.email);
    say(`Account created. We sent a code to ${user.email}.`, true);
  });
});

panels[2].addEventListener("submit", (e) => {
  e.preventDefault();
  const { email, code } = formData(e.target);
  busy(e.submitter, async () => {
    await api.verify(email, code.trim());
    if (pendingLogin?.email === email) {
      await signIn(pendingLogin.email, pendingLogin.password);
      return;
    }
    show("login");
    document.getElementById("login-email").value = email;
    say("Email verified. You can sign in now.", true);
  });
});

document.getElementById("send-code").addEventListener("click", (e) => {
  const email = document.getElementById("verify-email").value.trim();
  if (!email) {
    say("Enter your email first.");
    return;
  }
  busy(e.currentTarget, async () => {
    await api.sendCode(email);
    say(`Code sent to ${email}.`, true);
  });
});

const showFromHash = () => show(location.hash === "#register" ? "register" : "login");
window.addEventListener("hashchange", showFromHash);
showFromHash();
