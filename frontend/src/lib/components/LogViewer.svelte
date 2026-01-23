<script lang="ts">
  export let lines: string[] = [];
</script>

<div class="glass rounded-2xl p-4">
  <p class="panel-title muted">Logs</p>
  <pre class="mt-3 max-h-96 overflow-auto text-xs font-mono text-haze/80">{lines.join('\n')}</pre>
</div>
