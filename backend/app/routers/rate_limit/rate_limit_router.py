from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel, Field

from app.core.rate_limit import RateLimiter
from app.core.rate_limit.storage import RateLimitStorage
from app.core.rate_limit.rate_limiter import RateLimitScope, RateLimitConfig
from app.core.rate_limit.runtime_config import (
    RuntimeRateLimitConfig,
    get_runtime_rate_limit_config,
    save_runtime_rate_limit_config
)
from app.core.decorators import has_permission
from app.core.models import ResponseModel
from app.core.utils import logger

# 创建API路由
router = APIRouter(
    prefix="/rate-limit",
    tags=["限流管理"],
    dependencies=[Depends(has_permission(["RATE_LIMIT_MANAGE"]))]
)

# 初始化限流器
storage = RateLimitStorage()
rate_limiter = RateLimiter(storage)


class WhitelistRequest(BaseModel):
    """白名单请求模型"""
    identifier: str = Field(..., description="标识符（IP地址或用户ID）")
    expire_time: Optional[int] = Field(None, description="过期时间（秒）", ge=1, le=86400*30)


class BlacklistRequest(BaseModel):
    """黑名单请求模型"""
    identifier: str = Field(..., description="标识符（IP地址或用户ID）")
    expire_time: Optional[int] = Field(None, description="过期时间（秒）", ge=1, le=86400*30)


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
    except HTTPException:
        raise
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
            raise HTTPException(status_code=404, detail=f"{identifier} 不在白名单中")
    except HTTPException:
        raise
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
    except HTTPException:
        raise
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
            raise HTTPException(status_code=404, detail=f"{identifier} 不在黑名单中")
    except HTTPException:
        raise
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
        runtime_config = await get_runtime_rate_limit_config()
        check_config = RateLimitConfig(
            limit=runtime_config.default_requests,
            window=60,
            burst=runtime_config.default_burst,
            block_duration=runtime_config.block_duration,
            enabled=runtime_config.enabled,
            enable_whitelist=runtime_config.enable_whitelist,
            enable_blacklist=runtime_config.enable_blacklist,
            log_violations=runtime_config.log_violations
        )

        result = await rate_limiter.is_allowed(
            scope=scope,
            identifier=identifier,
            algorithm=runtime_config.algorithm,
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
        config_info = await get_runtime_rate_limit_config()

        return ResponseModel(
            code=200,
            message="获取限流配置成功",
            data=config_info.model_dump()
        )
    except Exception as e:
        logger.error(f"获取限流配置失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取限流配置失败: {str(e)}")


@router.put("/config", summary="更新限流配置")
async def update_rate_limit_config(config: RuntimeRateLimitConfig) -> ResponseModel:
    """
    更新运行时限流配置，保存后立即生效并持久化到Redis。
    """
    try:
        saved_config = await save_runtime_rate_limit_config(config)
        return ResponseModel(
            code=200,
            message="限流配置保存成功",
            data=saved_config.model_dump()
        )
    except Exception as e:
        logger.error(f"保存限流配置失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"保存限流配置失败: {str(e)}")
