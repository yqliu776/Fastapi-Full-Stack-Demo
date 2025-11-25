import time
import math
from abc import ABC, abstractmethod
from typing import Optional

from app.core.utils import logger


class RateLimitAlgorithm(ABC):
    """限流算法基类"""

    def __init__(self, key: str, limit: int, window: int = 60):
        """
        初始化限流算法

        Args:
            key: 限流键
            limit: 限制数量
            window: 时间窗口（秒）
        """
        self.key = key
        self.limit = limit
        self.window = window

    @abstractmethod
    async def is_allowed(self, redis_client) -> bool:
        """检查是否允许请求"""
        pass

    @abstractmethod
    async def get_remaining(self, redis_client) -> int:
        """获取剩余可用次数"""
        pass

    @abstractmethod
    async def get_reset_time(self, redis_client) -> int:
        """获取重置时间戳"""
        pass


class TokenBucket(RateLimitAlgorithm):
    """令牌桶算法"""

    def __init__(self, key: str, limit: int, window: int = 60, burst: int = 10):
        """
        初始化令牌桶

        Args:
            key: 限流键
            limit: 每秒生成的令牌数
            window: 时间窗口（秒）
            burst: 桶的容量（突发流量）
        """
        super().__init__(key, limit, window)
        self.burst = burst
        self.tokens_key = f"rate_limit:tokens:{key}"
        self.last_refill_key = f"rate_limit:last_refill:{key}"

    async def is_allowed(self, redis_client) -> bool:
        """检查是否允许请求"""
        try:
            redis = await redis_client.get_redis()

            # 获取当前令牌数和上次填充时间
            tokens_data = await redis.mget(self.tokens_key, self.last_refill_key)
            current_tokens = float(tokens_data[0]) if tokens_data[0] else self.burst
            last_refill = float(tokens_data[1]) if tokens_data[1] else time.time()

            now = time.time()
            time_passed = now - last_refill

            # 计算新添加的令牌数
            tokens_to_add = time_passed * (self.limit / self.window)
            current_tokens = min(current_tokens + tokens_to_add, self.burst)

            # 检查是否有足够的令牌
            if current_tokens >= 1:
                current_tokens -= 1
                # 更新令牌数和填充时间
                await redis.mset({
                    self.tokens_key: current_tokens,
                    self.last_refill_key: now
                })
                # 设置过期时间
                await redis.expire(self.tokens_key, self.window * 2)
                await redis.expire(self.last_refill_key, self.window * 2)
                return True
            else:
                # 更新填充时间
                await redis.set(self.last_refill_key, now, ex=self.window * 2)
                return False

        except Exception as e:
            logger.error(f"令牌桶算法执行失败: {str(e)}")
            # 出现异常时允许请求通过，避免服务不可用
            return True

    async def get_remaining(self, redis_client) -> int:
        """获取剩余令牌数"""
        try:
            redis = await redis_client.get_redis()
            tokens_data = await redis.mget(self.tokens_key, self.last_refill_key)
            current_tokens = float(tokens_data[0]) if tokens_data[0] else self.burst
            return max(0, int(current_tokens))
        except Exception:
            return self.limit

    async def get_reset_time(self, redis_client) -> int:
        """获取令牌桶重置时间"""
        try:
            redis = await redis_client.get_redis()
            last_refill = await redis.get(self.last_refill_key)
            if last_refill:
                return int(float(last_refill)) + self.window
            return int(time.time()) + self.window
        except Exception:
            return int(time.time()) + self.window


class SlidingWindow(RateLimitAlgorithm):
    """滑动窗口算法"""

    def __init__(self, key: str, limit: int, window: int = 60):
        """
        初始化滑动窗口

        Args:
            key: 限流键
            limit: 时间窗口内的最大请求数
            window: 时间窗口（秒）
        """
        super().__init__(key, limit, window)
        self.requests_key = f"rate_limit:requests:{key}"

    async def is_allowed(self, redis_client) -> bool:
        """检查是否允许请求"""
        try:
            redis = await redis_client.get_redis()
            now = time.time()

            # 移除过期的请求记录
            await redis.zremrangebyscore(self.requests_key, 0, now - self.window)

            # 获取当前窗口内的请求数
            current_requests = await redis.zcard(self.requests_key)

            if current_requests < self.limit:
                # 添加当前请求
                await redis.zadd(self.requests_key, {str(now): now})
                # 设置过期时间
                await redis.expire(self.requests_key, self.window + 1)
                return True
            else:
                return False

        except Exception as e:
            logger.error(f"滑动窗口算法执行失败: {str(e)}")
            return True

    async def get_remaining(self, redis_client) -> int:
        """获取剩余可用次数"""
        try:
            redis = await redis_client.get_redis()
            now = time.time()

            # 移除过期的请求记录
            await redis.zremrangebyscore(self.requests_key, 0, now - self.window)

            # 获取当前窗口内的请求数
            current_requests = await redis.zcard(self.requests_key)
            return max(0, self.limit - current_requests)
        except Exception:
            return self.limit

    async def get_reset_time(self, redis_client) -> int:
        """获取窗口重置时间"""
        try:
            redis = await redis_client.get_redis()
            now = time.time()

            # 获取最早的请求时间
            earliest_requests = await redis.zrange(self.requests_key, 0, 0, withscores=True)
            if earliest_requests:
                earliest_time = earliest_requests[0][1]
                return int(earliest_time) + self.window
            return int(now) + self.window
        except Exception:
            return int(time.time()) + self.window


class FixedWindow(RateLimitAlgorithm):
    """固定窗口算法"""

    def __init__(self, key: str, limit: int, window: int = 60):
        """
        初始化固定窗口

        Args:
            key: 限流键
            limit: 时间窗口内的最大请求数
            window: 时间窗口（秒）
        """
        super().__init__(key, limit, window)
        self.counter_key = f"rate_limit:counter:{key}"

    async def is_allowed(self, redis_client) -> bool:
        """检查是否允许请求"""
        try:
            redis = await redis_client.get_redis()
            now = time.time()

            # 计算当前窗口的起始时间
            window_start = int(now // self.window) * self.window
            window_key = f"{self.counter_key}:{window_start}"

            # 获取当前窗口的请求数
            current_count = await redis.get(window_key)
            current_count = int(current_count) if current_count else 0

            if current_count < self.limit:
                # 增加计数
                await redis.incr(window_key)
                # 设置过期时间
                await redis.expire(window_key, self.window + 1)
                return True
            else:
                return False

        except Exception as e:
            logger.error(f"固定窗口算法执行失败: {str(e)}")
            return True

    async def get_remaining(self, redis_client) -> int:
        """获取剩余可用次数"""
        try:
            redis = await redis_client.get_redis()
            now = time.time()

            # 计算当前窗口的起始时间
            window_start = int(now // self.window) * self.window
            window_key = f"{self.counter_key}:{window_start}"

            # 获取当前窗口的请求数
            current_count = await redis.get(window_key)
            current_count = int(current_count) if current_count else 0

            return max(0, self.limit - current_count)
        except Exception:
            return self.limit

    async def get_reset_time(self, redis_client) -> int:
        """获取窗口重置时间"""
        try:
            now = time.time()
            # 计算当前窗口的结束时间
            window_end = (int(now // self.window) + 1) * self.window
            return int(window_end)
        except Exception:
            return int(time.time()) + self.window