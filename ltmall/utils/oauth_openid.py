# !usr/bin/env python
# -*- coding:utf-8 _*-
"""
@Author：Rick
@Blog：http://xxxxxx
 
@File：oauth_openid.py
@Time：2022/1/15 15:37
 
@Motto：不积跬步无以至千里，不积小流无以成江海！
@Description：序列化和反序列化openid
"""
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from django.conf import settings
from ltmall.settings import const


def generate_access_token(open_id):
    s = Serializer(settings.SECRET_KEY, const.ACCESS_TOKEN_EXPIRES)     # 过期时间300s
    data = {'openid': open_id}
    token = s.dumps(data)

    return token.decode()

