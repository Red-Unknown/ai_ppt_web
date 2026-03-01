# QA 服务重构计划

## 1. 目标
按照 ReAct 架构重新组织 `backend/app/services/qa` 目录，使代码结构更清晰、职责更单一，便于维护和扩展。

## 2. 当前结构分析
当前目录 `backend/app/services/qa` 包含以下文件：
- `agent.py`: ReAct Agent 核心逻辑。
- `analyzer.py`: 意图分析器。
- `math_solver.py`: 数学求解器（旧版？）。
- `retriever.py`: 检索器实现。
- `router.py`: 对话路由器。
- `service.py`: 服务入口 (Facade)。
- `skills/`: 工具/技能目录。
  - `base.py`
  - `local_rag_skill.py`
  - `manager.py`
  - `math_skill.py`
  - `search_skill.py`

## 3. 拟定新结构

建议采用 **分层 + 功能模块** 的方式进行重构：

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

## 4. 迁移步骤

1.  **创建目录结构**:
    - `core/`, `agents/`, `tools/`, `retrieval/`, `analysis/`
2.  **移动文件**:
    - `agent.py` -> `agents/react.py`
    - `analyzer.py` -> `analysis/intent.py`
    - `router.py` -> `analysis/router.py`
    - `retriever.py` -> `retrieval/tree_retriever.py`
    - `skills/*.py` -> `tools/*.py`
3.  **重构导入**:
    - 更新 `service.py` 中的导入路径。
    - 更新各模块内部的相互引用。
    - 确保 `backend.app.api.v1.chat` 中的引用（主要是 `QAService`）不受影响（因为 `service.py` 位置不变）。
4.  **清理废弃代码**:
    - 检查 `math_solver.py` 是否已被 `tools/calculator.py` 取代，如果是则归档或删除。

## 5. 预期收益
- **高内聚**: 相关功能的代码物理上聚集在一起（如所有 Agent 在 `agents/`，所有工具在 `tools/`）。
- **低耦合**: 通过明确的目录边界减少随意引用。
- **可扩展性**: 新增工具或 Agent 只需在对应目录添加文件，无需修改现有大文件。
