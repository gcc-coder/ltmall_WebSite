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


class RegisterFrom(forms.Form):
    username = forms.CharField(max_length=10, min_length=3, required=True, error_messages={'max_length': '用户名字符不能超过10个'})
    password = forms.CharField(max_length=8, min_length=6)
    password2 = forms.CharField(max_length=8, min_length=6)
    mobile = forms.CharField(max_length=11, min_length=11)

    # 短信和图片验证码
    # sms_code = forms.CharField(max_length=6)
    # image_code = forms.CharField(max_length=6)

    def clean(self):
        cleaned_data = super().clean()
        pwd = cleaned_data.get('password')
        pwd2 = cleaned_data.get('password2')

        if pwd != pwd2:
            print(forms.ValidationError('两次密码不一致')) # ['两次密码不一致']
            raise forms.ValidationError('两次密码不一致')

        return cleaned_data
