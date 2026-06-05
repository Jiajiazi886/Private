CREATE TABLE IF NOT EXISTS ai_character (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  user_id BIGINT NOT NULL COMMENT 'user id',
  name VARCHAR(100) NOT NULL COMMENT 'character name',
  avatar_url TEXT COMMENT 'avatar url',
  description TEXT COMMENT 'description',
  personality TEXT COMMENT 'personality',
  scenario TEXT COMMENT 'scenario',
  first_message TEXT COMMENT 'first assistant message',
  system_prompt TEXT COMMENT 'system prompt',
  example_dialogues TEXT COMMENT 'example dialogues',
  voice_profile_id BIGINT NULL COMMENT 'voice profile id',
  status CHAR(1) DEFAULT '0' COMMENT '0 enabled, 1 disabled',
  create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
  update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  remark TEXT,
  INDEX idx_ai_character_user_id (user_id),
  INDEX idx_ai_character_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='AI character';

CREATE TABLE IF NOT EXISTS ai_conversation (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  user_id BIGINT NOT NULL COMMENT 'user id',
  character_id BIGINT NOT NULL COMMENT 'character id',
  title VARCHAR(200) COMMENT 'conversation title',
  summary LONGTEXT COMMENT 'long term summary',
  summary_version INT DEFAULT 0 COMMENT 'summary version',
  summary_turn_count INT DEFAULT 0 COMMENT 'turn count since last summary',
  last_summarized_message_id BIGINT NULL COMMENT 'last summarized message id',
  last_summary_time DATETIME NULL COMMENT 'last summary time',
  summary_status VARCHAR(20) DEFAULT 'idle' COMMENT 'idle/pending/running/failed',
  total_turn_count INT DEFAULT 0 COMMENT 'total user turns',
  total_message_count INT DEFAULT 0 COMMENT 'total messages',
  status CHAR(1) DEFAULT '0' COMMENT '0 enabled, 1 disabled',
  create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
  update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX idx_ai_conversation_user_id (user_id),
  INDEX idx_ai_conversation_character_id (character_id),
  INDEX idx_ai_conversation_update_time (update_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='AI conversation';

CREATE TABLE IF NOT EXISTS ai_message (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  conversation_id BIGINT NOT NULL COMMENT 'conversation id',
  user_id BIGINT NOT NULL COMMENT 'user id',
  character_id BIGINT NULL COMMENT 'character id',
  role VARCHAR(20) NOT NULL COMMENT 'user/assistant/system',
  content LONGTEXT NOT NULL COMMENT 'message content',
  seq_no INT NOT NULL DEFAULT 0 COMMENT 'message sequence in conversation',
  prompt_tokens INT DEFAULT 0 COMMENT 'input tokens',
  completion_tokens INT DEFAULT 0 COMMENT 'output tokens',
  total_tokens INT DEFAULT 0 COMMENT 'total tokens',
  audio_url TEXT COMMENT 'future voice audio url',
  audio_status VARCHAR(20) DEFAULT 'none' COMMENT 'none/pending/ready/failed',
  voice_profile_id BIGINT NULL COMMENT 'voice profile id',
  create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_ai_message_conversation_id (conversation_id),
  INDEX idx_ai_message_user_id (user_id),
  INDEX idx_ai_message_character_id (character_id),
  INDEX idx_ai_message_role (role),
  INDEX idx_ai_message_seq_no (conversation_id, seq_no),
  INDEX idx_ai_message_create_time (create_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='AI message';

CREATE TABLE IF NOT EXISTS ai_token_usage (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  user_id BIGINT NOT NULL COMMENT 'user id',
  conversation_id BIGINT NULL COMMENT 'conversation id',
  character_id BIGINT NULL COMMENT 'character id',
  message_id BIGINT NULL COMMENT 'message id',
  provider VARCHAR(50) DEFAULT 'deepseek' COMMENT 'provider',
  model VARCHAR(100) NOT NULL COMMENT 'model',
  prompt_tokens INT DEFAULT 0 COMMENT 'input tokens',
  completion_tokens INT DEFAULT 0 COMMENT 'output tokens',
  total_tokens INT DEFAULT 0 COMMENT 'total tokens',
  reasoning_tokens INT NULL COMMENT 'reasoning tokens',
  cached_tokens INT NULL COMMENT 'cache hit tokens',
  prompt_cache_hit_tokens INT DEFAULT 0 COMMENT 'prompt cache hit tokens',
  prompt_cache_miss_tokens INT DEFAULT 0 COMMENT 'prompt cache miss tokens',
  estimated_cost_yuan DECIMAL(18, 6) DEFAULT 0 COMMENT 'estimated cost in CNY',
  request_type VARCHAR(50) DEFAULT 'chat' COMMENT 'chat/summary/voice',
  request_id VARCHAR(100) NULL COMMENT 'provider request id',
  latency_ms INT NULL COMMENT 'latency in milliseconds',
  success TINYINT(1) DEFAULT 1 COMMENT 'success flag',
  error_message TEXT COMMENT 'error message',
  create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_ai_token_usage_user_id (user_id),
  INDEX idx_ai_token_usage_conversation_id (conversation_id),
  INDEX idx_ai_token_usage_model (model),
  INDEX idx_ai_token_usage_request_type (request_type),
  INDEX idx_ai_token_usage_create_time (create_time),
  INDEX idx_ai_token_usage_success (success)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='AI token usage';

CREATE TABLE IF NOT EXISTS ai_summary_log (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  user_id BIGINT NOT NULL,
  conversation_id BIGINT NOT NULL,
  character_id BIGINT NULL,
  old_summary LONGTEXT COMMENT 'old summary',
  new_summary LONGTEXT COMMENT 'new summary',
  start_message_id BIGINT NULL COMMENT 'start message id',
  end_message_id BIGINT NULL COMMENT 'end message id',
  message_count INT DEFAULT 0 COMMENT 'summarized message count',
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='AI summary log';

CREATE TABLE IF NOT EXISTS sys_user_token_setting (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  user_id BIGINT NOT NULL COMMENT 'user id',
  daily_token_limit BIGINT DEFAULT 0 COMMENT 'daily token limit, 0 means unlimited',
  monthly_token_limit BIGINT DEFAULT 0 COMMENT 'monthly token limit, 0 means unlimited',
  total_token_limit BIGINT DEFAULT 0 COMMENT 'total token limit, 0 means unlimited',
  daily_cost_limit_yuan DECIMAL(18, 6) DEFAULT 0 COMMENT 'daily cost limit in CNY, 0 means unlimited',
  monthly_cost_limit_yuan DECIMAL(18, 6) DEFAULT 0 COMMENT 'monthly cost limit in CNY, 0 means unlimited',
  total_cost_limit_yuan DECIMAL(18, 6) DEFAULT 0 COMMENT 'total cost limit in CNY, 0 means unlimited',
  enabled TINYINT(1) DEFAULT 1 COMMENT 'quota enabled',
  create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
  update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  remark TEXT,
  UNIQUE KEY uk_sys_user_token_setting_user_id (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='用户Token设置';

INSERT INTO sys_role
SELECT '1', '超级管理员', 'admin', 1, 1, 1, 1, '0', '0', 'admin', sysdate(), '', null, '超级管理员'
WHERE NOT EXISTS (SELECT 1 FROM sys_role WHERE role_id = 1);

INSERT INTO sys_menu
SELECT '1', '系统管理', '0', '1', 'system', NULL, '', '', 1, 0, 'M', '0', '0', '', 'system', 'admin', sysdate(), '', null, '系统管理目录'
WHERE NOT EXISTS (SELECT 1 FROM sys_menu WHERE menu_id = 1);

INSERT INTO sys_menu
SELECT '100', '用户管理', '1', '1', 'user', 'system/user/index', '', '', 1, 0, 'C', '0', '0', 'system:user:list', 'user', 'admin', sysdate(), '', null, '用户管理菜单'
WHERE NOT EXISTS (SELECT 1 FROM sys_menu WHERE menu_id = 100);

INSERT INTO sys_menu
SELECT '101', '角色管理', '1', '2', 'role', 'system/role/index', '', '', 1, 0, 'C', '0', '0', 'system:role:list', 'peoples', 'admin', sysdate(), '', null, '角色管理菜单'
WHERE NOT EXISTS (SELECT 1 FROM sys_menu WHERE menu_id = 101);

INSERT INTO sys_menu
SELECT '102', '菜单管理', '1', '3', 'menu', 'system/menu/index', '', '', 1, 0, 'C', '0', '0', 'system:menu:list', 'tree-table', 'admin', sysdate(), '', null, '菜单管理菜单'
WHERE NOT EXISTS (SELECT 1 FROM sys_menu WHERE menu_id = 102);

INSERT INTO sys_menu
SELECT '1600', '用户Token设置', '1', '10', 'userToken', 'system/userToken/index', '', '', 1, 0, 'C', '0', '0', 'system:userToken:list', 'money', 'admin', sysdate(), '', null, '用户Token设置菜单'
WHERE NOT EXISTS (SELECT 1 FROM sys_menu WHERE menu_id = 1600);

INSERT INTO sys_menu
SELECT '1601', '用户Token查询', '1600', '1', '', '', '', '', 1, 0, 'F', '0', '0', 'system:userToken:list', '#', 'admin', sysdate(), '', null, '用户Token查询按钮'
WHERE NOT EXISTS (SELECT 1 FROM sys_menu WHERE menu_id = 1601);

INSERT INTO sys_menu
SELECT '1602', '用户Token修改', '1600', '2', '', '', '', '', 1, 0, 'F', '0', '0', 'system:userToken:edit', '#', 'admin', sysdate(), '', null, '用户Token修改按钮'
WHERE NOT EXISTS (SELECT 1 FROM sys_menu WHERE menu_id = 1602);

INSERT INTO sys_menu
SELECT menu_id, menu_name, parent_id, order_num, path, component, query, route_name, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark
FROM (
  SELECT '1000' menu_id, '用户查询' menu_name, '100' parent_id, '1' order_num, '' path, '' component, '' query, '' route_name, 1 is_frame, 0 is_cache, 'F' menu_type, '0' visible, '0' status, 'system:user:query' perms, '#' icon, 'admin' create_by, sysdate() create_time, '' update_by, null update_time, '' remark
  UNION ALL SELECT '1001', '用户新增', '100', '2', '', '', '', '', 1, 0, 'F', '0', '0', 'system:user:add', '#', 'admin', sysdate(), '', null, ''
  UNION ALL SELECT '1002', '用户修改', '100', '3', '', '', '', '', 1, 0, 'F', '0', '0', 'system:user:edit', '#', 'admin', sysdate(), '', null, ''
  UNION ALL SELECT '1003', '用户删除', '100', '4', '', '', '', '', 1, 0, 'F', '0', '0', 'system:user:remove', '#', 'admin', sysdate(), '', null, ''
  UNION ALL SELECT '1004', '用户导出', '100', '5', '', '', '', '', 1, 0, 'F', '0', '0', 'system:user:export', '#', 'admin', sysdate(), '', null, ''
  UNION ALL SELECT '1005', '用户导入', '100', '6', '', '', '', '', 1, 0, 'F', '0', '0', 'system:user:import', '#', 'admin', sysdate(), '', null, ''
  UNION ALL SELECT '1006', '重置密码', '100', '7', '', '', '', '', 1, 0, 'F', '0', '0', 'system:user:resetPwd', '#', 'admin', sysdate(), '', null, ''
  UNION ALL SELECT '1007', '角色查询', '101', '1', '', '', '', '', 1, 0, 'F', '0', '0', 'system:role:query', '#', 'admin', sysdate(), '', null, ''
  UNION ALL SELECT '1008', '角色新增', '101', '2', '', '', '', '', 1, 0, 'F', '0', '0', 'system:role:add', '#', 'admin', sysdate(), '', null, ''
  UNION ALL SELECT '1009', '角色修改', '101', '3', '', '', '', '', 1, 0, 'F', '0', '0', 'system:role:edit', '#', 'admin', sysdate(), '', null, ''
  UNION ALL SELECT '1010', '角色删除', '101', '4', '', '', '', '', 1, 0, 'F', '0', '0', 'system:role:remove', '#', 'admin', sysdate(), '', null, ''
  UNION ALL SELECT '1011', '角色导出', '101', '5', '', '', '', '', 1, 0, 'F', '0', '0', 'system:role:export', '#', 'admin', sysdate(), '', null, ''
  UNION ALL SELECT '1012', '菜单查询', '102', '1', '', '', '', '', 1, 0, 'F', '0', '0', 'system:menu:query', '#', 'admin', sysdate(), '', null, ''
  UNION ALL SELECT '1013', '菜单新增', '102', '2', '', '', '', '', 1, 0, 'F', '0', '0', 'system:menu:add', '#', 'admin', sysdate(), '', null, ''
  UNION ALL SELECT '1014', '菜单修改', '102', '3', '', '', '', '', 1, 0, 'F', '0', '0', 'system:menu:edit', '#', 'admin', sysdate(), '', null, ''
  UNION ALL SELECT '1015', '菜单删除', '102', '4', '', '', '', '', 1, 0, 'F', '0', '0', 'system:menu:remove', '#', 'admin', sysdate(), '', null, ''
) restored_menu
WHERE NOT EXISTS (SELECT 1 FROM sys_menu WHERE sys_menu.menu_id = restored_menu.menu_id);

INSERT INTO sys_menu
SELECT '4', 'AI 管理', '0', '4', 'ai', NULL, '', '', 1, 0, 'M', '0', '0', '', 'ai-manage', 'admin', sysdate(), '', null, 'AI 管理目录'
WHERE NOT EXISTS (SELECT 1 FROM sys_menu WHERE menu_id = 4);

INSERT INTO sys_menu
SELECT '1500', 'AI 酒馆管理', '4', '10', 'tavern', NULL, '', '', 1, 0, 'M', '0', '0', '', 'ai-chat', 'admin', sysdate(), '', null, 'AI 酒馆管理目录'
WHERE NOT EXISTS (SELECT 1 FROM sys_menu WHERE menu_id = 1500);

INSERT INTO sys_menu
SELECT '1501', 'Token 消耗', '1500', '1', 'tokenUsage', 'ai-tavern/tokenUsage/index', '', '', 1, 0, 'C', '0', '0', 'ai:token:list', 'money', 'admin', sysdate(), '', null, 'AI Token 消耗菜单'
WHERE NOT EXISTS (SELECT 1 FROM sys_menu WHERE menu_id = 1501);

INSERT INTO sys_menu
SELECT '1502', 'Token 查询', '1501', '1', '', '', '', '', 1, 0, 'F', '0', '0', 'ai:token:list', '#', 'admin', sysdate(), '', null, 'AI Token 查询按钮'
WHERE NOT EXISTS (SELECT 1 FROM sys_menu WHERE menu_id = 1502);

INSERT INTO sys_menu
SELECT '1503', '角色管理', '1500', '2', 'character', 'ai-tavern/character/index', '', '', 1, 0, 'C', '0', '0', 'ai:character:list', 'peoples', 'admin', sysdate(), '', null, 'AI 角色管理菜单'
WHERE NOT EXISTS (SELECT 1 FROM sys_menu WHERE menu_id = 1503);

INSERT INTO sys_menu
SELECT '1504', '会话管理', '1500', '3', 'conversation', 'ai-tavern/conversation/index', '', '', 1, 0, 'C', '0', '0', 'ai:conversation:list', 'message', 'admin', sysdate(), '', null, 'AI 会话管理菜单'
WHERE NOT EXISTS (SELECT 1 FROM sys_menu WHERE menu_id = 1504);

INSERT INTO sys_menu
SELECT '1505', '角色聊天', '1500', '4', 'chat', 'ai-tavern/chat/index', '', '', 1, 0, 'C', '0', '0', 'ai:chat:send', 'ai-chat', 'admin', sysdate(), '', null, 'AI 角色聊天菜单'
WHERE NOT EXISTS (SELECT 1 FROM sys_menu WHERE menu_id = 1505);

INSERT INTO sys_menu
SELECT '1506', '角色查询', '1503', '1', '', '', '', '', 1, 0, 'F', '0', '0', 'ai:character:list', '#', 'admin', sysdate(), '', null, 'AI 角色查询按钮'
WHERE NOT EXISTS (SELECT 1 FROM sys_menu WHERE menu_id = 1506);

INSERT INTO sys_menu
SELECT '1507', '会话查询', '1504', '1', '', '', '', '', 1, 0, 'F', '0', '0', 'ai:conversation:list', '#', 'admin', sysdate(), '', null, 'AI 会话查询按钮'
WHERE NOT EXISTS (SELECT 1 FROM sys_menu WHERE menu_id = 1507);

INSERT INTO sys_user_role
SELECT 1, 1
WHERE EXISTS (SELECT 1 FROM sys_user WHERE user_id = 1)
  AND EXISTS (SELECT 1 FROM sys_role WHERE role_id = 1)
  AND NOT EXISTS (SELECT 1 FROM sys_user_role WHERE user_id = 1 AND role_id = 1);

INSERT INTO sys_role_menu
SELECT 1, menu_id
FROM sys_menu
WHERE (menu_id = 4 OR menu_id BETWEEN 1500 AND 1507)
  AND EXISTS (SELECT 1 FROM sys_role WHERE role_id = 1)
  AND NOT EXISTS (
    SELECT 1 FROM sys_role_menu WHERE role_id = 1 AND sys_role_menu.menu_id = sys_menu.menu_id
  );

INSERT INTO sys_role_menu
SELECT 1, menu_id
FROM sys_menu
WHERE (menu_id IN (1, 100, 101, 102, 1600, 1601, 1602) OR menu_id BETWEEN 1000 AND 1015)
  AND EXISTS (SELECT 1 FROM sys_role WHERE role_id = 1)
  AND NOT EXISTS (
    SELECT 1 FROM sys_role_menu WHERE role_id = 1 AND sys_role_menu.menu_id = sys_menu.menu_id
  );
