<script lang="ts">
  export let containers: Array<Record<string, any>> = [];
</script>

<div class="glass rounded-2xl p-4">
  <p class="panel-title muted">Podman Containers</p>
  <div class="mt-3 max-h-72 overflow-auto">
    <table class="w-full text-left text-xs">
      <thead class="text-haze/60">
        <tr>
          <th class="pb-2">Name</th>
          <th class="pb-2">State</th>
          <th class="pb-2">Image</th>
        </tr>
      </thead>
      <tbody>
        {#each containers as container}
          <tr class="border-t border-white/10">
            <td class="py-2 font-mono text-haze/80">{container.Names?.[0] ?? container.Id}</td>
            <td class={`py-2 ${container.State === 'running' ? 'text-neon' : 'text-rose-300'}`}>{container.State}</td>
            <td class="py-2 text-haze/60">{container.Image}</td>
          </tr>
        {/each}
      </tbody>
    </table>
  </div>
</div>
