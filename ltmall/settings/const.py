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

# Cookie有效期
SET_COOKIE_EXPIRES = 3600*24*3

# oauth Access_Token的过期时间
ACCESS_TOKEN_EXPIRES = 300

# 省市区缓存数据过期时间
AREAS_CACHE_EXPIRES = 3600

# QQ登录的配置参数
QQ_CLIENT_ID = '101518219'
QQ_CLIENT_SECRET = '418d84ebdc7241efb79536886ae95224'
QQ_REDIRECT_URI = 'http://www.meiduo.site:8000/oauth_callback'

# 邮箱验证
VERIFY_EMAIL_URL = 'http://www.im30.top:8000/users/emails/verification/'