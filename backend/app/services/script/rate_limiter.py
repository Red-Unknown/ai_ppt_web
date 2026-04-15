import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from collections import defaultdict
import time

class RateLimiter:
    def __init__(self, max_requests: int = 100, time_window_seconds: int = 60):
        self.max_requests = max_requests
        self.time_window = timedelta(seconds=time_window_seconds)
        self.clients: Dict[str, list] = defaultdict(list)
        self._lock = asyncio.Lock()

    async def is_allowed(self, client_id: str) -> bool:
        async with self._lock:
            now = datetime.now()
            timestamps = self.clients[client_id]
            
            timestamps = [t for t in timestamps if now - t < self.time_window]
            self.clients[client_id] = timestamps
            
            if len(timestamps) < self.max_requests:
                self.clients[client_id].append(now)
                return True
            return False

    async def get_client_status(self, client_id: str) -> Dict[str, Any]:
        async with self._lock:
            now = datetime.now()
            timestamps = self.clients[client_id]
            timestamps = [t for t in timestamps if now - t < self.time_window]
            self.clients[client_id] = timestamps
            
            remaining = self.max_requests - len(timestamps)
            reset_time = None
            
            if timestamps:
                oldest = timestamps[0]
                reset_time = oldest + self.time_window
            
            return {
                "remaining_requests": remaining,
                "total_requests": self.max_requests,
                "reset_time": reset_time.isoformat() if reset_time else None,
                "current_window_requests": len(timestamps)
            }

    async def reset_client(self, client_id: str):
        async with self._lock:
            if client_id in self.clients:
                del self.clients[client_id]

    def get_global_stats(self) -> Dict[str, Any]:
        now = datetime.now()
        total_requests = 0
        active_clients = 0
        
        for client_id, timestamps in list(self.clients.items()):
            timestamps = [t for t in timestamps if now - t < self.time_window]
            self.clients[client_id] = timestamps
            
            if timestamps:
                active_clients += 1
                total_requests += len(timestamps)
        
        return {
            "total_active_clients": active_clients,
            "total_requests_in_window": total_requests,
            "max_requests_per_client": self.max_requests,
            "time_window_seconds": self.time_window.total_seconds()
        }