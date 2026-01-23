<script lang="ts">
  export let index: number;
  export let title: string;
  export let active: boolean = false;
</script>

<div class={`rounded-xl border px-4 py-3 ${active ? 'border-neon/50 bg-neon/10' : 'border-white/10 bg-white/5'}`}>
  <p class="text-xs uppercase tracking-[0.3em] text-haze/60">Step {index}</p>
  <p class="text-sm font-semibold">{title}</p>
</div>
