from django.shortcuts import render, redirect, reverse
from django.http import HttpResponse, JsonResponse
from django.views.generic import View
from .forms import RegisterFrom
from .models import User
from django.contrib.auth import login

# Create your views here.
def index(request):
    return render(request, 'users/index.html')


class RegisterView(View):
    """用户注册"""
    def get(self, request):
        """
        提供注册界面
        :param request: 请求对象
        :return: 注册界面
        """
        return render(request, 'users/register.html')

    def post (self, request):
        """提供用户注册逻辑, 处理POST提交的数据逻辑"""
        form = RegisterFrom(request.POST)

        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            mobile = form.cleaned_data.get('mobile')
            # 需判断用户名或手机号是否已经存在于数据库
            # user_info = User.objects.values('mobile', 'username')
            # info = [info.values() for info in user_info]
            # if (mobile not in info) and (username not in info):
            # 将用户信息保存到数据库
            try:
                user = User.objects.create_user(username=username, password=password, mobile=mobile)
            except Exception as e:
                print(e)
                return render(request, 'users/register.html', {'register_errmsg': '注册失败'})
            # 状态保持
            login(request, user)
            # 注册成功，响应结果
            # return HttpResponse('注册成功，重定向到登录页面')
            return redirect("contents:index")

        else:
            context: {
                'forms_error': form.errors.get_json_data()
            }
            return render(request, 'users/register.html', context=context)
            # return HttpResponse('验证数据无效，请检查')


class CheckUserView(View):
    """检测用户名是否重复注册"""

    def get(self, request, username):
        """
        :param username: 用户名
        :return: 返回JSON数据。count若为1，表示用户名重复
        """
        count = User.objects.filter(username=username).count()
        return JsonResponse({'code': 200, 'errmsg': 'OK', 'count': count})


class CheckMobileView(View):
    """检测手机号是否重复注册"""

    def get(self, request, mobile):
        """
        :param mobile: 手机号
        :return: 返回JSON数据。count若为1，表示手机号重复
        """
        count = User.objects.filter(mobile=mobile).count()
        return JsonResponse({'code': 200, 'errmsg': 'OK', 'count': count})