// Base URL of your FastAPI backend. Set VITE_API_BASE_URL in a .env file
// (see .env.example) or it falls back to same-origin /api.
const BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

const ACCESS_KEY = "rag_chat_access_token";
const REFRESH_KEY = "rag_chat_refresh_token";

export function getTokens() {
  return {
    access: localStorage.getItem(ACCESS_KEY),
    refresh: localStorage.getItem(REFRESH_KEY),
  };
}

export function setTokens({ access_token, refresh_token }) {
  if (access_token) localStorage.setItem(ACCESS_KEY, access_token);
  if (refresh_token) localStorage.setItem(REFRESH_KEY, refresh_token);
}

export function clearTokens() {
  localStorage.removeItem(ACCESS_KEY);
  localStorage.removeItem(REFRESH_KEY);
}

class ApiError extends Error {
  constructor(message, status, detail) {
    super(message);
    this.status = status;
    this.detail = detail;
  }
}

// Only one refresh call in flight at a time, even if several requests 401 together.
let refreshPromise = null;

async function doRefresh() {
  const { refresh } = getTokens();
  if (!refresh) throw new ApiError("No refresh token", 401);

  const res = await fetch(`${BASE_URL}/auth/refresh`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ refresh_token: refresh }),
  });

  if (!res.ok) {
    clearTokens();
    throw new ApiError("Session expired", res.status);
  }

  const data = await res.json();
  setTokens({ access_token: data.access_token });
  return data.access_token;
}

/**
 * Core request helper — AUTH BYPASS: no Authorization header sent.
 * Handles JSON bodies/query params.
 */
async function request(
  path,
  { method = "GET", body, query } = {}
) {
  const url = new URL(`${BASE_URL}${path}`);
  if (query) {
    Object.entries(query).forEach(([k, v]) => {
      if (v !== undefined && v !== null) url.searchParams.set(k, v);
    });
  }

  const headers = { "Content-Type": "application/json" };

  const res = await fetch(url.toString(), {
    method,
    headers,
    body: body !== undefined ? JSON.stringify(body) : undefined,
  });

  if (res.status === 204) return null;

  let data = null;
  const text = await res.text();
  if (text) {
    try {
      data = JSON.parse(text);
    } catch {
      data = text;
    }
  }

  if (!res.ok) {
    const message =
      (data && (data.detail?.[0]?.msg || data.detail)) ||
      `Request failed (${res.status})`;
    throw new ApiError(
      typeof message === "string" ? message : "Request failed",
      res.status,
      data
    );
  }

  return data;
}

// ── Auth ──────────────────────────────────────────────────────────────────

export const authApi = {
  register: (email, password, full_name) =>
    request("/auth/register", {
      method: "POST",
      auth: false,
      body: { email, password, full_name },
    }),

  login: async (email, password) => {
    const tokens = await request("/auth/login", {
      method: "POST",
      auth: false,
      body: { email, password },
    });
    setTokens(tokens);
    return tokens;
  },

  me: () => request("/auth/me"),

  logout: async () => {
    const { refresh } = getTokens();
    try {
      if (refresh) {
        await request("/auth/logout", {
          method: "POST",
          body: { refresh_token: refresh },
        });
      }
    } finally {
      clearTokens();
    }
  },
};

/**
 * Like `request`, but for binary responses (file downloads). Returns a Blob.
 * AUTH BYPASS: no Authorization header sent.
 */
async function requestBlob(path) {
  const res = await fetch(`${BASE_URL}${path}`);

  if (!res.ok) {
    throw new ApiError(`Download failed (${res.status})`, res.status);
  }

  return res.blob();
}

/** Triggers a browser save-as for a blob, without navigating the page. */
function saveBlob(blob, fileName) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = fileName;
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}

// ── Chat ──────────────────────────────────────────────────────────────────

export const chatApi = {
  listConversations: () => request("/chat/conversations"),

  createConversation: (name) =>
    request("/chat/conversations", { method: "POST", body: { name } }),

  renameConversation: (id, name) =>
    request(`/chat/conversations/${id}`, { method: "PATCH", body: { name } }),

  deleteConversation: (id) =>
    request(`/chat/conversations/${id}`, { method: "DELETE" }),

  getHistory: (id) => request(`/chat/conversations/${id}/messages`),

  sendMessage: (id, query) =>
    request(`/chat/conversations/${id}/messages`, {
      method: "POST",
      query: { query },
    }),

  // Downloads a source document by the file_name returned in CitedSource,
  // served from your backend's /chat/files/{file_name} endpoint (see
  // backend-snippet-download-endpoint.py).
  downloadFile: async (fileName) => {
    const blob = await requestBlob(`/chat/files/${encodeURIComponent(fileName)}`);
    saveBlob(blob, fileName);
  },
};

export { ApiError };
