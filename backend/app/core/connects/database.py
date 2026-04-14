from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from typing import AsyncGenerator
import asyncio

from app.core.settings import settings
from app.core.utils import logger


class Database:
    """数据库连接管理类
    
    该类负责管理SQLAlchemy的异步数据库连接，提供数据库会话管理和连接池配置。
    使用懒加载模式，仅在首次使用时初始化数据库连接。
    支持MySQL和PostgresSQL。
    
    属性:
        engine: SQLAlchemy异步引擎实例
        AsyncSessionLocal: 异步会话制造工厂
        _base: SQLAlchemy声明性基类
    """

    def __init__(self):
        """初始化数据库管理器
        
        创建一个新的数据库管理器实例，但不会立即建立数据库连接。
        连接将在首次调用init_db()时创建。
        """
        self.engine = None
        self.AsyncSessionLocal = None
        self._base = declarative_base()

    def init_db(self):
        """初始化数据库连接
        
        创建数据库引擎和会话工厂。仅在首次调用时执行初始化。
        配置包括:
            - 连接池大小
            - 最大溢出连接数
            - 连接超时时间
            - SQL语句回显设置
        
        支持的数据库类型：MySQL和PostgresSQL
        """
        db_type = settings.DATABASE_TYPE
        logger.info(f"初始化{db_type.upper()}连接...")
        
        try:
            if not self.engine:
                db_url = settings.SQLALCHEMY_DATABASE_URL
                
                # 获取数据库连接参数
                if db_type == "mysql":
                    echo = settings.MYSQL_ECHO_SQL
                    pool_size = settings.MYSQL_POOL_SIZE
                    max_overflow = settings.MYSQL_MAX_OVERFLOW
                    pool_timeout = settings.MYSQL_POOL_TIMEOUT
                    db_url = db_url.replace("pymysql", "aiomysql")
                    connect_args = {"charset": "utf8mb4"}
                elif db_type == "postgresql":
                    echo = settings.POSTGRES_ECHO_SQL
                    pool_size = settings.POSTGRES_POOL_SIZE
                    max_overflow = settings.POSTGRES_MAX_OVERFLOW
                    pool_timeout = settings.POSTGRES_POOL_TIMEOUT
                    connect_args = None
                else:
                    raise ValueError(f"不支持的数据库类型: {db_type}")
                
                engine_kwargs = {
                    "echo": echo,
                    "pool_size": pool_size,
                    "max_overflow": max_overflow,
                    "pool_timeout": pool_timeout
                }
                if connect_args:
                    engine_kwargs["connect_args"] = connect_args
                
                self.engine = create_async_engine(db_url, **engine_kwargs)
                
                self.AsyncSessionLocal = async_sessionmaker(
                    self.engine,
                    class_=AsyncSession,
                    expire_on_commit=False
                )
                logger.info(f"{db_type.upper()}连接初始化成功")

        except Exception as e:
            logger.error(f"数据库连接初始化失败: {str(e)}")
            raise

    @property
    def base(self):
        """获取SQLAlchemy声明性基类
        
        Returns:
            declarative_base: SQLAlchemy声明性基类，用于创建模型类
        """
        return self._base

    _init_lock = asyncio.Lock()

    async def get_db(self) -> AsyncGenerator[AsyncSession, None]:
        """创建数据库会话的异步生成器"""
        if not self.AsyncSessionLocal:
            async with self._init_lock:
                if not self.AsyncSessionLocal:
                    self.init_db()
            
        async with self.AsyncSessionLocal() as session:
            try:
                yield session
            finally:
                await session.close()

    async def close(self):
        """关闭数据库连接
        
        关闭数据库引擎和所有活动连接。应在应用程序关闭时调用。
        """
        if self.engine:
            await self.engine.dispose()
            self.engine = None
            self.AsyncSessionLocal = None

# 创建数据库实例
db = Database()
Base = db.base
