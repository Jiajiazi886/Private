from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class TavernBaseModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, from_attributes=True)


class CharacterModel(TavernBaseModel):
    id: int | None = None
    user_id: int | None = None
    name: str = Field(min_length=1, max_length=100)
    avatar_url: str | None = None
    description: str | None = None
    personality: str | None = None
    scenario: str | None = None
    first_message: str | None = None
    system_prompt: str | None = None
    example_dialogues: str | None = None
    status: Literal['0', '1'] | None = '0'
    remark: str | None = None
    create_time: datetime | None = None
    update_time: datetime | None = None


class CharacterQueryModel(TavernBaseModel):
    page_num: int = 1
    page_size: int = 10
    name: str | None = None
    user_id: int | None = None
    status: Literal['0', '1'] | None = None


class ConversationCreateModel(TavernBaseModel):
    character_id: int
    title: str | None = None
    conversation_prompt: str | None = None


class ConversationQueryModel(TavernBaseModel):
    page_num: int = 1
    page_size: int = 10
    user_id: int | None = None
    character_id: int | None = None
    title: str | None = None
    status: Literal['0', '1'] | None = None


class ConversationUpdateModel(TavernBaseModel):
    title: str | None = Field(default=None, max_length=200)
    summary: str | None = None
    conversation_prompt: str | None = None
    forced_memory: str | None = None


class MessageQueryModel(TavernBaseModel):
    page_num: int = 1
    page_size: int = 10
    user_id: int | None = None
    conversation_id: int | None = None
    character_id: int | None = None
    role: str | None = None


class MessageModel(TavernBaseModel):
    id: int | None = None
    conversation_id: int | None = None
    user_id: int | None = None
    character_id: int | None = None
    role: str | None = None
    content: str | None = None
    seq_no: int | None = None
    prompt_tokens: int | None = 0
    completion_tokens: int | None = 0
    total_tokens: int | None = 0
    audio_status: str | None = None
    is_edited: bool | None = False
    create_time: datetime | None = None
    update_time: datetime | None = None


class ChatSendModel(TavernBaseModel):
    conversation_id: int
    content: str = Field(min_length=1)


class MessageUpdateModel(TavernBaseModel):
    content: str = Field(min_length=1)


class TokenUsageModel(TavernBaseModel):
    id: int | None = None
    user_id: int | None = None
    user_name: str | None = None
    nick_name: str | None = None
    conversation_id: int | None = None
    character_id: int | None = None
    message_id: int | None = None
    provider: str | None = None
    model: str | None = None
    prompt_tokens: int | None = 0
    completion_tokens: int | None = 0
    total_tokens: int | None = 0
    reasoning_tokens: int | None = None
    cached_tokens: int | None = None
    prompt_cache_hit_tokens: int | None = 0
    prompt_cache_miss_tokens: int | None = 0
    estimated_cost_yuan: str | None = '0'
    request_type: str | None = None
    request_id: str | None = None
    latency_ms: int | None = None
    success: bool | None = True
    error_message: str | None = None
    create_time: datetime | None = None


class TokenUsageQueryModel(TavernBaseModel):
    page_num: int = 1
    page_size: int = 10
    user_id: int | None = None
    model: str | None = None
    request_type: str | None = None
    success: bool | None = None
    begin_time: str | None = None
    end_time: str | None = None


class SummaryLogModel(TavernBaseModel):
    id: int | None = None
    user_id: int | None = None
    conversation_id: int | None = None
    character_id: int | None = None
    old_summary: str | None = None
    new_summary: str | None = None
    start_message_id: int | None = None
    end_message_id: int | None = None
    message_count: int | None = 0
    model: str | None = None
    prompt_tokens: int | None = 0
    completion_tokens: int | None = 0
    total_tokens: int | None = 0
    success: bool | None = True
    error_message: str | None = None
    create_time: datetime | None = None


class UserTokenSettingModel(TavernBaseModel):
    id: int | None = None
    user_id: int
    user_name: str | None = None
    nick_name: str | None = None
    daily_token_limit: int | None = 0
    monthly_token_limit: int | None = 0
    total_token_limit: int | None = 0
    daily_cost_limit_yuan: Decimal | None = Decimal('0')
    monthly_cost_limit_yuan: Decimal | None = Decimal('0')
    total_cost_limit_yuan: Decimal | None = Decimal('0')
    enabled: bool | None = True
    used_today_tokens: int | None = 0
    used_month_tokens: int | None = 0
    used_total_tokens: int | None = 0
    used_today_cost_yuan: Decimal | None = Decimal('0')
    used_month_cost_yuan: Decimal | None = Decimal('0')
    used_total_cost_yuan: Decimal | None = Decimal('0')
    create_time: datetime | None = None
    update_time: datetime | None = None
    remark: str | None = None


class UserTokenSettingQueryModel(TavernBaseModel):
    page_num: int = 1
    page_size: int = 10
    user_id: int | None = None
    user_name: str | None = None
    nick_name: str | None = None
    enabled: bool | None = None


class UserTokenSettingUpdateModel(TavernBaseModel):
    user_id: int
    daily_token_limit: int | None = 0
    monthly_token_limit: int | None = 0
    total_token_limit: int | None = 0
    daily_cost_limit_yuan: Decimal | None = Decimal('0')
    monthly_cost_limit_yuan: Decimal | None = Decimal('0')
    total_cost_limit_yuan: Decimal | None = Decimal('0')
    enabled: bool | None = True
    remark: str | None = None
