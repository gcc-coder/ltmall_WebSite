from django.shortcuts import render
from django.views import View
from ltmall.utils.category import get_categories


class GoodsListView(View):
    """商品列表页面"""

    def get(self, request, category_id, page_num):

        categories = get_categories()
        context = {
            'categories': categories
        }

        return render(request, "contents/list.html", context)