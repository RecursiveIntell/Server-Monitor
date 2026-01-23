<script lang="ts">
  import { page } from '$app/stores';
  import { createQuery } from '@tanstack/svelte-query';
  import { api } from '$lib/api/client';
  import type { CloudflaredRoute } from '$lib/api/types';

  $: routeIndex = Number($page.params.id);

  const routesQuery = createQuery({
    queryKey: ['routes'],
    queryFn: () => api.get<CloudflaredRoute[]>('/routes/cloudflared')
  });
</script>

<section class="glass rounded-3xl p-6">
  <p class="panel-title muted">Route Detail</p>
  {#if $routesQuery.data}
    {#if $routesQuery.data[routeIndex]}
      <h2 class="mt-2 text-2xl font-semibold">{$routesQuery.data[routeIndex].hostname ?? 'catch-all'}</h2>
      <p class="mt-2 text-sm text-haze/70">{$routesQuery.data[routeIndex].service}</p>
    {:else}
      <p class="text-sm text-haze/70">Route not found.</p>
    {/if}
  {:else}
    <p class="text-sm text-haze/70">Loading...</p>
  {/if}
</section>
