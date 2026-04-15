import asyncio
import os
from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timedelta

from .task_queue import TaskQueue, TaskStatus
from .rate_limiter import RateLimiter

class AsyncTTSService:
    def __init__(self):
        self.task_queue = TaskQueue(max_concurrent_tasks=10)
        self.rate_limiter = RateLimiter(max_requests=100, time_window_seconds=60)
        self._started = False
        self._cleanup_interval = 3600
        self._cleanup_task = None

    async def start(self):
        if not self._started:
            await self.task_queue.start_workers()
            self._cleanup_task = asyncio.create_task(self._periodic_cleanup())
            self._started = True

    async def shutdown(self):
        if self._started:
            await self.task_queue.shutdown()
            if self._cleanup_task:
                self._cleanup_task.cancel()
                try:
                    await self._cleanup_task
                except asyncio.CancelledError:
                    pass
            self._started = False

    async def synthesize_async(self, text: str, voice: str, client_id: str = "default") -> Tuple[str, Dict[str, Any]]:
        is_allowed = await self.rate_limiter.is_allowed(client_id)
        if not is_allowed:
            client_status = await self.rate_limiter.get_client_status(client_id)
            return None, {
                "error": "rate_limit_exceeded",
                "message": "请求过于频繁，请稍后重试",
                "reset_time": client_status.get("reset_time")
            }

        if not self._started:
            await self.start()

        task_id = await self.task_queue.enqueue(text, voice)
        client_status = await self.rate_limiter.get_client_status(client_id)
        
        return task_id, {
            "status": "accepted",
            "task_id": task_id,
            "message": "任务已提交，正在处理中",
            "remaining_requests": client_status.get("remaining_requests")
        }

    async def get_task_status(self, task_id: str) -> Dict[str, Any]:
        task = await self.task_queue.get_task(task_id)
        if not task:
            return {
                "error": "task_not_found",
                "message": "任务不存在或已过期"
            }

        response = {
            "task_id": task.task_id,
            "status": task.status.value,
            "progress": task.progress,
            "created_at": task.created_at.isoformat()
        }

        if task.started_at:
            response["started_at"] = task.started_at.isoformat()
        
        if task.completed_at:
            response["completed_at"] = task.completed_at.isoformat()
            response["duration_ms"] = int((task.completed_at - task.created_at).total_seconds() * 1000)

        if task.error:
            response["error"] = task.error
        
        if task.status == TaskStatus.COMPLETED:
            response["message"] = "语音生成完成"
        elif task.status == TaskStatus.PROCESSING:
            response["message"] = "正在生成语音..."
        elif task.status == TaskStatus.PENDING:
            response["message"] = "等待处理中"
        elif task.status == TaskStatus.FAILED:
            response["message"] = "语音生成失败"

        return response

    async def get_task_result(self, task_id: str) -> Optional[bytes]:
        task = await self.task_queue.get_task(task_id)
        if task and task.status == TaskStatus.COMPLETED:
            return task.result
        return None

    async def cancel_task(self, task_id: str) -> bool:
        task = await self.task_queue.get_task(task_id)
        if task and task.status == TaskStatus.PENDING:
            await self.task_queue.update_task_status(task_id, TaskStatus.CANCELLED)
            return True
        return False

    def get_stats(self) -> Dict[str, Any]:
        queue_stats = self.task_queue.get_stats()
        rate_stats = self.rate_limiter.get_global_stats()
        
        return {
            "queue": queue_stats,
            "rate_limit": rate_stats,
            "service_running": self._started
        }

    async def _periodic_cleanup(self):
        while True:
            try:
                await asyncio.sleep(self._cleanup_interval)
                await self._cleanup_completed_tasks()
            except asyncio.CancelledError:
                break
            except Exception:
                pass

    async def _cleanup_completed_tasks(self):
        cutoff_time = datetime.now() - timedelta(hours=1)
        task_ids_to_remove = []
        
        async for task_id in self._iterate_tasks():
            task = await self.task_queue.get_task(task_id)
            if task and task.completed_at and task.completed_at < cutoff_time:
                task_ids_to_remove.append(task_id)
        
        for task_id in task_ids_to_remove:
            await self.task_queue.remove_task(task_id)

    async def _iterate_tasks(self):
        task_ids = list(self.task_queue.tasks.keys())
        for task_id in task_ids:
            yield task_id

async_tts_service = AsyncTTSService()