# Role B: 结构引擎 & CIR API 接口文档

## 1. 概述

本模块（Role B）负责在 **课件解析结果** 与 **智课生成 / 问答互动** 之间搭建桥梁，核心职责：

- **结构归一化**：将 Role A 输出的 PPT/PDF 解析结果转换为统一的 **CIR (Course Intermediate Representation, 课程中间表示)**。
- **课程树管理**：维护课程的章节 / 小节 / 知识点树形结构，并提供 CRUD 接口。
- **图结构服务**：为 Role C（讲稿/视频生成）与 Role D（RAG 检索、问答）提供节点查询与路径上下文。

与其它角色的关系：

- A → B：A 负责底层解析，B 基于解析 JSON 构建 CIR & 课程树。
- B → C：C 从 B 读取 CIR 与节点树，生成结构化讲稿、TTS 文本。
- B → D：D 调用 B 的节点/路径接口，为知识图谱检索提供结构上下文。

---

## 2. 核心数据模型：CIR JSON

### 2.1 顶层结构

统一的课程中间表示 CIR 建议采用如下 JSON 结构（可挂载在 `/courses/{course_id}/cir`）：

```json
{
  "course_id": "c_1001",
  "title": "深度学习导论",
  "version": 4,
  "nodes": [
    {
      "id": "n_501",
      "type": "node",
      "title": "链式法则",
      "parent_id": "sec_1_1",
      "order": 2,
      "metadata": {
        "slide_indexes": [4],
        "key_phrases": ["微积分", "链式法则"],
        "summary": "复习微积分中的链式求导法则，这是理解反向传播的数学基础。",
        "depends_on": [],
        "level": 3
      }
    },
    {
      "id": "n_502",
      "type": "node",
      "title": "反向传播的基本思想",
      "parent_id": "sec_1_1",
      "order": 3,
      "metadata": {
        "slide_indexes": [5, 6],
        "key_phrases": ["反向传播", "梯度下降", "误差传递"],
        "summary": "本节主要介绍了反向传播算法中，如何利用链式法则将输出层的误差梯度逐层向后传递，从而更新网络权重。",
        "depends_on": ["n_501"], 
        "level": 3
      }
    }
  ],
  "edges": [
    {
      "source": "n_501",
      "target": "n_502",
      "type": "prerequisite",
      "description": "反向传播依赖链式法则的数学前置知识"
    }
  ]
}
```

说明：

- `nodes`：以扁平列表形式存储所有节点，支持 `chapter/section/node` 等类型。
- `edges`：预留为知识图谱扩展，可记录父子关系、先后关系等。
- `metadata`：承载 PPT 页码区间、关键短语、标题层级等信息。

---

## 3. 与 Role A 的接口：CIR 构建任务

### 3.1 触发 CIR 构建（解析结果 → CIR）

**POST** `/api/v1/structure/courses/{course_id}/cir/build`

用于在 Role A 完成课件解析后，基于解析结果异步构建或重建 CIR。

**请求体**：

```json
{
  "parser_result_id": "pr_20260320_001",
  "force_rebuild": false
}
```

- `parser_result_id`：Role A 产出的解析结果标识（数据库记录 ID / 对象存储 key）。
- `force_rebuild`：是否强制重建（忽略已有版本的 CIR 缓存）。

**响应 (202 Accepted)**：

```json
{
  "code": "OK",
  "message": "CIR 构建任务已提交",
  "request_id": "req_20260320_100",
  "data": {
    "task_id": "cir_task_abc123",
    "course_id": "c_1001"
  }
}
```

### 3.2 查询 CIR 构建任务状态

**GET** `/api/v1/structure/cir-tasks/{task_id}`

**响应 (200 OK)**：

```json
{
  "code": "OK",
  "message": "查询成功",
  "request_id": "req_20260320_101",
  "data": {
    "status": "processing",   // processing | completed | failed
    "progress": 60,
    "error_code": null,
    "error_message": null
  }
}
```

---

## 4. 课程结构管理接口（对前端 & 教师）

> 与《总API接口文档》中的「4. 课程结构管理」保持一致，这里给出更聚焦于 Role B 的说明。

### 4.1 获取课程树形大纲

**GET** `/api/v1/courses/{course_id}/tree`

**描述**：返回课程的完整树形结构，供前端左侧大纲展示。

**响应 (200 OK)**：

```json
{
  "code": "OK",
  "message": "查询成功",
  "request_id": "req_20260320_040",
  "data": {
    "course_id": "c_1001",
    "root": {
      "id": "root_1",
      "title": "深度学习导论",
      "children": [
        {
          "id": "chap_1",
          "title": "第一章：基础知识",
          "children": [
            {
              "id": "sec_1_1",
              "title": "1.1 感知机",
              "children": []
            }
          ]
        }
      ]
    }
  }
}
```

### 4.2 课程节点 CRUD（教师编辑）

#### 4.2.1 创建节点

**POST** `/api/v1/courses/{course_id}/nodes`

**请求体**：

```json
{
  "title": "1.2 反向传播算法",
  "parent_id": "chap_1",
  "type": "section",              // chapter | section | node
  "order": 2,
  "metadata": {
    "slide_range": [11, 15]
  }
}
```

**响应 (201 Created)**：返回新建节点的完整信息。

#### 4.2.2 更新节点

**PUT** `/api/v1/courses/{course_id}/nodes/{node_id}`

**请求体**：

```json
{
  "title": "1.2 反向传播基本思想",
  "order": 2,
  "metadata": {
    "slide_range": [11, 16]
  }
}
```

#### 4.2.3 删除节点

**DELETE** `/api/v1/courses/{course_id}/nodes/{node_id}`

**描述**：删除指定节点及其子树（需在文档中说明是否允许删除有子节点的节点，或强制要求为空节点才能删）。  
所有响应统一使用 `code/message/data/request_id` 包裹。

---

## 5. 结构查询接口（供 Role C / D 使用）

### 5.1 获取单个节点详情

**GET** `/api/v1/structure/nodes/{node_id}`

**描述**：为 Role C / D 提供单个节点的详细结构信息及路径上下文。

**响应 (200 OK)**：

```json
{
  "code": "OK",
  "message": "查询成功",
  "request_id": "req_20260320_050",
  "data": {
    "id": "n_502",
    "title": "反向传播的基本思想",
    "type": "node",
    "path": "/第一章/第三节/反向传播",
    "ancestors": ["chap_1", "sec_1_3"],
    "metadata": {
      "slide_indexes": [5, 6],
      "level": 3,
      "key_phrases": ["反向传播", "梯度下降"]
    }
  }
}
```

### 5.2 按关键字/路径搜索节点

**GET** `/api/v1/structure/courses/{course_id}/nodes/search`

**Query 参数**：

- `keyword`（可选）：在标题 / 关键短语中模糊搜索。
- `path_prefix`（可选）：限定搜索在某一章节子树下。

**响应 (200 OK)**：

{
  "code": "OK",
  "message": "查询成功",
  "request_id": "req_20260320_051",
  "data": {
    "results": [
      {
        "node_id": "n_502",
        "title": "反向传播的基本思想",
        "path": "/第一章/第一节/反向传播",
        "slide_indexes": [5, 6], 
        "summary": "本节主要介绍了反向传播算法中，如何利用链式法则...", 
        "relevance_score": 0.92
      }
    ]
  }
}
```
5.3获取节点上下文与前置依赖 API
**GET** /api/v1/structure/nodes/{node_id}/context
{
  "code": "OK",
  "message": "查询成功",
  "request_id": "req_20260320_052",
  "data": {
    "current_node": {
      "id": "n_502",
      "title": "反向传播的基本思想",
      "slide_indexes": [5, 6]
    },
    "prerequisites": [
      {
        "id": "n_501",
        "title": "链式法则",
        "slide_indexes": [4],
        "summary": "复习微积分中的链式求导法则，这是理解反向传播的数学基础。",
        "relation_type": "prerequisite"
      }
    ],
    "next_node": {
      "id": "n_503",
      "title": "梯度消失问题",
      "slide_indexes": [7]
    }
  }
}

> Role D 的 `/knowledge/retrieve` 可以内部依赖该接口获取候选节点，再与向量检索结果融合。

---

## 6. 演示与评审建议

为了更好展示 Role B 在整套系统中的价值，推荐在答辩 Demo 中突出以下流程：

1. **结构可视化**：前端调用 `GET /courses/{course_id}/tree`，在左侧展示完整课程树（章节/小节/知识点）。
2. **编辑联动**：演示教师在前端拖拽/编辑节点（调用节点 CRUD 接口）后，再次调用树接口，结构实时更新。
3. **与 Role C/D 的联动**：
   - 通过 `GET /structure/nodes/{node_id}` 展示某一知识点的上下文信息（父节点路径、关联 PPT 页码等）。
   - 说明 Role C 如何基于 CIR 生成分章节讲稿；Role D 如何利用节点搜索接口做 RAG 检索与问答。

通过以上接口设计，Role B 清晰地承担了「结构中台」的职责，实现从底层解析到上层智课/问答的解耦与复用。 

