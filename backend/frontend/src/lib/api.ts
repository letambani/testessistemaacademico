export async function fetchJson<T>(
  url: string,
  init?: RequestInit,
): Promise<T> {
  const method = (init?.method ?? "GET").toUpperCase();
  const jsonBody = method !== "GET" && method !== "HEAD" && init?.body;
  const r = await fetch(url, {
    ...init,
    credentials: "include",
    headers: {
      ...(jsonBody ? { "Content-Type": "application/json" } : {}),
      ...(init?.headers ?? {}),
    },
  });
  const data: unknown = await r.json().catch(() => ({}));
  if (!r.ok) {
    const err =
      typeof data === "object" &&
      data !== null &&
      "error" in data &&
      typeof (data as { error?: unknown }).error === "string"
        ? (data as { error: string }).error
        : `${r.status} ${r.statusText}`;
    throw new Error(err);
  }
  return data as T;
}
