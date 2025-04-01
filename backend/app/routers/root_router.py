from fastapi import APIRouter, HTTPException, Query
from app.services import RootService
from app.core.decorators import response_wrapper
from typing import Optional
import json
import os
from pathlib import Path

root_router = APIRouter(tags=["根路由"])
service = RootService()

@root_router.get("/")
@response_wrapper(message="S")
async def root():
    return {"status": "OK!"}

@root_router.get("/info")
@response_wrapper(message="获取系统信息成功")
async def info(field: Optional[str] = Query(None, description="要过滤的字段名称")):
    return await service.get_info(field)

