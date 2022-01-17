# !usr/bin/env python
# -*- coding:utf-8 _*-
"""
@Author：Rick
@Blog：http://xxxxxx
 
@File：main.py
@Time：2022/1/6 11:57
 
@Motto：不积跬步无以至千里，不积小流无以成江海！
@Description：Celery的入口
"""
from celery import Celery

import os
if not os.getenv('DJANGO_SETTINGS_MODULE'):
    os.environ['DJANGO_SETTINGS_MODULE'] = 'ltmall.settings.dev'

# 创建celery实例
celery_app = Celery('ltmall')   # 定义名称

# 加载celery配置
celery_app.config_from_object('celery_tasks.config')

# 注册任务
celery_app.autodiscover_tasks(['celery_tasks.sms', 'celery_tasks.emails'])
