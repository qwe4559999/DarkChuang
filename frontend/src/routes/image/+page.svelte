<script>
	import { onMount } from 'svelte';
	import axios from 'axios';

	let files = [];
	let dragActive = false;
	let uploading = false;
	let results = null;
	let error = null;
	let fileInput;

	const API_BASE = 'http://localhost:8000';

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
		// 过滤只保留图像文件
		const imageFiles = droppedFiles.filter(file => 
			file.type.startsWith('image/')
		);
		files = [...files, ...imageFiles];
	}

	function handleFileSelect(e) {
		const selectedFiles = Array.from(e.target.files);
		files = [...files, ...selectedFiles];
	}

	function removeFile(index) {
		files = files.filter((_, i) => i !== index);
	}

	async function analyzeImages() {
		if (files.length === 0) {
			error = '请选择要分析的图像文件';
			return;
		}

		uploading = true;
		error = null;
		results = [];

		try {
			for (const file of files) {
				const formData = new FormData();
				formData.append('file', file);

				const response = await axios.post(`${API_BASE}/api/upload-image`, formData, {
					headers: {
						'Content-Type': 'multipart/form-data'
					},
					timeout: 600000 // 10分钟超时
				});

				results.push({
					filename: file.name,
					...response.data
				});
			}
		} catch (err) {
			error = err.response?.data?.detail || '图像分析失败，请重试';
		} finally {
			uploading = false;
		}
	}

	function formatFileSize(bytes) {
		if (bytes === 0) return '0 Bytes';
		const k = 1024;
		const sizes = ['Bytes', 'KB', 'MB', 'GB'];
		const i = Math.floor(Math.log(bytes) / Math.log(k));
		return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
	}
</script>

<svelte:head>
	<title>图像分析 - DarkChuang</title>
	<meta name="description" content="上传图像文件进行AI智能分析" />
</svelte:head>

<div class="image-analysis-container">
	<h1>智能图像分析</h1>
	<p>上传您的图像文件，我们将使用先进的AI视觉模型为您提供详细的分析结果。</p>

	<div class="upload-section">
		<div 
			class="drop-zone" 
			class:active={dragActive}
			on:dragover={handleDragOver}
			on:dragleave={handleDragLeave}
			on:drop={handleDrop}
		>
			<div class="drop-content">
				<svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
					<rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
					<circle cx="8.5" cy="8.5" r="1.5"></circle>
					<polyline points="21,15 16,10 5,21"></polyline>
				</svg>
				<p>拖拽图像文件到此处或点击选择文件</p>
				<p class="file-types">支持格式: JPG, PNG, GIF, WebP, BMP</p>
			</div>
			<input 
				type="file" 
				multiple 
				accept="image/*"
				on:change={handleFileSelect}
				style="display: none;"
				bind:this={fileInput}
			/>
		</div>

		{#if files.length > 0}
			<div class="file-list">
				<h3>已选择的图像:</h3>
				{#each files as file, index}
					<div class="file-item">
						<div class="file-info">
							<span class="file-name">{file.name}</span>
							<span class="file-size">({formatFileSize(file.size)})</span>
							<span class="file-type">{file.type}</span>
						</div>
						<button class="remove-btn" on:click={() => removeFile(index)}>×</button>
					</div>
				{/each}
			</div>
		{/if}

		<div class="upload-actions">
			<button 
				class="btn btn-secondary" 
				on:click={() => fileInput.click()}
				disabled={uploading}
			>
				选择图像
			</button>
			<button 
				class="btn btn-primary" 
				on:click={analyzeImages}
				disabled={uploading || files.length === 0}
			>
				{uploading ? '分析中...' : '开始分析'}
			</button>
		</div>

		{#if error}
			<div class="error">
				<p>{error}</p>
			</div>
		{/if}

		{#if results && results.length > 0}
			<div class="results">
				<h3>分析结果:</h3>
				{#each results as result}
					<div class="result-item">
						<h4>{result.filename}</h4>
						{#if result.analysis_result}
							<div class="analysis-content">
								<div class="analysis-section">
									<h5>📝 文本内容</h5>
									<p class="text-content">{result.analysis_result.text_content || '未检测到文本内容'}</p>
								</div>
								
								{#if result.analysis_result.chemical_formulas && result.analysis_result.chemical_formulas.length > 0}
									<div class="analysis-section">
										<h5>🧪 化学公式</h5>
										<ul class="formula-list">
											{#each result.analysis_result.chemical_formulas as formula}
												<li>{formula}</li>
											{/each}
										</ul>
									</div>
								{/if}

								{#if result.analysis_result.confidence_scores}
									<div class="analysis-section">
										<h5>📊 置信度分数</h5>
										<div class="confidence-scores">
											{#each Object.entries(result.analysis_result.confidence_scores) as [key, value]}
												<div class="score-item">
													<span class="score-label">{key}:</span>
													<span class="score-value">{(value * 100).toFixed(1)}%</span>
												</div>
											{/each}
										</div>
									</div>
								{/if}

								<div class="analysis-meta">
									<small>处理时间: {result.analysis_result.processing_time?.toFixed(2)}秒</small>
								</div>
							</div>
						{:else}
							<p>分析结果不可用</p>
						{/if}
					</div>
				{/each}
			</div>
		{/if}
	</div>
</div>

<style>
	.image-analysis-container {
		max-width: 800px;
		margin: 0 auto;
		padding: 2rem;
	}

	h1 {
		color: #2c3e50;
		margin-bottom: 0.5rem;
		font-size: 2.5rem;
		font-weight: 700;
	}

	p {
		color: #7f8c8d;
		margin-bottom: 2rem;
		font-size: 1.1rem;
		line-height: 1.6;
	}

	.upload-section {
		background: white;
		border-radius: 12px;
		padding: 2rem;
		box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
	}

	.drop-zone {
		border: 3px dashed #bdc3c7;
		border-radius: 12px;
		padding: 3rem 2rem;
		text-align: center;
		transition: all 0.3s ease;
		cursor: pointer;
		position: relative;
	}

	.drop-zone:hover,
	.drop-zone.active {
		border-color: #3498db;
		background-color: #f8f9fa;
		transform: translateY(-2px);
	}

	.drop-content svg {
		color: #95a5a6;
		margin-bottom: 1rem;
	}

	.drop-content p {
		margin: 0.5rem 0;
		color: #2c3e50;
		font-weight: 500;
	}

	.file-types {
		font-size: 0.9rem;
		color: #95a5a6 !important;
	}

	.file-list {
		margin: 2rem 0;
	}

	.file-list h3 {
		color: #2c3e50;
		margin-bottom: 1rem;
		font-size: 1.2rem;
	}

	.file-item {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 0.75rem 1rem;
		background: #f8f9fa;
		border-radius: 8px;
		margin-bottom: 0.5rem;
		border: 1px solid #e9ecef;
	}

	.file-info {
		display: flex;
		flex-direction: column;
		gap: 0.25rem;
	}

	.file-name {
		font-weight: 500;
		color: #2c3e50;
	}

	.file-size,
	.file-type {
		font-size: 0.85rem;
		color: #6c757d;
	}

	.remove-btn {
		background: #e74c3c;
		color: white;
		border: none;
		border-radius: 50%;
		width: 24px;
		height: 24px;
		cursor: pointer;
		font-size: 16px;
		display: flex;
		align-items: center;
		justify-content: center;
		transition: background-color 0.2s;
	}

	.remove-btn:hover {
		background: #c0392b;
	}

	.upload-actions {
		display: flex;
		gap: 1rem;
		margin-top: 2rem;
	}

	.btn {
		padding: 0.75rem 1.5rem;
		border: none;
		border-radius: 8px;
		font-size: 1rem;
		font-weight: 500;
		cursor: pointer;
		transition: all 0.2s;
		flex: 1;
	}

	.btn:disabled {
		opacity: 0.6;
		cursor: not-allowed;
	}

	.btn-secondary {
		background: #6c757d;
		color: white;
	}

	.btn-secondary:hover:not(:disabled) {
		background: #5a6268;
	}

	.btn-primary {
		background: #3498db;
		color: white;
	}

	.btn-primary:hover:not(:disabled) {
		background: #2980b9;
	}

	.error {
		background: #f8d7da;
		color: #721c24;
		padding: 1rem;
		border-radius: 8px;
		margin-top: 1rem;
		border: 1px solid #f5c6cb;
	}

	.results {
		margin-top: 2rem;
	}

	.results h3 {
		color: #2c3e50;
		margin-bottom: 1.5rem;
		font-size: 1.4rem;
	}

	.result-item {
		background: white;
		border: 1px solid #e9ecef;
		border-radius: 12px;
		padding: 1.5rem;
		margin-bottom: 1.5rem;
		box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
	}

	.result-item h4 {
		color: #2c3e50;
		margin-bottom: 1rem;
		font-size: 1.2rem;
		border-bottom: 2px solid #3498db;
		padding-bottom: 0.5rem;
	}

	.analysis-content {
		display: flex;
		flex-direction: column;
		gap: 1.5rem;
	}

	.analysis-section {
		background: #f8f9fa;
		padding: 1rem;
		border-radius: 8px;
		border-left: 4px solid #3498db;
	}

	.analysis-section h5 {
		color: #2c3e50;
		margin-bottom: 0.75rem;
		font-size: 1rem;
		font-weight: 600;
	}

	.text-content {
		background: white;
		padding: 1rem;
		border-radius: 6px;
		border: 1px solid #dee2e6;
		white-space: pre-wrap;
		line-height: 1.5;
		color: #495057;
	}

	.formula-list {
		list-style: none;
		padding: 0;
		margin: 0;
	}

	.formula-list li {
		background: white;
		padding: 0.5rem 0.75rem;
		margin-bottom: 0.5rem;
		border-radius: 6px;
		border: 1px solid #dee2e6;
		font-family: 'Courier New', monospace;
		color: #495057;
	}

	.confidence-scores {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
		gap: 0.75rem;
	}

	.score-item {
		background: white;
		padding: 0.75rem;
		border-radius: 6px;
		border: 1px solid #dee2e6;
		display: flex;
		justify-content: space-between;
		align-items: center;
	}

	.score-label {
		font-weight: 500;
		color: #495057;
	}

	.score-value {
		font-weight: 600;
		color: #28a745;
	}

	.analysis-meta {
		text-align: right;
		padding-top: 1rem;
		border-top: 1px solid #dee2e6;
		margin-top: 1rem;
	}

	.analysis-meta small {
		color: #6c757d;
		font-style: italic;
	}

	@media (max-width: 768px) {
		.image-analysis-container {
			padding: 1rem;
		}

		.upload-actions {
			flex-direction: column;
		}

		.confidence-scores {
			grid-template-columns: 1fr;
		}
	}
</style>