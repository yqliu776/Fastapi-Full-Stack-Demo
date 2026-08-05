# Fastapi-Full-Stack-Demo

<p align="center">
  <a href="https://github.com/yqliu776/Fastapi-Full-Stack-Demo">
    <img src="https://img.shields.io/github/stars/yqliu776/Fastapi-Full-Stack-Demo?style=social" alt="GitHub stars">
  </a>
  <a href="https://github.com/yqliu776/Fastapi-Full-Stack-Demo">
    <img src="https://img.shields.io/github/last-commit/yqliu776/Fastapi-Full-Stack-Demo" alt="GitHub last commit">
  </a>
</p>

## 项目简介

本项目是一个基于FastAPI和Vue 3构建的全栈应用示例，旨在展示现代化Web应用的开发架构和最佳实践。项目采用前后端分离的设计，包含完整的用户认证、权限管理、数据处理等功能，可以用作应用的开发模板。

## 技术栈

### 后端
- **FastAPI**：高性能异步Web框架
- **SQLAlchemy**：ORM数据库操作
- **Pydantic**：数据验证和设置管理
- **JWT**：基于Token的身份验证
- **MySQL**：关系型数据库支持
- **Redis**：缓存和会话管理
- **Loguru**：日志管理
- **Uvicorn**：ASGI服务器
- **Alembic**：数据库迁移和种子数据管理

### 前端
- **Vue 3**：渐进式JavaScript框架
- **TypeScript**：类型安全的JavaScript超集
- **Vite**：现代前端构建工具
- **Pinia**：Vue的状态管理库
- **Vue Router**：官方路由管理器
- **Tailwind CSS**：实用优先的CSS框架
- **Element Plus**：企业级组件库
- **Vitest**：单元测试框架
- **Cypress**：端到端测试框架

## 项目结构

```
.
├── backend/                 # 后端应用
│   ├── app/                # 应用主目录
│   │   ├── core/          # 核心组件(连接、中间件、配置等)
│   │   ├── modules/       # 业务模块(模型、仓库、架构)
│   │   ├── routers/       # API路由(认证、权限、用户管理)
│   │   ├── services/      # 业务服务层
│   │   └── scripts/       # 脚本工具
│   ├── main.py            # 应用入口
│   └── README.md          # 后端文档
│
├── frontend/               # 前端应用
│   ├── src/               # 源代码目录
│   │   ├── assets/        # 静态资源
│   │   ├── components/    # 组件
│   │   ├── router/        # 路由配置
│   │   ├── stores/        # 状态管理
│   │   ├── views/         # 页面视图
│   │   ├── App.vue        # 根组件
│   │   └── main.ts        # 入口文件
│   └── README.md          # 前端文档
│
├── sql/                    # SQL脚本和数据库相关文件
├── docs/                   # 项目文档
├── docker-compose.yml      # 本地 MySQL/Redis 开发环境
└── README.md               # 项目说明(当前文件)
```

## 系统要求
版本信息为开发时适用版本，未对任何其他版本进行测试。
- Python >= 3.12
- Node.js >= 18
- MySQL >= 8.0
- Redis >= 7.4.2

## 快速开始

### 本地 Docker 环境

项目默认使用 MySQL 和 Redis，本地开发不需要 PostgreSQL。根目录提供了 `docker-compose.yml`，会自动启动 MySQL 8 和 Redis 7，并在 MySQL 首次初始化时依次导入 [mysql-8.sql](sql/mysql-8.sql) 和 [init_mysql.sql](sql/init_mysql.sql)。

1. 启动 MySQL 和 Redis
   ```bash
   docker compose up -d mysql redis
   ```

2. 查看服务状态
   ```bash
   docker compose ps
   ```

3. 默认连接信息
   ```text
   MySQL: localhost:3306
   Database: full-stack-demo
   User: root
   Password: FastFullStack123

   Redis: localhost:6379
   Password: FastFullStackRedis123
   ```

4. 默认登录账号
   ```text
   Username: admin
   Password: Admin@123
   ```

如果需要重新执行初始化 SQL，可以删除 MySQL 数据卷后再启动：

```bash
docker compose down -v
docker compose up -d mysql redis
```

#### 后端设置

1. 进入后端目录
   ```bash
   cd backend
   ```

2. 创建并激活虚拟环境
   ```bash
   # 使用UV
   pip install uv
   uv venv .venv
   # Windows
   .\.venv\Scripts\activate
   # Linux/macOS
   source .venv/bin/activate
   ```

3. 安装依赖
   ```bash
   uv sync
   ```

4. 配置环境变量
   ```bash
   # Windows PowerShell
   Copy-Item .env.example .env

   # Linux/macOS
   cp .env.example .env
   ```

5. 启动服务
   ```bash
   uvicorn main:app --host 127.0.0.1 --port 8090 --reload
   ```

6. 访问后端入口
   ```text
   API: http://localhost:8090
   Health: http://localhost:8090/health
   Swagger: http://localhost:8090/api/docs
   ReDoc: http://localhost:8090/api/redoc
   ```

如果使用空数据库或需要把已有数据库升级到最新结构，可以在 `backend` 目录执行：

```bash
uv run alembic upgrade head
```

> Windows 上部分机器会保留 `7981-8080` 端口段，导致 `8000` 无法绑定。本项目本地默认使用 `8090` 作为后端开发端口。

#### 前端设置

1. 进入前端目录
   ```bash
   cd frontend
   ```

2. 安装依赖
   ```bash
   npm install
   # 或
   pnpm install
   ```

3. 启动开发服务器
   ```bash
   npm run dev
   # 或
   pnpm run dev
   ```

4. 访问前端应用
   浏览器打开 http://localhost:5173

前端默认读取 [frontend/.env](frontend/.env) 中的 `VITE_API_BASE_URL=http://localhost:8090` 访问后端。
后台管理入口默认使用 `/admin-console` 前缀，登录页为 http://localhost:5173/admin-console/login。

## 主要功能

- **用户认证**：JWT认证系统，包括登录、前台业务注册、刷新令牌等
- **RBAC权限**：基于角色的访问控制系统
- **菜单管理**：动态菜单配置、组件映射与权限控制
- **API限流**：基于 Redis 的限流、白名单、黑名单与状态检查
- **后台控制台**：前台首页、后台登录、管理后台、个人信息、用户/角色/权限/菜单管理
- **响应式设计**：适配不同设备的前端界面
- **API文档**：自动生成的Swagger和ReDoc文档
- **数据验证**：前后端数据验证机制

## GitHub Star 统计

![Star History](https://api.star-history.com/svg?repos=yqliu776/Fastapi-Full-Stack-Demo&type=Date)

GitHub 仓库地址：[yqliu776/Fastapi-Full-Stack-Demo](https://github.com/yqliu776/Fastapi-Full-Stack-Demo)

## 文档

详细文档请参阅各模块的README和`docs`目录下的文档文件：

- 后端文档：[backend/README.md](backend/README.md)
- 前端文档：[frontend/README.md](frontend/README.md)
- 项目开发规范：[docs/DEVELOPMENT_GUIDE.md](docs/DEVELOPMENT_GUIDE.md)
- 历史代码审查记录：[docs/CODE_REVIEW.md](docs/CODE_REVIEW.md)

## 历史问题与近期维护

- 历史审查记录保留在 [docs/CODE_REVIEW.md](docs/CODE_REVIEW.md)：共记录 52 项问题，严重 12 / 高 15 / 中 16 / 低 9，截至 2026-03-24 为已修复 50 项、跳过 2 项、待修复 0 项。
- 已统一本地后端端口为 `8090`，避免 Windows 上 `7981-8080` 保留端口段导致 `8000` 无法绑定的问题。
- 本地开发默认使用 MySQL 8 + Redis 7，不再以 PostgreSQL 作为默认开发数据库。
- 前端后台路由默认前缀为 `/admin-console`，动态路由会在登录、刷新和登出后按菜单权限重新加载。
- OAuth 刷新令牌、Cookie 安全属性、动态路由重置、限流接口鉴权等历史审查问题已在代码审查记录中追踪。
- IDEA 项目文件已通过 `.gitignore` 忽略，并从 Git 跟踪中移除，避免后续提交包含 `.idea/` 本地配置。

## 贡献指南

1. Fork项目仓库
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启Pull Request


## 维护者

- 项目维护者: [Kevin·liu]
- 联系方式: [yqliumail@gmail.com]
