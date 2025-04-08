from contextlib import asynccontextmanager
from typing import Callable, Awaitable, Optional
from fastapi import FastAPI, APIRouter
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from app.core.connects import db, redis_client
from app.core.utils import logger_manager, logger
from app.core.middleware import LoggingMiddleware
from app.core.middleware import ErrorHandlerMiddleware
from app.core.settings import settings
from app.routers import auth_router, role_router, permission_router, menu_router


class AppLifecycle:
    """FastAPI 应用程序生命周期控制器。

    该类负责管理 FastAPI 应用程序的启动和关闭生命周期事件。

    Attributes:
        on_startup (Optional[Callable[[], Awaitable[None]]]): 应用启动时执行的异步回调函数
        on_shutdown (Optional[Callable[[], Awaitable[None]]]): 应用关闭时执行的异步回调函数

    Example:
        ```python
        lifecycle = AppLifecycle(
            on_startup=my_startup_handler,
            on_shutdown=my_shutdown_handler
        )
        app = FastAPI(lifespan=lifecycle.lifespan)
        ```
    """

    def __init__(self,
                 on_startup: Optional[Callable[[], Awaitable[None]]] = None,
                 on_shutdown: Optional[Callable[[], Awaitable[None]]] = None
                 ):
        """初始化生命周期控制器。

        Args:
            on_startup: 可选的应用启动回调函数
            on_shutdown: 可选的应用关闭回调函数
        """
        self.on_startup = on_startup
        self.on_shutdown = on_shutdown

    @staticmethod
    async def on_startup():
        """默认的应用启动回调函数。

        此方法可作为默认的启动处理程序，初始化数据库连接并执行其他启动操作。
        """
        logger.info("执行自定义启动操作...")
        # 初始化数据库连接
        db.init_db()
        logger.info("数据库连接已初始化")
        
        # 初始化Redis连接
        await redis_client.init_redis()
        logger.info("Redis连接已初始化")

    @staticmethod
    async def shutdown():
        """默认的应用关闭回调函数。

        此方法可作为默认的关闭处理程序，关闭数据库连接并执行其他清理操作。
        """
        logger.info("执行自定义关闭操作...")
        # 关闭数据库连接
        await db.close()
        logger.info("数据库连接已关闭")
        
        # 关闭Redis连接
        await redis_client.close()
        logger.info("Redis连接已关闭")

    @asynccontextmanager
    async def lifespan(self, _app: FastAPI):
        """应用程序生命周期管理器。

        实现 FastAPI 的生命周期管理协议，处理应用的启动和关闭事件。

        Args:
            _app: FastAPI 应用实例

        Yields:
            None: 用于上下文管理器的占位符

        Raises:
            Exception: 当启动或关闭过程中发生错误时抛出
        """
        try:
            logger.info("应用程序正在启动...")
            if self.on_startup:
                await self.on_startup()
            logger.info("应用程序启动完成")
            yield
        except Exception as e:
            logger.info(f"应用程序运行时发生错误: {str(e)}")
            raise
        finally:
            try:
                logger.info("应用程序正在关闭...")
                if self.on_shutdown:
                    await self.on_shutdown()
                logger.info("应用程序已成功关闭")
            except Exception as e:
                logger.error(f"应用程序关闭时发生错误: {str(e)}")
                raise

    @staticmethod
    def create_app():
        """创建并配置 FastAPI 应用实例。

        Returns:
            FastAPI: 配置好生命周期管理和中间件的 FastAPI 应用实例
        """
        lifecycle = AppLifecycle(on_startup=AppLifecycle.on_startup, on_shutdown=AppLifecycle.shutdown)
        
        # 创建FastAPI应用，配置Swagger和OpenAPI
        app = FastAPI(
            lifespan=lifecycle.lifespan,
            # 应用基本信息配置
            title="fast-full-stack-backend",  # API文档标题
            description="框架后端服务API文档，提供所有接口的详细说明和测试功能",  # API文档描述
            version="0.1.0",  # API版本
            
            # OpenAPI配置
            openapi_url="/api/v1/openapi.json",  # OpenAPI JSON的访问路径
            openapi_tags=[  # API标签分组信息
                {
                    "name": "认证",
                    "description": "认证相关接口",
                },
                {
                    "name": "角色管理",
                    "description": "角色管理相关接口",
                },
                {
                    "name": "权限管理",
                    "description": "权限管理相关接口",
                },
                {
                    "name": "菜单管理",
                    "description": "菜单管理相关接口",
                },
                # 可以添加更多标签分组
            ],
            
            # Swagger UI配置
            docs_url="/api/docs",  # Swagger UI访问路径
            swagger_ui_oauth2_redirect_url="/api/docs/oauth2-redirect",  # OAuth2重定向URL
            swagger_ui_parameters={
                "defaultModelsExpandDepth": -1,  # 默认模型展开深度，-1表示不展开
                "persistAuthorization": True,  # 保存授权信息
                "syntaxHighlight.theme": "obsidian",  # 语法高亮主题
                "docExpansion": "none",  # 文档默认展开状态，none表示折叠所有
            },
            
            # Redoc UI配置
            redoc_url="/api/redoc",  # ReDoc文档访问路径
            
            # 安全定义
            swagger_ui_init_oauth={
                "usePkceWithAuthorizationCodeGrant": False,
                "clientId": "",
                "clientSecret": "",
                "realm": "",
                "appName": "后端API认证",
                "scopeSeparator": " ",
                "scopes": "",
                "useBasicAuthenticationWithAccessCodeGrant": True,
            },
        )

        # 配置OAuth2安全定义 - 在路由前设置
        oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login/oauth")
        
        # 修改OpenAPI架构，添加安全定义
        def custom_openapi():
            if not hasattr(app, 'openapi_schema') or app.openapi_schema is None:
                # 保存原始的方法引用
                original_openapi = app.openapi
                
                # 创建一个新的函数以避免递归
                def get_openapi():
                    from fastapi.openapi.utils import get_openapi
                    
                    return get_openapi(
                        title=app.title,
                        version=app.version,
                        description=app.description,
                        routes=app.routes,
                        tags=app.openapi_tags,
                        servers=app.servers,
                    )
                
                # 获取基础OpenAPI架构
                openapi_schema = get_openapi()
                
                # 安全方案定义
                security_schemes = {
                    "OAuth2PasswordBearer": {
                        "type": "oauth2",
                        "flows": {
                            "password": {
                                "tokenUrl": "/auth/login/oauth",
                                "scopes": {}
                            }
                        }
                    }
                }
                
                # 全局安全需求
                security_requirement = [{"OAuth2PasswordBearer": []}]
                
                # 添加安全方案
                if "components" not in openapi_schema:
                    openapi_schema["components"] = {}
                    
                openapi_schema["components"]["securitySchemes"] = security_schemes
                openapi_schema["security"] = security_requirement
                
                # 缓存结果
                app.openapi_schema = openapi_schema
                
            return app.openapi_schema
        
        # 替换OpenAPI生成函数
        app.openapi = custom_openapi
        
        # 添加路由 - 需要在定义openapi后添加路由
        router_list = [
            auth_router,
            role_router,
            permission_router,
            menu_router
        ]
        for router in router_list:
            app.include_router(router)
        
        # 添加中间件 - 标准ASGI中间件的添加方式
        app.add_middleware(ErrorHandlerMiddleware)
        app.add_middleware(
            LoggingMiddleware,
            logger_manager=logger_manager,
            formatted_output=settings.FORMATTED_OUTPUT,
        )
        
        # 添加CORS中间件
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.BACKEND_CORS_ORIGINS,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        return app