<h1 align="center">AI Tavern</h1>

<h3 align="center">基于 RuoYi-Vue3-FastAPI 二次开发的 AI 酒馆角色聊天系统</h3>

<p align="center">
  <img alt="version" src="https://img.shields.io/badge/version-1.0.0-brightgreen">
  <img alt="python" src="https://img.shields.io/badge/python-3.11-blue">
  <img alt="node" src="https://img.shields.io/badge/node-20.x-blue">
  <img alt="vue" src="https://img.shields.io/badge/vue-3.5.26-42b883">
  <img alt="fastapi" src="https://img.shields.io/badge/FastAPI-0.128.2-009688">
  <img alt="mysql" src="https://img.shields.io/badge/MySQL-8.0-orange">
  <img alt="redis" src="https://img.shields.io/badge/Redis-7.x-red">
  <img alt="DeepSeek" src="https://img.shields.io/badge/DeepSeek-v4--flash-purple">
  <img alt="license" src="https://img.shields.io/badge/license-MIT-green">
</p>

## 项目简介

AI Tavern 是在 `RuoYi-Vue3-FastAPI 1.9.0` 基础上二次开发的 AI 角色聊天后台系统。项目保留了若依体系里的用户管理、角色管理、菜单权限、日志管理等后台能力，并新增 AI 酒馆相关功能，用于角色管理、会话管理、对话记录存储、DeepSeek 模型接入和用户 Token / 金额额度管理。

当前版本重点面向网页端管理后台，移动端目录保留但暂不作为主要开发目标。

## 当前能力

### AI 酒馆

1. 角色管理：创建和维护 AI 角色资料、提示词、状态等信息。
2. 会话管理：查看和维护用户与角色的会话。
3. 角色聊天：网页端可与角色进行连续对话。
4. 对话记录：用户消息和模型回复写入 MySQL，便于后续审计和统计。
5. 生成耗时：聊天消息展示模型生成耗时，单位为秒，支持小数。
6. 上下文总结：支持会话摘要能力，减少长期聊天上下文压力。

### DeepSeek 接入

1. 使用 OpenAI SDK 兼容方式接入 DeepSeek。
2. 默认模型：`deepseek-v4-flash`。
3. 默认非思考模式：`DEEPSEEK_THINKING_ENABLED = false`。
4. API Key 通过后端环境变量配置，不提交到 GitHub。

### Token 与额度管理

1. 记录每次对话的 prompt tokens、completion tokens、total tokens。
2. 记录缓存命中与未命中 token。
3. 按 DeepSeek 计费规则估算人民币消耗。
4. 后台提供 Token 消耗页面。
5. 系统管理中提供用户 Token 设置页面。
6. 支持按人民币额度设置每日、每月、总额度。
7. 权限可由角色管理控制。

### 系统管理

1. 用户管理：创建用户、修改用户、分配角色。
2. 角色管理：配置角色菜单权限和按钮权限。
3. 菜单管理：维护后台菜单、路由、权限标识。
4. 用户 Token 设置：维护用户 AI 使用额度。
5. 登录验证码：当前项目已取消登录验证码机制。

## 技术栈

### 后端

- Python 3.11
- FastAPI 0.128.2
- SQLAlchemy 2.0.46
- MySQL 8.0
- Redis 7.x
- OpenAI SDK 2.17.0
- JWT / OAuth2

### 前端

- Vue 3.5.26
- Vite 6.4.1
- Element Plus 2.13.1
- Pinia 3.0.4
- Vue Router 4.6.4
- Axios 1.13.5

## 目录结构

```text
.
├── docs                         # 项目文档
├── ruoyi-fastapi-backend         # FastAPI 后端
├── ruoyi-fastapi-frontend        # Vue3 网页端
├── ruoyi-fastapi-app             # 移动端目录，当前暂不重点开发
└── ruoyi-fastapi-test            # 测试目录
```

## 环境变量

真实环境变量文件不会提交到 GitHub。首次部署或本地开发时，请复制模板后再填写自己的配置。

后端：

```bash
cd ruoyi-fastapi-backend
cp .env.example .env.prod
```

前端：

```bash
cd ruoyi-fastapi-frontend
cp .env.example .env.production
```

需要重点填写：

```env
DB_USERNAME = '你的数据库用户'
DB_PASSWORD = '你的数据库密码'
DB_DATABASE = 'ruoyi_fastapi'

DEEPSEEK_API_KEY = '你的 DeepSeek API Key'
DEEPSEEK_MODEL = 'deepseek-v4-flash'
DEEPSEEK_THINKING_ENABLED = false
```

## 本地启动

### 后端

```bash
cd ruoyi-fastapi-backend
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements-prod.txt
python app.py --env=prod
```

Windows PowerShell 可使用：

```powershell
cd ruoyi-fastapi-backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements-prod.txt
python app.py --env=prod
```

### 前端

```bash
cd ruoyi-fastapi-frontend
npm install --registry=https://registry.npmmirror.com
npm run dev
```

生产打包：

```bash
npm run build:prod
```

## 数据库初始化

首次部署时按顺序导入：

```text
ruoyi-fastapi-backend/sql/ruoyi-fastapi.sql
ruoyi-fastapi-backend/sql/ai-tavern.sql
```

注意：后续版本更新不要重复导入初始化 SQL，避免影响已有用户、角色、会话、聊天记录和 Token 消耗数据。后续数据库结构变化应使用增量 SQL。

## 部署文档

推荐使用宝塔面板部署：

- [宝塔 Python 项目管理器部署详细版](./docs/baota-python-manager-full-deploy.md)
- [GitHub 初始上传与后续开发流程](./docs/github-initial-upload.md)

## 服务器更新原则

为了保证线上数据不丢失，后续升级版本时请遵守：

1. 不删除 MySQL 数据库。
2. 不重新创建 `ruoyi_fastapi` 数据库。
3. 不重复导入 `ruoyi-fastapi.sql` 和 `ai-tavern.sql`。
4. 不覆盖服务器上的 `.env.prod`。
5. 先备份数据库，再上传新版代码。
6. 如果有数据库变化，只执行增量 SQL。

## 安全提醒

不要把以下内容提交到 GitHub：

```text
.env.dev
.env.prod
.env.dockermy
.env.dockerpg
venv
node_modules
dist
logs
```

如果 API Key 曾经在聊天记录、截图或仓库历史里明文出现，建议立即去对应平台重置 Key。

## 许可

本项目基于 RuoYi-Vue3-FastAPI 二次开发，遵循 MIT License。
