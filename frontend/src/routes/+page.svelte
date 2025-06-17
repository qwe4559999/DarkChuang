<script>
	import Welcome from '$lib/components/Welcome.svelte';
</script>

<svelte:head>
	<title>DarkChuang - 化学光谱分析平台</title>
	<meta name="description" content="基于AI的化学光谱分析和识别平台" />
</svelte:head>

<section>
	<Welcome />
	<div class="welcome">
		<div class="welcome-content">
			<h1>欢迎使用 DarkChuang</h1>
			<p>这是一个基于AI的化学光谱分析和识别平台</p>
			<div class="features">
				<div class="feature">
					<h3>🧪 化学问答</h3>
					<p>基于AI的智能化学知识问答系统，解答各种化学问题</p>
					<a href="/chat" class="feature-link">立即体验</a>
				</div>
				<div class="feature">
					<h3>🔬 谱图识别</h3>
					<p>上传化学谱图，AI自动识别和分析谱图特征</p>
					<a href="/spectrum" class="feature-link">开始分析</a>
				</div>
				<div class="feature">
					<h3>📊 数据处理</h3>
					<p>强大的数据处理和可视化功能，支持多种文件格式</p>
					<a href="/upload" class="feature-link">上传数据</a>
				</div>
			</div>
			<div class="actions">
				<a href="/upload" class="btn btn-primary">开始分析</a>
				<a href="/about" class="btn btn-secondary">了解更多</a>
			</div>
		</div>
	</div>
</section>

<style>
	section {
		display: flex;
		flex-direction: column;
		justify-content: center;
		align-items: center;
		flex: 0.6;
	}

	.welcome {
		max-width: 800px;
		margin: 2rem auto;
		padding: 2rem;
		text-align: center;
	}

	.welcome-content h1 {
		color: var(--color-theme-1);
		margin-bottom: 1rem;
	}

	.features {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
		gap: 2rem;
		margin: 3rem 0;
	}

	.feature {
		padding: 1.5rem;
		background: rgba(255, 255, 255, 0.8);
		border-radius: 8px;
		box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
	}

	.feature h3 {
		margin-bottom: 1rem;
		color: var(--color-theme-2);
	}

	.feature-link {
		display: inline-block;
		margin-top: 1rem;
		padding: 0.5rem 1rem;
		background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
		color: white;
		text-decoration: none;
		border-radius: 6px;
		font-size: 0.9rem;
		font-weight: 500;
		transition: all 0.2s;
	}

	.feature-link:hover {
		transform: translateY(-2px);
		box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
	}

	.actions {
		display: flex;
		gap: 1rem;
		justify-content: center;
		margin-top: 2rem;
	}

	.btn {
		padding: 0.75rem 1.5rem;
		border-radius: 6px;
		text-decoration: none;
		font-weight: 500;
		transition: all 0.2s;
	}

	.btn-primary {
		background: var(--color-theme-1);
		color: white;
	}

	.btn-primary:hover {
		background: #e63900;
		transform: translateY(-2px);
	}

	.btn-secondary {
		background: var(--color-theme-2);
		color: white;
	}

	.btn-secondary:hover {
		background: #2d5a87;
		transform: translateY(-2px);
	}

	@media (max-width: 768px) {
		.actions {
			flex-direction: column;
			align-items: center;
		}
	}
</style>