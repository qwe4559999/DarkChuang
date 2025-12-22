<script lang="ts">
  import { onMount, afterUpdate } from 'svelte';
  import ChatMessage from './components/ChatMessage.svelte';
  import ChatInput from './components/ChatInput.svelte';
  import { messages, isLoading } from './stores/chat';
  import { api } from './lib/api';
  import { FlaskConical, MessageSquare, FileText, Upload } from 'lucide-svelte';

  let chatContainer: HTMLElement;
  let activeTab = 'chat'; // 'chat', 'spectrum', 'knowledge'
  let spectrumFile: File | null = null;
  let spectrumType = 'auto';
  let spectrumResult: any = null;
  let isAnalyzing = false;
  let analysisStatus = ''; // 'Uploading...', 'Analyzing with AI...', 'Parsing results...'

  let knowledgeFiles: FileList | null = null;
  let isUploading = false;
  let uploadStatus = '';

  function scrollToBottom() {
    if (chatContainer) {
      chatContainer.scrollTop = chatContainer.scrollHeight;
    }
  }

  afterUpdate(() => {
    if (activeTab === 'chat') scrollToBottom();
  });

  async function handleSend(event: CustomEvent<{ text: string, file: File | null }>) {
    const { text, file } = event.detail;
    if (!text.trim() && !file) return;

    // Add user message
    messages.addMessage({ 
        role: 'user', 
        content: text,
        type: file ? 'image' : 'text',
        data: file ? { imageUrl: URL.createObjectURL(file) } : undefined
    });
    isLoading.set(true);

    try {
      let imagePath = undefined;
      if (file) {
          const uploadResult = await api.uploadImage(file);
          imagePath = uploadResult.file_path;
      }

      // 1. Get Chat Response
      const response = await api.sendMessage(text, imagePath);
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

  async function handleSpectrumUpload() {
      if (!spectrumFile) return;
      isAnalyzing = true;
      analysisStatus = 'Initializing analysis...';
      spectrumResult = null;
      
      try {
          // Simulate progress steps since backend is monolithic
          const progressTimer = setInterval(() => {
             if (analysisStatus === 'Initializing analysis...') analysisStatus = 'Uploading image...';
             else if (analysisStatus === 'Uploading image...') analysisStatus = 'AI Model is analyzing spectrum (this may take 10-20s)...';
          }, 1000);

          const result = await api.uploadSpectrum(spectrumFile, spectrumType);
          clearInterval(progressTimer);
          analysisStatus = 'Analysis complete!';
          spectrumResult = result;
      } catch (e) {
          console.error(e);
          analysisStatus = 'Error occurred';
          alert("Analysis failed: " + e);
      } finally {
          isAnalyzing = false;
          setTimeout(() => { if (!isAnalyzing) analysisStatus = ''; }, 3000);
      }
  }

  async function handleKnowledgeUpload() {
      if (!knowledgeFiles || knowledgeFiles.length === 0) return;
      isUploading = true;
      uploadStatus = 'Uploading...';
      try {
          const files = Array.from(knowledgeFiles);
          const result = await api.uploadDocuments(files);
          uploadStatus = `Success! ${result.message}`;
          setTimeout(() => uploadStatus = '', 5000);
          knowledgeFiles = null;
      } catch (e) {
          console.error(e);
          uploadStatus = 'Upload failed: ' + e;
      } finally {
          isUploading = false;
      }
  }
</script>

<div class="flex h-screen bg-gray-100">
  <!-- Sidebar -->
  <aside class="w-64 bg-white shadow-md flex flex-col z-20">
      <div class="p-6 border-b border-gray-100">
          <div class="flex items-center gap-2 text-blue-600 font-bold text-xl">
              <FlaskConical size={24} />
              <span>DarkChuang</span>
          </div>
          <p class="text-xs text-gray-400 mt-1 ml-8">AI Chemistry Assistant</p>
      </div>

      <nav class="flex-1 p-4 space-y-2">
          <button
              class="w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-colors {activeTab === 'chat' ? 'bg-blue-50 text-blue-600' : 'text-gray-600 hover:bg-gray-50'}"
              on:click={() => activeTab = 'chat'}
          >
              <MessageSquare size={20} />
              <span>Chat Assistant</span>
          </button>

          <button
              class="w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-colors {activeTab === 'knowledge' ? 'bg-blue-50 text-blue-600' : 'text-gray-600 hover:bg-gray-50'}"
              on:click={() => activeTab = 'knowledge'}
          >
              <FileText size={20} />
              <span>Knowledge Base</span>
          </button>
      </nav>
  </aside>

  <!-- Main Content -->
  <main class="flex-1 flex flex-col h-screen overflow-hidden">
    <!-- Header -->
    <header class="bg-white shadow-sm px-6 py-4 flex items-center justify-between z-10">
      <h2 class="text-lg font-semibold text-gray-800">
          {#if activeTab === 'chat'}Chat Assistant{/if}
          {#if activeTab === 'spectrum'}Spectrum Analysis{/if}
          {#if activeTab === 'knowledge'}Knowledge Base Management{/if}
      </h2>
    </header>

    <!-- Content Area -->
    <div class="flex-1 overflow-hidden relative">

        <!-- Chat Tab -->
        {#if activeTab === 'chat'}
            <div class="flex flex-col h-full">
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
        {/if}

        <!-- Spectrum Tab -->
        <!-- Knowledge Tab -->
        {#if activeTab === 'knowledge'}
            <div class="h-full overflow-y-auto p-8">
                <div class="max-w-4xl mx-auto bg-white rounded-xl shadow-sm p-8">
                    <div class="mb-8">
                        <h3 class="text-2xl font-bold text-gray-800">Knowledge Base Management</h3>
                        <p class="text-gray-500 mt-2">Upload scientific papers, textbooks, or notes (PDF, TXT, MD) to enhance the AI's knowledge.</p>
                    </div>

                    <div class="bg-blue-50 border border-blue-100 rounded-lg p-6 mb-8">
                        <h4 class="font-bold text-blue-800 mb-2">Upload New Documents</h4>
                        <div class="flex gap-4 items-center">
                            <input
                                type="file"
                                multiple
                                accept=".pdf,.txt,.md"
                                class="flex-1 block w-full text-sm text-slate-500
                                file:mr-4 file:py-2 file:px-4
                                file:rounded-full file:border-0
                                file:text-sm file:font-semibold
                                file:bg-white file:text-blue-700
                                hover:file:bg-blue-50"
                                on:change={(e) => knowledgeFiles = e.target.files}
                            />
                            <button
                                class="px-6 py-2 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition disabled:opacity-50"
                                disabled={!knowledgeFiles || isUploading}
                                on:click={handleKnowledgeUpload}
                            >
                                {isUploading ? 'Uploading...' : 'Upload & Index'}
                            </button>
                        </div>
                        {#if uploadStatus}
                            <p class="mt-2 text-sm text-blue-600 font-medium">{uploadStatus}</p>
                        {/if}
                    </div>

                    <div>
                        <h4 class="font-bold text-gray-800 mb-4">System Status</h4>
                        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                            <div class="p-4 bg-gray-50 rounded-lg">
                                <span class="block text-sm text-gray-500">RAG Status</span>
                                <span class="text-lg font-bold text-green-600">Active</span>
                            </div>
                            <div class="p-4 bg-gray-50 rounded-lg">
                                <span class="block text-sm text-gray-500">Vector DB</span>
                                <span class="text-lg font-bold text-gray-800">ChromaDB</span>
                            </div>
                            <div class="p-4 bg-gray-50 rounded-lg">
                                <span class="block text-sm text-gray-500">Embedding Model</span>
                                <span class="text-lg font-bold text-gray-800">BGE-Large-ZH</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        {/if}
    </div>
  </main>
</div>
