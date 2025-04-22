# Fastapi-Full-Stack-Demo

## 项目简介

本项目是一个基于FastAPI和Vue 3构建的全栈应用示例，旨在展示现代化Web应用的开发架构和最佳实践。项目采用前后端分离的设计，包含完整的用户认证、权限管理、数据处理等功能，可作为企业级应用的开发模板。

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

### 前端
- **Vue 3**：渐进式JavaScript框架
- **TypeScript**：类型安全的JavaScript超集
- **Vite**：现代前端构建工具
- **Pinia**：Vue的状态管理库
- **Vue Router**：官方路由管理器
- **Tailwind CSS**：实用优先的CSS框架
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
└── README.md               # 项目说明(当前文件)
```

## 系统要求

- Python >= 3.12
- Node.js >= 16
- MySQL >= 8.0
- Redis >= 7.4.2

## 快速开始

### 后端设置

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
   创建`.env`文件并设置数据库、Redis等配置

5. 启动服务
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

### 前端设置

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
   pnpm dev
   ```

4. 访问前端应用
   浏览器打开 http://localhost:5173

## 主要功能

- **用户认证**：JWT认证系统，包括登录、注册、刷新令牌等
- **RBAC权限**：基于角色的访问控制系统
- **菜单管理**：动态菜单配置与权限控制
- **响应式设计**：适配不同设备的前端界面
- **API文档**：自动生成的Swagger和ReDoc文档
- **数据验证**：前后端数据验证机制

## 文档

详细文档请参阅各模块的README和`docs`目录下的文档文件：

- 后端文档：[backend/README.md](backend/README.md)
- 前端文档：[frontend/README.md](frontend/README.md)

## 贡献指南

1. Fork项目仓库
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启Pull Request

## 许可证

MIT License

## 维护者

- 项目维护者: [Kevin·liu]
- 联系方式: [yqliumail@linux.do]
