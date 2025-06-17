<script>
	import { onMount } from 'svelte';

	let activeEndpoint = 'overview'; // 'overview', 'auth', 'spectrum', 'chat', 'image', 'errors'
	let apiBaseUrl = ''; // Will be set onMount
	let copySuccessMessage = '';

	onMount(() => {
		apiBaseUrl = window.location.origin;
	});

	function setActiveEndpoint(endpoint) {
		activeEndpoint = endpoint;
	}

	async function copyToClipboard(text) {
		try {
			await navigator.clipboard.writeText(text);
			copySuccessMessage = '已复制到剪贴板!';
			setTimeout(() => {
				copySuccessMessage = '';
			}, 2000);
		} catch (err) {
			copySuccessMessage = '复制失败!';
			console.error('Failed to copy: ', err);
			setTimeout(() => {
				copySuccessMessage = '';
			}, 2000);
		}
	}
</script>

<svelte:head>
	<title>API 文档 - DarkChuang</title>
	<meta name="description" content="DarkChuang 化学光谱分析平台 API 文档" />
</svelte:head>

{#if copySuccessMessage}
	<div class="copy-notification">
		{copySuccessMessage}
	</div>
{/if}

<div class="api-docs-container">
	<aside class="sidebar">
		<nav class="api-nav">
			<h3>API 文档</h3>
			<ul>
				<li>
					<button class:active={activeEndpoint === 'overview'} on:click={() => setActiveEndpoint('overview')}>
						概述
					</button>
				</li>
				<li>
					<button class:active={activeEndpoint === 'authentication'} on:click={() => setActiveEndpoint('authentication')}>
						认证
					</button>
				</li>
				<li>
					<button class:active={activeEndpoint === 'spectrum'} on:click={() => setActiveEndpoint('spectrum')}>
						谱图分析
					</button>
				</li>
				<li>
					<button class:active={activeEndpoint === 'chat'} on:click={() => setActiveEndpoint('chat')}>
						化学问答
					</button>
				</li>
				<li>
					<button class:active={activeEndpoint === 'image'} on:click={() => setActiveEndpoint('image')}>
						图像分析
					</button>
				</li>
				<li>
					<button class:active={activeEndpoint === 'errors'} on:click={() => setActiveEndpoint('errors')}>
						错误代码
					</button>
				</li>
			</ul>
		</nav>
	</aside>

	<main class="api-content">
		{#if activeEndpoint === 'overview'}
			<section class="api-section">
				<h1>🔌 API 概述</h1>
				<p>DarkChuang API 提供了完整的化学光谱分析服务，支持 RESTful 接口调用。</p>
				
				<div class="info-card">
					<h3>基础信息</h3>
					<ul>
						<li><strong>Base URL:</strong> <code>{apiBaseUrl}/api</code></li>
						<li><strong>API 版本:</strong> v1</li>
						<li><strong>数据格式:</strong> JSON</li>
						<li><strong>字符编码:</strong> UTF-8</li>
					</ul>
				</div>

				<div class="info-card">
					<h3>快速开始</h3>
					<p>所有API端点均相对于上述 Base URL。</p>
					<p>例如，谱图分析接口的完整URL为:</p>
					<div class="code-block">
						<button class="copy-btn" on:click={() => copyToClipboard(`${apiBaseUrl}/api/spectrum/analyze`)}>复制</button>
						<pre><code>{`${apiBaseUrl}/api/spectrum/analyze`}</code></pre>
					</div>
				</div>

				<div class="info-card">
					<h3>支持的功能</h3>
					<ul>
						<li>🔬 光谱图像识别和分析</li>
						<li>💬 智能化学问答</li>
						<li>🖼️ 化学图像处理</li>
						<li>📊 数据可视化</li>
					</ul>
				</div>
			</section>
		{/if}

		{#if activeEndpoint === 'authentication'}
			<section class="api-section">
				<h1>🔐 认证</h1>
				<p>API 请求需要在 HTTP Header 中包含 <code>Authorization</code> 字段，值为 <code>Bearer &lt;YOUR_ACCESS_TOKEN&gt;</code>。</p>
				<p>Access Token 可以通过用户登录获取。</p>
				
				<div class="info-card">
					<h3>请求头示例</h3>
					<div class="code-block">
						<button class="copy-btn" on:click={() => copyToClipboard('Content-Type: application/json\nAccept: application/json\nAuthorization: Bearer <YOUR_ACCESS_TOKEN>')}>复制</button>
						<pre><code>{`Content-Type: application/json
Accept: application/json
Authorization: Bearer <YOUR_ACCESS_TOKEN>`}</code></pre>
					</div>
				</div>

				<div class="info-card">
					<h3>CORS 支持</h3>
					<p>API 支持跨域请求，允许从授权的域名访问。</p>
				</div>
			</section>
		{/if}

		{#if activeEndpoint === 'spectrum'}
			<section class="api-section">
				<h1>🔬 谱图分析 API</h1>
				
				<div class="endpoint-card">
					<div class="endpoint-header">
						<span class="method post">POST</span>
						<span class="path">/api/spectrum/analyze</span>
					</div>
					<p>上传并分析光谱图像。请求体为 <code>multipart/form-data</code>。</p>
					
					<h4>请求参数</h4>
					<div class="params-table">
						<table>
							<thead>
								<tr>
									<th>参数名</th>
									<th>类型</th>
									<th>必需</th>
									<th>描述</th>
								</tr>
							</thead>
							<tbody>
								<tr>
									<td><code>file</code></td>
									<td>File</td>
									<td>是</td>
									<td>光谱图像文件 (JPG, PNG, PDF)</td>
								</tr>
								<tr>
									<td><code>spectrum_type</code></td>
									<td>String</td>
									<td>否</td>
									<td>谱图类型 (例如: IR, NMR, MS, UV-Vis)。如果提供，有助于提高分析准确性。</td>
								</tr>
							</tbody>
						</table>
					</div>

					<h4>响应示例 (成功)</h4>
					<div class="code-block">
						<button class="copy-btn" on:click={() => copyToClipboard(`{
  "success": true,
  "data": {
    "compound_name": "苯甲酸",
    "molecular_formula": "C7H6O2",
    "confidence": 0.95,
    "peaks": [
      {"frequency": 1680, "intensity": "strong", "assignment": "C=O stretch"},
      {"frequency": 3000, "intensity": "broad", "assignment": "O-H stretch"}
    ],
    "properties": {
      "molecular_weight": 122.12,
      "melting_point": "122-123°C",
      "boiling_point": "249°C"
    }
  }
}`)}>复制</button>
						<pre><code>{`{
  "success": true,
  "data": {
    "compound_name": "苯甲酸",
    "molecular_formula": "C7H6O2",
    "confidence": 0.95,
    "peaks": [
      {"frequency": 1680, "intensity": "strong", "assignment": "C=O stretch"},
      {"frequency": 3000, "intensity": "broad", "assignment": "O-H stretch"}
    ],
    "properties": {
      "molecular_weight": 122.12,
      "melting_point": "122-123°C",
      "boiling_point": "249°C"
    }
  }
}`}</code></pre>
					</div>
				</div>

				<div class="endpoint-card">
					<div class="endpoint-header">
						<span class="method get">GET</span>
						<span class="path">/api/spectrum/history</span>
					</div>
					<p>获取当前用户的光谱分析历史记录。</p>
					
					<h4>查询参数</h4>
					<div class="params-table">
						<table>
							<thead>
								<tr>
									<th>参数名</th>
									<th>类型</th>
									<th>默认值</th>
									<th>描述</th>
								</tr>
							</thead>
							<tbody>
								<tr>
									<td><code>page</code></td>
									<td>Integer</td>
									<td>1</td>
									<td>页码</td>
								</tr>
								<tr>
									<td><code>limit</code></td>
									<td>Integer</td>
									<td>10</td>
									<td>每页数量</td>
								</tr>
							</tbody>
						</table>
					</div>
					<h4>响应示例 (成功)</h4>
					<div class="code-block">
						<button class="copy-btn" on:click={() => copyToClipboard(`{
  "success": true,
  "data": {
    "history": [
      {
        "analysis_id": "spectrum_xyz789",
        "compound_name": "乙酸乙酯",
        "timestamp": "2024-07-28T10:30:00Z",
        "thumbnail_url": "${apiBaseUrl}/thumbnails/spectrum_xyz789.png"
      }
    ],
    "pagination": {
      "current_page": 1,
      "total_pages": 5,
      "total_items": 48
    }
  }
}`)}>复制</button>
						<pre><code>{`{
  "success": true,
  "data": {
    "history": [
      {
        "analysis_id": "spectrum_xyz789",
        "compound_name": "乙酸乙酯",
        "timestamp": "2024-07-28T10:30:00Z",
        "thumbnail_url": "${apiBaseUrl}/thumbnails/spectrum_xyz789.png"
      }
    ],
    "pagination": {
      "current_page": 1,
      "total_pages": 5,
      "total_items": 48
    }
  }
}`}</code></pre>
					</div>
				</div>
			</section>
		{/if}

		{#if activeEndpoint === 'chat'}
			<section class="api-section">
				<h1>💬 化学问答 API</h1>
				
				<div class="endpoint-card">
					<div class="endpoint-header">
						<span class="method post">POST</span>
						<span class="path">/api/chat/ask</span>
					</div>
					<p>发送化学问题并获取AI回答。请求体为 JSON。</p>
					
					<h4>请求体示例</h4>
					<div class="code-block">
						<button class="copy-btn" on:click={() => copyToClipboard(`{
  "question": "苯的分子式是什么？",
  "context": "有机化学",
  "session_id": "optional_session_id_to_continue_conversation"
}`)}>复制</button>
						<pre><code>{`{
  "question": "苯的分子式是什么？",
  "context": "有机化学",
  "session_id": "optional_session_id_to_continue_conversation"
}`}</code></pre>
					</div>

					<h4>响应示例 (成功)</h4>
					<div class="code-block">
						<button class="copy-btn" on:click={() => copyToClipboard(`{
  "success": true,
  "data": {
    "answer": "苯的分子式是 C6H6。苯是最简单的芳香烃，具有平面六元环结构...",
    "confidence": 0.98,
    "sources": ["有机化学教材 第五版", "维基百科 - 苯"],
    "session_id": "chat_session_abc123",
    "timestamp": "2024-07-28T12:00:00Z"
  }
}`)}>复制</button>
						<pre><code>{`{
  "success": true,
  "data": {
    "answer": "苯的分子式是 C6H6。苯是最简单的芳香烃，具有平面六元环结构...",
    "confidence": 0.98,
    "sources": ["有机化学教材 第五版", "维基百科 - 苯"],
    "session_id": "chat_session_abc123",
    "timestamp": "2024-07-28T12:00:00Z"
  }
}`}</code></pre>
					</div>
				</div>

				<div class="endpoint-card">
					<div class="endpoint-header">
						<span class="method get">GET</span>
						<span class="path">/api/chat/history/{'{session_id}'}</span>
					</div>
					<p>获取指定会话ID的对话历史记录。</p>
					<h4>响应示例 (成功)</h4>
					<div class="code-block">
						<button class="copy-btn" on:click={() => copyToClipboard(`{
  "success": true,
  "data": {
    "session_id": "chat_session_abc123",
    "messages": [
      {
        "role": "user",
        "content": "苯的分子式是什么？",
        "timestamp": "2024-07-28T11:59:00Z"
      },
      {
        "role": "assistant",
        "content": "苯的分子式是 C6H6。苯是最简单的芳香烃，具有平面六元环结构...",
        "timestamp": "2024-07-28T12:00:00Z"
      }
    ]
  }
}`)}>复制</button>
						<pre><code>{`{
  "success": true,
  "data": {
    "session_id": "chat_session_abc123",
    "messages": [
      {
        "role": "user",
        "content": "苯的分子式是什么？",
        "timestamp": "2024-07-28T11:59:00Z"
      },
      {
        "role": "assistant",
        "content": "苯的分子式是 C6H6。苯是最简单的芳香烃，具有平面六元环结构...",
        "timestamp": "2024-07-28T12:00:00Z"
      }
    ]
  }
}`}</code></pre>
					</div>
				</div>
			</section>
		{/if}

		{#if activeEndpoint === 'image'}
			<section class="api-section">
				<h1>🖼️ 图像分析 API</h1>
				
				<div class="endpoint-card">
					<div class="endpoint-header">
						<span class="method post">POST</span>
						<span class="path">/api/image/analyze</span>
					</div>
					<p>分析化学相关图像 (例如: 分子结构图, 实验装置图)。请求体为 <code>multipart/form-data</code>。</p>
					
					<h4>请求参数</h4>
					<div class="params-table">
						<table>
							<thead>
								<tr>
									<th>参数名</th>
									<th>类型</th>
									<th>必需</th>
									<th>描述</th>
								</tr>
							</thead>
							<tbody>
								<tr>
									<td><code>image</code></td>
									<td>File</td>
									<td>是</td>
									<td>图像文件 (JPG, PNG)</td>
								</tr>
								<tr>
									<td><code>analysis_type</code></td>
									<td>String</td>
									<td>否</td>
									<td>分析类型 (例如: structure, reaction, apparatus)。如果提供，有助于提高分析准确性。</td>
								</tr>
							</tbody>
						</table>
					</div>

					<h4>响应示例 (成功)</h4>
					<div class="code-block">
						<button class="copy-btn" on:click={() => copyToClipboard(`{
  "success": true,
  "data": {
    "analysis_type": "structure",
    "detected_elements": [
      {
        "name": "乙醇",
        "formula": "C2H5OH",
        "confidence": 0.92,
        "bounding_box": [100, 150, 250, 300]
      }
    ],
    "description": "图像中检测到乙醇分子结构，包含一个羟基官能团。"
  }
}`)}>复制</button>
						<pre><code>{`{
  "success": true,
  "data": {
    "analysis_type": "structure",
    "detected_elements": [
      {
        "name": "乙醇",
        "formula": "C2H5OH",
        "confidence": 0.92,
        "bounding_box": [100, 150, 250, 300]
      }
    ],
    "description": "图像中检测到乙醇分子结构，包含一个羟基官能团。"
  }
}`}</code></pre>
					</div>
				</div>
			</section>
		{/if}

		{#if activeEndpoint === 'errors'}
			<section class="api-section">
				<h1>⚠️ 错误代码</h1>
				<p>API 可能返回以下 HTTP 状态码和错误格式。</p>
				
				<div class="error-codes-grid">
					<div class="error-card">
						<h3>常见 HTTP 状态码</h3>
						<table>
							<thead>
								<tr>
									<th>状态码</th>
									<th>含义</th>
									<th>描述</th>
								</tr>
							</thead>
							<tbody>
								<tr><td><code>200</code></td><td>OK</td><td>请求成功。</td></tr>
								<tr><td><code>201</code></td><td>Created</td><td>资源创建成功。</td></tr>
								<tr><td><code>204</code></td><td>No Content</td><td>请求成功，但无内容返回。</td></tr>
								<tr><td><code>400</code></td><td>Bad Request</td><td>请求无效 (例如: 参数错误, 格式错误)。</td></tr>
								<tr><td><code>401</code></td><td>Unauthorized</td><td>未授权，需要有效的认证凭据。</td></tr>
								<tr><td><code>403</code></td><td>Forbidden</td><td>禁止访问，认证凭据有效但无权限。</td></tr>
								<tr><td><code>404</code></td><td>Not Found</td><td>请求的资源不存在。</td></tr>
								<tr><td><code>413</code></td><td>Payload Too Large</td><td>请求体过大 (例如: 上传文件超过限制)。</td></tr>
								<tr><td><code>422</code></td><td>Unprocessable Entity</td><td>请求格式正确，但由于语义错误无法处理。</td></tr>
								<tr><td><code>429</code></td><td>Too Many Requests</td><td>请求频率过高。</td></tr>
								<tr><td><code>500</code></td><td>Internal Server Error</td><td>服务器内部错误。</td></tr>
							</tbody>
						</table>
					</div>

					<div class="error-card">
						<h3>错误响应格式</h3>
						<p>当 API 调用失败时，会返回如下格式的 JSON 响应体:</p>
						<div class="code-block">
							<button class="copy-btn" on:click={() => copyToClipboard(`{
  "success": false,
  "error": {
    "code": "ERROR_CODE_STRING",
    "message": "人类可读的错误描述信息。",
    "details": "可选的，更详细的错误信息或导致错误的具体字段。"
  }
}`)}>复制</button>
							<pre><code>{`{
  "success": false,
  "error": {
    "code": "ERROR_CODE_STRING",
    "message": "人类可读的错误描述信息。",
    "details": "可选的，更详细的错误信息或导致错误的具体字段。"
  }
}`}</code></pre>
						</div>
						<h4>示例: 无效文件格式</h4>
						<div class="code-block">
							<button class="copy-btn" on:click={() => copyToClipboard(`{
  "success": false,
  "error": {
    "code": "INVALID_FILE_FORMAT",
    "message": "不支持的文件格式。",
    "details": "请上传 JPG, PNG 或 PDF 格式的光谱图像文件。"
  }
}`)}>复制</button>
							<pre><code>{`{
  "success": false,
  "error": {
    "code": "INVALID_FILE_FORMAT",
    "message": "不支持的文件格式。",
    "details": "请上传 JPG, PNG 或 PDF 格式的光谱图像文件。"
  }
}`}</code></pre>
						</div>
					</div>
				</div>
			</section>
		{/if}
	</main>
</div>

<style>
	.api-docs-container {
		display: flex;
		max-width: 1400px;
		margin: 2rem auto;
		padding: 0 2rem;
		gap: 3rem;
		min-height: calc(100vh - 200px);
		background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
		border-radius: 16px;
		box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
	}

	.sidebar {
		flex: 0 0 300px;
		position: sticky;
		top: 2rem;
		height: calc(100vh - 4rem);
		overflow-y: auto;
		padding: 2rem 1.5rem 2rem 2rem;
		background: linear-gradient(145deg, #ffffff 0%, #f8fafc 100%);
		border-radius: 16px;
		border: 1px solid rgba(226, 232, 240, 0.8);
		box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06);
		backdrop-filter: blur(10px);
	}

	.api-nav h3 {
		margin: 0 0 2rem 0;
		color: #1e293b;
		font-size: 1.5rem;
		font-weight: 700;
		text-align: center;
		padding-bottom: 1rem;
		border-bottom: 2px solid #e2e8f0;
		position: relative;
	}

	.api-nav h3::after {
		content: '';
		position: absolute;
		bottom: -2px;
		left: 50%;
		transform: translateX(-50%);
		width: 60px;
		height: 3px;
		background: linear-gradient(90deg, #3b82f6, #8b5cf6);
		border-radius: 2px;
	}

	.api-nav ul {
		list-style: none;
		padding: 0;
		margin: 0;
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
	}

	.api-nav li {
		margin-bottom: 0;
	}

	.api-nav button {
		width: 100%;
		padding: 1rem 1.5rem;
		text-align: left;
		border: none;
		background: transparent;
		color: #64748b;
		border-radius: 12px;
		cursor: pointer;
		transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
		font-size: 1rem;
		font-weight: 500;
		position: relative;
		overflow: hidden;
	}

	.api-nav button::before {
		content: '';
		position: absolute;
		top: 0;
		left: -100%;
		width: 100%;
		height: 100%;
		background: linear-gradient(90deg, transparent, rgba(59, 130, 246, 0.1), transparent);
		transition: left 0.5s ease;
	}

	.api-nav button:hover::before {
		left: 100%;
	}

	.api-nav button:hover {
		background: linear-gradient(135deg, rgba(59, 130, 246, 0.08) 0%, rgba(139, 92, 246, 0.08) 100%);
		color: #3b82f6;
		transform: translateX(8px);
		box-shadow: 0 4px 12px rgba(59, 130, 246, 0.15);
	}

	.api-nav button.active {
		background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
		color: white;
		font-weight: 600;
		transform: translateX(8px);
		box-shadow: 0 6px 20px rgba(59, 130, 246, 0.3);
	}

	.api-content {
		flex: 1;
		min-width: 0;
		padding: 2rem;
		padding-bottom: 3rem;
		background: rgba(255, 255, 255, 0.7);
		border-radius: 16px;
		backdrop-filter: blur(10px);
		border: 1px solid rgba(255, 255, 255, 0.2);
	}

	.api-section h1 {
		margin: 0 0 3rem 0;
		color: #1e293b;
		font-size: 3rem;
		font-weight: 800;
		text-align: center;
		padding-bottom: 1.5rem;
		position: relative;
		background: linear-gradient(135deg, #3b82f6, #8b5cf6);
		-webkit-background-clip: text;
		-webkit-text-fill-color: transparent;
		background-clip: text;
	}

	.api-section h1::after {
		content: '';
		position: absolute;
		bottom: 0;
		left: 50%;
		transform: translateX(-50%);
		width: 120px;
		height: 4px;
		background: linear-gradient(90deg, #3b82f6, #8b5cf6);
		border-radius: 2px;
	}

	.info-card, .endpoint-card, .error-card {
		margin-bottom: 2.5rem;
		padding: 2.5rem;
		background: linear-gradient(145deg, #ffffff 0%, #f8fafc 100%);
		border-radius: 16px;
		border: 1px solid rgba(226, 232, 240, 0.6);
		box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
		transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
		position: relative;
		overflow: hidden;
	}

	.info-card::before, .endpoint-card::before, .error-card::before {
		content: '';
		position: absolute;
		top: 0;
		left: 0;
		width: 100%;
		height: 4px;
		background: linear-gradient(90deg, #3b82f6, #8b5cf6);
	}

	.info-card:hover, .endpoint-card:hover, .error-card:hover {
		transform: translateY(-4px);
		box-shadow: 0 12px 40px rgba(0, 0, 0, 0.12);
	}

	.info-card h3, .endpoint-card h4, .error-card h3 {
		margin: 0 0 1.5rem 0;
		color: #1e293b;
		font-size: 1.6rem;
		font-weight: 700;
	}

	.endpoint-card h4 {
		font-size: 1.4rem;
	}

	.endpoint-header {
		display: flex;
		align-items: center;
		gap: 1rem;
		margin-bottom: 1.5rem;
		padding-bottom: 1rem;
		border-bottom: 1px dashed var(--color-bg-2, #eee);
	}

	.method {
		padding: 0.4rem 1rem;
		border-radius: 6px;
		font-weight: bold;
		font-size: 0.9rem;
		text-transform: uppercase;
		color: white;
	}

	.method.get { background: #4CAF50; }
	.method.post { background: #2196F3; }
	.method.put { background: #ff9800; }
	.method.delete { background: #f44336; }

	.path {
		font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, Courier, monospace;
		font-size: 1.2rem;
		color: var(--color-theme-1);
		font-weight: 600;
		background-color: rgba(var(--color-theme-1-rgb), 0.05);
		padding: 0.25rem 0.5rem;
		border-radius: 4px;
	}

	.code-block {
		position: relative;
		margin: 2rem 0;
		background: linear-gradient(145deg, #1e293b 0%, #334155 100%);
		border-radius: 12px;
		overflow: hidden;
		border: 1px solid #475569;
		box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
	}

	.copy-btn {
		position: absolute;
		top: 1rem;
		right: 1rem;
		padding: 0.5rem 1rem;
		background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
		color: white;
		border: none;
		border-radius: 8px;
		cursor: pointer;
		font-size: 0.85rem;
		font-weight: 500;
		transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
		z-index: 1;
		box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
	}

	.copy-btn:hover {
		background: linear-gradient(135deg, #2563eb 0%, #7c3aed 100%);
		transform: translateY(-2px);
		box-shadow: 0 6px 20px rgba(59, 130, 246, 0.4);
	}

	.copy-btn:active {
		transform: translateY(0);
	}

	.code-block pre {
		margin: 0;
		padding: 2rem;
		overflow-x: auto;
		color: #e2e8f0;
		font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, Courier, monospace;
		font-size: 0.95rem;
		line-height: 1.6;
		background: transparent;
	}

	.params-table {
		overflow-x: auto;
		margin: 2rem 0;
		border: 1px solid rgba(226, 232, 240, 0.6);
		border-radius: 12px;
		background: linear-gradient(145deg, #ffffff 0%, #f8fafc 100%);
		box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06);
	}

	.params-table table {
		width: 100%;
		border-collapse: collapse;
	}

	.params-table th,
	.params-table td {
		padding: 1.25rem;
		text-align: left;
		border-bottom: 1px solid rgba(226, 232, 240, 0.4);
	}

	.params-table tr:last-child td {
		border-bottom: none;
	}

	.params-table th {
		background: linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%);
		font-weight: 700;
		color: #1e293b;
		position: relative;
	}

	.params-table th::after {
		content: '';
		position: absolute;
		bottom: 0;
		left: 0;
		width: 100%;
		height: 2px;
		background: linear-gradient(90deg, #3b82f6, #8b5cf6);
	}

	.params-table code {
		background: linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%);
		padding: 0.4rem 0.8rem;
		border-radius: 6px;
		font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, Courier, monospace;
		color: #3b82f6;
		font-weight: 500;
		border: 1px solid rgba(59, 130, 246, 0.2);
		font-size: 0.9rem;
	}

	.error-codes-grid {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
		gap: 2.5rem;
	}

	.copy-notification {
		position: fixed;
		top: 2rem;
		left: 50%;
		transform: translateX(-50%);
		background: linear-gradient(135deg, #10b981 0%, #059669 100%);
		color: white;
		padding: 1rem 2rem;
		border-radius: 12px;
		box-shadow: 0 8px 32px rgba(16, 185, 129, 0.3);
		z-index: 1000;
		font-size: 0.95rem;
		font-weight: 500;
		backdrop-filter: blur(10px);
		border: 1px solid rgba(255, 255, 255, 0.2);
		animation: slideDown 0.3s ease-out;
	}

	@keyframes slideDown {
		from {
			transform: translateX(-50%) translateY(-100%);
			opacity: 0;
		}
		to {
			transform: translateX(-50%) translateY(0);
			opacity: 1;
		}
	}

	/* Responsive adjustments */
	@media (max-width: 992px) {
		.api-docs-container {
			flex-direction: column;
			padding: 1.5rem;
			gap: 2rem;
			margin: 1rem auto;
		}

		.sidebar {
			position: static;
			height: auto;
			overflow-y: visible;
			margin-bottom: 2rem;
			padding: 1.5rem;
			flex: none;
		}

		.api-content {
			padding: 1.5rem;
		}

		.api-nav h3 {
			text-align: center;
			font-size: 1.3rem;
		}

		.api-nav ul {
			display: flex;
			flex-wrap: wrap;
			gap: 0.75rem;
			justify-content: center;
		}

		.api-nav li {
			margin-bottom: 0;
			flex: 1 1 auto;
			min-width: 120px;
		}

		.api-nav button {
			font-size: 0.9rem;
			padding: 0.8rem 1rem;
			text-align: center;
			white-space: nowrap;
		}

		.api-section h1 {
			font-size: 2.5rem;
		}

		.info-card, .endpoint-card, .error-card {
			padding: 2rem;
		}

		.error-codes-grid {
			grid-template-columns: 1fr;
			gap: 1.5rem;
		}

		.api-nav button:hover, .api-nav button.active {
			transform: none;
			box-shadow: 0 4px 12px rgba(59, 130, 246, 0.15);
		}
	}

	@media (max-width: 768px) {
		.api-docs-container {
			padding: 1rem;
			margin: 0.5rem auto;
		}

		.sidebar {
			padding: 1rem;
		}

		.api-content {
			padding: 1rem;
		}

		.api-section h1 {
			font-size: 2.2rem;
		}

		.info-card, .endpoint-card, .error-card {
			padding: 1.5rem;
		}

		.endpoint-header {
			flex-direction: column;
			align-items: flex-start;
			gap: 1rem;
		}

		.method {
			font-size: 0.8rem;
			padding: 0.3rem 0.8rem;
		}

		.path {
			font-size: 1rem;
			word-break: break-all;
		}

		.code-block pre {
			padding: 1.5rem;
			font-size: 0.85rem;
		}

		.copy-btn {
			top: 0.5rem;
			right: 0.5rem;
			padding: 0.4rem 0.8rem;
			font-size: 0.8rem;
		}

		.params-table th,
		.params-table td {
			padding: 1rem;
			font-size: 0.9rem;
		}

		.error-codes-grid {
			grid-template-columns: 1fr;
		}

		.copy-notification {
			top: 1rem;
			padding: 0.8rem 1.5rem;
			font-size: 0.9rem;
		}
	}

</style>