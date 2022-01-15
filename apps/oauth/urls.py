# !usr/bin/env python
# -*- coding:utf-8 _*-
"""
@Author：Rick
@Blog：http://xxxxxx
 
@File：urls.py
@Time：2022/1/12 17:46
 
@Motto：不积跬步无以至千里，不积小流无以成江海！
@Description：
"""
from django.urls import path, re_path
from . import views


urlpatterns = [
    # 提供QQ登录扫码页面
    path('qq/login/', views.QQAuthURLView.as_view()),
    # 处理QQ登录回调
    path('oauth_callback/', views.QQAuthUserView.as_view()),
]
