# 🌟 星星对话（StarChat）

**面向自闭症儿童的友好对话 AI 助手**

> 我是"星星"，一个耐心、友善的对话小伙伴。  
> 我会用简单的话和你聊天，陪你玩游戏，帮你认识情绪。

---

## 📋 项目简介

本项目是一个面向自闭症谱系障碍（ASD）儿童的多轮对话 AI 原型系统，旨在探索如何利用大语言模型为特殊儿童提供安全、有趣、有教育意义的对话陪伴。

### 设计动机

自闭症儿童在社交沟通方面面临独特挑战：
- 语言理解偏向字面，难以理解比喻、讽刺等抽象表达
- 对话轮替困难，可能固着于特定话题
- 情绪识别和表达需要额外支持

本系统针对这些特点，在 **System Prompt**、**情绪感知**、**知识库增强** 三个层面进行了专门设计，参考了 ABA（应用行为分析）干预策略和 ASD 儿童沟通研究。

---

## ✨ 核心特点

| 特点 | 说明 |
|------|------|
| 🗣️ **儿童友好对话** | 语言简短清晰，正向鼓励为主，避免抽象表达 |
| 🎭 **情绪感知** | 实时检测用户情绪，自动调整回应策略（共情优先） |
| 📚 **RAG 知识增强** | 基于特教知识库检索，对话内容有专业依据 |
| 🔄 **模型无关设计** | 支持 DeepSeek / OpenAI / Qwen 等任意 OpenAI 兼容模型 |
| 🐳 **Docker 一键部署** | 开箱即用，方便分享和演示 |

---

## 🏗️ 系统架构

```
用户输入（文本）
    │
    ▼
┌─────────────────────────────────┐
│  Chainlit Web 界面               │
│  ├─ 对话窗口                     │
│  ├─ 话题选择按钮                  │
│  └─ 系统状态展示                  │
└──────────┬──────────────────────┘
           │
           ▼
┌─────────────────────────────────┐
│  LangChain 对话链                │
│  ├─ 情绪检测模块（关键词匹配）     │  ← 感知层
│  ├─ RAG 检索模块（FAISS）         │  ← 知识层
│  ├─ System Prompt（ABA 策略）     │  ← 策略层
│  └─ 对话记忆（滑动窗口）          │  ← 记忆层
└──────────┬──────────────────────┘
           │
           ▼
┌─────────────────────────────────┐
│  LLM（DeepSeek / OpenAI / Qwen） │
└─────────────────────────────────┘
```

---

## 🚀 快速开始

### 方式一：本地运行

```bash
# 1. 克隆项目
git clone https://github.com/yijingsun/autism-chat.git
cd autism-chat

# 2. 创建虚拟环境（需要 Python 3.10）
python3.10 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置 API Key
cp .env.example .env
# 编辑 .env，填入你的 LLM API Key

# 5.（可选）构建知识库
python build_knowledge_base.py

# 6. 启动应用
chainlit run app.py
# 浏览器打开 http://localhost:8000
```

### 方式二：Docker 运行

```bash
# 1. 配置 API Key
cp .env.example .env
# 编辑 .env，填入你的 LLM API Key

# 2. 构建并启动
docker compose up -d --build

# 浏览器打开 http://localhost:8000
```

---

## ⚙️ 配置说明

### LLM 模型切换

在 `.env` 文件中修改以下配置即可切换模型：

**DeepSeek（默认）：**
```env
LLM_API_KEY=sk-xxx
LLM_BASE_URL=https://api.deepseek.com
LLM_MODEL_NAME=deepseek-chat
```

**OpenAI：**
```env
LLM_API_KEY=sk-xxx
LLM_BASE_URL=https://api.openai.com/v1
LLM_MODEL_NAME=gpt-4o-mini
```

**通义千问（Qwen）：**
```env
LLM_API_KEY=xxx
LLM_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
LLM_MODEL_NAME=qwen-turbo
```

### 知识库构建

将特教相关资料（`.txt` 格式）放入 `data/knowledge/` 目录，然后运行：

```bash
python build_knowledge_base.py
```

系统会自动将文档切分、向量化，存入 FAISS 索引。

> 💡 知识库为可选功能。未构建时，系统仍可正常对话，仅不启用 RAG 检索。
>
> 🤗 Embedding 使用本地 HuggingFace 模型（`all-MiniLM-L6-v2`），无需额外 API Key。首次运行会自动下载模型（约 90MB）。

---

## 📁 项目结构

```
autism-chat/
├── app.py                     # Chainlit 主界面
├── chain.py                   # LangChain 对话链组装
├── config.py                  # 配置中心
├── prompts.py                 # System Prompt 设计
├── emotion.py                 # 情绪关键词检测
├── rag.py                     # RAG 知识库检索
├── build_knowledge_base.py    # FAISS 索引构建脚本
├── requirements.txt           # Python 依赖
├── .env.example               # 环境变量模板
├── Dockerfile                 # Docker 配置
├── docker-compose.yml         # Docker Compose 配置
├── .chainlit/
│   └── config.toml            # Chainlit UI 配置
├── public/
│   ├── custom.css             # 自定义样式
│   └── loading.js             # 加载遮罩控制
└── data/
    ├── knowledge/             # 知识库文档目录
    │   ├── aba_intervention.txt
    │   └── autism_communication.txt
    └── faiss_index/           # FAISS 向量索引（构建后生成）
```

---

## 🧠 设计理念

### System Prompt 设计

System Prompt 是本项目的核心，体现了对自闭症儿童沟通方式的理解：

1. **简短清晰**：句子简短易懂，避免抽象表达，每次回复 3-5 句保证内容丰富有温度
2. **一次一问**：不给认知负担
3. **正向鼓励**：多用"你真棒""你好厉害"
4. **情绪共情优先**：检测到负面情绪时，先安慰再引导
5. **话题结构化**：预设打招呼、认颜色、数数等场景

### 情绪感知

通过关键词匹配实时检测用户情绪倾向：
- 检测到负面情绪 → 切换为共情模式，先安慰再引导
- 检测到正面情绪 → 保持鼓励，继续愉快对话
- 中性情绪 → 正常对话流程

### 相关前沿研究

本项目的对话策略设计融合了应用行为分析（ABA）原则及自闭症谱系障碍（ASD）儿童的沟通特点等特殊教育实践知识。为进一步拓宽视野，以下列举该领域近期的三项代表性研究工作，供延伸阅读：

- **ASD‑iLLM (EMNLP 2025 Findings)**：构建了首个中文自闭症临床对话干预数据集（ASD‑iLLM‑8k），并基于 ABA 原则对开源大语言模型进行微调，实现了自动化对话干预。该工作验证了 LLM 在结构化行为干预场景中的可行性与有效性。  
  [ACL Anthology](https://aclanthology.org/2025.findings-emnlp.427/) | [代码](https://github.com/Shuzhong-Lai/ASD-iLLM)

- **AACessTalk (CHI 2025 Best Paper)**：设计了一款平板电脑上的 AI 辅助沟通系统，通过动态情境引导与个性化词汇卡推荐，帮助低语言能力的自闭症儿童与家长进行更流畅、有意义的互动。该成果荣获人机交互顶会 CHI 2025 最佳论文奖。  
  [项目官网](https://naver-ai.github.io/aacesstalk) | [代码](https://github.com/naver-ai/aacesstalk-monorepo)

- **ASD‑Chat (arXiv 2024 / IEEE Xplore)**：结合 VB‑MAPP（语言行为里程碑评估与安置程序）评估框架与 ChatGPT 等大语言模型，设计了针对自闭症儿童的对话干预范式与提示词策略，为个性化社交技能训练提供了新的技术路径。  
  [arXiv](https://arxiv.org/abs/2409.01867) | [IEEE](https://ieeexplore.ieee.org/document/11227794)

---

## 🛠️ 技术栈

| 组件 | 技术选型 |
|------|----------|
| LLM 框架 | LangChain |
| 向量数据库 | FAISS |
| Embedding 模型 | HuggingFace `all-MiniLM-L6-v2`（本地） |
| Web 界面 | Chainlit |
| LLM | DeepSeek API（可切换） |
| 部署 | Docker |

---

## 📄 License

MIT License

---

## 📮 联系方式

如有问题或建议，欢迎联系：
- Email:
- GitHub Issues
