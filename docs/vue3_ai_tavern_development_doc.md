# AI 酒馆角色聊天应用开发文档

版本：v0.4  
基础框架：RuoYi-Vue3-FastAPI-master  
数据库：MySQL  
数据库名：`ceshi`  
数据库用户名：`ceshi`  
数据库密码：`123456`  
初版核心目标：**对话存储 + 长文本对话摘要记忆**  
摘要规则：**每 20 轮用户对话自动总结一次**  
AI 模型：DeepSeek `deepseek-v4-flash`，默认思考模式  
后续扩展：阿里云声音复刻、语音合成、向量记忆检索

---

## 1. 项目目标

本项目要基于 `RuoYi-Vue3-FastAPI-master` 开发一个类似“酒馆角色 / Tavern / SillyTavern”的 AI 角色扮演聊天系统。

初版先不要做太复杂，只完成最重要的闭环：

```text
用户登录
    ↓
创建 AI 角色
    ↓
创建会话
    ↓
发送消息
    ↓
DeepSeek 生成 AI 回复
    ↓
服务器保存完整对话
    ↓
每 20 轮对话生成一次长期摘要
    ↓
下次对话时带上摘要，减少角色失忆
```

初版必须做到：

```text
1. 用户对话永久保存在 MySQL。
2. 每条 user 和 assistant 消息都保存。
3. AI 请求 token 消耗保存到数据库。
4. 每 20 轮用户消息更新一次会话摘要。
5. 下次请求 DeepSeek 时拼接：角色设定 + 长期摘要 + 最近消息 + 用户新消息。
6. 管理员后台可以查看用户、角色、会话、消息、token 消耗。
```

后续版本再做：

```text
AI 语音复刻
语音朗读
向量记忆检索
角色市场
世界书
安卓端优化
```

---

## 2. 技术栈

### 2.1 基础框架

使用：

```text
RuoYi-Vue3-FastAPI-master
```

项目大体结构：

```text
RuoYi-Vue3-FastAPI-master/
  ruoyi-fastapi-backend/     FastAPI 后端
  ruoyi-fastapi-frontend/    Vue3 + Element Plus 管理后台
  ruoyi-fastapi-app/         uni-app + Vue3 用户端 / H5 / 安卓
```

本项目不再使用 Node.js + Fastify + Prisma。  
后端业务全部在 `ruoyi-fastapi-backend` 中扩展。

---

### 2.2 后端技术栈

```text
Python
FastAPI
SQLAlchemy
MySQL
Redis
OAuth2 + JWT
RuoYi 权限系统
DeepSeek API
```

---

### 2.3 管理后台技术栈

```text
Vue3
Vite
Element Plus
RuoYi 动态菜单
RuoYi 按钮权限
Axios
```

管理后台使用：

```text
ruoyi-fastapi-frontend
```

---

### 2.4 用户端技术栈

```text
uni-app
Vue3
Vite
Tailwind CSS
```

用户聊天端使用：

```text
ruoyi-fastapi-app
```

后期安卓端从 `ruoyi-fastapi-app` 打包。

---

## 3. MySQL 数据库配置

### 3.1 数据库信息

你指定的数据库配置如下：

```text
数据库类型：MySQL
数据库名：ceshi
用户名：ceshi
密码：123456
端口：3306
字符集：utf8mb4
排序规则：utf8mb4_general_ci
```

注意：`123456` 密码只建议用于本地开发或测试环境。正式上线时必须换成强密码。

---

## 4. 本地 MySQL 创建数据库

在 MySQL 中执行：

```sql
CREATE DATABASE IF NOT EXISTS ceshi
  DEFAULT CHARACTER SET utf8mb4
  COLLATE utf8mb4_general_ci;

CREATE USER IF NOT EXISTS 'ceshi'@'%' IDENTIFIED BY '123456';

GRANT ALL PRIVILEGES ON ceshi.* TO 'ceshi'@'%';

FLUSH PRIVILEGES;
```

如果你只允许本机连接，可以再创建本机用户：

```sql
CREATE USER IF NOT EXISTS 'ceshi'@'localhost' IDENTIFIED BY '123456';

GRANT ALL PRIVILEGES ON ceshi.* TO 'ceshi'@'localhost';

FLUSH PRIVILEGES;
```

测试登录：

```bash
mysql -h 127.0.0.1 -P 3306 -u ceshi -p
```

输入密码：

```text
123456
```

进入后测试：

```sql
USE ceshi;
SHOW TABLES;
```

---

## 5. 修改 RuoYi 后端数据库配置

进入后端目录：

```bash
cd RuoYi-Vue3-FastAPI-master/ruoyi-fastapi-backend
```

修改：

```text
.env.dev
```

把数据库部分改成：

```env
# -------- 数据库配置 --------
DB_TYPE = 'mysql'
DB_HOST = '127.0.0.1'
DB_PORT = 3306
DB_USERNAME = 'ceshi'
DB_PASSWORD = 'replace-with-database-password'
DB_DATABASE = 'ceshi'

DB_ECHO = true
DB_MAX_OVERFLOW = 10
DB_POOL_SIZE = 50
DB_POOL_RECYCLE = 3600
DB_POOL_TIMEOUT = 30
```

如果你的后端也在 Docker 容器内运行，并且 MySQL 服务名叫 `ruoyi-mysql`，则应改成：

```env
DB_HOST = 'ruoyi-mysql'
DB_PORT = 3306
DB_USERNAME = 'ceshi'
DB_PASSWORD = 'replace-with-database-password'
DB_DATABASE = 'ceshi'
```

---

## 6. 修改 Docker Compose MySQL 配置

如果你用 Docker Compose 启动 MySQL，修改项目根目录：

```text
docker-compose.my.yml
```

找到 MySQL 服务，改成类似：

```yaml
ruoyi-mysql:
  image: mysql:8.0
  container_name: ruoyi-mysql
  environment:
    MYSQL_ROOT_PASSWORD: root
    MYSQL_DATABASE: ceshi
    MYSQL_USER: ceshi
    MYSQL_PASSWORD: "123456"
  ports:
    - "13306:3306"
  volumes:
    - ./mysql-data:/var/lib/mysql
    - ./ruoyi-fastapi-backend/sql/ruoyi-fastapi.sql:/docker-entrypoint-initdb.d/01-ruoyi-fastapi.sql
    - ./ruoyi-fastapi-backend/sql/ai-tavern.sql:/docker-entrypoint-initdb.d/02-ai-tavern.sql
  command: --character-set-server=utf8mb4 --collation-server=utf8mb4_general_ci --skip-character-set-client-handshake=1
```

然后后端 `.env.dev` 里如果在宿主机运行，MySQL 端口是 `13306`：

```env
DB_HOST = '127.0.0.1'
DB_PORT = 13306
DB_USERNAME = 'ceshi'
DB_PASSWORD = 'replace-with-database-password'
DB_DATABASE = 'ceshi'
```

如果后端也在 Docker 网络里运行，MySQL 端口是容器内部端口 `3306`：

```env
DB_HOST = 'ruoyi-mysql'
DB_PORT = 3306
DB_USERNAME = 'ceshi'
DB_PASSWORD = 'replace-with-database-password'
DB_DATABASE = 'ceshi'
```

启动：

```bash
docker compose -f docker-compose.my.yml up -d --build
```

---

## 7. 导入 RuoYi 原始 SQL

RuoYi 原始系统表必须先导入，例如：

```text
ruoyi-fastapi-backend/sql/ruoyi-fastapi.sql
```

如果本地 MySQL：

```bash
mysql -h 127.0.0.1 -P 3306 -u ceshi -p ceshi < ruoyi-fastapi-backend/sql/ruoyi-fastapi.sql
```

如果 Docker 暴露端口是 `13306`：

```bash
mysql -h 127.0.0.1 -P 13306 -u ceshi -p ceshi < ruoyi-fastapi-backend/sql/ruoyi-fastapi.sql
```

导入后检查：

```sql
USE ceshi;
SHOW TABLES;
```

应该能看到 RuoYi 自带的系统表，例如用户、角色、菜单、日志等表。

---

## 8. 新增 AI 酒馆业务模块

后端新增模块：

```text
ruoyi-fastapi-backend/module_ai_tavern/
  controller/
    character_controller.py
    conversation_controller.py
    chat_controller.py
    message_controller.py
    token_usage_controller.py
  service/
    character_service.py
    conversation_service.py
    chat_service.py
    message_service.py
    summary_service.py
    token_usage_service.py
  dao/
    character_dao.py
    conversation_dao.py
    message_dao.py
    token_usage_dao.py
  entity/
    ai_character.py
    ai_conversation.py
    ai_message.py
    ai_token_usage.py
  schema/
    character_schema.py
    conversation_schema.py
    chat_schema.py
    message_schema.py
    token_usage_schema.py
  prompt/
    character_prompt.py
    summary_prompt.py
  provider/
    deepseek_provider.py
  utils/
    token_counter.py
```

模块作用：

```text
controller：接口入口
service：业务逻辑
dao：数据库查询
entity：SQLAlchemy 表模型
schema：Pydantic 请求和返回模型
prompt：提示词模板
provider：第三方 AI 模型适配
```

---

## 9. AI 酒馆业务表设计

新建 SQL 文件：

```text
ruoyi-fastapi-backend/sql/ai-tavern.sql
```

内容如下。

---

### 9.1 角色表 ai_character

```sql
CREATE TABLE IF NOT EXISTS ai_character (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  user_id BIGINT NOT NULL COMMENT '用户ID',
  name VARCHAR(100) NOT NULL COMMENT '角色名称',
  avatar_url TEXT COMMENT '角色头像',
  description TEXT COMMENT '角色描述',
  personality TEXT COMMENT '性格设定',
  scenario TEXT COMMENT '当前场景',
  first_message TEXT COMMENT '开场白',
  system_prompt TEXT COMMENT '系统提示词',
  example_dialogues TEXT COMMENT '示例对话',
  voice_profile_id BIGINT NULL COMMENT '默认音色ID，后续语音功能使用',
  status CHAR(1) DEFAULT '0' COMMENT '状态：0正常，1禁用',
  create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
  update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  remark TEXT,
  INDEX idx_ai_character_user_id (user_id),
  INDEX idx_ai_character_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='AI角色表';
```

---

### 9.2 会话表 ai_conversation

```sql
CREATE TABLE IF NOT EXISTS ai_conversation (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  user_id BIGINT NOT NULL COMMENT '用户ID',
  character_id BIGINT NOT NULL COMMENT '角色ID',
  title VARCHAR(200) COMMENT '会话标题',

  summary LONGTEXT COMMENT '长期剧情摘要',
  summary_version INT DEFAULT 0 COMMENT '摘要版本',
  summary_turn_count INT DEFAULT 0 COMMENT '距离上次摘要后新增的用户轮数',
  last_summarized_message_id BIGINT NULL COMMENT '最后一次摘要到哪条消息',
  last_summary_time DATETIME NULL COMMENT '最后摘要时间',
  summary_status VARCHAR(20) DEFAULT 'idle' COMMENT 'idle/pending/running/failed',

  total_turn_count INT DEFAULT 0 COMMENT '总用户轮数',
  total_message_count INT DEFAULT 0 COMMENT '总消息数',

  status CHAR(1) DEFAULT '0' COMMENT '状态：0正常，1删除/禁用',
  create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
  update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  INDEX idx_ai_conversation_user_id (user_id),
  INDEX idx_ai_conversation_character_id (character_id),
  INDEX idx_ai_conversation_update_time (update_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='AI会话表';
```

说明：

```text
summary：长期摘要
summary_turn_count：上次摘要后新增多少轮用户消息
total_turn_count：整个会话累计多少轮用户消息
last_summarized_message_id：摘要已处理到哪条消息
```

---

### 9.3 消息表 ai_message

```sql
CREATE TABLE IF NOT EXISTS ai_message (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  conversation_id BIGINT NOT NULL COMMENT '会话ID',
  user_id BIGINT NOT NULL COMMENT '用户ID',
  character_id BIGINT NULL COMMENT '角色ID',

  role VARCHAR(20) NOT NULL COMMENT 'user/assistant/system',
  content LONGTEXT NOT NULL COMMENT '消息内容',
  seq_no INT NOT NULL DEFAULT 0 COMMENT '会话内消息序号',

  prompt_tokens INT DEFAULT 0 COMMENT '输入token',
  completion_tokens INT DEFAULT 0 COMMENT '输出token',
  total_tokens INT DEFAULT 0 COMMENT '总token',

  audio_url TEXT COMMENT '后续语音音频地址',
  audio_status VARCHAR(20) DEFAULT 'none' COMMENT 'none/pending/ready/failed',
  voice_profile_id BIGINT NULL COMMENT '音色ID',

  create_time DATETIME DEFAULT CURRENT_TIMESTAMP,

  INDEX idx_ai_message_conversation_id (conversation_id),
  INDEX idx_ai_message_user_id (user_id),
  INDEX idx_ai_message_character_id (character_id),
  INDEX idx_ai_message_role (role),
  INDEX idx_ai_message_seq_no (conversation_id, seq_no),
  INDEX idx_ai_message_create_time (create_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='AI消息表';
```

注意：

```text
content 使用 LONGTEXT，避免长对话或长回复被截断。
普通聊天只保存 user 和 assistant。
不要把 DeepSeek 的 reasoning_content 保存给用户展示。
```

---

### 9.4 Token 消耗表 ai_token_usage

```sql
CREATE TABLE IF NOT EXISTS ai_token_usage (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  user_id BIGINT NOT NULL COMMENT '用户ID',
  conversation_id BIGINT NULL COMMENT '会话ID',
  character_id BIGINT NULL COMMENT '角色ID',
  message_id BIGINT NULL COMMENT '消息ID',

  provider VARCHAR(50) DEFAULT 'deepseek' COMMENT '供应商',
  model VARCHAR(100) NOT NULL COMMENT '模型名',

  prompt_tokens INT DEFAULT 0 COMMENT '输入token',
  completion_tokens INT DEFAULT 0 COMMENT '输出token',
  total_tokens INT DEFAULT 0 COMMENT '总token',
  reasoning_tokens INT NULL COMMENT '思考token，如接口返回则记录',
  cached_tokens INT NULL COMMENT '缓存命中token，如接口返回则记录',

  request_type VARCHAR(50) DEFAULT 'chat' COMMENT 'chat/summary/voice等',
  request_id VARCHAR(100) NULL COMMENT '第三方请求ID',
  latency_ms INT NULL COMMENT '耗时毫秒',
  success TINYINT(1) DEFAULT 1 COMMENT '是否成功',
  error_message TEXT COMMENT '错误信息',

  create_time DATETIME DEFAULT CURRENT_TIMESTAMP,

  INDEX idx_ai_token_usage_user_id (user_id),
  INDEX idx_ai_token_usage_conversation_id (conversation_id),
  INDEX idx_ai_token_usage_model (model),
  INDEX idx_ai_token_usage_request_type (request_type),
  INDEX idx_ai_token_usage_create_time (create_time),
  INDEX idx_ai_token_usage_success (success)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='AI Token消耗表';
```

用途：

```text
管理员后台统计每个用户消耗多少 token。
统计每日 token。
统计失败请求。
后期可做用户额度、充值、限流。
```

---

### 9.5 摘要日志表 ai_summary_log

建议新增摘要日志表，方便排查摘要是否正常。

```sql
CREATE TABLE IF NOT EXISTS ai_summary_log (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  user_id BIGINT NOT NULL,
  conversation_id BIGINT NOT NULL,
  character_id BIGINT NULL,

  old_summary LONGTEXT COMMENT '旧摘要',
  new_summary LONGTEXT COMMENT '新摘要',
  start_message_id BIGINT NULL COMMENT '本次摘要起始消息ID',
  end_message_id BIGINT NULL COMMENT '本次摘要结束消息ID',
  message_count INT DEFAULT 0 COMMENT '本次摘要消息数量',

  model VARCHAR(100) DEFAULT 'deepseek-v4-flash',
  prompt_tokens INT DEFAULT 0,
  completion_tokens INT DEFAULT 0,
  total_tokens INT DEFAULT 0,

  success TINYINT(1) DEFAULT 1,
  error_message TEXT,
  create_time DATETIME DEFAULT CURRENT_TIMESTAMP,

  INDEX idx_ai_summary_log_conversation_id (conversation_id),
  INDEX idx_ai_summary_log_user_id (user_id),
  INDEX idx_ai_summary_log_create_time (create_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='AI摘要日志表';
```

---

## 10. 导入 AI 酒馆业务表

保存 SQL 后执行：

```bash
mysql -h 127.0.0.1 -P 3306 -u ceshi -p ceshi < ruoyi-fastapi-backend/sql/ai-tavern.sql
```

Docker 端口是 `13306` 时：

```bash
mysql -h 127.0.0.1 -P 13306 -u ceshi -p ceshi < ruoyi-fastapi-backend/sql/ai-tavern.sql
```

检查：

```sql
USE ceshi;

SHOW TABLES LIKE 'ai_%';

DESC ai_character;
DESC ai_conversation;
DESC ai_message;
DESC ai_token_usage;
DESC ai_summary_log;
```

---

## 11. DeepSeek 配置

后端 `.env.dev` 增加：

```env
# -------- DeepSeek 配置 --------
DEEPSEEK_API_KEY = '你的DeepSeek_API_Key'
DEEPSEEK_BASE_URL = 'https://api.deepseek.com'
DEEPSEEK_MODEL = 'deepseek-v4-flash'
DEEPSEEK_THINKING_ENABLED = true
DEEPSEEK_REASONING_EFFORT = 'high'
DEEPSEEK_MAX_TOKENS = 2048

# -------- AI 酒馆配置 --------
AI_SUMMARY_EVERY_N_TURNS = 20
AI_RECENT_MESSAGE_LIMIT = 60
AI_ENABLE_SUMMARY = true
```

说明：

```text
AI_SUMMARY_EVERY_N_TURNS = 20 表示每 20 轮用户消息总结一次。
AI_RECENT_MESSAGE_LIMIT = 60 表示每次发给模型的最近消息最多取 60 条。
```

---

## 12. DeepSeek Provider 示例

文件：

```text
module_ai_tavern/provider/deepseek_provider.py
```

示例：

```python
import time
from openai import AsyncOpenAI

from config.env import settings


client = AsyncOpenAI(
    api_key=settings.DEEPSEEK_API_KEY,
    base_url=settings.DEEPSEEK_BASE_URL,
)


async def chat_with_deepseek(
    messages: list[dict],
    user_id: str,
    request_type: str = "chat",
):
    started_at = time.time()

    response = await client.chat.completions.create(
        model=settings.DEEPSEEK_MODEL,
        messages=messages,
        max_tokens=settings.DEEPSEEK_MAX_TOKENS,
        reasoning_effort=settings.DEEPSEEK_REASONING_EFFORT,
        extra_body={
            "thinking": {"type": "enabled"},
            "user_id": user_id,
        },
    )

    latency_ms = int((time.time() - started_at) * 1000)
    choice = response.choices[0]
    message = choice.message

    return {
        "content": message.content or "",
        "reasoning_content": getattr(message, "reasoning_content", None),
        "usage": response.usage,
        "latency_ms": latency_ms,
        "model": settings.DEEPSEEK_MODEL,
        "request_type": request_type,
    }
```

注意：

```text
普通聊天页面只展示 content。
reasoning_content 不展示给用户。
```

---

## 13. 角色 Prompt 模板

文件：

```text
module_ai_tavern/prompt/character_prompt.py
```

内容：

```python
def build_character_system_prompt(character) -> str:
    return f"""
你正在扮演一个虚拟角色。

【角色名称】
{character.name}

【角色设定】
{character.description or ""}

【性格】
{character.personality or ""}

【当前场景】
{character.scenario or ""}

【补充设定】
{character.system_prompt or ""}

【扮演规则】
1. 始终保持角色身份。
2. 不要说自己是 AI、模型、程序。
3. 不要跳出剧情解释系统规则。
4. 回复要自然，像真人聊天，不要写成说明文。
5. 你需要参考长期剧情摘要，保持关系和剧情连续。
6. 如果用户提到过去发生的事，优先根据摘要和最近消息回应。
""".strip()
```

---

## 14. 长文本对话摘要机制

### 14.1 摘要目标

长文本对话不能每次把所有历史都发给 DeepSeek。  
初版采用“信息摘要”方案。

规则：

```text
每 20 轮用户消息，生成一次新的长期摘要。
```

这里的“一轮”定义为：

```text
用户发送 1 条消息，并收到 AI 的 1 条回复 = 1 轮
```

因此：

```text
20 轮 ≈ 20 条 user 消息 + 20 条 assistant 消息
```

---

### 14.2 每次请求 DeepSeek 的上下文组成

每次用户发送消息时，后端拼接：

```text
1. 角色设定 system prompt
2. 当前会话长期摘要 summary
3. 最近 60 条消息
4. 用户最新输入
```

不要每次发送完整历史。

---

### 14.3 摘要更新逻辑

`ai_conversation.summary_turn_count` 用于记录距离上次摘要后新增了多少轮。

流程：

```text
用户发送消息
    ↓
保存 user 消息
    ↓
DeepSeek 回复
    ↓
保存 assistant 消息
    ↓
conversation.summary_turn_count + 1
    ↓
如果 summary_turn_count >= 20
        触发摘要更新
        更新 conversation.summary
        summary_version + 1
        summary_turn_count = 0
        last_summarized_message_id = 本次处理到的最后消息ID
```

---

### 14.4 摘要 Prompt

文件：

```text
module_ai_tavern/prompt/summary_prompt.py
```

内容：

```python
def build_summary_prompt(old_summary: str, new_messages_text: str) -> list[dict]:
    system_prompt = """
你是一个角色扮演聊天应用的长期记忆整理器。

你的任务是把旧摘要和新增聊天记录合并成新的长期摘要。

必须保留：
1. 用户的重要偏好。
2. 角色和用户的关系变化。
3. 已经发生的重要剧情。
4. 角色或用户做出的承诺、约定、未完成事件。
5. 重要地点、人物、组织、世界观设定。
6. 用户明确要求记住的信息。

必须删除：
1. 普通寒暄。
2. 临时情绪。
3. 重复内容。
4. 对后续剧情没有影响的细节。

输出要求：
1. 使用中文。
2. 分条写。
3. 不要超过 1000 字。
4. 不要编造聊天记录里没有的信息。
""".strip()

    user_prompt = f"""
【旧摘要】
{old_summary or "暂无"}

【新增聊天记录】
{new_messages_text}

请输出合并后的新长期摘要。
""".strip()

    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]
```

---

### 14.5 摘要示例

旧摘要：

```text
用户与扶摇在雨夜小酒馆相识。扶摇性格克制但关心用户。
```

新增聊天：

```text
用户：你还记得我怕黑吗？
扶摇：记得。以后夜路我陪你走。
用户：那你明天陪我去海边？
扶摇：好，明日黄昏，我在城门口等你。
```

新摘要：

```text
1. 用户怕黑，扶摇知道这一点，并承诺以后夜路陪用户走。
2. 用户与扶摇约定明日黄昏去海边，见面地点是城门口。
3. 扶摇对用户的态度比初见时更亲近，表现出保护和陪伴意愿。
```

---

## 15. 上下文拼接实现

文件：

```text
module_ai_tavern/service/chat_context_service.py
```

伪代码：

```python
from module_ai_tavern.prompt.character_prompt import build_character_system_prompt


async def build_chat_messages(conversation_id: int, user_input: str):
    conversation = await conversation_service.get_by_id(conversation_id)
    character = await character_service.get_by_id(conversation.character_id)

    recent_messages = await message_service.get_recent_messages(
        conversation_id=conversation_id,
        limit=60,
    )

    messages = []

    messages.append({
        "role": "system",
        "content": build_character_system_prompt(character),
    })

    if conversation.summary:
        messages.append({
            "role": "system",
            "content": f"【长期剧情摘要】\n{conversation.summary}",
        })

    for item in recent_messages:
        messages.append({
            "role": item.role,
            "content": item.content,
        })

    messages.append({
        "role": "user",
        "content": user_input,
    })

    return messages
```

---

## 16. 聊天发送完整流程

接口：

```text
POST /ai/chat/send
```

请求：

```json
{
  "conversationId": 1001,
  "content": "你还记得我们昨天说好的事情吗？"
}
```

返回：

```json
{
  "message": {
    "id": 2002,
    "conversationId": 1001,
    "role": "assistant",
    "content": "当然记得，我答应过你，明日黄昏陪你去海边。",
    "audioStatus": "none"
  },
  "summaryTriggered": false
}
```

业务流程：

```text
1. 校验用户登录。
2. 校验 conversationId 是否属于当前用户。
3. 保存 user 消息到 ai_message。
4. 构建 DeepSeek messages。
5. 调用 DeepSeek。
6. 保存 assistant 回复到 ai_message。
7. 保存 ai_token_usage。
8. 更新 ai_conversation.total_turn_count。
9. 更新 ai_conversation.summary_turn_count。
10. 如果 summary_turn_count >= 20，触发摘要更新。
11. 返回 assistant 消息。
```

---

## 17. chat_service.py 伪代码

```python
async def send_chat(user_id: int, conversation_id: int, content: str):
    conversation = await conversation_service.get_user_conversation(
        user_id=user_id,
        conversation_id=conversation_id,
    )

    if not conversation:
        raise Exception("会话不存在或无权限访问")

    character = await character_service.get_by_id(conversation.character_id)

    # 1. 保存用户消息
    user_message = await message_service.create_message(
        conversation_id=conversation_id,
        user_id=user_id,
        character_id=character.id,
        role="user",
        content=content,
    )

    # 2. 构建上下文
    messages = await chat_context_service.build_chat_messages(
        conversation_id=conversation_id,
        user_input=content,
    )

    # 3. 调用 DeepSeek
    try:
        result = await deepseek_provider.chat_with_deepseek(
            messages=messages,
            user_id=str(user_id),
            request_type="chat",
        )

        # 4. 保存 AI 回复
        assistant_message = await message_service.create_message(
            conversation_id=conversation_id,
            user_id=user_id,
            character_id=character.id,
            role="assistant",
            content=result["content"],
        )

        # 5. 保存 token 消耗
        await token_usage_service.record_success(
            user_id=user_id,
            conversation_id=conversation_id,
            character_id=character.id,
            message_id=assistant_message.id,
            model=result["model"],
            usage=result["usage"],
            latency_ms=result["latency_ms"],
            request_type="chat",
        )

    except Exception as e:
        await token_usage_service.record_failed(
            user_id=user_id,
            conversation_id=conversation_id,
            character_id=character.id,
            model="deepseek-v4-flash",
            error_message=str(e),
            request_type="chat",
        )
        raise

    # 6. 更新会话计数
    await conversation_service.increase_turn_count(conversation_id)

    # 7. 每 20 轮触发摘要
    summary_triggered = False
    conversation = await conversation_service.get_by_id(conversation_id)

    if conversation.summary_turn_count >= 20:
        summary_triggered = True
        await summary_service.update_conversation_summary(
            user_id=user_id,
            conversation_id=conversation_id,
        )

    return {
        "message": assistant_message,
        "summaryTriggered": summary_triggered,
    }
```

---

## 18. 摘要服务实现逻辑

文件：

```text
module_ai_tavern/service/summary_service.py
```

流程：

```text
1. 读取 conversation。
2. 找到 last_summarized_message_id 之后的消息。
3. 如果没有 last_summarized_message_id，则取本会话最早未摘要消息。
4. 拼成新增聊天记录文本。
5. 使用旧 summary + 新聊天记录，调用 DeepSeek 生成新 summary。
6. 更新 ai_conversation.summary。
7. 更新 summary_version。
8. 更新 last_summarized_message_id。
9. 重置 summary_turn_count = 0。
10. 写入 ai_summary_log。
11. 写入 ai_token_usage，request_type = summary。
```

伪代码：

```python
async def update_conversation_summary(user_id: int, conversation_id: int):
    conversation = await conversation_service.get_by_id(conversation_id)

    messages = await message_service.get_messages_after_id(
        conversation_id=conversation_id,
        after_id=conversation.last_summarized_message_id,
    )

    if not messages:
        return conversation.summary

    new_messages_text = format_messages_for_summary(messages)

    summary_messages = build_summary_prompt(
        old_summary=conversation.summary or "",
        new_messages_text=new_messages_text,
    )

    result = await deepseek_provider.chat_with_deepseek(
        messages=summary_messages,
        user_id=str(user_id),
        request_type="summary",
    )

    new_summary = result["content"]
    end_message_id = messages[-1].id

    await conversation_service.update_summary(
        conversation_id=conversation_id,
        summary=new_summary,
        last_summarized_message_id=end_message_id,
    )

    await summary_log_service.create_log(
        user_id=user_id,
        conversation_id=conversation_id,
        old_summary=conversation.summary,
        new_summary=new_summary,
        start_message_id=messages[0].id,
        end_message_id=end_message_id,
        message_count=len(messages),
        usage=result["usage"],
        success=True,
    )

    await token_usage_service.record_success(
        user_id=user_id,
        conversation_id=conversation_id,
        model=result["model"],
        usage=result["usage"],
        latency_ms=result["latency_ms"],
        request_type="summary",
    )

    return new_summary
```

---

## 19. 消息格式化为摘要输入

```python
def format_messages_for_summary(messages):
    lines = []

    for msg in messages:
        if msg.role == "user":
            speaker = "用户"
        elif msg.role == "assistant":
            speaker = "角色"
        else:
            speaker = msg.role

        lines.append(f"{speaker}：{msg.content}")

    return "\n".join(lines)
```

---

## 20. 初版接口清单

### 20.1 角色接口

```text
POST   /ai/characters
GET    /ai/characters
GET    /ai/characters/{id}
PUT    /ai/characters/{id}
DELETE /ai/characters/{id}
```

### 20.2 会话接口

```text
POST   /ai/conversations
GET    /ai/conversations
GET    /ai/conversations/{id}
DELETE /ai/conversations/{id}
```

### 20.3 消息接口

```text
GET /ai/conversations/{id}/messages
```

### 20.4 聊天接口

```text
POST /ai/chat/send
```

### 20.5 摘要接口

```text
POST /ai/conversations/{id}/summary/rebuild
GET  /ai/conversations/{id}/summary
```

### 20.6 管理后台接口

```text
GET /admin/ai/dashboard
GET /admin/ai/characters
GET /admin/ai/conversations
GET /admin/ai/conversations/{id}
GET /admin/ai/messages
GET /admin/ai/token-usage
GET /admin/ai/summary-logs
```

---

## 21. 管理后台页面

在 `ruoyi-fastapi-frontend` 新增菜单：

```text
AI 酒馆管理
  ├─ AI 仪表盘
  ├─ 角色管理
  ├─ 会话管理
  ├─ 消息查询
  ├─ Token 消耗
  └─ 摘要日志
```

页面目录建议：

```text
ruoyi-fastapi-frontend/src/views/ai-tavern/
  dashboard/index.vue
  character/index.vue
  conversation/index.vue
  message/index.vue
  tokenUsage/index.vue
  summaryLog/index.vue
```

权限标识：

```text
ai:dashboard:view
ai:character:list
ai:character:query
ai:character:edit
ai:conversation:list
ai:conversation:query
ai:message:list
ai:token:list
ai:summary:list
```

---

## 22. 用户端页面

在 `ruoyi-fastapi-app` 中新增：

```text
src/pages/character/list.vue
src/pages/character/edit.vue
src/pages/conversation/list.vue
src/pages/chat/index.vue
```

初版页面：

```text
角色列表
创建角色
会话列表
聊天页
```

聊天页需要支持：

```text
加载历史消息
发送消息
显示 AI 回复
发送中 loading
失败重试
滚动到底部
```

---

## 23. 启动步骤

### 23.1 安装后端依赖

进入后端：

```bash
cd ruoyi-fastapi-backend
```

MySQL 版本安装：

```bash
pip3 install -r requirements.txt
```

---

### 23.2 配置后端环境

修改：

```text
.env.dev
```

至少确认：

```env
DB_TYPE = 'mysql'
DB_HOST = '127.0.0.1'
DB_PORT = 3306
DB_USERNAME = 'ceshi'
DB_PASSWORD = 'replace-with-database-password'
DB_DATABASE = 'ceshi'

REDIS_HOST = '127.0.0.1'
REDIS_PORT = 6379

DEEPSEEK_API_KEY = '你的DeepSeek_API_Key'
DEEPSEEK_BASE_URL = 'https://api.deepseek.com'
DEEPSEEK_MODEL = 'deepseek-v4-flash'

AI_SUMMARY_EVERY_N_TURNS = 20
AI_RECENT_MESSAGE_LIMIT = 60
AI_ENABLE_SUMMARY = true
```

---

### 23.3 启动后端

```bash
ruoyi app run --env=dev
```

默认后端地址：

```text
http://localhost:9099
```

接口文档：

```text
http://localhost:9099/docs
```

---

### 23.4 启动管理后台

```bash
cd ruoyi-fastapi-frontend
npm install --registry=https://registry.npmmirror.com
npm run dev
```

默认账号：

```text
admin
```

默认密码：

```text
admin123
```

---

### 23.5 启动用户端 H5

```bash
cd ruoyi-fastapi-app
pnpm install
pnpm dev:h5
```

---

## 24. 初版开发顺序

严格按这个顺序做：

```text
1. 跑通 RuoYi-Vue3-FastAPI 原项目。
2. 改 MySQL 数据库为 ceshi。
3. 导入 RuoYi 原始 SQL。
4. 新建 ai-tavern.sql。
5. 导入 AI 酒馆业务表。
6. 新建 module_ai_tavern 模块。
7. 实现 ai_character 角色 CRUD。
8. 实现 ai_conversation 会话 CRUD。
9. 实现 ai_message 消息保存和读取。
10. 接入 DeepSeek Provider。
11. 实现 build_chat_messages 上下文拼接。
12. 实现 POST /ai/chat/send。
13. 保存 ai_token_usage。
14. 实现每 20 轮摘要一次。
15. 管理后台增加 AI 菜单。
16. 管理后台查看会话、消息、token、摘要日志。
17. 用户端实现聊天页。
18. 测试长对话 50 轮以上是否能连续。
```

---

## 25. 初版验收标准

初版完成后，必须满足：

```text
[ ] MySQL 使用 ceshi 数据库。
[ ] 数据库用户名是 ceshi。
[ ] 数据库密码是 123456。
[ ] RuoYi 管理后台能正常登录。
[ ] 用户可以创建 AI 角色。
[ ] 用户可以创建会话。
[ ] 用户发送的消息保存到 ai_message。
[ ] AI 回复保存到 ai_message。
[ ] 刷新页面后还能看到历史聊天。
[ ] DeepSeek token 消耗保存到 ai_token_usage。
[ ] 每 20 轮用户消息自动生成一次 summary。
[ ] summary 保存到 ai_conversation.summary。
[ ] 后续聊天请求会带上 summary。
[ ] 管理员后台能看到 token 消耗。
[ ] 管理员后台能看到摘要日志。
```

---

## 26. 长文本对话测试方案

测试流程：

```text
1. 创建角色“扶摇”。
2. 创建新会话。
3. 连续发送 25 轮消息。
4. 检查 ai_message 是否有 50 条左右消息。
5. 检查 ai_conversation.summary 是否不为空。
6. 检查 summary_turn_count 是否被重置。
7. 继续发送 20 轮。
8. 检查 summary_version 是否 +1。
9. 问角色第 1~20 轮发生的重要事件。
10. 观察角色是否能根据摘要回答。
```

测试 SQL：

```sql
SELECT id, summary_version, summary_turn_count, last_summarized_message_id, summary
FROM ai_conversation
WHERE id = 你的会话ID;

SELECT COUNT(*)
FROM ai_message
WHERE conversation_id = 你的会话ID;

SELECT *
FROM ai_summary_log
WHERE conversation_id = 你的会话ID
ORDER BY create_time DESC;

SELECT request_type, SUM(total_tokens)
FROM ai_token_usage
WHERE conversation_id = 你的会话ID
GROUP BY request_type;
```

---

## 27. 重要开发注意事项

### 27.1 不要把 API Key 放前端

禁止放在：

```text
ruoyi-fastapi-frontend
ruoyi-fastapi-app
安卓包
Git 仓库
```

只能放在：

```text
ruoyi-fastapi-backend/.env.dev
ruoyi-fastapi-backend/.env.prod
```

---

### 27.2 对话必须保存服务器

客户端缓存只能加速显示，不能作为唯一存储。

正确：

```text
用户消息 → 后端 → MySQL ai_message
AI 回复 → 后端 → MySQL ai_message
```

错误：

```text
只存在 localStorage
只存在手机本地
只存在前端状态
```

---

### 27.3 摘要不要覆盖完整历史

摘要只是辅助记忆。  
完整历史仍然保存在 `ai_message` 中。

不要因为生成摘要就删除原始消息。

---

### 27.4 初版不要做向量记忆

初版只做：

```text
长期摘要 + 最近消息窗口
```

向量记忆后期再做。

---

### 27.5 每次请求不要发送所有历史

正确：

```text
角色设定 + 长期摘要 + 最近 60 条消息 + 用户新消息
```

错误：

```text
角色设定 + 从第一条开始的全部聊天历史
```

---

### 27.6 摘要失败不能影响聊天

如果摘要失败：

```text
聊天消息仍然要保存。
AI 回复仍然要返回。
summary_status 标记 failed。
ai_summary_log 记录失败原因。
管理员后台可以看到失败日志。
```

---

### 27.7 20 轮摘要建议后期改异步

初版可以同步执行，逻辑简单。  
但正式版建议后台异步执行，避免用户等待摘要完成。

推荐后期流程：

```text
聊天先返回
    ↓
summary_status = pending
    ↓
后台任务生成摘要
    ↓
更新 summary
```

---

## 28. 后续语音模块保留设计

后续接入阿里云声音复刻时新增：

```text
voice_profile
voice_clone_attempt
voice_synthesis_job
```

初版不需要实现，但 `ai_message` 已经预留：

```text
audio_url
audio_status
voice_profile_id
```

这样后续可以无缝扩展。

---

## 29. 后续向量记忆保留设计

如果以后使用 MySQL，向量检索不如 PostgreSQL + pgvector 方便。

后续可以选择：

```text
方案 A：继续 MySQL，使用独立向量数据库 Milvus / Qdrant。
方案 B：迁移记忆模块到 PostgreSQL + pgvector。
方案 C：初期只用 summary，不做向量。
```

你现在的初版目标是稳定做出产品，所以建议先用：

```text
MySQL + 摘要记忆
```

---

## 30. 最终初版目标

本阶段最终要得到：

```text
RuoYi-Vue3-FastAPI
    ↓
MySQL ceshi 数据库
    ↓
AI 酒馆业务表
    ↓
DeepSeek 对话
    ↓
服务器保存完整历史
    ↓
每 20 轮生成长期摘要
    ↓
管理员后台查看 token 和摘要日志
    ↓
用户端可持续长对话
```

这就是项目初版最重要、最现实、最容易成功的版本。
