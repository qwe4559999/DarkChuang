<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import { slide } from 'svelte/transition';
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

<div class="w-full flex flex-col gap-3">
  {#if selectedFile}
    <div transition:slide={{ duration: 200 }} class="flex items-center gap-3 p-3 bg-blue-50 border border-blue-100 rounded-xl w-fit">
      <div class="p-2 bg-white rounded-lg text-blue-600">
        <Paperclip size={16} />
      </div>
      <div class="flex flex-col">
        <span class="text-sm font-medium text-gray-700 truncate max-w-[200px]">{selectedFile.name}</span>
        <span class="text-xs text-gray-500">{(selectedFile.size / 1024).toFixed(1)} KB</span>
      </div>
      <button 
        on:click={clearFile} 
        class="ml-2 p-1 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded-full transition-all"
      >
        <X size={16} />
      </button>
    </div>
  {/if}

  <div class="relative flex items-center gap-2 p-2 bg-white border border-gray-200 rounded-2xl shadow-sm hover:shadow-md transition-all focus-within:ring-2 focus-within:ring-blue-100 focus-within:border-blue-400">
    <input
        type="file"
        bind:this={fileInput}
        on:change={handleFileSelect}
        accept="image/*"
        class="hidden"
    />
    
    <button
        on:click={() => fileInput.click()}
        class="p-3 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded-xl transition-all"
        title="Upload Image"
    >
        <Paperclip size={20} />
    </button>

    <textarea
        bind:value={input}
        on:keydown={handleKeydown}
        disabled={disabled}
        placeholder="Ask about a chemical reaction, molecule, or upload a spectrum..."
        class="w-full max-h-32 py-3 bg-transparent border-none resize-none focus:ring-0 focus:outline-none text-gray-700 placeholder-gray-400 text-base leading-relaxed"
        rows="1"
    ></textarea>

    <button
        on:click={handleSubmit}
        disabled={(!input.trim() && !selectedFile) || disabled}
        class="p-3 bg-blue-600 text-white rounded-xl hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-sm hover:shadow-blue-200"
    >
        <Send size={20} />
    </button>
  </div>
</div>
