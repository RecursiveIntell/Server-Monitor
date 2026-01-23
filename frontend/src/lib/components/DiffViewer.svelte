<script lang="ts">
  export let diff: string = '';
</script>

<div class="glass rounded-2xl p-4">
  <p class="panel-title muted">Diff</p>
  <pre class="mt-3 max-h-96 overflow-auto text-xs font-mono text-haze/80">{diff}</pre>
</div>
