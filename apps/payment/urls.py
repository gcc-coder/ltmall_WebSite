# !usr/bin/env python
# -*- coding:utf-8 _*-
"""
@Author：Rick
@Blog：http://xxxxxx
 
@File：urls.py
@Time：2022/3/6 13:38
 
@Motto：不积跬步无以至千里，不积小流无以成江海！
@Description：
"""
from django.urls import path, re_path
from . import views

# app_name = ''

urlpatterns = [
    re_path(r'payment/(?P<order_id>\d+)/', views.PaymentView.as_view()),
    re_path(r'payment/status/$', views.PaymentStatusView.as_view()),
]
