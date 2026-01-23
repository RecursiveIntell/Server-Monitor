<script lang="ts">
  import { page } from '$app/stores';
  import { createQuery } from '@tanstack/svelte-query';
  import { api } from '$lib/api/client';

  $: productId = $page.params.id;

  const productQuery = createQuery({
    queryKey: ['product', productId],
    queryFn: () => api.get<any>(`/products/${productId}`)
  });
</script>

<section class="glass rounded-3xl p-6">
  {#if $productQuery.data}
    <p class="panel-title muted">Product Detail</p>
    <h2 class="mt-2 text-2xl font-semibold">{$productQuery.data.name}</h2>
    <p class="mt-2 text-sm text-haze/70">{$productQuery.data.description ?? 'No description'}</p>
  {:else}
    <p class="text-sm text-haze/70">Loading...</p>
  {/if}
</section>
