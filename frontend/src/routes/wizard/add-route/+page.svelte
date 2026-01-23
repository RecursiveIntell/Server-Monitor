<script lang="ts">
  import DiffViewer from '$lib/components/DiffViewer.svelte';
  import WizardStep from '$lib/components/WizardStep.svelte';
  import { api } from '$lib/api/client';

  let step = 1;
  let configText = '';
  let diff = '';
  let error = '';

  async function preview() {
    error = '';
    try {
      const response = await api.post<{ diff: string }>('/routes/cloudflared/preview', {
        new_config: configText
      });
      diff = response.diff;
      step = 2;
    } catch (err) {
      error = err instanceof Error ? err.message : 'Preview failed.';
    }
  }

  async function apply() {
    error = '';
    try {
      await api.post('/routes/cloudflared/apply', { new_config: configText, reason: 'Wizard apply' });
      step = 3;
    } catch (err) {
      error = err instanceof Error ? err.message : 'Apply failed.';
    }
  }
</script>

<section class="grid gap-6">
  <div class="flex flex-wrap gap-3">
    <WizardStep index={1} title="Paste Config" active={step === 1} />
    <WizardStep index={2} title="Preview Diff" active={step === 2} />
    <WizardStep index={3} title="Applied" active={step === 3} />
  </div>

  <div class="glass rounded-3xl p-6">
    {#if step === 1}
      <p class="panel-title muted">Paste Cloudflared Config</p>
      <textarea
        class="mt-4 h-64 w-full rounded-2xl border border-white/10 bg-transparent p-4 font-mono text-xs"
        bind:value={configText}
        placeholder="Paste full config.yml contents here"
      ></textarea>
      <button class="mt-4 rounded-xl bg-neon/80 px-4 py-2 text-sm font-semibold text-night" on:click={preview}>
        Preview Diff
      </button>
    {:else if step === 2}
      <DiffViewer {diff} />
      <button class="mt-4 rounded-xl bg-ember/80 px-4 py-2 text-sm font-semibold text-night" on:click={apply}>
        Apply Patch
      </button>
    {:else}
      <p class="text-lg font-semibold text-neon">Config applied. Review changes for rollback.</p>
    {/if}

    {#if error}
      <p class="mt-3 text-sm text-rose-300">{error}</p>
    {/if}
  </div>
</section>
