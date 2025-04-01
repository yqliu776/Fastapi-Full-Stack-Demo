from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, BigInteger
from sqlalchemy.ext.declarative import declared_attr

from app.core.connects.database import Base


class BaseModel(Base):
    """所有模型的基础类，提供公共字段和行为"""
    
    __abstract__ = True
    
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="主键ID")
    
    # 公共审计字段
    creation_date = Column(DateTime, nullable=False, default=datetime.now, comment="创建时间")
    created_by = Column(String(50), nullable=False, comment="创建人")
    last_update_date = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now, comment="修改时间")
    last_updated_by = Column(String(50), nullable=False, comment="修改人")
    last_update_login = Column(String(50), nullable=False, comment="最后登录ID")
    delete_flag = Column(String(1), nullable=False, default="N", comment="删除标识，Y/N")
    version_num = Column(Integer, nullable=False, default=1, comment="版本号")
    
    @declared_attr
    def __tablename__(self) -> str:
        """自动根据类名生成表名"""
        return self.__name__.lower()