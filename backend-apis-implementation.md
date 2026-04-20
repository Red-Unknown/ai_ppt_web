# 前端功能所需后端接口说明（实现状态标注）

本文档列出了前端实现的功能模块所需的后端接口，并标注了各接口的实现状态。

## 一、用户认证模块

| 接口路径                       | 请求方法 | 功能描述   | 请求参数                                                                                                  | 响应数据                                                                                             | 认证要求 | 错误处理                  | 实现状态 | 备注 |
| -------------------------- | ---- | ------ | ----------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------ | ---- | --------------------- | ---- | ---- |
| `/api/auth/login`          | POST | 用户登录   | `email: string` (必填)<br>`password: string` (必填)                                                           | `{ "token": string, "user": { "id": number, "name": string, "email": string, "role": string } }` | 无    | 401: 账号或密码错误<br>400: 参数缺失 | 已实现 | 实际路径为 `/api/v1/login/` |
| `/api/auth/register`       | POST | 用户注册   | `name: string` (必填)<br>`email: string` (必填)<br>`password: string` (必填)<br>`role: string` (必填，'student'或'teacher') | `{ "id": number, "name": string, "email": string, "role": string }`                              | 无    | 400: 邮箱已存在<br>400: 参数缺失   | 未实现 | |
| `/api/auth/me`             | GET  | 获取用户信息 | 无                                                                                                     | `{ "id": number, "name": string, "email": string, "role": string }`                              | JWT  | 401: 未认证<br>403: 权限不足     | 未实现 | |
| `/api/auth/reset-password` | POST | 密码重置   | `email: string` (必填)                                                                                  | `{ "message": "重置链接已发送" }`                                                                       | 无    | 404: 邮箱不存在            | 未实现 | |

## 二、科目与章节模块

| 接口路径                | 请求方法 | 功能描述   | 请求参数                                    | 响应数据                                                                                                | 认证要求     | 错误处理                  | 实现状态 | 备注 |
| --------------------- | ---- | ------ | --------------------------------------- | --------------------------------------------------------------------------------------------------- | -------- | --------------------- | ---- | ---- |
| `/api/subjects`        | GET  | 获取科目列表 | `role: string` (可选，'student'或'teacher') | `[{ "id": number, "name": string, "createdAt": string }]`                                           | JWT      | 401: 未认证            | 未实现 | |
| `/api/subjects`        | POST | 创建科目   | `name: string` (必填)                      | `{ "id": number, "name": string, "createdAt": string }`                                           | JWT (教师) | 400: 参数缺失<br>403: 权限不足 | 未实现 | |
| `/api/subjects/:id`    | PUT  | 更新科目   | `name: string` (必填)                      | `{ "id": number, "name": string, "updatedAt": string }`                                           | JWT (教师) | 404: 科目不存在<br>403: 权限不足 | 未实现 | |
| `/api/subjects/:id`    | DELETE | 删除科目   | 无                                       | `{ "message": "科目删除成功" }`                                                                           | JWT (教师) | 404: 科目不存在<br>403: 权限不足 | 未实现 | |
| `/api/chapters`        | GET  | 获取章节列表 | `subjectId: number` (必填)                 | `[{ "id": number, "subjectId": number, "name": string, "order": number, "createdAt": string }]`      | JWT      | 401: 未认证            | 未实现 | |
| `/api/chapters`        | POST | 创建章节   | `subjectId: number` (必填)<br>`name: string` (必填)<br>`order: number` (必填) | `{ "id": number, "subjectId": number, "name": string, "order": number, "createdAt": string }`      | JWT (教师) | 400: 参数缺失<br>403: 权限不足 | 未实现 | |
| `/api/chapters/:id`    | PUT  | 更新章节   | `name: string` (可选)<br>`order: number` (可选) | `{ "id": number, "name": string, "order": number, "updatedAt": string }`                           | JWT (教师) | 404: 章节不存在<br>403: 权限不足 | 未实现 | |
| `/api/chapters/:id`    | DELETE | 删除章节   | 无                                       | `{ "message": "章节删除成功" }`                                                                           | JWT (教师) | 404: 章节不存在<br>403: 权限不足 | 未实现 | |

## 三、课程模块

| 接口路径                         | 请求方法 | 功能描述   | 请求参数                                    | 响应数据                                                                                                                 | 认证要求     | 错误处理       | 实现状态 | 备注 |
| ---------------------------- | ---- | ------ | --------------------------------------- | -------------------------------------------------------------------------------------------------------------------- | -------- | ---------- | ---- | ---- |
| `/api/courses`               | GET  | 获取课程列表 | `role: string` (可选，'student'或'teacher')<br>`subjectId: number` (可选)<br>`chapterId: number` (可选) | `[{ "id": number, "title": string, "description": string, "subjectId": number, "chapterId": number, "createdAt": string }]` | JWT      | 401: 未认证   | 未实现 | |
| `/api/courses`               | POST | 创建课程   | `title: string` (必填)<br>`description: string` (必填)<br>`subjectId: number` (必填)<br>`chapterId: number` (必填) | `{ "id": number, "title": string, "description": string, "subjectId": number, "chapterId": number, "createdAt": string }` | JWT (教师) | 400: 参数缺失<br>403: 权限不足 | 未实现 | |
| `/api/courses/:id`           | GET  | 获取课程详情 | 无                                       | `{ "id": number, "title": string, "description": string, "subjectId": number, "chapterId": number, "slideCount": number, "createdAt": string, "updatedAt": string }` | JWT      | 404: 课程不存在 | 未实现 | |
| `/api/courses/:id`           | PUT  | 更新课程   | `title: string` (可选)<br>`description: string` (可选) | `{ "id": number, "title": string, "description": string, "updatedAt": string }`                             | JWT (教师) | 404: 课程不存在<br>403: 权限不足 | 未实现 | |
| `/api/courses/:id`           | DELETE | 删除课程   | 无                                       | `{ "message": "课程删除成功" }`                                                                           | JWT (教师) | 404: 课程不存在<br>403: 权限不足 | 未实现 | |
| `/api/courses/:id/slides`    | GET  | 获取幻灯片列表 | 无                                       | `[{ "id": number, "slideIndex": number, "imageUrl": string, "duration": number }]`                                      | JWT      | 404: 幻灯片不存在 | 未实现 | |
| `/api/courses/:id/documents` | GET  | 获取课程文档 | 无                                       | `[{ "id": number, "title": string, "content": string, "type": string }]`                                             | JWT      | 404: 课程不存在 | 未实现 | |

## 四、PPT/图片上传模块（教师端）

| 接口路径                            | 请求方法 | 功能描述    | 请求参数                                     | 响应数据                                                                     | 认证要求     | 错误处理                 | 实现状态 | 备注 |
| ------------------------------- | ---- | ------- | ---------------------------------------- | ------------------------------------------------------------------------ | -------- | -------------------- | ---- | ---- |
| `/api/ppts`                     | POST | 上传PPT/图片 | `courseId: number` (必填)<br>`file: file` (必填) | `{ "id": number, "courseId": number, "fileName": string, "slides": [] }` | JWT (教师) | 400: 文件格式错误<br>403: 权限不足 | 未实现 | |
| `/api/ppts/:id`                 | GET  | 获取PPT信息 | 无                                        | `{ "id": number, "courseId": number, "fileName": string, "slides": [] }` | JWT (教师) | 404: PPT不存在<br>403: 权限不足 | 未实现 | |
| `/api/ppts/:id/parse`           | POST | 解析PPT/图片 | 无                                        | `{ "id": number, "slides": [] }`                                         | JWT (教师) | 404: PPT不存在<br>403: 权限不足 | 未实现 | |
| `/api/ppts/:id`                 | DELETE | 删除PPT/图片 | 无                                        | `{ "message": "PPT删除成功" }`                                             | JWT (教师) | 404: PPT不存在<br>403: 权限不足 | 未实现 | |

## 五、AI教案生成模块（教师端）

| 接口路径                          | 请求方法 | 功能描述    | 请求参数                                    | 响应数据                                                                     | 认证要求     | 错误处理                 | 实现状态 | 备注 |
| ------------------------------- | ---- | ------- | ---------------------------------------- | ------------------------------------------------------------------------ | -------- | -------------------- | ---- | ---- |
| `/api/ai/generate-lesson-plan`  | POST | 生成AI教案 | `courseId: number` (必填)<br>`pptId: number` (必填) | `{ "id": number, "courseId": number, "content": object, "createdAt": string }` | JWT (教师) | 400: 参数缺失<br>403: 权限不足 | 未实现 | |
| `/api/lesson-plans/:courseId`   | GET  | 获取教案   | 无                                        | `{ "id": number, "courseId": number, "content": object, "createdAt": string, "updatedAt": string }` | JWT (教师) | 404: 教案不存在<br>403: 权限不足 | 未实现 | |
| `/api/lesson-plans`             | POST | 保存教案   | `courseId: number` (必填)<br>`content: object` (必填) | `{ "id": number, "courseId": number, "content": object, "updatedAt": string }` | JWT (教师) | 400: 参数缺失<br>403: 权限不足 | 未实现 | |
| `/api/lesson-plans/:id`         | PUT  | 更新教案   | `content: object` (必填)                    | `{ "id": number, "content": object, "updatedAt": string }`             | JWT (教师) | 404: 教案不存在<br>403: 权限不足 | 未实现 | |
| `/api/lesson-plans/:id`         | DELETE | 删除教案   | 无                                        | `{ "message": "教案删除成功" }`                                             | JWT (教师) | 404: 教案不存在<br>403: 权限不足 | 未实现 | |

## 六、AI助手模块

| 接口路径                  | 请求方法 | 功能描述   | 请求参数                                                                                                  | 响应数据                                                                                                   | 认证要求 | 错误处理       | 实现状态 | 备注 |
| --------------------- | ---- | ------ | ----------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------ | ---- | ---------- | ---- | ---- |
| `/api/ai/ask`         | POST | 发送问题   | `question: string` (必填)<br>`courseId: number` (可选)<br>`addedContents: array` (可选，添加的PPT内容)                    | `{ "id": number, "answer": string, "thinkingSteps": [] }`                                              | JWT  | 400: 问题为空  | 未实现 | |
| `/api/ai/history`     | GET  | 获取历史对话 | `page: number` (可选，默认1)<br>`limit: number` (可选，默认10)                                                      | `[{ "id": number, "question": string, "answer": string, "createdAt": string }]`                        | JWT  | 401: 未认证   | 已实现 | 实际路径为 `/api/v1/chat/sessions` |
| `/api/ai/history/:id` | GET  | 获取对话详情 | 无                                                                                                     | `{ "id": number, "question": string, "answer": string, "createdAt": string, "followupQuestions": [] }` | JWT  | 404: 对话不存在 | 已实现 | 实际路径为 `/api/v1/chat/history/{session_id}` |
| `/api/ai/history`     | POST | 保存对话   | `question: string` (必填)<br>`answer: string` (必填)<br>`courseId: number` (可选)                                   | `{ "id": number, "question": string, "answer": string }`                                               | JWT  | 400: 参数缺失  | 已实现 | 实际通过WebSocket会话自动保存 |
| `/api/ai/settings`    | POST | 保存AI设置 | `model: string` (必填)<br>`usePython: boolean` (必填)<br>`useInternet: boolean` (必填)<br>`preciseAnswer: boolean` (必填) | `{ "model": string, "usePython": boolean, "useInternet": boolean, "preciseAnswer": boolean }`          | JWT  | 400: 参数缺失  | 未实现 | |

## 七、已实现的额外接口

| 接口路径                       | 请求方法 | 功能描述   | 说明 |
| -------------------------- | ---- | ------ | ---- |
| `/api/v1/login/logout`     | POST | 用户登出   | 实际实现的登出接口 |
| `/api/v1/login/validate`   | POST | 验证会话有效性 | 实际实现的会话验证接口 |
| `/api/v1/login/user/{username}` | GET | 获取用户信息 | 实际实现的用户信息获取接口 |
| `/api/v1/chat/ws`          | WebSocket | 实时聊天   | 实现了WebSocket实时通信 |
| `/api/v1/chat/session/start` | POST | 开始学习会话 | 开始学习或预览会话 |
| `/api/v1/chat/session/{session_id}/preview` | GET | 获取预览状态 | 获取视频生成状态 |
| `/api/v1/chat/sse`         | GET  | SSE聊天接口 | 实现了Server-Sent Events聊天 |
| `/api/v1/student/profile`  | POST | 创建/更新学生档案 | 学生档案管理 |
| `/api/v1/student/profile`  | GET  | 获取学生档案 | 学生档案查询 |

## 八、认证机制

- 所有需要用户身份的接口都使用JWT认证
- 在请求头中添加 `Authorization: Bearer {token}`
- 令牌有效期为24小时

## 九、错误处理

| 状态码 | 含义                    | 描述       |
| --- | --------------------- | -------- |
| 400 | Bad Request           | 参数错误或缺失  |
| 401 | Unauthorized          | 未认证或认证失效 |
| 403 | Forbidden             | 权限不足     |
| 404 | Not Found             | 资源不存在    |
| 500 | Internal Server Error | 服务器内部错误  |

## 十、数据格式

- 所有接口使用JSON格式
- 日期时间使用ISO 8601格式
- 分页接口返回格式：`{ "data": [], "total": number, "page": number, "limit": number }`

## 十一、安全性

- 密码使用bcrypt加密存储
- 上传文件进行类型和大小验证
- 接口请求频率限制
- 输入参数验证和清理

## 十二、性能考虑

- 大文件上传使用分块上传
- 图片资源使用CDN加速
- 缓存频繁访问的数据