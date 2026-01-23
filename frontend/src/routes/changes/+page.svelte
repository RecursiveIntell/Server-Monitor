<script lang="ts">
  import { createQuery } from '@tanstack/svelte-query';
  import { api } from '$lib/api/client';
  import DiffViewer from '$lib/components/DiffViewer.svelte';
  import type { ChangeRecord } from '$lib/api/types';

  let selected: ChangeRecord | null = null;

  const changesQuery = createQuery({
    queryKey: ['changes'],
    queryFn: () => api.get<ChangeRecord[]>('/changes')
  });
</script>

<section class="grid gap-6 lg:grid-cols-[1fr,1.2fr]">
  <div class="glass rounded-3xl p-6">
    <p class="panel-title muted">Change Log</p>
    <div class="mt-4 space-y-3">
      {#if $changesQuery.data?.length}
        {#each $changesQuery.data as change}
          <button
            class="w-full rounded-2xl border border-white/10 bg-white/5 p-4 text-left"
            on:click={() => (selected = change)}
          >
            <p class="text-xs text-haze/60">{change.path}</p>
            <p class="text-sm font-semibold">{change.status}</p>
          </button>
        {/each}
      {:else}
        <p class="text-sm text-haze/70">No changes recorded.</p>
      {/if}
    </div>
  </div>

  <div>
    <DiffViewer diff={selected?.diff ?? 'Select a change to preview the diff.'} />
  </div>
</section>
