# !usr/bin/env python
# -*- coding:utf-8 _*-
"""
@Author：Rick
@Blog：http://xxxxxx
 
@File：urls.py
@Time：2022/1/27 18:29
 
@Motto：不积跬步无以至千里，不积小流无以成江海！
@Description：
"""
from django.urls import path, re_path
from . import views

app_name = 'goods'

urlpatterns = [
    re_path(r'^list/(?P<category_id>\d+)/(?P<page_num>\d+)/$', views.GoodsListView.as_view(), name='list'),
    # 热销排行
    re_path(r'^hot/(?P<category_id>\d+)/$', views.HotGoodsView.as_view()),
]
