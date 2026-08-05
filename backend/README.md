# Fast Full Stack Demo Backend

FastAPI 后端服务，提供 JWT 认证、用户管理、RBAC 角色/权限/菜单管理、API 权限绑定、限流管理和 Redis 缓存能力。

## 功能范围

- 认证与会话：登录、注册、OAuth2 登录入口、Access Token / Refresh Token 刷新、登出。
- 用户中心：用户列表、详情、创建、更新、删除、重置密码、角色绑定。
- RBAC 权限：角色、权限、菜单、角色权限、角色菜单、API 权限绑定。
- 动态菜单：为前端提供当前用户菜单列表和菜单树，支持 `component_key` 驱动页面组件映射。
- API 限流：Redis 存储的限流配置、统计、检查、白名单和黑名单管理。
- 接口文档：Swagger UI、ReDoc 和带 OAuth2 安全定义的 OpenAPI 文档。

## 技术栈

- Python 3.12+
- FastAPI + Uvicorn
- SQLAlchemy Async ORM
- Alembic 数据库迁移
- MySQL 8
- Redis 7
- pytest / pytest-asyncio

## 本地启动

后端本地开发默认使用根目录的 Docker Compose 启动 MySQL 和 Redis，不需要 PostgreSQL。

1. 启动基础服务

```bash
cd ..
docker compose up -d mysql redis
docker compose ps
```

2. 配置后端环境变量

```bash
cd backend
Copy-Item .env.example .env
```

Linux/macOS:

```bash
cp .env.example .env
```

3. 安装依赖

```bash
uv sync
```

4. 初始化或升级数据库

如果使用根目录 `docker-compose.yml` 首次创建的 MySQL 数据卷，容器会自动执行 `sql/mysql-8.sql` 和 `sql/init_mysql.sql`。

如果是空数据库或需要迁移到最新结构，运行：

```bash
uv run alembic upgrade head
```

5. 启动后端

```bash
uv run uvicorn main:app --host 127.0.0.1 --port 8090 --reload
```

也可以直接运行：

```bash
uv run python main.py
```

> Windows 上部分机器会保留 `7981-8080` 端口段，导致 `8000` 无法绑定。本项目本地默认使用 `8090` 作为后端开发端口。

## 本地入口

- API 服务: http://localhost:8090
- 健康检查: http://localhost:8090/health
- Swagger: http://localhost:8090/api/docs
- ReDoc: http://localhost:8090/api/redoc

默认账号：

```text
Username: admin
Password: Admin@123
```

默认连接信息：

```text
MySQL: localhost:3306
Database: full-stack-demo
User: root
Password: FastFullStack123

Redis: localhost:6379
Password: FastFullStackRedis123
```

## 常用命令

```bash
# 运行 RBAC 核心测试
uv run pytest tests/test_rbac_core.py

# 查看当前迁移版本
uv run alembic current

# 升级到最新迁移
uv run alembic upgrade head

# 回滚一个迁移
uv run alembic downgrade -1
```

## 配置说明

后端读取 `backend/.env`，示例配置见 `backend/.env.example`。

关键配置：

```env
DATABASE_TYPE=mysql
MYSQL_SERVER=localhost:3306
MYSQL_USER=root
MYSQL_PASSWORD=FastFullStack123
MYSQL_DB=full-stack-demo

REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=FastFullStackRedis123
REDIS_DB=0
REDIS_TIMEOUT=5

BACKEND_CORS_ORIGINS=["http://localhost:3000","http://localhost:8080","http://localhost:5173","http://127.0.0.1:5173"]

SECRET_KEY=local-dev-secret-key-change-before-production
PWD_SALT=local-dev-password-salt
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=7
DEBUG=True
```

生产环境必须替换 `SECRET_KEY` 和 `PWD_SALT`，并关闭 `DEBUG`。

## 数据库初始化

项目现在有两套可初始化新环境的方式：

- Docker Compose 首次启动 MySQL 数据卷时执行 `sql/mysql-8.sql` 和 `sql/init_mysql.sql`。
- Alembic 使用 `backend/alembic/versions` 下的迁移脚本创建结构和种子数据。

两种方式都以 MySQL 8 为目标，并包含默认 RBAC 权限、菜单、API 权限绑定和管理员账号。

## 历史问题与回归重点

完整历史审查记录见 [../docs/CODE_REVIEW.md](../docs/CODE_REVIEW.md)，其中记录了 52 项问题，严重 12 / 高 15 / 中 16 / 低 9，截至 2026-03-24 为已修复 50 项、跳过 2 项、待修复 0 项。

后端相关改动需要特别回归以下历史问题：

- 权限校验必须处理空权限、旧 token 和无权限场景，避免空指针或误放行。
- Refresh Token 必须通过请求体传递，并和 Access Token 做类型区分。
- 生产环境不得向客户端暴露数据库异常详情，详细错误只进入日志。
- 限流管理接口必须保留认证和权限校验，避免匿名用户修改白名单/黑名单。
- RBAC 关联表需要保持唯一约束和审计字段完整，避免重复授权和审计缺失。
- 本地开发默认目标是 MySQL 8 + Redis 7；如果启用其他数据库驱动，需要同步检查配置、迁移和文档。

## 维护者

- 项目维护者: Kevin·liu
- 联系方式: yqliumail@gmail.com
