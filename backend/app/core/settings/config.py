from typing import List, Literal
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # 项目设置
    PROJECT_NAME: str = "fastApi_demo"
    VERSION: str = "0.1.0"
    DEBUG: bool = True
    FORMATTED_OUTPUT: bool = True  # 是否使用格式化的 JSON 输出
    SIMPLIFY_RESPONSE_BODY: bool = True  # 是否简化响应体
    
    # 时区设置
    USE_CHINA_TIMEZONE: bool = True  # 是否使用中国时区（UTC+8）
    
    # 数据库类型选择
    DATABASE_TYPE: Literal["mysql", "postgresql"] = "mysql"
    
    # MySQL设置
    MYSQL_SERVER: str = "localhost:3306"
    MYSQL_USER: str = "root"
    MYSQL_PASSWORD: str = ""  # 移除硬编码的密码
    MYSQL_DB: str = "fatest"
    MYSQL_ECHO_SQL: bool = False  # 是否打印SQL语句
    MYSQL_POOL_SIZE: int = 5  # 连接池大小
    MYSQL_MAX_OVERFLOW: int = 10  # 连接池最大溢出大小
    MYSQL_POOL_TIMEOUT: int = 30  # 连接池超时时间（秒）
    
    # PostgreSQL设置
    POSTGRES_SERVER: str = "localhost:5432"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = ""  # 移除硬编码的密码
    POSTGRES_DB: str = "fatest"
    POSTGRES_ECHO_SQL: bool = False  # 是否打印SQL语句
    POSTGRES_POOL_SIZE: int = 5  # 连接池大小
    POSTGRES_MAX_OVERFLOW: int = 10  # 连接池最大溢出大小
    POSTGRES_POOL_TIMEOUT: int = 30  # 连接池超时时间（秒）
    
    # Redis设置
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str = ""  # 移除硬编码的密码
    REDIS_DB: int = 0
    REDIS_TIMEOUT: int = 5  # Redis连接超时时间（秒）
    
    # 数据库URL
    @property
    def SQLALCHEMY_DATABASE_URL(self) -> str:
        if self.DATABASE_TYPE == "mysql":
            return f"mysql+pymysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}@{self.MYSQL_SERVER}/{self.MYSQL_DB}"
        elif self.DATABASE_TYPE == "postgresql":
            return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}/{self.POSTGRES_DB}"
        else:
            raise ValueError(f"不支持的数据库类型: {self.DATABASE_TYPE}")
    
    # JWT设置
    SECRET_KEY: str = Field(
        default="please-change-in-production-environment-with-strong-key",
        description="JWT secret key"
    )
    # 密码加密设置
    PWD_SALT: str = Field(
        default="please-change-in-production",
        description="Password hash salt"
    )
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7  # 添加刷新令牌过期天数配置，默认7天
    
    # CORS设置
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000",
                                       "http://localhost:8080"]
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )


# 加载配置实例
settings = Settings()
