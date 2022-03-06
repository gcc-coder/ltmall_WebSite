# !usr/bin/env python
# -*- coding:utf-8 _*-
"""
@Author：Rick
@Blog：http://xxxxxx
 
@File：crons.py
@Time：2022/3/6 15:57
 
@Motto：不积跬步无以至千里，不积小流无以成江海！
@Description：封装实现页面静态化方法
"""
# 静态化页面
from .models import ContentCategory, Content
from ltmall.utils.category import get_categories
from django.template import loader
from django.conf import settings
import os


# 查询首页相关数据
# 获取首页模板文件
# 渲染首页html字符串
# 将首页html字符串写入到指定目录，命名'index.html'


def generate_static_index_html():
    # 查看并展示商品分类
    categories = get_categories()
    # 查询所有首页广告
    context_categories = ContentCategory.objects.all()

    contents = {}
    for context_category in context_categories:
        contents[context_category.key] = Content.objects.filter(category__id=context_category.id, status=True).order_by(
            'sequence')

    context = {
        'categories': categories,
        'contents': contents
    }

    template = loader.get_template('contents\index.html')
    html_text = template.render(context)

    # 将生成的静态页面文件保存至static目录
    file_path = os.path.join(settings.STATICFILES_DIRS[0], 'index.html')
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(html_text)
