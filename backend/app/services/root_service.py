from .base_service import BaseService

class RootService(BaseService):

    def __init__(self):
        pass

    async def get_info(self):
        import psutil
        from datetime import datetime

        # 获取系统启动时间和当前时间计算运行时间
        boot_time = datetime.fromtimestamp(psutil.boot_time())
        now = datetime.now()
        uptime = now - boot_time
            
        # 系统资源信息
        cpu_usage = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')

        runtime = {
            "system_uptime": str(uptime),
            "boot_time": boot_time.strftime("%Y-%m-%d %H:%M:%S"),
            "current_time": now.strftime("%Y-%m-%d %H:%M:%S")
        }

        status = {
            "system": "运行正常",
            "api": "可用"
        }
        
        resources = {
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

        return {
            "runtime": runtime,
            "status": status,
            "resources": resources
        }