<script>
	import { onMount } from 'svelte';
	import axios from 'axios';

	let messages = [];
	let currentMessage = '';
	let loading = false;
	let error = null;
	let chatContainer;
	let useRAG = false;

	const API_BASE = 'http://localhost:8000';

	// 预设问题
	const presetQuestions = [
		'什么是苯环？',
		'请解释酸碱反应的机理',
		'有机化学中的取代反应有哪些类型？',
		'如何区分醛和酮？',
		'什么是共价键？',
		'解释化学平衡的概念'
	];

	onMount(() => {
		// 添加欢迎消息
		messages = [
			{
				id: Date.now(),
				type: 'assistant',
				content: '您好！我是DarkChuang化学知识助手。我可以回答各种化学相关的问题，包括有机化学、无机化学、物理化学等。请随时向我提问！',
				timestamp: new Date()
			}
		];
	});

	async function sendMessage() {
		if (!currentMessage.trim() || loading) return;

		const userMessage = {
			id: Date.now(),
			type: 'user',
			content: currentMessage.trim(),
			timestamp: new Date()
		};

		messages = [...messages, userMessage];
		const messageToSend = currentMessage.trim();
		currentMessage = '';
		loading = true;
		error = null;

		try {
				const response = await axios.post(`${API_BASE}/api/v1/chat`, {
					message: messageToSend,
					use_rag: useRAG,
					max_tokens: 500
				}, {
					headers: {
						'Content-Type': 'application/json'
					},
					timeout: 600000 // 10分钟超时
				});

			const assistantMessage = {
				id: Date.now() + 1,
				type: 'assistant',
				content: response.data.message,
				timestamp: new Date(),
				processing_time: response.data.processing_time,
				sources: response.data.sources
			};

			messages = [...messages, assistantMessage];
		} catch (err) {
			error = err.response?.data?.detail || '发送消息失败，请重试';
			const errorMessage = {
				id: Date.now() + 1,
				type: 'error',
				content: `抱歉，我遇到了一些问题：${error}`,
				timestamp: new Date()
			};
			messages = [...messages, errorMessage];
		} finally {
			loading = false;
			// 滚动到底部
			setTimeout(() => {
				if (chatContainer) {
					chatContainer.scrollTop = chatContainer.scrollHeight;
				}
			}, 100);
		}
	}

	function selectPresetQuestion(question) {
		currentMessage = question;
		sendMessage();
	}

	function handleKeyPress(event) {
		if (event.key === 'Enter' && !event.shiftKey) {
			event.preventDefault();
			sendMessage();
		}
	}

	function clearChat() {
		messages = [
			{
				id: Date.now(),
				type: 'assistant',
				content: '对话已清空。请继续向我提问！',
				timestamp: new Date()
			}
		];
	}
</script>

<svelte:head>
	<title>化学知识问答 - DarkChuang</title>
	<meta name="description" content="AI驱动的化学知识问答系统" />
</svelte:head>

<div class="chat-container">
	<div class="chat-header">
		<h1>🧪 化学知识问答</h1>
		<p>基于AI的智能化学知识助手</p>
		<div class="chat-controls">
			<label class="rag-toggle">
				<input type="checkbox" bind:checked={useRAG} />
				<span>启用知识库检索</span>
			</label>
			<button class="clear-btn" on:click={clearChat}>清空对话</button>
		</div>
	</div>

	<!-- 预设问题 -->
	{#if messages.length <= 1}
		<div class="preset-questions">
			<h3>💡 常见问题</h3>
			<div class="questions-grid">
				{#each presetQuestions as question}
					<button 
						class="preset-question" 
						on:click={() => selectPresetQuestion(question)}
						disabled={loading}
					>
						{question}
					</button>
				{/each}
			</div>
		</div>
	{/if}

	<!-- 聊天消息区域 -->
	<div class="chat-messages" bind:this={chatContainer}>
		{#each messages as message (message.id)}
			<div class="message {message.type}">
				<div class="message-content">
					<div class="message-text">{message.content}</div>
					{#if message.processing_time}
						<div class="message-meta">
							处理时间: {message.processing_time.toFixed(2)}秒
						</div>
					{/if}
					{#if message.sources && message.sources.length > 0}
						<div class="message-sources">
							<strong>参考来源:</strong>
							{#each message.sources as source}
								<span class="source">{source}</span>
							{/each}
						</div>
					{/if}
				</div>
				<div class="message-time">
					{message.timestamp.toLocaleTimeString()}
				</div>
			</div>
		{/each}

		{#if loading}
			<div class="message assistant loading">
				<div class="message-content">
					<div class="typing-indicator">
						<span></span>
						<span></span>
						<span></span>
					</div>
				</div>
			</div>
		{/if}
	</div>

	<!-- 输入区域 -->
	<div class="chat-input">
		<div class="input-container">
			<textarea
				bind:value={currentMessage}
				on:keypress={handleKeyPress}
				placeholder="请输入您的化学问题..."
				disabled={loading}
				rows="1"
			></textarea>
			<button 
				class="send-btn" 
				on:click={sendMessage} 
				disabled={loading || !currentMessage.trim()}
			>
				{#if loading}
					<span class="loading-spinner"></span>
				{:else}
					发送
				{/if}
			</button>
		</div>
	</div>
</div>

<style>
	.chat-container {
		max-width: 800px;
		margin: 0 auto;
		height: calc(100vh - 200px);
		display: flex;
		flex-direction: column;
		background: white;
		border-radius: 12px;
		box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
		overflow: hidden;
	}

	.chat-header {
		padding: 1.5rem;
		background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
		color: white;
		text-align: center;
	}

	.chat-header h1 {
		margin: 0 0 0.5rem 0;
		font-size: 1.8rem;
	}

	.chat-header p {
		margin: 0 0 1rem 0;
		opacity: 0.9;
	}

	.chat-controls {
		display: flex;
		justify-content: space-between;
		align-items: center;
		gap: 1rem;
	}

	.rag-toggle {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		font-size: 0.9rem;
	}

	.clear-btn {
		padding: 0.5rem 1rem;
		background: rgba(255, 255, 255, 0.2);
		color: white;
		border: 1px solid rgba(255, 255, 255, 0.3);
		border-radius: 6px;
		cursor: pointer;
		transition: all 0.2s;
	}

	.clear-btn:hover {
		background: rgba(255, 255, 255, 0.3);
	}

	.preset-questions {
		padding: 1.5rem;
		border-bottom: 1px solid #eee;
	}

	.preset-questions h3 {
		margin: 0 0 1rem 0;
		color: #333;
	}

	.questions-grid {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
		gap: 0.75rem;
	}

	.preset-question {
		padding: 0.75rem 1rem;
		background: #f8f9fa;
		border: 1px solid #e9ecef;
		border-radius: 8px;
		cursor: pointer;
		transition: all 0.2s;
		text-align: left;
		font-size: 0.9rem;
	}

	.preset-question:hover {
		background: #e9ecef;
		transform: translateY(-1px);
	}

	.preset-question:disabled {
		opacity: 0.6;
		cursor: not-allowed;
	}

	.chat-messages {
		flex: 1;
		overflow-y: auto;
		padding: 1rem;
		display: flex;
		flex-direction: column;
		gap: 1rem;
	}

	.message {
		display: flex;
		flex-direction: column;
		max-width: 80%;
	}

	.message.user {
		align-self: flex-end;
	}

	.message.assistant,
	.message.error {
		align-self: flex-start;
	}

	.message-content {
		padding: 1rem;
		border-radius: 12px;
		line-height: 1.5;
	}

	.message.user .message-content {
		background: #667eea;
		color: white;
	}

	.message.assistant .message-content {
		background: #f8f9fa;
		color: #333;
		border: 1px solid #e9ecef;
	}

	.message.error .message-content {
		background: #f8d7da;
		color: #721c24;
		border: 1px solid #f5c6cb;
	}

	.message-text {
		white-space: pre-wrap;
		word-wrap: break-word;
	}

	.message-meta {
		margin-top: 0.5rem;
		font-size: 0.8rem;
		opacity: 0.7;
	}

	.message-sources {
		margin-top: 0.5rem;
		font-size: 0.8rem;
	}

	.source {
		display: inline-block;
		margin: 0.2rem 0.5rem 0.2rem 0;
		padding: 0.2rem 0.5rem;
		background: #e9ecef;
		border-radius: 4px;
	}

	.message-time {
		font-size: 0.7rem;
		color: #666;
		margin-top: 0.25rem;
		align-self: flex-end;
	}

	.message.user .message-time {
		align-self: flex-end;
	}

	.message.assistant .message-time,
	.message.error .message-time {
		align-self: flex-start;
	}

	.typing-indicator {
		display: flex;
		gap: 0.3rem;
		align-items: center;
	}

	.typing-indicator span {
		width: 8px;
		height: 8px;
		background: #666;
		border-radius: 50%;
		animation: typing 1.4s infinite ease-in-out;
	}

	.typing-indicator span:nth-child(1) {
		animation-delay: -0.32s;
	}

	.typing-indicator span:nth-child(2) {
		animation-delay: -0.16s;
	}

	@keyframes typing {
		0%, 80%, 100% {
			transform: scale(0);
		}
		40% {
			transform: scale(1);
		}
	}

	.chat-input {
		padding: 1rem;
		border-top: 1px solid #eee;
		background: white;
	}

	.input-container {
		display: flex;
		gap: 0.75rem;
		align-items: flex-end;
	}

	.input-container textarea {
		flex: 1;
		padding: 0.75rem;
		border: 1px solid #ddd;
		border-radius: 8px;
		resize: none;
		font-family: inherit;
		font-size: 1rem;
		min-height: 44px;
		max-height: 120px;
	}

	.input-container textarea:focus {
		outline: none;
		border-color: #667eea;
		box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.2);
	}

	.send-btn {
		padding: 0.75rem 1.5rem;
		background: #667eea;
		color: white;
		border: none;
		border-radius: 8px;
		cursor: pointer;
		transition: all 0.2s;
		font-weight: 500;
		min-width: 80px;
		height: 44px;
		display: flex;
		align-items: center;
		justify-content: center;
	}

	.send-btn:hover:not(:disabled) {
		background: #5a6fd8;
		transform: translateY(-1px);
	}

	.send-btn:disabled {
		opacity: 0.6;
		cursor: not-allowed;
		transform: none;
	}

	.loading-spinner {
		width: 16px;
		height: 16px;
		border: 2px solid rgba(255, 255, 255, 0.3);
		border-radius: 50%;
		border-top-color: white;
		animation: spin 1s ease-in-out infinite;
	}

	@keyframes spin {
		to {
			transform: rotate(360deg);
		}
	}

	@media (max-width: 768px) {
		.chat-container {
			height: calc(100vh - 120px);
			margin: 0;
			border-radius: 0;
		}

		.questions-grid {
			grid-template-columns: 1fr;
		}

		.message {
			max-width: 90%;
		}

		.chat-controls {
			flex-direction: column;
			gap: 0.5rem;
		}
	}
</style>