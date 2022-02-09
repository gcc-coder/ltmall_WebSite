# !usr/bin/env python
# -*- coding:utf-8 _*-
"""
@Author：Rick
@Blog：http://xxxxxx
 
@File：breadcrumb.py
@Time：2022/2/7 19:35
 
@Motto：不积跬步无以至千里，不积小流无以成江海！
@Description：
"""
from goods.models import GoodsCategory


def get_breadcrumb(category):
    # 面包屑导航  一级:一级  二级:一级+二级  三级:一级+二级+三级
    """
    breadcrumb = {'cat1':'', 'cat2': '', 'cat3': ''}
    """
    # category3 = GoodsCategory.objects.filter(parent_id=category.id)

    breadcrumb = {'cat1': '', 'cat2': '', 'cat3': ''}

    if category.parent is None:
        # 一级
        breadcrumb['cat1'] = category
    # elif category3.count() == 0:
    elif category.subs.count() == 0:
        # 三级：若传入的category_id，在parent_id中查询不到，即为三级分类
        cat2 = category.parent
        breadcrumb = {
            'cat1': cat2.parent,
            'cat2': cat2,
            'cat3': category
        }
    else:
        # 二级
        breadcrumb = {
            'cat1': category.parent,
            'cat2': category
        }

    return breadcrumb
