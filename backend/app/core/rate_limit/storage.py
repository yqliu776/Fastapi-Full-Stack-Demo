from typing import Optional
from app.core.connects import redis_client
from app.core.utils import logger


class RateLimitStorage:
    """限流存储后端"""

    def __init__(self):
        """初始化存储后端"""
        self.redis_client = redis_client

    async def add_to_whitelist(self, identifier: str, expire_time: Optional[int] = None) -> bool:
        """
        添加到白名单

        Args:
            identifier: 标识符
            expire_time: 过期时间（秒）

        Returns:
            是否成功
        """
        try:
            redis = await self.redis_client.get_redis()
            key = f"rate_limit:whitelist:{identifier}"
            if expire_time:
                await redis.set(key, "1", ex=expire_time)
            else:
                await redis.set(key, "1")
            logger.info(f"已将 {identifier} 添加到白名单")
            return True
        except Exception as e:
            logger.error(f"添加到白名单失败: {str(e)}")
            return False

    async def remove_from_whitelist(self, identifier: str) -> bool:
        """
        从白名单移除

        Args:
            identifier: 标识符

        Returns:
            是否成功
        """
        try:
            redis = await self.redis_client.get_redis()
            key = f"rate_limit:whitelist:{identifier}"
            result = await redis.delete(key)
            if result > 0:
                logger.info(f"已将 {identifier} 从白名单移除")
                return True
            return False
        except Exception as e:
            logger.error(f"从白名单移除失败: {str(e)}")
            return False

    async def is_whitelisted(self, identifier: str) -> bool:
        """
        检查是否在白名单中

        Args:
            identifier: 标识符

        Returns:
            是否在白名单中
        """
        try:
            redis = await self.redis_client.get_redis()
            key = f"rate_limit:whitelist:{identifier}"
            result = await redis.exists(key)
            return result > 0
        except Exception as e:
            logger.error(f"检查白名单失败: {str(e)}")
            return False

    async def add_to_blacklist(self, identifier: str, expire_time: Optional[int] = None) -> bool:
        """
        添加到黑名单

        Args:
            identifier: 标识符
            expire_time: 过期时间（秒）

        Returns:
            是否成功
        """
        try:
            redis = await self.redis_client.get_redis()
            key = f"rate_limit:blacklist:{identifier}"
            if expire_time:
                await redis.set(key, "1", ex=expire_time)
            else:
                await redis.set(key, "1")
            logger.info(f"已将 {identifier} 添加到黑名单")
            return True
        except Exception as e:
            logger.error(f"添加到黑名单失败: {str(e)}")
            return False

    async def remove_from_blacklist(self, identifier: str) -> bool:
        """
        从黑名单移除

        Args:
            identifier: 标识符

        Returns:
            是否成功
        """
        try:
            redis = await self.redis_client.get_redis()
            key = f"rate_limit:blacklist:{identifier}"
            result = await redis.delete(key)
            if result > 0:
                logger.info(f"已将 {identifier} 从黑名单移除")
                return True
            return False
        except Exception as e:
            logger.error(f"从黑名单移除失败: {str(e)}")
            return False

    async def is_blacklisted(self, identifier: str) -> bool:
        """
        检查是否在黑名单中

        Args:
            identifier: 标识符

        Returns:
            是否在黑名单中
        """
        try:
            redis = await self.redis_client.get_redis()
            key = f"rate_limit:blacklist:{identifier}"
            result = await redis.exists(key)
            return result > 0
        except Exception as e:
            logger.error(f"检查黑名单失败: {str(e)}")
            return False

    async def get_whitelist(self) -> list:
        """
        获取白名单列表

        Returns:
            白名单列表
        """
        try:
            redis = await self.redis_client.get_redis()
            pattern = "rate_limit:whitelist:*"
            keys = await redis.keys(pattern)
            whitelist = []
            for key in keys:
                identifier = key.replace("rate_limit:whitelist:", "")
                ttl = await redis.ttl(key)
                whitelist.append({
                    "identifier": identifier,
                    "ttl": ttl if ttl > 0 else None
                })
            return whitelist
        except Exception as e:
            logger.error(f"获取白名单失败: {str(e)}")
            return []

    async def get_blacklist(self) -> list:
        """
        获取黑名单列表

        Returns:
            黑名单列表
        """
        try:
            redis = await self.redis_client.get_redis()
            pattern = "rate_limit:blacklist:*"
            keys = await redis.keys(pattern)
            blacklist = []
            for key in keys:
                identifier = key.replace("rate_limit:blacklist:", "")
                ttl = await redis.ttl(key)
                blacklist.append({
                    "identifier": identifier,
                    "ttl": ttl if ttl > 0 else None
                })
            return blacklist
        except Exception as e:
            logger.error(f"获取黑名单失败: {str(e)}")
            return []