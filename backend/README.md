# 项目名称

## 简介
本项目基于 [FastAPI](https://fastapi.tiangolo.com/) 框架开发，旨在提供一套可扩展、可维护的中大型服务端应用结构示例。
## 目录结构
```bash
.
├── app
│   ├── core
│   │   ├── middleware
│   │   ├── settings
│   │   ├── tools
│   │   └── utils
│   ├── modules
│   ├── routers
│   ├── tests
│   └── app_lifecycle.py
├── docs
│   └── database_usage.md
├── main.py
├── pyproject.toml
├── README.md
├── .gitignore
├── .python-version
└── requirements.txt
```
## 快速开始
### 安装依赖
#### 推荐使用UV进行依赖安装
`pip install uv`
```bash
cd project_dir
uv venv .venv
uv sync
uv run main.py
```
#### 或者直接使用 uvicorn
`uvicorn main:app --host 0.0.0.0 --port 8000 --reload`

打开浏览器访问`http://localhost:8000`

##### OpenApiDoc:`http://localhost:8000/docs`
##### OpenJson:`http://localhost:8000/redoc`

## 数据库配置
本项目支持MySQL和PostgreSQL两种关系型数据库，并提供完全的异步支持。

配置数据库类型和连接参数请查看 [数据库使用指南](../docs/database_usage.md)。

## 贡献
#### 欢迎提交 issue 与 PR，共同完善项目结构与功能。

## License


