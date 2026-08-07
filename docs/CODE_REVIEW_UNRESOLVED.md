# 代码审查未解决问题清单（状态跟踪）

> 本文件跟踪代码审查发现的遗留问题。已解决项标 `✅`，延后项标注延后原因与前置条件。
> 最近一次执行：按 `docs/DEVELOPMENT_GUIDE.md` 规范完成批量修复（详见下文各条目）。

---

## 一、高（High）

### H-03 注册接口无速率限制和验证码（限流已解决，验证码延后）

**文件：** `backend/app/routers/user/users_router.py:22`、`backend/app/core/rate_limit/middleware.py:32`

**现状：**
- ✅ 速率限制已确认生效：`RateLimitMiddleware` 在 `app_lifecycle.py` 全局挂载，`/users/register` 已配置 `RateLimitConfig(limit=5, window=3600)`（每 IP 每小时 5 次），可有效阻止脚本批量注册。
- ⏳ 验证码校验：项目暂无验证码基础设施（Bot 中间件仅返回 429 挑战响应，无真实验证码生成/校验）。**延后**：需独立实现验证码服务（生成、Redis 存储、校验接口）并接入前端注册页，不在此次范围内。

---

### H-07 Bot 检测中间件状态不跨实例共享（✅ 已解决）

**文件：** `backend/app/core/middleware/bot_detection_middleware.py`

**修复内容：**
- 请求指纹（时间戳窗口）从进程内存迁移至 Redis（`bot:fingerprint:{ip}:{fp}`，List + TTL + LTRIM 保留最近 100 条），多 Worker/多实例共享检测数据。
- 封禁状态迁移至 Redis（`bot:block:{ip}`，TTL = `block_duration_seconds`），并**真正执行封禁**：dispatch 入口先查封禁态，命中直接返回 403；蜜罐命中或高度可疑且未启用验证码时自动封禁 IP。
- Redis 不可用时 fail-open（放行请求），保持现有容错语义。

---

## 二、中（Medium）

### M-02 前端类型定义分散且不一致（✅ 已解决）

**文件：** `frontend/src/types/`（新建 `api.ts`、`menu.ts`、`permission.ts`、`role.ts`、`user.ts`）

**修复内容：**
- 收敛到 `src/types/` 单一数据源；`roleService.ts`、`menuService.ts`、`permissionService.ts`、`userService.ts` 改为从 `src/types/` 导入并 `export type` 再导出，保持既有消费者导入不破坏。
- `Menu.sort_order` 统一为必填 `number`（与后端始终返回一致）；`OperationResponse`/`ListResponse`/`SingleResponse` 重复定义收敛到 `src/types/api.ts`。

---

### M-09 `get_me` 接口计时无意义（✅ 已解决）

**文件：** `backend/app/routers/auth/auth_router.py:139-144`

删除 `get_user_info` 中的空计时（`start_time`/`process_time`），直接返回 `ResponseModel.success(...)`。

---

### M-10 `get_current_user` 跨层直接访问 Repository（✅ 已解决）

**文件：** `backend/app/services/auth_service.py`、`backend/app/routers/auth/auth_router.py:55`

`AuthService` 新增 `get_user_with_roles(user_id)` 作为统一入口；Router 层 `get_current_user` 改为调用该方法，不再直接访问 `auth_service.user_repository`。

---

### M-11 后端响应格式不一致（✅ 已解决）

**文件：** `backend/app/routers/rbac/role_router.py`、`menu_router.py`、`permission_router.py`

三个 RBAC router 全部统一为 `ResponseModel.success(...)` / `ResponseModel.error(...)`；删除类接口的失败分支改用 `error(code=400, ...)`，不再混用 `ResponseModel(code=200,...)` 构造风格。

---

### M-15 前端全量注册 Element Plus 图标（✅ 已解决）

**文件：** `frontend/src/utils/icons.ts`（新建）、`frontend/src/main.ts`

按需注册审计出的 42 个实际使用图标（覆盖模板标签、动态字符串、`el-button :icon` 字符串用法），移除 `main.ts` 全量循环。构建产物 index chunk 由 1161 kB 降至 1024 kB（gzip 375→339 kB）。

---

### M-16 `declarative_base()` 使用已弃用 API（✅ 已解决）

**文件：** `backend/app/core/connects/database.py`、`backend/app/modules/models/base_model.py`

改用 SQLAlchemy 2.0 `DeclarativeBase`（模块级 `class Base(DeclarativeBase)`），`declared_attr` 从 `sqlalchemy.orm` 导入；`MovedIn20Warning` 消失，模型表结构不变，无需迁移。

---

## 三、低（Low）

### L-03 `datetime.now` 缺少时区信息（✅ 已解决）

**文件：** `backend/app/modules/models/base_model.py:16-18`

`creation_date`/`last_update_date` 默认值改用项目已有的 `tzu.get_now()`（时区感知，遵循 `USE_CHINA_TIMEZONE` 配置）。

---

### L-04 蜜罐路径可能与正常路由冲突（✅ 已解决）

**文件：** `backend/app/core/middleware/bot_detection_middleware.py`

- `check_honeypot_trap` 改为**精确匹配**（`path in honeypot_paths`），移除 `startswith`/子串匹配的误伤。
- 蜜罐列表移除 `/test`、`/dev`、`/staging`、`/api/private`、`/old` 等易命中开发/测试路径的项，仅保留明确陷阱路径（`/.env`、`/.git`、`/.svn`、`/wp-admin`、`/admin.php`、`/phpmyadmin`、`/config.php`、`/mysql`、`/_debug`、`/__debug__`）。

---

## 四、部分修复（复核补充）

### M-05 权限缓存失效函数从未被调用（✅ 已解决）

删除 `auth_service._invalidate_role_permissions_cache` 死代码；失效逻辑保持由 `role_repository` 各写路径统一处理（第 247、273、419、499、521 行）。

### M-06 菜单树递归数据库查询（✅ 已解决）

`get_menu` 详情接口改为一次 `get_menu_tree()` 查询 + 内存构建以 `menu_id` 为根的子树（新增 `_build_menu_subtree`），消除子/孙菜单逐层 N+1 查询；`MenuDetail.children` 递归类型天然支持任意层级。

### C-09 前端 Cookie 缺少安全属性（延后）

当前已有 `Secure`（HTTPS 下）+ `SameSite=Strict`。Cookie 由前端 `document.cookie` 写入，无法设置 `HttpOnly`。**延后**：若要 `HttpOnly`，须改由后端 `Set-Cookie` 响应头下发 Token，并同步增加 CSRF 防护，涉及登录/刷新流程整体改造。

---

## 处理建议（当前状态）

| 优先级 | 条目 | 说明 |
|--------|------|------|
| 立即 | H-03、H-07 | H-07 已解决；H-03 限流已生效，验证码延后 |
| 迭代 | M-02、M-09、M-10、M-11、M-15、M-16 | 已全部解决 |
| 随手 | L-03、L-04 | 已全部解决 |
| 顺手 | M-05、M-06、C-09 | M-05/M-06 已解决；C-09 延后 |
