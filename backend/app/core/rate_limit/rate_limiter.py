import time
from typing import Optional, Dict, Any, List
from enum import Enum

from app.core.rate_limit.algorithms import TokenBucket, SlidingWindow, FixedWindow
from app.core.rate_limit.storage import RateLimitStorage
from app.core.models import AppException
from app.core.utils import logger


class RateLimitScope(str, Enum):
    """限流作用域"""
    GLOBAL = "global"  # 全局限流
    IP = "ip"  # IP地址限流
    USER = "user"  # 用户限流
    ENDPOINT = "endpoint"  # 端点限流
    IP_USER = "ip_user"  # IP+用户组合限流
    IP_ENDPOINT = "ip_endpoint"  # IP+端点组合限流
    USER_ENDPOINT = "user_endpoint"  # 用户+端点组合限流


class RateLimitResult:
    """限流结果"""

    def __init__(self, allowed: bool, remaining: int, reset_time: int,
                 limit: int, retry_after: Optional[int] = None):
        """
        初始化限流结果

        Args:
            allowed: 是否允许请求
            remaining: 剩余可用次数
            reset_time: 重置时间戳
            limit: 限制总数
            retry_after: 重试等待时间（秒）
        """
        self.allowed = allowed
        self.remaining = remaining
        self.reset_time = reset_time
        self.limit = limit
        self.retry_after = retry_after

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "allowed": self.allowed,
            "remaining": self.remaining,
            "reset_time": self.reset_time,
            "limit": self.limit,
            "retry_after": self.retry_after
        }


class RateLimitConfig:
    """限流配置"""

    def __init__(self,
                 limit: int = 100,
                 window: int = 60,
                 burst: int = 10,
                 block_duration: int = 60,
                 enabled: bool = True):
        """
        初始化限流配置

        Args:
            limit: 限制数量
            window: 时间窗口（秒）
            burst: 突发容量（令牌桶算法使用）
            block_duration: 封禁时长（秒）
            enabled: 是否启用
        """
        self.limit = limit
        self.window = window
        self.burst = burst
        self.block_duration = block_duration
        self.enabled = enabled


class RateLimiter:
    """限流器主类"""

    def __init__(self, storage: RateLimitStorage):
        """
        初始化限流器

        Args:
            storage: 存储后端
        """
        self.storage = storage
        self.algorithms = {
            "token_bucket": TokenBucket,
            "sliding_window": SlidingWindow,
            "fixed_window": FixedWindow
        }

    @staticmethod
    def _build_rate_limit_key(scope: RateLimitScope, identifier: str,
                              endpoint: Optional[str] = None, user_id: Optional[str] = None) -> str:
        """
        构建限流键

        Args:
            scope: 限流作用域
            identifier: 标识符（IP地址等）
            endpoint: API端点
            user_id: 用户ID

        Returns:
            限流键
        """
        key_parts = ["rate_limit"]

        if scope == RateLimitScope.GLOBAL:
            key_parts.append("global")
        elif scope == RateLimitScope.IP:
            key_parts.extend(["ip", identifier])
        elif scope == RateLimitScope.USER and user_id:
            key_parts.extend(["user", user_id])
        elif scope == RateLimitScope.ENDPOINT and endpoint:
            key_parts.extend(["endpoint", endpoint.replace("/", "_")])
        elif scope == RateLimitScope.IP_USER and user_id:
            key_parts.extend(["ip_user", f"{identifier}_{user_id}"])
        elif scope == RateLimitScope.IP_ENDPOINT and endpoint:
            key_parts.extend(["ip_endpoint", f"{identifier}_{endpoint.replace('/', '_')}"])
        elif scope == RateLimitScope.USER_ENDPOINT and user_id and endpoint:
            key_parts.extend(["user_endpoint", f"{user_id}_{endpoint.replace('/', '_')}"])
        else:
            # 默认使用IP限流
            key_parts.extend(["ip", identifier])

        return ":".join(key_parts)

    async def is_allowed(self,
                        scope: RateLimitScope,
                        identifier: str,
                        algorithm: str = "token_bucket",
                        config: Optional[RateLimitConfig] = None,
                        endpoint: Optional[str] = None,
                        user_id: Optional[str] = None) -> RateLimitResult:
        """
        检查是否允许请求

        Args:
            scope: 限流作用域
            identifier: 标识符（IP地址等）
            algorithm: 限流算法
            config: 限流配置
            endpoint: API端点
            user_id: 用户ID

        Returns:
            限流结果
        """
        from app.core.settings import settings

        # 如果限流被禁用，直接允许
        if not settings.RATE_LIMIT_ENABLED:
            return RateLimitResult(
                allowed=True,
                remaining=999999,
                reset_time=int(time.time()) + 3600,
                limit=999999
            )

        # 使用默认配置
        if config is None:
            config = RateLimitConfig(
                limit=settings.RATE_LIMIT_DEFAULT_REQUESTS,
                window=60,
                burst=settings.RATE_LIMIT_DEFAULT_BURST,
                block_duration=settings.RATE_LIMIT_BLOCK_DURATION
            )

        # 如果配置禁用限流，直接允许
        if not config.enabled:
            return RateLimitResult(
                allowed=True,
                remaining=999999,
                reset_time=int(time.time()) + 3600,
                limit=999999
            )

        try:
            # 构建限流键
            rate_limit_key = self._build_rate_limit_key(scope, identifier, endpoint, user_id)

            # 检查是否在黑名单中
            if await self.storage.is_blacklisted(identifier):
                logger.warning(f"IP {identifier} 在黑名单中，拒绝请求")
                return RateLimitResult(
                    allowed=False,
                    remaining=0,
                    reset_time=int(time.time()) + config.block_duration,
                    limit=0,
                    retry_after=config.block_duration
                )

            # 检查是否在白名单中
            if await self.storage.is_whitelisted(identifier):
                logger.info(f"IP {identifier} 在白名单中，允许请求")
                return RateLimitResult(
                    allowed=True,
                    remaining=999999,
                    reset_time=int(time.time()) + 3600,
                    limit=999999
                )

            # 获取算法实例
            algorithm_class = self.algorithms.get(algorithm, TokenBucket)

            if algorithm == "token_bucket":
                algorithm_instance = algorithm_class(
                    rate_limit_key, config.limit, config.window, config.burst
                )
            else:
                algorithm_instance = algorithm_class(
                    rate_limit_key, config.limit, config.window
                )

            # 执行限流检查
            allowed = await algorithm_instance.is_allowed(self.storage.redis_client)
            remaining = await algorithm_instance.get_remaining(self.storage.redis_client)
            reset_time = await algorithm_instance.get_reset_time(self.storage.redis_client)

            # 如果被限流，记录违规日志
            if not allowed and settings.RATE_LIMIT_LOG_VIOLATIONS:
                logger.warning(f"限流触发: key={rate_limit_key}, identifier={identifier}")

            retry_after = None
            if not allowed:
                retry_after = reset_time - int(time.time())

            return RateLimitResult(
                allowed=allowed,
                remaining=remaining,
                reset_time=reset_time,
                limit=config.limit,
                retry_after=retry_after
            )

        except Exception as e:
            logger.error(f"限流检查失败: {str(e)}")
            # 出现异常时允许请求通过，避免服务不可用
            return RateLimitResult(
                allowed=True,
                remaining=config.limit,
                reset_time=int(time.time()) + config.window,
                limit=config.limit
            )

    async def add_to_whitelist(self, identifier: str, expire_time: Optional[int] = None) -> bool:
        """
        添加到白名单

        Args:
            identifier: 标识符
            expire_time: 过期时间（秒）

        Returns:
            是否成功
        """
        return await self.storage.add_to_whitelist(identifier, expire_time)

    async def remove_from_whitelist(self, identifier: str) -> bool:
        """
        从白名单移除

        Args:
            identifier: 标识符

        Returns:
            是否成功
        """
        return await self.storage.remove_from_whitelist(identifier)

    async def add_to_blacklist(self, identifier: str, expire_time: Optional[int] = None) -> bool:
        """
        添加到黑名单

        Args:
            identifier: 标识符
            expire_time: 过期时间（秒）

        Returns:
            是否成功
        """
        return await self.storage.add_to_blacklist(identifier, expire_time)

    async def remove_from_blacklist(self, identifier: str) -> bool:
        """
        从黑名单移除

        Args:
            identifier: 标识符

        Returns:
            是否成功
        """
        return await self.storage.remove_from_blacklist(identifier)

    async def get_stats(self, scope: RateLimitScope, identifier: str,
                       endpoint: Optional[str] = None, user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        获取限流统计信息

        Args:
            scope: 限流作用域
            identifier: 标识符
            endpoint: API端点
            user_id: 用户ID

        Returns:
            统计信息
        """
        try:
            rate_limit_key = self._build_rate_limit_key(scope, identifier, endpoint, user_id)

            # 获取各种算法的基础统计信息
            stats = {
                "scope": scope.value,
                "identifier": identifier,
                "rate_limit_key": rate_limit_key,
                "whitelisted": await self.storage.is_whitelisted(identifier),
                "blacklisted": await self.storage.is_blacklisted(identifier)
            }

            return stats

        except Exception as e:
            logger.error(f"获取限流统计失败: {str(e)}")
            return {"error": str(e)}