export const API = import.meta.env.VITE_API || "http://localhost:8000";
export const WS_URL = API.replace(/^http/, "ws") + "/ws";

export async function post(path, body) {
  const res = await fetch(`${API}${path}`, {
    method: "POST",
    headers: body ? { "Content-Type": "application/json" } : undefined,
    body: body ? JSON.stringify(body) : undefined,
  });
  return res.json();
}

export async function get(path) {
  const res = await fetch(`${API}${path}`);
  return res.json();
}
