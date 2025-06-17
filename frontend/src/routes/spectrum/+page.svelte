<script>
	import { onMount } from 'svelte';
	import axios from 'axios';

	let files = [];
	let dragActive = false;
	let analyzing = false;
	let results = [];
	let error = null;
	let fileInput;
	let selectedSpectrumType = 'auto';
	let supportedTypes = [];
	let showTypeSelection = false; // 控制是否显示类型选择
	let analysisProgress = { current: 0, total: 0, currentFile: '' }; // 分析进度
	let additionalInfo = ''; // 补充信息输入框

	const API_BASE = 'http://localhost:8000';

	// 谱图类型说明
	const spectrumTypeDescriptions = {
		'IR': '红外光谱 - 用于识别官能团和分子结构',
		'NMR': '核磁共振谱 - 分析分子骨架和化学环境',
		'UV': '紫外光谱 - 检测共轭体系和芳香化合物',
		'MS': '质谱 - 确定分子量和分子式',
		'Raman': '拉曼光谱 - 分析分子振动和晶体结构',
		'XRD': 'X射线衍射 - 确定晶体结构'
	};

	onMount(async () => {
		// 获取支持的谱图类型
		try {
			const response = await axios.get(`${API_BASE}/api/v1/spectrum/supported-types`);
			supportedTypes = response.data.supported_types || Object.keys(spectrumTypeDescriptions);
		} catch (err) {
			console.warn('无法获取支持的谱图类型，使用默认类型');
			supportedTypes = Object.keys(spectrumTypeDescriptions);
		}
	});

	function handleDragOver(e) {
		e.preventDefault();
		dragActive = true;
	}

	function handleDragLeave(e) {
		e.preventDefault();
		dragActive = false;
	}

	function handleDrop(e) {
		e.preventDefault();
		dragActive = false;
		const droppedFiles = Array.from(e.dataTransfer.files);
		const imageFiles = droppedFiles.filter(file => file.type.startsWith('image/'));
		files = [...files, ...imageFiles];
	}

	function handleFileSelect(e) {
		const selectedFiles = Array.from(e.target.files);
		const imageFiles = selectedFiles.filter(file => file.type.startsWith('image/'));
		files = [...files, ...imageFiles];
	}

	function removeFile(index) {
		files = files.filter((_, i) => i !== index);
	}

	function clearResults() {
		results = [];
		error = null;
		// 清理文件URL以释放内存
		files.forEach(file => {
			if (file.url) {
				URL.revokeObjectURL(file.url);
			}
		});
	}

	async function analyzeSpectra() {
		if (files.length === 0) {
			error = '请选择要分析的谱图文件';
			return;
		}

		analyzing = true;
		error = null;
		results = [];

		// 临时存储分析结果，避免过早显示
		const tempResults = [];
		let currentProgress = 0;

		try {
			for (let i = 0; i < files.length; i++) {
				const file = files[i];
				currentProgress = i + 1;
				
				// 更新进度状态
				analysisProgress = {
					current: currentProgress,
					total: files.length,
					currentFile: file.name
				};
				console.log(`正在分析第 ${currentProgress}/${files.length} 个文件: ${file.name}`);

				const formData = new FormData();
				formData.append('file', file);
				formData.append('spectrum_type', selectedSpectrumType);
				// 添加补充信息
				if (additionalInfo.trim()) {
					formData.append('additional_info', additionalInfo.trim());
				}

				const response = await axios.post(`${API_BASE}/api/v1/spectrum/analyze`, formData, {
					headers: {
						'Content-Type': 'multipart/form-data'
					},
					timeout: 600000 // 10分钟超时
				});

				// 检查响应是否成功
				if (!response.data || !response.data.success) {
					throw new Error(response.data?.message || `文件 ${file.name} 分析失败`);
				}

				// 获取原始分析结果
				const analysisResult = {
					filename: file.name,
					fileUrl: URL.createObjectURL(file),
					...response.data
				};

				// 使用DeepSeek的原始Markdown格式分析结果
			const rawAnalysis = response.data.raw_analysis || response.data.analysis_result;
			analysisResult.formatted_analysis = rawAnalysis;
			
			// 创建简化的可视化结构
			const simpleViz = createSimpleVisualization(rawAnalysis);
			if (simpleViz) {
				analysisResult.visualization = simpleViz;
			}

				// 添加到临时结果数组
				tempResults.push(analysisResult);
			}

			// 所有文件分析完成后，一次性更新结果
			results = tempResults;
			analysisProgress = { current: 0, total: 0, currentFile: '' }; // 重置进度
			console.log(`分析完成，共处理 ${results.length} 个文件`);
			
		} catch (err) {
			console.error('分析过程中出现错误:', err);
			error = err.message || err.response?.data?.detail || '分析失败，请重试';
			// 如果有部分成功的结果，仍然显示
			if (tempResults.length > 0) {
				results = tempResults;
			}
		} finally {
			analyzing = false;
			analysisProgress = { current: 0, total: 0, currentFile: '' }; // 重置进度
		}
	}

	function formatAnalysisResult(result) {
		if (typeof result === 'string') {
			// 处理Markdown格式的文本
			let formatted = result
				// 处理代码块（三个反引号）
				.replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>')
				// 处理行内代码（单个反引号）
				.replace(/`([^`]+)`/g, '<code>$1</code>')
				// 处理不同级别的标题
				.replace(/^#{6}\s+(.+)$/gm, '<h6>$1</h6>')
				.replace(/^#{5}\s+(.+)$/gm, '<h5>$1</h5>')
				.replace(/^#{4}\s+(.+)$/gm, '<h4>$1</h4>')
				.replace(/^#{3}\s+(.+)$/gm, '<h3>$1</h3>')
				.replace(/^#{2}\s+(.+)$/gm, '<h2>$1</h2>')
				.replace(/^#{1}\s+(.+)$/gm, '<h1>$1</h1>')
				// 处理粗体
				.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
				// 处理斜体（避免与粗体冲突）
				.replace(/(?<!\*)\*([^*]+)\*(?!\*)/g, '<em>$1</em>')
				// 处理删除线
				.replace(/~~(.*?)~~/g, '<del>$1</del>')
				// 处理链接
				.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank">$1</a>')
				// 处理水平分割线
				.replace(/^---+$/gm, '<hr>')
				// 处理引用块
				.replace(/^>\s+(.+)$/gm, '<blockquote>$1</blockquote>')
				// 处理无序列表项
				.replace(/^[-*+]\s+(.+)$/gm, '<li>$1</li>')
				// 处理有序列表项
				.replace(/^\d+\.\s+(.+)$/gm, '<li class="ordered">$1</li>')
				// 处理表格（简单实现）
				.replace(/\|(.+)\|/g, (match, content) => {
					const cells = content.split('|').map(cell => `<td>${cell.trim()}</td>`).join('');
					return `<tr>${cells}</tr>`;
				})
				// 处理段落分隔（双换行）
				.replace(/\n\s*\n/g, '</p><p>')
				// 处理单个换行
				.replace(/\n/g, '<br>');
			
			// 包装列表
			formatted = formatted
				// 包装有序列表
				.replace(/(<li class="ordered">.*?<\/li>)/gs, (match) => {
					return `<ol>${match.replace(/class="ordered"/g, '')}</ol>`;
				})
				// 包装无序列表
				.replace(/(<li>.*?<\/li>)/gs, '<ul>$1</ul>')
				// 包装表格
				.replace(/(<tr>.*?<\/tr>)/gs, '<table class="analysis-table">$1</table>');
			
			// 包装段落（在最后处理）
			if (!formatted.startsWith('<')) {
				formatted = '<p>' + formatted + '</p>';
			}
			
			// 清理多余的段落标签
			formatted = formatted
				.replace(/<p>(<h[1-6]>)/g, '$1')
				.replace(/(<\/h[1-6]>)<\/p>/g, '$1')
				.replace(/<p>(<ul>)/g, '$1')
				.replace(/(<\/ul>)<\/p>/g, '$1')
				.replace(/<p>(<ol>)/g, '$1')
				.replace(/(<\/ol>)<\/p>/g, '$1')
				.replace(/<p>(<blockquote>)/g, '$1')
				.replace(/(<\/blockquote>)<\/p>/g, '$1')
				.replace(/<p>(<pre>)/g, '$1')
				.replace(/(<\/pre>)<\/p>/g, '$1')
				.replace(/<p>(<table)/g, '$1')
				.replace(/(<\/table>)<\/p>/g, '$1')
				.replace(/<p>(<hr>)<\/p>/g, '$1');
			
			return formatted;
		}
		if (typeof result === 'object') {
			return `<pre><code>${JSON.stringify(result, null, 2)}</code></pre>`;
		}
		return String(result);
	}

	// 简化的可视化处理函数
	function createSimpleVisualization(rawAnalysis) {
		if (!rawAnalysis || typeof rawAnalysis !== 'string') {
			return null;
		}
		
		try {
			// 提取主要部分
			const sections = rawAnalysis.split(/\n\s*\n/);
			const visualization = {
				summary: '',
				key_findings: [],
				detailed_analysis: '',
				recommendations: ''
			};
			
			// 简单的内容分类
			for (let section of sections) {
				section = section.trim();
				if (!section) continue;
				
				// 检查是否是摘要部分
				if (section.includes('摘要') || section.includes('总结') || section.includes('概述')) {
					visualization.summary = section;
				}
				// 检查是否是关键发现
				else if (section.includes('关键') || section.includes('发现') || section.includes('特征峰')) {
					// 提取列表项
					const findings = section.split('\n').filter(line => 
						line.trim().startsWith('-') || 
						line.trim().startsWith('*') || 
						line.trim().match(/^\d+\./)
					);
					visualization.key_findings = findings.map(f => f.replace(/^[-*\d.\s]+/, '').trim());
				}
				// 检查是否是建议部分
				else if (section.includes('建议') || section.includes('推荐') || section.includes('结论')) {
					visualization.recommendations = section;
				}
				// 其他内容归为详细分析
				else {
					visualization.detailed_analysis += section + '\n\n';
				}
			}
			
			// 如果没有找到特定部分，将所有内容作为详细分析
			if (!visualization.summary && !visualization.key_findings.length && !visualization.recommendations) {
				visualization.detailed_analysis = rawAnalysis;
			}
			
			return visualization;
		} catch (error) {
			console.error('创建简化可视化失败:', error);
			return null;
		}
	}

	function downloadResult(result) {
		const dataStr = JSON.stringify(result, null, 2);
		const dataBlob = new Blob([dataStr], { type: 'application/json' });
		const url = URL.createObjectURL(dataBlob);
		const link = document.createElement('a');
		link.href = url;
		link.download = `${result.filename}_analysis.json`;
		link.click();
		URL.revokeObjectURL(url);
	}
</script>

<svelte:head>
	<title>谱图识别分析 - DarkChuang</title>
	<meta name="description" content="AI驱动的化学谱图识别和分析系统" />
</svelte:head>

<div class="spectrum-container">
	<div class="spectrum-header">
		<h1>🔬 谱图识别分析</h1>
		<p>上传化学谱图，AI将自动识别类型并提供专业分析结果</p>
		
		<!-- 类型选择切换按钮 -->
		<div class="type-selection-toggle">
			<button 
				class="toggle-btn"
				on:click={() => showTypeSelection = !showTypeSelection}
			>
				{showTypeSelection ? '🤖 使用AI自动识别' : '⚙️ 手动选择类型'}
			</button>
			{#if !showTypeSelection}
				<span class="auto-mode-hint">当前模式：AI自动识别谱图类型</span>
			{/if}
		</div>
	</div>

	<!-- 谱图类型选择（可选） -->
	{#if showTypeSelection}
		<div class="spectrum-type-section">
			<h3>手动选择谱图类型</h3>
			<div class="spectrum-types">
				<label class="spectrum-type-option">
					<input 
						type="radio" 
						bind:group={selectedSpectrumType} 
						value="auto"
					/>
					<div class="spectrum-type-card auto-card">
						<div class="spectrum-type-name">🤖 AUTO</div>
						<div class="spectrum-type-desc">
							AI自动识别谱图类型（推荐）
						</div>
					</div>
				</label>
				{#each supportedTypes as type}
					<label class="spectrum-type-option">
						<input 
							type="radio" 
							bind:group={selectedSpectrumType} 
							value={type}
						/>
						<div class="spectrum-type-card">
							<div class="spectrum-type-name">{type}</div>
							<div class="spectrum-type-desc">
								{spectrumTypeDescriptions[type] || '专业谱图分析'}
							</div>
						</div>
					</label>
				{/each}
			</div>
		</div>
	{/if}

	<!-- 文件上传区域 -->
	<div class="upload-section">
		<h3>上传谱图文件</h3>
		<div 
			class="drop-zone" 
			class:active={dragActive}
			on:dragover={handleDragOver}
			on:dragleave={handleDragLeave}
			on:drop={handleDrop}
			on:click={() => fileInput.click()}
		>
			<div class="drop-content">
				<svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
					<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
					<polyline points="7,10 12,15 17,10"></polyline>
					<line x1="12" y1="15" x2="12" y2="3"></line>
				</svg>
				<p>拖拽谱图文件到此处或点击选择文件</p>
				<p class="file-types">支持格式: PNG, JPG, JPEG, GIF, BMP</p>
			</div>
			<input 
				type="file" 
				multiple 
				accept="image/*"
				bind:this={fileInput}
				on:change={handleFileSelect}
				style="display: none;"
			/>
		</div>

		<!-- 补充信息输入区域 -->
		<div class="additional-info-section">
			<h4>📝 补充信息（可选）</h4>
			<div class="info-input-container">
				<textarea 
					bind:value={additionalInfo}
					placeholder="请输入补充信息，例如：&#10;• 分子式：C6H6&#10;• 化合物名称：苯&#10;• 实验条件：室温，KBr压片&#10;• 其他相关信息..."
					rows="4"
					class="additional-info-input"
				></textarea>
				<div class="info-hint">
					<span class="hint-icon">💡</span>
					<span>提供分子式、化合物名称、实验条件等信息可以帮助AI进行更准确的分析</span>
				</div>
			</div>
		</div>

		<!-- 已选择的文件列表 -->
		{#if files.length > 0}
			<div class="file-list">
				<h4>已选择的文件 ({files.length})</h4>
				<div class="files">
					{#each files as file, index}
						<div class="file-item">
							<div class="file-preview">
								<img src={URL.createObjectURL(file)} alt={file.name} />
							</div>
							<div class="file-info">
								<div class="file-name">{file.name}</div>
								<div class="file-size">{(file.size / 1024 / 1024).toFixed(2)} MB</div>
							</div>
							<button class="remove-btn" on:click={() => removeFile(index)}>×</button>
						</div>
					{/each}
				</div>
			</div>
		{/if}

		<!-- 操作按钮 -->
		<div class="action-buttons">
			<button 
				class="analyze-btn" 
				on:click={analyzeSpectra} 
				disabled={analyzing || files.length === 0}
			>
				{#if analyzing}
					<span class="loading-spinner"></span>
					{#if analysisProgress.total > 0}
						分析中... ({analysisProgress.current}/{analysisProgress.total})
						{#if analysisProgress.currentFile}
							<br><small>当前: {analysisProgress.currentFile}</small>
						{/if}
					{:else}
						分析中...
					{/if}
				{:else}
					开始分析
				{/if}
			</button>
			{#if results.length > 0}
				<button class="clear-btn" on:click={clearResults}>清空结果</button>
			{/if}
		</div>
	</div>

	<!-- 错误信息 -->
	{#if error}
		<div class="error-message">
			<strong>错误:</strong> {error}
		</div>
	{/if}

	<!-- 分析结果 -->
	{#if results.length > 0}
		<div class="results-section">
			<h3>分析结果</h3>
			<div class="results">
				{#each results as result, index}
					<div class="result-item">
						<div class="result-header">
							<h4>{result.filename}</h4>
							<div class="result-actions">
								<button class="download-btn" on:click={() => downloadResult(result)}>
									下载结果
								</button>
							</div>
						</div>

						<div class="result-content">
							<div class="result-image">
								<img src={result.fileUrl} alt={result.filename} />
							</div>

							<div class="result-analysis">
								{#if result.success}
									{#if result.formatted_analysis}
								<div class="analysis-section">
									<h5>📊 DeepSeek专业分析结果</h5>
									<div class="formatted-content">
										{#if result.visualization}
											<!-- 可视化显示 -->
											<div class="visualization-container">
												{#if result.visualization.summary}
													<div class="summary-section">
														<h6>📋 分析摘要</h6>
														<div class="summary-content">
															{@html formatAnalysisResult(result.visualization.summary)}
														</div>
													</div>
												{/if}
												
												{#if result.visualization.key_findings.length > 0}
													<div class="key-findings-section">
														<h6>🔍 关键发现</h6>
														<ul class="key-findings-list">
															{#each result.visualization.key_findings as finding}
																<li>{finding}</li>
															{/each}
														</ul>
													</div>
												{/if}
												
												{#if result.visualization.detailed_analysis}
													<div class="detailed-analysis-section">
														<h6>📊 详细分析</h6>
														<div class="detailed-analysis-content">
															{@html formatAnalysisResult(result.visualization.detailed_analysis)}
														</div>
													</div>
												{/if}
												
												{#if result.visualization.recommendations}
													<div class="recommendations-section">
														<h6>💡 建议与结论</h6>
														<div class="recommendations-content">
															{@html formatAnalysisResult(result.visualization.recommendations)}
														</div>
													</div>
												{/if}
											</div>
										{:else}
											<!-- 原始Markdown显示 -->
											{@html formatAnalysisResult(result.formatted_analysis)}
										{/if}
									</div>
								</div>
							{/if}
									
									<!-- 双模型分析结果展示 -->
									{#if result.vision_description}
										<div class="analysis-section vision-section">
											<h5>👁️ 视觉模型描述 (Qwen2.5-VL)</h5>
											<div class="vision-description">
												{result.vision_description}
											</div>
										</div>
									{/if}

									{#if result.deepseek_analysis}
										<div class="analysis-section deepseek-section">
											<h5>🧠 专业分析 (DeepSeek-R1)</h5>
											<div class="deepseek-analysis">
								{@html formatAnalysisResult(result.deepseek_analysis)}
							</div>
										</div>
									{/if}

									<!-- 兼容旧版本单模型结果 -->
									{#if result.analysis && !result.vision_description && !result.deepseek_analysis}
										<div class="analysis-section">
											<h5>📊 分析结果</h5>
											<div class="analysis-text">
								{@html formatAnalysisResult(result.analysis)}
							</div>
										</div>
									{/if}

									{#if result.extracted_text}
										<div class="analysis-section">
											<h5>📝 提取的文本</h5>
											<div class="extracted-text">
												{result.extracted_text}
											</div>
										</div>
									{/if}

									{#if result.chemical_formulas && result.chemical_formulas.length > 0}
										<div class="analysis-section">
											<h5>🧪 化学公式</h5>
											<div class="chemical-formulas">
												{#each result.chemical_formulas as formula}
													<span class="formula">{formula}</span>
												{/each}
											</div>
										</div>
									{/if}

									{#if result.processing_time}
										<div class="analysis-meta">
											<small>处理时间: {result.processing_time.toFixed(2)}秒</small>
										</div>
									{/if}
								{:else}
									<div class="error-result">
										<strong>分析失败:</strong> {result.error || '未知错误'}
									</div>
								{/if}
							</div>
						</div>
					</div>
				{/each}
			</div>
		</div>
	{/if}
</div>

<style>
	.spectrum-container {
		max-width: 1000px;
		margin: 0 auto;
		padding: 2rem;
	}

	.spectrum-header {
		text-align: center;
		margin-bottom: 2rem;
	}

	.spectrum-header h1 {
		margin: 0 0 0.5rem 0;
		font-size: 2.5rem;
		color: #333;
	}

	.spectrum-header p {
		margin: 0;
		color: #666;
		font-size: 1.1rem;
	}

	.spectrum-type-section {
		margin-bottom: 2rem;
	}

	.spectrum-type-section h3 {
		margin: 0 0 1rem 0;
		color: #333;
	}

	.spectrum-types {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
		gap: 1rem;
	}

	.spectrum-type-option {
		cursor: pointer;
	}

	.spectrum-type-option input {
		display: none;
	}

	.spectrum-type-card {
		padding: 1rem;
		border: 2px solid #e9ecef;
		border-radius: 8px;
		transition: all 0.2s;
		background: white;
	}

	.spectrum-type-option input:checked + .spectrum-type-card {
		border-color: #667eea;
		background: #f8f9ff;
	}

	.spectrum-type-card:hover {
		border-color: #667eea;
		transform: translateY(-2px);
		box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
	}

	.spectrum-type-name {
		font-weight: bold;
		font-size: 1.1rem;
		color: #333;
		margin-bottom: 0.5rem;
	}

	.spectrum-type-desc {
		font-size: 0.9rem;
		color: #666;
		line-height: 1.4;
	}

	.upload-section {
		margin-bottom: 2rem;
	}

	.upload-section h3 {
		margin: 0 0 1rem 0;
		color: #333;
	}

	.drop-zone {
		border: 2px dashed #ddd;
		border-radius: 12px;
		padding: 3rem 2rem;
		text-align: center;
		cursor: pointer;
		transition: all 0.3s;
		background: #fafafa;
	}

	.drop-zone.active {
		border-color: #667eea;
		background: #f8f9ff;
	}

	.drop-zone:hover {
		border-color: #667eea;
		background: #f8f9ff;
	}

	.drop-content svg {
		color: #667eea;
		margin-bottom: 1rem;
	}

	.drop-content p {
		margin: 0.5rem 0;
		color: #333;
	}

	.file-types {
		font-size: 0.9rem;
		color: #666;
	}

	.file-list {
		margin-top: 1.5rem;
	}

	.file-list h4 {
		margin: 0 0 1rem 0;
		color: #333;
	}

	.files {
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
		gap: 1rem;
	}

	.file-item {
		border: 1px solid #e9ecef;
		border-radius: 8px;
		padding: 1rem;
		position: relative;
		background: white;
	}

	.file-preview {
		width: 100%;
		height: 120px;
		margin-bottom: 0.5rem;
		border-radius: 4px;
		overflow: hidden;
		background: #f8f9fa;
	}

	.file-preview img {
		width: 100%;
		height: 100%;
		object-fit: cover;
	}

	.file-info {
		text-align: center;
	}

	.file-name {
		font-weight: 500;
		color: #333;
		margin-bottom: 0.25rem;
		word-break: break-all;
	}

	.file-size {
		font-size: 0.8rem;
		color: #666;
	}

	.remove-btn {
		position: absolute;
		top: 0.5rem;
		right: 0.5rem;
		width: 24px;
		height: 24px;
		border: none;
		background: #dc3545;
		color: white;
		border-radius: 50%;
		cursor: pointer;
		font-size: 16px;
		line-height: 1;
		display: flex;
		align-items: center;
		justify-content: center;
	}

	.remove-btn:hover {
		background: #c82333;
	}

	.action-buttons {
		display: flex;
		gap: 1rem;
		margin-top: 1.5rem;
		justify-content: center;
	}

	.analyze-btn {
		padding: 0.75rem 2rem;
		background: #667eea;
		color: white;
		border: none;
		border-radius: 8px;
		cursor: pointer;
		font-size: 1rem;
		font-weight: 500;
		transition: all 0.2s;
		display: flex;
		align-items: center;
		gap: 0.5rem;
	}

	.analyze-btn:hover:not(:disabled) {
		background: #5a6fd8;
		transform: translateY(-1px);
	}

	.analyze-btn:disabled {
		opacity: 0.6;
		cursor: not-allowed;
		transform: none;
	}

	.clear-btn {
		padding: 0.75rem 1.5rem;
		background: #6c757d;
		color: white;
		border: none;
		border-radius: 8px;
		cursor: pointer;
		font-size: 1rem;
		transition: all 0.2s;
	}

	.clear-btn:hover {
		background: #5a6268;
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

	.error-message {
		padding: 1rem;
		background: #f8d7da;
		color: #721c24;
		border: 1px solid #f5c6cb;
		border-radius: 8px;
		margin: 1rem 0;
	}

	.results-section {
		margin-top: 2rem;
	}

	.results-section h3 {
		margin: 0 0 1.5rem 0;
		color: #333;
	}

	.results {
		display: flex;
		flex-direction: column;
		gap: 2rem;
	}

	.result-item {
		border: 1px solid #e9ecef;
		border-radius: 12px;
		padding: 1.5rem;
		background: white;
		box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
	}

	.result-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 1rem;
		padding-bottom: 1rem;
		border-bottom: 1px solid #e9ecef;
	}

	.result-header h4 {
		margin: 0;
		color: #333;
	}

	.download-btn {
		padding: 0.5rem 1rem;
		background: #28a745;
		color: white;
		border: none;
		border-radius: 6px;
		cursor: pointer;
		font-size: 0.9rem;
		transition: all 0.2s;
	}

	.download-btn:hover {
		background: #218838;
	}

	.result-content {
		display: grid;
		grid-template-columns: 300px 1fr;
		gap: 1.5rem;
		align-items: start;
	}

	.result-image {
		border: 1px solid #e9ecef;
		border-radius: 8px;
		overflow: hidden;
		background: #f8f9fa;
	}

	.result-image img {
		width: 100%;
		height: auto;
		display: block;
	}

	.result-analysis {
		display: flex;
		flex-direction: column;
		gap: 1rem;
	}

	.analysis-section {
		margin-bottom: 1.5rem;
		padding: 1.5rem;
		background: #f8fafc;
		border-left: 4px solid #3b82f6;
		border-radius: 8px;
		font-weight: 500;
		box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
		transition: all 0.2s ease;
	}

	.analysis-section:hover {
		box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
		transform: translateY(-1px);
	}

	.analysis-section h5 {
		margin: 0 0 0.75rem 0;
		color: #333;
		font-size: 1rem;
	}

	.analysis-text {
		white-space: pre-wrap;
		line-height: 1.6;
		color: #333;
	}

	.extracted-text {
		background: white;
		padding: 0.75rem;
		border-radius: 4px;
		border: 1px solid #e9ecef;
		font-family: monospace;
		font-size: 0.9rem;
		line-height: 1.4;
	}

	.chemical-formulas {
		display: flex;
		flex-wrap: wrap;
		gap: 0.5rem;
	}

	.formula {
		padding: 0.25rem 0.75rem;
		background: #667eea;
		color: white;
		border-radius: 20px;
		font-size: 0.9rem;
		font-family: monospace;
	}

	.analysis-meta {
		text-align: right;
		color: #666;
		font-style: italic;
	}

	.error-result {
		padding: 1rem;
		background: #f8d7da;
		color: #721c24;
		border-radius: 8px;
	}

	@media (max-width: 768px) {
		.spectrum-container {
			padding: 1rem;
		}

		.spectrum-types {
			grid-template-columns: 1fr;
		}

		.files {
			grid-template-columns: 1fr;
		}

		.result-content {
			grid-template-columns: 1fr;
			gap: 1rem;
		}

		.action-buttons {
			flex-direction: column;
			align-items: center;
		}

		.result-header {
			flex-direction: column;
			gap: 0.5rem;
			align-items: flex-start;
		}
	}

	/* 类型选择切换样式 */
	.type-selection-toggle {
		margin-top: 1rem;
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 0.5rem;
	}

	.toggle-btn {
		padding: 0.75rem 1.5rem;
		background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
		color: white;
		border: none;
		border-radius: 25px;
		cursor: pointer;
		font-size: 0.95rem;
		font-weight: 500;
		transition: all 0.3s ease;
		box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
	}

	.toggle-btn:hover {
		transform: translateY(-2px);
		box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
	}

	.auto-mode-hint {
		font-size: 0.9rem;
		color: #28a745;
	}

	/* 双模型分析结果样式 */
	.vision-section {
		background: linear-gradient(135deg, #e3f2fd 0%, #f3e5f5 100%);
		border-left: 4px solid #2196f3;
	}

	.vision-description {
		white-space: pre-wrap;
		line-height: 1.6;
		color: #1565c0;
		font-style: italic;
		background: rgba(255, 255, 255, 0.7);
		padding: 0.75rem;
		border-radius: 6px;
	}

	.deepseek-section {
		background: linear-gradient(135deg, #fff3e0 0%, #fce4ec 100%);
		border-left: 4px solid #ff9800;
	}

	.deepseek-analysis {
		white-space: pre-wrap;
		line-height: 1.6;
		color: #e65100;
		background: rgba(255, 255, 255, 0.8);
		padding: 0.75rem;
		border-radius: 6px;
		font-weight: 500;
	}

	.vision-section {
		border-left-color: #1565c0;
	}

	.vision-section h5 {
		color: #1565c0;
		font-weight: 600;
	}

	.deepseek-section {
		border-left-color: #e65100;
	}

	.deepseek-section h5 {
		color: #e65100;
		font-weight: 600;
	}

	/* 分析结果内容样式 */
	.vision-description,
	.deepseek-analysis,
	.analysis-text {
		line-height: 1.6;
		color: #374151;
	}

	.vision-description :global(p),
	.deepseek-analysis :global(p),
	.analysis-text :global(p) {
		margin: 0.5rem 0;
	}

	.vision-description :global(h4),
	.deepseek-analysis :global(h4),
	.analysis-text :global(h4) {
		color: #1f2937;
		margin: 1rem 0 0.5rem 0;
		font-size: 1.1rem;
		font-weight: 600;
	}

	.vision-description :global(strong),
	.deepseek-analysis :global(strong),
	.analysis-text :global(strong) {
		color: #1f2937;
		font-weight: 600;
	}

	.vision-description :global(em),
	.deepseek-analysis :global(em),
	.analysis-text :global(em) {
		color: #6b7280;
		font-style: italic;
	}

	.vision-description :global(ul),
	.deepseek-analysis :global(ul),
	.analysis-text :global(ul) {
		margin: 0.5rem 0;
		padding-left: 1.5rem;
	}

	.vision-description :global(li),
	.deepseek-analysis :global(li),
	.analysis-text :global(li) {
		margin: 0.25rem 0;
		list-style-type: disc;
	}

	.vision-description :global(pre),
	.deepseek-analysis :global(pre),
	.analysis-text :global(pre) {
		background: #f3f4f6;
		padding: 1rem;
		border-radius: 6px;
		overflow-x: auto;
		font-family: 'Courier New', monospace;
		font-size: 0.9rem;
		line-height: 1.4;
	}



	.summary-section,
	.key-findings-section,
	.detailed-analysis-section,
	.chemical-info-section,
	.recommendations-section,
	.formatted-content-section {
		background: rgba(255, 255, 255, 0.8);
		padding: 1rem;
		border-radius: 8px;
		border: 1px solid rgba(16, 185, 129, 0.2);
	}

	.summary-section h6,
	.key-findings-section h6,
	.detailed-analysis-section h6,
	.chemical-info-section h6,
	.recommendations-section h6 {
		color: #047857;
		font-weight: 600;
		margin: 0 0 0.75rem 0;
		font-size: 1rem;
		display: flex;
		align-items: center;
		gap: 0.5rem;
	}

	.summary-section p {
		margin: 0;
		line-height: 1.6;
		color: #374151;
		font-size: 1rem;
	}

	.key-findings-list {
		margin: 0;
		padding-left: 1.5rem;
		list-style-type: disc;
	}

	.key-findings-list li {
		margin-bottom: 0.5rem;
		line-height: 1.5;
		color: #374151;
	}

	.key-findings-list li strong {
		color: #047857;
		font-weight: 600;
	}

	.detailed-analysis-content,
	.chemical-info-content,
	.recommendations-content,
	.formatted-content {
		line-height: 1.6;
		color: #374151;
	}

	.detailed-analysis-content :global(h4),
	.chemical-info-content :global(h4),
	.recommendations-content :global(h4),
	.formatted-content :global(h4) {
		color: #047857;
		margin: 1rem 0 0.5rem 0;
		font-size: 1.1rem;
	}

	.detailed-analysis-content :global(p),
	.chemical-info-content :global(p),
	.recommendations-content :global(p),
	.formatted-content :global(p) {
		margin: 0.5rem 0;
	}

	.detailed-analysis-content :global(ul),
	.chemical-info-content :global(ul),
	.recommendations-content :global(ul),
	.formatted-content :global(ul) {
		padding-left: 1.5rem;
		margin: 0.5rem 0;
	}

	.detailed-analysis-content :global(li),
	.chemical-info-content :global(li),
	.recommendations-content :global(li),
	.formatted-content :global(li) {
		margin-bottom: 0.25rem;
	}

	.detailed-analysis-content :global(strong),
	.chemical-info-content :global(strong),
	.recommendations-content :global(strong),
	.formatted-content :global(strong) {
		color: #047857;
		font-weight: 600;
	}

	.detailed-analysis-content :global(pre),
	.chemical-info-content :global(pre),
	.recommendations-content :global(pre),
	.formatted-content :global(pre) {
		background: #f8f9fa;
		border: 1px solid #e9ecef;
		border-radius: 4px;
		padding: 0.75rem;
		overflow-x: auto;
		font-family: 'Courier New', monospace;
		font-size: 0.9rem;
		color: #495057;
		margin: 0.5rem 0;
	}

	/* 新增Markdown元素样式 */
	.detailed-analysis-content :global(code),
	.chemical-info-content :global(code),
	.recommendations-content :global(code),
	.formatted-content :global(code) {
		background: #f1f3f4;
		border: 1px solid #e1e5e9;
		border-radius: 3px;
		padding: 0.2rem 0.4rem;
		font-family: 'Courier New', monospace;
		font-size: 0.85rem;
		color: #d73a49;
	}

	.detailed-analysis-content :global(blockquote),
	.chemical-info-content :global(blockquote),
	.recommendations-content :global(blockquote),
	.formatted-content :global(blockquote) {
		border-left: 4px solid #667eea;
		background: #f8f9ff;
		padding: 0.75rem 1rem;
		margin: 1rem 0;
		font-style: italic;
		color: #4a5568;
	}

	.detailed-analysis-content :global(hr),
	.chemical-info-content :global(hr),
	.recommendations-content :global(hr),
	.formatted-content :global(hr) {
		border: none;
		border-top: 2px solid #e9ecef;
		margin: 1.5rem 0;
	}

	.detailed-analysis-content :global(.analysis-table),
	.chemical-info-content :global(.analysis-table),
	.recommendations-content :global(.analysis-table),
	.formatted-content :global(.analysis-table) {
		border-collapse: collapse;
		width: 100%;
		margin: 1rem 0;
		border: 1px solid #e9ecef;
		border-radius: 4px;
		overflow: hidden;
	}

	.detailed-analysis-content :global(.analysis-table td),
	.chemical-info-content :global(.analysis-table td),
	.recommendations-content :global(.analysis-table td),
	.formatted-content :global(.analysis-table td) {
		padding: 0.75rem;
		border-bottom: 1px solid #e9ecef;
		border-right: 1px solid #e9ecef;
		vertical-align: top;
	}

	.detailed-analysis-content :global(.analysis-table tr:nth-child(even)),
	.chemical-info-content :global(.analysis-table tr:nth-child(even)),
	.recommendations-content :global(.analysis-table tr:nth-child(even)),
	.formatted-content :global(.analysis-table tr:nth-child(even)) {
		background: #f8f9fa;
	}

	.detailed-analysis-content :global(ol),
	.chemical-info-content :global(ol),
	.recommendations-content :global(ol),
	.formatted-content :global(ol) {
		padding-left: 1.5rem;
		margin: 0.5rem 0;
		list-style-type: decimal;
	}

	.detailed-analysis-content :global(h1),
	.chemical-info-content :global(h1),
	.recommendations-content :global(h1),
	.formatted-content :global(h1) {
		color: #047857;
		margin: 1.5rem 0 1rem 0;
		font-size: 1.5rem;
		font-weight: 700;
		border-bottom: 2px solid #047857;
		padding-bottom: 0.5rem;
	}

	.detailed-analysis-content :global(h2),
	.chemical-info-content :global(h2),
	.recommendations-content :global(h2),
	.formatted-content :global(h2) {
		color: #047857;
		margin: 1.25rem 0 0.75rem 0;
		font-size: 1.3rem;
		font-weight: 600;
	}

	.detailed-analysis-content :global(h3),
	.chemical-info-content :global(h3),
	.recommendations-content :global(h3),
	.formatted-content :global(h3) {
		color: #047857;
		margin: 1rem 0 0.5rem 0;
		font-size: 1.2rem;
		font-weight: 600;
	}

	.detailed-analysis-content :global(h5),
	.chemical-info-content :global(h5),
	.recommendations-content :global(h5),
	.formatted-content :global(h5) {
		color: #047857;
		margin: 0.75rem 0 0.25rem 0;
		font-size: 1rem;
		font-weight: 600;
	}

	.detailed-analysis-content :global(h6),
	.chemical-info-content :global(h6),
	.recommendations-content :global(h6),
	.formatted-content :global(h6) {
		color: #047857;
		margin: 0.5rem 0 0.25rem 0;
		font-size: 0.9rem;
		font-weight: 600;
		text-transform: uppercase;
		letter-spacing: 0.5px;
	}

	.detailed-analysis-content :global(a),
	.chemical-info-content :global(a),
	.recommendations-content :global(a),
	.formatted-content :global(a) {
		color: #667eea;
		text-decoration: none;
		border-bottom: 1px solid #667eea;
		transition: all 0.2s;
	}

	.detailed-analysis-content :global(a:hover),
	.chemical-info-content :global(a:hover),
	.recommendations-content :global(a:hover),
	.formatted-content :global(a:hover) {
		color: #4c51bf;
		border-bottom-color: #4c51bf;
	}

	.detailed-analysis-content :global(del),
	.chemical-info-content :global(del),
	.recommendations-content :global(del),
	.formatted-content :global(del) {
		color: #6b7280;
		text-decoration: line-through;
	}

	.auto-card {
		background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
		color: white;
		border: 2px solid #28a745;
	}

	.auto-card .spectrum-type-name {
		color: white;
		font-weight: bold;
	}

	.auto-card .spectrum-type-desc {
		color: rgba(255, 255, 255, 0.9);
	}



	/* 分析按钮进度显示样式 */
	.analyze-btn small {
		font-size: 0.8rem;
		opacity: 0.8;
		font-weight: normal;
	}

	/* 可视化容器样式 */
	.visualization-container {
		display: flex;
		flex-direction: column;
		gap: 20px;
		padding: 10px 0;
	}

	/* 摘要部分样式 */
	.summary-section {
		background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
		color: white;
		padding: 20px;
		border-radius: 12px;
		box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
	}

	.summary-section h6 {
		margin: 0 0 15px 0;
		font-size: 1.1em;
		font-weight: 600;
		display: flex;
		align-items: center;
		gap: 8px;
	}

	.summary-content {
		line-height: 1.6;
		opacity: 0.95;
	}

	/* 关键发现部分样式 */
	.key-findings-section {
		background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
		color: white;
		padding: 20px;
		border-radius: 12px;
		box-shadow: 0 4px 15px rgba(240, 147, 251, 0.3);
	}

	.key-findings-section h6 {
		margin: 0 0 15px 0;
		font-size: 1.1em;
		font-weight: 600;
		display: flex;
		align-items: center;
		gap: 8px;
	}

	.key-findings-list {
		list-style: none;
		padding: 0;
		margin: 0;
	}

	.key-findings-list li {
		background: rgba(255, 255, 255, 0.2);
		padding: 12px 16px;
		margin: 8px 0;
		border-radius: 8px;
		border-left: 4px solid rgba(255, 255, 255, 0.5);
		backdrop-filter: blur(10px);
		transition: all 0.3s ease;
	}

	.key-findings-list li:hover {
		background: rgba(255, 255, 255, 0.3);
		transform: translateX(5px);
	}

	/* 详细分析部分样式 */
	.detailed-analysis-section {
		background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
		color: white;
		padding: 20px;
		border-radius: 12px;
		box-shadow: 0 4px 15px rgba(79, 172, 254, 0.3);
	}

	.detailed-analysis-section h6 {
		margin: 0 0 15px 0;
		font-size: 1.1em;
		font-weight: 600;
		display: flex;
		align-items: center;
		gap: 8px;
	}

	.detailed-analysis-content {
		line-height: 1.6;
		opacity: 0.95;
	}

	/* 建议部分样式 */
	.recommendations-section {
		background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
		color: #333;
		padding: 20px;
		border-radius: 12px;
		box-shadow: 0 4px 15px rgba(250, 112, 154, 0.3);
	}

	.recommendations-section h6 {
		margin: 0 0 15px 0;
		font-size: 1.1em;
		font-weight: 600;
		display: flex;
		align-items: center;
		gap: 8px;
		color: #333;
	}

	.recommendations-content {
		line-height: 1.6;
		color: #444;
	}

	/* 响应式设计 */
	@media (max-width: 768px) {
		.visualization-container {
			gap: 15px;
		}

		.summary-section,
		.key-findings-section,
		.detailed-analysis-section,
		.recommendations-section {
			padding: 15px;
			border-radius: 8px;
		}

		.key-findings-list li {
			padding: 10px 12px;
		}
	}

	/* 补充信息输入区域样式 */
	.additional-info-section {
		margin: 25px 0;
		padding: 20px;
		background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
		border-radius: 12px;
		border: 1px solid #dee2e6;
		box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
	}

	.additional-info-section h4 {
		margin: 0 0 15px 0;
		color: #495057;
		font-size: 1.1em;
		font-weight: 600;
		display: flex;
		align-items: center;
		gap: 8px;
	}

	.info-input-container {
		display: flex;
		flex-direction: column;
		gap: 12px;
	}

	.additional-info-input {
		width: 100%;
		box-sizing: border-box;
		padding: 12px 16px;
		border: 2px solid #e9ecef;
		border-radius: 8px;
		font-size: 14px;
		line-height: 1.5;
		resize: vertical;
		min-height: 100px;
		background: white;
		transition: all 0.3s ease;
		font-family: inherit;
	}

	.additional-info-input:focus {
		outline: none;
		border-color: #007bff;
		box-shadow: 0 0 0 3px rgba(0, 123, 255, 0.1);
		background: #fafbfc;
	}

	.additional-info-input::placeholder {
		color: #6c757d;
		white-space: pre-line;
	}

	.info-hint {
		display: flex;
		align-items: flex-start;
		gap: 8px;
		padding: 10px 12px;
		background: rgba(0, 123, 255, 0.05);
		border-left: 3px solid #007bff;
		border-radius: 4px;
		font-size: 13px;
		color: #495057;
		line-height: 1.4;
	}

	.hint-icon {
		flex-shrink: 0;
		font-size: 14px;
	}

	/* 响应式设计 */
	@media (max-width: 768px) {
		.additional-info-section {
			margin: 20px 0;
			padding: 15px;
		}

		.additional-info-input {
			padding: 10px 12px;
			font-size: 13px;
		}

		.info-hint {
			padding: 8px 10px;
			font-size: 12px;
		}
	}
</style>