# 团队协作项目规范 (Team Collaboration Guidelines)

> **核心原则**：
> 1. **一切皆可复现**：环境、数据、代码行为在任何机器上必须一致。
> 2. **显式优于隐式**：依赖版本、数据来源、变更原因必须明确记录。
> 3. **自动化优先**：能用脚本解决的规范，绝不依赖人工记忆。

---

## 1. 代码运行环境 (Environment Governance)

### 1.1 单一 Conda 虚拟环境策略

- **唯一性原则**：项目所有活动（本地调试、模型训练、评估、推理服务、CI、部署前检查）必须在 **同一 Conda 虚拟环境** 中完成。
- **禁止私自创建**：禁止因“版本冲突”“依赖缺失”等理由私自新建额外 Conda 环境或 venv。
    - 需要新增/升级依赖时，必须按 1.2 中的流程修改统一环境。
    - 如需做一次性实验，可在本地临时环境中验证，但实验结果进入主仓库前，必须回写到统一 Conda 环境并通过 CI。
- **命名规范**：环境名称在 `environment.yml` 中统一定义，禁止使用未记录在仓库中的环境名称。
- **运行约束**：禁止在 Conda 环境外直接运行项目相关脚本或服务。

### 1.2 环境生命周期管理

#### 1.2.1 项目初始化阶段
目标：新成员或新机器在 **一次命令** 内获得完全一致的开发环境。

- **自动化脚本**：使用 `scripts/bootstrap.sh` (Linux) 或 `scripts/bootstrap.bat` (Windows)。
    - 自动检测 `environment.yml`。
    - 检查环境是否存在：
        - 若存在：校验一致性。
        - 若不存在：执行 `conda env create -f environment.yml`。
    - 记录日志至 `logs/env_bootstrap.log`（包含时间戳、触发人、yml哈希值、操作结果）。
- **完成判定**：
    - Conda 环境可被正常调用。
    - Python 版本与 `requirements-lock.txt` 一致。

#### 1.2.2 日常开发阶段
目标：变更可追溯、可复现。

- **依赖变更流程**：
    1. 激活统一环境。
    2. `conda install` 或 `pip install`。
    3. 导出环境：`conda env export --no-builds > environment.yml`。
    4. 生成锁文件：`pip freeze --require-virtualenv > requirements-lock.txt`。
    5. 本地运行完整测试。
- **PR 提交要求**：任何依赖变更必须同时包含更新后的 `environment.yml` 和 `requirements-lock.txt`。
- **CI 检查**：CI 启动时校验环境定义与实际环境的一致性，不一致直接失败。

#### 1.2.3 环境迁移 / 灾难恢复
- **触发条件**：仅在环境彻底损坏或上游依赖不可逆变更时允许重建。
- **恢复流程**：
    1. 记录错误日志。
    2. 重建环境：`conda env create -f environment.yml -n <new_env_name>`。
    3. 验证可用性。
    4. 重新冻结并更新文档（记录迁移原因、旧环境备份路径）。

### 1.3 版本可追溯与锁定

- **`environment.yml`**：显式记录 Python 精确版本（如 `3.10.12=h955ad1f_0`），固定关键依赖版本。
- **`requirements-lock.txt`**：锁定 pip 依赖，建议启用哈希校验。
- **跨平台兼容性**：
    - 项目需在 Windows 和 Linux 双端运行。
    - `environment.yml` 中应避免仅限特定 OS 的二进制包（或使用 selector 区分）。
    - 路径处理必须使用 `os.path.join` 或 `pathlib`，严禁硬编码 `\` 或 `/`。

---

## 2. 数据规范 (Data Governance)

### 2.1 联调测试数据集冻结策略 (fixtures/)

- **目录职责**：`fixtures/` 仅用于前后端联调与 E2E 测试。
- **冻结策略**：
    - 初始版本由脚本生成，禁止手工编辑大文件。
    - 生成后计算 MD5 和行数，写入 `fixtures/README.md`。
    - 未经审批禁止删除或覆盖已冻结文件。

### 2.2 数据 schema 变更与备份流程

当 Schema 变更导致数据结构变化时：
1. **修改脚本**：在独立分支修改数据生成脚本。
2. **自动备份**：运行 `scripts/data_freeze.sh` 将旧数据备份至 `fixtures/archive/<YYYYMMDD>/<hash>/`。
3. **重新冻结**：生成新数据，更新 `fixtures/README.md` 中的校验信息。

### 2.3 数据安全
- **最小权限**：仅包含联调所需字段。
- **脱敏要求**：严禁包含真实用户隐私数据。

---

## 3. Git 拉取与提交规范 (Git Workflow)

### 3.1 提交粒度 (Commit Granularity)
> **核心规则**：**File-Level Commit (文件级粒度)**

- **原则**：一个 Commit 理想情况下只包含**一个文件**的修改，或者**一组强耦合文件**（如：修改了接口定义 `api.py` 及其对应的测试文件 `test_api.py`）的修改。
- **禁止行为**：
    - 禁止 `git add .` 后直接提交。
    - 禁止在一个 Commit 中混合包含“修复 Bug A”和“开发 Feature B”的代码。
    - 禁止在一个 Commit 中混合包含“代码逻辑修改”和“大规模格式化/重命名”。
- **操作建议**：
    - 使用 `git add <file_path>` 逐个添加文件。
    - 使用 `git add -p` (patch mode) 仅提交文件中的特定代码块（如果一个文件里改了两个不相关的功能）。

### 3.2 提交信息规范 (Commit Message)
采用 **Conventional Commits** 标准，格式：`<type>(<scope>): <subject>`

- **Type（类型）**：
    - `feat`: 新功能
    - `fix`: 修复 Bug
    - `docs`: 仅文档变更
    - `style`: 代码格式调整（不影响逻辑，如空格、分号）
    - `refactor`: 代码重构（无新功能或 Bug 修复）
    - `perf`: 性能优化
    - `test`: 添加或修改测试
    - `chore`: 构建过程或辅助工具变动（如 environment.yml 更新）
- **Scope（范围）**：文件名或模块名，如 `(auth)`, `(parser)`.
- **Subject（简述）**：简短描述，动词开头，英文或中文统一。

### 3.3 分支管理
- `main`: 主分支，保持随时可部署/演示状态。
- `dev`: 开发主分支。
- `feat/<feature-name>`: 功能开发分支。
- `fix/<bug-name>`: 修复分支。

---

## 4. 文件与命名规范 (File & Naming Convention)

### 4.1 命名规范
- **文件与目录**：
    - 使用 **全小写 + 下划线** (`snake_case`)。
    - 示例：`course_parser.py`, `utils/image_processing.py`。
- **Python 代码命名**：
    - **变量/函数**：`snake_case`。
    - **类名**：`PascalCase`。
    - **常量**：`UPPER_CASE`。

---

## 5. 代码风格规范 (Code Style)

### 5.1 Python 风格
- **标准**：遵循 **PEP 8**。
- **强制工具**：`Black` (格式化), `isort` (导入排序), `Flake8` (静态检查)。
- **类型提示**：关键业务逻辑必须包含 Type Hints。

### 5.2 错误处理
- **禁止裸露的 except**：严禁使用 `except:`。
- **日志**：异常必须记录日志（含堆栈）。

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

---

## 7. API 与接口设计规范 (API Design)

### 7.1 异步任务模式 (Async Task Pattern)
针对赛题中“课件解析耗时 ≤ 2分钟”的要求，相关接口必须设计为**异步非阻塞**。

- **提交任务接口**：
    - `POST /api/v1/parser/upload`
    - **Return**: `{ "task_id": "uuid", "status": "pending" }` (HTTP 202 Accepted)
- **查询状态接口**：
    - `GET /api/v1/parser/tasks/{task_id}`
    - **Return**: `{ "status": "processing", "progress": 45, "result": null }`
- **获取结果接口**：
    - 当状态为 `completed` 时，`result` 字段返回 CIR JSON 数据的 URL 或 ID。

### 7.2 接口定义标准
- **URL 风格**：RESTful, 名词复数 (e.g., `/courses/{id}/chapters`).
- **数据格式**：Request/Response Body 必须使用 JSON。
- **错误响应**：
    ```json
    {
      "code": 400,
      "message": "Invalid file format",
      "data": null
    }
    ```
- **文档优先**：修改接口前，必须先更新 OpenAPI (Swagger) 定义或与前端协商。
