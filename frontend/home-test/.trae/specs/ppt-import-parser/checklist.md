# Checklist

## 后端服务
- [x] mock-server 在端口 8001 正常运行
- [x] WebSocket 端点 /api/v1/ws/script 可连接
- [x] HTTP 端点 /health 返回正常状态
- [x] 支持 full_pipeline 服务解析

## 前端配置
- [x] PptShow2.vue WebSocket URL 配置正确 (ws://127.0.0.1:8001/api/v1/ws/script)
- [x] PptShow2.vue 文件上传 API 配置正确 (http://127.0.0.1:8001/api/v1/lesson/upload)
- [x] PptTeach2.vue PPTParserService 初始化正确

## PptShow2.vue 功能
- [x] 导入弹窗 UI 正常显示（添加按钮、文件选择、导入按钮）
- [x] 文件选择后显示已选文件列表
- [x] 点击导入按钮触发文件上传
- [x] 上传进度条正常显示
- [x] WebSocket 连接自动建立
- [x] 解析状态实时更新（start → vl_llm_parse_complete → ... → done）
- [x] 解析进度条正常显示
- [x] 解析完成后课程卡片添加到列表
- [x] 错误处理正常（显示错误提示）

## PptTeach2.vue 功能
- [x] PPTParserService 在页面加载时自动初始化
- [x] 解析状态栏显示连接状态
- [x] "测试解析"按钮已删除
- [x] "重新连接"按钮已删除
- [x] 页面卸载时正确断开 WebSocket 连接

## 端到端流程
- [x] 从 PptShow2.vue 导入 PPT 文件流程完整
- [x] 文件上传 → WebSocket 解析 → 结果展示 流程正常
- [x] 解析结果数据正确（教案、幻灯片、思维导图）
