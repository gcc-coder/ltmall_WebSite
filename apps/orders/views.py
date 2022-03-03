from django.shortcuts import render
from django.views import View
from ltmall.utils.loginRequire import LoginRequiredMixin, LoginRequiredJsonMixin
from users.models import Address
from goods.models import SKU
from orders.models import OrderInfo, OrderGoods
from decimal import Decimal
from django_redis import get_redis_connection
from ltmall.utils.response_code import RETCODE
from django.utils import timezone
from django.db import transaction
from django import http
import json


class OrderSettlementView(LoginRequiredMixin, View):
    """结算订单"""

    def get(self, request):
        """提供订单结算页面"""

        # 查询用户收货地址
        user = request.user
        try:
            addresses = Address.objects.filter(user=user, is_deleted=False)
        except Exception as e:
            addresses = None

        redis_conn = get_redis_connection('carts')
        # {b'1': b'2', b'3': '4'}
        redis_cart = redis_conn.hgetall("carts_%s" % user.id)
        # {b'1'}
        redis_selected = redis_conn.smembers("selected_%s" % user.id)

        # 构造购物车中被勾选的数据
        new_cart_dict = {}  # {1:2, 2:4}
        for sku_id in redis_selected:
            new_cart_dict[int(sku_id)] = int(redis_cart[sku_id])

        sku_ids = new_cart_dict.keys()
        skus = SKU.objects.filter(id__in=sku_ids)

        total_count = 0
        total_amount = Decimal(0.00)
        for sku in skus:
            # 给sku添加count(数量)和小计(amount)
            sku.count = new_cart_dict[sku.id]
            sku.amount = sku.price * sku.count
            # Decimal   float  1.23
            # print(type(sku.amount))

            # 累加数量和金额
            total_count += sku.count
            total_amount += sku.amount

        # 运费
        freight = Decimal(10.00)
        payment_amount = total_amount + freight

        context = {
            'addresses': addresses,
            'skus': skus,
            'payment_amount': payment_amount,
            'total_count': total_count,
            'total_amount': total_amount,
            'freight': freight
        }

        return render(request, 'contents/place_order.html', context)


class OrderCommitView(LoginRequiredJsonMixin, View):
    """订单提交"""

    def post(self, request):
        """保存订单信息和订单商品信息"""
        # 接收参数
        json_dict = json.loads(request.body.decode())
        address_id = json_dict.get('address_id')
        pay_method = json_dict.get('pay_method')
        user = request.user

        # 校验参数
        try:
            address = Address.objects.get(id=address_id)
        except Exception as e:
            return http.HttpResponseForbidden('参数address_id有误')

        if pay_method not in [OrderInfo.PAY_METHODS_ENUM['CASH'], OrderInfo.PAY_METHODS_ENUM['ALIPAY']]:
            return http.HttpResponseForbidden('参数pay_method有误')

        # 开启事务
        with transaction.atomic():
            # 创建一个保存点
            save_id = transaction.savepoint()
            try:
                # 20200903210058 + id
                order_id = timezone.localtime().strftime('%Y%m%d%H%M%S') + '%09d' % user.id
                # 保存订单信息
                order = OrderInfo.objects.create(
                    order_id=order_id,
                    user=user,
                    address=address,
                    total_count=0,
                    total_amount=0,
                    freight=Decimal(10.0),  # 运费
                    pay_method=pay_method,
                    # status = '未支付' if pay_method == '支付宝' else '未发货'
                    status=OrderInfo.ORDER_STATUS_ENUM['UNPAID'] if pay_method == OrderInfo.PAY_METHODS_ENUM[
                        'ALIPAY'] else
                    OrderInfo.ORDER_STATUS_ENUM['UNSEND']
                )

                # 连接Redis
                redis_conn = get_redis_connection('carts')
                # {b'1': b'2', b'3': '4'}
                redis_cart = redis_conn.hgetall("carts_%s" % user.id)
                # {b'1'}
                redis_selected = redis_conn.smembers("selected_%s" % user.id)

                # 构造购物车中被勾选的数据
                new_cart_dict = {}  # {1:2, 2:4}
                for sku_id in redis_selected:
                    new_cart_dict[int(sku_id)] = int(redis_cart[sku_id])

                sku_ids = new_cart_dict.keys()

                for sku_id in sku_ids:
                    sku = SKU.objects.get(id=sku_id)
                    # 原始的库存
                    origin_stock = sku.stock
                    # 提交订单的商品的数量  10  5
                    sku_count = new_cart_dict[sku.id]

                    # 判断商品的库存
                    if sku_count > origin_stock:
                        # 库存不足 回滚
                        transaction.savepoint_rollback(save_id)
                        return http.JsonResponse({'code': RETCODE.STOCKERR, 'errmsg': '库存不足'})
                    # SKU 减库存  加销量
                    sku.stock -= sku_count  # 会用到搜索，需要开启elasticsearch容器
                    sku.sales += sku_count
                    sku.save()
                    # print(sku.query)

                    # SPU 加销量
                    sku.spu.sales += sku_count
                    sku.spu.save()

                    # 保存订单商品信息
                    OrderGoods.objects.create(
                        order=order,
                        sku=sku,
                        count=sku_count,
                        price=sku.price
                    )

                    # 累加订单商品的数量和总价到订单基本信息
                    order.total_count += sku_count
                    order.total_amount += sku_count * sku.price

                # 最后加运费
                order.total_amount += order.freight
                order.save()
            except Exception as e:
                # 发生异常 回滚
                transaction.savepoint_rollback(save_id)
                return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '下单失败'})

            # 数据库操作成功 提交事务
            transaction.savepoint_commit(save_id)

        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'order_id': order_id})
