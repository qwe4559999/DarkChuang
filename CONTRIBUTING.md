# 贡献指南

感谢您对化学问答机器人项目的关注！我们欢迎各种形式的贡献，包括但不限于：

- 🐛 报告错误
- 💡 提出新功能建议
- 📝 改进文档
- 🔧 提交代码修复
- ✨ 添加新功能
- 🧪 编写测试
- 🎨 改进用户界面

## 开始之前

在开始贡献之前，请：

1. 阅读我们的 [行为准则](#行为准则)
2. 查看 [现有的 Issues](https://github.com/your-repo/issues)
3. 搜索相关的 [Pull Requests](https://github.com/your-repo/pulls)
4. 阅读项目的 [README.md](README.md)

## 如何贡献

### 报告错误

如果您发现了错误，请：

1. 检查是否已有相关的 Issue
2. 如果没有，请创建新的 Issue
3. 使用错误报告模板
4. 提供详细的重现步骤
5. 包含系统信息和错误日志

**错误报告应包含：**
- 清晰的标题
- 详细的描述
- 重现步骤
- 预期行为
- 实际行为
- 系统环境信息
- 相关的错误日志或截图

### 提出功能建议

我们欢迎新功能的建议！请：

1. 检查是否已有相关的功能请求
2. 创建新的 Issue 并使用功能请求模板
3. 详细描述功能的用途和价值
4. 提供可能的实现方案

**功能请求应包含：**
- 功能的背景和动机
- 详细的功能描述
- 可能的实现方案
- 替代方案
- 对现有功能的影响

### 提交代码

#### 开发环境设置

1. **Fork 项目**
   ```bash
   # 在 GitHub 上 Fork 项目
   # 然后克隆您的 Fork
   git clone https://github.com/your-username/DarkChuang.git
   cd DarkChuang
   ```

2. **设置开发环境**
   ```bash
   # 运行安装脚本
   python scripts/install.py
   
   # 或手动安装
   # 后端
   cd backend
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # 开发依赖
   
   # 前端
   cd ../frontend
   npm install
   ```

3. **配置环境变量**
   ```bash
   cp .env.example .env
   # 编辑 .env 文件，设置必要的配置
   ```

4. **运行测试**
   ```bash
   python scripts/test.py
   ```

#### 开发流程

1. **创建分支**
   ```bash
   git checkout -b feature/your-feature-name
   # 或
   git checkout -b fix/your-bug-fix
   ```

2. **进行开发**
   - 遵循代码规范
   - 编写测试
   - 更新文档
   - 提交有意义的 commit 信息

3. **测试您的更改**
   ```bash
   # 运行所有测试
   python scripts/test.py
   
   # 运行特定测试
   cd backend
   pytest tests/test_specific.py
   
   # 前端测试
   cd frontend
   npm test
   ```

4. **提交更改**
   ```bash
   git add .
   git commit -m "feat: add new feature description"
   git push origin feature/your-feature-name
   ```

5. **创建 Pull Request**
   - 在 GitHub 上创建 Pull Request
   - 使用 PR 模板
   - 详细描述您的更改
   - 链接相关的 Issues

## 代码规范

### Python 代码规范

我们遵循 [PEP 8](https://www.python.org/dev/peps/pep-0008/) 规范：

- 使用 4 个空格缩进
- 行长度不超过 88 字符
- 使用有意义的变量和函数名
- 添加适当的注释和文档字符串

**代码格式化工具：**
```bash
# 安装开发工具
pip install black isort flake8 mypy

# 格式化代码
black backend/
isort backend/

# 检查代码质量
flake8 backend/
mypy backend/
```

### TypeScript/JavaScript 代码规范

- 使用 2 个空格缩进
- 使用 TypeScript 进行类型检查
- 遵循 ESLint 规则
- 使用有意义的组件和变量名

**代码格式化：**
```bash
cd frontend
npm run lint
npm run format
```

### Git Commit 规范

我们使用 [Conventional Commits](https://www.conventionalcommits.org/) 规范：

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

**类型：**
- `feat`: 新功能
- `fix`: 错误修复
- `docs`: 文档更新
- `style`: 代码格式化
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 构建过程或辅助工具的变动

**示例：**
```
feat(api): add image recognition endpoint

fix(frontend): resolve chat interface scrolling issue

docs: update installation guide

test(backend): add unit tests for RAG service
```

## 测试指南

### 后端测试

```bash
cd backend

# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/test_api.py

# 运行带覆盖率的测试
pytest --cov=app tests/

# 运行特定标记的测试
pytest -m "not slow"
```

### 前端测试

```bash
cd frontend

# 运行单元测试
npm test

# 运行端到端测试
npm run test:e2e

# 生成测试覆盖率报告
npm run test:coverage
```

### 测试编写指南

- 为新功能编写测试
- 确保测试覆盖率不降低
- 编写清晰的测试名称
- 使用适当的测试数据
- 模拟外部依赖

## 文档贡献

### 文档类型

- **用户文档**: 面向最终用户的使用指南
- **开发文档**: 面向开发者的技术文档
- **API 文档**: API 接口说明
- **代码注释**: 代码内的说明

### 文档规范

- 使用 Markdown 格式
- 保持简洁明了
- 提供实际的示例
- 及时更新过时的信息
- 支持中英文双语

### 生成文档

```bash
# 生成所有文档
python scripts/generate_docs.py

# 查看生成的文档
open docs/index.html
```

## Pull Request 指南

### PR 检查清单

在提交 PR 之前，请确保：

- [ ] 代码遵循项目的编码规范
- [ ] 所有测试都通过
- [ ] 添加了必要的测试
- [ ] 更新了相关文档
- [ ] Commit 信息遵循规范
- [ ] PR 描述清晰完整
- [ ] 解决了所有的 merge conflicts

### PR 模板

```markdown
## 更改类型
- [ ] 错误修复
- [ ] 新功能
- [ ] 文档更新
- [ ] 性能改进
- [ ] 代码重构
- [ ] 其他

## 描述
简要描述您的更改...

## 相关 Issue
关闭 #issue_number

## 测试
描述您如何测试这些更改...

## 截图（如适用）

## 检查清单
- [ ] 我的代码遵循项目的编码规范
- [ ] 我已经进行了自我审查
- [ ] 我已经添加了必要的注释
- [ ] 我已经更新了相关文档
- [ ] 我的更改不会产生新的警告
- [ ] 我已经添加了测试来证明我的修复是有效的或我的功能可以工作
- [ ] 新的和现有的单元测试都通过了
```

### 代码审查

所有的 PR 都需要经过代码审查：

- 至少需要一个维护者的批准
- 解决所有的审查意见
- 确保 CI/CD 检查通过
- 保持 PR 的大小合理（建议 < 500 行）

## 发布流程

### 版本号规范

我们使用 [语义化版本](https://semver.org/)：

- `MAJOR.MINOR.PATCH`
- `MAJOR`: 不兼容的 API 更改
- `MINOR`: 向后兼容的功能添加
- `PATCH`: 向后兼容的错误修复

### 发布步骤

1. 更新版本号
2. 更新 CHANGELOG.md
3. 创建 release tag
4. 构建和发布 Docker 镜像
5. 更新文档

## 社区

### 沟通渠道

- **GitHub Issues**: 错误报告和功能请求
- **GitHub Discussions**: 一般讨论和问答
- **Email**: 私人或敏感问题

### 获得帮助

如果您需要帮助：

1. 查看 [FAQ](docs/user/faq.md)
2. 搜索现有的 Issues 和 Discussions
3. 创建新的 Discussion 或 Issue
4. 联系维护者

## 行为准则

### 我们的承诺

为了营造一个开放和友好的环境，我们承诺：

- 使用友好和包容的语言
- 尊重不同的观点和经验
- 优雅地接受建设性批评
- 关注对社区最有利的事情
- 对其他社区成员表示同理心

### 不可接受的行为

- 使用性化的语言或图像
- 人身攻击或政治攻击
- 公开或私下的骚扰
- 未经许可发布他人的私人信息
- 其他在专业环境中不当的行为

### 执行

如果您遇到不当行为，请联系项目维护者。所有投诉都会被审查和调查。

## 致谢

感谢所有为这个项目做出贡献的人！

### 贡献者

- 查看 [贡献者列表](https://github.com/your-repo/graphs/contributors)

### 特别感谢

- 感谢所有提供反馈和建议的用户
- 感谢开源社区提供的优秀工具和库
- 感谢所有参与测试和文档改进的志愿者

---

再次感谢您的贡献！如果您有任何问题，请随时联系我们。