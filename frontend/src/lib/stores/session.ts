import { browser } from '$app/environment';
import { writable } from 'svelte/store';

export type SessionState = {
  token: string | null;
};

const initialToken = browser ? localStorage.getItem('recursiveops_token') : null;

export const session = writable<SessionState>({
  token: initialToken
});

export function setToken(token: string | null) {
  session.set({ token });
  if (!browser) {
    return;
  }
  if (token) {
    localStorage.setItem('recursiveops_token', token);
  } else {
    localStorage.removeItem('recursiveops_token');
  }
}
