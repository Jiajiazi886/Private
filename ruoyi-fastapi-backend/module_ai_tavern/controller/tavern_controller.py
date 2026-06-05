from typing import Annotated

from fastapi import Path, Query, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession

from common.aspect.db_seesion import DBSessionDependency
from common.aspect.interface_auth import UserInterfaceAuthDependency
from common.aspect.pre_auth import CurrentUserDependency, PreAuthDependency
from common.router import APIRouterPro
from common.vo import DataResponseModel, PageResponseModel, ResponseBaseModel
from module_admin.entity.vo.user_vo import CurrentUserModel
from module_ai_tavern.entity.vo.tavern_vo import (
    CharacterModel,
    CharacterQueryModel,
    ChatSendModel,
    ConversationCreateModel,
    ConversationQueryModel,
    ConversationUpdateModel,
    MessageUpdateModel,
    MessageQueryModel,
    SummaryLogModel,
    TokenUsageModel,
    TokenUsageQueryModel,
    UserTokenSettingModel,
    UserTokenSettingQueryModel,
    UserTokenSettingUpdateModel,
)
from module_ai_tavern.service.tavern_service import TavernService
from utils.response_util import ResponseUtil

tavern_controller = APIRouterPro(
    prefix='/ai/tavern', order_num=30, tags=['AI酒馆'], dependencies=[PreAuthDependency()]
)


@tavern_controller.post('/characters', summary='创建AI角色', response_model=DataResponseModel[CharacterModel])
async def create_character(
    request: Request,
    data: CharacterModel,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
) -> Response:
    result = await TavernService.create_character(query_db, current_user.user.user_id, data)
    return ResponseUtil.success(data=result)


@tavern_controller.get('/characters', summary='获取AI角色列表', response_model=PageResponseModel[CharacterModel])
async def list_characters(
    request: Request,
    query: Annotated[CharacterQueryModel, Query()],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
) -> Response:
    result = await TavernService.list_characters(query_db, query, current_user.user.user_id)
    return ResponseUtil.success(model_content=result)


@tavern_controller.get('/characters/{character_id}', summary='获取AI角色详情', response_model=DataResponseModel[CharacterModel])
async def get_character(
    request: Request,
    character_id: Annotated[int, Path()],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
) -> Response:
    result = await TavernService.get_character_detail(query_db, current_user.user.user_id, character_id)
    return ResponseUtil.success(data=result)


@tavern_controller.put('/characters/{character_id}', summary='更新AI角色', response_model=ResponseBaseModel)
async def update_character(
    request: Request,
    character_id: Annotated[int, Path()],
    data: CharacterModel,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
) -> Response:
    result = await TavernService.update_character(query_db, current_user.user.user_id, character_id, data)
    return ResponseUtil.success(msg=result.message)


@tavern_controller.delete('/characters/{character_id}', summary='删除AI角色', response_model=ResponseBaseModel)
async def delete_character(
    request: Request,
    character_id: Annotated[int, Path()],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
) -> Response:
    result = await TavernService.delete_character(query_db, current_user.user.user_id, character_id)
    return ResponseUtil.success(msg=result.message)


@tavern_controller.post('/conversations', summary='创建会话', response_model=DataResponseModel[dict])
async def create_conversation(
    request: Request,
    data: ConversationCreateModel,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
) -> Response:
    result = await TavernService.create_conversation(query_db, current_user.user.user_id, data)
    return ResponseUtil.success(data=result)


@tavern_controller.get('/conversations', summary='获取会话列表')
async def list_conversations(
    request: Request,
    query: Annotated[ConversationQueryModel, Query()],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
) -> Response:
    result = await TavernService.list_conversations(query_db, query, current_user.user.user_id)
    return ResponseUtil.success(model_content=result)


@tavern_controller.delete('/conversations/{conversation_id}', summary='删除会话', response_model=ResponseBaseModel)
async def delete_conversation(
    request: Request,
    conversation_id: Annotated[int, Path()],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
) -> Response:
    result = await TavernService.delete_conversation(query_db, current_user.user.user_id, conversation_id)
    return ResponseUtil.success(msg=result.message)


@tavern_controller.get('/conversations/{conversation_id}', summary='获取会话详情')
async def get_conversation(
    request: Request,
    conversation_id: Annotated[int, Path()],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
) -> Response:
    result = await TavernService.get_conversation_detail(query_db, current_user.user.user_id, conversation_id)
    return ResponseUtil.success(data=result)


@tavern_controller.put('/conversations/{conversation_id}', summary='更新会话设置', response_model=ResponseBaseModel)
async def update_conversation(
    request: Request,
    conversation_id: Annotated[int, Path()],
    data: ConversationUpdateModel,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
) -> Response:
    result = await TavernService.update_conversation(query_db, current_user.user.user_id, conversation_id, data)
    return ResponseUtil.success(msg=result.message)


@tavern_controller.get('/conversations/{conversation_id}/messages', summary='获取会话消息')
async def get_messages(
    request: Request,
    conversation_id: Annotated[int, Path()],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
) -> Response:
    result = await TavernService.get_conversation_messages(query_db, current_user.user.user_id, conversation_id)
    return ResponseUtil.success(data=result)


@tavern_controller.put('/messages/{message_id}', summary='编辑会话消息')
async def update_message(
    request: Request,
    message_id: Annotated[int, Path()],
    data: MessageUpdateModel,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
) -> Response:
    result = await TavernService.update_message(query_db, current_user.user.user_id, message_id, data)
    return ResponseUtil.success(data=result)


@tavern_controller.post('/chat/send', summary='发送角色聊天消息')
async def send_chat(
    request: Request,
    data: ChatSendModel,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
) -> Response:
    result = await TavernService.send_chat(query_db, current_user.user.user_id, data)
    return ResponseUtil.success(data=result)


@tavern_controller.post('/conversations/{conversation_id}/summary/rebuild', summary='重建会话摘要')
async def rebuild_summary(
    request: Request,
    conversation_id: Annotated[int, Path()],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
) -> Response:
    result = await TavernService.update_summary(query_db, current_user.user.user_id, conversation_id)
    await query_db.commit()
    return ResponseUtil.success(data={'summary': result})


admin_tavern_controller = APIRouterPro(
    prefix='/admin/ai/tavern', order_num=31, tags=['AI酒馆管理'], dependencies=[PreAuthDependency()]
)


@admin_tavern_controller.get('/dashboard', summary='AI酒馆仪表盘')
async def admin_dashboard(
    request: Request,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    result = await TavernService.dashboard(query_db)
    return ResponseUtil.success(data=result)


@admin_tavern_controller.get('/characters', summary='管理员角色列表', response_model=PageResponseModel[CharacterModel])
async def admin_list_characters(
    request: Request,
    query: Annotated[CharacterQueryModel, Query()],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    result = await TavernService.list_characters(query_db, query)
    return ResponseUtil.success(model_content=result)


@admin_tavern_controller.get('/conversations', summary='管理员会话列表')
async def admin_list_conversations(
    request: Request,
    query: Annotated[ConversationQueryModel, Query()],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    result = await TavernService.list_conversations(query_db, query)
    return ResponseUtil.success(model_content=result)


@admin_tavern_controller.get('/messages', summary='管理员消息查询')
async def admin_list_messages(
    request: Request,
    query: Annotated[MessageQueryModel, Query()],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    result = await TavernService.list_messages(query_db, query)
    return ResponseUtil.success(model_content=result)


@admin_tavern_controller.get('/token-usage', summary='管理员Token消耗查询', response_model=PageResponseModel[TokenUsageModel])
async def admin_token_usage(
    request: Request,
    query: Annotated[TokenUsageQueryModel, Query()],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    result = await TavernService.list_token_usage(query_db, query)
    return ResponseUtil.success(model_content=result)


@admin_tavern_controller.get('/summary-logs', summary='管理员摘要日志查询', response_model=PageResponseModel[SummaryLogModel])
async def admin_summary_logs(
    request: Request,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    page_num: int = Query(default=1, alias='pageNum'),
    page_size: int = Query(default=10, alias='pageSize'),
) -> Response:
    result = await TavernService.list_summary_logs(query_db, page_num, page_size)
    return ResponseUtil.success(model_content=result)


user_token_setting_controller = APIRouterPro(
    prefix='/system/user-token-setting',
    order_num=32,
    tags=['系统管理-用户Token设置'],
    dependencies=[PreAuthDependency()],
)


@user_token_setting_controller.get(
    '/list',
    summary='用户Token设置列表',
    response_model=PageResponseModel[UserTokenSettingModel],
    dependencies=[UserInterfaceAuthDependency('system:userToken:list')],
)
async def list_user_token_settings(
    request: Request,
    query: Annotated[UserTokenSettingQueryModel, Query()],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    result = await TavernService.list_user_token_settings(query_db, query)
    return ResponseUtil.success(model_content=result)


@user_token_setting_controller.put(
    '',
    summary='保存用户Token设置',
    response_model=ResponseBaseModel,
    dependencies=[UserInterfaceAuthDependency('system:userToken:edit')],
)
async def save_user_token_setting(
    request: Request,
    data: UserTokenSettingUpdateModel,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    result = await TavernService.save_user_token_setting(query_db, data)
    return ResponseUtil.success(msg=result.message)
