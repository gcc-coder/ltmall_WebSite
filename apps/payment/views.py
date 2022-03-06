from django.shortcuts import render
from ltmall.utils.loginRequire import LoginRequiredJsonMixin
from django.views import View
from alipay import AliPay
import os
from django.conf import settings
from orders.models import OrderInfo
from django import http
from ltmall.utils.response_code import RETCODE


class PaymentView(LoginRequiredJsonMixin, View):
    """订单支付功能"""

    def get(self, request, order_id):
        user = request.user
        try:
            # 获取未支付订单信息
            order = OrderInfo.objects.get(order_id=order_id, user=user, status=OrderInfo.ORDER_STATUS_ENUM['UNPAID'])
        except Exception as e:
            return http.HttpResponseForbidden('订单信息错误')

        # 读取密钥文件
        app_private_key_string = open(
            os.path.join(os.path.dirname(os.path.abspath(__file__)), 'keys/app_private_key.pem')).read()
        alipay_public_key_string = open(
            os.path.join(os.path.dirname(os.path.abspath(__file__)), 'keys/alipay_public_key.pem')).read()

        alipay = AliPay(
            appid=settings.ALIPAY_APPID,
            app_notify_url=None,  # 默认回调url
            app_private_key_string=app_private_key_string,
            # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
            alipay_public_key_string=alipay_public_key_string,
            sign_type="RSA2",  # RSA 或者 RSA2
            debug=settings.ALIPAY_DEBUG,  # 默认False
        )

        subject = "LT商城%s" % order_id

        # 电脑网站支付，需要跳转到https://openapi.alipay.com/gateway.do? + order_string
        order_string = alipay.api_alipay_trade_page_pay(
            out_trade_no=order_id,  # 订单编号
            total_amount=str(order.total_amount),  # 订单支付的总金额
            subject=subject,  # 订单标题
            return_url="https://www.meiduo.site:8000/payment/status",  # 回调地址
        )

        alipay_url = settings.ALIPAY_URL + '?' + order_string

        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'alipay_url': alipay_url})
