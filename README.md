 # 基于泛雅平台的 AI 互动智课生成与实时问答系统

面向第十七届服创大赛 A12 赛题，构建一个可嵌入泛雅平台的 AI 智课生成与实时问答系统：支持课件解析、结构化讲授脚本生成、多轮上下文问答以及进度续接与节奏调整。

---

## 项目结构概览

- `backend/`：FastAPI 后端服务（API、业务逻辑、异步任务等）
- `frontend/`：基于 Vite + Vue 3 + Tailwind CSS 的前端界面
- `fixtures/`：联调和端到端测试用冻结数据集
- `scripts/`：环境初始化等自动化脚本
- `sandbox/`：个人调试空间（已在 .gitignore 中忽略）
- `TEAM_GUIDELINES.md`：团队协作与开发规范总纲
- `environment.yml`：统一 Conda 环境定义

更详细的团队协作规范与目录说明见 `TEAM_GUIDELINES.md`。

---

## 开发环境准备

1. 安装 Conda（Miniconda 或 Anaconda）
2. 在项目根目录执行环境引导脚本（Windows）：

   ```bash
   scripts\bootstrap.bat
   ```

3. 激活环境：

   ```bash
   conda activate fwwb_a12_env
   ```

如需调整依赖，请严格按照 `TEAM_GUIDELINES.md` 中的环境变更流程进行，并在提交时同步更新 `environment.yml`。

---

## 启动项目

### 后端服务（FastAPI）

```bash
conda activate fwwb_a12_env
cd backend
python main.py
```

启动成功后，可在浏览器中访问：

- OpenAPI 文档：`http://localhost:8000/docs`

### 前端界面（Vue 3 + Vite）

首次需要安装依赖：

```bash
cd frontend
npm install
```

之后启动开发服务器：

```bash
npm run dev
```

默认访问地址为：`http://localhost:5173`

---

## 分支与提交规范（简要）

- 分支：
  - `main`：保持可演示、可发布状态
  - `dev`：日常开发主分支
  - `feat/<feature-name>`：新功能开发分支
  - `fix/<bug-name>`：缺陷修复分支
- 提交信息：
  - 推荐使用类 Conventional Commits 风格，例如：
    - `feat(parser): add ppt upload api`
    - `fix(qa): improve answer accuracy`

完整规则与更多约定（环境、数据、代码风格等）请参见 `TEAM_GUIDELINES.md`。

