<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import { marked } from '../lib/markdown';
  import { Maximize2 } from 'lucide-svelte';
  import type { Message } from '../lib/api';
  import Molecule3D from './Molecule3D.svelte';

  export let message: Message;

  const dispatch = createEventDispatcher();

  // Check if content is a tool command (internal JSON)
  $: isToolCommand = (() => {
    if (!message.content) return false;
    const content = message.content.trim();
    // Check for raw JSON
    if (content.startsWith('{') && (content.includes('"tool":') || content.includes('"action":'))) return true;
    // Check for Markdown JSON block
    if (content.startsWith('```json') || content.startsWith('```')) {
       const inner = content.replace(/```json|```/g, '').trim();
       if (inner.startsWith('{') && (inner.includes('"tool":') || inner.includes('"action":'))) return true;
    }
    return false;
  })();

  function handleImagePreview(src: string) {
    dispatch('preview', { type: 'image', src });
  }

  function handleMoleculePreview(sdf: string) {
    dispatch('preview', { type: 'molecule', sdf });
  }

  // Custom renderer for images in Markdown
  const renderer = new marked.Renderer();
  renderer.image = (href, title, text) => {
    return `
      <div class="relative group inline-block my-2">
        <img src="${href}" alt="${text}" class="rounded-lg cursor-pointer hover:opacity-90 transition-opacity max-h-64 border border-gray-200 bg-white" />
        <div class="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity bg-black/50 text-white p-1 rounded-full pointer-events-none">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="15 3 21 3 21 9"></polyline><polyline points="9 21 3 21 3 15"></polyline><line x1="21" y1="3" x2="14" y2="10"></line><line x1="3" y1="21" x2="10" y2="14"></line></svg>
        </div>
      </div>
    `;
  };

  function handleContentClick(e: MouseEvent) {
    const target = e.target as HTMLElement;
    if (target.tagName === 'IMG') {
      const img = target as HTMLImageElement;
      handleImagePreview(img.src);
    }
  }
</script>

{#if !isToolCommand}
<div class={`flex w-full mb-4 ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}>
  <div
    class={`max-w-[80%] rounded-lg p-4 shadow-sm ${
      message.role === 'user'
        ? 'bg-blue-600 text-white'
        : 'bg-white border border-gray-200 text-gray-800'
    }`}
  >
    <!-- Image Display -->
    {#if message.type === 'image' && message.data?.imageUrl}
      <div class="mb-3 relative group">
        <img 
          src={message.data.imageUrl} 
          alt="Uploaded Content" 
          class="max-h-64 rounded-lg border border-white/20 cursor-pointer hover:opacity-90 transition-opacity"
          on:click={() => handleImagePreview(message.data.imageUrl)}
        />
        <div class="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity bg-black/50 text-white p-1 rounded-full pointer-events-none">
          <Maximize2 size={16} />
        </div>
      </div>
    {/if}

    <!-- Text Content (Markdown) -->
    <!-- svelte-ignore a11y-click-events-have-key-events -->
    <!-- svelte-ignore a11y-no-static-element-interactions -->
    <div 
      class="prose prose-sm max-w-none dark:prose-invert"
      on:click={handleContentClick}
    >
      {@html marked(message.content || '', { renderer })}
    </div>

    <!-- Molecule Display -->
    {#if message.type === 'molecule' && message.data}
      <div class="mt-3 p-3 bg-gray-50 rounded border border-gray-200">
        <!-- 3D Structure -->
        {#if message.data.sdf}
          <div class="mb-3 relative group">
             <Molecule3D sdf={message.data.sdf} />
             <button 
               class="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity bg-white/80 hover:bg-white text-gray-700 p-1.5 rounded-lg shadow-sm border border-gray-200"
               on:click={() => handleMoleculePreview(message.data.sdf)}
               title="Expand 3D View"
             >
               <Maximize2 size={16} />
             </button>
          </div>
        {:else if message.data.image}
           <!-- 2D Fallback -->
           <div class="mb-3 relative group flex justify-center">
             <!-- svelte-ignore a11y-click-events-have-key-events -->
             <!-- svelte-ignore a11y-no-noninteractive-element-interactions -->
             <img 
               src={message.data.image} 
               alt="Molecule Structure" 
               class="max-h-48 rounded cursor-pointer hover:opacity-90 transition-opacity" 
               on:click={() => handleImagePreview(message.data.image)}
             />
             <button 
               class="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity bg-black/50 text-white p-1 rounded-full"
               on:click={() => handleImagePreview(message.data.image)}
             >
               <Maximize2 size={16} />
             </button>
           </div>
        {/if}

        {#if message.data.properties}
          <div class="grid grid-cols-2 gap-2 text-xs">
            {#each Object.entries(message.data.properties) as [key, value]}
              <div class="flex justify-between">
                <span class="font-medium text-gray-500 capitalize">{key.replace(/_/g, ' ')}:</span>
                <span class="font-mono text-gray-800">{value}</span>
              </div>
            {/each}
          </div>
        {/if}
      </div>
    {/if}
  </div>
</div>
{/if}
