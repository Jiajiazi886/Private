# GitHub 初始上传与后续开发流程

这份文档用于把当前项目作为 GitHub 初始版本保存，方便后续继续开发。

## 1. 推荐的仓库根目录

推荐把下面这个目录作为 Git 仓库根目录：

```text
D:\cc\cc\jiuba\RuoYi-Vue3-FastAPI-1.9.0\RuoYi-Vue3-FastAPI-1.9.0
```

这个目录里有：

```text
ruoyi-fastapi-backend
ruoyi-fastapi-frontend
ruoyi-fastapi-app
docs
README.md
.gitignore
```

## 2. 不要上传的内容

这些内容不要上传 GitHub：

```text
ruoyi-fastapi-backend/.env.dev
ruoyi-fastapi-backend/.env.prod
ruoyi-fastapi-backend/.env.dockermy
ruoyi-fastapi-backend/.env.dockerpg
ruoyi-fastapi-backend/venv
ruoyi-fastapi-backend/logs
ruoyi-fastapi-frontend/node_modules
ruoyi-fastapi-frontend/dist
ruoyi-fastapi-app/node_modules
```

原因：

```text
.env 里有密钥和数据库密码
node_modules 和 venv 可以重新安装
dist 可以重新打包生成
logs 是运行日志
```

## 3. 第一次提交前检查密钥

在项目根目录执行：

```bash
rg -uu "sk-[A-Za-z0-9]|DEEPSEEK_API_KEY|DB_PASSWORD|JWT_SECRET_KEY" -g "!**/node_modules/**" -g "!**/dist/**" -g "!**/.git/**"
```

如果只在这些文件里看到真实值，一般没问题，因为它们被 `.gitignore` 忽略：

```text
ruoyi-fastapi-backend/.env.dev
ruoyi-fastapi-backend/.env.prod
ruoyi-fastapi-backend/.env.dockermy
ruoyi-fastapi-backend/.env.dockerpg
```

如果在源码文件里看到真实 API Key，需要先删除。

## 4. 本地初始化 Git

进入项目根目录：

```bash
cd D:\cc\cc\jiuba\RuoYi-Vue3-FastAPI-1.9.0\RuoYi-Vue3-FastAPI-1.9.0
```

初始化：

```bash
git init
git branch -M main
```

查看将要提交的文件：

```bash
git status --short
```

确认没有这些文件：

```text
.env.dev
.env.prod
node_modules
dist
venv
logs
```

## 5. 创建初始提交

```bash
git add .
git status --short
git commit -m "Initial project snapshot"
```

如果 Git 提示没有配置用户名和邮箱，执行：

```bash
git config --global user.name "你的GitHub用户名"
git config --global user.email "你的邮箱"
```

然后重新提交：

```bash
git commit -m "Initial project snapshot"
```

## 6. 在 GitHub 创建仓库

打开 GitHub，创建一个新仓库。

建议：

```text
Repository name：ai-tavern
Visibility：Private
Initialize this repository：不要勾选 README / .gitignore / license
```

建议先用 Private 私有仓库，等密钥和历史都确认安全后再考虑公开。

## 7. 绑定远程仓库并推送

GitHub 创建完仓库后，会给你一个地址，类似：

```text
https://github.com/你的用户名/ai-tavern.git
```

在本地执行：

```bash
git remote add origin https://github.com/你的用户名/ai-tavern.git
git push -u origin main
```

如果以后换远程地址：

```bash
git remote set-url origin https://github.com/你的用户名/ai-tavern.git
```

## 8. 后续开发流程

每次开发前：

```bash
git pull
```

开发完成后：

```bash
git status --short
git add .
git commit -m "描述这次改了什么"
git push
```

## 9. 服务器更新代码时保护数据

服务器数据库不要删，不要重新导入初始化 SQL。

更新前先备份数据库：

```bash
mysqldump -u ruoyi_fastapi -p --single-transaction --routines --triggers ruoyi_fastapi > /www/backup/ai-tavern/ruoyi_fastapi_$(date +%F_%H%M%S).sql
```

更新代码后：

```bash
cd /www/wwwroot/ai-tavern/ruoyi-fastapi-backend
source venv/bin/activate
pip install -r requirements-prod.txt -i https://mirrors.tencent.com/pypi/simple
```

然后重启宝塔 Python 项目管理器里的后端项目。

前端重新打包或上传新的 `dist`，再重载 Nginx：

```bash
nginx -t
systemctl reload nginx
```

## 10. 重要安全提醒

你之前用于开发的 DeepSeek API Key 已经在本地 `.env` 文件里出现过，也曾经在对话中明文出现。建议去 DeepSeek 控制台重新生成一个新 Key，并废弃旧 Key。

以后真实 Key 只放：

```text
服务器 /www/wwwroot/ai-tavern/ruoyi-fastapi-backend/.env.prod
本地 ruoyi-fastapi-backend/.env.dev
```

不要提交到 GitHub。
