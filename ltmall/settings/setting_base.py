# !usr/bin/env python
# -*- coding:utf-8 _*-
"""
@Author:Rick
@Blog:http://xxxxxx
 
@File:setting_base.py
@Time:2021/12/17 15:07
 
@Motto:不积跬步无以至千里，不积小流无以成江海！
"""
import os
print(os.environ)

# 导入开发环境以及生产环境设置
if os.environ.get('PRODUCTION_SETTINGS', 0):
    from .dev import *
else:
    from .pro import *
