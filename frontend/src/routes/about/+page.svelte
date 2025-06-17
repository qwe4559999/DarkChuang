<svelte:head>
	<title>关于我们 - DarkChuang</title>
	<meta name="description" content="了解 DarkChuang 化学光谱分析平台" />
</svelte:head>

<div class="text-column">
	<h1>关于 DarkChuang</h1>

	<p>
		DarkChuang 是一个基于人工智能的化学光谱分析和识别平台。我们致力于为化学研究人员、
		实验室技术人员和学生提供先进的光谱分析工具。
	</p>

	<h2>我们的使命</h2>
	<p>
		通过先进的机器学习技术，让化学光谱分析变得更加准确、高效和易于使用。
		我们相信技术可以加速科学发现，推动化学研究的进步。
	</p>

	<h2>核心功能</h2>
	<ul>
		<li><strong>光谱上传与分析</strong> - 支持多种光谱格式的上传和自动分析</li>
		<li><strong>AI化合物识别</strong> - 基于深度学习的化合物结构识别</li>
		<li><strong>数据可视化</strong> - 直观的图表和报告生成</li>
		<li><strong>历史记录管理</strong> - 完整的分析历史和数据管理</li>
	</ul>

	<h2>技术栈</h2>
	<div class="tech-stack">
		<div class="tech-category">
			<h3>前端</h3>
			<ul>
				<li>Svelte & SvelteKit</li>
				<li>TypeScript</li>
				<li>Vite</li>
			</ul>
		</div>
		<div class="tech-category">
			<h3>后端</h3>
			<ul>
				<li>Python FastAPI</li>
				<li>机器学习模型</li>
				<li>向量数据库</li>
			</ul>
		</div>
	</div>

	<div class="actions">
		<a href="/" class="btn">返回首页</a>
		<a href="/upload" class="btn btn-primary">开始使用</a>
	</div>
</div>

<style>
	.tech-stack {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
		gap: 2rem;
		margin: 2rem 0;
	}

	.tech-category {
		padding: 1.5rem;
		background: rgba(255, 255, 255, 0.8);
		border-radius: 8px;
		box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
	}

	.tech-category h3 {
		color: var(--color-theme-2);
		margin-bottom: 1rem;
	}

	.tech-category ul {
		list-style: none;
		padding: 0;
	}

	.tech-category li {
		padding: 0.25rem 0;
		color: var(--color-text);
	}

	.actions {
		display: flex;
		gap: 1rem;
		justify-content: center;
		margin-top: 3rem;
	}

	.btn {
		padding: 0.75rem 1.5rem;
		border-radius: 6px;
		text-decoration: none;
		font-weight: 500;
		transition: all 0.2s;
		background: var(--color-theme-2);
		color: white;
	}

	.btn:hover {
		background: #2d5a87;
		transform: translateY(-2px);
	}

	.btn-primary {
		background: var(--color-theme-1);
	}

	.btn-primary:hover {
		background: #e63900;
	}

	@media (max-width: 768px) {
		.actions {
			flex-direction: column;
			align-items: center;
		}
	}
</style>