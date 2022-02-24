# !usr/bin/env python
# -*- coding:utf-8 _*-
"""
@Author：Rick
@Blog：http://xxxxxx
 
@File：merge_carts.py
@Time：2022/2/24 11:32
 
@Motto：不积跬步无以至千里，不积小流无以成江海！
@Description：封装合并购物车数据方法
"""
import base64, pickle
from django_redis import get_redis_connection


def merge_carts_cookies_redis(request, user, response):
    """合并购物车商品数据"""
    # 1.获取cookie中的购物车数据
    # 2.判断cookie中的购物车数据是否存在：
    #   - 如果不存在,不需要合并，不作任何操作，直接返回response；
    #   - 如果存在,需要合并。
    # 3.准备新的数据容器, 存放数据的有什么？sku_id count selected
    # 4.根据新的数据结构,合并到Redis中

    # 获取cookie中的购物车数据
    cart_str = request.COOKIES.get('carts')

    # 判断cookie中的购物车数据是否存在
    if not cart_str:
        # cookie中若无购物车数据，则不作任何操作
        return response

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
    # sku_id count selected unselected
    new_cart_dict = {}
    # 构建勾选状态列表，以便于同步至Redis中
    new_selected_add = []
    new_selected_rem = []

    for sku_id, cookie_dict in cart_dict.items():
        # hash  carts_1 : {sku_id:count}
        new_cart_dict[sku_id] = cookie_dict['count']
        if cookie_dict['selected']:
            new_selected_add.append(sku_id)
        else:
            new_selected_rem.append(sku_id)

    # 合并到Redis
    redis_conn = get_redis_connection('carts')
    pl = redis_conn.pipeline()
    pl.hmset('carts_%s' % user.id, new_cart_dict)

    if new_selected_add:
        pl.sadd('selected_%s' % user.id, *new_selected_add)
    if new_selected_rem:
        pl.srem('selected_%s' % user.id, *new_selected_rem)
    pl.execute()

    response.delete_cookie('carts')

    return response
