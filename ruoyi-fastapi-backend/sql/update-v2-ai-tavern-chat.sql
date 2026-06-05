ALTER TABLE ai_conversation
  ADD COLUMN conversation_prompt LONGTEXT NULL COMMENT 'conversation prompt' AFTER summary;

ALTER TABLE ai_conversation
  ADD COLUMN forced_memory LONGTEXT NULL COMMENT 'forced memory' AFTER conversation_prompt;

ALTER TABLE ai_message
  ADD COLUMN is_edited TINYINT(1) DEFAULT 0 COMMENT 'message edited flag' AFTER voice_profile_id;

ALTER TABLE ai_message
  ADD COLUMN update_time DATETIME NULL COMMENT 'message update time' AFTER create_time;
