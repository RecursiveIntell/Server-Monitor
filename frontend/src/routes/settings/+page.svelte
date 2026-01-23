<script lang="ts">
  import { createQuery, useQueryClient } from '@tanstack/svelte-query';
  import { api } from '$lib/api/client';
  import DiffViewer from '$lib/components/DiffViewer.svelte';
  import type { Settings } from '$lib/api/types';

  const queryClient = useQueryClient();
  const settingsQuery = createQuery({
    queryKey: ['settings'],
    queryFn: () => api.get<Settings>('/settings')
  });

  let initialized = false;
  let llmEnabled = false;
  let llmProvider = 'ollama';
  let ollamaBaseUrl = '';
  let ollamaModel = '';
  let cloudEnabled = false;
  let cloudProvider = 'stub';
  let diff = '';
  let diffError = '';
  let saveError = '';
  let saving = false;
  let ollamaStatus: { ok: boolean; error?: string; model?: string; base_url?: string } | null = null;
  let ollamaStatusLoading = false;
  let ollamaStatusError = '';
  let cloudflaredConfig = '';
  let pathDiff = '';
  let pathDiffError = '';
  let pathSaveError = '';
  let savingPaths = false;

  $: if ($settingsQuery.data && !initialized) {
    llmEnabled = $settingsQuery.data.llm.enabled;
    llmProvider = $settingsQuery.data.llm.provider;
    ollamaBaseUrl = $settingsQuery.data.llm.ollama.base_url;
    ollamaModel = $settingsQuery.data.llm.ollama.model;
    cloudEnabled = $settingsQuery.data.llm.cloud.enabled;
    cloudProvider = $settingsQuery.data.llm.cloud.provider;
    cloudflaredConfig = $settingsQuery.data.paths.cloudflared_config;
    initialized = true;
  }

  function buildPayload() {
    return {
      enabled: llmEnabled,
      provider: llmProvider,
      ollama: {
        base_url: ollamaBaseUrl,
        model: ollamaModel
      },
      cloud: {
        enabled: cloudEnabled,
        provider: cloudProvider
      }
    };
  }

  async function previewChanges() {
    diffError = '';
    diff = '';
    try {
      const response = await api.post<{ diff: string }>('/settings/llm/preview', buildPayload());
      diff = response.diff;
    } catch (err) {
      diffError = err instanceof Error ? err.message : 'Failed to preview changes.';
    }
  }

  async function applyChanges() {
    saveError = '';
    saving = true;
    try {
      const response = await api.post<{ diff: string }>('/settings/llm/apply', buildPayload());
      diff = response.diff;
      await queryClient.refetchQueries({ queryKey: ['settings'] });
    } catch (err) {
      saveError = err instanceof Error ? err.message : 'Failed to apply settings.';
    } finally {
      saving = false;
    }
  }

  function buildPathsPayload() {
    return {
      cloudflared_config: cloudflaredConfig
    };
  }

  async function previewPathChanges() {
    pathDiffError = '';
    pathDiff = '';
    try {
      const response = await api.post<{ diff: string }>('/settings/paths/preview', buildPathsPayload());
      pathDiff = response.diff;
    } catch (err) {
      pathDiffError = err instanceof Error ? err.message : 'Failed to preview path changes.';
    }
  }

  async function applyPathChanges() {
    pathSaveError = '';
    savingPaths = true;
    try {
      const response = await api.post<{ diff: string }>('/settings/paths/apply', buildPathsPayload());
      pathDiff = response.diff;
      await queryClient.refetchQueries({ queryKey: ['settings'] });
    } catch (err) {
      pathSaveError = err instanceof Error ? err.message : 'Failed to apply path changes.';
    } finally {
      savingPaths = false;
    }
  }

  async function checkOllama() {
    ollamaStatusError = '';
    ollamaStatusLoading = true;
    try {
      ollamaStatus = await api.get<any>('/llm/health');
    } catch (err) {
      ollamaStatusError = err instanceof Error ? err.message : 'Failed to check Ollama.';
    } finally {
      ollamaStatusLoading = false;
    }
  }
</script>

<section class="glass rounded-3xl p-6">
  <p class="panel-title muted">Settings</p>
  {#if $settingsQuery.isError}
    <div class="mt-4 rounded-2xl border border-rose-400/40 bg-rose-400/10 p-4 text-sm text-rose-200">
      {$settingsQuery.error?.message ?? 'Failed to load settings.'}
      <a class="ml-2 underline" href="/login">Sign in</a>
    </div>
  {:else if $settingsQuery.data}
    <div class="mt-4 grid gap-4 md:grid-cols-2">
      <div class="rounded-2xl border border-white/10 bg-white/5 p-4">
        <p class="text-xs text-haze/60">Bind</p>
        <p class="text-lg font-semibold">{$settingsQuery.data.server.bind_host}:{$settingsQuery.data.server.bind_port}</p>
      </div>
      <div class="rounded-2xl border border-white/10 bg-white/5 p-4">
        <p class="text-xs text-haze/60">Cloudflared</p>
        <p class="text-sm font-mono text-haze/70">{$settingsQuery.data.paths.cloudflared_config}</p>
      </div>
      <div class="rounded-2xl border border-white/10 bg-white/5 p-4">
        <p class="text-xs text-haze/60">LLM</p>
        <p class="text-lg font-semibold">{$settingsQuery.data.llm.enabled ? 'Enabled' : 'Disabled'}</p>
      </div>
      <div class="rounded-2xl border border-white/10 bg-white/5 p-4">
        <p class="text-xs text-haze/60">Actions</p>
        <p class="text-lg font-semibold">{$settingsQuery.data.security.allow_actions ? 'Allowed' : 'Blocked'}</p>
      </div>
    </div>

    <div class="mt-8 grid gap-6 lg:grid-cols-[1.1fr,0.9fr]">
      <div class="rounded-2xl border border-white/10 bg-white/5 p-5">
        <p class="panel-title muted">LLM Configuration</p>
        <p class="mt-2 text-sm text-haze/70">
          Update model access settings. Changes are written to the config with a snapshot.
        </p>
        <div class="mt-4 grid gap-4">
          <label class="flex items-center gap-3 text-sm text-haze/70">
            <input type="checkbox" bind:checked={llmEnabled} />
            Enable LLM
          </label>
          <div>
            <p class="text-xs text-haze/60">Provider</p>
            <input class="mt-2 w-full rounded-xl border border-white/10 bg-transparent px-3 py-2 text-sm" bind:value={llmProvider} />
          </div>
          <div class="grid gap-3 md:grid-cols-2">
            <div>
              <p class="text-xs text-haze/60">Ollama Base URL</p>
              <input
                class="mt-2 w-full rounded-xl border border-white/10 bg-transparent px-3 py-2 text-sm"
                bind:value={ollamaBaseUrl}
              />
            </div>
            <div>
              <p class="text-xs text-haze/60">Ollama Model</p>
              <input
                class="mt-2 w-full rounded-xl border border-white/10 bg-transparent px-3 py-2 text-sm"
                bind:value={ollamaModel}
              />
            </div>
          </div>
          <div class="grid gap-3 md:grid-cols-2">
            <label class="flex items-center gap-3 text-sm text-haze/70">
              <input type="checkbox" bind:checked={cloudEnabled} />
              Enable Cloud Provider
            </label>
            <div>
              <p class="text-xs text-haze/60">Cloud Provider</p>
              <input
                class="mt-2 w-full rounded-xl border border-white/10 bg-transparent px-3 py-2 text-sm"
                bind:value={cloudProvider}
              />
            </div>
          </div>
        <div class="flex flex-wrap items-center gap-3">
          <button class="rounded-xl border border-white/20 px-4 py-2 text-sm font-semibold text-haze/80" on:click={previewChanges}>
            Preview Diff
          </button>
          <button
              class="rounded-xl bg-neon/80 px-4 py-2 text-sm font-semibold text-night"
              on:click={applyChanges}
              disabled={saving || !$settingsQuery.data.security.allow_actions}
            >
              {saving ? 'Saving…' : 'Apply Changes'}
            </button>
            <button
              class="rounded-xl border border-white/20 px-4 py-2 text-sm font-semibold text-haze/80"
              on:click={checkOllama}
              disabled={ollamaStatusLoading}
            >
              {ollamaStatusLoading ? 'Checking…' : 'Test Ollama'}
            </button>
            {#if !$settingsQuery.data.security.allow_actions}
              <span class="text-xs text-haze/60">Actions disabled.</span>
            {/if}
          </div>
          {#if diffError}
            <p class="text-sm text-rose-300">{diffError}</p>
          {/if}
          {#if saveError}
            <p class="text-sm text-rose-300">{saveError}</p>
          {/if}
          {#if ollamaStatusError}
            <p class="text-sm text-rose-300">{ollamaStatusError}</p>
          {/if}
          {#if ollamaStatus}
            <p class={`text-sm ${ollamaStatus.ok ? 'text-neon' : 'text-rose-300'}`}>
              {ollamaStatus.ok ? 'Ollama reachable and model found.' : `Ollama check failed: ${ollamaStatus.error ?? 'unknown error'}`}
            </p>
          {/if}
        </div>
      </div>

      <div class="flex flex-col gap-4">
        {#if diff}
          <DiffViewer {diff} />
        {:else}
          <div class="rounded-2xl border border-white/10 bg-white/5 p-4">
            <p class="text-xs text-haze/60">Diff Preview</p>
            <p class="mt-2 text-sm text-haze/70">Run preview to see YAML changes before applying.</p>
          </div>
        {/if}
      </div>
    </div>

    <div class="mt-8 grid gap-6 lg:grid-cols-[1.1fr,0.9fr]">
      <div class="rounded-2xl border border-white/10 bg-white/5 p-5">
        <p class="panel-title muted">Cloudflared Config Path</p>
        <p class="mt-2 text-sm text-haze/70">Point to the cloudflared config used for routes and health checks.</p>
        <div class="mt-4 grid gap-3">
          <input
            class="w-full rounded-xl border border-white/10 bg-transparent px-3 py-2 text-sm"
            bind:value={cloudflaredConfig}
          />
          <div class="flex flex-wrap items-center gap-3">
            <button class="rounded-xl border border-white/20 px-4 py-2 text-sm font-semibold text-haze/80" on:click={previewPathChanges}>
              Preview Diff
            </button>
            <button
              class="rounded-xl bg-neon/80 px-4 py-2 text-sm font-semibold text-night"
              on:click={applyPathChanges}
              disabled={savingPaths || !$settingsQuery.data.security.allow_actions}
            >
              {savingPaths ? 'Saving…' : 'Apply Path'}
            </button>
            {#if !$settingsQuery.data.security.allow_actions}
              <span class="text-xs text-haze/60">Actions disabled.</span>
            {/if}
          </div>
          {#if pathDiffError}
            <p class="text-sm text-rose-300">{pathDiffError}</p>
          {/if}
          {#if pathSaveError}
            <p class="text-sm text-rose-300">{pathSaveError}</p>
          {/if}
        </div>
      </div>

      <div class="flex flex-col gap-4">
        {#if pathDiff}
          <DiffViewer diff={pathDiff} />
        {:else}
          <div class="rounded-2xl border border-white/10 bg-white/5 p-4">
            <p class="text-xs text-haze/60">Diff Preview</p>
            <p class="mt-2 text-sm text-haze/70">Preview to confirm path changes.</p>
          </div>
        {/if}
      </div>
    </div>
  {:else}
    <p class="text-sm text-haze/70">Loading...</p>
  {/if}
</section>
