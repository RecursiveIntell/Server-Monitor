<script lang="ts">
  export let status: 'ok' | 'warn' | 'error' | 'unknown' = 'unknown';

  const colors: Record<string, string> = {
    ok: 'bg-neon/20 text-neon border-neon/40',
    warn: 'bg-amber-400/20 text-amber-200 border-amber-400/40',
    error: 'bg-rose-400/20 text-rose-200 border-rose-400/40',
    unknown: 'bg-steel/20 text-steel border-steel/40'
  };
</script>

<span class={`inline-flex items-center gap-1 rounded-full border px-3 py-1 text-xs font-semibold uppercase tracking-[0.2em] ${colors[status]}`}>
  {status}
</span>
