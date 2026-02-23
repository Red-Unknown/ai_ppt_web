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
