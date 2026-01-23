import { get } from 'svelte/store';
import { session, setToken } from '$lib/stores/session';

const API_BASE = import.meta.env.VITE_API_BASE ?? 'http://127.0.0.1:8844/api';

export class ApiError extends Error {
  status: number;

  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

export async function apiFetch<T>(path: string, options: RequestInit = {}): Promise<T> {
  const { token } = get(session);
  const headers = new Headers(options.headers ?? {});
  headers.set('Content-Type', 'application/json');
  if (token) {
    headers.set('Authorization', `Bearer ${token}`);
  }

  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers
  });

  if (!response.ok) {
    if (response.status === 401) {
      setToken(null);
    }
    let message = response.statusText;
    try {
      const contentType = response.headers.get('content-type') ?? '';
      if (contentType.includes('application/json')) {
        const payload = await response.json();
        message = payload.detail ?? JSON.stringify(payload);
      } else {
        message = await response.text();
      }
    } catch (err) {
      message = response.statusText;
    }
    throw new ApiError(response.status, message || response.statusText);
  }

  return (await response.json()) as T;
}

export const api = {
  get: <T>(path: string) => apiFetch<T>(path),
  post: <T>(path: string, body?: unknown) =>
    apiFetch<T>(path, {
      method: 'POST',
      body: body ? JSON.stringify(body) : undefined
    })
};
