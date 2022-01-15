# !usr/bin/env python
# -*- coding:utf-8 _*-
"""
@Author：Rick
@Blog：http://xxxxxx
 
@File：abs_models.py
@Time：2022/1/12 17:48
 
@Motto：不积跬步无以至千里，不积小流无以成江海！
@Description：
"""
from django.db import models


class BaseModel(models.Model):
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        # 数据库迁移时，不会创建该表
        abstract = True