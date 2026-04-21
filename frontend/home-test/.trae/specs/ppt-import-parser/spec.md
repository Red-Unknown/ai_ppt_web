# PPT 导入解析功能 Spec

## Why
教师端需要能够导入 PPT 文件并自动解析内容，生成教案、思维导图和语音讲解，以支持智能教学辅助功能。

## What Changes
- 集成 PPTParserService WebSocket 服务进行 PPT 内容解析
- 在 PptShow2.vue 中实现文件上传 → WebSocket 解析 → 结果展示的完整流程
- 在 PptTeach2.vue 中集成 PPTParserService 用于教学展示
- 配置前端路由指向 mock 后端服务 (ws://127.0.0.1:8001/api/v1/ws/script)
- 删除 PptTeach2.vue 中的测试按钮和重新连接按钮

## Impact
- Affected specs: PPT 解析服务接口、文件上传组件、教案展示组件
- Affected code: 
  - PptShow2.vue (文件导入弹窗、WebSocket 连接、解析状态展示)
  - PptTeach2.vue (PPTParserService 集成、解析控制栏)
  - pptParserService.js (WebSocket 服务封装)
  - mock-server/server.js (Mock 后端服务)

## ADDED Requirements

### Requirement: PPT 文件导入功能
The system SHALL 提供 PPT 文件导入功能，支持 .ppt, .pptx, .pdf, .jpg, .jpeg, .png 格式。

#### Scenario: 成功导入文件
- **WHEN** 用户点击"+"按钮打开导入弹窗
- **AND** 用户选择文件并点击"导入"按钮
- **THEN** 文件上传到后端 /api/v1/lesson/upload
- **AND** 自动建立 WebSocket 连接进行解析
- **AND** 实时显示解析进度和状态

### Requirement: WebSocket PPT 解析
The system SHALL 通过 WebSocket 连接发送解析请求并接收实时进度更新。

#### Scenario: 解析流程成功
- **WHEN** WebSocket 连接建立成功
- **AND** 发送解析请求 {service: 'full_pipeline', file_path, file_type, course_id}
- **THEN** 接收 status 消息: start → vl_llm_parse_complete → content_text → script → postgres_cir_base → mind_map → tts(progress) → tts_done → qdrant → done
- **AND** 每个阶段更新 UI 进度显示

#### Scenario: 解析过程出错
- **WHEN** 解析过程中发生错误
- **THEN** 接收 error 消息并显示错误提示
- **AND** 关闭 WebSocket 连接

### Requirement: 解析结果展示
The system SHALL 在解析完成后展示生成的教案内容、幻灯片、思维导图。

#### Scenario: 展示教案内容
- **WHEN** 接收到 done 消息
- **THEN** 更新 lessonContent (教学目标、重难点、教学步骤、练习题)
- **AND** 更新 slides (幻灯片图片和元素)
- **AND** 更新 mindMapContent (思维导图数据)

## MODIFIED Requirements

### Requirement: PptTeach2.vue 界面优化
**修改内容**: 删除测试按钮和重新连接按钮，保留解析状态显示栏。

**原因**: 这些按钮仅用于开发测试，不应出现在生产环境。

## REMOVED Requirements

### Requirement: 测试解析按钮
**Reason**: 仅用于开发调试，功能已由文件导入流程替代。
**Migration**: 使用文件导入弹窗触发解析。

### Requirement: 重新连接按钮
**Reason**: 连接管理应由服务自动处理，无需手动干预。
**Migration**: 页面加载时自动初始化连接，断线自动重连。
