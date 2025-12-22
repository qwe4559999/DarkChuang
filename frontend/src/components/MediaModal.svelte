<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import { X, ZoomIn } from 'lucide-svelte';
  import Molecule3D from './Molecule3D.svelte';

  export let type: 'image' | 'molecule' = 'image';
  export let src: string = '';
  export let sdf: string = '';
  export let alt: string = '';

  const dispatch = createEventDispatcher();

  function close() {
    dispatch('close');
  }

  function handleKeydown(e: KeyboardEvent) {
    if (e.key === 'Escape') close();
  }
</script>

<svelte:window on:keydown={handleKeydown} />

<!-- Backdrop -->
<div 
  class="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4 animate-in fade-in duration-200"
  on:click|self={close}
  role="button"
  tabindex="0"
  on:keydown={(e) => e.key === 'Enter' && close()}
>
  <!-- Close Button -->
  <button 
    class="absolute top-4 right-4 text-white/70 hover:text-white bg-white/10 hover:bg-white/20 rounded-full p-2 transition-all"
    on:click={close}
  >
    <X size={24} />
  </button>

  <!-- Content -->
  <div 
    class="relative max-w-5xl w-full max-h-[90vh] bg-white rounded-2xl overflow-hidden shadow-2xl flex flex-col"
    on:click|stopPropagation
    role="document"
  >
    {#if type === 'image'}
      <div class="flex-1 overflow-auto flex items-center justify-center bg-gray-900 p-4">
        <img {src} {alt} class="max-w-full max-h-[80vh] object-contain rounded-lg" />
      </div>
    {:else if type === 'molecule'}
      <div class="w-full h-[80vh] bg-gray-50 relative">
        <Molecule3D {sdf} className="h-full" />
        <div class="absolute bottom-4 left-4 bg-white/90 backdrop-blur px-3 py-1 rounded-full text-xs text-gray-500 shadow-sm">
            Interactive 3D View
        </div>
      </div>
    {/if}
  </div>
</div>
