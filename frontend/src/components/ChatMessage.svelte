<script lang="ts">
  import { marked } from 'marked';
  import type { Message } from '../lib/api';

  export let message: Message;

  // Configure marked for security (optional but recommended)
  // marked.setOptions({ sanitize: true });
</script>

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
      <div class="mb-3">
        <img src={message.data.imageUrl} alt="Uploaded Content" class="max-h-64 rounded-lg border border-white/20" />
      </div>
    {/if}

    <!-- Text Content (Markdown) -->
    <div class="prose prose-sm max-w-none dark:prose-invert">
      {@html marked(message.content || '')}
    </div>

    <!-- Molecule Display -->
    {#if message.type === 'molecule' && message.data}
      <div class="mt-3 p-3 bg-gray-50 rounded border border-gray-200">
        {#if message.data.image}
           <!-- svelte-ignore a11y-img-redundant-alt -->
          <img src={message.data.image} alt="Molecule Structure" class="mx-auto mb-2 max-h-48" />
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
