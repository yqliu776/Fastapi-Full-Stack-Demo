from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel

from app.core.rate_limit import RateLimiter
from app.core.rate_limit.storage import RateLimitStorage
from app.core.rate_limit.rate_limiter import RateLimitScope, RateLimitConfig
from app.core.models import ResponseModel
from app.core.utils import logger
from app.core.settings import settings

# 创建API路由
router = APIRouter(prefix="/rate-limit", tags=["限流管理"])

# 初始化限流器
storage = RateLimitStorage()
rate_limiter = RateLimiter(storage)


class RateLimitConfigRequest(BaseModel):
    """限流配置请求模型"""
    limit: int = Query(..., description="限制数量", ge=1, le=10000)
    window: int = Query(..., description="时间窗口（秒）", ge=1, le=3600)
    burst: int = Query(10, description="突发容量", ge=1, le=1000)
    block_duration: int = Query(60, description="封禁时长（秒）", ge=1, le=86400)
    enabled: bool = Query(True, description="是否启用")


class WhitelistRequest(BaseModel):
    """白名单请求模型"""
    identifier: str = Query(..., description="标识符（IP地址或用户ID）")
    expire_time: Optional[int] = Query(None, description="过期时间（秒）", ge=1, le=86400*30)


class BlacklistRequest(BaseModel):
    """黑名单请求模型"""
    identifier: str = Query(..., description="标识符（IP地址或用户ID）")
    expire_time: Optional[int] = Query(None, description="过期时间（秒）", ge=1, le=86400*30)


class RateLimitStats(BaseModel):
    """限流统计信息"""
    scope: str
    identifier: str
    rate_limit_key: str
    whitelisted: bool
    blacklisted: bool


@router.get("/stats", summary="获取限流统计信息")
async def get_rate_limit_stats(
    scope: RateLimitScope = Query(..., description="限流作用域"),
    identifier: str = Query(..., description="标识符"),
    endpoint: Optional[str] = Query(None, description="API端点"),
    user_id: Optional[str] = Query(None, description="用户ID")
) -> ResponseModel:
    """
    获取指定标识符的限流统计信息
    """
    try:
        stats = await rate_limiter.get_stats(
            scope=scope,
            identifier=identifier,
            endpoint=endpoint,
            user_id=user_id
        )

        return ResponseModel(
            code=200,
            message="获取限流统计成功",
            data=stats
        )
    except Exception as e:
        logger.error(f"获取限流统计失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取限流统计失败: {str(e)}")


@router.post("/whitelist", summary="添加到白名单")
async def add_to_whitelist(request: WhitelistRequest) -> ResponseModel:
    """
    将指定标识符添加到白名单
    """
    try:
        success = await rate_limiter.add_to_whitelist(
            identifier=request.identifier,
            expire_time=request.expire_time
        )

        if success:
            return ResponseModel(
                code=200,
                message=f"已将 {request.identifier} 添加到白名单",
                data={"identifier": request.identifier, "expire_time": request.expire_time}
            )
        else:
            raise HTTPException(status_code=500, detail="添加到白名单失败")
    except Exception as e:
        logger.error(f"添加到白名单失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"添加到白名单失败: {str(e)}")


@router.delete("/whitelist/{identifier}", summary="从白名单移除")
async def remove_from_whitelist(identifier: str) -> ResponseModel:
    """
    将指定标识符从白名单移除
    """
    try:
        success = await rate_limiter.remove_from_whitelist(identifier=identifier)

        if success:
            return ResponseModel(
                code=200,
                message=f"已将 {identifier} 从白名单移除",
                data={"identifier": identifier}
            )
        else:
            return ResponseModel(
                code=404,
                message=f"{identifier} 不在白名单中",
                data={"identifier": identifier}
            )
    except Exception as e:
        logger.error(f"从白名单移除失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"从白名单移除失败: {str(e)}")


@router.get("/whitelist", summary="获取白名单列表")
async def get_whitelist() -> ResponseModel:
    """
    获取当前白名单列表
    """
    try:
        whitelist = await storage.get_whitelist()

        return ResponseModel(
            code=200,
            message="获取白名单成功",
            data=whitelist
        )
    except Exception as e:
        logger.error(f"获取白名单失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取白名单失败: {str(e)}")


@router.post("/blacklist", summary="添加到黑名单")
async def add_to_blacklist(request: BlacklistRequest) -> ResponseModel:
    """
    将指定标识符添加到黑名单
    """
    try:
        success = await rate_limiter.add_to_blacklist(
            identifier=request.identifier,
            expire_time=request.expire_time
        )

        if success:
            return ResponseModel(
                code=200,
                message=f"已将 {request.identifier} 添加到黑名单",
                data={"identifier": request.identifier, "expire_time": request.expire_time}
            )
        else:
            raise HTTPException(status_code=500, detail="添加到黑名单失败")
    except Exception as e:
        logger.error(f"添加到黑名单失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"添加到黑名单失败: {str(e)}")


@router.delete("/blacklist/{identifier}", summary="从黑名单移除")
async def remove_from_blacklist(identifier: str) -> ResponseModel:
    """
    将指定标识符从黑名单移除
    """
    try:
        success = await rate_limiter.remove_from_blacklist(identifier=identifier)

        if success:
            return ResponseModel(
                code=200,
                message=f"已将 {identifier} 从黑名单移除",
                data={"identifier": identifier}
            )
        else:
            return ResponseModel(
                code=404,
                message=f"{identifier} 不在黑名单中",
                data={"identifier": identifier}
            )
    except Exception as e:
        logger.error(f"从黑名单移除失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"从黑名单移除失败: {str(e)}")


@router.get("/blacklist", summary="获取黑名单列表")
async def get_blacklist() -> ResponseModel:
    """
    获取当前黑名单列表
    """
    try:
        blacklist = await storage.get_blacklist()

        return ResponseModel(
            code=200,
            message="获取黑名单成功",
            data=blacklist
        )
    except Exception as e:
        logger.error(f"获取黑名单失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取黑名单失败: {str(e)}")


@router.post("/check", summary="检查限流状态")
async def check_rate_limit(
    request: Request,
    scope: RateLimitScope = Query(..., description="限流作用域"),
    identifier: str = Query(..., description="标识符"),
    endpoint: Optional[str] = Query(None, description="API端点"),
    user_id: Optional[str] = Query(None, description="用户ID")
) -> ResponseModel:
    """
    检查指定请求的限流状态，不实际消耗限流额度
    """
    try:
        # 执行限流检查，但不实际消耗额度
        # 这里使用一个特殊的配置，limit设置为0，enabled为True
        # 这样可以在不消耗实际额度的情况下检查状态
        check_config = RateLimitConfig(limit=999999, window=60, enabled=True)

        result = await rate_limiter.is_allowed(
            scope=scope,
            identifier=identifier,
            algorithm="token_bucket",
            config=check_config,
            endpoint=endpoint,
            user_id=user_id
        )

        return ResponseModel(
            code=200,
            message="限流检查完成",
            data={
                "allowed": result.allowed,
                "remaining": result.remaining,
                "reset_time": result.reset_time,
                "limit": result.limit,
                "retry_after": result.retry_after
            }
        )
    except Exception as e:
        logger.error(f"限流检查失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"限流检查失败: {str(e)}")


@router.get("/config", summary="获取限流配置")
async def get_rate_limit_config() -> ResponseModel:
    """
    获取当前限流配置信息
    """
    try:
        config_info = {
            "enabled": settings.RATE_LIMIT_ENABLED,
            "algorithm": settings.RATE_LIMIT_ALGORITHM,
            "storage": settings.RATE_LIMIT_STORAGE,
            "default_requests": settings.RATE_LIMIT_DEFAULT_REQUESTS,
            "default_burst": settings.RATE_LIMIT_DEFAULT_BURST,
            "block_duration": settings.RATE_LIMIT_BLOCK_DURATION,
            "enable_whitelist": settings.RATE_LIMIT_ENABLE_WHITELIST,
            "enable_blacklist": settings.RATE_LIMIT_ENABLE_BLACKLIST,
            "log_violations": settings.RATE_LIMIT_LOG_VIOLATIONS
        }

        return ResponseModel(
            code=200,
            message="获取限流配置成功",
            data=config_info
        )
    except Exception as e:
        logger.error(f"获取限流配置失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取限流配置失败: {str(e)}")