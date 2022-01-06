# !usr/bin/env python
# -*- coding:utf-8 _*-
"""
@Author:Rick
@Blog:http://xxxxxx
 
@File:ccp_sms.py
@Time:2021/12/28 10:47
 
@Motto:不积跬步无以至千里，不积小流无以成江海！
"""
from ronglian_sms_sdk import SmsSDK
import json


accId = 'xxx'
accToken = 'xxx'
appId = 'xxx'


class CCP(object):
    """单例设计模式"""
    def __new__(cls, *args, **kwargs):
        # 判断是否存在类属性_instance
        if not hasattr(cls, '_instance'):
            cls._instance = super().__new__(cls, *args, **kwargs)
            cls._instance.sdk = SmsSDK(accId, accToken, appId)

        return cls._instance

    def send_message(self, tid, mobile, datas):
        sdk = self._instance.sdk
        # tid = '1'
        # mobile = '17710290729'
        # datas = ('0319', '3')
        resp = sdk.sendMessage(tid, mobile, datas)
        res = json.loads(resp)
        if res["statusCode"] == "000000":
            return 0
        else:
            return -1
