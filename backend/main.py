import time
import uvicorn
from app import AppLifecycle

# 创建应用实例
app = AppLifecycle.create_app()

if __name__ == "__main__":
    # 启动应用服务器
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )
