from datetime import datetime, time
from decimal import Decimal
from typing import Any

from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from common.vo import CrudResponseModel, PageModel
from config.env import AiTavernConfig
from exceptions.exception import ServiceException
from module_ai_tavern.dao.tavern_dao import TavernDao
from module_ai_tavern.entity.do.tavern_do import (
    AiCharacter,
    AiConversation,
    AiMessage,
    AiSummaryLog,
    AiTokenUsage,
    SysUserTokenSetting,
)
from module_ai_tavern.entity.vo.tavern_vo import (
    CharacterModel,
    CharacterQueryModel,
    ChatSendModel,
    ConversationCreateModel,
    ConversationQueryModel,
    MessageQueryModel,
    TokenUsageQueryModel,
    UserTokenSettingQueryModel,
    UserTokenSettingUpdateModel,
)
from module_ai_tavern.prompt.character_prompt import build_character_system_prompt
from module_ai_tavern.prompt.summary_prompt import build_summary_prompt
from module_ai_tavern.provider.deepseek_provider import DeepSeekProvider
from utils.common_util import CamelCaseUtil


class TokenCost:
    # DeepSeek V4 Flash prices, CNY per 1M tokens, read 2026-06-02 from official docs.
    INPUT_CACHE_HIT = Decimal('0.02')
    INPUT_CACHE_MISS = Decimal('1')
    OUTPUT = Decimal('2')

    @classmethod
    def estimate_yuan(cls, hit: int, miss: int, output: int) -> Decimal:
        total = (
            Decimal(hit) * cls.INPUT_CACHE_HIT
            + Decimal(miss) * cls.INPUT_CACHE_MISS
            + Decimal(output) * cls.OUTPUT
        ) / Decimal(1_000_000)
        return total.quantize(Decimal('0.000001'))


class UsageParser:
    @classmethod
    def get(cls, usage: Any, name: str, default: int = 0) -> int:
        if usage is None:
            return default
        if isinstance(usage, dict):
            return int(usage.get(name) or default)
        return int(getattr(usage, name, default) or default)

    @classmethod
    def reasoning_tokens(cls, usage: Any) -> int | None:
        details = None
        if isinstance(usage, dict):
            details = usage.get('completion_tokens_details')
        elif usage is not None:
            details = getattr(usage, 'completion_tokens_details', None)
        if not details:
            return None
        if isinstance(details, dict):
            return details.get('reasoning_tokens')
        return getattr(details, 'reasoning_tokens', None)


class TavernService:
    @classmethod
    async def create_character(cls, db: AsyncSession, user_id: int, data: CharacterModel) -> CharacterModel:
        character = AiCharacter(
            user_id=user_id,
            name=data.name,
            avatar_url=data.avatar_url,
            description=data.description,
            personality=data.personality,
            scenario=data.scenario,
            first_message=data.first_message,
            system_prompt=data.system_prompt,
            example_dialogues=data.example_dialogues,
            status=data.status or '0',
            remark=data.remark,
            create_time=datetime.now(),
            update_time=datetime.now(),
        )
        await TavernDao.add_character(db, character)
        await db.commit()
        return CharacterModel.model_validate(character)

    @classmethod
    async def update_character(cls, db: AsyncSession, user_id: int, character_id: int, data: CharacterModel) -> CrudResponseModel:
        character = await TavernDao.get_character(db, character_id)
        if not character or character.user_id != user_id:
            raise ServiceException(message='角色不存在或无权限访问')
        for field in [
            'name',
            'avatar_url',
            'description',
            'personality',
            'scenario',
            'first_message',
            'system_prompt',
            'example_dialogues',
            'status',
            'remark',
        ]:
            value = getattr(data, field, None)
            if value is not None:
                setattr(character, field, value)
        character.update_time = datetime.now()
        await db.commit()
        return CrudResponseModel(is_success=True, message='更新成功')

    @classmethod
    async def list_characters(cls, db: AsyncSession, query: CharacterQueryModel, current_user_id: int | None = None) -> Any:
        if current_user_id and not query.user_id:
            query.user_id = current_user_id
        return await TavernDao.list_characters(db, query, is_page=True)

    @classmethod
    async def get_character_detail(cls, db: AsyncSession, user_id: int, character_id: int) -> CharacterModel:
        character = await TavernDao.get_character(db, character_id)
        if not character or character.user_id != user_id:
            raise ServiceException(message='角色不存在或无权限访问')
        return CharacterModel.model_validate(character)

    @classmethod
    async def delete_character(cls, db: AsyncSession, user_id: int, character_id: int) -> CrudResponseModel:
        await TavernDao.delete_character(db, character_id, user_id)
        await db.commit()
        return CrudResponseModel(is_success=True, message='删除成功')

    @classmethod
    async def create_conversation(
        cls, db: AsyncSession, user_id: int, data: ConversationCreateModel
    ) -> dict[str, Any]:
        character = await TavernDao.get_character(db, data.character_id)
        if not character or character.user_id != user_id or character.status != '0':
            raise ServiceException(message='角色不存在或无权限访问')
        conversation = AiConversation(
            user_id=user_id,
            character_id=data.character_id,
            title=data.title or f'和{character.name}的对话',
            create_time=datetime.now(),
            update_time=datetime.now(),
        )
        await TavernDao.add_conversation(db, conversation)
        if character.first_message:
            seq = await TavernDao.get_next_message_seq(db, conversation.id)
            await TavernDao.add_message(
                db,
                AiMessage(
                    conversation_id=conversation.id,
                    user_id=user_id,
                    character_id=character.id,
                    role='assistant',
                    content=character.first_message,
                    seq_no=seq,
                    create_time=datetime.now(),
                ),
            )
            conversation.total_message_count = 1
        await db.commit()
        return CamelCaseUtil.transform_result(conversation)

    @classmethod
    async def list_conversations(
        cls, db: AsyncSession, query: ConversationQueryModel, current_user_id: int | None = None
    ) -> Any:
        if current_user_id and not query.user_id:
            query.user_id = current_user_id
        return await TavernDao.list_conversations(db, query, is_page=True)

    @classmethod
    async def delete_conversation(cls, db: AsyncSession, user_id: int, conversation_id: int) -> CrudResponseModel:
        await TavernDao.delete_conversation(db, conversation_id, user_id)
        await db.commit()
        return CrudResponseModel(is_success=True, message='删除成功')

    @classmethod
    async def list_messages(cls, db: AsyncSession, query: MessageQueryModel, current_user_id: int | None = None) -> Any:
        if current_user_id and not query.user_id:
            query.user_id = current_user_id
        return await TavernDao.list_messages(db, query, is_page=True)

    @classmethod
    async def get_conversation_messages(cls, db: AsyncSession, user_id: int, conversation_id: int) -> list[dict[str, Any]]:
        conversation = await TavernDao.get_user_conversation(db, user_id, conversation_id)
        if not conversation:
            raise ServiceException(message='会话不存在或无权限访问')
        messages = await TavernDao.recent_messages(db, conversation_id, 1000)
        result = CamelCaseUtil.transform_result(messages)
        latency_map = await TavernDao.message_latency_map(db, [message.id for message in messages])
        for item in result:
            if item.get('id') in latency_map:
                item['latencyMs'] = latency_map[item['id']]
        return result

    @classmethod
    async def send_chat(cls, db: AsyncSession, user_id: int, data: ChatSendModel) -> dict[str, Any]:
        conversation = await TavernDao.get_user_conversation(db, user_id, data.conversation_id)
        if not conversation:
            raise ServiceException(message='会话不存在或无权限访问')
        character = await TavernDao.get_character(db, conversation.character_id)
        if not character or character.status != '0':
            raise ServiceException(message='角色不存在或已禁用')
        await cls._assert_user_token_quota(db, user_id)

        user_message = await cls._create_message(db, conversation, 'user', data.content)
        messages = await cls._build_chat_messages(db, conversation, character, data.content)

        try:
            result = await DeepSeekProvider.chat(messages=messages, user_id=str(user_id), request_type='chat')
            assistant_message = await cls._create_message(db, conversation, 'assistant', result['content'])
            await cls._record_usage(
                db=db,
                user_id=user_id,
                conversation_id=conversation.id,
                character_id=character.id,
                message_id=assistant_message.id,
                model=result['model'],
                usage=result['usage'],
                latency_ms=result['latency_ms'],
                request_type='chat',
                request_id=result.get('request_id'),
                success=True,
            )
        except Exception as e:
            await cls._record_usage(
                db=db,
                user_id=user_id,
                conversation_id=conversation.id,
                character_id=character.id,
                message_id=user_message.id,
                model=AiTavernConfig.deepseek_model,
                usage=None,
                latency_ms=None,
                request_type='chat',
                success=False,
                error_message=str(e),
            )
            await db.commit()
            raise

        conversation.total_turn_count = (conversation.total_turn_count or 0) + 1
        conversation.summary_turn_count = (conversation.summary_turn_count or 0) + 1
        conversation.total_message_count = (conversation.total_message_count or 0) + 2
        conversation.update_time = datetime.now()

        summary_triggered = False
        if AiTavernConfig.ai_enable_summary and conversation.summary_turn_count >= AiTavernConfig.ai_summary_every_n_turns:
            summary_triggered = True
            try:
                await cls.update_summary(db, user_id, conversation.id)
            except Exception as e:
                conversation.summary_status = 'failed'
                await cls._create_summary_log(
                    db=db,
                    user_id=user_id,
                    conversation=conversation,
                    messages=[],
                    old_summary=conversation.summary,
                    new_summary=None,
                    usage=None,
                    success=False,
                    error_message=str(e),
                )

        await db.commit()
        assistant_payload = CamelCaseUtil.transform_result(assistant_message)
        assistant_payload['latencyMs'] = result['latency_ms']
        return {
            'message': assistant_payload,
            'userMessage': CamelCaseUtil.transform_result(user_message),
            'summaryTriggered': summary_triggered,
        }

    @classmethod
    async def update_summary(cls, db: AsyncSession, user_id: int, conversation_id: int) -> str | None:
        conversation = await TavernDao.get_user_conversation(db, user_id, conversation_id)
        if not conversation:
            raise ServiceException(message='会话不存在或无权限访问')
        messages = await TavernDao.messages_after_id(db, conversation_id, conversation.last_summarized_message_id)
        if not messages:
            return conversation.summary

        old_summary = conversation.summary
        conversation.summary_status = 'running'
        summary_messages = build_summary_prompt(old_summary or '', cls._format_messages_for_summary(messages))
        result = await DeepSeekProvider.chat(messages=summary_messages, user_id=str(user_id), request_type='summary')
        new_summary = result['content']
        conversation.summary = new_summary
        conversation.summary_version = (conversation.summary_version or 0) + 1
        conversation.summary_turn_count = 0
        conversation.last_summarized_message_id = messages[-1].id
        conversation.last_summary_time = datetime.now()
        conversation.summary_status = 'idle'
        conversation.update_time = datetime.now()

        await cls._create_summary_log(
            db=db,
            user_id=user_id,
            conversation=conversation,
            messages=messages,
            old_summary=old_summary,
            new_summary=new_summary,
            usage=result['usage'],
            success=True,
        )
        await cls._record_usage(
            db=db,
            user_id=user_id,
            conversation_id=conversation.id,
            character_id=conversation.character_id,
            message_id=None,
            model=result['model'],
            usage=result['usage'],
            latency_ms=result['latency_ms'],
            request_type='summary',
            request_id=result.get('request_id'),
            success=True,
        )
        return new_summary

    @classmethod
    async def list_token_usage(cls, db: AsyncSession, query: TokenUsageQueryModel) -> PageModel:
        return await TavernDao.list_token_usage(db, query, is_page=True)

    @classmethod
    async def list_summary_logs(cls, db: AsyncSession, page_num: int, page_size: int) -> PageModel:
        return await TavernDao.list_summary_logs(db, page_num, page_size, is_page=True)

    @classmethod
    async def dashboard(cls, db: AsyncSession) -> dict[str, Any]:
        return await TavernDao.dashboard(db)

    @classmethod
    async def list_user_token_settings(cls, db: AsyncSession, query: UserTokenSettingQueryModel) -> PageModel:
        return await TavernDao.list_user_token_settings(db, query, is_page=True)

    @classmethod
    async def save_user_token_setting(cls, db: AsyncSession, data: UserTokenSettingUpdateModel) -> CrudResponseModel:
        setting = await TavernDao.get_user_token_setting(db, data.user_id)
        if not setting:
            setting = SysUserTokenSetting(
                user_id=data.user_id,
                create_time=datetime.now(),
            )
        setting.daily_cost_limit_yuan = data.daily_cost_limit_yuan or Decimal('0')
        setting.monthly_cost_limit_yuan = data.monthly_cost_limit_yuan or Decimal('0')
        setting.total_cost_limit_yuan = data.total_cost_limit_yuan or Decimal('0')
        setting.enabled = True if data.enabled is None else data.enabled
        setting.remark = data.remark
        setting.update_time = datetime.now()
        await TavernDao.save_user_token_setting(db, setting)
        await db.commit()
        return CrudResponseModel(is_success=True, message='保存成功')

    @classmethod
    async def _create_message(
        cls, db: AsyncSession, conversation: AiConversation, role: str, content: str
    ) -> AiMessage:
        seq = await TavernDao.get_next_message_seq(db, conversation.id)
        message = AiMessage(
            conversation_id=conversation.id,
            user_id=conversation.user_id,
            character_id=conversation.character_id,
            role=role,
            content=content,
            seq_no=seq,
            create_time=datetime.now(),
        )
        return await TavernDao.add_message(db, message)

    @classmethod
    async def _assert_user_token_quota(cls, db: AsyncSession, user_id: int) -> None:
        setting = await TavernDao.get_user_token_setting(db, user_id)
        if not setting or not setting.enabled:
            return

        today = datetime.combine(datetime.now().date(), time(0, 0, 0))
        month = datetime.combine(datetime.now().date().replace(day=1), time(0, 0, 0))
        quota_checks = [
            ('今日', setting.daily_cost_limit_yuan, await TavernDao.user_cost_usage_sum(db, user_id, today)),
            ('本月', setting.monthly_cost_limit_yuan, await TavernDao.user_cost_usage_sum(db, user_id, month)),
            ('累计', setting.total_cost_limit_yuan, await TavernDao.user_cost_usage_sum(db, user_id)),
        ]
        for label, limit, used in quota_checks:
            if limit and Decimal(str(limit)) > 0 and Decimal(str(used)) >= Decimal(str(limit)):
                raise ServiceException(message=f'{label}人民币额度已用完，请联系管理员调整用户Token设置')

    @classmethod
    async def _build_chat_messages(
        cls, db: AsyncSession, conversation: AiConversation, character: AiCharacter, user_input: str
    ) -> list[dict[str, str]]:
        messages = [{'role': 'system', 'content': build_character_system_prompt(character)}]
        if conversation.summary:
            messages.append({'role': 'system', 'content': f'【长期剧情摘要】\n{conversation.summary}'})
        recent = await TavernDao.recent_messages(db, conversation.id, AiTavernConfig.ai_recent_message_limit)
        messages.extend({'role': msg.role, 'content': msg.content} for msg in recent if msg.role in {'user', 'assistant'})
        messages.append({'role': 'user', 'content': user_input})
        return messages

    @classmethod
    async def _record_usage(  # noqa: PLR0913
        cls,
        db: AsyncSession,
        user_id: int,
        conversation_id: int | None,
        character_id: int | None,
        message_id: int | None,
        model: str,
        usage: Any,
        latency_ms: int | None,
        request_type: str,
        request_id: str | None = None,
        success: bool = True,
        error_message: str | None = None,
    ) -> AiTokenUsage:
        prompt_tokens = UsageParser.get(usage, 'prompt_tokens')
        completion_tokens = UsageParser.get(usage, 'completion_tokens')
        total_tokens = UsageParser.get(usage, 'total_tokens')
        hit_tokens = UsageParser.get(usage, 'prompt_cache_hit_tokens')
        miss_tokens = UsageParser.get(usage, 'prompt_cache_miss_tokens', prompt_tokens - hit_tokens)
        reasoning_tokens = UsageParser.reasoning_tokens(usage)
        estimated_cost = TokenCost.estimate_yuan(hit_tokens, miss_tokens, completion_tokens)
        token_usage = AiTokenUsage(
            user_id=user_id,
            conversation_id=conversation_id,
            character_id=character_id,
            message_id=message_id,
            model=model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            reasoning_tokens=reasoning_tokens,
            cached_tokens=hit_tokens,
            prompt_cache_hit_tokens=hit_tokens,
            prompt_cache_miss_tokens=miss_tokens,
            estimated_cost_yuan=str(estimated_cost),
            request_type=request_type,
            request_id=request_id,
            latency_ms=latency_ms,
            success=success,
            error_message=error_message,
            create_time=datetime.now(),
        )
        if message_id:
            await db.execute(
                update(AiMessage)
                .where(AiMessage.id == message_id)
                .values(
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                    total_tokens=total_tokens,
                )
            )
        return await TavernDao.add_token_usage(db, token_usage)

    @classmethod
    async def _create_summary_log(
        cls,
        db: AsyncSession,
        user_id: int,
        conversation: AiConversation,
        messages: list[AiMessage],
        old_summary: str | None,
        new_summary: str | None,
        usage: Any,
        success: bool,
        error_message: str | None = None,
    ) -> AiSummaryLog:
        log = AiSummaryLog(
            user_id=user_id,
            conversation_id=conversation.id,
            character_id=conversation.character_id,
            old_summary=old_summary,
            new_summary=new_summary,
            start_message_id=messages[0].id if messages else None,
            end_message_id=messages[-1].id if messages else None,
            message_count=len(messages),
            model=AiTavernConfig.deepseek_model,
            prompt_tokens=UsageParser.get(usage, 'prompt_tokens'),
            completion_tokens=UsageParser.get(usage, 'completion_tokens'),
            total_tokens=UsageParser.get(usage, 'total_tokens'),
            success=success,
            error_message=error_message,
            create_time=datetime.now(),
        )
        return await TavernDao.add_summary_log(db, log)

    @classmethod
    def _format_messages_for_summary(cls, messages: list[AiMessage]) -> str:
        lines = []
        for msg in messages:
            speaker = '用户' if msg.role == 'user' else '角色' if msg.role == 'assistant' else msg.role
            lines.append(f'{speaker}：{msg.content}')
        return '\n'.join(lines)
