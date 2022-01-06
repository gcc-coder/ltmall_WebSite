# !usr/bin/env python
# -*- coding:utf-8 _*-
"""
@Author:Rick
@Blog:http://xxxxxx
 
@File:const.py
@Time:2021/12/27 16:40
 
@Motto:不积跬步无以至千里，不积小流无以成江海！
"""
# 验证码有效期
IMAGE_CODE_REDIS_EXPIRES = 300
SMS_CODE_REDIS_EXPIRES = 300

# 短信模板
SMS_SEND_TEMPLATE_ID = 1

# 60s内是否重复发送短信验证码的标记
SEND_SMS_CODE_FLAG = 60
