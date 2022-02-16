from django.shortcuts import render
from django.views import View
from ltmall.utils.category import get_categories
from ltmall.utils.breadcrumb import get_breadcrumb
from goods.models import SKU, GoodsCategory, SPUSpecification, SKUSpecification,  GoodsVisitCount
from django import http
from ltmall.utils.response_code import RETCODE
from django.views.generic import ListView
from django.core.paginator import Paginator
from django.utils import timezone
from datetime import datetime
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
        try:
            # 获取第page_num页的数据
            page_skus = paginator.page(page_num)
        except Exception as e:
            logger.error(e)
            return render(request, "contents/404.html")
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


class HotGoodsView(View):
    """热销排行"""

    def get(self, request, category_id):
        """
        提供商品热销排行JSON数据
        :param category_id: 必传参数
        :return: Json数据
        """
        # 根据销量倒序，取前两个数据
        skus = SKU.objects.filter(category_id=category_id, is_launched=True).order_by('-sales')[:2]
        # print(skus)
        '''
        "code":"0",
        "errmsg":"OK",
        "hot_skus":[
            {
                "id":6,
                "default_image_url":"http://image.meiduo.site:8888/group1/M00/00/02/CtM3BVrRbI2ARekNAAFZsBqChgk3141998",
                "name":"Apple iPhone 8 Plus (A1864) 256GB 深空灰色 移动联通电信4G手机",
                "price":"7988.00"
            },
        ]
        '''
        hot_skus = []
        for sku in skus:
            hot_sku = {
                'id': sku.id,
                'default_image_url': sku.default_image.url,
                'name': sku.name,
                'price': sku.price
            }
            hot_skus.append(hot_sku)

        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'ok', 'hot_skus': hot_skus})


class DetailView(View):
    """商品详情页"""

    def get(self, request, sku_id):
        """提供商品详情页"""
        try:
            # 获取当前商品的sku信息
            goods_sku = SKU.objects.get(id=sku_id)
        except Exception as e:
            return render(request, 'contents/404.html')

        # 查询商品类别
        categories = get_categories()
        # 获取面包屑导航数据
        breadcrumb = get_breadcrumb(goods_sku.category)

        # 构建当前商品的SKU规格键key
        sku_specs = SKUSpecification.objects.filter(sku__id=sku_id).order_by('spec_id')
        sku_key = []
        for spec in sku_specs:
            sku_key.append(spec.option.id)

        # 获取当前商品的所有SKU
        spu_id = goods_sku.spu_id
        skus = SKU.objects.filter(spu_id=spu_id)
        # print(skus.query)   # 将ORM转换为SQL语句

        # 构建不同规格参数（选项）的sku字典
        spec_sku_map = {}   # {(1,4,7):1, }
        for sku in skus:
            # 获取商品所有sku的规格参数
            sku_specs = sku.specs.order_by('spec_id')
            # 用于形成规格参数-sku字典的键
            key = []
            for spec in sku_specs:
                key.append(spec.option.id)
            # 向规格参数-sku字典添加记录
            spec_sku_map[tuple(key)] = sku.id
        # 获取当前商品的SPU规格信息
        goods_specs = SPUSpecification.objects.filter(spu_id=spu_id).order_by('id')
        """
        <QuerySet [<SPUSpecification: 华为 HUAWEI P10 Plus: 颜色>, <SPUSpecification: 华为 HUAWEI P10 Plus: 版本>]>
        """
        # 若当前sku的规格信息不完整，则不再继续
        if len(sku_key) < len(goods_specs):
            return

        for index, spec in enumerate(goods_specs):
            # print(spec)     # 华为 HUAWEI P10 Plus: 颜色
            # 复制当前sku的规格键
            key = sku_key[:]
            # 获取该规格的所有选项
            spec_options = spec.options.all()

            for option in spec_options:
                # print(option)       # 华为 HUAWEI P10 Plus: 颜色 - 钻雕金
                # 在规格参数sku字典中查找符合当前规格的sku
                key[index] = option.id
                # 给option类添加属性
                option.sku_id = spec_sku_map.get(tuple(key))
            # 给spec添加属性
            spec.spec_options = spec_options    # spec是一个class
            # for s in spec.spec_options:
                # print(s.sku_id, s.spec_id, goods_sku.id)

        # 渲染页面
        context = {
            'categories': categories,
            'breadcrumb': breadcrumb,
            'goods_sku': goods_sku,
            # category_id用于获取热销排行数据
            'category_id': goods_sku.category.id,
            'specs': goods_specs,
        }

        return render(request, 'contents/detail.html', context)


class DetailVisitView(View):
    """详情页分类商品访问量"""

    def post(self, request, category_id):
        try:
            category = GoodsCategory.objects.get(id=category_id)
        except Exception as e:
            return http.HttpResponseForbidden('参数异常')

        # 获取当天的日期
        t = timezone.localtime()
        today_str = '%d-%02d-%02d' % (t.year, t.month, t.day)

        today_date = datetime.strptime(today_str, '%Y-%m-%d')
        try:
            # 查询当天该类别的商品的访问量
            counts_data = category.visit.get(date=today_date)
        except Exception as e:
            # 如果该类别的商品在当天没有访问记录，就新建一个
            counts_data = GoodsVisitCount()

        try:
            counts_data.category = category
            counts_data.count += 1
            counts_data.save()
        except Exception as e:
            logger.error(e)
            return http.HttpResponseServerError('服务器异常')

        # 响应结果
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK'})