from django.shortcuts import render
from django.views import View
from ltmall.utils.category import get_categories
from ltmall.utils.breadcrumb import get_breadcrumb
from goods.models import SKU, GoodsCategory
from django import http
from django.views.generic import ListView
from django.core.paginator import Paginator
from ltmall.settings import const
import logging

logger = logging.getLogger('django')


class GoodsListView(View):
    """商品列表页面"""

    def get(self, request, category_id, page_num):
        try:
            # 判断category_id是否正确
            category = GoodsCategory.objects.get(id=category_id)
        except Exception as e:
            logger.error(e)
            return render(request, 'contents/404.html')

        # 查询商品类别
        categories = get_categories()
        # 获取面包屑导航数据
        breadcrumb = get_breadcrumb(category)

        # 接收sort参数：如果不传sort，使用默认的排序规则
        sort = request.GET.get('sort', 'default')
        # 按照排序规则查询该分类商品SKU信息
        if sort == 'price':
            sort_field = 'price'  # 正序
        elif sort == 'hot':
            sort_field = '-sales'  # 倒序
        else:
            # 'price'和'sales'以外的所有排序方式都归为'default'
            sort = 'default'
            sort_field = 'create_time'

        # 排序
        skus = SKU.objects.filter(category=category, is_launched=True).order_by(sort_field)
        # print(skus)

        # 分页 创建分页器: Paginator('分页的记录来源', '每页记录的条数')
        paginator = Paginator(skus, const.PAGINATOR_NUM)
        # 获取第page_num页的数据
        page_skus = paginator.page(page_num)
        # 总页面数
        total_page = paginator.num_pages

        context = {
            'categories': categories,
            'breadcrumb': breadcrumb,
            'page_skus': page_skus,
            'total_page': total_page,
            'category_id': category_id,
            'sort': sort,
            'page_num': page_num,
        }

        # 响应结果
        return render(request, "contents/list.html", context)
