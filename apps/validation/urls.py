# !usr/bin/env python
# -*- coding:utf-8 _*-
"""
@Author:Rick
@Blog:http://xxxxxx
 
@File:urls.py
@Time:2021/12/24 20:51
 
@Motto:不积跬步无以至千里，不积小流无以成江海！
"""
from django.urls import path, re_path
from . import views

# app_name = 'validation'

urlpatterns = [
    # 图形验证码
    re_path(r'^image_codes/(?P<uuid>[\w-]+)/$', views.ImageCodeView.as_view()),
]
