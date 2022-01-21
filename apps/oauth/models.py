from django.db import models
from ltmall.utils.abs_models import BaseModel


class OAuthQQUser(BaseModel):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, verbose_name='用户')
    openid = models.CharField(max_length=100, verbose_name='open_id')

    class Meta:
        db_table = 'tb_oauth_qq'
        verbose_name = 'QQ登录用户数据'
        verbose_name_plural = verbose_name