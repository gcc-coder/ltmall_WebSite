# !usr/bin/env python
# -*- coding:utf-8 _*-
"""
@Author:Rick
@Blog:http://xxxxxx
 
@File:urls.py
@Time:2021/12/17 15:28
 
@Motto:不积跬步无以至千里，不积小流无以成江海！
"""
from django.urls import path, re_path
from . import views

app_name = ''

urlpatterns = [
    path('', views.index),
    path('register', views.RegisterView.as_view(), name='register'),

    # 判断用户名是否重复，register.js会调用该url
    re_path(r'username/(?P<username>[a-zA-Z0-9_-]{4,20})/count/$', views.CheckUserView.as_view()),
    re_path(r'mobile/(?P<mobile>1[35789][0-9]{9})/count/$', views.CheckMobileView.as_view()),
]