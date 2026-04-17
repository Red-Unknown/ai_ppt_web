# generate_mindmap.py 使用说明书

## 简介
根据课程讲义内容，调用 DeepSeek 推理模型自动生成树状思维导图（JSON格式）。

## 前置要求

### 1. 环境配置
- Python 3.10+
- 已安装依赖：`langchain-openai`, `langchain-core`

```bash
pip install langchain-openai langchain-core
```

### 2. API Key 配置
需要设置 DeepSeek API Key 环境变量：

**Windows PowerShell:**
```powershell
$env:DEEPSEEK_API_KEY="your-api-key-here"
```

**Windows CMD:**
```cmd
set DEEPSEEK_API_KEY=your-api-key-here
```

**Linux/Mac:**
```bash
export DEEPSEEK_API_KEY="your-api-key-here"
```

> 💡 获取 API Key: [DeepSeek 开放平台](https://platform.deepseek.com/)

## 使用方法

### 基本用法

1. **准备输入文件**
   - 将课程讲义内容保存到 `d:/ai_ppt_web/out_put.txt`

2. **运行脚本**
   ```powershell
   # PowerShell
   $env:DEEPSEEK_API_KEY="sk-xxx"; .\venv\Scripts\python.exe generate_mindmap.py
   ```

3. **查看输出**
   - 生成的思维导图保存在 `d:/ai_ppt_web/mind_map.json`

### 输出格式示例

```json
{
  "root": {
    "name": "轴向拉伸与压缩",
    "children": [
      {
        "name": "引言与基本概念",
        "children": [
          {"name": "定义"},
          {"name": "实例与应用"}
        ]
      }
    ]
  }
}
```

## 配置参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `DEEPSEEK_API_KEY` | DeepSeek API 密钥 | 必填 |
| `DEEPSEEK_BASE_URL` | API 基础地址 | `https://api.deepseek.com` |
| 输入文件 | 课程讲义文本 | `d:/ai_ppt_web/out_put.txt` |
| 输出文件 | 思维导图 JSON | `d:/ai_ppt_web/mind_map.json` |

## 模型配置

脚本使用以下默认配置：
- **模型**: `deepseek-reasoner` (DeepSeek 推理模型)
- **温度**: 0.3 (低随机性，更确定性输出)
- **最大 Token**: 4000

## 故障排除

| 问题 | 解决方案 |
|------|----------|
| `ModuleNotFoundError` | 安装依赖：`pip install langchain-openai langchain-core` |
| `API Key 不存在` | 检查环境变量是否正确设置 |
| `文件不存在` | 确认 `out_put.txt` 路径正确 |
| JSON 解析错误 | 检查输入文件内容是否为空或格式异常 |

## 文件结构

```
ai_ppt_web/
├── generate_mindmap.py      # 主脚本
├── generate_mindmap_README.md  # 本说明书
├── out_put.txt              # 输入：课程讲义
└── mind_map.json            # 输出：思维导图
```

## 集成建议

生成的 `mind_map.json` 可直接：
1. 存入数据库 `lessons.mind_map` 字段（JSONB 类型）
2. 前端使用 D3.js、ECharts 等库可视化展示
3. 作为课程知识导航的交互式目录树

---
*生成时间: 2026-04-17*
