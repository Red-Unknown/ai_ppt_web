---
alwaysApply: false
description: 涉及技术架构与模块规范
---
## 6. 技术架构与模块规范 (Architecture & Modules)

> **架构选型**：**模块化单体 (Modular Monolith) + 前后端分离**
> 鉴于 5 人团队规模及单服务器部署需求，不采用微服务架构，但后端代码必须在逻辑上严格解耦。

### 6.1 核心技术栈
- **前端 (Web/Mobile)**: Vue 3 + Vite + TailwindCSS (适配泛雅/学习通嵌入)。
- **后端 (API)**: Python FastAPI (高性能，原生支持异步)。
- **异步任务队列**: Celery + Redis (处理耗时的 PPT 解析、视频生成)。
- **数据存储**: PostgreSQL (业务数据) + Milvus/Chroma (向量检索) + MinIO/本地文件系统 (文件存储)。
- **AI 引擎**: LangChain / LlamaIndex (RAG 编排)。

### 6.2 模块职责划分 (Role Mapping)
基于赛题任务，后端代码划分为以下核心域 (Domain)：

| 模块目录 (`backend/app/services/`) | 对应职责 (Role) | 功能描述 |
| :--- | :--- | :--- |
| **`parser/`** | **Role A (课件解析)** | PPT/PDF 提取、OCR、页面元素结构化。 |
| **`structure/`** | **Role B (结构引擎)** | 构建 CIR (Course Intermediate Representation)、知识图谱、节点树。 |
| **`script/`** | **Role C (智课生成)** | 生成讲稿、TTS 合成、数字人/视频合成。 |
| **`qa/`** | **Role D (问答互动)** | RAG 检索、上下文管理、多轮对话状态机。 |
| **`session/`** | **Role D (进度控制)** | 学习进度追踪、断点续接策略、理解度分析。 |
| **`integration/`** | **Role E (集成适配)** | 泛雅 API 适配、鉴权 (Auth)、外部接口防腐层。 |

### 6.3 目录结构规范 (Directory Layout)
严格遵守以下目录结构，严禁随意在根目录新建文件。

```text
project_root/
├── .gitignore
├── README.md
├── TEAM_GUIDELINES.md  # 本规范文档
├── environment.yml     # 统一环境
├── backend/            # 后端工程 (FastAPI)
│   ├── app/
│   │   ├── api/        # 路由层 (Endpoints Only, No Business Logic)
│   │   │   ├── v1/
│   │   │   │   ├── parser.py
│   │   │   │   ├── chat.py
│   │   │   │   └── ...
│   │   ├── core/       # 全局配置, Logging, Security
│   │   ├── models/     # 数据库 ORM 模型 (SQLAlchemy)
│   │   ├── schemas/    # Pydantic 数据模型 (API I/O)
│   │   ├── services/   # 核心业务逻辑 (见 6.2)
│   │   │   ├── parser/
│   │   │   ├── qa/
│   │   │   └── ...
│   │   └── workers/    # Celery 任务定义
│   ├── tests/          # 单元测试 & 集成测试
│   ├── main.py         # 启动入口
│   └── alembic/        # 数据库迁移脚本
├── frontend/           # 前端工程 (Vue3)
│   ├── src/
│   │   ├── api/        # Axios 封装
│   │   ├── components/ # 通用组件
│   │   ├── views/      # 页面 (Teacher/Student)
│   │   └── ...
├── fixtures/           # 冻结的测试数据 (见 2.1)
├── docs/               # 接口文档、架构图
├── scripts/            # 自动化脚本 (bootstrap, deploy)
└── sandbox/            # 【新增】个人调试空间
    ├── .keep           # 占位文件
    ├── user_zhangsan/  # 张三的个人实验代码 (git ignored)
    └── user_lisi/      # 李四的个人实验代码 (git ignored)
```

### 6.4 个人调试空间 (Sandbox Policy)
- **位置**：`sandbox/<user_name>/`
- **规则**：
    - `sandbox/` 目录下的内容（除 `.keep` 外）已被 `.gitignore` 忽略。
    - 每个人在此目录下建立自己的文件夹进行代码片段调试、临时脚本编写。
    - **严禁**在 `sandbox` 中引用 `backend` 内部的相对路径（应将 `project_root` 加入 PYTHONPATH 运行）。
    - 调试通过的代码必须迁移至 `backend/app/services` 并编写测试用例，**严禁**直接将 `sandbox` 代码作为生产代码提交。
