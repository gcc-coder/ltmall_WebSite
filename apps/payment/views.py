from django.shortcuts import render
from ltmall.utils.loginRequire import LoginRequiredJsonMixin, LoginRequiredMixin
from django.views import View
from alipay import AliPay
from django.conf import settings
from orders.models import OrderInfo
from payment.models import Payment
from django import http
from ltmall.utils.response_code import RETCODE
import os


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
            return_url=settings.ALIPAY_RETURN_URL,  # 回调地址
        )

        alipay_url = settings.ALIPAY_URL + '?' + order_string

        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'alipay_url': alipay_url})


class PaymentStatusView(LoginRequiredMixin, View):
    """保存支付订单的结果"""

    def get(self, request):
        # 获取支付后的URL回调参数
        query_dict = request.GET  # 返回QueryDict格式数据
        data = query_dict.dict()  # 转为字典格式

        signature = data.pop("sign")

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

        # 校验支付成功否
        success = alipay.verify(data, signature)

        if success:
            # 保存数据
            order_id = data.get('out_trade_no')
            trade_id = data.get('trade_no')
            Payment.objects.create(
                order_id=order_id,
                trade_id=trade_id
            )
            # 修改订单商品状态为未评价
            OrderInfo.objects.filter(order_id=order_id, status=OrderInfo.ORDER_STATUS_ENUM['UNPAID']).update(
                status=OrderInfo.ORDER_STATUS_ENUM['UNCOMMENT'])

            context = {
                'trade_id': trade_id
            }

            return render(request, 'contents/pay_success.html', context=context)
        else:
            return http.HttpResponseForbidden('支付失败')
