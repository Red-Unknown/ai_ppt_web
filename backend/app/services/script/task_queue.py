import asyncio
import uuid
from typing import Dict, Any, Optional, Callable
from enum import Enum
from dataclasses import dataclass
from datetime import datetime

class TaskStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class Task:
    task_id: str
    text: str
    voice: str
    status: TaskStatus
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[bytes] = None
    error: Optional[str] = None
    progress: int = 0

class TaskQueue:
    def __init__(self, max_concurrent_tasks: int = 10):
        self.queue = asyncio.Queue()
        self.tasks: Dict[str, Task] = {}
        self.max_concurrent = max_concurrent_tasks
        self.active_workers = 0
        self._lock = asyncio.Lock()
        self._shutdown_event = asyncio.Event()
        self._workers = []

    async def enqueue(self, text: str, voice: str) -> str:
        task_id = str(uuid.uuid4())
        task = Task(
            task_id=task_id,
            text=text,
            voice=voice,
            status=TaskStatus.PENDING,
            created_at=datetime.now()
        )
        self.tasks[task_id] = task
        await self.queue.put(task_id)
        return task_id

    async def dequeue(self) -> Optional[str]:
        try:
            task_id = await asyncio.wait_for(self.queue.get(), timeout=1.0)
            return task_id
        except asyncio.TimeoutError:
            return None

    async def get_task(self, task_id: str) -> Optional[Task]:
        async with self._lock:
            return self.tasks.get(task_id)

    async def update_task_status(self, task_id: str, status: TaskStatus):
        async with self._lock:
            if task_id in self.tasks:
                self.tasks[task_id].status = status
                if status == TaskStatus.PROCESSING:
                    self.tasks[task_id].started_at = datetime.now()
                elif status in (TaskStatus.COMPLETED, TaskStatus.FAILED):
                    self.tasks[task_id].completed_at = datetime.now()

    async def update_task_progress(self, task_id: str, progress: int):
        async with self._lock:
            if task_id in self.tasks:
                self.tasks[task_id].progress = progress

    async def set_task_result(self, task_id: str, result: bytes):
        async with self._lock:
            if task_id in self.tasks:
                self.tasks[task_id].result = result
                self.tasks[task_id].status = TaskStatus.COMPLETED
                self.tasks[task_id].completed_at = datetime.now()
                self.tasks[task_id].progress = 100

    async def set_task_error(self, task_id: str, error: str):
        async with self._lock:
            if task_id in self.tasks:
                self.tasks[task_id].error = error
                self.tasks[task_id].status = TaskStatus.FAILED
                self.tasks[task_id].completed_at = datetime.now()

    async def remove_task(self, task_id: str):
        async with self._lock:
            if task_id in self.tasks:
                del self.tasks[task_id]

    async def start_workers(self):
        for _ in range(self.max_concurrent):
            worker = asyncio.create_task(self._worker())
            self._workers.append(worker)

    async def shutdown(self):
        self._shutdown_event.set()
        await asyncio.gather(*self._workers, return_exceptions=True)

    async def _worker(self):
        while not self._shutdown_event.is_set():
            task_id = await self.dequeue()
            if task_id is None:
                await asyncio.sleep(0.1)
                continue

            async with self._lock:
                self.active_workers += 1

            try:
                await self.update_task_status(task_id, TaskStatus.PROCESSING)
                await self.update_task_progress(task_id, 20)
                
                task = await self.get_task(task_id)
                if task:
                    from .tts import TTSService
                    await self.update_task_progress(task_id, 50)
                    audio_data = await TTSService.synthesize(task.text, task.voice, preprocess=True)
                    await self.update_task_progress(task_id, 80)
                    await self.set_task_result(task_id, audio_data)
                    await self.update_task_progress(task_id, 100)
            except Exception as e:
                await self.set_task_error(task_id, str(e))
            finally:
                async with self._lock:
                    self.active_workers -= 1
                self.queue.task_done()

    def get_stats(self) -> Dict[str, Any]:
        pending = sum(1 for t in self.tasks.values() if t.status == TaskStatus.PENDING)
        processing = sum(1 for t in self.tasks.values() if t.status == TaskStatus.PROCESSING)
        completed = sum(1 for t in self.tasks.values() if t.status == TaskStatus.COMPLETED)
        failed = sum(1 for t in self.tasks.values() if t.status == TaskStatus.FAILED)
        
        return {
            "total_tasks": len(self.tasks),
            "pending_tasks": pending,
            "processing_tasks": processing,
            "completed_tasks": completed,
            "failed_tasks": failed,
            "active_workers": self.active_workers,
            "max_concurrent": self.max_concurrent
        }