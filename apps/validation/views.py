from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import View
from validation.libs.captcha.captcha import captcha
from django_redis import get_redis_connection
from ltmall.settings import const


class ImageCodeView(View):
    """图形验证码逻辑"""

    def get(self, request, uuid):
        """
        :param request: 请求对象
        :param uuid: 通用唯一识别符, 用于标识图片验证码属于哪个用户
        :return: image/jpeg 或 image/png
        """
        # 生成图片验证码
        text, image = captcha.generate_captcha()
        # print(text)

        # 保存图片验证码到Redis
        redis_conn = get_redis_connection('image_codes')
        redis_conn.setex('img_%s' % uuid, const.IMAGE_CODE_REDIS_EXPIRES, text)    # 有效时间300s

        # 响应图片验证码
        # content_type用来指定返回值image的格式
        return HttpResponse(image, content_type='image/jpeg')
