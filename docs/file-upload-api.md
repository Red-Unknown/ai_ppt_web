# 文件传输接口文档（PPT/PDF 上传）

## 1. 接口概览

- **接口名称**：课件文件上传
- **请求方法**：`POST`
- **接口路径**：`/api/v1/lesson/upload`
- **Content-Type**：`multipart/form-data`
- **后端实现**：`backend/app/api/v1/parser.py`

---

## 2. 功能说明

用于上传课件文件（`ppt` / `pptx` / `pdf`），服务端保存到本地目录后，返回可用于后续解析流程的文件元信息（如 `fileUrl`、`fileType`）。

---

## 3. 请求参数

| 参数名 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `file` | file | 是 | 课件文件，支持 `.ppt` `.pptx` `.pdf` |
| `course_id` | string | 否 | 课程ID（可用于联调透传） |
| `school_id` | string | 否 | 学校ID（可用于联调透传） |

### 上传限制

- 允许类型：`.ppt` `.pptx` `.pdf`
- 文件大小上限：`100MB`

---

## 4. 成功响应

```json
{
  "code": 200,
  "msg": "Upload successful",
  "data": {
    "fileId": "7ddf84b4d5fd4e17b8e7f5a07f9c6d58",
    "fileName": "第九章 压杆稳定.ppt",
    "fileType": "ppt",
    "fileSize": 14381283,
    "fileUrl": "uploads/lesson_files/7ddf84b4d5fd4e17b8e7f5a07f9c6d58.ppt",
    "courseId": "course_mechanics_001",
    "schoolId": "SCH001",
    "uploadedAt": "2026-04-20T13:20:00.000000+00:00"
  }
}
```

---

## 5. 错误响应

### 5.1 文件类型不支持

```json
{
  "detail": "Unsupported file type: .png. Allowed: ['.pdf', '.ppt', '.pptx']"
}
```

### 5.2 空文件

```json
{
  "detail": "Uploaded file is empty"
}
```

### 5.3 文件过大

```json
{
  "detail": "File too large. Max: 100MB"
}
```

---

## 6. 前端调用示例

### 6.1 JavaScript (fetch)

```javascript
const formData = new FormData();
formData.append("file", fileInput.files[0]);
formData.append("course_id", "course_mechanics_001");
formData.append("school_id", "SCH001");

const resp = await fetch("http://127.0.0.1:8001/api/v1/lesson/upload", {
  method: "POST",
  body: formData
});

const data = await resp.json();
console.log(data);
```

### 6.2 Python (requests)

```python
import requests

url = "http://127.0.0.1:8001/api/v1/lesson/upload"
with open("sandbox/第九章 压杆稳定.ppt", "rb") as f:
    files = {"file": ("第九章 压杆稳定.ppt", f, "application/vnd.ms-powerpoint")}
    data = {"course_id": "course_mechanics_001", "school_id": "SCH001"}
    r = requests.post(url, files=files, data=data, timeout=120)
    print(r.status_code, r.json())
```

---

## 7. 与全流程解析衔接

上传成功后可使用返回值中的：

- `data.fileUrl`
- `data.fileType`

作为 `full_pipeline` 的输入参数（通过 WebSocket `/api/v1/ws/script`，`service=full_pipeline`）。
