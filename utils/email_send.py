from random import Random  # 用于生成随机码

from django.core.mail import send_mail  # 发送邮件模块
from users.models import EmailVerifyRecord  # 邮箱验证model
from DockerCloud.settings import EMAIL_FROM  # setting.py添加的的配置信息


# 生成随机字符串
def random_str(randomlength=8):
    str = ''
    chars = 'AaBbCcDdEeFfGgHhiJjKkLMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789'
    length = len(chars) - 1
    random = Random()
    for i in range(randomlength):
        str += chars[random.randint(0, length)]
    return str


def send_register_email(email, send_type="register"):
    email_record = EmailVerifyRecord()
    # 将给用户发的信息保存在数据库中
    code = random_str(6)
    email_record.code = code
    email_record.email = email
    email_record.send_type = send_type
    email_record.save()
    # 初始化为空
    email_title = ""
    email_body = ""
    # 如果为注册类型
    if send_type == "register":
        email_title = "注册激活码"
        email_body = "你的验证码为:{0}".format(code)
        # 发送邮件
        send_status = send_mail(email_title, email_body, EMAIL_FROM, [email])
        if send_status:
            pass


def send_sucess_email(email, vm, send_type="success"):
    email_record = EmailVerifyRecord()
    # 将给用户发的信息保存在数据库中
    code = random_str(6)
    email_record.code = code
    email_record.email = email
    email_record.send_type = send_type
    email_record.save()

    if send_type == "success":
        email_title = "虚拟机申请成功"
        email_body = "你在{0}申请的{1}虚拟机已经通过审核，请查看你的虚拟机:\n用户名{2}\n处理器{3}核 内存{4}G 硬盘{5}G\n操作系统{6}\n连接地址{7}:{8}". \
            format(vm.start_time, vm.region.domain, vm.os.default_user, vm.vCPUs, vm.memory, vm.diskSize,
                   vm.os.os_version, vm.gateway_ip, str(vm.conn_port))
        # 发送邮件
        send_status = send_mail(email_title, email_body, EMAIL_FROM, [email])
        if send_status:
            pass
