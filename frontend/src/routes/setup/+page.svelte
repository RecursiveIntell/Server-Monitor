<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { api } from '$lib/api/client';
  import { setToken } from '$lib/stores/session';

  let requiresSetup: boolean | null = null;
  let username = '';
  let password = '';
  let error = '';
  let loading = false;

  onMount(async () => {
    try {
      const status = await api.get<{ requires_setup: boolean }>('/setup/status');
      requiresSetup = status.requires_setup;
    } catch (err) {
      error = err instanceof Error ? err.message : 'Failed to check setup status.';
      requiresSetup = null;
    }
  });

  async function submit() {
    error = '';
    loading = true;
    try {
      const response = await api.post<{ access_token: string; token_type: string }>('/setup/create', {
        username,
        password
      });
      setToken(response.access_token);
      await goto('/');
    } catch (err) {
      error = err instanceof Error ? err.message : 'Setup failed.';
    } finally {
      loading = false;
    }
  }
</script>

<section class="glass rounded-3xl p-8">
  <p class="panel-title muted">First-Run Setup</p>
  <h2 class="mt-2 text-2xl font-semibold">Create your admin account</h2>
  <p class="mt-2 text-sm text-haze/70">This only appears before any users exist.</p>

  {#if requiresSetup === false}
    <div class="mt-6 rounded-2xl border border-neon/40 bg-neon/10 p-4 text-sm text-neon">
      Setup has already been completed. <a class="ml-2 underline" href="/login">Sign in</a>.
    </div>
  {:else}
    <div class="mt-6 grid gap-4 sm:grid-cols-2">
      <input
        class="rounded-xl border border-white/10 bg-transparent px-4 py-3 text-sm"
        placeholder="Admin username"
        bind:value={username}
      />
      <input
        type="password"
        class="rounded-xl border border-white/10 bg-transparent px-4 py-3 text-sm"
        placeholder="Admin password"
        bind:value={password}
      />
    </div>
    {#if error}
      <p class="mt-3 text-sm text-rose-300">{error}</p>
    {/if}
    <button
      class="mt-4 rounded-xl bg-neon/80 px-4 py-3 text-sm font-semibold text-night"
      on:click={submit}
      disabled={loading}
    >
      {loading ? 'Creating...' : 'Create Admin'}
    </button>
  {/if}
</section>
