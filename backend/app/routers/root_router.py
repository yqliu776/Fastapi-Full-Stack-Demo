from fastapi import APIRouter, HTTPException
from app.services import RootService
from app.core.decorators import response_wrapper

root_router = APIRouter(tags=["根路由"])
service = RootService()

@root_router.get("/")
@response_wrapper(message="系统正常运行中")
async def root():
    return {"status": "OK!"}

@root_router.get("/info")
@response_wrapper(message="获取系统信息成功")
async def info():
    try:
        return await service.get_info()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    
