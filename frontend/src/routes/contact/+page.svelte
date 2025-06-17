<script>
	import { onMount } from 'svelte';

	let formData = {
		name: '',
		email: '',
		subject: '',
		message: '',
		type: 'general'
	};

	let isSubmitting = false;
	let submitStatus = null;

	async function handleSubmit() {
		if (isSubmitting) return;
		
		isSubmitting = true;
		submitStatus = null;

		// 模拟提交过程
		try {
			// 这里可以添加实际的提交逻辑
			await new Promise(resolve => setTimeout(resolve, 1000));
			
			submitStatus = 'success';
			// 重置表单
			formData = {
				name: '',
				email: '',
				subject: '',
				message: '',
				type: 'general'
			};
		} catch (error) {
			submitStatus = 'error';
		} finally {
			isSubmitting = false;
		}
	}

	function copyToClipboard(text) {
		navigator.clipboard.writeText(text).then(() => {
			alert('已复制到剪贴板');
		});
	}
</script>

<svelte:head>
	<title>联系我们 - DarkChuang</title>
	<meta name="description" content="联系 DarkChuang 团队，获取技术支持和合作咨询" />
</svelte:head>

<div class="contact-container">
	<div class="contact-header">
		<h1>📞 联系我们</h1>
		<p>我们很乐意听到您的声音！无论是技术支持、功能建议还是合作咨询，请随时与我们联系。</p>
	</div>

	<div class="contact-content">
		<div class="contact-info">
			<div class="info-section">
				<h2>🏢 团队信息</h2>
				<div class="info-card">
					<h3>DarkChuang 开发团队</h3>
					<p>专注于化学光谱分析和AI技术的创新团队</p>
					<ul>
						<li><strong>成立时间:</strong> 2024年</li>
						<li><strong>专业领域:</strong> 化学分析、机器学习、Web开发</li>
						<li><strong>服务范围:</strong> 全球</li>
					</ul>
				</div>
			</div>

			<div class="info-section">
				<h2>📧 联系方式</h2>
				<div class="contact-methods">
					<div class="contact-method">
						<div class="method-icon">📧</div>
						<div class="method-info">
							<h4>邮箱</h4>
							<p>support@darkchuang.com</p>
							<button class="copy-btn" on:click={() => copyToClipboard('support@darkchuang.com')}>复制</button>
						</div>
					</div>

					<div class="contact-method">
						<div class="method-icon">💬</div>
						<div class="method-info">
							<h4>在线客服</h4>
							<p>工作日 9:00-18:00</p>
							<button class="contact-btn">开始对话</button>
						</div>
					</div>

					<div class="contact-method">
						<div class="method-icon">🐙</div>
						<div class="method-info">
							<h4>GitHub</h4>
							<p>github.com/darkchuang</p>
							<button class="contact-btn" on:click={() => window.open('https://github.com/darkchuang', '_blank')}>访问</button>
						</div>
					</div>

					<div class="contact-method">
						<div class="method-icon">🌐</div>
						<div class="method-info">
							<h4>官方网站</h4>
							<p>www.darkchuang.com</p>
							<button class="contact-btn" on:click={() => window.open('https://www.darkchuang.com', '_blank')}>访问</button>
						</div>
					</div>
				</div>
			</div>

			<div class="info-section">
				<h2>⏰ 响应时间</h2>
				<div class="response-times">
					<div class="response-item">
						<h4>🚨 紧急问题</h4>
						<p>2小时内响应</p>
						<small>系统故障、安全问题</small>
					</div>
					<div class="response-item">
						<h4>🔧 技术支持</h4>
						<p>24小时内响应</p>
						<small>使用问题、功能咨询</small>
					</div>
					<div class="response-item">
						<h4>💡 功能建议</h4>
						<p>3-5个工作日</p>
						<small>新功能、改进建议</small>
					</div>
					<div class="response-item">
						<h4>🤝 商务合作</h4>
						<p>1-2个工作日</p>
						<small>合作洽谈、定制开发</small>
					</div>
				</div>
			</div>
		</div>

		<div class="contact-form-section">
			<h2>📝 发送消息</h2>
			<form on:submit|preventDefault={handleSubmit} class="contact-form">
				<div class="form-group">
					<label for="type">消息类型</label>
					<select id="type" bind:value={formData.type} required>
						<option value="general">一般咨询</option>
						<option value="technical">技术支持</option>
						<option value="feature">功能建议</option>
						<option value="bug">问题报告</option>
						<option value="business">商务合作</option>
					</select>
				</div>

				<div class="form-row">
					<div class="form-group">
						<label for="name">姓名 *</label>
						<input 
							id="name" 
							type="text" 
							bind:value={formData.name} 
							required 
							placeholder="请输入您的姓名"
						/>
					</div>

					<div class="form-group">
						<label for="email">邮箱 *</label>
						<input 
							id="email" 
							type="email" 
							bind:value={formData.email} 
							required 
							placeholder="请输入您的邮箱"
						/>
					</div>
				</div>

				<div class="form-group">
					<label for="subject">主题 *</label>
					<input 
						id="subject" 
						type="text" 
						bind:value={formData.subject} 
						required 
						placeholder="请简要描述您的问题或需求"
					/>
				</div>

				<div class="form-group">
					<label for="message">详细描述 *</label>
					<textarea 
						id="message" 
						bind:value={formData.message} 
						required 
						rows="6"
						placeholder="请详细描述您的问题、建议或需求..."
					></textarea>
				</div>

				{#if submitStatus === 'success'}
					<div class="status-message success">
						✅ 消息发送成功！我们会尽快回复您。
					</div>
				{:else if submitStatus === 'error'}
					<div class="status-message error">
						❌ 发送失败，请稍后重试或直接发送邮件至 support@darkchuang.com
					</div>
				{/if}

				<button type="submit" class="submit-btn" disabled={isSubmitting}>
					{#if isSubmitting}
						<span class="loading">发送中...</span>
					{:else}
						发送消息
					{/if}
				</button>
			</form>
		</div>
	</div>

	<div class="faq-section">
		<h2>❓ 常见问题</h2>
		<div class="faq-grid">
			<div class="faq-item">
				<h4>如何上传谱图文件？</h4>
				<p>支持 JPG、PNG、PDF 格式，文件大小不超过 10MB。建议使用高清晰度的图像以获得更好的分析结果。</p>
			</div>
			<div class="faq-item">
				<h4>分析结果的准确性如何？</h4>
				<p>我们的AI模型经过大量化学数据训练，准确率超过90%。但建议将结果作为参考，重要决策请结合专业知识。</p>
			</div>
			<div class="faq-item">
				<h4>是否支持批量处理？</h4>
				<p>目前支持单个文件处理。批量处理功能正在开发中，敬请期待。</p>
			</div>
			<div class="faq-item">
				<h4>数据安全如何保障？</h4>
				<p>所有上传的文件都经过加密处理，分析完成后会自动删除。我们严格遵守数据保护法规。</p>
			</div>
		</div>
	</div>
</div>

<style>
	.contact-container {
		max-width: 1200px;
		margin: 0 auto;
		padding: 2rem;
	}

	.contact-header {
		text-align: center;
		margin-bottom: 3rem;
	}

	.contact-header h1 {
		margin: 0 0 1rem 0;
		color: var(--color-theme-1);
		font-size: 2.5rem;
	}

	.contact-header p {
		font-size: 1.1rem;
		color: var(--color-text);
		max-width: 600px;
		margin: 0 auto;
		line-height: 1.6;
	}

	.contact-content {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 3rem;
		margin-bottom: 3rem;
	}

	.contact-info {
		display: flex;
		flex-direction: column;
		gap: 2rem;
	}

	.info-section h2 {
		margin: 0 0 1.5rem 0;
		color: var(--color-theme-2);
		font-size: 1.5rem;
	}

	.info-card {
		padding: 1.5rem;
		background: var(--color-bg-0);
		border-radius: 8px;
		border: 1px solid var(--color-bg-1);
	}

	.info-card h3 {
		margin: 0 0 1rem 0;
		color: var(--color-theme-1);
	}

	.info-card ul {
		list-style: none;
		padding: 0;
		margin: 1rem 0 0 0;
	}

	.info-card li {
		margin-bottom: 0.5rem;
		color: var(--color-text);
	}

	.contact-methods {
		display: flex;
		flex-direction: column;
		gap: 1rem;
	}

	.contact-method {
		display: flex;
		align-items: center;
		gap: 1rem;
		padding: 1rem;
		background: var(--color-bg-0);
		border-radius: 8px;
		border: 1px solid var(--color-bg-1);
	}

	.method-icon {
		font-size: 2rem;
		flex-shrink: 0;
	}

	.method-info {
		flex: 1;
	}

	.method-info h4 {
		margin: 0 0 0.5rem 0;
		color: var(--color-theme-2);
	}

	.method-info p {
		margin: 0;
		color: var(--color-text);
	}

	.copy-btn, .contact-btn {
		padding: 0.5rem 1rem;
		background: var(--color-theme-1);
		color: white;
		border: none;
		border-radius: 4px;
		cursor: pointer;
		font-size: 0.9rem;
		margin-top: 0.5rem;
		transition: background 0.2s;
	}

	.copy-btn:hover, .contact-btn:hover {
		background: var(--color-theme-2);
	}

	.response-times {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 1rem;
	}

	.response-item {
		padding: 1rem;
		background: var(--color-bg-0);
		border-radius: 8px;
		border: 1px solid var(--color-bg-1);
		text-align: center;
	}

	.response-item h4 {
		margin: 0 0 0.5rem 0;
		color: var(--color-theme-2);
		font-size: 1rem;
	}

	.response-item p {
		margin: 0 0 0.5rem 0;
		font-weight: bold;
		color: var(--color-theme-1);
	}

	.response-item small {
		color: var(--color-text);
		font-size: 0.8rem;
	}

	.contact-form-section h2 {
		margin: 0 0 1.5rem 0;
		color: var(--color-theme-2);
		font-size: 1.5rem;
	}

	.contact-form {
		display: flex;
		flex-direction: column;
		gap: 1.5rem;
	}

	.form-row {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 1rem;
	}

	.form-group {
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
	}

	.form-group label {
		font-weight: bold;
		color: var(--color-theme-2);
	}

	.form-group input,
	.form-group select,
	.form-group textarea {
		padding: 0.75rem;
		border: 1px solid var(--color-bg-1);
		border-radius: 6px;
		background: var(--color-bg-0);
		color: var(--color-text);
		font-size: 1rem;
		transition: border-color 0.2s;
	}

	.form-group input:focus,
	.form-group select:focus,
	.form-group textarea:focus {
		outline: none;
		border-color: var(--color-theme-1);
	}

	.form-group textarea {
		resize: vertical;
		min-height: 120px;
		font-family: inherit;
	}

	.status-message {
		padding: 1rem;
		border-radius: 6px;
		text-align: center;
		font-weight: bold;
	}

	.status-message.success {
		background: rgba(76, 175, 80, 0.1);
		color: #4CAF50;
		border: 1px solid rgba(76, 175, 80, 0.3);
	}

	.status-message.error {
		background: rgba(244, 67, 54, 0.1);
		color: #f44336;
		border: 1px solid rgba(244, 67, 54, 0.3);
	}

	.submit-btn {
		padding: 1rem 2rem;
		background: var(--color-theme-1);
		color: white;
		border: none;
		border-radius: 6px;
		font-size: 1.1rem;
		font-weight: bold;
		cursor: pointer;
		transition: background 0.2s;
		align-self: flex-start;
	}

	.submit-btn:hover:not(:disabled) {
		background: var(--color-theme-2);
	}

	.submit-btn:disabled {
		opacity: 0.6;
		cursor: not-allowed;
	}

	.loading {
		display: flex;
		align-items: center;
		gap: 0.5rem;
	}

	.loading::after {
		content: '';
		width: 16px;
		height: 16px;
		border: 2px solid transparent;
		border-top: 2px solid currentColor;
		border-radius: 50%;
		animation: spin 1s linear infinite;
	}

	@keyframes spin {
		to {
			transform: rotate(360deg);
		}
	}

	.faq-section {
		margin-top: 3rem;
		padding-top: 3rem;
		border-top: 1px solid var(--color-bg-1);
	}

	.faq-section h2 {
		margin: 0 0 2rem 0;
		color: var(--color-theme-2);
		font-size: 1.5rem;
		text-align: center;
	}

	.faq-grid {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
		gap: 1.5rem;
	}

	.faq-item {
		padding: 1.5rem;
		background: var(--color-bg-0);
		border-radius: 8px;
		border: 1px solid var(--color-bg-1);
	}

	.faq-item h4 {
		margin: 0 0 1rem 0;
		color: var(--color-theme-1);
		font-size: 1.1rem;
	}

	.faq-item p {
		margin: 0;
		color: var(--color-text);
		line-height: 1.6;
	}

	@media (max-width: 768px) {
		.contact-container {
			padding: 1rem;
		}

		.contact-header h1 {
			font-size: 2rem;
		}

		.contact-content {
			grid-template-columns: 1fr;
			gap: 2rem;
		}

		.form-row {
			grid-template-columns: 1fr;
		}

		.response-times {
			grid-template-columns: 1fr;
		}

		.faq-grid {
			grid-template-columns: 1fr;
		}
	}
</style>