// Local development talks to the local API; the deployed site talks to the hosted one (Vercel project nexora-api).
// Override either with: localStorage.setItem("nexora_api", "https://...")
const LOCAL = ["localhost", "127.0.0.1"].includes(location.hostname);
export const API_BASE =
  localStorage.getItem("nexora_api") || (LOCAL ? "http://localhost:8000" : "https://nexora-api-smoky.vercel.app");

const TOKEN_KEY = "nexora_token";

export const getToken = () => localStorage.getItem(TOKEN_KEY);
export const setToken = (token) => localStorage.setItem(TOKEN_KEY, token);
export const clearToken = () => localStorage.removeItem(TOKEN_KEY);

export class ApiError extends Error {
  constructor(message, status) {
    super(message);
    this.status = status;
  }
}

function errorMessage(data, status) {
  const detail = data?.detail;
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail) && detail.length) {
    return detail.map((e) => `${e.loc?.at(-1)}: ${e.msg}`).join("; ");
  }
  return `Request failed (${status})`;
}

async function request(method, path, body) {
  const headers = {};
  if (body !== undefined) headers["Content-Type"] = "application/json";
  const token = getToken();
  if (token) headers.Authorization = `Bearer ${token}`;

  let res;
  try {
    res = await fetch(API_BASE + path, {
      method,
      headers,
      body: body === undefined ? undefined : JSON.stringify(body),
    });
  } catch {
    throw new ApiError(`Can't reach the API at ${API_BASE}. Is it running?`, 0);
  }

  const data = await res.json().catch(() => null);
  if (!res.ok) throw new ApiError(errorMessage(data, res.status), res.status);
  return data;
}

const enc = encodeURIComponent;

export const api = {
  login: (email, password) => request("POST", "/auth/login", { email, password }),
  register: (user) => request("POST", "/auth/register", user),
  sendCode: (email) => request("POST", `/auth/send/${enc(email)}/code`),
  verify: (email, code) => request("POST", `/auth/verify/${enc(email)}/${enc(code)}`),
  me: () => request("GET", "/user/me"),
  updateMe: (fields) => request("PATCH", "/user/me", fields),
  changePassword: (current_password, new_password) => request("PUT", "/user/me/password", { current_password, new_password }),
  deleteMe: (password) => request("DELETE", "/user/me", { password }),
  setAvatar: (image) => request("PUT", "/user/me/avatar", { image }),
  removeAvatar: () => request("DELETE", "/user/me/avatar"),
  getTeam: () => request("GET", "/team"),
  createTeam: (name) => request("POST", "/team", { name }),
  renameTeam: (name) => request("PATCH", "/team", { name }),
  deleteTeam: () => request("DELETE", "/team"),
  invite: (email) => request("POST", "/team/invites", { email }),
  cancelInvite: (id) => request("DELETE", `/team/invites/${id}`),
  myInvites: () => request("GET", "/team/invites/mine"),
  acceptInvite: (id) => request("POST", `/team/invites/${id}/accept`),
  declineInvite: (id) => request("POST", `/team/invites/${id}/decline`),
  removeMember: (userId) => request("DELETE", `/team/members/${userId}`),
  leaveTeam: () => request("POST", "/team/leave"),
  messages: (afterId) => request("GET", `/team/messages${afterId ? `?after_id=${afterId}` : ""}`),
  sendMessage: (body) => request("POST", "/team/messages", { body }),
  listTasks: () => request("GET", "/task/list"),
  createTask: (task) => request("POST", "/task", task),
  updateTask: (id, fields) => request("PATCH", `/task/${id}`, fields),
  setStatus: (id, status) => request("PATCH", `/task/transitions/${id}/${status}`),
  deleteTask: (id) => request("DELETE", `/task/${id}`),
};
