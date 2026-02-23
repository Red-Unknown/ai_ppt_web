---
alwaysApply: false
description: 对数据相关文件操作时
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