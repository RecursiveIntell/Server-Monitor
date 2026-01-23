<script lang="ts">
  import { createQuery } from '@tanstack/svelte-query';
  import { api } from '$lib/api/client';
  import LogViewer from '$lib/components/LogViewer.svelte';
  import type { LLMFailureExplanation, Settings } from '$lib/api/types';

  const settingsQuery = createQuery({
    queryKey: ['settings'],
    queryFn: () => api.get<Settings>('/settings')
  });

  let journalLines: string[] = [];
  let journalLimit = 500;
  let journalError = '';

  let unit = 'ssh.service';
  let systemdLines: string[] = [];
  let systemdError = '';

  let container = '';
  let podmanLines: string[] = [];
  let podmanError = '';

  let bundleUnits = '';
  let bundleContainers = '';
  let bundleIncludeSystem = true;
  let bundleLimit = 500;
  let bundleLines: string[] = [];
  let bundleError = '';
  let bundleLoading = false;
  let lastBundleRequest: {
    systemd_units: string[];
    podman_containers: string[];
    include_system: boolean;
    limit: number;
  } | null = null;

  let llmLoading = false;
  let llmError = '';
  let llmResult: LLMFailureExplanation | null = null;

  function splitList(value: string): string[] {
    return value
      .split(',')
      .map((item) => item.trim())
      .filter(Boolean);
  }

  async function loadJournal() {
    journalError = '';
    try {
      const limit = Number(journalLimit) || 500;
      journalLines = await api.get<string[]>(`/logs/journal?lines=${limit}`);
    } catch (err) {
      journalError = err instanceof Error ? err.message : 'Failed to load journal logs.';
    }
  }

  async function loadSystemd() {
    systemdError = '';
    try {
      systemdLines = await api.get<string[]>(`/logs/systemd/${unit}`);
    } catch (err) {
      systemdError = err instanceof Error ? err.message : 'Failed to load logs.';
    }
  }

  async function loadPodman() {
    podmanError = '';
    try {
      podmanLines = await api.get<string[]>(`/logs/podman/${container}`);
    } catch (err) {
      podmanError = err instanceof Error ? err.message : 'Failed to load logs.';
    }
  }

  async function loadBundle() {
    bundleError = '';
    bundleLoading = true;
    llmResult = null;
    try {
      const payload = {
        systemd_units: splitList(bundleUnits),
        podman_containers: splitList(bundleContainers),
        include_system: bundleIncludeSystem,
        limit: Number(bundleLimit) || 500
      };
      lastBundleRequest = payload;
      const response = await api.post<{ bundle: string }>('/logs/bundle', payload);
      bundleLines = response.bundle ? response.bundle.split('\n') : [];
    } catch (err) {
      bundleError = err instanceof Error ? err.message : 'Failed to build log bundle.';
    } finally {
      bundleLoading = false;
    }
  }

  async function analyzeBundle() {
    llmError = '';
    llmLoading = true;
    try {
      if (!bundleLines.length) {
        await loadBundle();
      }
      if (!bundleLines.length) {
        llmError = 'No bundle data available for analysis.';
        return;
      }
      const payload = {
        context: lastBundleRequest ?? {
          systemd_units: splitList(bundleUnits),
          podman_containers: splitList(bundleContainers),
          include_system: bundleIncludeSystem,
          limit: Number(bundleLimit) || 500
        },
        bundle: bundleLines.join('\n')
      };
      const response = await api.post<LLMFailureExplanation>('/llm/explain-failure', { payload });
      llmResult = response;
    } catch (err) {
      llmError = err instanceof Error ? err.message : 'LLM analysis failed.';
    } finally {
      llmLoading = false;
    }
  }
</script>

<section class="grid gap-6">
  <div class="glass rounded-3xl p-6">
    <p class="panel-title muted">System Journal</p>
    <div class="mt-4 flex flex-wrap items-center gap-3">
      <input class="w-24 rounded-xl border border-white/10 bg-transparent px-3 py-2 text-sm" type="number" bind:value={journalLimit} min="50" max="5000" />
      <button class="rounded-xl bg-neon/80 px-4 py-2 text-sm font-semibold text-night" on:click={loadJournal}>
        Load Journal
      </button>
    </div>
    {#if journalError}
      <p class="mt-3 text-sm text-rose-300">{journalError}</p>
    {/if}
    <div class="mt-4">
      <LogViewer lines={journalLines} />
    </div>
  </div>

  <div class="grid gap-6 lg:grid-cols-2">
    <div class="glass rounded-3xl p-6">
      <p class="panel-title muted">Systemd Logs</p>
      <div class="mt-4 flex flex-wrap gap-3">
        <input class="rounded-xl border border-white/10 bg-transparent px-4 py-2 text-sm" bind:value={unit} />
        <button class="rounded-xl bg-neon/80 px-4 py-2 text-sm font-semibold text-night" on:click={loadSystemd}>
          Load
        </button>
      </div>
      {#if systemdError}
        <p class="mt-3 text-sm text-rose-300">{systemdError}</p>
      {/if}
      <div class="mt-4">
        <LogViewer lines={systemdLines} />
      </div>
    </div>

    <div class="glass rounded-3xl p-6">
      <p class="panel-title muted">Podman Logs</p>
      <div class="mt-4 flex flex-wrap gap-3">
        <input
          class="rounded-xl border border-white/10 bg-transparent px-4 py-2 text-sm"
          bind:value={container}
          placeholder="Container ID or name"
        />
        <button class="rounded-xl bg-ember/80 px-4 py-2 text-sm font-semibold text-night" on:click={loadPodman}>
          Load
        </button>
      </div>
      {#if podmanError}
        <p class="mt-3 text-sm text-rose-300">{podmanError}</p>
      {/if}
      <div class="mt-4">
        <LogViewer lines={podmanLines} />
      </div>
    </div>
  </div>

  <div class="glass rounded-3xl p-6">
    <p class="panel-title muted">LLM Log Bundle</p>
    <p class="mt-2 text-sm text-haze/70">
      Combine logs and send the redacted bundle to the LLM for a failure summary.
    </p>
    <div class="mt-4 grid gap-3 md:grid-cols-2">
      <input
        class="rounded-xl border border-white/10 bg-transparent px-4 py-2 text-sm"
        bind:value={bundleUnits}
        placeholder="Systemd units (comma separated)"
      />
      <input
        class="rounded-xl border border-white/10 bg-transparent px-4 py-2 text-sm"
        bind:value={bundleContainers}
        placeholder="Podman containers (comma separated)"
      />
    </div>
    <div class="mt-3 flex flex-wrap items-center gap-3">
      <label class="flex items-center gap-2 text-xs text-haze/70">
        <input type="checkbox" bind:checked={bundleIncludeSystem} />
        Include system journal
      </label>
      <input class="w-24 rounded-xl border border-white/10 bg-transparent px-3 py-2 text-sm" type="number" bind:value={bundleLimit} min="50" max="5000" />
      <button
        class="rounded-xl bg-neon/80 px-4 py-2 text-sm font-semibold text-night"
        on:click={loadBundle}
        disabled={bundleLoading}
      >
        {bundleLoading ? 'Building…' : 'Build Bundle'}
      </button>
      <button
        class="rounded-xl border border-white/20 px-4 py-2 text-sm font-semibold text-haze/80"
        on:click={analyzeBundle}
        disabled={llmLoading || !$settingsQuery.data?.llm?.enabled}
      >
        {llmLoading ? 'Analyzing…' : 'Analyze with LLM'}
      </button>
      {#if $settingsQuery.data && !$settingsQuery.data.llm.enabled}
        <span class="text-xs text-haze/60">LLM disabled in settings.</span>
      {/if}
    </div>
    {#if bundleError}
      <p class="mt-3 text-sm text-rose-300">{bundleError}</p>
    {/if}
    <div class="mt-4">
      <LogViewer lines={bundleLines} />
    </div>
    {#if llmError}
      <p class="mt-4 text-sm text-rose-300">{llmError}</p>
    {/if}
    {#if llmResult}
      <div class="mt-4 grid gap-3 md:grid-cols-2">
        <div class="rounded-2xl border border-white/10 bg-white/5 p-4">
          <p class="text-xs text-haze/60">Summary</p>
          <p class="mt-2 text-sm text-haze/80">{llmResult.summary}</p>
        </div>
        <div class="rounded-2xl border border-white/10 bg-white/5 p-4">
          <p class="text-xs text-haze/60">Possible Causes</p>
          <ul class="mt-2 text-sm text-haze/80">
            {#each llmResult.possible_causes as cause}
              <li>• {cause}</li>
            {/each}
          </ul>
        </div>
        <div class="rounded-2xl border border-white/10 bg-white/5 p-4 md:col-span-2">
          <p class="text-xs text-haze/60">Suggested Actions</p>
          <ul class="mt-2 text-sm text-haze/80">
            {#each llmResult.suggested_actions as action}
              <li>• {action}</li>
            {/each}
          </ul>
        </div>
      </div>
    {/if}
  </div>
</section>
