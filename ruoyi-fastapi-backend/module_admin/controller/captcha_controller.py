from fastapi import Request, Response

from common.enums import RedisInitKeyConfig
from common.router import APIRouterPro
from common.vo import DynamicResponseModel
from module_admin.entity.vo.login_vo import CaptchaCode
from utils.response_util import ResponseUtil

captcha_controller = APIRouterPro(order_num=2, tags=['验证码模块'])


@captcha_controller.get(
    '/captchaImage',
    summary='获取图片验证码接口',
    description='用于获取图片验证码',
    response_model=DynamicResponseModel[CaptchaCode],
)
async def get_captcha_image(request: Request) -> Response:
    register_enabled = (
        await request.app.state.redis.get(f'{RedisInitKeyConfig.SYS_CONFIG.key}:sys.account.registerUser') == 'true'
    )

    return ResponseUtil.success(
        model_content=CaptchaCode(
            captchaEnabled=False, registerEnabled=register_enabled, img='', uuid=''
        )
    )
