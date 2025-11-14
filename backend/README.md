# FastAPI 全栈后端服务

## 🎯 项目概述

基于 [FastAPI](https://fastapi.tiangolo.com/) 框架构建的企业级异步Web后端服务，采用现代化的分层架构设计，提供完整的RBAC权限管理、JWT认证、Redis缓存等核心功能。项目遵循**领域驱动设计(DDD)**原则，适合作为中大型Web应用的后端服务基础框架。

### ✨ 核心特性
- **🔐 企业级认证授权**: JWT双令牌机制 + OAuth2兼容 + RBAC细粒度权限控制
- **⚡ 高性能异步架构**: 全链路异步处理，支持高并发场景
- **🛡️ 安全保障**: bcrypt密码加密、请求验证、SQL注入防护、CORS配置
- **📊 智能缓存**: Redis多级缓存策略，权限缓存自动刷新
- **🔍 可观测性**: 结构化日志、全局异常处理、性能监控
- **📚 API文档**: 自动生成Swagger UI和ReDoc文档，支持OAuth2安全定义

## 🏗️ 技术架构

### 核心技术栈
| 组件 | 技术 | 版本 | 用途 |
|------|------|------|------|
| Web框架 | FastAPI | 0.115.8 | 高性能异步Web框架 |
| ORM | SQLAlchemy | 2.0.38 | 异步数据库操作 |
| 数据验证 | Pydantic | 2.10.6 | 类型安全和数据验证 |
| 认证授权 | python-jose | 3.8.0 | JWT令牌处理 |
| 密码安全 | bcrypt | 4.0.1 | 密码哈希加密 |
| 缓存 | Redis | 5.0+ | 分布式缓存和会话 |
| 日志 | Loguru | 0.7.3 | 结构化日志管理 |
| 服务器 | Uvicorn | 0.34.0 | ASGI异步服务器 |

### 系统要求
- **Python**: ≥3.12（利用最新类型注解和异步特性）
- **数据库**: MySQL ≥8.0 或 PostgreSQL ≥12.0
- **缓存**: Redis ≥7.4.2
- **包管理器**: UV（现代Python包管理工具）

## 📁 项目结构

```bash
.
├── app/                          # 应用主目录
│   ├── core/                     # 核心组件层
│   │   ├── connects/            # 数据库和Redis连接管理
│   │   ├── decorators/          # 装饰器（权限、响应等）
│   │   ├── middleware/          # 中间件（日志、错误处理、CORS）
│   │   ├── models/              # 核心数据模型（响应模型、异常）
│   │   ├── settings/            # 应用配置管理（Pydantic Settings）
│   │   └── utils/               # 工具函数（日志、密码、安全、Redis等）
│   ├── modules/                 # 业务模块层（DDD领域层）
│   │   ├── models/              # 数据模型定义（RBAC模型）
│   │   ├── repositories/        # 数据仓库层（数据库操作抽象）
│   │   └── schemas/             # Pydantic数据验证模式
│   ├── routers/                 # API路由层（接口层）
│   │   ├── auth/                # 认证相关路由
│   │   ├── rbac/                # 角色权限管理路由
│   │   └── user/                # 用户管理路由
│   ├── services/                # 业务服务层（应用服务）
│   ├── ai/                      # AI功能模块（预留扩展）
│   ├── websocket/               # WebSocket功能（预留扩展）
│   ├── logs/                    # 日志目录（自动归档）
│   └── app_lifecycle.py         # 应用生命周期管理
├── static/                      # 静态文件存储
├── tests/                       # 测试目录（待完善）
├── main.py                      # 应用入口点
├── pyproject.toml               # 项目依赖管理（UV）
└── README.md                    # 项目文档
```

### 架构模式
- **分层架构**: 接口层 → 应用服务层 → 领域层 → 基础设施层
- **依赖注入**: FastAPI原生DI容器，支持生命周期管理
- **仓储模式**: 数据访问抽象，支持多数据源
- **领域驱动**: 业务逻辑与基础设施解耦

## 🔧 核心功能详解

### 认证授权系统
- **JWT双令牌机制**: 访问令牌(60分钟) + 刷新令牌(7天)
- **OAuth2兼容**: 支持标准OAuth2密码授权模式
- **会话管理**: Redis集中式会话存储，支持强制下线
- **权限缓存**: 角色权限缓存1小时TTL，自动刷新

### RBAC权限管理
- **五表结构设计**: 用户-角色-权限-菜单完整关联
- **细粒度控制**: 基于权限码的访问控制
- **超级管理员**: 支持超级管理员权限绕过
- **装饰器模式**: 简洁的`@has_permission(["USER_MANAGE"])`用法

### 数据访问层
- **完全异步**: SQLAlchemy 2.0异步API，全链路非阻塞
- **多数据库支持**: MySQL和PostgreSQL双数据库适配
- **连接池优化**: 可配置的连接池参数和超时设置
- **事务管理**: 依赖注入确保会话正确生命周期

### 企业级特性
- **全局异常处理**: 分层异常捕获，统一响应格式
- **结构化日志**: Loguru异步日志，支持自动归档
- **API文档**: 自动生成Swagger UI和ReDoc
- **健康监控**: 系统资源监控和性能指标

## 🚀 快速开始

### 前置要求
- **Python环境**: 3.12或更高版本
- **数据库**: MySQL 8.0+ 或 PostgreSQL 12.0+
- **缓存服务**: Redis 7.4.2+
- **包管理**: UV包管理器

### 🔧 环境配置

#### 1. 克隆项目
```bash
git clone <项目仓库URL>
cd fast-full-stack-demo/backend
```

#### 2. 创建虚拟环境
```bash
# 安装UV包管理器
pip install uv

# 创建虚拟环境
uv venv .venv

# 激活虚拟环境
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate
```

#### 3. 安装依赖
```bash
# 使用UV安装依赖（推荐）
uv sync

# 或使用pip
pip install -r requirements.txt
```

#### 4. 数据库配置
创建`.env`文件，配置以下环境变量：

```env
# === 数据库配置 ===
DATABASE_TYPE=mysql  # 或 postgresql

# MySQL配置
MYSQL_SERVER=localhost:3306
MYSQL_USER=root
MYSQL_PASSWORD=your_secure_password
MYSQL_DB=fastapi_demo

# PostgreSQL配置（可选）
POSTGRES_SERVER=localhost:5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_secure_password
POSTGRES_DB=fastapi_demo

# === Redis配置 ===
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=your_redis_password
REDIS_DB=0

# === 安全配置 ===
# ⚠️ 警告：生产环境必须修改默认值
SECRET_KEY=your-very-secure-secret-key-at-least-32-characters
PWD_SALT=your-secure-password-salt

# === 应用配置 ===
DEBUG=False
LOG_LEVEL=INFO
```

#### 5. 数据库初始化
```bash
# 创建数据库
mysql -u root -p -e "CREATE DATABASE fastapi_demo CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# 项目启动时会自动创建表结构
```

### 🏃‍♂️ 启动应用

#### 开发环境启动
```bash
# 使用UV运行
uv run main.py

# 或使用uvicorn热重载模式
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

#### 生产环境启动
```bash
# 使用Gunicorn + Uvicorn工作进程
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 🔗 访问服务
- **API服务**: http://localhost:8000
- **Swagger文档**: http://localhost:8000/api/docs
- **ReDoc文档**: http://localhost:8000/api/redoc
- **健康检查**: http://localhost:8000/health

## 💻 开发指南

### 核心设计模式

#### 1. 依赖注入模式
```python
# 路由层使用依赖注入
@router.get("/users/me")
async def read_current_user(
    current_user: User = Depends(get_current_user)
):
    return current_user

# 服务层依赖注入
@router.get("/users/")
async def get_users(
    user_service: UserService = Depends(get_user_service)
):
    return await user_service.get_user_list()
```

#### 2. 仓储模式
```python
# 数据访问抽象
class UserRepository:
    async def get_by_id(self, user_id: int) -> Optional[User]:
        # 数据库操作细节封装
        pass

    async def create(self, user_data: CreateUserRequest) -> User:
        # 创建用户逻辑
        pass
```

#### 3. 装饰器模式
```python
# 权限验证装饰器
@router.get("/users/")
@has_permission(["USER_MANAGE"])
async def get_users():
    # 只有具备USER_MANAGE权限的用户才能访问
    pass
```

### 添加新功能模块

#### 步骤1: 定义数据模型
```python
# app/modules/models/new_model.py
from sqlalchemy import Column, Integer, String
from app.modules.models.base import BaseModel

class NewEntity(BaseModel):
    __tablename__ = "new_entities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False, comment="实体名称")
```

#### 步骤2: 创建Pydantic模式
```python
# app/modules/schemas/new_schema.py
from pydantic import BaseModel

class CreateEntityRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)

class EntityResponse(BaseModel):
    id: int
    name: str
```

#### 步骤3: 实现仓储层
```python
# app/modules/repositories/new_repository.py
from app.modules.repositories.base import BaseRepository

class NewRepository(BaseRepository):
    async def create(self, entity_data: dict) -> NewEntity:
        # 实现创建逻辑
        pass

    async def get_by_id(self, entity_id: int) -> Optional[NewEntity]:
        # 实现查询逻辑
        pass
```

#### 步骤4: 实现服务层
```python
# app/services/new_service.py
from app.services.base import BaseService

class NewService(BaseService):
    def __init__(self, repository: NewRepository):
        self.repository = repository

    async def create_entity(self, request: CreateEntityRequest) -> EntityResponse:
        # 业务逻辑实现
        pass
```

#### 步骤5: 创建路由
```python
# app/routers/new_router.py
from fastapi import APIRouter, Depends

router = APIRouter(prefix="/entities", tags=["entities"])

@router.post("/", response_model=EntityResponse)
@has_permission(["ENTITY_MANAGE"])
async def create_entity(
    request: CreateEntityRequest,
    service: NewService = Depends(get_new_service)
):
    return await service.create_entity(request)
```

#### 步骤6: 注册路由
```python
# app/app_lifecycle.py
from app.routers.new_router import router as new_router

# 在create_app函数中添加
app.include_router(new_router, prefix="/api/v1")
```

### 测试最佳实践

#### 单元测试示例
```python
# tests/test_user_service.py
import pytest
from unittest.mock import AsyncMock
from app.services.user_service import UserService

@pytest.mark.asyncio
async def test_create_user():
    # Mock依赖
    mock_repo = AsyncMock()
    mock_repo.create.return_value = mock_user

    service = UserService(mock_repo)
    result = await service.create_user(valid_user_data)

    # 断言验证
    assert result.username == "testuser"
    mock_repo.create.assert_called_once()
```

### 🔒 安全最佳实践

#### 1. 配置安全
```python
# 生产环境配置检查
SECRET_KEY: str = Field(
    default_factory=lambda: secrets.token_urlsafe(32),
    description="JWT密钥，生产环境必须设置"
)
```

#### 2. 输入验证
```python
# 严格的输入验证
class UserCreateRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=20, regex="^[a-zA-Z0-9_]+$")
    password: str = Field(..., min_length=8, max_length=128)
    email: EmailStr
```

#### 3. SQL注入防护
```python
# 使用ORM参数化查询
async def get_user_by_name(self, username: str) -> Optional[User]:
    result = await self.db.execute(
        select(User).where(User.username == username)  # 参数化查询
    )
    return result.scalar_one_or_none()
```

## 🔧 配置详解

### 数据库配置
支持MySQL和PostgreSQL双数据库，智能连接池管理：

```env
# 数据库类型选择
DATABASE_TYPE=mysql  # 或 postgresql

# MySQL连接池配置
MYSQL_POOL_SIZE=20
MYSQL_MAX_OVERFLOW=40
MYSQL_POOL_TIMEOUT=30

# PostgreSQL连接池配置
POSTGRES_POOL_SIZE=20
POSTGRES_MAX_OVERFLOW=40
```

### Redis配置
多级缓存策略配置：

```env
# Redis连接
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=your_password
REDIS_DB=0

# 缓存TTL配置
CACHE_TTL_ROLE_PERMISSIONS=3600  # 角色权限缓存1小时
CACHE_TTL_USER_SESSION=86400     # 用户会话缓存24小时
```

### 安全配置
生产环境安全配置：

```env
# JWT配置
SECRET_KEY=your-very-secure-secret-key-at-least-32-characters
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=7

# 密码安全
PWD_SALT=your-secure-salt
BCRYPT_ROUNDS=12
```

### 日志配置
结构化日志和自动归档：

```env
# 日志配置
LOG_LEVEL=INFO
LOG_DIR=logs
LOG_MAX_BYTES=10485760  # 10MB
LOG_BACKUP_COUNT=5
```

## 📊 性能优化

### 数据库优化
- **连接池管理**: 智能连接池，支持连接复用
- **索引优化**: 关键字段添加索引，提升查询性能
- **查询优化**: 使用JOIN减少查询次数，避免N+1问题
- **读写分离**: 支持主从数据库配置（待实现）

### 缓存策略
- **权限缓存**: 角色权限缓存1小时，自动刷新
- **会话缓存**: 用户会话信息缓存24小时
- **查询缓存**: 热点数据缓存，减少数据库压力

### 异步优化
- **全链路异步**: 从路由到数据库操作全异步
- **并发控制**: 合理的并发连接数限制
- **超时设置**: 数据库和外部服务调用超时配置

## 🧪 测试策略

### 测试金字塔
```
   /\
  /  \
 /    \
--------  少量端到端测试
--------  适量集成测试
--------  大量单元测试
```

### 测试覆盖率目标
- **单元测试**: 80%+ 覆盖率
- **集成测试**: 关键业务流程覆盖
- **端到端测试**: 核心用户场景覆盖

### 测试工具推荐
- **pytest**: 单元测试框架
- **pytest-asyncio**: 异步测试支持
- **pytest-cov**: 覆盖率报告
- **httpx**: 异步HTTP测试客户端
- **factory-boy**: 测试数据工厂

## 🚀 部署指南

### Docker部署
```dockerfile
# Dockerfile示例
FROM python:3.12-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY pyproject.toml ./
RUN pip install uv && uv sync --frozen

# 复制应用代码
COPY . .

# 健康检查
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# 运行应用
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 生产环境配置
```yaml
# docker-compose.yml
version: '3.8'
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_TYPE=mysql
      - MYSQL_SERVER=db:3306
      - REDIS_HOST=redis
    depends_on:
      - db
      - redis
    restart: unless-stopped

  db:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: secure_password
      MYSQL_DATABASE: fastapi_demo
    volumes:
      - mysql_data:/var/lib/mysql
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    command: redis-server --requirepass redis_password
    volumes:
      - redis_data:/data
    restart: unless-stopped

volumes:
  mysql_data:
  redis_data:
```

### 监控和告警
- **应用监控**: 集成Prometheus指标收集
- **日志聚合**: ELK Stack日志收集和分析
- **性能监控**: APM工具监控API性能
- **健康检查**: 定期健康检查和自动恢复

## 🤝 贡献指南

我们欢迎所有形式的贡献，包括错误修复、功能增强、文档改进等。

### 开发规范
- **代码规范**: 遵循PEP 8编码规范，使用Black格式化代码
- **类型注解**: 所有函数和类必须包含完整的类型注解
- **文档要求**: 为所有公共函数和类编写详细的docstring
- **测试要求**: 新功能必须包含相应的单元测试和集成测试
- **提交规范**: 遵循[Conventional Commits](https://www.conventionalcommits.org/)规范

### 提交流程
1. Fork项目到个人仓库
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'feat: add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建Pull Request

### 代码审查标准
- [ ] 代码符合PEP 8规范
- [ ] 包含完整的类型注解
- [ ] 新增/修改代码有相应测试
- [ ] 测试覆盖率不低于80%
- [ ] 文档已更新
- [ ] 无安全漏洞

## 🐛 已知问题

### 高优先级
- [ ] **安全配置**: 默认SECRET_KEY和PWD_SALT存在安全隐患，必须在生产环境修改
- [ ] **测试缺失**: 项目缺乏单元测试和集成测试
- [ ] **API版本控制**: 缺少API版本管理策略

### 中优先级
- [ ] **数据库迁移**: 未集成Alembic数据库迁移工具
- [ ] **限流机制**: 缺少API限流和防刷保护
- [ ] **监控告警**: 缺少完善的系统监控和告警机制

### 低优先级
- [ ] **代码优化**: 部分魔法字符串需要提取为常量
- [ ] **性能优化**: 可添加查询结果缓存优化
- [ ] **文档完善**: API文档可添加更多使用示例

## 🗺️ 路线图

### 短期目标 (v1.1.0)
- [ ] 集成Alembic数据库迁移
- [ ] 添加单元测试框架和测试用例
- [ ] 实现API限流和防刷机制
- [ ] 完善Docker部署配置

### 中期目标 (v1.2.0)
- [ ] 集成Prometheus监控指标
- [ ] 添加WebSocket实时通信支持
- [ ] 实现文件上传和存储功能
- [ ] 添加定时任务和异步任务队列

### 长期目标 (v2.0.0)
- [ ] 微服务架构拆分
- [ ] 事件驱动架构实现
- [ ] 多租户支持
- [ ] 分布式缓存和会话

## 📞 技术支持

### 项目维护者
- **主要维护者**: Kevin·liu
- **邮箱**: yqliumail@linux.do
- **问题反馈**: 请提交GitHub Issue

### 社区支持
- **技术讨论**: GitHub Discussions
- **错误报告**: GitHub Issues
- **功能请求**: GitHub Issues (标记为enhancement)

### 商业支持
如需商业支持、定制开发或技术咨询，请联系项目维护者。

## 📄 许可证

本项目采用 **MIT License** 开源协议。

```
MIT License

Copyright (c) 2024 FastAPI Full Stack Demo

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## 🙏 致谢

感谢以下开源项目和社区的支持：

- [FastAPI](https://fastapi.tiangolo.com/) - 高性能异步Web框架
- [SQLAlchemy](https://www.sqlalchemy.org/) - Python SQL工具包和ORM
- [Pydantic](https://docs.pydantic.dev/) - 数据验证和设置管理
- [Redis](https://redis.io/) - 高性能内存数据库
- [UV](https://docs.astral.sh/uv/) - 极速Python包管理器

---

**⭐ 如果这个项目对你有帮助，请给我们一个Star！**


