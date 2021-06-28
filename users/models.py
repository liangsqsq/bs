from datetime import datetime

from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.
class UserProfile(AbstractUser):
    realname= models.CharField(null=True,max_length=10)
    group_type = models.IntegerField(null=True, default=1)

    class Meta(AbstractUser.Meta):
        pass


class user_log(models.Model):
    uid = models.IntegerField(null=True)
    start_time = models.IntegerField(null=True)
    end_time = models.IntegerField(null=True)


class group(models.Model):
    gname = models.CharField(max_length=10, null=True)


class EmailVerifyRecord(models.Model):
    # 验证码
    code = models.CharField(max_length=20, verbose_name=u"验证码")
    email = models.EmailField(max_length=50, verbose_name=u"邮箱")
    # 包含注册验证和找回验证
    send_type = models.CharField(verbose_name=u"验证码类型", max_length=10,
                                 choices=(("register", u"注册"), ("forget", u"找回密码")))
    send_time = models.DateTimeField(verbose_name=u"发送时间", default=datetime.now)

    class Meta:
        verbose_name = u"邮箱验证码"
        verbose_name_plural = verbose_name
    def __unicode__(self):
        return '{0}({1})'.format(self.code, self.email)
