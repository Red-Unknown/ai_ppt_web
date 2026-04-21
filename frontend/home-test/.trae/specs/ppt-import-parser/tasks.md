# Tasks

- [ ] Task 1: 验证 mock 后端服务运行状态
  - [ ] SubTask 1.1: 检查 mock-server 是否在端口 8001 运行
  - [ ] SubTask 1.2: 验证 WebSocket 端点 /api/v1/ws/script 可连接
  - [ ] SubTask 1.3: 测试健康检查端点 /health

- [ ] Task 2: 配置前端路由指向 mock 服务
  - [ ] SubTask 2.1: 确认 PptShow2.vue 中 WebSocket URL 配置为 ws://127.0.0.1:8001/api/v1/ws/script
  - [ ] SubTask 2.2: 确认文件上传 API 配置为 http://127.0.0.1:8001/api/v1/lesson/upload

- [ ] Task 3: 完善 PptShow2.vue 文件导入解析流程
  - [ ] SubTask 3.1: 确保 handleFileUpload 方法正确上传文件
  - [ ] SubTask 3.2: 确保 establishWebSocketConnection 方法正确建立连接
  - [ ] SubTask 3.3: 确保 WebSocket 消息处理正确更新进度和状态
  - [ ] SubTask 3.4: 解析完成后正确更新课程列表和跳转

- [ ] Task 4: 优化 PptTeach2.vue 界面
  - [ ] SubTask 4.1: 删除"测试解析"按钮
  - [ ] SubTask 4.2: 删除"重新连接"按钮
  - [ ] SubTask 4.3: 保留解析状态显示栏，仅用于展示状态

- [ ] Task 5: 验证端到端流程
  - [ ] SubTask 5.1: 在 PptShow2.vue 中导入测试 PPT 文件
  - [ ] SubTask 5.2: 验证文件上传成功
  - [ ] SubTask 5.3: 验证 WebSocket 解析流程正常
  - [ ] SubTask 5.4: 验证解析结果正确展示

# Task Dependencies
- Task 3 depends on Task 1, Task 2
- Task 4 depends on Task 1
- Task 5 depends on Task 3, Task 4
