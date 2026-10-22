// Per-account data the API can't store yet (time entries, goal targets, preferences).
// It lives in this browser only, so every read and write tolerates storage failing.

const DEFAULTS = { entries: [], running: null, goals: { weekly: 5, focus: 120 }, prefs: { startView: "overview" } };
let key = null;

export function useAccount(email) {
  key = `nexora_local_${email}`;
}

export function loadLocal() {
  try {
    const stored = JSON.parse(localStorage.getItem(key)) ?? {};
    return {
      ...structuredClone(DEFAULTS),
      ...stored,
      goals: { ...DEFAULTS.goals, ...stored.goals },
      prefs: { ...DEFAULTS.prefs, ...stored.prefs },
    };
  } catch {
    return structuredClone(DEFAULTS);
  }
}

export function saveLocal(data) {
  try {
    localStorage.setItem(key, JSON.stringify(data));
  } catch {
    // Private mode or full storage: the page keeps working for this session.
  }
}

export function clearLocal() {
  try {
    localStorage.removeItem(key);
  } catch {
    // Nothing stored, nothing to clear.
  }
}
