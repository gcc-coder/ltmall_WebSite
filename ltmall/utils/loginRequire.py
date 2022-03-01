# !usr/bin/env python
# -*- coding:utf-8 _*-
"""
@Author：Rick
@Blog：http://xxxxxx
 
@File：loginRequire.py
@Time：2022/1/16 16:58
 
@Motto：不积跬步无以至千里，不积小流无以成江海！
@Description：用户未登录时，进行验证邮箱的操作
"""

from django.contrib.auth.mixins import LoginRequiredMixin
from django import http
from ltmall.utils.response_code import RETCODE


class LoginRequiredJsonMixin(LoginRequiredMixin):
    """重写handle_no_permission方法"""

    def handle_no_permission(self):
        """返回JSON数据"""

        return http.JsonResponse({"code": RETCODE.SESSIONERR, 'errmsg': "用户未登陆"})