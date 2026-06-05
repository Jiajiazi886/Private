# AI Tavern 第二版更新到腾讯云宝塔部署文档

这份文档用于：你服务器上已经部署成功第一版，现在要把本地第二版更新到服务器，并且保证数据库里的用户、角色、聊天记录、Token 记录不丢失。

你的当前部署信息按下面写：

```text
服务器项目目录：/www/wwwroot/ai-tavern
后端目录：/www/wwwroot/ai-tavern/ruoyi-fastapi-backend
前端目录：/www/wwwroot/ai-tavern/ruoyi-fastapi-frontend
后端端口：9099
接口前缀：/prod-api
域名：www.xn--kbrr2vyxjytebq4azkrrie.icu
宝塔 Python 项目名：ai-tavern-backend
```

## 0. 重要原则

更新第二版时，千万不要重新导入这两个初始化 SQL：

```text
ruoyi-fastapi-backend/sql/ruoyi-fastapi.sql
ruoyi-fastapi-backend/sql/ai-tavern.sql
```

这两个是新服务器首次部署时用的。已经上线以后，再导入它们可能会覆盖或破坏已有数据。

第二版只需要执行这个增量 SQL：

```text
ruoyi-fastapi-backend/sql/update-v2-ai-tavern-chat.sql
```

这个 SQL 只用于给聊天功能补充新字段：会话提示词、强制记忆、消息编辑标记等。

## 1. 第二版更新内容

本次第二版主要更新 AI 酒馆聊天页和后端存储能力：

```text
1. 手机端聊天页改成微信式两层结构：外层会话/角色列表，内层聊天详情。
2. 手机端进入聊天详情后隐藏后台顶部导航和标签栏，进入沉浸式聊天。
3. 聊天标题栏固定在顶部，消息滚动时不会隐藏。
4. 右下角加号集成功能面板。
5. 新增会话专属提示词，可以针对单个会话设置规则。
6. 新增摘要查看、编辑、保存、重建。
7. 新增强制记忆，会作为高优先级记忆传给 AI。
8. 新增 AI 回复/历史消息编辑能力。
9. 后端新增对应接口和数据库字段。
10. 数据库保留原有用户、角色、会话、消息、Token 消耗记录。
```

第二版涉及的增量数据库字段：

```text
ai_conversation.conversation_prompt
ai_conversation.forced_memory
ai_message.is_edited
ai_message.update_time
```

## 2. 本文使用的软件版本

宝塔里版本小一点没关系，但大版本尽量一致。

| 工具 | 建议版本 |
| --- | --- |
| 宝塔面板 | 9.x |
| 系统 | OpenCloudOS 9.x |
| Nginx | 1.24.x |
| MySQL | 8.0.x，或者 5.7.x |
| Redis | 7.2.x，或者 6.2.x |
| Python | 3.11.x，不能用 3.7 |
| Node.js | 20.x LTS，22.x 也可以 |
| npm | 10.x |
| FastAPI | 0.128.2 |
| Vite | 6.4.1 |

服务器检查命令：

```bash
python3.11 --version
node -v
npm -v
mysql --version
redis-cli ping
nginx -v
```

`redis-cli ping` 正常应该返回：

```text
PONG
```

## 3. 本地先提交第二版代码到 GitHub

在你本地电脑打开终端，进入项目根目录：

```powershell
cd D:\cc\cc\jiuba\RuoYi-Vue3-FastAPI-1.9.0\RuoYi-Vue3-FastAPI-1.9.0
```

先确认当前分支：

```powershell
git branch --show-current
```

如果显示 `main`，后面推送就用 `main`。如果显示 `master`，后面推送就把 `main` 改成 `master`。

查看改动：

```powershell
git status
```

提交第二版：

```powershell
git add .
git commit -m "feat: update ai tavern mobile chat v2"
git push origin main
```

如果你的分支是 `master`，执行：

```powershell
git push origin master
```

提交成功后，打开 GitHub 仓库确认能看到最新代码：

```text
https://github.com/Jiajiazi886/Private.git
```

## 4. 服务器备份，必须做

打开宝塔终端，先创建备份目录：

```bash
mkdir -p /www/backup/ai-tavern
```

### 3.1 备份后端配置文件

```bash
cp /www/wwwroot/ai-tavern/ruoyi-fastapi-backend/.env.prod /www/backup/ai-tavern/.env.prod.$(date +%F-%H%M%S).bak
```

### 3.2 备份数据库

如果你的数据库名是 `ruoyi_fastapi`，执行：

```bash
mysqldump -uroot -p ruoyi_fastapi > /www/backup/ai-tavern/ruoyi_fastapi.$(date +%F-%H%M%S).sql
```

输入 MySQL root 密码后等待完成。

如果你不是 root 用户，而是宝塔创建的数据库用户，例如 `ruoyi_fastapi`，执行：

```bash
mysqldump -uruoyi_fastapi -p ruoyi_fastapi > /www/backup/ai-tavern/ruoyi_fastapi.$(date +%F-%H%M%S).sql
```

检查备份文件是否存在：

```bash
ls -lh /www/backup/ai-tavern
```

### 3.3 备份当前服务器代码

```bash
cd /www/wwwroot
tar --exclude='ai-tavern/ruoyi-fastapi-frontend/node_modules' \
    --exclude='ai-tavern/ruoyi-fastapi-frontend/dist' \
    --exclude='ai-tavern/ruoyi-fastapi-backend/__pycache__' \
    -czf /www/backup/ai-tavern/ai-tavern-code.$(date +%F-%H%M%S).tar.gz ai-tavern
```

检查备份：

```bash
ls -lh /www/backup/ai-tavern
```

看到 `.sql` 和 `.tar.gz` 两类文件，就可以继续。

## 5. 停止后端项目

打开宝塔面板：

```text
宝塔面板 -> Python 项目管理器 -> ai-tavern-backend -> 停止
```

也可以在终端检查 9099 是否还在运行：

```bash
ss -lntp | grep 9099
```

如果没有输出，说明后端已经停止。

## 6. 更新代码，推荐方式：GitHub 拉取

进入项目目录：

```bash
cd /www/wwwroot/ai-tavern
```

如果服务器上的项目本来就是用 GitHub 拉下来的，执行：

```bash
git status
git pull origin main
```

如果你的分支是 `master`，执行：

```bash
git pull origin master
```

拉取完成后，确认第二版 SQL 文件存在：

```bash
ls /www/wwwroot/ai-tavern/ruoyi-fastapi-backend/sql/update-v2-ai-tavern-chat.sql
```

如果能看到这个文件，说明代码更新到了第二版。

## 7. 如果服务器不能拉 GitHub，用上传覆盖方式

如果 GitHub 是私有仓库，服务器没有配置权限，`git pull` 失败，可以用这个方式。

### 6.1 本地打包

在本地电脑项目根目录执行：

```powershell
cd D:\cc\cc\jiuba\RuoYi-Vue3-FastAPI-1.9.0\RuoYi-Vue3-FastAPI-1.9.0
```

把下面两个文件夹压缩成 zip：

```text
ruoyi-fastapi-backend
ruoyi-fastapi-frontend
```

不要只上传 `dist`，因为这次后端接口和数据库字段也更新了。

### 6.2 上传到服务器

宝塔面板进入：

```text
文件 -> /www/wwwroot/ai-tavern
```

上传 zip 后解压。

注意：

```text
不要删除 /www/wwwroot/ai-tavern/ruoyi-fastapi-backend/.env.prod
不要删除后端上传目录 vf_admin/upload_path
不要重新导入初始化 SQL
```

如果你不确定，先把服务器 `.env.prod` 保存出来：

```bash
cp /www/wwwroot/ai-tavern/ruoyi-fastapi-backend/.env.prod /root/.env.prod.keep
```

覆盖代码后再放回去：

```bash
cp /root/.env.prod.keep /www/wwwroot/ai-tavern/ruoyi-fastapi-backend/.env.prod
```

## 8. 检查后端生产配置

打开：

```bash
cd /www/wwwroot/ai-tavern/ruoyi-fastapi-backend
cat .env.prod
```

重点检查这些配置：

```env
APP_ENV = 'prod'
APP_ROOT_PATH = '/prod-api'
APP_HOST = '0.0.0.0'
APP_PORT = 9099
APP_RELOAD = false
APP_WORKERS = 1

DB_TYPE = 'mysql'
DB_HOST = '127.0.0.1'
DB_PORT = 3306
DB_USERNAME = '你的数据库用户'
DB_PASSWORD = '你的数据库密码'
DB_DATABASE = '你的数据库名'
DB_ECHO = false

REDIS_HOST = '127.0.0.1'
REDIS_PORT = 6379
REDIS_DATABASE = 2

DEEPSEEK_API_KEY = '你的 DeepSeek Key'
DEEPSEEK_BASE_URL = 'https://api.deepseek.com'
DEEPSEEK_MODEL = 'deepseek-v4-flash'
DEEPSEEK_THINKING_ENABLED = false
DEEPSEEK_MAX_TOKENS = 2048
```

确认端口还是 `9099`，确认 `APP_ROOT_PATH` 是 `/prod-api`。

## 9. 执行第二版数据库增量 SQL

进入后端目录：

```bash
cd /www/wwwroot/ai-tavern/ruoyi-fastapi-backend
```

执行增量 SQL：

```bash
mysql -u你的数据库用户 -p 你的数据库名 < sql/update-v2-ai-tavern-chat.sql
```

例子：

```bash
mysql -uruoyi_fastapi -p ruoyi_fastapi < sql/update-v2-ai-tavern-chat.sql
```

输入数据库密码后，如果没有明显报错，就说明执行完成。

如果提示类似：

```text
Duplicate column name
```

说明这些字段已经存在，通常表示之前已经执行过或后端自动补过字段，这种情况可以继续下一步。

执行完后可以检查字段：

```bash
mysql -u你的数据库用户 -p 你的数据库名 -e "SHOW COLUMNS FROM ai_conversation LIKE 'conversation_prompt';"
mysql -u你的数据库用户 -p 你的数据库名 -e "SHOW COLUMNS FROM ai_conversation LIKE 'forced_memory';"
mysql -u你的数据库用户 -p 你的数据库名 -e "SHOW COLUMNS FROM ai_message LIKE 'is_edited';"
mysql -u你的数据库用户 -p 你的数据库名 -e "SHOW COLUMNS FROM ai_message LIKE 'update_time';"
```

四个命令都能查到字段，就对了。

## 10. 更新后端依赖

进入后端目录：

```bash
cd /www/wwwroot/ai-tavern/ruoyi-fastapi-backend
```

进入宝塔 Python 项目的虚拟环境：

```bash
unset _BT_PROJECT_ENV && source /www/server/panel/script/btpyprojectenv.sh ai-tavern-backend
source /www/server/python_project/vhost/env/ai-tavern-backend.env
```

确认 Python 是 3.11：

```bash
python --version
```

正确应该类似：

```text
Python 3.11.x
```

安装依赖：

```bash
pip install -U pip -i https://pypi.tuna.tsinghua.edu.cn/simple
pip install -r requirements-prod.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

如果 `requirements-prod.txt` 不存在，再用：

```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

检查关键依赖：

```bash
python -c "import uvicorn, fastapi, openai; print('backend deps ok')"
```

看到：

```text
backend deps ok
```

说明后端依赖没问题。

## 11. 打包前端

进入前端目录：

```bash
cd /www/wwwroot/ai-tavern/ruoyi-fastapi-frontend
```

安装依赖：

```bash
npm install --registry=https://registry.npmmirror.com
```

打包：

```bash
NODE_OPTIONS="--max-old-space-size=4096" npm run build:prod
```

如果打包成功，会看到类似：

```text
vite build
✓ built
```

并且生成：

```text
/www/wwwroot/ai-tavern/ruoyi-fastapi-frontend/dist
```

检查：

```bash
ls /www/wwwroot/ai-tavern/ruoyi-fastapi-frontend/dist
```

里面应该能看到：

```text
index.html
static
```

## 12. 如果服务器前端打包内存不够

如果出现：

```text
JavaScript heap out of memory
```

说明服务器内存不够打包。可以在本地电脑打包，然后上传 `dist`。

本地电脑执行：

```powershell
cd D:\cc\cc\jiuba\RuoYi-Vue3-FastAPI-1.9.0\RuoYi-Vue3-FastAPI-1.9.0\ruoyi-fastapi-frontend
npm install --registry=https://registry.npmmirror.com
$env:NODE_OPTIONS="--max-old-space-size=4096"
npm run build:prod
```

打包成功后，把本地这个目录上传到服务器：

```text
D:\cc\cc\jiuba\RuoYi-Vue3-FastAPI-1.9.0\RuoYi-Vue3-FastAPI-1.9.0\ruoyi-fastapi-frontend\dist
```

覆盖服务器这个目录：

```text
/www/wwwroot/ai-tavern/ruoyi-fastapi-frontend/dist
```

建议覆盖前先备份服务器旧 dist：

```bash
cd /www/wwwroot/ai-tavern/ruoyi-fastapi-frontend
mv dist dist.bak.$(date +%F-%H%M%S)
```

然后再上传新的 `dist`。

## 13. 启动后端

打开宝塔面板：

```text
宝塔面板 -> Python 项目管理器 -> ai-tavern-backend -> 启动
```

如果已经在运行，就点：

```text
重启
```

启动后在终端检查端口：

```bash
ss -lntp | grep 9099
```

能看到 `9099`，说明后端启动了。

检查后端接口：

```bash
curl -I http://127.0.0.1:9099/docs
```

正常应该看到：

```text
HTTP/1.1 200 OK
```

如果你生产环境关闭了 docs，可以改查：

```bash
curl -I http://127.0.0.1:9099/prod-api/getRouters
```

未登录返回 401 或 422 也没关系，只要不是连接失败、502、拒绝连接。

## 14. 检查 Nginx

如果你没有改 Nginx 配置，这一步只需要测试和重载。

```bash
nginx -t
systemctl reload nginx
```

正确输出应该包含：

```text
syntax is ok
test is successful
```

检查网站：

```bash
curl -I http://www.xn--kbrr2vyxjytebq4azkrrie.icu
```

正常应该看到：

```text
HTTP/1.1 200 OK
```

检查接口反向代理：

```bash
curl -I http://www.xn--kbrr2vyxjytebq4azkrrie.icu/prod-api/docs
```

如果 docs 没关闭，应该是 200。

如果 docs 关闭了，只要浏览器登录不出现 502 就行。

## 15. 浏览器验证

打开：

```text
http://www.xn--kbrr2vyxjytebq4azkrrie.icu
```

登录后台：

```text
账号：admin
密码：你的管理员密码
```

重点检查：

```text
1. 系统管理 -> 用户管理还在
2. 系统管理 -> 角色管理还在
3. 系统管理 -> 用户Token设置能打开
4. AI 管理 -> AI 酒馆管理 -> 角色聊天能打开
5. 手机宽度下进入聊天详情，会隐藏顶部导航和标签栏
6. 聊天标题固定在顶部，滚动不会消失
7. 右下角加号能打开功能面板
8. 摘要、强制记忆、提示词、编辑 AI 回复能打开弹窗
9. 发一句话，AI 能正常回复
10. Token 消耗页面能记录消耗
```

## 16. 常见问题

### 15.1 网站能打开，但是登录提示 502

通常是后端没启动，检查：

```bash
ss -lntp | grep 9099
```

没有输出就去宝塔 Python 项目管理器启动后端。

再看后端日志：

```bash
cd /www/wwwroot/ai-tavern/ruoyi-fastapi-backend
tail -n 100 logs/*.log
```

### 15.2 后端启动报 `No module named uvicorn`

说明没有进入正确虚拟环境，重新执行：

```bash
cd /www/wwwroot/ai-tavern/ruoyi-fastapi-backend
unset _BT_PROJECT_ENV && source /www/server/panel/script/btpyprojectenv.sh ai-tavern-backend
source /www/server/python_project/vhost/env/ai-tavern-backend.env
pip install -r requirements-prod.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 15.3 后端启动报 `cannot import name Literal`

说明用了 Python 3.7。必须换 Python 3.11。

宝塔里重新创建 Python 项目时选择：

```text
Python 3.11.x
```

### 15.4 前端打包内存不足

用本地电脑打包，然后上传 `dist`，看第 12 步。

### 15.5 执行增量 SQL 提示 Duplicate column

通常说明字段已经存在，可以继续启动项目。

不要因此去重新导入初始化 SQL。

### 15.6 更新后样式没变

可能是浏览器缓存或 Nginx 缓存。

先强制刷新浏览器：

```text
Ctrl + F5
```

再重载 Nginx：

```bash
nginx -t
systemctl reload nginx
```

确认 `dist` 是新的：

```bash
ls -lh /www/wwwroot/ai-tavern/ruoyi-fastapi-frontend/dist/index.html
```

## 17. 回滚方式

如果第二版更新后网站异常，先不要动数据库，优先回滚代码和前端。

### 16.1 回滚前端 dist

如果第 12 步备份过旧 dist：

```bash
cd /www/wwwroot/ai-tavern/ruoyi-fastapi-frontend
mv dist dist.bad.$(date +%F-%H%M%S)
mv dist.bak.你的备份时间 dist
nginx -t
systemctl reload nginx
```

### 16.2 回滚整套代码

查看备份：

```bash
ls -lh /www/backup/ai-tavern
```

解压代码备份到临时目录：

```bash
mkdir -p /www/backup/ai-tavern/restore-test
tar -xzf /www/backup/ai-tavern/ai-tavern-code.你的备份时间.tar.gz -C /www/backup/ai-tavern/restore-test
```

确认里面有旧代码后，再手动把旧的 `ruoyi-fastapi-backend` 和 `ruoyi-fastapi-frontend/dist` 覆盖回去。

数据库一般不需要回滚，因为第二版只是加字段，不会删除旧数据。

## 18. 最短更新流程

如果你已经熟悉了，以后每次更新可以按这个简化版做：

```bash
# 1. 备份
mkdir -p /www/backup/ai-tavern
mysqldump -u你的数据库用户 -p 你的数据库名 > /www/backup/ai-tavern/db.$(date +%F-%H%M%S).sql
cp /www/wwwroot/ai-tavern/ruoyi-fastapi-backend/.env.prod /www/backup/ai-tavern/.env.prod.$(date +%F-%H%M%S).bak

# 2. 拉代码
cd /www/wwwroot/ai-tavern
git pull origin main

# 3. 执行本版本增量 SQL，只执行一次
cd /www/wwwroot/ai-tavern/ruoyi-fastapi-backend
mysql -u你的数据库用户 -p 你的数据库名 < sql/update-v2-ai-tavern-chat.sql

# 4. 更新后端依赖
unset _BT_PROJECT_ENV && source /www/server/panel/script/btpyprojectenv.sh ai-tavern-backend
source /www/server/python_project/vhost/env/ai-tavern-backend.env
pip install -r requirements-prod.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 5. 打包前端
cd /www/wwwroot/ai-tavern/ruoyi-fastapi-frontend
npm install --registry=https://registry.npmmirror.com
NODE_OPTIONS="--max-old-space-size=4096" npm run build:prod

# 6. 重启后端和 Nginx
nginx -t
systemctl reload nginx
```

最后去宝塔 Python 项目管理器里重启：

```text
ai-tavern-backend
```

然后打开域名测试。
