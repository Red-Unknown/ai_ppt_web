## 6. 模块规范 (Modules)

### 6.1 模块职责划分 (Role Mapping)

基于赛题任务，后端代码划分为以下核心域 (Domain)：

| 模块目录 (`backend/app/services/`) | 对应职责 (Role) | 功能描述 |
| --- | --- | --- |
| **`parser/`** | **Role A (课件解析)** | PPT/PDF 提取、OCR、页面元素结构化。 |
| **`structure/`** | **Role B (结构引擎)** | 构建 CIR (Course Intermediate Representation)、知识图谱、节点树。 |
| **`script/`** | **Role C (智课生成)** | 生成讲稿、TTS 合成、数字人/视频合成。 |
| **`qa/`** | **Role D (问答互动)** | RAG 检索、上下文管理、多轮对话状态机。 |
| **`session/`** | **Role D (进度控制)** | 学习进度追踪、断点续接策略、理解度分析。 |
| **`integration/`** | **Role E (集成适配)** | 泛雅 API 适配、鉴权 (Auth)、外部接口防腐层。 |

### 6.2 目录结构规范 (Directory Layout)

严格遵守以下目录结构，严禁随意在根目录新建文件。

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
    │   ├── tests/          # 测试目录 (Refactored)
    │   │   ├── unit/       # 单元测试 (No External Deps)
    │   │   ├── integration/# 集成测试 (DB/API/External)
    │   │   ├── e2e/        # 端到端测试 (Full System)
    │   │   ├── conftest.py # Pytest Configuration
    │   │   └── pytest.ini  # Pytest Settings
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

qa系统目录结构

```text
backend/app/services/qa/
├── core/                   # 核心抽象与基类
│   ├── __init__.py
│   ├── agent_base.py       # Agent 抽象基类
│   └── events.py           # 事件定义 (Thought, Action 等)
├── agents/                 # 具体 Agent 实现
│   ├── __init__.py
│   ├── react.py            # ReActAgent (原 agent.py)
│   └── teacher.py          # TeacherAgent (如果存在)
├── tools/                  # 工具集 (原 skills/)
│   ├── __init__.py
│   ├── base.py             # BaseTool/BaseSkill
│   ├── retrieval.py        # LocalKnowledgeTool (原 local_rag_skill.py)
│   ├── web_search.py       # SearchTool
│   ├── calculator.py       # MathTool
│   └── manager.py          # ToolManager/SkillManager
├── retrieval/              # 检索子系统
│   ├── __init__.py
│   └── tree_retriever.py   # TreeStructureRetriever (原 retriever.py)
├── analysis/               # 理解与路由
│   ├── __init__.py
│   ├── intent.py           # QAAnalyzer (原 analyzer.py)
│   └── router.py           # DialogueRouter
├── service.py              # 服务入口 (保持不变，作为 Facade)
└── __init__.py
```

### 6.3 个人调试空间 (Sandbox Policy)

* **位置**：`sandbox/<user_name>/`
* **规则**：
  * `sandbox/` 目录下的内容（除 `.keep` 外）已被 `.gitignore` 忽略。
  * 每个人在此目录下建立自己的文件夹进行代码片段调试、临时脚本编写。
  * **严禁**在 `sandbox` 中引用 `backend` 内部的相对路径（应将 `project_root` 加入 PYTHONPATH 运行）。
  * 调试通过的代码必须迁移至 `backend/app/services` 并编写测试用例，**严禁**直接将 `sandbox` 代码作为生产代码提交。