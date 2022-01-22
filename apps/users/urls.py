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

app_name = 'users'

urlpatterns = [
    path('', views.index),
    path('register', views.RegisterView.as_view(), name='register'),

    # 判断用户名是否重复，register.js会调用该url
    re_path(r'username/(?P<username>[a-zA-Z0-9_-]{4,20})/count/$', views.CheckUserView.as_view()),
    re_path(r'mobile/(?P<mobile>1[35789][0-9]{9})/count/$', views.CheckMobileView.as_view()),
    # 登录
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    # 用户中心
    path('center/', views.UserCenterView.as_view(), name='center'),

    # 添加邮箱
    path('emails/', views.EmailView.as_view()),
    # 验证邮箱
    path('emails/verification/', views.VerifyEmailView.as_view()),

    # 渲染收货地址
    path('addresses/', views.AddressView.as_view(), name='address'),
    # 新增用户地址
    path('addresses/create/', views.CreateAddressView.as_view()),
    # 修改地址
    re_path('addresses/(?P<address_id>\d+)/$', views.UpdateDestroyAddressView.as_view()),
    # 设置默认地址
    re_path('addresses/(?P<address_id>\d+)/default/$', views.DefaultAddressView.as_view()),
]
