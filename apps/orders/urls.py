# !usr/bin/env python
# -*- coding:utf-8 _*-
"""
@Author：Rick
@Blog：http://xxxxxx
 
@File：urls.py
@Time：2022/3/1 15:59
 
@Motto：不积跬步无以至千里，不积小流无以成江海！
@Description：
"""
from django.urls import path, re_path
from . import views

app_name = 'orders'

urlpatterns = [
    path('orders/settlement/', views.OrderSettlementView.as_view(), name='settlement'),
]
