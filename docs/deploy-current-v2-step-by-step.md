# 当前第二版项目宝塔更新部署步骤

这份文档只针对当前项目：

```text
GitHub 仓库：https://github.com/Jiajiazi886/Private.git
GitHub 分支：main
服务器项目目录：/www/wwwroot/ai-tavern
后端目录：/www/wwwroot/ai-tavern/ruoyi-fastapi-backend
前端目录：/www/wwwroot/ai-tavern/ruoyi-fastapi-frontend
后端端口：9099
接口前缀：/prod-api
域名：www.xn--kbrr2vyxjytebq4azkrrie.icu
宝塔 Python 项目名：ai-tavern-backend
```

本文只写一条部署路线：服务器从 GitHub 的 `main` 分支拉取最新代码，然后更新数据库、打包前端、重启后端。

## 1. 本次第二版包含的功能

```text
1. 手机端聊天页改成微信式两层结构。
2. 进入聊天详情后隐藏顶部导航栏和标签栏。
3. 聊天标题栏固定在顶部，滚动消息时不会消失。
4. 右下角加号集成功能面板。
5. 新增会话专属提示词。
6. 新增摘要查看、编辑、保存、重建。
7. 新增强制记忆。
8. 新增 AI 回复和历史消息编辑。
9. 后端新增对应接口。
10. 数据库新增对应字段。
```

本次新增数据库字段：

```text
ai_conversation.conversation_prompt
ai_conversation.forced_memory
ai_message.is_edited
ai_message.update_time
```

本次只执行这个增量 SQL：

```text
/www/wwwroot/ai-tavern/ruoyi-fastapi-backend/sql/update-v2-ai-tavern-chat.sql
```

不要重新导入下面两个初始化 SQL：

```text
/www/wwwroot/ai-tavern/ruoyi-fastapi-backend/sql/ruoyi-fastapi.sql
/www/wwwroot/ai-tavern/ruoyi-fastapi-backend/sql/ai-tavern.sql
```

## 2. 进入宝塔终端

打开宝塔面板：

```text
宝塔面板 -> 终端
```

所有服务器命令都在宝塔终端执行。

## 3. 检查服务器工具版本

执行：

```bash
python3.11 --version
node -v
npm -v
mysql --version
redis-cli ping
nginx -v
```

你需要看到类似结果：

```text
Python 3.11.x
v20.x.x
10.x.x
PONG
nginx/1.24.x
```

Python 必须是 3.11。

## 4. 设置本次部署变量

把下面命令复制到宝塔终端执行。

把 `你的数据库名`、`你的数据库用户` 改成你宝塔数据库里的真实值。

```bash
export PROJECT_DIR=/www/wwwroot/ai-tavern
export BACKEND_DIR=/www/wwwroot/ai-tavern/ruoyi-fastapi-backend
export FRONTEND_DIR=/www/wwwroot/ai-tavern/ruoyi-fastapi-frontend
export BACKUP_DIR=/www/backup/ai-tavern
export DB_NAME=你的数据库名
export DB_USER=你的数据库用户
```

例子：

```bash
export DB_NAME=ruoyi_fastapi
export DB_USER=ruoyi_fastapi
```

创建备份目录：

```bash
mkdir -p $BACKUP_DIR
```

## 5. 备份后端生产配置

执行：

```bash
cp $BACKEND_DIR/.env.prod $BACKUP_DIR/.env.prod.$(date +%F-%H%M%S).bak
```

检查备份：

```bash
ls -lh $BACKUP_DIR
```

## 6. 备份数据库

执行：

```bash
mysqldump -u$DB_USER -p $DB_NAME > $BACKUP_DIR/$DB_NAME.$(date +%F-%H%M%S).sql
```

终端提示输入密码时，输入你的数据库密码。

检查备份：

```bash
ls -lh $BACKUP_DIR
```

你应该看到一个 `.sql` 文件。

## 7. 备份当前服务器代码

执行：

```bash
cd /www/wwwroot
tar --exclude='ai-tavern/ruoyi-fastapi-frontend/node_modules' \
    --exclude='ai-tavern/ruoyi-fastapi-frontend/dist' \
    --exclude='ai-tavern/ruoyi-fastapi-backend/__pycache__' \
    --exclude='ai-tavern/ruoyi-fastapi-backend/logs' \
    -czf $BACKUP_DIR/ai-tavern-code.$(date +%F-%H%M%S).tar.gz ai-tavern
```

检查备份：

```bash
ls -lh $BACKUP_DIR
```

你应该看到一个 `.tar.gz` 文件。

## 8. 停止后端

打开宝塔面板：

```text
宝塔面板 -> Python 项目管理器 -> ai-tavern-backend -> 停止
```

回到宝塔终端检查端口：

```bash
ss -lntp | grep 9099
```

没有输出代表后端已经停止。

## 9. 从 GitHub 拉取当前第二版代码

执行：

```bash
cd $PROJECT_DIR
git pull origin main
```

查看最新提交：

```bash
git log -1 --oneline
```

你应该看到类似：

```text
1025fa7 feat: improve ai tavern chat v2
```

确认增量 SQL 文件存在：

```bash
ls $BACKEND_DIR/sql/update-v2-ai-tavern-chat.sql
```

## 10. 检查后端生产配置

执行：

```bash
cd $BACKEND_DIR
cat .env.prod
```

重点确认这些值：

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

`.env.prod` 不要提交到 GitHub，只保留在服务器。

## 11. 执行第二版数据库增量 SQL

执行：

```bash
cd $BACKEND_DIR
mysql -u$DB_USER -p $DB_NAME < sql/update-v2-ai-tavern-chat.sql
```

输入数据库密码。

执行完检查四个字段：

```bash
mysql -u$DB_USER -p $DB_NAME -e "SHOW COLUMNS FROM ai_conversation LIKE 'conversation_prompt';"
mysql -u$DB_USER -p $DB_NAME -e "SHOW COLUMNS FROM ai_conversation LIKE 'forced_memory';"
mysql -u$DB_USER -p $DB_NAME -e "SHOW COLUMNS FROM ai_message LIKE 'is_edited';"
mysql -u$DB_USER -p $DB_NAME -e "SHOW COLUMNS FROM ai_message LIKE 'update_time';"
```

四个字段都能查到，数据库更新完成。

## 12. 更新后端依赖

进入后端目录：

```bash
cd $BACKEND_DIR
```

进入宝塔 Python 项目虚拟环境：

```bash
unset _BT_PROJECT_ENV && source /www/server/panel/script/btpyprojectenv.sh ai-tavern-backend
source /www/server/python_project/vhost/env/ai-tavern-backend.env
```

确认 Python：

```bash
python --version
```

安装依赖：

```bash
pip install -U pip -i https://pypi.tuna.tsinghua.edu.cn/simple
pip install -r requirements-prod.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

检查依赖：

```bash
python -c "import uvicorn, fastapi, openai; print('backend deps ok')"
```

看到：

```text
backend deps ok
```

## 13. 打包前端

进入前端目录：

```bash
cd $FRONTEND_DIR
```

安装依赖：

```bash
npm install --registry=https://registry.npmmirror.com
```

打包：

```bash
NODE_OPTIONS="--max-old-space-size=4096" npm run build:prod
```

检查打包结果：

```bash
ls $FRONTEND_DIR/dist
```

应该能看到：

```text
index.html
static
```

## 14. 检查 Nginx 配置

执行：

```bash
nginx -t
```

正确结果：

```text
syntax is ok
test is successful
```

重载 Nginx：

```bash
systemctl reload nginx
```

## 15. 启动后端

打开宝塔面板：

```text
宝塔面板 -> Python 项目管理器 -> ai-tavern-backend -> 启动
```

回到宝塔终端检查：

```bash
ss -lntp | grep 9099
```

能看到 `9099` 代表后端已启动。

## 16. 检查后端接口

执行：

```bash
curl -I http://127.0.0.1:9099/docs
```

看到 `HTTP/1.1 200 OK` 代表后端可访问。

检查域名：

```bash
curl -I http://www.xn--kbrr2vyxjytebq4azkrrie.icu
```

看到 `HTTP/1.1 200 OK` 代表前端可访问。

## 17. 浏览器验证

打开：

```text
http://www.xn--kbrr2vyxjytebq4azkrrie.icu
```

登录后台后检查：

```text
1. 系统管理 -> 用户管理能打开。
2. 系统管理 -> 角色管理能打开。
3. 系统管理 -> 用户Token设置能打开。
4. AI 管理 -> AI 酒馆管理 -> 角色聊天能打开。
5. 手机宽度进入聊天详情后，顶部导航栏和标签栏隐藏。
6. 聊天标题固定在顶部。
7. 右下角加号能打开功能面板。
8. 提示词、摘要、强制记忆、编辑 AI 回复功能能打开。
9. 发送消息后 AI 能回复。
10. Token 消耗页面能看到记录。
```

## 18. 更新失败时看日志

查看宝塔 Python 项目日志：

```text
宝塔面板 -> Python 项目管理器 -> ai-tavern-backend -> 日志
```

终端查看后端日志：

```bash
cd $BACKEND_DIR
tail -n 100 logs/*.log
```

查看 Nginx 错误日志：

```bash
tail -n 100 /www/wwwlogs/www.xn--kbrr2vyxjytebq4azkrrie.icu.error.log
```

## 19. 常见错误处理

### 19.1 登录提示 502

执行：

```bash
ss -lntp | grep 9099
```

没有输出时，去宝塔 Python 项目管理器启动 `ai-tavern-backend`。

### 19.2 提示 `No module named uvicorn`

执行：

```bash
cd $BACKEND_DIR
unset _BT_PROJECT_ENV && source /www/server/panel/script/btpyprojectenv.sh ai-tavern-backend
source /www/server/python_project/vhost/env/ai-tavern-backend.env
pip install -r requirements-prod.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 19.3 提示 `cannot import name Literal`

宝塔 Python 项目管理器里把项目 Python 版本改成 3.11。

### 19.4 前端打包提示内存不足

执行：

```bash
cd $FRONTEND_DIR
NODE_OPTIONS="--max-old-space-size=4096" npm run build:prod
```

### 19.5 页面样式没变化

浏览器执行强制刷新：

```text
Ctrl + F5
```

服务器重载 Nginx：

```bash
nginx -t
systemctl reload nginx
```

## 20. 最短命令清单

熟悉流程后，更新第二版直接按下面执行。

```bash
export PROJECT_DIR=/www/wwwroot/ai-tavern
export BACKEND_DIR=/www/wwwroot/ai-tavern/ruoyi-fastapi-backend
export FRONTEND_DIR=/www/wwwroot/ai-tavern/ruoyi-fastapi-frontend
export BACKUP_DIR=/www/backup/ai-tavern
export DB_NAME=你的数据库名
export DB_USER=你的数据库用户

mkdir -p $BACKUP_DIR
cp $BACKEND_DIR/.env.prod $BACKUP_DIR/.env.prod.$(date +%F-%H%M%S).bak
mysqldump -u$DB_USER -p $DB_NAME > $BACKUP_DIR/$DB_NAME.$(date +%F-%H%M%S).sql

cd $PROJECT_DIR
git pull origin main

cd $BACKEND_DIR
mysql -u$DB_USER -p $DB_NAME < sql/update-v2-ai-tavern-chat.sql

unset _BT_PROJECT_ENV && source /www/server/panel/script/btpyprojectenv.sh ai-tavern-backend
source /www/server/python_project/vhost/env/ai-tavern-backend.env
pip install -r requirements-prod.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

cd $FRONTEND_DIR
npm install --registry=https://registry.npmmirror.com
NODE_OPTIONS="--max-old-space-size=4096" npm run build:prod

nginx -t
systemctl reload nginx
```

最后在宝塔 Python 项目管理器里重启：

```text
ai-tavern-backend
```
