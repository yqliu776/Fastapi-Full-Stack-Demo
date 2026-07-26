import json
from typing import Any, Dict, Literal

from pydantic import BaseModel, Field

from app.core.connects import redis_client
from app.core.settings import settings
from app.core.utils import logger


RATE_LIMIT_CONFIG_KEY = "rate_limit:runtime_config"


class RuntimeRateLimitConfig(BaseModel):
    """运行时限流配置"""

    enabled: bool = Field(True, description="是否启用限流")
    algorithm: Literal["token_bucket", "sliding_window", "fixed_window"] = Field(
        "token_bucket",
        description="限流算法"
    )
    storage: Literal["redis", "memory"] = Field("redis", description="存储方式")
    default_requests: int = Field(100, ge=1, le=10000, description="默认每分钟请求数")
    default_burst: int = Field(10, ge=1, le=1000, description="突发容量")
    block_duration: int = Field(60, ge=1, le=86400, description="封禁时长")
    enable_whitelist: bool = Field(True, description="是否启用白名单")
    enable_blacklist: bool = Field(True, description="是否启用黑名单")
    log_violations: bool = Field(True, description="是否记录违规日志")


def get_default_rate_limit_config() -> RuntimeRateLimitConfig:
    return RuntimeRateLimitConfig(
        enabled=settings.RATE_LIMIT_ENABLED,
        algorithm=settings.RATE_LIMIT_ALGORITHM,
        storage=settings.RATE_LIMIT_STORAGE,
        default_requests=settings.RATE_LIMIT_DEFAULT_REQUESTS,
        default_burst=settings.RATE_LIMIT_DEFAULT_BURST,
        block_duration=settings.RATE_LIMIT_BLOCK_DURATION,
        enable_whitelist=settings.RATE_LIMIT_ENABLE_WHITELIST,
        enable_blacklist=settings.RATE_LIMIT_ENABLE_BLACKLIST,
        log_violations=settings.RATE_LIMIT_LOG_VIOLATIONS
    )


async def get_runtime_rate_limit_config() -> RuntimeRateLimitConfig:
    config = get_default_rate_limit_config()

    try:
        redis = await redis_client.get_redis()
        raw_config = await redis.get(RATE_LIMIT_CONFIG_KEY)
        if not raw_config:
            return config

        saved_config: Dict[str, Any] = json.loads(raw_config)
        return RuntimeRateLimitConfig.model_validate({
            **config.model_dump(),
            **saved_config
        })
    except Exception as exc:
        logger.error(f"读取运行时限流配置失败: {str(exc)}")
        return config


async def save_runtime_rate_limit_config(config: RuntimeRateLimitConfig) -> RuntimeRateLimitConfig:
    redis = await redis_client.get_redis()
    await redis.set(RATE_LIMIT_CONFIG_KEY, json.dumps(config.model_dump(), ensure_ascii=False))
    return config
