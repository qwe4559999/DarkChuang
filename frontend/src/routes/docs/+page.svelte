<script>
	import { onMount } from 'svelte';

	let activeSection = 'getting-started';

	function scrollToSection(sectionId) {
		activeSection = sectionId;
		document.getElementById(sectionId)?.scrollIntoView({ behavior: 'smooth' });
	}
</script>

<svelte:head>
	<title>使用文档 - DarkChuang</title>
	<meta name="description" content="DarkChuang 化学光谱分析平台使用文档" />
</svelte:head>

<div class="docs-container">
	<aside class="sidebar">
		<nav class="docs-nav">
			<h3>目录</h3>
			<ul>
				<li>
					<button 
						class:active={activeSection === 'getting-started'}
						on:click={() => scrollToSection('getting-started')}
					>
						快速开始
					</button>
				</li>
				<li>
					<button 
						class:active={activeSection === 'spectrum-analysis'}
						on:click={() => scrollToSection('spectrum-analysis')}
					>
						谱图识别
					</button>
				</li>
				<li>
					<button 
						class:active={activeSection === 'chat-feature'}
						on:click={() => scrollToSection('chat-feature')}
					>
						化学问答
					</button>
				</li>
				<li>
					<button 
						class:active={activeSection === 'image-analysis'}
						on:click={() => scrollToSection('image-analysis')}
					>
						图像分析
					</button>
				</li>
				<li>
					<button 
						class:active={activeSection === 'troubleshooting'}
						on:click={() => scrollToSection('troubleshooting')}
					>
						常见问题
					</button>
				</li>
			</ul>
		</nav>
	</aside>

	<main class="docs-content">
		<header class="docs-header">
			<h1>📚 使用文档</h1>
			<p>欢迎使用 DarkChuang 化学光谱分析平台！本文档将帮助您快速上手并充分利用平台的各项功能。</p>
		</header>

		<section id="getting-started" class="docs-section">
			<h2>🚀 快速开始</h2>
			<div class="content-block">
				<h3>平台简介</h3>
				<p>DarkChuang 是一个基于人工智能的化学光谱分析平台，提供以下核心功能：</p>
				<ul>
					<li><strong>谱图识别</strong>：上传光谱图像，AI 自动识别化合物结构</li>
					<li><strong>化学问答</strong>：智能化学知识问答系统</li>
					<li><strong>图像分析</strong>：化学相关图像的智能分析</li>
				</ul>
			</div>

			<div class="content-block">
				<h3>系统要求</h3>
				<ul>
					<li>现代浏览器（Chrome、Firefox、Safari、Edge）</li>
					<li>稳定的网络连接</li>
					<li>支持 JavaScript</li>
				</ul>
			</div>
		</section>

		<section id="spectrum-analysis" class="docs-section">
			<h2>🔬 谱图识别</h2>
			<div class="content-block">
				<h3>支持的谱图类型</h3>
				<ul>
					<li>红外光谱 (IR)</li>
					<li>核磁共振谱 (NMR)</li>
					<li>质谱 (MS)</li>
					<li>紫外可见光谱 (UV-Vis)</li>
				</ul>
			</div>

			<div class="content-block">
				<h3>使用步骤</h3>
				<ol>
					<li>点击导航栏中的「谱图识别」</li>
					<li>选择谱图类型</li>
					<li>上传谱图图像文件（支持 JPG、PNG、PDF 格式）</li>
					<li>等待 AI 分析处理</li>
					<li>查看识别结果和化合物信息</li>
				</ol>
			</div>

			<div class="content-block">
				<h3>最佳实践</h3>
				<ul>
					<li>确保谱图图像清晰，分辨率不低于 300 DPI</li>
					<li>避免图像模糊或过度压缩</li>
					<li>确保坐标轴和峰值标注清晰可见</li>
				</ul>
			</div>
		</section>

		<section id="chat-feature" class="docs-section">
			<h2>💬 化学问答</h2>
			<div class="content-block">
				<h3>功能特点</h3>
				<ul>
					<li>基于大语言模型的智能问答</li>
					<li>支持化学知识查询</li>
					<li>实时对话交互</li>
					<li>上下文理解能力</li>
				</ul>
			</div>

			<div class="content-block">
				<h3>使用方法</h3>
				<ol>
					<li>点击导航栏中的「化学问答」</li>
					<li>在输入框中输入您的问题</li>
					<li>点击发送或按 Enter 键</li>
					<li>查看 AI 的回答</li>
					<li>可以继续追问或开始新话题</li>
				</ol>
			</div>

			<div class="content-block">
				<h3>问题示例</h3>
				<ul>
					<li>"苯的分子式是什么？"</li>
					<li>"如何区分醇和酚？"</li>
					<li>"解释一下 SN1 和 SN2 反应的区别"</li>
					<li>"什么是芳香性？"</li>
				</ul>
			</div>
		</section>

		<section id="image-analysis" class="docs-section">
			<h2>🖼️ 图像分析</h2>
			<div class="content-block">
				<h3>支持的图像类型</h3>
				<ul>
					<li>化学结构式</li>
					<li>实验装置图</li>
					<li>化学反应式</li>
					<li>分子模型图</li>
				</ul>
			</div>

			<div class="content-block">
				<h3>分析功能</h3>
				<ul>
					<li>结构式识别和命名</li>
					<li>分子式推导</li>
					<li>化学性质预测</li>
					<li>相似化合物推荐</li>
				</ul>
			</div>
		</section>

		<section id="troubleshooting" class="docs-section">
			<h2>❓ 常见问题</h2>
			<div class="content-block">
				<h3>上传问题</h3>
				<div class="faq-item">
					<h4>Q: 为什么我的图片上传失败？</h4>
					<p>A: 请检查以下几点：</p>
					<ul>
						<li>文件格式是否支持（JPG、PNG、PDF）</li>
						<li>文件大小是否超过 10MB</li>
						<li>网络连接是否稳定</li>
					</ul>
				</div>

				<div class="faq-item">
					<h4>Q: 识别结果不准确怎么办？</h4>
					<p>A: 可以尝试：</p>
					<ul>
						<li>提高图像质量和清晰度</li>
						<li>确保谱图完整，包含坐标轴</li>
						<li>选择正确的谱图类型</li>
					</ul>
				</div>
			</div>

			<div class="content-block">
				<h3>技术支持</h3>
				<p>如果您遇到其他问题，请：</p>
				<ul>
					<li>查看 <a href="/api-docs">API 文档</a></li>
					<li>访问 <a href="/contact">联系我们</a> 页面</li>
					<li>发送邮件至技术支持团队</li>
				</ul>
			</div>
		</section>
	</main>
</div>

<style>
	.docs-container {
		display: flex;
		max-width: 1200px;
		margin: 0 auto;
		padding: 2rem;
		gap: 2rem;
		min-height: calc(100vh - 200px);
	}

	.sidebar {
		flex: 0 0 250px;
		position: sticky;
		top: 2rem;
		height: fit-content;
	}

	.docs-nav h3 {
		margin: 0 0 1rem 0;
		color: var(--color-theme-1);
		font-size: 1.2rem;
	}

	.docs-nav ul {
		list-style: none;
		padding: 0;
		margin: 0;
	}

	.docs-nav li {
		margin-bottom: 0.5rem;
	}

	.docs-nav button {
		width: 100%;
		padding: 0.75rem 1rem;
		text-align: left;
		border: none;
		background: transparent;
		color: var(--color-text);
		border-radius: 6px;
		cursor: pointer;
		transition: all 0.2s;
		font-size: 0.9rem;
	}

	.docs-nav button:hover {
		background: rgba(255, 62, 0, 0.1);
		color: var(--color-theme-1);
	}

	.docs-nav button.active {
		background: var(--color-theme-1);
		color: white;
	}

	.docs-content {
		flex: 1;
		min-width: 0;
	}

	.docs-header {
		margin-bottom: 3rem;
		padding-bottom: 2rem;
		border-bottom: 2px solid var(--color-bg-1);
	}

	.docs-header h1 {
		margin: 0 0 1rem 0;
		color: var(--color-theme-1);
		font-size: 2.5rem;
	}

	.docs-header p {
		margin: 0;
		font-size: 1.1rem;
		color: var(--color-text-secondary);
		line-height: 1.6;
	}

	.docs-section {
		margin-bottom: 3rem;
		padding-bottom: 2rem;
		border-bottom: 1px solid var(--color-bg-1);
	}

	.docs-section:last-child {
		border-bottom: none;
	}

	.docs-section h2 {
		margin: 0 0 2rem 0;
		color: var(--color-theme-1);
		font-size: 2rem;
	}

	.content-block {
		margin-bottom: 2rem;
		padding: 1.5rem;
		background: var(--color-bg-0);
		border-radius: 8px;
		border: 1px solid var(--color-bg-1);
	}

	.content-block h3 {
		margin: 0 0 1rem 0;
		color: var(--color-theme-2);
		font-size: 1.3rem;
	}

	.content-block h4 {
		margin: 1rem 0 0.5rem 0;
		color: var(--color-text);
		font-size: 1.1rem;
	}

	.content-block p {
		margin: 0 0 1rem 0;
		line-height: 1.6;
	}

	.content-block ul,
	.content-block ol {
		margin: 0 0 1rem 0;
		padding-left: 1.5rem;
	}

	.content-block li {
		margin-bottom: 0.5rem;
		line-height: 1.5;
	}

	.faq-item {
		margin-bottom: 1.5rem;
		padding: 1rem;
		background: rgba(255, 62, 0, 0.05);
		border-radius: 6px;
		border-left: 4px solid var(--color-theme-1);
	}

	.faq-item:last-child {
		margin-bottom: 0;
	}

	.content-block a {
		color: var(--color-theme-1);
		text-decoration: none;
	}

	.content-block a:hover {
		text-decoration: underline;
	}

	@media (max-width: 768px) {
		.docs-container {
			flex-direction: column;
			padding: 1rem;
		}

		.sidebar {
			flex: none;
			position: static;
			margin-bottom: 2rem;
		}

		.docs-nav {
			display: flex;
			overflow-x: auto;
			gap: 0.5rem;
		}

		.docs-nav ul {
			display: flex;
			gap: 0.5rem;
			min-width: max-content;
		}

		.docs-nav li {
			margin-bottom: 0;
		}

		.docs-nav button {
			white-space: nowrap;
			padding: 0.5rem 1rem;
		}

		.docs-header h1 {
			font-size: 2rem;
		}

		.docs-section h2 {
			font-size: 1.5rem;
		}
	}
</style>