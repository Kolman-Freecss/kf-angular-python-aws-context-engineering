import json
import redis
from typing import Any, Optional, Union
from core.config import settings
import logging

logger = logging.getLogger(__name__)

class CacheService:
    """Redis-based caching service for performance optimization"""
    
    def __init__(self):
        self.redis_client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            decode_responses=True
        )
        self.default_ttl = 300  # 5 minutes default TTL
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            value = self.redis_client.get(key)
            if value:
                return json.loads(value)
            return None
        except (redis.RedisError, json.JSONDecodeError) as e:
            logger.warning(f"Cache get error for key {key}: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache with TTL"""
        try:
            ttl = ttl or self.default_ttl
            serialized_value = json.dumps(value, default=str)
            return self.redis_client.setex(key, ttl, serialized_value)
        except (redis.RedisError, json.JSONEncodeError) as e:
            logger.warning(f"Cache set error for key {key}: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        try:
            return bool(self.redis_client.delete(key))
        except redis.RedisError as e:
            logger.warning(f"Cache delete error for key {key}: {e}")
            return False
    
    def delete_pattern(self, pattern: str) -> int:
        """Delete all keys matching pattern"""
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                return self.redis_client.delete(*keys)
            return 0
        except redis.RedisError as e:
            logger.warning(f"Cache delete pattern error for {pattern}: {e}")
            return 0
    
    def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        try:
            return bool(self.redis_client.exists(key))
        except redis.RedisError as e:
            logger.warning(f"Cache exists error for key {key}: {e}")
            return False
    
    def get_ttl(self, key: str) -> int:
        """Get TTL for key"""
        try:
            return self.redis_client.ttl(key)
        except redis.RedisError as e:
            logger.warning(f"Cache TTL error for key {key}: {e}")
            return -1
    
    def extend_ttl(self, key: str, ttl: int) -> bool:
        """Extend TTL for key"""
        try:
            return bool(self.redis_client.expire(key, ttl))
        except redis.RedisError as e:
            logger.warning(f"Cache extend TTL error for key {key}: {e}")
            return False
    
    def clear_all(self) -> bool:
        """Clear all cache entries"""
        try:
            self.redis_client.flushdb()
            return True
        except redis.RedisError as e:
            logger.warning(f"Cache clear all error: {e}")
            return False
    
    def get_stats(self) -> dict:
        """Get cache statistics"""
        try:
            info = self.redis_client.info()
            return {
                'connected_clients': info.get('connected_clients', 0),
                'used_memory': info.get('used_memory_human', '0B'),
                'keyspace_hits': info.get('keyspace_hits', 0),
                'keyspace_misses': info.get('keyspace_misses', 0),
                'total_keys': self.redis_client.dbsize()
            }
        except redis.RedisError as e:
            logger.warning(f"Cache stats error: {e}")
            return {}

# Global cache instance
cache_service = CacheService()

def get_cache() -> CacheService:
    """Dependency to get cache service"""
    return cache_service
