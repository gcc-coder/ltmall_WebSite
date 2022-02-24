from django.shortcuts import render, redirect, reverse
from django.views import View
from QQLoginTool.QQtool import OAuthQQ
from ltmall.settings import const
from django import http
from ltmall.utils.response_code import RETCODE
from ltmall.utils.oauth_openid import generate_access_token, check_access_token
from ltmall.utils.merge_carts import merge_carts_cookies_redis
from oauth.models import OAuthQQUser
from users.models import User
from django.contrib.auth import login
from django_redis import get_redis_connection
from users.forms import RegisterFrom

import logging


logger = logging.getLogger('django')

class QQAuthUserView(View):
    """处理QQ登录回调"""

    def get(self, request):
        # 通过回调URL，获取Authorization Code
        code = request.GET.get('code')
        if not code:
            return http.HttpResponseForbidden('获取code失败')

        # 创建oauth对象
        oauth = OAuthQQ(const.QQ_CLIENT_ID, const.QQ_CLIENT_SECRET, const.QQ_REDIRECT_URI, state=next)
        try:
            access_token = oauth.get_access_token(code)
            open_id = oauth.get_open_id(access_token)
        except Exception as e:
            logger.error(e)
            return http.HttpResponseServerError('OAuth2.0认证失败')

        try:
            oauth_user = OAuthQQUser.objects.get(openid=open_id)
        except Exception as e:
            # 没有查询到用户，则返回一个绑定的页面
            access_token_openid = generate_access_token(open_id)        # 序列化openid
            # access_token_openid 传到模板中 form参数
            context = {"access_token_openid": access_token_openid}

            # <input type="hidden" name="access_token_openid" value="{{ access_token_openid }}">
            return render(request, 'oauth_callback.html', context)
            # return render(request, 'oauth_callback.html')
        else:
            # 若查询到oauth_user的处理逻辑

            # 表示从QQ模型对象中，找到对应的用户模型对象
            qq_user = oauth_user.user
            # 状态保持
            login(request, qq_user)

            # 获取next参数
            next = request.GET.get('state')
            if next != 'None':
                response = redirect(next)
            else:
                response = redirect(reverse('contents:index'))

            # 登录时用户名写入到cookie，以进行展示，有效期3天
            response.set_cookie('username', qq_user.username, const.SET_COOKIE_EXPIRES)

            # 用户登录成功后,合并购物车
            response = merge_carts_cookies_redis(request, qq_user, response)

            # # 响应结果
            # return redirect(reverse('contents:index'))
            return response

    def post(self, request):
        """提供绑定用户注册逻辑, 处理POST提交的数据逻辑"""
        # 验证参数
        form = RegisterFrom(request.POST)

        if form.is_valid():
            # 接收参数

            password = form.cleaned_data.get('password')
            mobile = form.cleaned_data.get('mobile')
            sms_code_client = form.cleaned_data.get('sms_code')
            # 密文openid
            access_token_openid = request.POST.get('access_token_openid')
            # 校验短信验证码
            redis_conn = get_redis_connection('verify_codes')
            sms_code_server = redis_conn.get('sms_%s' % mobile)
            if sms_code_server is None:
                return render(request, 'users/oauth_callback.html', {'sms_code_errmsg': '短信验证码已经失效'})
            if sms_code_client != sms_code_server.decode():
                return render(request, 'users/oauth_callback.html', {'sms_code_errmsg': '短信验证码输入有误'})
            # 判断openid
            openid = check_access_token(access_token_openid)
            if not openid:
                return render(request, "users/oauth_callback.html", {"openid_errmsg": "openid已经失效"})

            # 使用手机号查询对应的用户
            try:
                user = User.objects.get(mobile=mobile)
            except User.DoesNotExist:
                # 1.用户不存在，新建用户
                user = User.objects.create_user(username=mobile, password=password, mobile=mobile)
            else:
                # 2.用户存在, 校验密码
                if not user.check_password(password):
                    return render(request, "users/oauth_callback.html", {"qq_login_errmsg": "账号或者密码错误"})

            # 将openid和用户绑定(新注册用户或已存在用户)
            try:
                qq_user = OAuthQQUser.objects.create(user=user, openid=openid)
            except Exception as e:
                logger.error(e)
                return render(request, "users/oauth_callback.html", {"qq_login_errmsg": "账号或者密码错误"})
            # 状态保持
            login(request, qq_user.user)
            # 响应登录结果
            next = request.GET.get('state')
            if next != 'None':
                response = redirect(next)
            else:
                response = redirect(reverse('contents:index'))

            # 设置cookies
            response.set_cookie('username', qq_user.user.username, const.SET_COOKIE_EXPIRES)
            return response


class QQAuthURLView(View):
    """提供QQ登录扫描页面"""

    def get(self, request):
        # 接收next
        next = request.GET.get('next')

        # 创建oauth对象
        oauth = OAuthQQ(const.QQ_CLIENT_ID, const.QQ_CLIENT_SECRET, const.QQ_REDIRECT_URI, state=next)

        # 生成QQ登录扫描链接地址
        login_url = oauth.get_qq_url()
        # print(login_url)

        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'login_url': login_url})

# login_url
# https://graph.qq.com/oauth2.0/show?which=error&display=pc&error=100010&which=Login&display=pc&response_type=code&client_id=101518219&redirect_uri=http%3A%2F%2Fwww.im30.top%3A8000%2Foauth_callback&state=None