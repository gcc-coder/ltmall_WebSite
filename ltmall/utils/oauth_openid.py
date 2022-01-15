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
    """
    序列化: openid
    :param open_id: openid明文
    :return: 返回openid密文
    """
    # 创建序列化对象
    s = Serializer(settings.SECRET_KEY, const.ACCESS_TOKEN_EXPIRES)     # 过期时间300s
    data = {'openid': open_id}
    # 进行序列化
    token = s.dumps(data)

    return token.decode()


def check_access_token(access_token_openid):
    """
    反序列化
    :param access_token_openid: openid的密文
    :return: openid明文
    """
    # 创建序列化对象
    s = Serializer(settings.SECRET_KEY, const.ACCESS_TOKEN_EXPIRES)
    # 字典
    try:
        data = s.loads(access_token_openid)
    except Exception as e:
        return None
    else:
        return data.get('openid')

