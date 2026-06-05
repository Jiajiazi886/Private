from datetime import datetime, time
from typing import Any

from sqlalchemy import Select, case, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from common.vo import PageModel
from module_admin.entity.do.user_do import SysUser
from module_ai_tavern.entity.do.tavern_do import (
    AiCharacter,
    AiConversation,
    AiMessage,
    AiSummaryLog,
    AiTokenUsage,
    SysUserTokenSetting,
)
from module_ai_tavern.entity.vo.tavern_vo import (
    CharacterQueryModel,
    ConversationQueryModel,
    MessageQueryModel,
    TokenUsageQueryModel,
    UserTokenSettingQueryModel,
)
from utils.common_util import CamelCaseUtil
from utils.page_util import PageUtil


class TavernDao:
    @classmethod
    async def paginate(cls, db: AsyncSession, query: Select, page_num: int, page_size: int) -> PageModel:
        return await PageUtil.paginate(db, query, page_num, page_size, is_page=True)

    @classmethod
    async def get_character(cls, db: AsyncSession, character_id: int) -> AiCharacter | None:
        return (await db.execute(select(AiCharacter).where(AiCharacter.id == character_id))).scalars().first()

    @classmethod
    async def list_characters(cls, db: AsyncSession, query_object: CharacterQueryModel, is_page: bool = True) -> Any:
        query = (
            select(AiCharacter)
            .where(
                AiCharacter.user_id == query_object.user_id if query_object.user_id else True,
                AiCharacter.name.like(f'%{query_object.name}%') if query_object.name else True,
                AiCharacter.status == query_object.status if query_object.status else True,
            )
            .order_by(AiCharacter.update_time.desc(), AiCharacter.id.desc())
        )
        return await PageUtil.paginate(db, query, query_object.page_num, query_object.page_size, is_page)

    @classmethod
    async def add_character(cls, db: AsyncSession, character: AiCharacter) -> AiCharacter:
        db.add(character)
        await db.flush()
        return character

    @classmethod
    async def delete_character(cls, db: AsyncSession, character_id: int, user_id: int | None = None) -> None:
        await db.execute(
            update(AiCharacter)
            .where(AiCharacter.id == character_id, AiCharacter.user_id == user_id if user_id else True)
            .values(status='1', update_time=datetime.now())
        )

    @classmethod
    async def get_conversation(cls, db: AsyncSession, conversation_id: int) -> AiConversation | None:
        return (await db.execute(select(AiConversation).where(AiConversation.id == conversation_id))).scalars().first()

    @classmethod
    async def get_user_conversation(
        cls, db: AsyncSession, user_id: int, conversation_id: int
    ) -> AiConversation | None:
        return (
            (
                await db.execute(
                    select(AiConversation).where(
                        AiConversation.id == conversation_id,
                        AiConversation.user_id == user_id,
                        AiConversation.status == '0',
                    )
                )
            )
            .scalars()
            .first()
        )

    @classmethod
    async def list_conversations(
        cls, db: AsyncSession, query_object: ConversationQueryModel, is_page: bool = True
    ) -> Any:
        query = (
            select(AiConversation, AiCharacter.name.label('character_name'))
            .join(AiCharacter, AiConversation.character_id == AiCharacter.id)
            .where(
                AiConversation.user_id == query_object.user_id if query_object.user_id else True,
                AiConversation.character_id == query_object.character_id if query_object.character_id else True,
                AiConversation.title.like(f'%{query_object.title}%') if query_object.title else True,
                AiConversation.status == query_object.status if query_object.status else True,
            )
            .order_by(AiConversation.update_time.desc(), AiConversation.id.desc())
        )
        return await cls.paginate_joined(db, query, query_object.page_num, query_object.page_size, is_page)

    @classmethod
    async def add_conversation(cls, db: AsyncSession, conversation: AiConversation) -> AiConversation:
        db.add(conversation)
        await db.flush()
        return conversation

    @classmethod
    async def get_user_message(cls, db: AsyncSession, user_id: int, message_id: int) -> AiMessage | None:
        return (
            (
                await db.execute(
                    select(AiMessage).where(
                        AiMessage.id == message_id,
                        AiMessage.user_id == user_id,
                    )
                )
            )
            .scalars()
            .first()
        )

    @classmethod
    async def delete_conversation(cls, db: AsyncSession, conversation_id: int, user_id: int | None = None) -> None:
        await db.execute(
            update(AiConversation)
            .where(AiConversation.id == conversation_id, AiConversation.user_id == user_id if user_id else True)
            .values(status='1', update_time=datetime.now())
        )

    @classmethod
    async def get_next_message_seq(cls, db: AsyncSession, conversation_id: int) -> int:
        current = (
            await db.execute(select(func.coalesce(func.max(AiMessage.seq_no), 0)).where(AiMessage.conversation_id == conversation_id))
        ).scalar()
        return int(current or 0) + 1

    @classmethod
    async def add_message(cls, db: AsyncSession, message: AiMessage) -> AiMessage:
        db.add(message)
        await db.flush()
        return message

    @classmethod
    async def list_messages(cls, db: AsyncSession, query_object: MessageQueryModel, is_page: bool = True) -> Any:
        query = (
            select(AiMessage)
            .where(
                AiMessage.user_id == query_object.user_id if query_object.user_id else True,
                AiMessage.conversation_id == query_object.conversation_id if query_object.conversation_id else True,
                AiMessage.character_id == query_object.character_id if query_object.character_id else True,
                AiMessage.role == query_object.role if query_object.role else True,
            )
            .order_by(AiMessage.conversation_id.desc(), AiMessage.seq_no.asc(), AiMessage.id.asc())
        )
        return await PageUtil.paginate(db, query, query_object.page_num, query_object.page_size, is_page)

    @classmethod
    async def recent_messages(cls, db: AsyncSession, conversation_id: int, limit: int) -> list[AiMessage]:
        rows = (
            (
                await db.execute(
                    select(AiMessage)
                    .where(AiMessage.conversation_id == conversation_id)
                    .order_by(AiMessage.seq_no.desc(), AiMessage.id.desc())
                    .limit(limit)
                )
            )
            .scalars()
            .all()
        )
        return list(reversed(rows))

    @classmethod
    async def messages_after_id(
        cls, db: AsyncSession, conversation_id: int, after_id: int | None
    ) -> list[AiMessage]:
        query = select(AiMessage).where(AiMessage.conversation_id == conversation_id)
        if after_id:
            query = query.where(AiMessage.id > after_id)
        return list((await db.execute(query.order_by(AiMessage.seq_no.asc(), AiMessage.id.asc()))).scalars().all())

    @classmethod
    async def message_latency_map(cls, db: AsyncSession, message_ids: list[int]) -> dict[int, int]:
        if not message_ids:
            return {}
        rows = (
            await db.execute(
                select(AiTokenUsage.message_id, AiTokenUsage.latency_ms).where(
                    AiTokenUsage.message_id.in_(message_ids),
                    AiTokenUsage.success.is_(True),
                )
            )
        ).all()
        return {int(message_id): int(latency_ms) for message_id, latency_ms in rows if message_id and latency_ms}

    @classmethod
    async def add_token_usage(cls, db: AsyncSession, usage: AiTokenUsage) -> AiTokenUsage:
        db.add(usage)
        await db.flush()
        return usage

    @classmethod
    async def list_token_usage(cls, db: AsyncSession, query_object: TokenUsageQueryModel, is_page: bool = True) -> Any:
        query = (
            select(AiTokenUsage, SysUser.user_name, SysUser.nick_name)
            .outerjoin(SysUser, AiTokenUsage.user_id == SysUser.user_id)
            .where(
                AiTokenUsage.user_id == query_object.user_id if query_object.user_id else True,
                AiTokenUsage.model == query_object.model if query_object.model else True,
                AiTokenUsage.request_type == query_object.request_type if query_object.request_type else True,
                AiTokenUsage.success == query_object.success if query_object.success is not None else True,
                AiTokenUsage.create_time.between(
                    datetime.combine(datetime.strptime(query_object.begin_time, '%Y-%m-%d'), time(0, 0, 0)),
                    datetime.combine(datetime.strptime(query_object.end_time, '%Y-%m-%d'), time(23, 59, 59)),
                )
                if query_object.begin_time and query_object.end_time
                else True,
            )
            .order_by(AiTokenUsage.create_time.desc(), AiTokenUsage.id.desc())
        )
        return await cls.paginate_joined(db, query, query_object.page_num, query_object.page_size, is_page)

    @classmethod
    async def add_summary_log(cls, db: AsyncSession, log: AiSummaryLog) -> AiSummaryLog:
        db.add(log)
        await db.flush()
        return log

    @classmethod
    async def list_summary_logs(cls, db: AsyncSession, page_num: int, page_size: int, is_page: bool = True) -> Any:
        query = select(AiSummaryLog).order_by(AiSummaryLog.create_time.desc(), AiSummaryLog.id.desc())
        return await PageUtil.paginate(db, query, page_num, page_size, is_page)

    @classmethod
    async def get_user_token_setting(cls, db: AsyncSession, user_id: int) -> SysUserTokenSetting | None:
        return (
            await db.execute(select(SysUserTokenSetting).where(SysUserTokenSetting.user_id == user_id))
        ).scalars().first()

    @classmethod
    async def save_user_token_setting(
        cls,
        db: AsyncSession,
        setting: SysUserTokenSetting,
    ) -> SysUserTokenSetting:
        db.add(setting)
        await db.flush()
        return setting

    @classmethod
    async def user_token_usage_sum(cls, db: AsyncSession, user_id: int, begin_time: datetime | None = None) -> int:
        query = select(func.coalesce(func.sum(AiTokenUsage.total_tokens), 0)).where(
            AiTokenUsage.user_id == user_id,
            AiTokenUsage.success.is_(True),
        )
        if begin_time:
            query = query.where(AiTokenUsage.create_time >= begin_time)
        return int((await db.execute(query)).scalar() or 0)

    @classmethod
    async def user_cost_usage_sum(cls, db: AsyncSession, user_id: int, begin_time: datetime | None = None) -> Any:
        query = select(func.coalesce(func.sum(AiTokenUsage.estimated_cost_yuan), 0)).where(
            AiTokenUsage.user_id == user_id,
            AiTokenUsage.success.is_(True),
        )
        if begin_time:
            query = query.where(AiTokenUsage.create_time >= begin_time)
        return (await db.execute(query)).scalar() or 0

    @classmethod
    async def list_user_token_settings(
        cls, db: AsyncSession, query_object: UserTokenSettingQueryModel, is_page: bool = True
    ) -> PageModel:
        today = datetime.combine(datetime.now().date(), time(0, 0, 0))
        month = datetime.combine(datetime.now().date().replace(day=1), time(0, 0, 0))
        base_query = (
            select(
                SysUser.user_id,
                SysUser.user_name,
                SysUser.nick_name,
                SysUserTokenSetting.id,
                SysUserTokenSetting.daily_token_limit,
                SysUserTokenSetting.monthly_token_limit,
                SysUserTokenSetting.total_token_limit,
                SysUserTokenSetting.daily_cost_limit_yuan,
                SysUserTokenSetting.monthly_cost_limit_yuan,
                SysUserTokenSetting.total_cost_limit_yuan,
                SysUserTokenSetting.enabled,
                SysUserTokenSetting.create_time,
                SysUserTokenSetting.update_time,
                SysUserTokenSetting.remark,
                func.coalesce(
                    func.sum(case((AiTokenUsage.success.is_(True), AiTokenUsage.total_tokens), else_=0)),
                    0,
                ).label('used_total_tokens'),
                func.coalesce(
                    func.sum(case((AiTokenUsage.success.is_(True), AiTokenUsage.estimated_cost_yuan), else_=0)),
                    0,
                ).label('used_total_cost_yuan'),
                func.coalesce(
                    func.sum(
                        case(
                            (
                                (AiTokenUsage.success.is_(True)) & (AiTokenUsage.create_time >= today),
                                AiTokenUsage.total_tokens,
                            ),
                            else_=0,
                        )
                    ),
                    0,
                ).label('used_today_tokens'),
                func.coalesce(
                    func.sum(
                        case(
                            (
                                (AiTokenUsage.success.is_(True)) & (AiTokenUsage.create_time >= today),
                                AiTokenUsage.estimated_cost_yuan,
                            ),
                            else_=0,
                        )
                    ),
                    0,
                ).label('used_today_cost_yuan'),
                func.coalesce(
                    func.sum(
                        case(
                            (
                                (AiTokenUsage.success.is_(True)) & (AiTokenUsage.create_time >= month),
                                AiTokenUsage.total_tokens,
                            ),
                            else_=0,
                        )
                    ),
                    0,
                ).label('used_month_tokens'),
                func.coalesce(
                    func.sum(
                        case(
                            (
                                (AiTokenUsage.success.is_(True)) & (AiTokenUsage.create_time >= month),
                                AiTokenUsage.estimated_cost_yuan,
                            ),
                            else_=0,
                        )
                    ),
                    0,
                ).label('used_month_cost_yuan'),
            )
            .select_from(SysUser)
            .outerjoin(SysUserTokenSetting, SysUser.user_id == SysUserTokenSetting.user_id)
            .outerjoin(AiTokenUsage, SysUser.user_id == AiTokenUsage.user_id)
            .where(
                SysUser.del_flag == '0',
                SysUser.user_id == query_object.user_id if query_object.user_id else True,
                SysUser.user_name.like(f'%{query_object.user_name}%') if query_object.user_name else True,
                SysUser.nick_name.like(f'%{query_object.nick_name}%') if query_object.nick_name else True,
                SysUserTokenSetting.enabled == query_object.enabled if query_object.enabled is not None else True,
            )
            .group_by(
                SysUser.user_id,
                SysUser.user_name,
                SysUser.nick_name,
                SysUserTokenSetting.id,
                SysUserTokenSetting.daily_token_limit,
                SysUserTokenSetting.monthly_token_limit,
                SysUserTokenSetting.total_token_limit,
                SysUserTokenSetting.daily_cost_limit_yuan,
                SysUserTokenSetting.monthly_cost_limit_yuan,
                SysUserTokenSetting.total_cost_limit_yuan,
                SysUserTokenSetting.enabled,
                SysUserTokenSetting.create_time,
                SysUserTokenSetting.update_time,
                SysUserTokenSetting.remark,
            )
            .order_by(SysUser.user_id.asc())
        )
        total = (await db.execute(select(func.count('*')).select_from(base_query.subquery()))).scalar() or 0
        if is_page:
            base_query = base_query.offset((query_object.page_num - 1) * query_object.page_size).limit(query_object.page_size)
        rows = (await db.execute(base_query)).mappings().all()
        return PageModel[Any](
            rows=[CamelCaseUtil.transform_result(dict(row)) for row in rows],
            pageNum=query_object.page_num,
            pageSize=query_object.page_size,
            total=total,
            hasNext=(total + query_object.page_size - 1) // query_object.page_size > query_object.page_num,
        )

    @classmethod
    async def dashboard(cls, db: AsyncSession) -> dict[str, Any]:
        today = datetime.combine(datetime.now().date(), time(0, 0, 0))
        total_users = (await db.execute(select(func.count(func.distinct(AiTokenUsage.user_id))))).scalar() or 0
        total_characters = (await db.execute(select(func.count()).select_from(AiCharacter))).scalar() or 0
        total_conversations = (await db.execute(select(func.count()).select_from(AiConversation))).scalar() or 0
        total_messages = (await db.execute(select(func.count()).select_from(AiMessage))).scalar() or 0
        token_sums = (
            await db.execute(
                select(
                    func.coalesce(func.sum(AiTokenUsage.total_tokens), 0),
                    func.coalesce(func.sum(AiTokenUsage.prompt_tokens), 0),
                    func.coalesce(func.sum(AiTokenUsage.completion_tokens), 0),
                    func.coalesce(func.sum(AiTokenUsage.estimated_cost_yuan), 0),
                )
            )
        ).first()
        today_tokens = (
            await db.execute(
                select(func.coalesce(func.sum(AiTokenUsage.total_tokens), 0)).where(AiTokenUsage.create_time >= today)
            )
        ).scalar() or 0
        failed_requests = (
            await db.execute(select(func.count()).select_from(AiTokenUsage).where(AiTokenUsage.success.is_(False)))
        ).scalar() or 0
        return {
            'totalUsers': total_users,
            'totalCharacters': total_characters,
            'totalConversations': total_conversations,
            'totalMessages': total_messages,
            'totalTokens': int(token_sums[0] or 0),
            'promptTokens': int(token_sums[1] or 0),
            'completionTokens': int(token_sums[2] or 0),
            'estimatedCostYuan': str(token_sums[3] or 0),
            'todayTokens': int(today_tokens),
            'failedRequests': int(failed_requests),
        }

    @classmethod
    async def paginate_joined(
        cls, db: AsyncSession, query: Select, page_num: int, page_size: int, is_page: bool = True
    ) -> Any:
        async def rows_to_dicts(rows: list[Any]) -> list[dict[str, Any]]:
            result = []
            for row in rows:
                item: dict[str, Any] = {}
                for key, value in row._mapping.items():
                    if hasattr(value, '__table__'):
                        item.update(CamelCaseUtil.transform_result(value))
                        continue
                    if isinstance(key, str) and not hasattr(value, '__table__'):
                        item[CamelCaseUtil.snake_to_camel(key)] = value
                result.append(item)
            return result

        if not is_page:
            return await rows_to_dicts((await db.execute(query)).all())

        total = (await db.execute(select(func.count('*')).select_from(query.subquery()))).scalar() or 0
        rows = (await db.execute(query.offset((page_num - 1) * page_size).limit(page_size))).all()
        return PageModel[Any](
            rows=await rows_to_dicts(rows),
            pageNum=page_num,
            pageSize=page_size,
            total=total,
            hasNext=(total + page_size - 1) // page_size > page_num,
        )
