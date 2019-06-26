from django import http
from django.contrib.auth.backends import ModelBackend
import re
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, BadData
from django.conf import settings

from .models import User


# 修改用户认证后端目的：实现多账号登录（用户名、手机号）
def get_user_by_account(account):
    '''根据用户名或手机号获取user'''
    try:
        if re.match(r'^1[3-90]\d{9}$', account):
            user = User.objects.get(mobile=account)
        else:
            user = User.objects.get(username=account)
    except User.DoesNotExist:
        return None
        # return http.HttpResponseForbidden("用户不存在")
    return user


class UsernameMobileAuthBackend(ModelBackend):
   '''自定义用户认证后端 '''

   def authenticate(self, request, username=None, password=None, **kwargs):
        # 1.获取user(mobile, username)
        # 根据传入的username获取user对象。username可以是手机号也可以是账号
        user = get_user_by_account(username)

        # 判断是否为超级用户，只有超级用户才能登录后台管理系统(# 判断是否通过vue组件发送请求)
        # 如果request为None，就会找到后台管理站点超级管理员登录判断，如下：
        if request == None:
            # 再判断是否是超级管理员
            # if not user.is_superuser:
            if not user.is_staff:
               # 如果不是超级管理员，则返回None，是超级管理员才能执行后续操作
               return None

        # 2.校验密码是否正确
        if user and user.check_password(password) and user.is_active:
            # 3.返回user
            return user


def generate_email_verify_url(user):
    """生成邮件的激活验证链接"""
    serializer = Serializer(settings.SECRET_KEY, 3600 * 24)
    data = {'user_id': user.id, 'email': user.email}
    token = serializer.dumps(data).decode()
    verify_url = settings.EMAIL_VERIFY_URL + '?token=' + token
    return verify_url


def check_verify_token(token):
    """对token进行解密并获取到指定user"""
    serializer = Serializer(settings.SECRET_KEY, 3600 * 24)
    try:
        data = serializer.loads(token)
    except BadData:
        return None
    else:
        user_id = data.get('user_id')
        email = data.get('email')
        try:
            user = User.objects.get(id=user_id, email=email)
        except User.DoesNotExist:
            return None
        else:
            return user


def generate_send_sms_code_token(user):
    """获取发送短信的token"""
    serializer = Serializer(settings.SECRET_KEY, 60)

    # mobile1 = user.mobile[3:6]
    # mobile = user.mobile.replace(mobile1, "****")
    data = {'user_id': user.id, 'mobile': user.mobile}
    token = serializer.dumps(data).decode()
    return token


def check_sms_code_token(token):
    """对token进行解密并获取到指定user"""
    serializer = Serializer(settings.SECRET_KEY, 60)
    try:
        data = serializer.loads(token)
    except BadData:
        return None
    else:
        user_id = data.get('user_id')
        mobile = data.get('mobile')
        try:
            user = User.objects.get(id=user_id, mobile=mobile)
        except User.DoesNotExist:
            return None
        else:
            return user
