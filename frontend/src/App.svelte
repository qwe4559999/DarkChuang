<script lang="ts">
  import { onMount, afterUpdate } from 'svelte';
  import ChatMessage from './components/ChatMessage.svelte';
  import ChatInput from './components/ChatInput.svelte';
  import { messages, isLoading } from './stores/chat';
  import { api } from './lib/api';
  import { FlaskConical } from 'lucide-svelte';

  let chatContainer: HTMLElement;

  function scrollToBottom() {
    if (chatContainer) {
      chatContainer.scrollTop = chatContainer.scrollHeight;
    }
  }

  afterUpdate(() => {
    scrollToBottom();
  });

  async function handleSend(event: CustomEvent<string>) {
    const text = event.detail;
    if (!text.trim()) return;

    // Add user message
    messages.addMessage({ role: 'user', content: text });
    isLoading.set(true);

    try {
      // 1. Get Chat Response
      const response = await api.sendMessage(text);
      messages.addMessage({ role: 'assistant', content: response.message || response }); // Handle varied backend responses

      // 2. Simple Intent Detection for Chemistry Tools (Demo Logic)
      // In a real app, the LLM would decide this via function calling.
      // Here we look for simple keywords to trigger the "Chemistry Tool" visual
      const lowerText = text.toLowerCase();
      const isChemistryQuery = /molecule|structure|calculate|properties|结构|分子|属性/.test(lowerText);

      // Extract potential molecule name (very naive, just assumes the last word or the whole query if short)
      // A better way is to ask the LLM to extract the SMILES/Name.
      // For this demo, we'll try to extract if the user says "Show me aspirin" -> "aspirin"
      let moleculeName = "";
      if (isChemistryQuery) {
          // Naive extraction: try to find common chemical names or just use the query if short
          const parts = text.split(' ');
          moleculeName = parts[parts.length - 1].replace(/[?.!]/g, '');

          // Or just try to get property for the whole query if it looks like a formula (e.g. "C6H6")
          if (/^[A-Za-z0-9]+$/.test(text)) moleculeName = text;
      }

      if (isChemistryQuery && moleculeName && moleculeName.length > 1) {
          try {
              // Parallel fetch for structure and properties
              const [propsData, structData] = await Promise.all([
                  api.calculateProperties(moleculeName).catch(e => null),
                  api.generateStructure(moleculeName).catch(e => null)
              ]);

              if ((propsData && propsData.success) || (structData && structData.success)) {
                  messages.addMessage({
                      role: 'assistant',
                      content: `I analyzed **${moleculeName}** for you:`,
                      type: 'molecule',
                      data: {
                          properties: propsData?.success ? propsData.properties : null,
                          image: structData?.success ? structData.image : null
                      }
                  });
              }
          } catch (chemError) {
              console.error("Chemistry tool error:", chemError);
          }
      }

    } catch (error) {
      messages.addMessage({
        role: 'assistant',
        content: `**Error:** Failed to get response. ${error}`
      });
    } finally {
      isLoading.set(false);
    }
  }
</script>

<div class="flex flex-col h-screen bg-gray-100">
  <!-- Header -->
  <header class="bg-white shadow-sm px-6 py-4 flex items-center gap-3 z-10">
    <div class="p-2 bg-blue-100 text-blue-600 rounded-lg">
      <FlaskConical size={24} />
    </div>
    <div>
      <h1 class="text-xl font-bold text-gray-900">DarkChuang AI</h1>
      <p class="text-xs text-gray-500">Professional Chemistry Assistant</p>
    </div>
  </header>

  <!-- Chat Area -->
  <div
    class="flex-1 overflow-y-auto p-4 md:p-6"
    bind:this={chatContainer}
  >
    <div class="max-w-3xl mx-auto space-y-6">
      {#if $messages.length === 0}
        <div class="text-center text-gray-400 py-20">
          <FlaskConical size={48} class="mx-auto mb-4 opacity-50" />
          <p class="text-lg">Ask me about chemical structures, reactions, or upload a spectrum.</p>
          <div class="mt-6 flex flex-wrap justify-center gap-2">
             <button class="px-3 py-1 bg-white border border-gray-200 rounded-full text-sm hover:bg-gray-50 transition" on:click={() => handleSend(new CustomEvent('send', { detail: 'Show me the structure of Aspirin' }))}>
                Show me the structure of Aspirin
             </button>
             <button class="px-3 py-1 bg-white border border-gray-200 rounded-full text-sm hover:bg-gray-50 transition" on:click={() => handleSend(new CustomEvent('send', { detail: 'Calculate properties of Caffeine' }))}>
                Calculate properties of Caffeine
             </button>
          </div>
        </div>
      {/if}

      {#each $messages as msg}
        <ChatMessage message={msg} />
      {/each}

      {#if $isLoading}
        <div class="flex justify-start w-full">
          <div class="bg-white border border-gray-200 rounded-lg p-4 flex gap-2 items-center">
            <div class="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style="animation-delay: 0ms"></div>
            <div class="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style="animation-delay: 150ms"></div>
            <div class="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style="animation-delay: 300ms"></div>
          </div>
        </div>
      {/if}
    </div>
  </div>

  <!-- Input Area -->
  <div class="bg-white border-t border-gray-200 p-4">
    <div class="max-w-3xl mx-auto">
      <ChatInput on:send={handleSend} disabled={$isLoading} />
      <p class="text-center text-xs text-gray-400 mt-2">
        AI can make mistakes. Please verify important chemical data.
      </p>
    </div>
  </div>
</div>
