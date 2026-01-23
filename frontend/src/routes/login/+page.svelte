<script lang="ts">
  import { z } from 'zod';
  import { goto } from '$app/navigation';
  import { api } from '$lib/api/client';
  import { setToken } from '$lib/stores/session';

  const schema = z.object({
    username: z.string().min(1),
    password: z.string().min(1)
  });

  let username = '';
  let password = '';
  let error = '';

  async function submit() {
    error = '';
    const result = schema.safeParse({ username, password });
    if (!result.success) {
      error = 'Please enter username and password.';
      return;
    }
    try {
      const response = await api.post<{ access_token: string; token_type: string }>('/auth/login', {
        username,
        password
      });
      setToken(response.access_token);
      await goto('/');
    } catch (err) {
      error = err instanceof Error ? err.message : 'Login failed.';
    }
  }
</script>

<div class="mx-auto max-w-md rounded-3xl border border-white/10 bg-white/5 p-8">
  <h2 class="text-2xl font-semibold">Sign in</h2>
  <p class="mt-2 text-sm text-haze/70">Authenticate to access RecursiveOps.</p>

  <div class="mt-6 space-y-4">
    <input
      class="w-full rounded-xl border border-white/10 bg-transparent px-4 py-3 text-sm"
      placeholder="Username"
      bind:value={username}
    />
    <input
      type="password"
      class="w-full rounded-xl border border-white/10 bg-transparent px-4 py-3 text-sm"
      placeholder="Password"
      bind:value={password}
    />
    {#if error}
      <p class="text-sm text-rose-300">{error}</p>
    {/if}
    <button class="w-full rounded-xl bg-neon/80 px-4 py-3 text-sm font-semibold text-night" on:click={submit}>
      Enter Control Room
    </button>
  </div>
</div>
