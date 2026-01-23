<script lang="ts">
  import '../app.css';
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { page } from '$app/stores';
  import { QueryClient, QueryClientProvider } from '@tanstack/svelte-query';
  import { session } from '$lib/stores/session';
  import { api } from '$lib/api/client';

  const queryClient = new QueryClient();
  const links = [
    { href: '/', label: 'Dashboard' },
    { href: '/routes', label: 'Routes' },
    { href: '/logs', label: 'Logs' },
    { href: '/changes', label: 'Changes' },
    { href: '/wizard/add-route', label: 'Add Route' },
    { href: '/settings', label: 'Settings' },
    { href: '/products', label: 'Products' }
  ];

  $: currentPath = $page.url.pathname;

  onMount(async () => {
    try {
      const status = await api.get<{ requires_setup: boolean }>('/setup/status');
      if (status.requires_setup && currentPath !== '/setup') {
        await goto('/setup');
      }
    } catch (err) {
      // Ignore setup checks if the API is unavailable.
    }
  });
</script>

<QueryClientProvider client={queryClient}>
  <div class="min-h-screen">
  <header class="glass mx-auto mt-6 flex w-[min(1200px,92%)] flex-wrap items-center justify-between gap-4 rounded-3xl px-6 py-4">
    <div>
      <p class="panel-title muted">RecursiveOps</p>
      <h1 class="text-2xl font-semibold tracking-tight">Fedora Control Center</h1>
    </div>
    <div class="hidden gap-3 text-sm md:flex">
      {#each links as link}
        <a class="rounded-full border border-white/10 px-4 py-2 text-haze/70 transition hover:border-neon/60 hover:text-neon" href={link.href}>
          {link.label}
        </a>
      {/each}
    </div>
    <div class="flex items-center gap-3 text-sm">
      {#if $session.token}
        <span class="rounded-full border border-neon/40 px-4 py-2 text-neon">Signed in</span>
      {:else}
        <a class="rounded-full border border-white/20 px-4 py-2 text-haze/70 hover:border-neon/60 hover:text-neon" href="/login">
          Sign in
        </a>
      {/if}
    </div>
  </header>

    <main class="mx-auto mt-10 w-[min(1200px,92%)]">
      <slot />
    </main>
  </div>
</QueryClientProvider>
