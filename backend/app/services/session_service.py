from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from uuid import uuid4

from app.core.utils.redis_util import RedisUtil
from app.core.settings import settings


class SessionService:
    """用户会话管理服务类
    
    提供用户会话的创建、获取、更新和删除功能
    支持分布式环境下的会话共享
    支持会话自动过期
    """
    
    def __init__(self):
        self.redis_util = RedisUtil()
        self.session_prefix = "session:"
        self.default_expire = 3600  # 默认会话过期时间（秒）
    
    async def create_session(self, user_id: int, user_data: Dict[str, Any], expire: Optional[int] = None) -> str:
        """创建用户会话
        
        Args:
            user_id: 用户ID
            user_data: 用户数据
            expire: 会话过期时间（秒），None表示使用默认值
            
        Returns:
            str: 会话ID
        """
        # 生成唯一的会话ID
        session_id = str(uuid4())
        
        # 构建会话数据
        session_data = {
            "user_id": user_id,
            "user_data": user_data,
            "created_at": datetime.now().isoformat(),
            "last_accessed": datetime.now().isoformat()
        }
        
        # 设置会话过期时间
        expire_time = expire if expire is not None else self.default_expire
        
        # 存储会话数据
        await self.redis_util.set(
            f"{self.session_prefix}{session_id}",
            session_data,
            ex=expire_time
        )
        
        return session_id
    
    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """获取会话数据
        
        Args:
            session_id: 会话ID
            
        Returns:
            Optional[Dict[str, Any]]: 会话数据，不存在返回None
        """
        session_data = await self.redis_util.get(f"{self.session_prefix}{session_id}")
        
        if session_data:
            # 更新最后访问时间
            session_data["last_accessed"] = datetime.now().isoformat()
            await self.redis_util.set(
                f"{self.session_prefix}{session_id}",
                session_data,
                ex=self.default_expire
            )
            
        return session_data
    
    async def update_session(self, session_id: str, user_data: Dict[str, Any]) -> bool:
        """更新会话数据
        
        Args:
            session_id: 会话ID
            user_data: 新的用户数据
            
        Returns:
            bool: 更新是否成功
        """
        session_data = await self.get_session(session_id)
        if not session_data:
            return False
            
        # 更新用户数据
        session_data["user_data"] = user_data
        session_data["last_accessed"] = datetime.now().isoformat()
        
        # 保存更新后的会话数据
        await self.redis_util.set(
            f"{self.session_prefix}{session_id}",
            session_data,
            ex=self.default_expire
        )
        
        return True
    
    async def delete_session(self, session_id: str) -> bool:
        """删除会话
        
        Args:
            session_id: 会话ID
            
        Returns:
            bool: 删除是否成功
        """
        return await self.redis_util.delete(f"{self.session_prefix}{session_id}")
    
    async def get_user_sessions(self, user_id: int) -> list:
        """获取用户的所有会话
        
        Args:
            user_id: 用户ID
            
        Returns:
            list: 会话列表
        """
        # 注意：这个实现可能需要根据实际需求优化
        # 在大型系统中，可能需要使用其他数据结构来存储用户会话列表
        sessions = []
        # 这里只是示例，实际实现可能需要使用 Redis 的 SCAN 命令
        # 或者使用其他数据结构来存储用户会话列表
        return sessions
    
    async def invalidate_user_sessions(self, user_id: int) -> bool:
        """使用户的所有会话失效
        
        Args:
            user_id: 用户ID
            
        Returns:
            bool: 操作是否成功
        """
        # 注意：这个实现可能需要根据实际需求优化
        # 在大型系统中，可能需要使用其他数据结构来存储用户会话列表
        return True


# 创建全局会话服务实例
session_service = SessionService() 