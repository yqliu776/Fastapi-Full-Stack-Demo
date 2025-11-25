from typing import Optional, Dict, Any, Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import time

from app.core.rate_limit import RateLimiter
from app.core.rate_limit.storage import RateLimitStorage
from app.core.rate_limit.rate_limiter import RateLimitScope, RateLimitConfig
from app.core.models import ResponseModel
from app.core.settings import settings
from app.core.utils import logger


class RateLimitMiddleware(BaseHTTPMiddleware):
    """限流中间件"""

    def __init__(self, app):
        """初始化限流中间件"""
        super().__init__(app)
        self.storage = RateLimitStorage()
        self.rate_limiter = RateLimiter(self.storage)

        # 限流规则配置
        self.rate_limit_rules = {
            # 全局限流规则
            "/auth/login": RateLimitConfig(limit=10, window=60, enabled=True),  # 登录接口
            "/auth/register": RateLimitConfig(limit=5, window=60, enabled=True),  # 注册接口
            "/auth/refresh": RateLimitConfig(limit=20, window=60, enabled=True),  # 刷新token

            # 用户管理相关
            "/users/register": RateLimitConfig(limit=5, window=3600, enabled=True),  # 用户注册

            # 默认规则
            "default": RateLimitConfig(
                limit=settings.RATE_LIMIT_DEFAULT_REQUESTS,
                window=60,
                burst=settings.RATE_LIMIT_DEFAULT_BURST,
                enabled=True
            )
        }

        # 排除不需要限流的路径
        self.exclude_paths = [
            "/health",
            "/metrics",
            "/docs",
            "/openapi.json",
            "/favicon.ico",
            "/api/docs",
            "/api/redoc",
            "/api/v1/openapi.json"
        ]

    def should_rate_limit(self, path: str) -> bool:
        """
        判断是否需要限流

        Args:
            path: 请求路径

        Returns:
            是否需要限流
        """
        # 检查是否在排除路径中
        for exclude_path in self.exclude_paths:
            if path.startswith(exclude_path):
                return False

        return True

    def get_client_ip(self, request: Request) -> str:
        """
        获取客户端真实IP地址

        Args:
            request: FastAPI请求对象

        Returns:
            客户端IP地址
        """
        # 优先检查 X-Forwarded-For 头
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # 取第一个IP地址
            return forwarded_for.split(",")[0].strip()

        # 检查 X-Real-IP 头
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip.strip()

        # 使用直接连接的客户端IP
        if request.client:
            return request.client.host

        # 默认返回未知IP
        return "unknown"

    def get_user_id(self, request: Request) -> Optional[str]:
        """
        获取用户ID

        Args:
            request: FastAPI请求对象

        Returns:
            用户ID，如果未登录返回None
        """
        try:
            # 从请求头中获取用户信息（如果有的话）
            # 这里可以根据实际的认证机制来获取用户ID
            authorization = request.headers.get("Authorization")
            if authorization and authorization.startswith("Bearer "):
                # 这里可以解析JWT token获取用户ID
                # 简化处理，返回token的一部分作为用户标识
                return authorization.split(" ")[1][:20]  # 取token前20位作为用户标识
            return None
        except Exception:
            return None

    def get_rate_limit_config(self, path: str, method: str = "GET") -> RateLimitConfig:
        """
        获取限流配置

        Args:
            path: 请求路径
            method: 请求方法

        Returns:
            限流配置
        """
        # 精确匹配
        if path in self.rate_limit_rules:
            return self.rate_limit_rules[path]

        # 前缀匹配
        for rule_path, config in self.rate_limit_rules.items():
            if path.startswith(rule_path):
                return config

        # 返回默认配置
        return self.rate_limit_rules["default"]

    def build_rate_limit_info(self, result: Any, config: RateLimitConfig) -> Dict[str, str]:
        """
        构建限流信息头

        Args:
            result: 限流结果
            config: 限流配置

        Returns:
            限流信息头字典
        """
        return {
            "X-RateLimit-Limit": str(config.limit),
            "X-RateLimit-Remaining": str(result.remaining),
            "X-RateLimit-Reset": str(result.reset_time),
            "X-RateLimit-Reset-After": str(max(0, result.reset_time - int(time.time())))
        }

    async def dispatch(self, request: Request, call_next) -> Response:
        """
        处理限流逻辑

        Args:
            request: FastAPI请求对象
            call_next: 下一个中间件

        Returns:
            响应对象
        """
        # 检查是否需要限流
        if not self.should_rate_limit(request.url.path):
            return await call_next(request)

        # 如果全局禁用限流，直接通过
        if not settings.RATE_LIMIT_ENABLED:
            return await call_next(request)

        try:
            # 获取客户端信息
            client_ip = self.get_client_ip(request)
            user_id = self.get_user_id(request)
            endpoint = request.url.path
            method = request.method

            # 获取限流配置
            config = self.get_rate_limit_config(endpoint, method)

            # 根据配置决定限流策略
            # 这里使用IP限流为主，用户限流为辅的策略
            scope = RateLimitScope.IP
            identifier = client_ip

            # 如果有用户ID，使用用户+IP的组合限流
            if user_id:
                scope = RateLimitScope.IP_USER
                identifier = client_ip

            # 执行限流检查
            result = await self.rate_limiter.is_allowed(
                scope=scope,
                identifier=identifier,
                algorithm=settings.RATE_LIMIT_ALGORITHM,
                config=config,
                endpoint=endpoint,
                user_id=user_id
            )

            # 构建限流信息头
            rate_limit_headers = self.build_rate_limit_info(result, config)

            # 如果被限流，返回限流响应
            if not result.allowed:
                retry_after = result.retry_after or config.block_duration

                # 记录限流日志
                logger.warning(
                    f"请求被限流: IP={client_ip}, User={user_id}, "
                    f"Endpoint={endpoint}, Retry-After={retry_after}s"
                )

                # 返回限流响应
                response = ResponseModel(
                    code=429,
                    message=f"请求过于频繁，请 {retry_after} 秒后再试",
                    data={
                        "retry_after": retry_after,
                        "limit": config.limit,
                        "window": config.window
                    }
                )

                return JSONResponse(
                    status_code=429,
                    content=response.model_dump(),
                    headers={
                        **rate_limit_headers,
                        "Retry-After": str(retry_after),
                        "Content-Type": "application/json"
                    }
                )

            # 请求被允许，继续处理
            response = await call_next(request)

            # 添加限流信息头到响应
            for header_name, header_value in rate_limit_headers.items():
                response.headers[header_name] = header_value

            return response

        except Exception as e:
            logger.error(f"限流中间件处理失败: {str(e)}")
            # 出现异常时允许请求通过，避免服务不可用
            return await call_next(request)


def rate_limit_decorator(
    limit: int = 100,
    window: int = 60,
    burst: int = 10,
    scope: RateLimitScope = RateLimitScope.IP,
    algorithm: str = "token_bucket",
    enabled: bool = True
):
    """
    限流装饰器

    Args:
        limit: 限制数量
        window: 时间窗口（秒）
        burst: 突发容量
        scope: 限流作用域
        algorithm: 限流算法
        enabled: 是否启用

    Returns:
        装饰器函数
    """
    def decorator(func: Callable) -> Callable:
        async def wrapper(*args, **kwargs):
            if not enabled:
                return await func(*args, **kwargs)

            # 这里需要实现装饰器的具体逻辑
            # 由于装饰器需要访问请求对象，实现会比较复杂
            # 建议使用中间件方式
            return await func(*args, **kwargs)
        return wrapper
    return decorator