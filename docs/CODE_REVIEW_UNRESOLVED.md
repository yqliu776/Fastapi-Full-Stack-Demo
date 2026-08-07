
---

## 一、高（High）— 仍待处理

### H-03 注册接口无速率限制和验证码（未解决）

**文件：** `backend/app/routers/user/users_router.py:22`

```python
@user_router.post("/register", response_model=ResponseModel, summary="前台业务用户注册")
async def register_user(user_data: UserCreate, auth_service: AuthService = Depends()):
```

注册接口未挂任何限流中间件、验证码或依赖注入限制，可被脚本批量注册垃圾账号。

**建议：** 为该端点叠加 `RateLimitMiddleware` 或注入依赖做频率限制，并接入验证码校验。

---

### H-07 Bot 检测中间件状态不跨实例共享（未解决）

**文件：** `backend/app/core/middleware/bot_detection_middleware.py:38-42`

```python
self.request_fingerprints = defaultdict(lambda: {
    'timestamps': deque(maxlen=100),
    'patterns': defaultdict(int),
    'suspicious_score': 0
})
```

指纹与可疑分数仍存于进程内存，多 Worker/多实例部署时各自独立统计，攻击请求分散即可绕过。

**建议：** 迁移到 Redis 存储检测数据（含 `block_duration` 封禁状态）。

---

## 二、中（Medium）— 仍待处理

### M-02 前端类型定义分散且不一致（未解决）

**文件：**
- `frontend/src/services/roleService.ts:19` — `Menu.sort_order?: number`（optional）
- `frontend/src/services/menuService.ts:11` — `sort_order: number`（required）
- `OperationResponse` 在 `menuService.ts:55`、`permissionService.ts:75`、`roleService.ts:89`、`userService.ts:80` 重复定义

**建议：** 收敛到 `src/types/` 目录，单一数据源。

---

### M-09 `get_me` 接口计时无意义（未解决）

**文件：** `backend/app/routers/auth/auth_router.py:142-143`

```python
start_time = time.time()
process_time = time.time() - start_time  # 两行之间无任何操作
```

**建议：** 删除无意义计时，或统计实际业务耗时。

---

### M-10 `get_current_user` 跨层直接访问 Repository（未解决）

**文件：** `backend/app/routers/auth/auth_router.py:55`

```python
user = await auth_service.user_repository.get_user_with_roles(user_id)
```

Router 层直接访问 Service 内部的 Repository，违反分层架构。应在 Service 层暴露方法。

---

### M-11 后端响应格式不一致（未解决）

**文件：** `backend/app/routers/rbac/role_router.py`

同一文件内混用两种风格：
- `ResponseModel(code=200, message=..., data=...)`（第 37-41、67-71、95-99 等）
- `ResponseModel.success(data=..., message=...)`（第 264、300、347、397、438、485 行）

**建议：** 统一为 `ResponseModel.success(...)` 一种风格。

---

### M-15 前端全量注册 Element Plus 图标（未解决）

**文件：** `frontend/src/main.ts:17-20`

```typescript
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}
```

注册全部图标，显著增加 bundle 体积。**建议：** 按需导入/注册。

---

### M-16 `declarative_base()` 使用已弃用 API（未解决）

**文件：** `backend/app/core/connects/database.py:2,31`

```python
from sqlalchemy.ext.declarative import declarative_base
self._base = declarative_base()
```

**建议：** 改用 SQLAlchemy 2.0 的 `DeclarativeBase`。

---

## 三、低（Low）— 仍待处理

### L-03 `datetime.now` 缺少时区信息（未解决）

**文件：** `backend/app/modules/models/base_model.py:16-18`

```python
creation_date = Column(DateTime, nullable=False, default=datetime.now)
last_update_date = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)
```

生成 naive datetime，跨时区部署时时间不一致。**建议：** 统一使用 `datetime.now(timezone.utc)` 或项目已有的 `tzu.get_now()`。

---

### L-04 蜜罐路径可能与正常路由冲突（未解决）

**文件：** `backend/app/core/middleware/bot_detection_middleware.py:56-61`

```python
self.honeypot_paths = [
    '/admin.php', '/wp-admin', '/config.php', '/.env',
    '/phpmyadmin', '/mysql', '/backup', '/old',
    '/test', '/dev', '/staging', '/api/private',
    '/_debug', '/__debug__', '/.git', '/.svn'
]
```

`/test`、`/dev`、`/staging`、`/api/private` 等路径可能命中开发/测试环境正常路由，导致正常请求被拦截。`check_honeypot_trap`（第 178-183 行）使用 `startswith`/子串匹配，误伤面更大。

**建议：** 收紧为精确匹配 + 仅对高可疑来源启用，或移除常见开发路径。

---

## 四、部分修复（复核补充）

以下项原文档未标 `✅`，经复核**功能上已基本修复**，但仍有遗留点：

### M-05 权限缓存失效函数从未被调用（部分修复）

`backend/app/services/auth_service.py:185-193` 的 `_invalidate_role_permissions_cache` 仍是**死代码**（全仓库无调用点）；
实际失效已由 `backend/app/modules/repositories/role_repository.py` 在多个写路径手动删除缓存（第 247、273、419、499、521 行）。

**遗留：** 删除服务层死代码，或将失效逻辑收敛到 Service 层统一处理。

### M-06 菜单树递归数据库查询（部分修复）

`rbac_service.get_menu_tree`（第 1152-1211 行）已改为一次查询 + 内存建树；
但 `get_menu` 详情接口（第 1040-1082 行）仍对子菜单、孙菜单逐层发起查询。

**遗留：** 详情接口同样一次查出全部子孙后再组装。

### C-09 前端 Cookie 缺少安全属性（部分修复）

`frontend/src/services/authService.ts:8-13` 已按 HTTPS 条件追加 `Secure`，并保留 `SameSite=Strict`；
但 Cookie 仍由前端 `document.cookie` 写入，**无法设置 `HttpOnly`**，也无 CSRF Token 防护。

**遗留：** 若需 `HttpOnly`，须改由后端通过 `Set-Cookie` 响应头下发 Token。

---

## 处理建议

| 优先级 | 条目 | 说明 |
|--------|------|------|
| 立即 | H-03、H-07 | 安全/抗滥用，直接影响线上可用性 |
| 迭代 | M-02、M-09、M-10、M-11、M-15、M-16 | 架构、性能、一致性优化 |
| 随手 | L-03、L-04 | 时区、误伤路由，改动小 |
| 顺手 | M-05、M-06、C-09 遗留点 | 死代码清理与局部重构 |
