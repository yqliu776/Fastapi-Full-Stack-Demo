# Fast Full Stack Demo Backend

FastAPI 后端服务，提供 JWT 认证、用户管理、RBAC 角色/权限/菜单管理、API 权限绑定、限流管理和 Redis 缓存能力。

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
