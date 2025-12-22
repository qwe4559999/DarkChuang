<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import { Send, Paperclip, X } from 'lucide-svelte';

  const dispatch = createEventDispatcher();
  let input = '';
  let selectedFile: File | null = null;
  let fileInput: HTMLInputElement;
  export let disabled = false;

  function handleSubmit() {
    if ((!input.trim() && !selectedFile) || disabled) return;
    dispatch('send', { text: input, file: selectedFile });
    input = '';
    selectedFile = null;
    if (fileInput) fileInput.value = '';
  }

  function handleKeydown(e: KeyboardEvent) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  }

  function handleFileSelect(e: Event) {
    const target = e.target as HTMLInputElement;
    if (target.files && target.files.length > 0) {
      selectedFile = target.files[0];
    }
  }

  function clearFile() {
    selectedFile = null;
    if (fileInput) fileInput.value = '';
  }
</script>

<div class="flex flex-col gap-2 p-2 bg-white border-t border-gray-200">
  {#if selectedFile}
    <div class="flex items-center gap-2 p-2 bg-gray-100 rounded-lg w-fit">
      <span class="text-sm text-gray-600 truncate max-w-[200px]">{selectedFile.name}</span>
      <button on:click={clearFile} class="text-gray-500 hover:text-red-500">
        <X size={16} />
      </button>
    </div>
  {/if}

  <div class="relative flex items-end gap-2">
    <input
        type="file"
        bind:this={fileInput}
        on:change={handleFileSelect}
        accept="image/*"
        class="hidden"
    />
    
    <button
        on:click={() => fileInput.click()}
        class="p-3 text-gray-500 hover:bg-gray-100 rounded-lg transition-colors"
        title="Upload Image"
    >
        <Paperclip size={20} />
    </button>

    <textarea
        bind:value={input}
        on:keydown={handleKeydown}
        disabled={disabled}
        placeholder="Ask about a chemical reaction, molecule, or upload a spectrum..."
        class="w-full max-h-32 p-3 bg-gray-50 border border-gray-200 rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:opacity-50"
        rows="1"
    ></textarea>

    <button
        on:click={handleSubmit}
        disabled={(!input.trim() && !selectedFile) || disabled}
        class="p-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
    >
        <Send size={20} />
    </button>
  </div>
</div>
