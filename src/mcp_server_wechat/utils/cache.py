"""
缓存管理

提供内存和文件缓存功能，优化 API 调用性能。
"""

import json
import time
import hashlib
from pathlib import Path
from typing import Any, Optional, Dict


class CacheManager:
    """缓存管理器"""
    
    def __init__(self, cache_dir: str = ".cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.memory_cache: Dict[str, Dict[str, Any]] = {}
        
    def _get_cache_key(self, prefix: str, **kwargs) -> str:
        """生成缓存键"""
        key_data = f"{prefix}_{json.dumps(kwargs, sort_keys=True)}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def get(self, prefix: str, ttl: int = 3600, **kwargs) -> Optional[Any]:
        """获取缓存"""
        cache_key = self._get_cache_key(prefix, **kwargs)
        
        # 检查内存缓存
        if cache_key in self.memory_cache:
            cache_data = self.memory_cache[cache_key]
            if time.time() < cache_data["expires_at"]:
                return cache_data["data"]
            else:
                del self.memory_cache[cache_key]
        
        # 检查文件缓存
        cache_file = self.cache_dir / f"{cache_key}.json"
        if cache_file.exists():
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                    
                if time.time() < cache_data["expires_at"]:
                    # 加载到内存缓存
                    self.memory_cache[cache_key] = cache_data
                    return cache_data["data"]
                else:
                    cache_file.unlink()  # 删除过期文件
            except (json.JSONDecodeError, KeyError):
                cache_file.unlink()  # 删除损坏文件
                
        return None
    
    def set(self, prefix: str, data: Any, ttl: int = 3600, **kwargs) -> None:
        """设置缓存"""
        cache_key = self._get_cache_key(prefix, **kwargs)
        expires_at = time.time() + ttl
        
        cache_data = {
            "data": data,
            "expires_at": expires_at,
            "created_at": time.time()
        }
        
        # 保存到内存缓存
        self.memory_cache[cache_key] = cache_data
        
        # 保存到文件缓存
        cache_file = self.cache_dir / f"{cache_key}.json"
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
        except Exception:
            pass  # 文件缓存失败不影响功能
    
    def clear_expired(self) -> None:
        """清理过期缓存"""
        current_time = time.time()
        
        # 清理内存缓存
        expired_keys = [
            key for key, data in self.memory_cache.items()
            if current_time >= data["expires_at"]
        ]
        for key in expired_keys:
            del self.memory_cache[key]
        
        # 清理文件缓存
        for cache_file in self.cache_dir.glob("*.json"):
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                    
                if current_time >= cache_data["expires_at"]:
                    cache_file.unlink()
            except Exception:
                cache_file.unlink()  # 删除损坏文件


# 全局缓存实例
cache_manager = CacheManager()