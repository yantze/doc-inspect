# MD 语义检索知识库

基于本地 Embedding 模型和向量数据库的 Markdown 文档语义检索与 AI 问答系统。

## 🏗️ 架构设计

```
┌─────────────┐
│  MD 文档    │
└──────┬──────┘
       │ 加载
       ▼
┌─────────────┐      ┌──────────────┐
│  文本分割    │─────▶│  Embedding   │
│  (Chunks)   │      │  (m3e-base)  │
└─────────────┘      └──────┬───────┘
                            │ 向量化
                            ▼
                     ┌──────────────┐
                     │ Milvus Lite  │
                     │  向量数据库   │
                     └──────┬───────┘
                            │
       ┌────────────────────┴────────────────────┐
       │                                         │
       ▼                                         ▼
┌─────────────┐                          ┌─────────────┐
│  语义检索    │                          │  RAG 问答   │
│   (query)   │                          │   (ask)     │
└─────────────┘                          └──────┬──────┘
                                                │
                                                ▼
                                         ┌─────────────┐
                                         │  AI 服务    │
                                         │ (OpenAI兼容)│
                                         └─────────────┘
```

**核心组件**：
- **Embedding**: m3e-base（中英文双语模型，768维）
- **向量存储**: Milvus Lite（本地轻量级向量数据库）
- **AI 服务**: OpenAI 兼容接口（支持各种模型）

## 📦 安装

### 1. 克隆项目
```bash
git clone <your-repo-url>
cd project-doc-insight
```

### 2. 创建虚拟环境
```bash
# 使用 uv（推荐）
uv venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# 或使用 Python 内置 venv
python -m venv .venv
source .venv/bin/activate
```

### 3. 安装依赖
```bash
# 使用 uv（推荐，速度快）
uv pip install -r requirements.txt

# 或使用 pip
pip install -r requirements.txt
```

### 4. 配置 Hugging Face 镜像（国内用户必须）
```bash
export HF_ENDPOINT=https://hf-mirror.com
```

### 5. 配置 AI 服务（可选）
编辑 `config.py`：
```python
OPENAI_BASE_URL = "https://api.openai.com/v1"  # API 地址
OPENAI_API_KEY = "your-api-key-here"           # API 密钥
OPENAI_MODEL = "gpt-3.5-turbo"                 # 模型名称
```

或设置环境变量：
```bash
export OPENAI_BASE_URL="https://api.openai.com/v1"
export OPENAI_API_KEY="your-api-key"
export OPENAI_MODEL="gpt-4"
```

## 🚀 使用流程

### 1️⃣ 建立索引
将你的 Markdown 文档放入 `docs/` 目录，然后建立索引：

```bash
python main.py index --docs-dir ./docs
```

输出示例：
```
📂 扫描目录: ./docs
   找到 3 个 md 文件, 共 15234 字符

✂️  分割文档...
   生成 110 个文本块

🔢 生成向量...
   向量维度: 768

💾 存储到向量数据库...
   插入 110 条记录

✅ 索引建立成功!
```

### 2️⃣ 语义检索
直接检索知识库，返回相关文档片段：

```bash
python main.py query
```

示例交互：
```
请输入问题: 如何使用 Docker
📚 找到 5 个相关结果：

[1] 相似度: 0.85 | 来源: docker-guide.md
    Docker 是一个开源的容器化平台...
```

### 3️⃣ AI 问答（RAG）
基于知识库内容，让 AI 生成答案：

```bash
python main.py ask
```

也可以直接指定 API 配置：
```bash
python main.py ask \
  --base-url https://api.example.com/v1 \
  --api-key YOUR_KEY \
  --model gpt-4 \
  --top-k 5
```

示例交互：
```
请输入问题: Docker 的主要优势是什么？

🤖 AI 回答：
╭─────────────────────────────╮
│ 基于参考资料，Docker 的主要  │
│ 优势包括：                  │
│ 1. 轻量级容器化...          │
│ 2. 环境一致性...            │
│ ...                         │
╰─────────────────────────────╯

Token 使用: 输入 256 | 输出 512 | 总计 768

📚 参考文档 (5 个)：
[1] 相似度: 0.85 | 来源: docker-guide.md
    Docker 容器相比虚拟机更加轻量...
```

### 4️⃣ 查看统计
```bash
python main.py stats
```

## 📁 项目结构

```
.
├── src/
│   ├── embedder.py      # Embedding 模型封装
│   ├── vector_store.py  # Milvus 向量数据库
│   ├── loader.py        # Markdown 文档加载
│   ├── splitter.py      # 文本分割
│   ├── ai_service.py    # AI 服务集成
│   └── qa_engine.py     # 问答引擎核心
├── docs/                # 存放 Markdown 文档
├── data/                # 向量数据库文件
├── config.py            # 配置文件
├── main.py              # 命令行入口
└── requirements.txt     # 依赖列表
```

## ⚙️ 配置说明

编辑 `config.py` 可以调整以下参数：

```python
# Embedding 模型
EMBEDDING_MODEL = "moka-ai/m3e-base"  # 中英文模型

# 文本分割
CHUNK_SIZE = 500        # 分块大小（字符）
CHUNK_OVERLAP = 50      # 分块重叠（字符）

# 检索配置
TOP_K = 5               # 返回结果数量

# AI 服务
OPENAI_BASE_URL = "https://api.openai.com/v1"
OPENAI_API_KEY = "your-api-key"
OPENAI_MODEL = "gpt-3.5-turbo"
OPENAI_MAX_TOKENS = 100000  # 最大回复长度
```

## 🔧 命令参考

```bash
# 建立索引
python main.py index --docs-dir ./docs

# 语义检索
python main.py query [--top-k 5]

# AI 问答
python main.py ask [--top-k 5] [--base-url URL] [--api-key KEY] [--model MODEL]

# 查看统计
python main.py stats

# 查看帮助
python main.py --help
```

## 📝 注意事项

1. **首次运行**会自动下载 m3e-base 模型（约 400MB），请确保网络畅通
2. **国内用户**务必配置 `HF_ENDPOINT` 镜像，否则模型下载会失败
3. **AI 问答功能**需要配置有效的 API 密钥才能使用
4. 向量数据库文件存储在 `./data/milvus.db`，可以安全删除以重建索引

## 📄 License

MIT
