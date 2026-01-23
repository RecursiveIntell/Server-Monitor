<script lang="ts">
  import { createQuery } from '@tanstack/svelte-query';
  import HealthCard from '$lib/components/HealthCard.svelte';
  import StatusBadge from '$lib/components/StatusBadge.svelte';
  import ServiceTable from '$lib/components/ServiceTable.svelte';
  import ContainerTable from '$lib/components/ContainerTable.svelte';
  import { api } from '$lib/api/client';

  const overviewQuery = createQuery({
    queryKey: ['overview'],
    queryFn: () => api.get<any>('/overview')
  });

  const routesQuery = createQuery({
    queryKey: ['routes'],
    queryFn: () => api.get<any[]>('/routes/cloudflared')
  });

  const checksQuery = createQuery({
    queryKey: ['checks'],
    queryFn: () => api.get<any[]>('/checks')
  });
</script>

<section class="grid gap-8">
  <div class="grid gap-6 lg:grid-cols-[2fr,1fr]">
    <div class="glass rounded-3xl p-6">
      <p class="panel-title muted">System Pulse</p>
      <div class="mt-4 grid gap-4 sm:grid-cols-3">
        <div class="rounded-2xl border border-white/10 bg-white/5 p-4">
          <p class="text-xs uppercase tracking-[0.3em] text-haze/60">Services</p>
          <p class="mt-2 text-3xl font-semibold text-neon">
            {$overviewQuery.data?.summary?.services_total ?? '--'}
          </p>
          <p class="text-xs text-haze/60">Failed: {$overviewQuery.data?.summary?.services_failed ?? '--'}</p>
        </div>
        <div class="rounded-2xl border border-white/10 bg-white/5 p-4">
          <p class="text-xs uppercase tracking-[0.3em] text-haze/60">Containers</p>
          <p class="mt-2 text-3xl font-semibold text-ember">
            {$overviewQuery.data?.summary?.containers_total ?? '--'}
          </p>
          <p class="text-xs text-haze/60">Running: {$overviewQuery.data?.summary?.containers_running ?? '--'}</p>
        </div>
        <div class="rounded-2xl border border-white/10 bg-white/5 p-4">
          <p class="text-xs uppercase tracking-[0.3em] text-haze/60">Routes</p>
          <p class="mt-2 text-3xl font-semibold text-haze">
            {$routesQuery.data?.length ?? '--'}
          </p>
        </div>
      </div>
    </div>

    <div class="glass rounded-3xl p-6">
      <p class="panel-title muted">Status</p>
      <div class="mt-5 flex flex-col gap-4">
        <div class="flex items-center justify-between">
          <span class="text-sm text-haze/70">API Connection</span>
          <StatusBadge status={$overviewQuery.isError ? 'error' : 'ok'} />
        </div>
        <div class="flex items-center justify-between">
          <span class="text-sm text-haze/70">Cloudflared</span>
          <StatusBadge status={$routesQuery.data ? 'ok' : 'warn'} />
        </div>
      </div>
    </div>
  </div>

  <div class="grid gap-6 lg:grid-cols-[1.2fr,1fr]">
    <div class="grid gap-4">
      <p class="panel-title muted">Health Checks</p>
      {#if $checksQuery.data?.length}
        {#each $checksQuery.data as check}
          <HealthCard name={check.name} url={check.url} status="unknown" detail="Run to refresh." />
        {/each}
      {:else}
        <HealthCard name="No checks yet" url="/checks" status="warn" detail="Add a health check to start monitoring." />
      {/if}
    </div>
    <div class="glass rounded-3xl p-6">
      <p class="panel-title muted">Recent Routes</p>
      <div class="mt-4 space-y-3">
        {#if $routesQuery.data?.length}
          {#each $routesQuery.data.slice(0, 4) as route}
            <div class="rounded-xl border border-white/10 bg-white/5 p-3">
              <p class="text-sm font-semibold">{route.hostname ?? 'catch-all'}</p>
              <p class="text-xs font-mono text-haze/70">{route.service}</p>
            </div>
          {/each}
        {:else}
          <p class="text-sm text-haze/70">No routes loaded.</p>
        {/if}
      </div>
    </div>
  </div>

  {#if $overviewQuery.data}
    <div class="grid gap-6 lg:grid-cols-2">
      <ServiceTable services={$overviewQuery.data.services ?? []} />
      <ContainerTable containers={$overviewQuery.data.containers ?? []} />
    </div>
  {/if}
</section>
