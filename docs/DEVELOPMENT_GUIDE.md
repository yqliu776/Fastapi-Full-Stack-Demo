# 项目开发规范

本文档用于约束 `fast-full-stack-demo` 的日常开发。目标是让后端、前端、数据库、文档和测试保持同一套工程约定，避免脚手架项目最常见的文档失真、接口风格漂移和安全配置误用。

## 适用范围

本规范适用于本仓库内所有新增和修改代码：

- 后端：`backend/app`、`backend/alembic`、`backend/tests`
- 前端：`frontend/src`、`frontend/.env*`、前端测试和构建配置
- 数据库：`sql`、`backend/alembic/versions`
- 文档：根目录 `README.md`、模块 README、`docs`

## 基本原则

- 以现有分层和技术栈为准，不引入平行框架或重复抽象。
- 所有对外接口必须有统一响应模板、完整接口注释和明确权限边界。
- 文档必须描述当前真实代码结构；新增、移动、删除目录时同步更新相关 README 或规范文档。
- 配置文件不能出现真实密钥、生产口令或任何前端可见的 secret。
- 默认本地后端端口为 `8090`，前端开发端口为 `5173`。
- 修改共享行为时必须补测试；只改文档也要做链接、路径和命令一致性检查。

## 后端规范

### 分层职责

后端采用 FastAPI + SQLAlchemy Async ORM + Pydantic + MySQL + Redis。

- `app/routers`: 只负责 HTTP 入参、权限依赖、调用服务、组装统一响应。
- `app/services`: 承载业务流程、跨仓储编排、业务异常。
- `app/modules/repositories`: 承载数据库访问，不写 HTTP 语义。
- `app/modules/models`: SQLAlchemy 模型和表结构映射。
- `app/modules/schemas`: Pydantic 入参、出参和批量响应模型。
- `app/core`: 配置、连接、中间件、异常、响应模型、通用工具。

新增功能时优先沿用该路径，不新增 `controllers`、`dao`、`common` 等同义层。

### 路由接口规范

所有 FastAPI 路由必须满足：

- 装饰器声明 `response_model=ResponseModel`。
- 装饰器声明清晰的 `summary`。
- 函数返回 `ResponseModel` 或显式返回包含 `ResponseModel.model_dump()` 的 `JSONResponse`。
- 函数 docstring 必须包含接口说明、`Args`、`Returns`；有业务异常时补 `Raises`。
- 需要登录或权限的接口必须使用 `Depends(get_current_user)` 或 `Depends(has_permission([...]))`。
- 不在 router 中直接拼 SQL，不在 router 中直接访问 Redis，除非这是基础设施诊断接口。

推荐写法：

```python
@router.post("/widgets", response_model=ResponseModel, summary="创建组件")
async def create_widget(
    widget_data: WidgetCreate,
    service: WidgetService = Depends(),
    current_user=Depends(get_current_user),
) -> ResponseModel:
    """
    创建组件。

    校验当前用户权限后创建业务组件，并返回创建后的组件详情。

    Args:
        widget_data: 组件创建参数。
        service: 组件服务实例。
        current_user: 当前认证用户。

    Returns:
        ResponseModel: 统一响应模型，data 为创建后的组件详情。

    Raises:
        HTTPException: 参数冲突或权限不足时返回对应错误。
    """
    widget = await service.create_widget(widget_data, current_user.user_name)
    return ResponseModel.success(data=widget, message="组件创建成功")
```

### 响应模板

项目统一响应模型为 `app.core.models.ResponseModel`：

```json
{
  "code": 200,
  "message": "操作成功",
  "data": {},
  "timestamp": 1710000000,
  "process_time": 0.0
}
```

约定：

- 成功响应使用 `ResponseModel.success(...)` 或等价的 `ResponseModel(...)`。
- 错误响应由统一异常处理器转换，业务代码优先抛 `HTTPException` 或项目自定义异常。
- `HTTPException`、422 校验错误、数据库错误和未知异常都必须保持同一响应外形。
- `/health` 这类基础接口也必须使用统一响应外形，允许 HTTP 状态码为 `503`。

### 异常与错误信息

- 面向客户端的 `message` 写业务可理解信息，不暴露 SQL、堆栈、密钥、内部路径。
- 数据库异常只在日志中记录详细信息，响应使用通用错误文案。
- 权限失败统一返回认证或授权语义，不返回“接口不存在”等误导信息。
- 参数校验错误保留字段级错误列表，放在 `data`。

### 权限与认证

- 认证接口在 `app/routers/auth`。
- 访问当前用户信息使用 `get_current_user`。
- RBAC 管理接口使用 `has_permission([...])`，权限编码必须来自种子数据或迁移。
- 新增管理端接口时，同步维护 API 权限绑定和前端菜单权限。
- Token 类型必须区分 access 和 refresh；refresh token 不通过 URL Query 传递。

### 数据库与迁移

- 表结构变化必须新增 Alembic migration，不直接只改 SQLAlchemy model。
- 迁移文件命名应表达业务意图，例如 `20260804_0003_add_widget_table.py`。
- 新表继承或遵循现有审计字段约定：创建人、更新人、更新时间、删除标记。
- 关联表需要明确唯一约束，避免重复授权或重复绑定。
- 涉及初始化数据时，迁移和 `sql` 初始化脚本要保持一致，避免新环境和迁移环境分叉。

### 后端测试

后端测试使用 `pytest` / `pytest-asyncio`。

必须补测试的场景：

- 新增或修改认证、权限、限流、响应模板等共享行为。
- 修改 repository 的查询条件、软删除逻辑、唯一性逻辑。
- 修改 token、密码、环境变量、安全策略。
- 修复线上或审查发现的 bug。

常用命令：

```bash
cd backend
uv run pytest
uv run pytest tests/test_response_template.py
uv run alembic upgrade head
```

## 前端规范

### 目录职责

前端采用 Vue 3 + TypeScript + Vite + Pinia + Vue Router + Element Plus + Tailwind CSS。

- `src/api`: Axios 客户端和底层请求配置。
- `src/services`: 按业务域封装 API 调用。
- `src/stores`: Pinia 状态管理。
- `src/router`: 路由、动态路由和导航守卫。
- `src/views`: 页面级组件。
- `src/components`: 可复用组件。
- `src/utils`: 通用工具函数。
- `src/assets`: 样式、图片、SVG 等静态资源。

不要在文档中提前声明未创建的目录。确实需要新增目录时，必须同时新增实际代码或更新文档说明。

### API 调用

- 所有 HTTP 请求通过 `src/api/client.ts` 创建的 Axios 实例。
- 业务 API 封装放在 `src/services`，页面组件不直接散落 `axios` 调用。
- 默认 API 地址统一为 `http://localhost:8090`。
- 前端按后端统一模板读取 `code/message/data`，不要假设接口直接返回裸数据。
- 401、403 等认证授权错误统一在请求层或 store 层处理，页面只展示业务结果。

### 状态与路由

- 登录态和用户信息由 `src/stores/user.ts` 管理。
- 菜单和动态路由由菜单 store 与 router 协作管理。
- 登出必须清理 token、用户信息、菜单状态和动态路由标记。
- 新增菜单页面时，需要同步后端菜单种子、权限编码、前端路由组件映射。

### UI 与组件

- 管理后台页面以高密度、清晰、可扫描为优先，不做营销式首屏。
- 页面级业务状态放在 `views`，可复用交互沉淀到 `components`。
- Element Plus 组件优先用于表格、表单、弹窗、消息、分页。
- Tailwind 用于局部布局和间距，不要和 Element Plus 样式互相覆盖到难以维护。
- 组件 props、emit、关键响应式状态必须有 TypeScript 类型。

### 前端环境变量

- 只有可公开配置允许使用 `VITE_` 前缀。
- 禁止在 `VITE_` 变量中放 OAuth client secret、JWT 密钥、数据库密码、Redis 密码。
- 前端环境样例维护在 `frontend/.env.example`。
- 修改 API 默认地址时，需要同步 `frontend/.env`、`frontend/.env.example`、前端 README、代码 fallback。

### 前端测试与检查

常用命令：

```bash
cd frontend
npm run build
npm run type-check
npm run lint
npm run test:unit
```

提交前至少运行与变更相关的检查：

- 改 TypeScript 类型、组件或服务：运行 `npm run build` 或 `npm run type-check`。
- 改路由、登录、权限：优先补充单元测试或 E2E 流程。
- 只改文档：检查命令、路径、端口和目录树是否真实存在。

## 文档规范

文档是脚手架的一部分，必须像代码一样维护。

- README 的目录树只能描述真实存在的目录和关键文件。
- 默认端口、默认账号、环境变量、启动命令必须全仓一致。
- 新增功能需要更新相邻 README 或 `docs` 中对应专题文档。
- 文档示例代码必须能对应当前真实模块路径。
- 安全相关配置必须明确哪些是演示值、哪些必须在生产替换。

建议新增文档放置位置：

- 项目级规范：`docs`
- 后端使用说明：`backend/README.md`
- 前端使用说明：`frontend/README.md`
- 数据库迁移说明：`docs/ALEMBIC_USAGE.md`

## 安全规范

- 不提交真实密钥、生产账号、生产数据库连接串。
- `.env.example` 只能放示例值，真实 `.env` 只用于本地。
- 前端构建产物可见的一切都视为公开信息。
- 密码、token、salt、client secret 只能在后端或部署平台密钥管理中保存。
- 认证、权限、限流、防刷相关改动必须补测试或至少补可复现验证说明。
- 日志中避免记录 token、密码、refresh token、验证码、完整 Authorization header。

## Git 与提交规范

提交前检查：

```bash
git status --short
git diff --check
```

提交信息使用 Conventional Commits：

- `feat:` 新功能
- `fix:` 缺陷修复
- `docs:` 文档更新
- `refactor:` 重构
- `test:` 测试
- `chore:` 构建或工具维护

一个提交应聚焦一个主题。不要把无关格式化、生成产物、个人环境文件混入业务提交。

## 推荐交付清单

后端接口变更：

- 路由有 `summary`、`response_model=ResponseModel`、完整 docstring。
- 响应保持统一模板。
- 权限依赖明确。
- Pydantic schema、service、repository 分层清晰。
- Alembic migration 和初始化数据已同步。
- 相关 pytest 已通过。

前端页面或交互变更：

- API 调用通过 `services`。
- 页面能处理后端统一响应模板。
- 登录态、权限、菜单状态处理完整。
- `npm run build` 或相关类型检查通过。
- README 或使用说明已同步。

文档变更：

- 文件路径、目录树、端口、命令真实可用。
- 没有把 secret 写进前端或公开文档。
- 与根 README、模块 README 不冲突。

## 当前基线命令

在提交较大变更前，建议至少执行：

```bash
cd backend
uv run pytest

cd ../frontend
npm run build
```

如果只改后端或只改前端，可以按变更范围缩小验证，但最终说明中必须写明实际运行了哪些检查，以及哪些检查因环境限制未运行。
