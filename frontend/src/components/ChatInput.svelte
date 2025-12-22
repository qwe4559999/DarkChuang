<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import { Send } from 'lucide-svelte';

  const dispatch = createEventDispatcher();
  let input = '';
  export let disabled = false;

  function handleSubmit() {
    if (!input.trim() || disabled) return;
    dispatch('send', input);
    input = '';
  }

  function handleKeydown(e: KeyboardEvent) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  }
</script>

<div class="relative flex items-end gap-2 p-2 bg-white border-t border-gray-200">
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
    disabled={!input.trim() || disabled}
    class="p-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
  >
    <Send size={20} />
  </button>
</div>
