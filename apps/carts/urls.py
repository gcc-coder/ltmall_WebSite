# !usr/bin/env python
# -*- coding:utf-8 _*-
"""
@Author：Rick
@Blog：http://xxxxxx
 
@File：urls.py
@Time：2022/2/17 18:21
 
@Motto：不积跬步无以至千里，不积小流无以成江海！
@Description：
"""
from django.urls import path, re_path
from . import views

app_name = 'carts'

urlpatterns = [
    # 购物车商品管理
    path('carts/', views.CartsView.as_view(), name='info'),
    # 全选购物车商品
    re_path('^carts/selection/$', views.CartSelectAllView.as_view()),
]
