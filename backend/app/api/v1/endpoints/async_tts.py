from fastapi import APIRouter, BackgroundTasks, HTTPException, Depends, Query
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any
import asyncio

from backend.app.services.script.async_tts_service import async_tts_service

router = APIRouter(prefix="/async-tts", tags=["异步文字转语音"])

class SynthesizeRequest(BaseModel):
    text: str
    voice: Optional[str] = "zh-CN-XiaoxiaoNeural"
    client_id: Optional[str] = "default"

class TaskStatusResponse(BaseModel):
    task_id: str
    status: str
    progress: int
    message: str
    created_at: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    duration_ms: Optional[int] = None
    error: Optional[str] = None

@router.on_event("startup")
async def startup_event():
    await async_tts_service.start()

@router.on_event("shutdown")
async def shutdown_event():
    await async_tts_service.shutdown()

@router.post("/synthesize", summary="提交语音合成任务")
async def synthesize_async(request: SynthesizeRequest):
    """
    提交异步语音合成任务，返回任务ID供后续查询状态和结果。
    
    **请求参数**:
    - `text`: 要合成的文本内容（支持数学公式转换）
    - `voice`: 语音标识，默认为中文晓晓 (zh-CN-XiaoxiaoNeural)
    - `client_id`: 客户端标识，用于限流控制
    
    **支持的语音**:
    - 中文: zh-CN-XiaoxiaoNeural, zh-CN-YunyangNeural, zh-CN-XiaoyiNeural
    - 英文: en-US-AriaNeural, en-US-GuyNeural
    
    **返回示例**:
    ```json
    {
        "status": "accepted",
        "task_id": "550e8400-e29b-41d4-a716-446655440000",
        "message": "任务已提交，正在处理中",
        "remaining_requests": 95
    }
    ```
    
    **错误情况**:
    - `rate_limit_exceeded`: 请求过于频繁，超过限流阈值
    """
    task_id, result = await async_tts_service.synthesize_async(
        text=request.text,
        voice=request.voice,
        client_id=request.client_id
    )
    
    if task_id is None:
        raise HTTPException(status_code=429, detail=result)
    
    return JSONResponse(content=result, status_code=202)

@router.get("/status/{task_id}", response_model=TaskStatusResponse, summary="查询任务状态")
async def get_task_status(task_id: str):
    """
    查询语音合成任务的状态和进度。
    
    **路径参数**:
    - `task_id`: 任务ID（从 /synthesize 接口获取）
    
    **状态说明**:
    - `pending`: 任务等待处理
    - `processing`: 正在生成语音（配合 progress 查看进度）
    - `completed`: 语音生成完成
    - `failed`: 语音生成失败
    
    **返回示例**:
    ```json
    {
        "task_id": "550e8400-e29b-41d4-a716-446655440000",
        "status": "processing",
        "progress": 50,
        "message": "正在生成语音...",
        "created_at": "2024-01-01T12:00:00Z",
        "started_at": "2024-01-01T12:00:01Z"
    }
    ```
    """
    result = await async_tts_service.get_task_status(task_id)
    
    if "error" in result:
        raise HTTPException(status_code=404, detail=result)
    
    return TaskStatusResponse(**result)

@router.get("/result/{task_id}", summary="获取语音合成结果")
async def get_task_result(task_id: str):
    """
    获取语音合成结果（MP3音频文件）。
    
    **路径参数**:
    - `task_id`: 任务ID
    
    **注意事项**:
    - 仅当任务状态为 `completed` 时才能获取结果
    - 返回MP3格式的音频数据
    
    **错误情况**:
    - `task_not_found`: 任务不存在或已过期
    - `task_not_completed`: 任务尚未完成
    
    **使用示例**:
    ```
    GET /async-tts/result/550e8400-e29b-41d4-a716-446655440000
    返回: MP3音频文件
    ```
    """
    result = await async_tts_service.get_task_status(task_id)
    
    if "error" in result:
        raise HTTPException(status_code=404, detail=result)
    
    if result["status"] != "completed":
        raise HTTPException(
            status_code=400,
            detail={
                "error": "task_not_completed",
                "message": "任务尚未完成，请先查询状态确认",
                "current_status": result["status"]
            }
        )
    
    audio_data = await async_tts_service.get_task_result(task_id)
    
    return StreamingResponse(
        iter([audio_data]),
        media_type="audio/mpeg",
        headers={
            "Content-Disposition": f"attachment; filename={task_id}.mp3"
        }
    )

@router.delete("/task/{task_id}", summary="取消任务")
async def cancel_task(task_id: str):
    """
    取消等待中的任务。
    
    **路径参数**:
    - `task_id`: 任务ID
    
    **注意事项**:
    - 仅能取消状态为 `pending` 的任务
    - 正在处理或已完成的任务无法取消
    
    **返回示例**:
    ```json
    {
        "success": true,
        "message": "任务已取消"
    }
    ```
    """
    success = await async_tts_service.cancel_task(task_id)
    
    if success:
        return {"success": true, "message": "任务已取消"}
    else:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "cannot_cancel",
                "message": "无法取消该任务（可能已在处理或已完成）"
            }
        )

@router.get("/stats", summary="获取服务统计信息")
async def get_stats():
    """
    获取异步TTS服务的统计信息，包括队列状态和限流信息。
    
    **返回示例**:
    ```json
    {
        "queue": {
            "total_tasks": 15,
            "pending_tasks": 3,
            "processing_tasks": 5,
            "completed_tasks": 7,
            "failed_tasks": 0,
            "active_workers": 5,
            "max_concurrent": 10
        },
        "rate_limit": {
            "total_active_clients": 12,
            "total_requests_in_window": 156,
            "max_requests_per_client": 100,
            "time_window_seconds": 60
        },
        "service_running": true
    }
    ```
    """
    return async_tts_service.get_stats()

@router.get("/wait/{task_id}", summary="阻塞等待任务完成")
async def wait_for_task(task_id: str, timeout: int = Query(60, ge=1, le=300)):
    """
    阻塞等待任务完成（最长等待timeout秒），适用于需要同步获取结果的场景。
    
    **路径参数**:
    - `task_id`: 任务ID
    
    **查询参数**:
    - `timeout`: 最长等待时间（秒），默认为60秒
    
    **返回示例**:
    ```json
    {
        "task_id": "550e8400-e29b-41d4-a716-446655440000",
        "status": "completed",
        "progress": 100,
        "message": "语音生成完成",
        "duration_ms": 2345
    }
    ```
    
    **错误情况**:
    - `timeout`: 等待超时
    """
    start_time = asyncio.get_event_loop().time()
    
    while asyncio.get_event_loop().time() - start_time < timeout:
        result = await async_tts_service.get_task_status(task_id)
        
        if "error" in result:
            raise HTTPException(status_code=404, detail=result)
        
        if result["status"] in ["completed", "failed"]:
            return result
        
        await asyncio.sleep(0.5)
    
    raise HTTPException(
        status_code=408,
        detail={
            "error": "timeout",
            "message": f"等待超时（{timeout}秒）",
            "hint": "请使用 /status 接口查询任务状态"
        }
    )