# !usr/bin/env python
# -*- coding:utf-8 _*-
"""
@Author：Rick
@Blog：http://xxxxxx
 
@File：auth_utils.py
@Time：2022/1/7 15:31
 
@Motto：不积跬步无以至千里，不积小流无以成江海！
@Description：重写authenticate方法
"""
from django.contrib.auth.backends import ModelBackend
from users.models import User
import re


def get_user_by_account(account):
    """
    获取user对象
    :param account: 手机号或者用户名
    :return: 返回user对象
    """
    try:
        # 判断接收的是手机号还是用户名
        if re.match('^1[3-9]\d{9}$', account):
            user = User.objects.get(mobile=account)
        else:
            user = User.objects.get(username=account)
    # except User.DoesNotExist:
    except:
        return None
    else:
        return user


class UsernameMobileBackend(ModelBackend):
    """自定义用户认证后端逻辑"""

    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        重写认证方法
        :param username: 用户名或者手机号
        :param password: 明文密码
        :param kwargs: 其他额外参数
        :return: 返回user对象
        """
        user = get_user_by_account(username)

        if user and user.check_password(password):
            return user
        else:
            return None

