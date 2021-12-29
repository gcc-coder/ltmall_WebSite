from django.http import HttpResponse, HttpResponseForbidden, JsonResponse
from django.views.generic import View
from validation.libs.captcha.captcha import captcha
from django_redis import get_redis_connection
from ltmall.settings import const
from validation.libs.ronglianyun.ccp_sms import CCP
from ltmall.utils.response_code import RETCODE
import random


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


class SMSCodeView(View):
    """短信验证码逻辑"""

    def get(self, request, mobile ):
        """
        :param request:
        :param mobile: 接收手机号参数
        :return: Json
        """
        # 接收查询字符串参数
        image_code_client = request.GET.get('image_code')       # 值的类型是字符串
        uuid = request.GET.get('uuid')
        # 校验参数
        if not all([image_code_client, uuid]):  # 使用all函数来校验参数是否有值
            return HttpResponseForbidden('缺少必传参数')
        # 提取图形验证码
        redis_conn = get_redis_connection('image_codes')
        image_code_server = redis_conn.get('img_%s' % uuid)     # 值的类型是字节
        # print(image_code_server)
        # 删除redis中的图形验证码
        redis_conn.delete('img_%s' % uuid)
        # 对比图形验证码
        if image_code_client.lower() != image_code_server.decode().lower():
            return JsonResponse({'code': RETCODE.IMAGECODEERR, 'errmsg': '输入的图形码有误'})

        # 生成6位短信验证码:%06d若出现空值，用0补位
        sms_code = "%06d" % random.randint(0, 999999)
        # 保存短信验证码到Redis
        redis_conn.setex('sms_%s' % mobile, const.IMAGE_CODE_REDIS_EXPIRES, sms_code)
        # 发送短信验证码
        CCP().send_message(const.SMS_SEND_TEMPLATE_ID, mobile, (sms_code, const.SMS_CODE_REDIS_EXPIRES//60))

        # 响应结果
        # return HttpResponse('Hello')
        return JsonResponse({'code': RETCODE.OK, 'errmsg': '短信验证码发送成功'})


