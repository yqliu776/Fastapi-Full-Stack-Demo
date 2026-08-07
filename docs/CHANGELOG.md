# 项目变更记录（Changelog）

本项目使用日期分组的阶段性变更记录。原代码审查清单 `docs/CODE_REVIEW_UNRESOLVED.md`
已在 2026-08-07 阶段处理完毕并归档删除，遗留项状态迁移至本文件。

## 2026-08-07 — 代码审查清理阶段

针对代码审查遗留问题完成一次集中修复，覆盖后端 9 个文件、前端 6 个文件、测试与文档。

### 已解决

| 编号 | 类别 | 修复内容 |
|------|------|----------|
| H-07 | 高 / 安全 | 机器人检测指纹与封禁状态迁移至 Redis（`bot:fingerprint:*` / `bot:block:*`），多 Worker/多实例共享，封禁配置真正生效 |
| L-04 | 低 / 误伤 | 蜜罐路径改为精确匹配，移除 `/test`、`/dev`、`/staging`、`/api/private` 等易误伤路径 |
| M-02 | 中 / 架构 | 前端类型收敛到 `src/types/`（api/menu/permission/role/user），`Menu.sort_order` 统一必填，重复响应类型单一化 |
| M-05 | 中 / 死代码 | 删除 `AuthService._invalidate_role_permissions_cache` 死代码 |
| M-06 | 中 / 性能 | `get_menu` 详情改为单次查询 + 内存建子树，消除逐层 N+1 |
| M-09 | 中 / 一致性 | 删除 `get_me` 接口空计时 |
| M-10 | 中 / 分层 | `AuthService.get_user_with_roles()` 统一入口，Router 不再直接访问 Repository |
| M-11 | 中 / 一致性 | role/menu/permission 三个 router 统一为 `ResponseModel.success/error` |
| M-15 | 中 / 性能 | 图标按需注册（新增 `src/utils/icons.ts`，注册 42 个实际使用图标），主 chunk 1161→1024 kB |
| M-16 | 中 / 维护 | 迁移 SQLAlchemy 2.0 `DeclarativeBase`，消除 `declarative_base()` 弃用告警，表结构不变 |
| L-03 | 低 / 一致性 | 审计时间默认值改用 `tzu.get_now()`（时区感知，遵循 `USE_CHINA_TIMEZONE`） |

### 确认无需改动

- H-03 注册接口：速率限制已生效（`RateLimitMiddleware` 全局挂载，`/users/register` 每 IP 每小时 5 次）；
  验证码校验延后（项目暂无验证码基础设施，需独立实现验证码服务并接入注册页）。

### 延后处理

- C-09 Cookie HttpOnly：Cookie 由前端 `document.cookie` 写入，无法设置 `HttpOnly`；
  如需该属性，须改由后端 `Set-Cookie` 响应头下发 Token，并同步增加 CSRF 防护，涉及登录/刷新流程整体改造。

### 验证结果

- 后端：`uv run pytest` 17 项通过（新增 `tests/test_bot_detection_middleware.py` 6 例：
  蜜罐精确匹配、子串不误伤、行为模式分析）。
- 前端：`pnpm run build`（type-check + vite build）通过；改动文件 ESLint 无新增错误。
- 数据库：`DeclarativeBase` 迁移不改变表结构，无需新增 Alembic 迁移。

### 行为说明

- H-07 使 `BOT_DETECTION_BLOCK_DURATION` 配置首次真正生效：默认配置下自动化行为返回 429 验证码挑战，
  蜜罐精确命中或未启用验证码时封禁 IP（`bot:block:{ip}`，TTL = 封禁时长）。

### 关联提交

- `4e8fa30` fix: 处理代码审查遗留问题（限流确认、Bot检测Redis化、响应统一、类型收敛等）
