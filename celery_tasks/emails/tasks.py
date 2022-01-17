# !usr/bin/env python
# -*- coding:utf-8 _*-
"""
@Author：Rick
@Blog：http://xxxxxx
 
@File：tasks.py
@Time：2022/1/17 15:26
 
@Motto：不积跬步无以至千里，不积小流无以成江海！
@Description：
"""
from django.conf import settings
from django.core.mail import send_mail
from celery_tasks.main import celery_app
import logging


logger = logging.getLogger('django')


# 保证celery识别任务, name是任务的名字
# retry_backoff:发送异常时，自动重试的时间间隔  retry_backoff*2^(n-1)s
@celery_app.task(bind=True, name='send_email', retry_backoff=3)
# @celery_app.task(name="send_email")
def send_validate_email(self, to_email, verify_url):
    html_message = '<p>尊敬的用户您好！</p>' \
                   '<p>感谢您使用商城。</p>' \
                   '<p>您的邮箱为：%s 。请点击此链接激活您的邮箱：</p>' \
                   '<p><a href="%s">%s<a></p>' % (to_email, verify_url, verify_url)
    try:
        send_mail(subject=settings.EMAIL_SUBJECT, message='', from_email=settings.EMAIL_HOST_USER,
                  recipient_list=[to_email], html_message=html_message)
    except Exception as e:
        logger.error(e)
        # 重新发送邮件的次数
        raise self.retry(exc=e, max_retries=3)