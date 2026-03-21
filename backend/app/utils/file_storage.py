import json
import os
from typing import Dict, Optional, Any

class FileStorage:
    def __init__(self, storage_path: str):
        self.storage_path = storage_path
        # 确保存储目录存在
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
    
    def load(self) -> Dict[str, Any]:
        """从文件加载数据"""
        try:
            if os.path.exists(self.storage_path):
                with open(self.storage_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            print(f"加载文件失败: {e}")
            return {}
    
    def save(self, data: Dict[str, Any]) -> bool:
        """保存数据到文件"""
        try:
            # 先写入临时文件，再重命名，确保原子性操作
            temp_path = f"{self.storage_path}.tmp"
            with open(temp_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            # 原子性重命名
            os.replace(temp_path, self.storage_path)
            return True
        except Exception as e:
            print(f"保存文件失败: {e}")
            return False
    
    def update(self, key: str, value: Any) -> bool:
        """更新指定键的值"""
        data = self.load()
        data[key] = value
        return self.save(data)