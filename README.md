# ETrace

基于AI的网络用户活动轨迹追踪平台，提供多平台用户档案、活动数据和行为模式的智能提取与可视化展示。

## 🌐 网络用户活动轨迹追踪

支持平台：
- [x] GitHub - 用户档案、仓库信息、活动事件
- [ ] 微博 - 用户动态、关注关系、互动数据
- [ ] 小红书 - 用户笔记、点赞收藏
- [ ] 知乎 - 问答活动、专栏文章、点赞评论
- [ ] 更多平台持续开发中...

## ✨ 特性

- 🤖 **AI驱动的数据提取** - 使用Crawl4AI进行智能网页内容抽取
- 🌐 **多平台支持** - 支持GitHub、微博、小红书、知乎等主流社交平台
- 📊 **API集成** - 获取用户事件、动态内容等实时数据
- 🔍 **活动轨迹分析** - 跨平台用户行为模式识别和分析
- 🎨 **现代化前端界面** - 基于Next.js 15和React 19构建
- 🔄 **RESTful API** - 完整的后端API服务
- 📱 **响应式设计** - 支持多设备访问
- 🏗️ **解耦架构** - 清晰的Schema层和Model层分离设计

## 🛠️ 技术栈

### 后端
- **Python 3.11+** - 主要开发语言
- **FastAPI** - 高性能Web框架
- **Crawl4AI** - AI驱动的网页爬取工具
- **Pydantic** - 数据验证和序列化
- **Uvicorn** - ASGI服务器
- **uv** - 现代Python包管理器

### 前端
- **Next.js 15** - React全栈框架
- **React 19** - UI库
- **TypeScript** - 类型安全
- **Tailwind CSS 4** - 样式框架
- **date-fns** - 日期处理

## 📋 功能模块

### 数据提取
- **用户档案爬取** - 跨平台提取用户详细信息和社交关系
- **内容信息获取** - 获取用户发布的内容、互动数据等
- **活动事件跟踪** - 实时获取用户在各平台的活动轨迹
- **行为模式分析** - 跨平台用户行为模式识别和关联分析
- **时间线分析** - 多平台用户活动时间线的可视化展示

### 平台特色功能
- **GitHub** - 代码仓库、提交记录、协作网络分析
- **微博** - 社交互动、话题参与、影响力分析（开发中）
- **小红书** - 内容偏好、消费习惯、兴趣标签（开发中）
- **知乎** - 知识图谱、专业领域、问答质量（开发中）

### API端点
- `GET /` - 服务状态
- `GET /health` - 健康检查
- `POST /github/profile` - 获取用户档案
- `POST /github/repositories` - 获取用户仓库
- `GET /github/events/{username}` - 获取用户事件
- `GET /github/repo-events/{owner}/{repo}` - 获取仓库事件

## 🚀 快速开始

### 环境要求
- Python 3.11+
- Node.js 18+
- Git
- uv (推荐的Python包管理器)

### 1. 克隆项目
```bash
git clone <repository-url>
cd etrace
```

### 2. 后端设置

#### 安装 uv (如果尚未安装)
```bash
# macOS 和 Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# 或者使用包管理器
# macOS: brew install uv
# Ubuntu: sudo snap install uv
```

#### 项目依赖安装
```bash
# 使用 uv 同步依赖和创建虚拟环境
uv sync

# 激活虚拟环境
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate     # Windows

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，设置必要的配置
```

### 3. 前端设置
```bash
cd frontend
npm install
```

### 4. 启动服务

**启动后端API服务：**
```bash
# 方式1：直接运行
python api.py

# 方式2：使用uvicorn
uvicorn api:app --host 0.0.0.0 --port 8000 --reload

# 方式3：使用uv运行
uv run python api.py
```

**启动前端开发服务器：**
```bash
cd frontend
npm run dev
```

访问 `http://localhost:3000` 查看前端界面，API文档可在 `http://localhost:8000/docs` 访问。

## 📁 项目结构

```
etrace/
├── src/                    # 后端源码
│   ├── config/            # 配置管理
│   ├── model/             # 数据模型
│   │   └── github/        # GitHub相关模型
│   ├── service/           # 业务服务
│   ├── strategy/          # 爬取策略
│   └── util/              # 工具函数
├── frontend/              # 前端应用
│   ├── src/
│   │   ├── app/           # Next.js应用目录
│   │   ├── components/    # React组件
│   │   ├── lib/           # 工具库
│   │   └── types/         # TypeScript类型
│   └── package.json
├── output/                # 数据输出目录
├── test/                  # 测试文件
├── api.py                # API服务入口
├── main.py               # 命令行工具
├── pyproject.toml        # Python项目配置
└── uv.lock               # uv依赖锁定文件
```

## 🔧 配置

### 环境变量
创建 `.env` 文件：
```bash
# 基础配置
LOG_LEVEL=INFO
OUTPUT_DIR=./output

# GitHub API Token (可选，提高API限制)
GITHUB_TOKEN=your_github_token_here

# 其他配置...
```

### 架构设计
项目采用解耦架构设计，详见 [MODEL_ARCHITECTURE.md](MODEL_ARCHITECTURE.md)：
- **Schema层** - 专注数据抽取
- **Model层** - 专注领域逻辑
- **转换层** - 数据映射

## 📊 使用示例

### 命令行使用
```python
from main import ETraceApp
import asyncio

async def example():
    app = ETraceApp()
    
    # 获取用户事件
    events = await app.get_github_events("username", per_page=10)
    
    # 获取仓库列表
    repos = await app.get_github_repositories("username")
    
    # 获取仓库详情
    repo_details = await app.get_github_repository_details("owner", "repo")

asyncio.run(example())
```

### API调用示例
```bash
# 获取用户事件
curl "http://localhost:8000/github/events/username?per_page=10"

# 获取仓库事件
curl "http://localhost:8000/github/repo-events/owner/repo?per_page=5"
```

## 🧪 开发

### 依赖管理
```bash
# 添加新依赖
uv add package_name

# 添加开发依赖
uv add --dev package_name

# 移除依赖
uv remove package_name

# 更新依赖
uv sync --upgrade
```

### 运行测试
```bash
# 后端测试
uv run python -m pytest test/

# 前端测试
cd frontend
npm test
```

### 代码格式化
```bash
# 前端
cd frontend
npm run lint

# 后端 (如果配置了格式化工具)
uv run ruff format .
uv run ruff check .
```

## 📄 许可证

[MIT License](LICENSE)

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📞 支持

如有问题，请：
1. 查看 [Issues](../../issues)
2. 创建新的 Issue
3. 联系维护者

---

**注意**: 请确保遵守GitHub的使用条款和API限制。建议配置GitHub Token以提高API调用限制。

## 🔗 相关链接

- [uv 文档](https://docs.astral.sh/uv/)
- [FastAPI 文档](https://fastapi.tiangolo.com/)
- [Next.js 文档](https://nextjs.org/docs)
- [Crawl4AI 文档](https://crawl4ai.com/mkdocs/)
