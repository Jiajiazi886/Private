from datetime import datetime

from sqlalchemy import CHAR, BigInteger, Boolean, Column, DateTime, Integer, Numeric, String, Text

from config.database import Base


class AiCharacter(Base):
    __tablename__ = 'ai_character'
    __table_args__ = {'comment': 'AI roleplay character'}

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    avatar_url = Column(Text)
    description = Column(Text)
    personality = Column(Text)
    scenario = Column(Text)
    first_message = Column(Text)
    system_prompt = Column(Text)
    example_dialogues = Column(Text)
    voice_profile_id = Column(BigInteger)
    status = Column(CHAR(1), default='0', server_default='0', index=True)
    create_time = Column(DateTime, default=datetime.now)
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    remark = Column(Text)


class AiConversation(Base):
    __tablename__ = 'ai_conversation'
    __table_args__ = {'comment': 'AI roleplay conversation'}

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, nullable=False, index=True)
    character_id = Column(BigInteger, nullable=False, index=True)
    title = Column(String(200))
    summary = Column(Text)
    conversation_prompt = Column(Text)
    forced_memory = Column(Text)
    summary_version = Column(Integer, default=0, server_default='0')
    summary_turn_count = Column(Integer, default=0, server_default='0')
    last_summarized_message_id = Column(BigInteger)
    last_summary_time = Column(DateTime)
    summary_status = Column(String(20), default='idle', server_default='idle')
    total_turn_count = Column(Integer, default=0, server_default='0')
    total_message_count = Column(Integer, default=0, server_default='0')
    status = Column(CHAR(1), default='0', server_default='0', index=True)
    create_time = Column(DateTime, default=datetime.now)
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now, index=True)


class AiMessage(Base):
    __tablename__ = 'ai_message'
    __table_args__ = {'comment': 'AI roleplay message'}

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    conversation_id = Column(BigInteger, nullable=False, index=True)
    user_id = Column(BigInteger, nullable=False, index=True)
    character_id = Column(BigInteger, index=True)
    role = Column(String(20), nullable=False, index=True)
    content = Column(Text, nullable=False)
    seq_no = Column(Integer, nullable=False, default=0, server_default='0')
    prompt_tokens = Column(Integer, default=0, server_default='0')
    completion_tokens = Column(Integer, default=0, server_default='0')
    total_tokens = Column(Integer, default=0, server_default='0')
    audio_url = Column(Text)
    audio_status = Column(String(20), default='none', server_default='none')
    voice_profile_id = Column(BigInteger)
    is_edited = Column(Boolean, default=False, server_default='0')
    create_time = Column(DateTime, default=datetime.now, index=True)
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class AiTokenUsage(Base):
    __tablename__ = 'ai_token_usage'
    __table_args__ = {'comment': 'AI token usage'}

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, nullable=False, index=True)
    conversation_id = Column(BigInteger, index=True)
    character_id = Column(BigInteger)
    message_id = Column(BigInteger)
    provider = Column(String(50), default='deepseek', server_default='deepseek')
    model = Column(String(100), nullable=False, index=True)
    prompt_tokens = Column(Integer, default=0, server_default='0')
    completion_tokens = Column(Integer, default=0, server_default='0')
    total_tokens = Column(Integer, default=0, server_default='0')
    reasoning_tokens = Column(Integer)
    cached_tokens = Column(Integer)
    prompt_cache_hit_tokens = Column(Integer, default=0, server_default='0')
    prompt_cache_miss_tokens = Column(Integer, default=0, server_default='0')
    estimated_cost_yuan = Column(Numeric(18, 6), default=0, server_default='0')
    request_type = Column(String(50), default='chat', server_default='chat', index=True)
    request_id = Column(String(100))
    latency_ms = Column(Integer)
    success = Column(Boolean, default=True, server_default='1', index=True)
    error_message = Column(Text)
    create_time = Column(DateTime, default=datetime.now, index=True)


class AiSummaryLog(Base):
    __tablename__ = 'ai_summary_log'
    __table_args__ = {'comment': 'AI summary log'}

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, nullable=False, index=True)
    conversation_id = Column(BigInteger, nullable=False, index=True)
    character_id = Column(BigInteger)
    old_summary = Column(Text)
    new_summary = Column(Text)
    start_message_id = Column(BigInteger)
    end_message_id = Column(BigInteger)
    message_count = Column(Integer, default=0, server_default='0')
    model = Column(String(100), default='deepseek-v4-flash', server_default='deepseek-v4-flash')
    prompt_tokens = Column(Integer, default=0, server_default='0')
    completion_tokens = Column(Integer, default=0, server_default='0')
    total_tokens = Column(Integer, default=0, server_default='0')
    success = Column(Boolean, default=True, server_default='1')
    error_message = Column(Text)
    create_time = Column(DateTime, default=datetime.now, index=True)


class SysUserTokenSetting(Base):
    __tablename__ = 'sys_user_token_setting'
    __table_args__ = {'comment': 'User token quota setting'}

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, nullable=False, unique=True, index=True)
    daily_token_limit = Column(BigInteger, default=0, server_default='0')
    monthly_token_limit = Column(BigInteger, default=0, server_default='0')
    total_token_limit = Column(BigInteger, default=0, server_default='0')
    daily_cost_limit_yuan = Column(Numeric(18, 6), default=0, server_default='0')
    monthly_cost_limit_yuan = Column(Numeric(18, 6), default=0, server_default='0')
    total_cost_limit_yuan = Column(Numeric(18, 6), default=0, server_default='0')
    enabled = Column(Boolean, default=True, server_default='1')
    create_time = Column(DateTime, default=datetime.now)
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    remark = Column(Text)
