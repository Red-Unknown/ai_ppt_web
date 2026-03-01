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
   conda activate ai_ppt_web
   ```

如需调整依赖，请严格按照 `TEAM_GUIDELINES.md` 中的环境变更流程进行，并在提交时同步更新 `environment.yml`。

---

## 启动项目

### 1. 环境变量配置 (Configuration)

本项目采用环境变量管理敏感密钥，支持 Windows/Linux/MacOS 多平台。

#### 必需变量

| 变量名 | 描述 | 示例值 |
| --- | --- | --- |
| `DEEPSEEK_API_KEY` | DeepSeek LLM 接口密钥 | `sk-xxxxxxxx` |
| `TAVILY_API_KEY` | Tavily 搜索服务密钥 (可选，启用联网搜索) | `tvly-xxxxxxxx` |

#### 配置命令指南

**Windows (PowerShell/CMD)**
```powershell
# 临时生效 (当前终端)
set DEEPSEEK_API_KEY=sk-your-key
set TAVILY_API_KEY=tvly-your-key

# 永久生效 (需重启终端)
setx DEEPSEEK_API_KEY "sk-your-key"
setx TAVILY_API_KEY "tvly-your-key"
```

**Linux / macOS**
```bash
# 临时生效
export DEEPSEEK_API_KEY="sk-your-key"
export TAVILY_API_KEY="tvly-your-key"

# 永久生效 (添加到 Shell 配置文件)
echo 'export DEEPSEEK_API_KEY="sk-your-key"' >> ~/.zshrc
echo 'export TAVILY_API_KEY="tvly-your-key"' >> ~/.zshrc
source ~/.zshrc
```

### 2. DeepSeek Reasoner 模式 (R1)

本项目集成了 DeepSeek R1 (Reasoner) 模型，用于处理复杂的逻辑推理、数学证明及代码生成任务。

**适用场景**
- **复杂理科解题**：多步骤数学推导、物理建模。
- **深度代码生成**：生成完整模块或复杂算法。
- **逻辑证明**：需要严密逻辑链的论证。

**使用方式**
系统具备**智能模式切换**功能：
1. **自动切换**：当用户提问包含 "solve", "prove", "calculate", "证明", "计算" 等复杂意图时，后端自动切换至 Reasoner 模式。
2. **手动指定**：在前端界面顶部下拉菜单选择 "DeepSeek Reasoner" 模型。

**前端展示**
在 Reasoner 模式下，前端会展示折叠的 "Thinking Process" (思考过程) 面板，实时流式输出模型的推理步骤，随后输出最终答案。

### 3. API 调用示例

代码中通过 `backend.app.core.config.settings` 统一读取环境变量，**严禁硬编码**。

```python
from backend.app.core.config import settings

def get_llm_client():
    if not settings.DEEPSEEK_API_KEY:
        raise ValueError("DEEPSEEK_API_KEY not found!")
        
    return ChatOpenAI(
        api_key=settings.DEEPSEEK_API_KEY,
        model=settings.DEEPSEEK_MODEL
    )
```

### 4. 故障排除 (Troubleshooting)

**Q: 启动时报错 `ConfigurationError: Missing required configuration: DEEPSEEK_API_KEY`**
A: 环境变量未正确设置。请检查：
1. 是否执行了 `export` 或 `setx` 命令。
2. Windows 下使用 `setx` 后是否重启了终端。
3. 检查 `.env` 文件是否存在（如果使用 `.env`）。

**Q: 联网搜索返回 "Mock Result"**
A: 说明 `TAVILY_API_KEY` 未设置或无效，且 DuckDuckGo 连接失败。系统自动降级为 Mock 模式。请申请 Tavily Key 并配置环境变量。

**Q: Reasoner 模式没有思考过程显示**
A: 
1. 确认当前模型是否为 `deepseek-reasoner`。
2. 检查网络连接，流式传输可能受网络波动影响。

---

### 一键启动前后端联调

使用启动脚本自动检查依赖并启动服务：

```bash
# 在项目根目录执行
python scripts/start_app.py
```

或指定运行模式：
```bash
python scripts/start_app.py --mode prod  # 生产模式（无热重载）
```

启动成功后访问：
- 前端界面：`http://localhost:5173`
- API 文档：`http://localhost:8000/docs`

### 手动分别启动

**后端服务（FastAPI）**
```bash
conda activate ai_ppt_web
cd backend
python main.py
```

**前端界面（Vue 3 + Vite）**
首次需要安装依赖：
```bash
cd frontend
npm install
```

启动开发服务器：
```bash
npm run dev
```

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

