# Alembic 数据库迁移使用指南

## 概述

本项目已集成 Alembic 数据库迁移工具，用于管理数据库架构的版本控制。Alembic 会自动检测 SQLAlchemy 模型的变化并生成相应的迁移脚本。

## 配置

Alembic 配置文件位于 `alembic.ini` 和 `alembic/env.py`。项目会自动从 `app.core.settings.config` 读取数据库配置。

## 常用命令

### 1. 生成迁移脚本
```bash
alembic revision --autogenerate -m "描述迁移内容"
```

### 2. 应用迁移
```bash
alembic upgrade head
```

### 3. 回退迁移
```bash
alembic downgrade -1  # 回退一个版本
alembic downgrade base  # 回退到初始状态
```

### 4. 查看迁移历史
```bash
alembic history  # 查看所有迁移历史
alembic current  # 查看当前版本
```

## 注意事项

1. **数据库类型支持**：本项目支持 MySQL 和 PostgreSQL，Alembic 会自动根据配置调整连接字符串。

2. **模型导入**：所有模型需要在 `app/modules/models/` 目录下定义，并确保被导入到 `app/core/connects/database.py` 中的 `Base.metadata`。

3. **迁移脚本检查**：自动生成的迁移脚本需要人工检查，确保没有意外的更改。

4. **外键约束**：如果迁移过程中遇到外键约束问题，可能需要手动调整迁移脚本或先删除相关约束。

## 最佳实践

1. **频繁提交**：每次模型变更都应该创建对应的迁移。

2. **测试迁移**：在开发环境测试迁移脚本，确保没有问题后再应用到生产环境。

3. **备份数据**：在生产环境应用迁移前，务必备份数据库。

4. **小步快跑**：尽量保持每次迁移的范围较小，便于问题定位和回退。

## 故障排除

### 1. 外键约束错误
如果遇到外键约束错误，可以尝试：
```sql
-- 临时禁用外键检查（MySQL）
SET FOREIGN_KEY_CHECKS = 0;
-- 执行迁移
-- 重新启用外键检查
SET FOREIGN_KEY_CHECKS = 1;
```

### 2. 迁移冲突
如果多人同时修改模型，可能会产生迁移冲突。解决方法是：
1. 合并代码
2. 删除冲突的迁移文件
3. 重新生成迁移

### 3. 数据库连接错误
确保数据库配置正确，并且数据库服务正在运行。

## 项目结构

```
alembic/
├── alembic.ini          # Alembic 配置文件
├── env.py               # 迁移环境配置
├── script.py.mako       # 迁移脚本模板
└── versions/            # 迁移脚本目录
    └── xxxxxxxx_xxx.py  # 具体的迁移脚本
```