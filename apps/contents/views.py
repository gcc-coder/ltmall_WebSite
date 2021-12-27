from django.shortcuts import render
from django.views import View


class IndexView(View):

    """提供主页内容"""
    def get(self, request):
        return render(request, 'contents/index.html')