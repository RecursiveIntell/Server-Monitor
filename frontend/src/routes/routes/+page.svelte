<script lang="ts">
  import { createQuery, useQueryClient } from '@tanstack/svelte-query';
  import StatusBadge from '$lib/components/StatusBadge.svelte';
  import { api } from '$lib/api/client';
  import type { CloudflaredTarget } from '$lib/api/types';

  const queryClient = useQueryClient();
  const routesQuery = createQuery({
    queryKey: ['routes'],
    queryFn: () => api.get<any[]>('/routes/cloudflared')
  });

  const targetsQuery = createQuery({
    queryKey: ['cloudflared-targets'],
    queryFn: () => api.get<CloudflaredTarget[]>('/cloudflared/targets')
  });

  let runResults: any[] = [];
  let runError = '';
  let runLoading = false;

  async function runHealth() {
    runError = '';
    runLoading = true;
    try {
      await queryClient.refetchQueries({ queryKey: ['cloudflared-targets'] });
      const response = await api.post<{ results: any[] }>('/cloudflared/run');
      runResults = response.results;
      await queryClient.refetchQueries({ queryKey: ['cloudflared-targets'] });
    } catch (err) {
      runError = err instanceof Error ? err.message : 'Failed to run health checks.';
    } finally {
      runLoading = false;
    }
  }
</script>

<section class="grid gap-6">
  <div class="glass rounded-3xl p-6">
    <div class="flex items-center justify-between">
      <p class="panel-title muted">Cloudflared Routes</p>
      <button class="rounded-xl bg-neon/80 px-4 py-2 text-sm font-semibold text-night" on:click={runHealth} disabled={runLoading}>
        {runLoading ? 'Running…' : 'Run Health Checks'}
      </button>
    </div>
    {#if $routesQuery.isError}
      <p class="mt-3 text-sm text-rose-300">{$routesQuery.error?.message ?? 'Failed to load routes.'}</p>
    {/if}
    <div class="mt-5 grid gap-4">
      {#if $routesQuery.data?.length}
        {#each $routesQuery.data as route, index}
          <a href={`/routes/${index}`} class="rounded-2xl border border-white/10 bg-white/5 p-4">
            <p class="text-sm text-haze/70">{route.hostname ?? 'catch-all'}</p>
            <p class="text-lg font-semibold">{route.service}</p>
          </a>
        {/each}
      {:else}
        <p class="text-sm text-haze/70">No routes loaded.</p>
      {/if}
    </div>
  </div>

  <div class="glass rounded-3xl p-6">
    <p class="panel-title muted">Health Targets</p>
    {#if runError}
      <p class="mt-3 text-sm text-rose-300">{runError}</p>
    {/if}
    {#if $targetsQuery.isError}
      <p class="mt-3 text-sm text-rose-300">{$targetsQuery.error?.message ?? 'Failed to load targets.'}</p>
    {/if}
    <div class="mt-4 space-y-3">
      {#if $targetsQuery.data?.length}
        {#each $targetsQuery.data as target}
          <div class="rounded-xl border border-white/10 bg-white/5 p-3">
            <div class="flex items-center justify-between">
              <p class="text-sm font-semibold">{target.hostname}</p>
              {#if target.last_result}
                <StatusBadge status={target.last_result.ok ? 'ok' : 'error'} />
              {:else}
                <StatusBadge status="unknown" />
              {/if}
            </div>
            <p class="text-xs font-mono text-haze/70">{target.url}</p>
            {#if target.last_result}
              <p class="mt-2 text-xs text-haze/70">
                {target.last_result.status_code ?? 'no status'} ·
                {target.last_result.response_time_ms ? `${Math.round(target.last_result.response_time_ms)}ms` : 'no timing'}
              </p>
              {#if target.last_result.error}
                <p class="mt-1 text-xs text-rose-200">{target.last_result.error}</p>
              {/if}
            {/if}
          </div>
        {/each}
      {:else}
        <p class="text-sm text-haze/70">No health targets available.</p>
      {/if}
    </div>
  </div>

  {#if runResults.length}
    <div class="glass rounded-3xl p-6">
      <p class="panel-title muted">Latest Run</p>
      <div class="mt-4 grid gap-3">
        {#each runResults as result}
          <div class="rounded-xl border border-white/10 bg-white/5 p-3">
            <div class="flex items-center justify-between">
              <p class="text-sm font-semibold">{result.hostname}</p>
              <StatusBadge status={result.ok ? 'ok' : 'error'} />
            </div>
            <p class="text-xs font-mono text-haze/70">{result.url}</p>
            <p class="mt-2 text-xs text-haze/70">
              {result.status_code ?? 'no status'} ·
              {result.response_time_ms ? `${Math.round(result.response_time_ms)}ms` : 'no timing'}
            </p>
            {#if result.error}
              <p class="mt-1 text-xs text-rose-200">{result.error}</p>
            {/if}
          </div>
        {/each}
      </div>
    </div>
  {/if}
</section>
