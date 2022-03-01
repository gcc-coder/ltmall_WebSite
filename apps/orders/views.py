from django.shortcuts import render
from django.views import View
from ltmall.utils.loginRequire import LoginRequiredMixin


class OrderSettlementView(LoginRequiredMixin, View):
    """结算订单"""

    def get(self, request):
        """提供订单结算页面"""
        return render(request, 'contents/place_order.html')
