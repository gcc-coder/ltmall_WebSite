# !usr/bin/env python
# -*- coding:utf-8 _*-
"""
@Author:Rick
@Blog:http://xxxxxx
 
@File:urls.py
@Time:2021/12/22 19:18
 
@Motto:不积跬步无以至千里，不积小流无以成江海！
"""
from django.urls import path, re_path
from . import views

app_name = 'contents'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
]
