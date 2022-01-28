from django.shortcuts import render
from django.views import View
from contents.models import ContentCategory, Content
from ltmall.utils.category import get_categories


class IndexView(View):
    """提供主页内容"""

    def get(self, request):
        """提供首页页面展示"""
        # 获取商品分类
        categories = get_categories()

        # 查询所有首页广告
        content_categories = ContentCategory.objects.all()
        contents = {}
        for content_cat in content_categories:
            content = Content.objects.filter(category_id=content_cat.id, status=True).order_by('sequence')
            contents[content_cat.key] = content

        context = {
            'categories': categories,
            'contents': contents
        }

        # return render(request, 'contents/index.html')
        return render(request, 'contents/index.html', context)