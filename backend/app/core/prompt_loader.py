import json
import os
import threading
from typing import Dict, Any, Optional
from backend.app.core.config import settings

_lock = threading.Lock()
_cache: Dict[str, Any] = {}
_mtime: Optional[float] = None

def _load_file(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def _ensure_loaded():
    global _cache, _mtime
    path = settings.DEEPSEEK_PROMPTS_PATH
    if not os.path.exists(path):
        raise FileNotFoundError(f"Prompts file not found: {path}")
    stat = os.stat(path)
    current_mtime = stat.st_mtime
    if _mtime is None or current_mtime != _mtime:
        data = _load_file(path)
        _cache = data
        _mtime = current_mtime

def get_prompt(version: str, key: str) -> str:
    with _lock:
        _ensure_loaded()
        versions = _cache.get("versions", {})
        if version not in versions:
            version = _cache.get("default_version", "default")
        item = versions.get(version, {})
        text = item.get(key, "")
        return text

def list_versions() -> Dict[str, Any]:
    with _lock:
        _ensure_loaded()
        return _cache.get("versions", {})

def reload():
    with _lock:
        global _mtime
        _mtime = None
        _ensure_loaded()
