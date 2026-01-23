<script lang="ts">
  import { createQuery } from '@tanstack/svelte-query';
  import { api } from '$lib/api/client';

  const productsQuery = createQuery({
    queryKey: ['products'],
    queryFn: () => api.get<any[]>('/products')
  });
</script>

<section class="glass rounded-3xl p-6">
  <p class="panel-title muted">Products</p>
  <div class="mt-4 grid gap-4">
    {#if $productsQuery.data?.length}
      {#each $productsQuery.data as product}
        <a href={`/products/${product.id}`} class="rounded-2xl border border-white/10 bg-white/5 p-4">
          <p class="text-lg font-semibold">{product.name}</p>
          <p class="text-sm text-haze/70">{product.description ?? 'No description'}</p>
        </a>
      {/each}
    {:else}
      <p class="text-sm text-haze/70">No products available.</p>
    {/if}
  </div>
</section>
