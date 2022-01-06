# !usr/bin/env python
# -*- coding:utf-8 _*-
"""
@Author：Rick
@Blog：http://xxxxxx
 
@File：const.py
@Time：2022/1/6 12:21
 
@Motto：不积跬步无以至千里，不积小流无以成江海！
@Description：定义celery所用常量
"""
# 图形验证码有效期  单位：秒
IMAGE_CODE_REDIS_EXPIRES = 300

# 短信验证码有效期  单位：秒
SMS_CODE_REDIS_EXPIRES = 300

# 短信模板
SEND_SMS_TEMPLATE_ID = 1

# 60s内是否重复发送的标记
SEND_SMS_CODE_FLAG = 60