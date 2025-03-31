from .base_service import BaseService
from typing import Optional, Dict, Any

class RootService(BaseService):

    def __init__(self):
        pass

    async def get_info(self, field: Optional[str] = None):
        fields = ["runtime", "status", "resources"]
        result = {}
        if field is None:
            for field in fields:
                result[field] = await self._get_field_info(field)
        else:
            result[field] = await self._get_field_info(field)
            result["aviliable"] = fields
    
        return result
    
    async def _get_field_info(self, field: str):
        if field == "runtime":
            return await self._get_runtime_info()
        elif field == "status":
            return self._get_status_info()
        elif field == "resources":
            return await self._get_resources_info()
        else:
            return {"Error": f"{field}:参数不可用！"}
        
    async def _get_runtime_info(self):
        import psutil
        from datetime import datetime
        from app.core.utils import tzu
        
        # 获取系统启动时间和当前时间计算运行时间
        boot_time = datetime.fromtimestamp(psutil.boot_time())
        now = tzu.get_now()

        uptime = tzu.time_diff(now, boot_time)
        
        return {
            "system_uptime": str(uptime),
            "boot_time": tzu.format_time(boot_time),
            "current_time": tzu.format_time(now)
        }
    
    def _get_status_info(self):
        return {
            "system": "运行正常",
            "api": "可用"
        }
    
    async def _get_resources_info(self):
        import psutil
        
        # 系统资源信息
        cpu_usage = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return {
            "cpu_usage": f"{cpu_usage}%",
            "memory": {
                "total": f"{memory.total / (1024**3):.2f} GB",
                "used": f"{memory.used / (1024**3):.2f} GB",
                "percent": f"{memory.percent}%"
            },
            "disk": {
                "total": f"{disk.total / (1024**3):.2f} GB",
                "used": f"{disk.used / (1024**3):.2f} GB",
                "percent": f"{disk.percent}%"
            }
        }