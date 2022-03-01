from django.shortcuts import render
from django.views import View
from ltmall.utils.loginRequire import LoginRequiredMixin
from users.models import Address
from goods.models import SKU
from decimal import Decimal
from django_redis import get_redis_connection


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
