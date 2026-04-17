# 环境规范
所有后端调试和生产都在 `ai_ppt_web` conda环境中运行
embedding 模型在 `embedding` conda环境中运行

# 启动脚本
- 启动前后端服务：
`python .\scripts\start_app.py`
- 启动 embedding 模型：
`cd backend\app\services\embedding ; .\start.ps1`

# powershell规则
不得使用`&&`等逻辑运算符，必须使用分号`;`分隔多个命令。
