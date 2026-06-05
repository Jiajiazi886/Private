from collections.abc import AsyncGenerator

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from config.database import AsyncSessionLocal, Base, async_engine
from utils.log_util import logger


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    每一个请求处理完毕后会关闭当前连接，不同的请求使用不同的连接

    :return:
    """
    async with AsyncSessionLocal() as current_db:
        yield current_db


async def init_create_table() -> None:
    """
    应用启动时初始化数据库连接

    :return:
    """
    logger.info('🔎 初始化数据库连接...')
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await _ensure_ai_tavern_columns(conn)
    logger.info('✅️ 数据库连接成功')


async def _ensure_ai_tavern_columns(conn) -> None:
    """Small compatibility migration for existing AI Tavern databases."""
    statements = [
        "ALTER TABLE ai_conversation ADD COLUMN conversation_prompt LONGTEXT NULL COMMENT 'conversation prompt' AFTER summary",
        "ALTER TABLE ai_conversation ADD COLUMN forced_memory LONGTEXT NULL COMMENT 'forced memory' AFTER conversation_prompt",
        "ALTER TABLE ai_message ADD COLUMN is_edited TINYINT(1) DEFAULT 0 COMMENT 'message edited flag' AFTER voice_profile_id",
        "ALTER TABLE ai_message ADD COLUMN update_time DATETIME NULL COMMENT 'message update time' AFTER create_time",
    ]
    for statement in statements:
        try:
            await conn.execute(text(statement))
        except SQLAlchemyError as exc:
            message = str(exc).lower()
            if 'duplicate column' in message or 'already exists' in message:
                continue
            logger.warning(f'AI酒馆兼容字段初始化跳过：{exc}')


async def close_async_engine() -> None:
    """
    应用关闭时释放数据库连接池

    :return:
    """
    await async_engine.dispose()
