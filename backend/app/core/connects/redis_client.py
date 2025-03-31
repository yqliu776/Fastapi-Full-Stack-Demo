import redis
from redis.asyncio import Redis, ConnectionPool
from app.core.settings import settings
from app.core.utils import logger


class RedisClient:
    """Redis客户端连接管理类
    
    提供Redis连接池和客户端管理功能，支持同步和异步操作
    """
    
    _pool: ConnectionPool = None
    _sync_client: redis.Redis = None
    
    @classmethod
    async def init_redis(cls):
        """初始化Redis连接池和客户端"""
        logger.info("初始化Redis连接...")
        try:
            # 初始化异步连接池
            cls._pool = ConnectionPool(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                password=settings.REDIS_PASSWORD,
                db=settings.REDIS_DB,
                decode_responses=True,  # 自动解码为字符串
                socket_timeout=settings.REDIS_TIMEOUT,
                socket_connect_timeout=settings.REDIS_TIMEOUT,
            )
            
            # 初始化同步客户端
            cls._sync_client = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                password=settings.REDIS_PASSWORD,
                db=settings.REDIS_DB,
                decode_responses=True,
                socket_timeout=settings.REDIS_TIMEOUT,
                socket_connect_timeout=settings.REDIS_TIMEOUT,
            )
            
            # 测试连接是否成功
            if await cls.ping():
                logger.info("Redis连接初始化成功")
            else:
                logger.error("Redis连接测试失败")
        except Exception as e:
            logger.error(f"Redis连接初始化失败: {str(e)}")
            raise

    # noinspection PyTypeChecker
    @classmethod
    async def close(cls):
        """关闭Redis连接"""
        logger.info("关闭Redis连接...")
        if cls._pool:
            await cls._pool.disconnect()
            cls._pool = None
        
        if cls._sync_client:
            cls._sync_client.close()
            cls._sync_client = None
        logger.info("Redis连接已关闭")
    
    @classmethod
    async def get_redis(cls) -> Redis:
        """获取异步Redis客户端
        
        Returns:
            Redis: 异步Redis客户端实例
        """
        if not cls._pool:
            await cls.init_redis()
        return Redis(connection_pool=cls._pool)
    
    @classmethod
    def get_sync_redis(cls) -> redis.Redis:
        """获取同步Redis客户端
        
        Returns:
            redis.Redis: 同步Redis客户端实例
        """
        if not cls._sync_client:
            cls._sync_client = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                password=settings.REDIS_PASSWORD,
                db=settings.REDIS_DB,
                decode_responses=True,
                socket_timeout=settings.REDIS_TIMEOUT,
                socket_connect_timeout=settings.REDIS_TIMEOUT,
            )
        return cls._sync_client
    
    @classmethod
    async def ping(cls) -> bool:
        """测试Redis连接是否正常
        
        Returns:
            bool: 连接正常返回True，否则返回False
        """
        try:
            _redis_client = await cls.get_redis()
            result = await _redis_client.ping()
            return result == True
        except Exception as e:
            logger.error(f"Redis ping失败: {str(e)}")
            return False


redis_client = RedisClient() 