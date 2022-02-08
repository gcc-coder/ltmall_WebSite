from django.shortcuts import render
from django.views import View
from ltmall.utils.category import get_categories
from ltmall.utils.breadcrumb import get_breadcrumb
from django import http
import logging


logger = logging.getLogger('django')
class GoodsListView(View):
    """商品列表页面"""

    def get(self, request, category_id, page_num):
        # 查询商品类别
        categories = get_categories()

        try:
            # 查询面包屑
            breadcrumb = get_breadcrumb(category_id)
        except Exception as e:
            logger.error(e)
            return render(request, 'contents/404.html')

        context = {
            'categories': categories,
            'breadcrumb': breadcrumb
        }

        # 响应结果
        return render(request, "contents/list.html", context)