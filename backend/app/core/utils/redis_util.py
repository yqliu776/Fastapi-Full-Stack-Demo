import json
from typing import Any, Dict, List, Optional
from datetime import datetime

from redis.asyncio import Redis
from sqlalchemy.ext.declarative import DeclarativeMeta

from app.core.connects import redis_client


class RedisUtil:
    """Redis工具类，提供常用Redis操作的封装
    
    支持字符串、哈希表、列表、集合等数据类型的常用操作
    自动序列化和反序列化复杂对象
    """
    
    @staticmethod
    async def get_redis() -> Redis:
        """获取Redis客户端实例"""
        return await redis_client.get_redis()
    
    @staticmethod
    def _serialize(value: Any) -> str:
        """将Python对象序列化为JSON字符串
        
        Args:
            value: 要序列化的对象
            
        Returns:
            str: 序列化后的JSON字符串
        """
        if isinstance(value, (str, int, float, bool)):
            return str(value)
        elif isinstance(value, datetime):
            return value.isoformat()
        elif isinstance(value, (list, tuple)):
            return json.dumps([RedisUtil._serialize(v) for v in value], ensure_ascii=False)
        elif isinstance(value, dict):
            return json.dumps({k: RedisUtil._serialize(v) for k, v in value.items()}, ensure_ascii=False)
        elif isinstance(value.__class__, DeclarativeMeta):
            # 处理 SQLAlchemy 模型对象
            return json.dumps({
                col.name: RedisUtil._serialize(getattr(value, col.name))
                for col in value.__table__.columns
            }, ensure_ascii=False)
        else:
            return json.dumps(value, ensure_ascii=False)
    
    @staticmethod
    def _deserialize(value: Optional[str]) -> Any:
        """将JSON字符串反序列化为Python对象
        
        Args:
            value: 要反序列化的字符串
            
        Returns:
            Any: 反序列化后的Python对象
        """
        if value is None:
            return None
        
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return value
    
    # 字符串操作
    @classmethod
    async def set(cls, key: str, value: Any, ex: Optional[int] = None) -> bool:
        """设置字符串值，可选过期时间
        
        Args:
            key: 键名
            value: 值（将自动序列化）
            ex: 过期时间（秒），None表示永不过期
            
        Returns:
            bool: 设置成功返回True
        """
        redis = await cls.get_redis()
        serialized = cls._serialize(value)
        await redis.set(key, serialized, ex=ex)
        return True
    
    @classmethod
    async def get(cls, key: str) -> Any:
        """获取字符串值
        
        Args:
            key: 键名
            
        Returns:
            Any: 反序列化后的值，不存在返回None
        """
        redis = await cls.get_redis()
        value = await redis.get(key)
        return cls._deserialize(value)
    
    @classmethod
    async def delete(cls, *keys: str) -> int:
        """删除一个或多个键
        
        Args:
            *keys: 一个或多个键名
            
        Returns:
            int: 成功删除的键数量
        """
        if not keys:
            return 0
        
        redis = await cls.get_redis()
        return await redis.delete(*keys)
    
    @classmethod
    async def exists(cls, key: str) -> bool:
        """检查键是否存在
        
        Args:
            key: 键名
            
        Returns:
            bool: 存在返回True，否则返回False
        """
        redis = await cls.get_redis()
        result = await redis.exists(key)
        return bool(result)
    
    @classmethod
    async def expire(cls, key: str, seconds: int) -> bool:
        """设置键的过期时间
        
        Args:
            key: 键名
            seconds: 过期时间（秒）
            
        Returns:
            bool: 设置成功返回True
        """
        redis = await cls.get_redis()
        return await redis.expire(key, seconds)
    
    @classmethod
    async def ttl(cls, key: str) -> int:
        """获取键的剩余生存时间
        
        Args:
            key: 键名
            
        Returns:
            int: 剩余生存时间（秒），-1表示永不过期，-2表示键不存在
        """
        redis = await cls.get_redis()
        return await redis.ttl(key)
    
    # 哈希表操作
    @classmethod
    async def hset(cls, name: str, key: str, value: Any) -> int:
        """设置哈希表字段值
        
        Args:
            name: 哈希表名
            key: 字段名
            value: 字段值（将自动序列化）
            
        Returns:
            int: 如果字段是新的并且值已设置，返回1，否则返回0
        """
        redis = await cls.get_redis()
        serialized = cls._serialize(value)
        return await redis.hset(name, key, serialized)
    
    @classmethod
    async def hget(cls, name: str, key: str) -> Any:
        """获取哈希表字段值
        
        Args:
            name: 哈希表名
            key: 字段名
            
        Returns:
            Any: 反序列化后的字段值，不存在返回None
        """
        redis = await cls.get_redis()
        value = await redis.hget(name, key)
        return cls._deserialize(value)
    
    @classmethod
    async def hmset(cls, name: str, mapping: Dict[str, Any]) -> bool:
        """批量设置哈希表字段值
        
        Args:
            name: 哈希表名
            mapping: 字段名到字段值的映射
            
        Returns:
            bool: 设置成功返回True
        """
        redis = await cls.get_redis()
        serialized_mapping = {k: cls._serialize(v) for k, v in mapping.items()}
        await redis.hset(name, mapping=serialized_mapping)
        return True
    
    @classmethod
    async def hgetall(cls, name: str) -> Dict[str, Any]:
        """获取哈希表所有字段和值
        
        Args:
            name: 哈希表名
            
        Returns:
            Dict[str, Any]: 字段名到反序列化字段值的映射
        """
        redis = await cls.get_redis()
        mapping = await redis.hgetall(name)
        return {k: cls._deserialize(v) for k, v in mapping.items()}
    
    @classmethod
    async def hdel(cls, name: str, *keys: str) -> int:
        """删除哈希表一个或多个字段
        
        Args:
            name: 哈希表名
            *keys: 一个或多个字段名
            
        Returns:
            int: 成功删除的字段数量
        """
        if not keys:
            return 0
        
        redis = await cls.get_redis()
        return await redis.hdel(name, *keys)
    
    # 列表操作
    @classmethod
    async def lpush(cls, name: str, *values: Any) -> int:
        """将一个或多个值插入到列表头部
        
        Args:
            name: 列表名
            *values: 一个或多个值（将自动序列化）
            
        Returns:
            int: 操作后列表的长度
        """
        if not values:
            return 0
        
        redis = await cls.get_redis()
        serialized_values = [cls._serialize(v) for v in values]
        return await redis.lpush(name, *serialized_values)
    
    @classmethod
    async def rpush(cls, name: str, *values: Any) -> int:
        """将一个或多个值插入到列表尾部
        
        Args:
            name: 列表名
            *values: 一个或多个值（将自动序列化）
            
        Returns:
            int: 操作后列表的长度
        """
        if not values:
            return 0
        
        redis = await cls.get_redis()
        serialized_values = [cls._serialize(v) for v in values]
        return await redis.rpush(name, *serialized_values)
    
    @classmethod
    async def lrange(cls, name: str, start: int, end: int) -> List[Any]:
        """获取列表指定范围内的元素
        
        Args:
            name: 列表名
            start: 开始索引
            end: 结束索引
            
        Returns:
            List[Any]: 反序列化后的元素列表
        """
        redis = await cls.get_redis()
        values = await redis.lrange(name, start, end)
        return [cls._deserialize(v) for v in values]
    
    @classmethod
    async def lpop(cls, name: str) -> Any:
        """移除并返回列表头部元素
        
        Args:
            name: 列表名
            
        Returns:
            Any: 反序列化后的元素，列表为空或不存在返回None
        """
        redis = await cls.get_redis()
        value = await redis.lpop(name)
        return cls._deserialize(value)
    
    @classmethod
    async def rpop(cls, name: str) -> Any:
        """移除并返回列表尾部元素
        
        Args:
            name: 列表名
            
        Returns:
            Any: 反序列化后的元素，列表为空或不存在返回None
        """
        redis = await cls.get_redis()
        value = await redis.rpop(name)
        return cls._deserialize(value)
    
    # 集合操作
    @classmethod
    async def sadd(cls, name: str, *values: Any) -> int:
        """向集合添加一个或多个成员
        
        Args:
            name: 集合名
            *values: 一个或多个值（将自动序列化）
            
        Returns:
            int: 添加到集合中的新成员数量
        """
        if not values:
            return 0
        
        redis = await cls.get_redis()
        serialized_values = [cls._serialize(v) for v in values]
        return await redis.sadd(name, *serialized_values)
    
    @classmethod
    async def smembers(cls, name: str) -> set:
        """返回集合中的所有成员
        
        Args:
            name: 集合名
            
        Returns:
            set: 反序列化后的集合成员
        """
        redis = await cls.get_redis()
        values = await redis.smembers(name)
        return {cls._deserialize(v) for v in values}
    
    @classmethod
    async def srem(cls, name: str, *values: Any) -> int:
        """移除集合中一个或多个成员
        
        Args:
            name: 集合名
            *values: 一个或多个值（将自动序列化）
            
        Returns:
            int: 成功移除的成员数量
        """
        if not values:
            return 0
        
        redis = await cls.get_redis()
        serialized_values = [cls._serialize(v) for v in values]
        return await redis.srem(name, *serialized_values)
    
    # 分布式锁
    @classmethod
    async def acquire_lock(cls, lock_name: str, token: str, expire: int = 10) -> bool:
        """获取分布式锁
        
        Args:
            lock_name: 锁名称
            token: 锁持有者标识（用于释放锁时验证身份）
            expire: 锁过期时间（秒），默认10秒
            
        Returns:
            bool: 获取锁成功返回True，否则返回False
        """
        redis = await cls.get_redis()
        result = await redis.set(f"lock:{lock_name}", token, nx=True, ex=expire)
        return result is not None
    
    @classmethod
    async def release_lock(cls, lock_name: str, token: str) -> bool:
        """释放分布式锁
        
        Args:
            lock_name: 锁名称
            token: 锁持有者标识（必须与获取锁时的token一致）
            
        Returns:
            bool: 释放锁成功返回True，否则返回False
        """
        redis = await cls.get_redis()
        lock_key = f"lock:{lock_name}"
        
        # 使用Lua脚本确保原子性操作
        script = """
        if redis.call('get', KEYS[1]) == ARGV[1] then
            return redis.call('del', KEYS[1])
        else
            return 0
        end
        """
        
        result = await redis.eval(script, 1, lock_key, token)
        return bool(result)


redis_util = RedisUtil() 