# AI 酒馆项目宝塔 Python 项目管理器部署详细版

本文档适合：服务器刚重装系统，从 0 开始部署。

项目域名：

```text
www.xn--kbrr2vyxjytebq4azkrrie.icu
```

后端端口：

```text
9099
```

接口前缀：

```text
/prod-api
```

默认后台账号：

```text
账号：admin
密码：admin123
```

## 0. 本文档使用的版本

尽量按下面版本装。宝塔里如果只有小版本不同，例如 Nginx 1.24.0 和 1.24.1，这种一般没关系；大版本尽量一致。

| 工具 | 推荐版本 |
| --- | --- |
| 宝塔 Linux 面板 | 9.x |
| 系统 | OpenCloudOS 9.x / CentOS 9 系 |
| Nginx | 1.24.x |
| MySQL | 8.0.x |
| Redis | 7.2.x |
| Python | 3.11.6 或 3.11.x |
| Node.js | 20.x LTS |
| npm | 10.x |
| 项目前端 | vfadmin 1.9.0 |
| Vue | 3.5.26 |
| Vite | 6.4.1 |
| FastAPI | 0.128.2 |
| SQLAlchemy | 2.0.46 |
| OpenAI SDK | 2.17.0 |

重要：不要用 Python 3.7。这个项目必须用 Python 3.11。

## 1. 宝塔安装软件

打开宝塔面板，进入：

```text
软件商店
```

安装下面软件：

```text
Nginx 1.24.x
MySQL 8.0.x
Redis 7.2.x
Python 项目管理器
Node.js 版本管理器
```

如果宝塔软件商店里 Redis 只有 7.0.x，也可以先用；但推荐 7.2.x。

## 2. 安装 Node.js 20

宝塔面板进入：

```text
软件商店 -> Node.js 版本管理器
```

安装：

```text
Node.js 20.x LTS
```

安装后，打开宝塔终端检查：

```bash
node -v
npm -v
```

正确示例：

```text
v20.x.x
10.x.x
```

只要 `node -v` 是 `v20` 开头即可。

## 3. 确认 Python 3.11

打开宝塔终端，执行：

```bash
python3.11 --version
```

正确示例：

```text
Python 3.11.6
```

如果提示找不到 `python3.11`，去宝塔：

```text
软件商店 -> Python 项目管理器
```

安装 Python 3.11。

## 4. 创建项目目录

打开宝塔终端，执行：

```bash
mkdir -p /www/wwwroot/ai-tavern
```

然后把本地项目里的这两个文件夹上传到服务器：

```text
ruoyi-fastapi-backend
ruoyi-fastapi-frontend
```

上传后目录必须是：

```text
/www/wwwroot/ai-tavern/ruoyi-fastapi-backend
/www/wwwroot/ai-tavern/ruoyi-fastapi-frontend
```

检查目录：

```bash
ls /www/wwwroot/ai-tavern
ls /www/wwwroot/ai-tavern/ruoyi-fastapi-backend
ls /www/wwwroot/ai-tavern/ruoyi-fastapi-frontend
```

后端目录里必须能看到：

```text
app.py
requirements-prod.txt
.env.prod
sql
```

前端目录里必须能看到：

```text
package.json
src
.env.production
```

## 5. 创建 MySQL 数据库

宝塔面板进入：

```text
数据库 -> 添加数据库
```

填写：

```text
数据库名：ruoyi_fastapi
用户名：ruoyi_fastapi
密码：自己设置一个强密码
字符集：utf8mb4
```

注意：数据库名建议用 `ruoyi_fastapi`，不要用 `ruoyi-fastapi`。

创建完成后，记住：

```text
数据库名：ruoyi_fastapi
数据库用户：ruoyi_fastapi
数据库密码：你刚设置的密码
```

## 6. 导入数据库文件

宝塔面板进入：

```text
数据库 -> ruoyi_fastapi -> 管理
```

按顺序导入两个 SQL 文件。

第一个：

```text
/www/wwwroot/ai-tavern/ruoyi-fastapi-backend/sql/ruoyi-fastapi.sql
```

第二个：

```text
/www/wwwroot/ai-tavern/ruoyi-fastapi-backend/sql/ai-tavern.sql
```

顺序不能反。

导入完成后，数据库里应该能看到很多表，例如：

```text
sys_user
sys_role
sys_menu
ai_tavern_character
ai_tavern_session
ai_tavern_message
ai_tavern_token_usage
ai_tavern_user_token_quota
```

## 7. 修改后端 .env.prod

打开文件：

```text
/www/wwwroot/ai-tavern/ruoyi-fastapi-backend/.env.prod
```

建议直接检查并修改下面这些配置。

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
DB_USERNAME = 'ruoyi_fastapi'
DB_PASSWORD = '你的数据库密码'
DB_DATABASE = 'ruoyi_fastapi'
DB_ECHO = false

REDIS_HOST = '127.0.0.1'
REDIS_PORT = 6379
REDIS_USERNAME = ''
REDIS_PASSWORD = ''
REDIS_DATABASE = 2

DEEPSEEK_API_KEY = '你的 DeepSeek API Key'
DEEPSEEK_BASE_URL = 'https://api.deepseek.com'
DEEPSEEK_MODEL = 'deepseek-v4-flash'
DEEPSEEK_THINKING_ENABLED = false
DEEPSEEK_MAX_TOKENS = 2048
```

重点检查：

```text
DB_DATABASE 必须是 ruoyi_fastapi
DB_USERNAME 必须是 ruoyi_fastapi
DB_PASSWORD 必须是你宝塔数据库的密码
```

如果这里还是：

```text
DB_DATABASE = 'ruoyi-fastapi'
```

后端会报错：

```text
Unknown database 'ruoyi-fastapi'
```

## 8. 创建 Python 3.11 虚拟环境

打开宝塔终端，执行：

```bash
cd /www/wwwroot/ai-tavern/ruoyi-fastapi-backend
rm -rf venv *_venv
python3.11 -m venv venv
source venv/bin/activate
python --version
```

正确示例：

```text
Python 3.11.6
```

如果这里显示 Python 3.7，立刻停下来，说明环境错了。

## 9. 安装后端依赖

继续在后端目录执行：

```bash
cd /www/wwwroot/ai-tavern/ruoyi-fastapi-backend
source venv/bin/activate
pip install -U pip
pip install -r requirements-prod.txt -i https://mirrors.tencent.com/pypi/simple
```

如果腾讯源失败，换官方源：

```bash
pip install -r requirements-prod.txt -i https://pypi.org/simple
```

注意：必须装这个文件：

```text
requirements-prod.txt
```

不要装：

```text
requirements.txt
```

否则可能遇到 `mistralai==1.12.0` 安装失败。

## 10. 手动测试后端能否启动

先手动跑一次：

```bash
cd /www/wwwroot/ai-tavern/ruoyi-fastapi-backend
source venv/bin/activate
python app.py --env=prod
```

正确情况：

```text
后端一直运行
终端不会立刻回到命令行
没有 Traceback
没有 Application startup failed
```

错误情况：

```text
出现 Traceback
出现 Application startup failed
回到了命令行
```

如果手动启动成功，另开一个宝塔终端，执行：

```bash
ss -lntp | grep 9099
```

能看到 `9099` 就说明后端已经监听。

再测试验证码接口：

```bash
curl http://127.0.0.1:9099/captchaImage
```

正确结果里应该有：

```json
"captchaEnabled":false
```

测试完成后，回到运行后端的终端，按：

```text
Ctrl + C
```

把手动启动停掉。

## 11. 用宝塔 Python 项目管理器托管后端

宝塔面板进入：

```text
软件商店 -> Python 项目管理器 -> 添加项目
```

不同宝塔版本字段名字可能略有不同，按下面填。

### 11.1 基本信息

```text
项目名称：ai-tavern-backend
项目路径：/www/wwwroot/ai-tavern/ruoyi-fastapi-backend
运行目录：/www/wwwroot/ai-tavern/ruoyi-fastapi-backend
项目端口：9099
```

如果有“框架”选项：

```text
框架：其他 / Python / 自定义
```

不要选择 Django。

### 11.2 Python 版本

选择：

```text
Python 3.11.x
```

如果可以填写 Python 解释器路径，填这个：

```text
/www/wwwroot/ai-tavern/ruoyi-fastapi-backend/venv/bin/python
```

这个路径最重要。不要用宝塔自动创建的 Python 3.7 环境。

### 11.3 启动方式

如果面板有“启动命令”，直接填：

```bash
/www/wwwroot/ai-tavern/ruoyi-fastapi-backend/venv/bin/python /www/wwwroot/ai-tavern/ruoyi-fastapi-backend/app.py --env=prod
```

如果面板是分开填写“启动文件”和“启动参数”，这样填：

```text
启动文件：/www/wwwroot/ai-tavern/ruoyi-fastapi-backend/app.py
启动参数：--env=prod
```

如果面板有“模块名 / WSGI / ASGI”之类字段，不用填，或者保持默认。

### 11.4 依赖安装

如果 Python 项目管理器问是否自动安装依赖：

```text
不勾选自动安装
```

原因：我们已经在第 9 步手动安装好了 `requirements-prod.txt`。

如果必须填写依赖文件，填：

```text
/www/wwwroot/ai-tavern/ruoyi-fastapi-backend/requirements-prod.txt
```

不要填 `requirements.txt`。

### 11.5 启动项目

点击：

```text
保存
启动
```

启动后，在宝塔终端执行：

```bash
ss -lntp | grep 9099
```

有输出就是成功。

也可以测试：

```bash
curl http://127.0.0.1:9099/captchaImage
```

正确结果里应该有：

```json
"captchaEnabled":false
```

## 12. Python 项目管理器常见错误

### 12.1 can't open file 'app.py'

错误类似：

```text
can't open file 'app.py': [Errno 2] No such file or directory
```

原因：

```text
运行目录错了
启动文件路径错了
```

改成：

```text
运行目录：/www/wwwroot/ai-tavern/ruoyi-fastapi-backend
启动文件：/www/wwwroot/ai-tavern/ruoyi-fastapi-backend/app.py
```

或者直接用完整启动命令：

```bash
/www/wwwroot/ai-tavern/ruoyi-fastapi-backend/venv/bin/python /www/wwwroot/ai-tavern/ruoyi-fastapi-backend/app.py --env=prod
```

### 12.2 cannot import name 'Literal'

错误类似：

```text
ImportError: cannot import name 'Literal' from 'typing'
```

原因：

```text
用了 Python 3.7
```

解决：

```text
Python 解释器路径必须是：
/www/wwwroot/ai-tavern/ruoyi-fastapi-backend/venv/bin/python
```

并且执行：

```bash
/www/wwwroot/ai-tavern/ruoyi-fastapi-backend/venv/bin/python --version
```

必须显示：

```text
Python 3.11.x
```

### 12.3 Unknown database

错误类似：

```text
Unknown database 'ruoyi-fastapi'
```

原因：

```text
.env.prod 里的 DB_DATABASE 写错了
```

打开：

```text
/www/wwwroot/ai-tavern/ruoyi-fastapi-backend/.env.prod
```

改成：

```env
DB_DATABASE = 'ruoyi_fastapi'
```

### 12.4 No module named uvicorn

错误类似：

```text
ModuleNotFoundError: No module named 'uvicorn'
```

原因：

```text
依赖没装到当前 venv 里
```

解决：

```bash
cd /www/wwwroot/ai-tavern/ruoyi-fastapi-backend
source venv/bin/activate
pip install -r requirements-prod.txt -i https://mirrors.tencent.com/pypi/simple
```

## 13. 打包前端

打开宝塔终端：

```bash
cd /www/wwwroot/ai-tavern/ruoyi-fastapi-frontend
npm install --registry=https://registry.npmmirror.com
NODE_OPTIONS="--max-old-space-size=4096" npm run build:prod
```

正确结果：

```text
vite build 成功
生成 dist 目录
```

检查：

```bash
ls /www/wwwroot/ai-tavern/ruoyi-fastapi-frontend/dist
```

应该能看到：

```text
index.html
static
```

如果打包报内存不足：

```text
JavaScript heap out of memory
```

执行：

```bash
dd if=/dev/zero of=/swapfile bs=1M count=4096
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile
NODE_OPTIONS="--max-old-space-size=4096" npm run build:prod
```

## 14. 宝塔创建网站

宝塔面板进入：

```text
网站 -> 添加站点
```

填写：

```text
域名：www.xn--kbrr2vyxjytebq4azkrrie.icu
根目录：/www/wwwroot/ai-tavern/ruoyi-fastapi-frontend/dist
PHP版本：纯静态
数据库：不创建
SSL：暂时不启用
```

保存。

## 15. 配置 Nginx

宝塔面板进入：

```text
网站 -> www.xn--kbrr2vyxjytebq4azkrrie.icu -> 设置 -> 配置文件
```

把原来的内容备份一下，然后覆盖成下面这一份：

```nginx
server {
    listen 80;
    listen [::]:80;
    server_name www.xn--kbrr2vyxjytebq4azkrrie.icu;

    index index.html index.htm default.html default.htm;
    root /www/wwwroot/ai-tavern/ruoyi-fastapi-frontend/dist;

    include /www/server/panel/vhost/nginx/well-known/www.xn--kbrr2vyxjytebq4azkrrie.icu.conf;
    include /www/server/panel/vhost/nginx/extension/www.xn--kbrr2vyxjytebq4azkrrie.icu/*.conf;

    error_page 404 /404.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /prod-api/ {
        proxy_pass http://127.0.0.1:9099/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
    }

    location ~ ^/(\.user.ini|\.htaccess|\.git|\.env|\.svn|\.project|LICENSE|README.md) {
        return 404;
    }

    location ~ \.well-known {
        allow all;
    }

    if ($uri ~ "^/\.well-known/.*\.(php|jsp|py|js|css|lua|ts|go|zip|tar\.gz|rar|7z|sql|bak)$") {
        return 403;
    }

    location ~ .*\.(gif|jpg|jpeg|png|bmp|swf)$ {
        expires 30d;
        error_log /dev/null;
        access_log /dev/null;
    }

    location ~ .*\.(js|css)?$ {
        expires 12h;
        error_log /dev/null;
        access_log /dev/null;
    }

    access_log /www/wwwlogs/www.xn--kbrr2vyxjytebq4azkrrie.icu.log;
    error_log /www/wwwlogs/www.xn--kbrr2vyxjytebq4azkrrie.icu.error.log;
}
```

保存后，在宝塔终端执行：

```bash
nginx -t
systemctl reload nginx
```

正确结果：

```text
syntax is ok
test is successful
```

## 16. 访问网站

浏览器打开：

```text
http://www.xn--kbrr2vyxjytebq4azkrrie.icu
```

登录：

```text
账号：admin
密码：admin123
```

当前代码已经取消验证码，所以登录页不应该出现验证码输入框。

## 17. 最终检查命令

检查后端端口：

```bash
ss -lntp | grep 9099
```

检查 Redis：

```bash
redis-cli ping
```

正确结果：

```text
PONG
```

检查后端接口：

```bash
curl http://127.0.0.1:9099/captchaImage
```

检查网站接口代理：

```bash
curl http://www.xn--kbrr2vyxjytebq4azkrrie.icu/prod-api/captchaImage
```

两个返回里都应该有：

```json
"captchaEnabled":false
```

## 18. 502 接口异常怎么查

如果前端提示：

```text
502 接口异常
```

第一步检查后端：

```bash
ss -lntp | grep 9099
```

没有输出，说明后端没启动。

第二步看 Python 项目管理器日志：

```text
宝塔 -> Python 项目管理器 -> ai-tavern-backend -> 日志
```

第三步检查 Nginx：

```bash
nginx -t
systemctl reload nginx
```

第四步检查反向代理是否写对：

```nginx
location /prod-api/ {
    proxy_pass http://127.0.0.1:9099/;
}
```

注意：`proxy_pass` 最后这个 `/` 不要删。

## 19. 更新代码后的重新部署

以后本地改完代码，重新上传服务器后，按下面步骤更新。

后端更新：

```bash
cd /www/wwwroot/ai-tavern/ruoyi-fastapi-backend
source venv/bin/activate
pip install -r requirements-prod.txt -i https://mirrors.tencent.com/pypi/simple
```

然后在宝塔 Python 项目管理器里重启：

```text
ai-tavern-backend -> 重启
```

前端更新：

```bash
cd /www/wwwroot/ai-tavern/ruoyi-fastapi-frontend
npm install --registry=https://registry.npmmirror.com
NODE_OPTIONS="--max-old-space-size=4096" npm run build:prod
```

然后：

```bash
systemctl reload nginx
```

浏览器强制刷新：

```text
Ctrl + F5
```
