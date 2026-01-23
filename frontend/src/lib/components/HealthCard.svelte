<script lang="ts">
  import StatusBadge from './StatusBadge.svelte';

  export let name: string;
  export let url: string;
  export let status: 'ok' | 'warn' | 'error' | 'unknown' = 'unknown';
  export let detail: string = '';
</script>

<div class="glass rounded-2xl p-5">
  <div class="flex items-center justify-between">
    <div>
      <p class="panel-title muted">Health Check</p>
      <h3 class="text-lg font-semibold">{name}</h3>
      <p class="text-xs font-mono text-haze/70">{url}</p>
    </div>
    <StatusBadge {status} />
  </div>
  {#if detail}
    <p class="mt-3 text-sm text-haze/80">{detail}</p>
  {/if}
</div>
