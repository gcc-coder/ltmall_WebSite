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
        """添加商品至购物车"""
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
            # # hash类型  carts_1 : {sku_id:count}
            # if carts_goods_count:
            #     # 增加购物车的商品数量
            #     goods_count += carts_goods_count
            #     redis_conn.hset('carts_%s' % user.id, sku_id, goods_count)
            # else:
            #     # 新增购物车商品数据
            #     redis_conn.hset('carts_%s' % user.id, sku_id, goods_count)
            # 增量购物车商品
            pl.hincrby('carts_%s' % user.id, sku_id, goods_count)

            # 被勾选的购物车商品
            if selected:
                # 集合类型 selected_user_id: [sku_id1, sku_id3, ...]
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
                # 购物车已有商品，直接添加（增量计算）
                cart_count = cart_dict[sku_id]['count']
                goods_count += cart_count

                cart_dict[sku_id] = {
                    'count': goods_count,
                    'selected': selected
                }
            else:
                # 第一次添加购物车数据到cookie
                cart_dict[sku_id] = {
                    'count': goods_count,
                    'selected': selected
                }
                # print(cart_dict)

            '''加密，渲染到前端cookie中'''
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

    def get(self, request):
        """查询购物车商品"""
        user = request.user
        if user.is_authenticated:
            # 用户已经登录逻辑
            redis_conn = get_redis_connection('carts')
            # carts_1 : {b'3':b'1', b'4':b'2'}  用户1 3号商品添加到购物车1件
            redis_cart = redis_conn.hgetall('carts_%s' % user.id)
            # 选中的商品的sku_id
            redis_selected = redis_conn.smembers('selected_%s' % user.id)

            # 将redis中的数据，转换成与cookie中同样格式的购物车字典
            cart_dict = {}
            for sku_id, count in redis_cart.items():
                cart_dict[int(sku_id)] = {
                    'count': int(count),
                    'selected': sku_id in redis_selected
                }
        else:
            # 用户未登陆逻辑
            cart_str = request.COOKIES.get('carts')
            # gAN9cQAoWAEAAAAxcQF9cQIoWAUAAABjb3VVgBAAAAMnEFfXEGKGg
            if cart_str:
                # 将cart_str转成bytes类型的字符串
                cart_str_bytes = cart_str.encode()
                # 将cart_str_bytes转成bytes类型的字典
                cart_dict_bytes = base64.b64decode(cart_str_bytes)
                # 将cart_dict_bytes转成字典
                cart_dict = pickle.loads(cart_dict_bytes)
            else:
                cart_dict = {}

        sku_ids = cart_dict.keys()
        # for sku_id in sku_ids:
        #     sku = SKU.objects.get(id=sku_id)
        skus = models.SKU.objects.filter(id__in=sku_ids)
        """
           {
              "sku_id1":{
                  "count":"1",
                  "selected":"True"
              }
           }
        """

        cart_skus = []
        for sku in skus:
            cart_skus.append({
                'id': sku.id,
                'count': cart_dict.get(sku.id).get('count'),
                # 转为字符串，方便前端Json调用
                'selected': str(cart_dict.get(sku.id).get('selected')),  # True 'True'
                'name': sku.name,
                'default_image_url': sku.default_image.url,
                'price': str(sku.price),
                'amount': str(sku.price * cart_dict.get(sku.id).get('count'))
            })

        context = {
            'cart_skus': cart_skus
        }

        return render(request, 'contents\cart.html', context=context)

    def put(self, request):
        """修改购物车商品数量"""

        # 接收参数
        json_dict = json.loads(request.body.decode())
        sku_id = json_dict.get('sku_id')  # 1000
        count = json_dict.get('count')
        selected = json_dict.get('selected')

        # 校验参数
        try:
            sku = models.SKU.objects.get(id=sku_id)
        except Exception as e:
            return http.HttpResponseForbidden('参数sku_id错误')

        try:
            count = int(count)
        except Exception as e:
            return http.HttpResponseForbidden('参数count错误')

        if selected:
            if not isinstance(selected, bool):
                return http.HttpResponseForbidden('参数selected错误')

        # 验证用户是否登录
        user = request.user
        if user.is_authenticated:
            # 用户已登录, 修改redis中的购物车数据
            redis_conn = get_redis_connection('carts')
            pl = redis_conn.pipeline()  # Redis管道
            pl.hset('carts_%s' % user.id, sku_id, count)
            if selected:
                pl.sadd('selected_%s' % user.id, sku_id)
            else:
                pl.srem('selected_%s' % user.id, sku_id)
            pl.execute()  # 执行管道

            cart_sku = {
                'id': sku_id,
                'count': count,
                'selected': selected,
                'name': sku.name,
                'default_image_url': sku.default_image.url,
                'price': sku.price,
                'amount': sku.price * count
            }

            return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '修改购物车成功', 'cart_sku': cart_sku})
        else:
            # 用户未登陆, 修改Cookies中的购物车数据
            cart_str = request.COOKIES.get('carts')
            # gAN9cQAoWAEAAAAxcQF9cQIoWAUAAABjb3VVgBAAAAMnEFfXEGKGg
            if cart_str:
                # 将cart_str转成bytes类型的字符串
                cart_str_bytes = cart_str.encode()
                # 将cart_str_bytes转成bytes类型的字典
                cart_dict_bytes = base64.b64decode(cart_str_bytes)
                # 将cart_dict_bytes转成字典
                cart_dict = pickle.loads(cart_dict_bytes)
            else:
                cart_dict = {}

            # 将接收到的数据,重新写入到cookie(覆盖)
            cart_dict[sku_id] = {
                'count': count,
                'selected': selected
            }

            # cart_dict将字典转成bytes类型的字典
            cart_dict_bytes = pickle.dumps(cart_dict)
            # cart_dict_bytes转成bytes字符串
            cart_str_bytes = base64.b64encode(cart_dict_bytes)
            # cart_str_bytes转成字符串
            cookie_cart_str = cart_str_bytes.decode()

            cart_sku = {
                'id': sku_id,
                'count': count,
                'selected': selected,
                'name': sku.name,
                'default_image_url': sku.default_image.url,
                'price': sku.price,
                'amount': sku.price * count
            }

            response = http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'ok', 'cart_sku': cart_sku})
            response.set_cookie('carts', cookie_cart_str)

            return response

    def delete(self, request):
        """删除购物车商品"""
        # 接收参数
        json_dict = json.loads(request.body.decode())
        sku_id = json_dict.get('sku_id')

        # 判断sku_id是否存在
        try:
            models.SKU.objects.get(id=sku_id)
        except Exception as e:
            return http.HttpResponseForbidden('商品不存在')

        # 判断用户是否登陆
        user = request.user
        if user.is_authenticated:
            # 用户已经登陆,删除redis购物车
            redis_conn = get_redis_connection('carts')
            pl = redis_conn.pipeline()
            # 删除hash购物车商品记录
            pl.hdel('carts_%s' % user.id, sku_id)
            # 移除选中状态
            pl.srem('selected_%s' % user.id, sku_id)
            # 执行
            pl.execute()
            return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK'})

        else:
            # 用户未登陆, 删除cookie购物车
            """
            {
               "sku_id1":{
                   "count":"1",
                   "selected":"True"
               }
            }
            """
            # 获取cookie中的购物车数据
            cart_str = request.COOKIES.get('carts')
            if cart_str:
                # 将cart_str转成bytes类型的字符串
                cart_str_bytes = cart_str.encode()
                # 将cart_str_bytes转成bytes类型的字典
                cart_dict_bytes = base64.b64decode(cart_str_bytes)
                # 将cart_dict_bytes转成字典
                cart_dict = pickle.loads(cart_dict_bytes)
            else:
                cart_dict = {}
            # print(cart_dict)
            # {1: {'count': 2, 'selected': True}, 2: {'count': 1, 'selected': True}}
            response = http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK'})
            if sku_id in cart_dict:
                del cart_dict[sku_id]

                # cart_dict将字典转成bytes类型的字典
                cart_dict_bytes = pickle.dumps(cart_dict)
                # cart_dict_bytes转成bytes字符串
                cart_str_bytes = base64.b64encode(cart_dict_bytes)
                # cart_str_bytes转成字符串
                cookie_cart_str = cart_str_bytes.decode()
                response.set_cookie('carts', cookie_cart_str)

            return response
