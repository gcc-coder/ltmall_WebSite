"""ltmall URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # 主页
    path('', include('contents.urls')),
    # 商品
    path('', include('goods.urls')),
    # 用户名相关
    path('users/', include('users.urls')),
    # 验证码
    path('', include('validation.urls')),
    # 第三方登录
    path('', include('oauth.urls')),
    # 省市区
    path('', include('areas.urls')),
    # Haystack搜索引擎扩展
    path(r'search/', include('haystack.urls')),
    # 购物车
    path('', include('carts.urls')),
    # 订单管理
    path('', include('orders.urls')),
    # 订单支付
    path('', include('payment.urls')),
]
