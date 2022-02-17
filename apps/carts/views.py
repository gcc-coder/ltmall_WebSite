from django.shortcuts import render
from django.views import View
from django import http
from ltmall.utils.response_code import RETCODE
from goods import models
from django_redis import get_redis_connection
import json, logging, base64, pickle

logger = logging.getLogger('django')


class CartsView(View):
    """购物车管理"""

    def post(self, request):
        """添加购物车"""
        # 接收参数
        carts_json = json.loads(request.body.decode())
        sku_id = carts_json.get('sku_id')
        goods_count = carts_json.get('count')
        # 非必传参数
        selected = carts_json.get('selected')

        # 校验参数
        try:
            models.SKU.objects.get(id=sku_id)
        except Exception as e:
            logger.error(e)
            return http.HttpResponseForbidden('参数sku_id错误')

        if not isinstance(goods_count, int):
            return http.HttpResponseForbidden('参数goods_count错误')
        # try:
        #     count = int(goods_count)
        # except Exception as e:
        #     return http.HttpResponseForbidden('参数count错误')

        if selected and not isinstance(selected, bool):
            return http.HttpResponseForbidden('参数selected错误')

        """判断用户是否登录"""
        user = request.user
        if user.is_authenticated:
            # 用户已登录，操作redis购物车
            redis_conn = get_redis_connection('carts')
            pl = redis_conn.pipeline()  # 使用管道
            # carts_goods_count = redis_conn.hget('carts_%s' % user.id, sku_id)
            # # hash  carts_1 : {sku_id:count}
            # if carts_goods_count:
            #     # 增加购物车的商品数量
            #     goods_count += carts_goods_count
            #     redis_conn.hset('carts_%s' % user.id, sku_id, goods_count)
            # else:
            #     # 新增购物车商品数据
            #     redis_conn.hset('carts_%s' % user.id, sku_id, goods_count)
            pl.hincrby('carts_%s' % user.id, sku_id, goods_count)

            # 被勾选的购物车商品
            if selected:
                # 集合 selected_user_id: [sku_id1, sku_id3, ...]
                pl.sadd('selected_%s' % user.id, sku_id)
            # 执行
            pl.execute()

            return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'ok'})
        else:
            # 用户未登录，操作cookie购物车
            cart_str = request.COOKIES.get('carts')

            if cart_str:
                '''解密'''
                # 将cart_str转成bytes类型的字符串
                cart_str_bytes = cart_str.encode()
                # 将cart_str_bytes转成bytes类型的字典
                cart_dict_bytes = base64.b64decode(cart_str_bytes)
                # 将cart_dict_bytes转成字典
                cart_dict = pickle.loads(cart_dict_bytes)
                """
                {
                   "sku_id1":{
                       "count":"1",
                       "selected":"True"
                   }
                }
               """
            else:
                cart_dict = {}

            # {1: {'count': 1, 'selected': None},2: {'count': 5, 'selected': True}}
            if sku_id in cart_dict:
                # 购物车已有商品，添加（增量计算
                cart_count = cart_dict[sku_id]['count']
                goods_count += cart_count

                cart_dict[sku_id] = {
                    'count': goods_count,
                    'selected': selected
                }
                # print(cart_dict)
            else:
                # 第一次添加购物车数据到cookie
                cart_dict[sku_id] = {
                    'count': goods_count,
                    'selected': selected
                }
                # print(cart_dict)

            '''加密'''
            # cart_dict将字典转成bytes类型的字典
            cart_dict_bytes = pickle.dumps(cart_dict)
            # cart_dict_bytes转成bytes字符串
            cart_str_bytes = base64.b64encode(cart_dict_bytes)
            # cart_str_bytes转成字符串  b'rick'=>'rick'
            cookie_cart_str = cart_str_bytes.decode()

            '''添加到cookie'''
            response = http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'ok'})
            response.set_cookie('carts', cookie_cart_str)

            return response

