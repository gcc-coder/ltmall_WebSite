# !usr/bin/env python
# -*- coding:utf-8 _*-
"""
@Author：Rick
@Blog：http://xxxxxx
 
@File：tasks.py
@Time：2022/1/6 12:20
 
@Motto：不积跬步无以至千里，不积小流无以成江海！
@Description：定义任务
"""
from celery_tasks.sms.ronglianyun.ccp_sms import CCP
from celery_tasks.sms import const
from celery_tasks.main import celery_app


# 保证celery识别任务, name是任务的名字
@celery_app.task(name="send_sms_code")
def send_sms_code(mobile, sms_code):
    """
    发送短信验证码的异步任务
    :param mobile: 手机号
    :param sms_code: 短信验证码
    :return: 成功 0 失败 -1
    """
    result = CCP().send_message(const.SEND_SMS_TEMPLATE_ID, mobile, (sms_code, const.SMS_CODE_REDIS_EXPIRES // 60))

    return result