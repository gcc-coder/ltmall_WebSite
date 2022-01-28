# !usr/bin/env python
# -*- coding:utf-8 _*-
"""
@Author：Rick
@Blog：http://xxxxxx
 
@File：category.py
@Time：2022/1/27 15:15
 
@Motto：不积跬步无以至千里，不积小流无以成江海！
@Description：封装商品分类
"""
from goods.models import GoodsChannel, GoodsCategory


def get_categories():
    # 查看并展示商品分类
    categories = {}
    # 查询所有的商品频道
    all_channels = GoodsChannel.objects.order_by('group_id', 'sequence')
    # all_channels <QuerySet [<GoodsChannel: 手机>, <GoodsChannel: 相机>, <GoodsChannel: 数码>...]>

    # 遍历所有频道
    for channel in all_channels:
        # 频道组
        group_id = channel.group_id
        if group_id not in categories:  # 过滤重复组id
            categories[group_id] = {
                "channels": [],
                "sub_cats": []
            }
        channels = categories[group_id].get('channels')
        sub_cats = categories[group_id].get('sub_cats')

        # 当前频道对应的一级类别
        categories1 = channel.category

        channels.append({
            'id': categories1.id,
            'name': categories1.name,
            'url': channel.url
        })

        categories2 = GoodsCategory.objects.filter(parent_id=categories1.id)

        # 查询二级和三级类别
        for category2 in categories2:
            category2.sub_cats = []
            sub_cats.append({
                'id': category2.id,
                'name': category2.name,
                'sub_cats': category2.sub_cats
            })
            categories3 = GoodsCategory.objects.filter(parent_id=category2.id)
            for category3 in categories3:
                category2.sub_cats.append({
                    'id': category3.id,
                    'name': category3.name
                })

    return categories
