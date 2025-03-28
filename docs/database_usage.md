# 数据库使用指南

本项目支持MySQL和PostgreSQL两种关系型数据库，并提供了完全的异步支持。

## 配置数据库类型

在`.env`文件中，通过`DATABASE_TYPE`设置选择使用的数据库类型：

```
# 数据库类型选择 (mysql 或 postgresql)
DATABASE_TYPE=mysql  # 或 DATABASE_TYPE=postgresql
```

## 数据库连接配置

### MySQL配置

```
# MySQL设置
MYSQL_SERVER=localhost:3306
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DB=database_name
MYSQL_ECHO_SQL=False  # 是否打印SQL语句
MYSQL_POOL_SIZE=5     # 连接池大小
MYSQL_MAX_OVERFLOW=10 # 连接池最大溢出大小
MYSQL_POOL_TIMEOUT=30 # 连接池超时时间（秒）
```

### PostgreSQL配置

```
# PostgreSQL设置
POSTGRES_SERVER=localhost:5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
POSTGRES_DB=database_name
POSTGRES_ECHO_SQL=False  # 是否打印SQL语句
POSTGRES_POOL_SIZE=5     # 连接池大小
POSTGRES_MAX_OVERFLOW=10 # 连接池最大溢出大小
POSTGRES_POOL_TIMEOUT=30 # 连接池超时时间（秒）
```

## 在代码中使用数据库

项目中的数据库连接由`app.core.connects.database.db`实例管理，该实例会根据配置自动连接到指定类型的数据库。

### 在路由中使用数据库

```python
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.connects.database import db

router = APIRouter()

@router.get("/items")
async def get_items(db_session: AsyncSession = Depends(db.get_db)):
    # 使用db_session进行数据库操作
    result = await db_session.execute("SELECT * FROM items")
    items = result.fetchall()
    return items
```

### 创建数据库模型

数据库模型定义示例：

```python
from sqlalchemy import Column, Integer, String

from app.core.connects.database import Base

class Item(Base):
    __tablename__ = "items"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    description = Column(String(255))
```

### 数据库迁移

本项目不提供自动数据库迁移功能，请使用数据库迁移工具（如Alembic）管理数据库结构变更。

## 异步支持

项目使用以下异步驱动程序支持完全异步的数据库访问：

- MySQL: `aiomysql`
- PostgreSQL: `asyncpg`

这些驱动程序已经在项目依赖中配置，无需额外安装。 