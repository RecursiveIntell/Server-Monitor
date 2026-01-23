<script lang="ts">
  export let services: Array<{ unit: string; active: string; sub: string; description: string }> = [];
</script>

<div class="glass rounded-2xl p-4">
  <p class="panel-title muted">Systemd Services</p>
  <div class="mt-3 max-h-72 overflow-auto">
    <table class="w-full text-left text-xs">
      <thead class="text-haze/60">
        <tr>
          <th class="pb-2">Unit</th>
          <th class="pb-2">Active</th>
          <th class="pb-2">Sub</th>
          <th class="pb-2">Description</th>
        </tr>
      </thead>
      <tbody>
        {#each services as service}
          <tr class="border-t border-white/10">
            <td class="py-2 font-mono text-haze/80">{service.unit}</td>
            <td class={`py-2 ${service.active === 'active' ? 'text-neon' : service.active === 'failed' ? 'text-rose-300' : 'text-haze/60'}`}>
              {service.active}
            </td>
            <td class="py-2 text-haze/60">{service.sub}</td>
            <td class="py-2 text-haze/60">{service.description}</td>
          </tr>
        {/each}
      </tbody>
    </table>
  </div>
</div>
