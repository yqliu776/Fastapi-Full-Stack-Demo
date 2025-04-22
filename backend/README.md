# Fast Full Stack Backend

## 项目简介
本项目基于 [FastAPI](https://fastapi.tiangolo.com/) 框架开发，旨在提供一套可扩展、可维护的中大型服务端应用结构示例。项目融合了现代化的后端开发实践，包括异步数据库操作、RBAC权限管理、JWT认证、Redis缓存等功能，可以作为企业级Web应用的后端服务基础框架。

## 技术栈
- **FastAPI**: 高性能异步Web框架
- **SQLAlchemy**: ORM数据库操作
- **Pydantic**: 数据验证和设置管理
- **JWT**: 基于Token的身份验证
- **MySQL/PostgreSQL**: 关系型数据库支持
- **Redis**: 缓存和会话管理
- **Loguru**: 日志管理
- **Uvicorn**: ASGI服务器

## 系统要求
- Python >= 3.12
- MySQL >= 8.0 或 PostgresSQL >= 12.0 (暂未实现)
- Redis >= 7.4.2

## 目录结构
```bash
.
├── app                     # 应用主目录
│   ├── core               # 核心组件
│   │   ├── connects       # 数据库和Redis连接管理
│   │   ├── decorators     # 装饰器
│   │   ├── middleware     # 中间件
│   │   ├── models         # 数据模型
│   │   ├── settings       # 应用配置
│   │   └── utils          # 工具函数
│   ├── modules            # 业务模块
│   │   ├── models         # 数据模型定义
│   │   ├── repositories   # 数据仓库
│   │   └── schemas        # 数据验证模式
│   ├── routers            # API路由
│   │   ├── auth           # 认证相关路由
│   │   ├── rbac           # 角色权限管理路由
│   │   └── user           # 用户管理路由
│   ├── scripts            # 脚本工具
│   ├── services           # 业务服务
│   └── app_lifecycle.py   # 应用生命周期管理
├── logs                    # 日志目录
├── main.py                 # 应用入口
├── pyproject.toml          # 项目依赖
├── .python-version         # Python版本控制
└── README.md               # 项目文档
```

## 主要功能
- **用户认证**: JWT认证系统，包含登录、注册、刷新令牌等功能
- **RBAC权限**: 基于角色的访问控制系统
- **菜单管理**: 动态菜单配置与权限控制
- **数据库抽象**: 支持MySQL和PostgreSQL，提供完全异步操作
- **缓存系统**: Redis缓存集成
- **文档自动生成**: 内置Swagger和ReDoc文档
- **异常处理**: 全局异常捕获与统一响应
- **日志系统**: 结构化日志记录

## 快速开始

### 环境准备
1. 安装Python 3.12或更高版本
2. 准备MySQL或~~PostgresSQL~~数据库
3. 安装Redis服务

### 安装步骤

#### 1. 克隆项目
```bash
git clone <项目仓库URL>
cd <项目目录>
```

#### 2. 创建并配置环境变量
创建`.env`文件，配置以下变量:
```
# 数据库配置
MYSQL_SERVER=localhost:3306
MYSQL_USER=root
MYSQL_PASSWORD=YOUR_PASSWORD
MYSQL_DB=full-stack-demo


# Redis配置
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=YOUR_PASSWORD
REDIS_DB=0

# 安全配置
SECRET_KEY=YOUR_PASSWORD
PWD_SALT=YOUR_PASSWORD_SALT
```

#### 3. 安装依赖
##### 推荐使用UV进行依赖安装
```bash
pip install uv
uv venv .venv
uv sync
``

#### 4. 启动应用
##### 使用UV
```bash
uv run main.py
```

##### 或直接使用uvicorn
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 访问应用
- API服务: http://localhost:8000
- Swagger文档: http://localhost:8000/api/docs
- ReDoc文档: http://localhost:8000/api/redoc

## 数据库配置
本项目支持MySQL和PostgreSQL（未开发）两种关系型数据库，并提供完全的异步支持。

### 配置数据库
在`.env`文件或者`app/core/settings/config.py`中配置数据库连接参数：

1. 数据库类型选择：
```
DATABASE_TYPE=mysql  # 或 postgresql（未开发）
```

2. 数据库连接参数：
```
# MySQL
MYSQL_SERVER=localhost:3306
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DB=your_database

# PostgreSQL（未开发）
POSTGRES_SERVER=localhost:5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
POSTGRES_DB=your_database
```

## 开发指南

### 添加新路由
1. 在`app/routers`下创建新的路由模块
2. 在`app/app_lifecycle.py`中注册路由

### 创建新的数据模型
1. 在`app/modules/models`下定义SQLAlchemy模型
2. 在`app/modules/schemas`下创建对应的Pydantic模式

### 定义业务逻辑
在`app/services`目录下创建服务类实现业务逻辑

## 贡献指南
欢迎提交issue与PR，共同完善项目结构与功能。

### 开发规范
- 遵循PEP 8编码规范
- 为所有函数和类编写文档字符串
- 添加单元测试覆盖新功能
- 提交PR前运行测试确保通过

## 许可证
MIT License

## 联系与支持
- 项目维护者: [Kevin·liu]
- 问题反馈: [yqliumail@linux.do]


