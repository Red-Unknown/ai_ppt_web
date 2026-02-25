---
alwaysApply: true
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