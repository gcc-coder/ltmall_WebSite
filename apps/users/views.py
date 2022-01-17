from django.shortcuts import render, redirect, reverse
from django.http import HttpResponse, JsonResponse, HttpResponseForbidden, HttpResponseServerError
from django.views.generic import View
from .forms import RegisterFrom, LoginForm
from .models import User
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from ltmall.utils.loginRequire_email import LoginRequiredJsonMixin
from django_redis import get_redis_connection
from ltmall.utils.response_code import RETCODE
from django.core.mail import send_mail
from django.db.models import Q
from django.conf import settings
import json, re, logging


logger = logging.getLogger('django')


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

    def post(self, request):
        """提供用户注册逻辑, 处理POST提交的数据逻辑"""
        # 验证参数
        form = RegisterFrom(request.POST)

        if form.is_valid():
            # 接收参数
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            mobile = form.cleaned_data.get('mobile')
            sms_code_client = form.cleaned_data.get('sms_code')

            # 校验短信验证码
            redis_conn = get_redis_connection('verify_codes')
            sms_code_server = redis_conn.get('sms_%s' % mobile)
            if sms_code_server is None:
                return render(request, 'users/register.html', {'sms_code_errmsg': '短信验证码已经失效'})
            if sms_code_client != sms_code_server.decode():
                return render(request, 'users/register.html', {'sms_code_errmsg': '短信验证码输入有误'})
            # 需判断用户名或手机号是否已经存在于数据库
            # user_info = User.objects.values('mobile', 'username')
            # info = [info.values() for info in user_info]
            # if (mobile not in info) and (username not in info):

            # 将用户信息保存到数据库
            try:
                user = User.objects.create_user(username=username, password=password, mobile=mobile)
            except Exception as e:
                return render(request, 'users/register.html', {'register_errmsg': '注册失败'})
            # 状态保持
            login(request, user)
            # 注册成功，响应结果
            # return HttpResponse('注册成功，重定向到登录页面')
            return redirect("contents:index")

        else:
            print(form.errors.get_json_data())
            context = {
                'forms_errors': form.errors
            }
            return render(request, 'users/register.html', context=context)
            # return HttpResponse('验证数据无效，请检查')


# 定义ajax所用接口，用来验证用户名和手机号是否已经注册
class CheckUserView(View):
    """检测用户名是否重复注册"""

    def get(self, request, username):
        """
        :param username: 用户名
        :return: 返回JSON数据。count若为1，表示用户名重复
        """
        count = User.objects.filter(username=username).count()
        return JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'count': count})


class CheckMobileView(View):
    """检测手机号是否重复注册"""

    def get(self, request, mobile):
        """
        :param mobile: 手机号
        :return: 返回JSON数据。count若为1，表示手机号重复
        """
        count = User.objects.filter(mobile=mobile).count()
        return JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'count': count})


class LoginView(View):
    """用户名登录逻辑"""

    def get(self, request):
        """
        提供登录界面
        :return: 渲染到登录界面
        """
        return render(request, "users/login.html")

    def post(self, request):
        """
        实现登录逻辑
        :return: 登录结果
        """
        login_form = LoginForm(request.POST)

        if login_form.is_valid():
            # 接收参数
            username = login_form.cleaned_data.get('username')
            password = login_form.cleaned_data.get('password')
            # 如果没有用form表单验证的话,不能用login_form.cleaned_data
            remembered = request.POST.get('remembered')

            # 校验参数: 用户名或手机号
            user_count = User.objects.filter(Q(username=username) | Q(mobile=username)).count()
            if user_count == 0:
                return render(request, "users/login.html", {"errmsg": "该账户没有注册"})

            # 认证登录用户
            # user = User.objects.get(username=username)
            # print(user.check_password(password))      # 若是未注册用户，会报错
            user = authenticate(username=username, password=password)
            # print(user)   # 未注册，返回None
            if user is None:
                return render(request, "users/login.html", {"errmsg": "用户名或密码不正确"})

            # 状态保持
            login(request, user)

            # 使用remembered保持登录状态
            if remembered != 'on':
                # 如果没有记住登录状态, 状态保持在浏览器关闭的时候就销毁
                request.session.set_expiry(0)
            else:
                # 如果记住登录状态 默认是两周
                request.session.set_expiry(None)

            next = request.GET.get('next')
            if next:
                response = redirect(next)
            else:
                response = redirect(reverse('contents:index'))
            response.set_cookie('username', user.username, max_age=3600*24*3)   # 保存3天
            # 响应登录结果
            return response

        else:
            # print(login_form.errors.get_json_data())
            context = {
                'forms_errors': login_form.errors
            }
            return render(request, 'users/login.html', context=context)


class LogoutView(View):
    """用户退出登录逻辑"""

    def get(self, request):
        """实现退出登录功能"""
        # 清除状态保持信息
        logout(request)

        # 重定向到首页或登录页面
        # response = redirect(reverse("contents:index"))
        response = redirect(reverse("users:login"))
        # 删除cookies信息
        response.delete_cookie('username')

        # 响应结果
        return response


# LoginRequiredMixin用于判断用户是否登录，及处理逻辑
class UserCenterView(LoginRequiredMixin, View):
    """显示用户中心逻辑"""

    def get(self, request):
        """响应用户中心页面"""
        # login_url = '/login/'
        # redirect_field_name = 'redirect_to'

        # if request.user.is_authenticated:
        #     return render(request, "users/user_center_info.html")
        # else:
        #     return redirect(reverse('users:login'))

        # print(request.user)
        context = {
            'username': request.user.username,
            'mobile': request.user.mobile
        }

        return render(request, "users/user_center_info.html", context)


class EmailView(LoginRequiredJsonMixin, View):
    """添加邮箱"""

    def put(self, request):
        # 将获取的put，转换为QueryDict
        # from django.http import QueryDict
        # put = QueryDict(request.body)   # <QueryDict: {'{"email":"firelong.guo@hotmail.com"}': ['']}>
        put = request.body.decode()
        email = json.loads(put).get('email')

        # 校验邮箱: ^[a-zA-Z0-9_-]+@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+)+$
        # rui-long.guo@hotmail.com
        if not re.match(r'^[a-zA-Z0-9_\.-]+@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+)+$', email):
            # return HttpResponseForbidden('email参数有误')
            print("email地址无效")
            return render(request, "users/user_center_info.html", {"errmsg": "email地址无效"})

        # 根据当前登录的用户, 保存到数据库中其对应的email字段
        try:
            request.user.email = email
            request.user.save()
        except Exception as e:
            logger.error(e)
            return HttpResponseServerError('邮箱激活失败')

        # 发送验证邮件
        # send_mail(subject, message, from_email, recipient_list, html_message=None)
        html_message = '<p>尊敬的用户您好！</p>' \
                       '<p>感谢您使用商城。</p>' \
                       '<p>您的邮箱为：%s 。请点击此链接激活您的邮箱：</p>' \
                       '<p><a href="%s">%s<a></p>' % (email, 'www.baidu.com', 'www.baidu.com')
        try:
            # 同步执行
            send_mail(subject=settings.EMAIL_SUBJECT, message='', from_email=settings.EMAIL_HOST_USER, recipient_list=[email], html_message=html_message)
        except Exception as e:
            logger.error(e)
            print(e)

        return JsonResponse({'code': RETCODE.OK, 'errmsg': 'ok'})
