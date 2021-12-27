from django.shortcuts import render
from django.views.generic import View


class ImageCodeView(View):
    """图形验证码逻辑"""

    def get(self, request, uuid):
        """
        :param uuid: 通用唯一识别符, 用于标识图片验证码属于哪个用户
        :return: image/jpeg 或 image/png
        """
