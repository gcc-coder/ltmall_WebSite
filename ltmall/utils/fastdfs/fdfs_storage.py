# !usr/bin/env python
# -*- coding:utf-8 _*-
"""
@Author：Rick
@Blog：http://xxxxxx
 
@File：fdfs_storage.py
@Time：2022/1/26 15:59
 
@Motto：不积跬步无以至千里，不积小流无以成江海！
@Description：
"""
from django.core.files.storage import Storage
from django.conf import settings


class FastDFSStorage(Storage):
    """自定义文件存储系统"""

    # def __init__(self, option=None):
    #     """
    #     构造初始化方法，可以传参
    #     :param option: Storage的IP或域名
    #     """
    #     self.fdfs_base_url = option or settings.FASTDFS_IMAGE_URL

    def _open(self, name, mode='rb'):
        pass

    def _save(self, name, content):
        pass

    def url(self, name):
        """
        返回FastDFS存储的图片的绝对URL
        :param name: SQL中存储的文件索引名称
        :return: 返回拼接的URL
        """
        # http://image.im30.top:8888/ + name
        return settings.FASTDFS_IMAGE_URL + name
        # return self.fdfs_base_url + name