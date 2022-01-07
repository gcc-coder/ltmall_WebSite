# !usr/bin/env python
# -*- coding:utf-8 _*-
"""
@Author:Rick
@Blog:http://xxxxxx
 
@File:forms.py
@Time:2021/12/20 20:03
 
@Motto:不积跬步无以至千里，不积小流无以成江海！
"""
from django import forms
from .models import User


class RegisterFrom(forms.Form):
    username = forms.CharField(max_length=11, min_length=3, required=True, error_messages={'max_length': '用户名字符不能超过10个'})
    password = forms.CharField(max_length=8, min_length=6)
    password2 = forms.CharField(max_length=8, min_length=6)
    mobile = forms.CharField(max_length=11, min_length=11)

    # 仅检测短信和图片验证码位数，具体逻辑不在此处实现
    sms_code = forms.CharField(max_length=6, min_length=6)
    # image_code = forms.CharField(max_length=6)

    def clean_pwd(self):
        # 重写clean方法
        cleaned_data = super().clean()
        pwd = cleaned_data.get('password')
        pwd2 = cleaned_data.get('password2')

        if pwd != pwd2:
            # print(forms.ValidationError('两次密码不一致'))     # ['两次密码不一致']
            raise forms.ValidationError('两次密码不一致')

        return cleaned_data

    # 可通过ajax方式定义接口，来验证用户名和手机号，此处可省略
    def clean_username(self):
        username = self.cleaned_data.get('username')
        username_exists = User.objects.filter(username=username).exists()
        if username_exists:
            raise forms.ValidationError('用户名已经存在')

        return username

    def clean_mobile(self):
        mobile = self.cleaned_data.get('mobile')
        mobile_exists = User.objects.filter(mobile=mobile).exists()
        if mobile_exists:
            raise forms.ValidationError('手机号码已经存在')

        return mobile


class LoginForm(forms.Form):
    username = forms.CharField(max_length=11, min_length=4)
    password = forms.CharField(max_length=8, min_length=6)