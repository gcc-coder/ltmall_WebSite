# !usr/bin/env python
# -*- coding:utf-8 _*-
"""
@Author：Rick
@Blog：http://xxxxxx
 
@File：verify_emails.py
@Time：2022/1/17 18:15
 
@Motto：不积跬步无以至千里，不积小流无以成江海！
@Description：序列化和反序列化邮箱验证链接
"""
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from django.conf import settings
from ltmall.settings import const
from users.models import User


def generate_verify_email_url(user):
    """
    生成验证邮箱链接
    :param user: 当前登录的用户
    :return: token序列化后的verify_url
    """
    s = Serializer(settings.SECRET_KEY, const.ACCESS_TOKEN_EXPIRES)     # 过期时间300s
    data = {
        'user_id': user.id,
        'email': user.email
    }
    token = s.dumps(data).decode()

    return const.VERIFY_EMAIL_URL + '?token=' + token


def check_verify_email_token(token):
    """
    反序列token, 获取user信息
    :param token: 序列化之后的用户信息
    :return: user
    """
    s = Serializer(settings.SECRET_KEY, const.ACCESS_TOKEN_EXPIRES)  # 过期时间300s

    try:
        # 反序列化token
        data = s.loads(token)
    except Exception as e:
        return None
    else:
        user_id = data.get('user_id')
        email = data.get('email')
        try:
            user = User.objects.get(id=user_id, email=email)
        except Exception as e:
            return None
        else:
            return user

