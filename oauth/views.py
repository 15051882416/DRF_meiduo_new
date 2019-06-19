import re

from django.contrib.auth import login
from django.shortcuts import render, redirect
from QQLoginTool.QQtool import OAuthQQ
from django.views import View
from django.conf import settings
from django import http
from django_redis import get_redis_connection

from carts.utils import merge_cart_cookie_to_redis
from oauth.utils import generate_openid_signature, check_openid_signature
from users.models import User
from .models import OAuthQQUser
from meiduo_mall.utils.response_code import RETCODE

import logging
logger = logging.getLogger('django')


class QQAuthURLView(View):
    '''提供QQ登录url'''
    def get(self, request):
        # 获取查询参数中的next,获取用户从哪里去到login界面
        next = request.GET.get('next') or '/'

        # QQ_CLIENT_ID = '101518219'
        # QQ_CLIENT_SECRET = '418d84ebdc7241efb79536886ae95224'
        # QQ_REDIRECT_URI = 'http://www.meiduo.site:8000/oauth_callback'

        # 创建QQSDK对象
        auth_qq = OAuthQQ(client_id=settings.QQ_CLIENT_ID,   # appid
                          client_secret=settings.QQ_CLIENT_SECRET,   # appkey
                          redirect_uri=settings.QQ_REDIRECT_URI,  # 登录成功之后回到美多的那个界面/回调地址
                          state=next)   # 记录界面跳转来源
        # 调用SDK中的get_qq_url方法得到拼接好的QQ登录url
        login_url = auth_qq.get_qq_url()

        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'login_url': login_url})


class QQAuthView(View):
    """QQ登录成功的回调处理"""
    def get(self, request):
        # 1.获取查询参数中的code
        code = request.GET.get('code')
        # 2.校验,如果code没有获取到
        if code is None:
            return http.HttpResponseForbidden('缺少code')
        # 再次创建一个QQ登录的SDK对象
        auth_qq = OAuthQQ(client_id=settings.QQ_CLIENT_ID,  # appid
                          client_secret=settings.QQ_CLIENT_SECRET,  # appkey
                          redirect_uri=settings.QQ_REDIRECT_URI  # 登录成功之后回到美多的那个界面/回调地址
                          )
        try:
            # 调用SDK中的get_access_token(code)方法得到access_token
            access_token = auth_qq.get_access_token(code)
            # 调用SKD中的get_open_id(access_token)方法得到openid
            openid = auth_qq.get_open_id(access_token)
        except Exception as e:
            logger.error(e)
            return http.HttpResponseServerError('QQ的OAuth2.0认证失败')

        try:
            # 查询表中否有当前这个openid
            oauth_qq = OAuthQQUser.objects.get(openid=openid)
        except OAuthQQUser.DoesNotExist:
            # 如果没有查询到openid，说明此QQ是一个新的还没有绑定过美多用户，应该绑定
            openid = generate_openid_signature(openid)
            return render(request, 'oauth_callback.html', {'openid': openid})

        else:
            # 如果查询到openid，说明之前已经绑定，直接代表登陆成功
            user = oauth_qq.user    # 获取openid所关联的用户
            login(request, user)    # 状态保持
            next = request.GET.get("state")   # 获取用户界面来源
            response = redirect(next or '/')     # 创建响应对象及重定向
            response.set_cookie('username', user.username, max_age=settings.SESSION_COOKIE_AGE)# 向cookie中设置username以备在状态栏显示登录用户的用户名

            # 在此就做合并购物车
            merge_cart_cookie_to_redis(request, response)

            return response

    def post(self, request):
        """美多用户绑定到openid处理"""

        # 1.接收表单参数
        # query_dict = request.POST
        mobile = request.POST.get('mobile')
        password = request.POST.get('password')
        sms_code = request.POST.get('sms_code')
        openid = request.POST.get('openid')

        # 2.校验参数（参数是否齐全）
        if all([mobile, password, sms_code, openid]) is False:
            return http.HttpResponseForbidden("缺少必传参数")

        if not re.match(r'^[0-9A-Za-z]{8,20}$', password):
            return http.HttpResponseForbidden('请输入8-20位的密码')

        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return http.HttpResponseForbidden('请输入5-20个字符的用户名')

        # 2.1 短信验证码后期再补充校验逻辑
        redis_conn = get_redis_connection('verify_code')
        # 2.2 获取redis中的短信验证码
        sms_code_server = redis_conn.get('sms_%s' % mobile)
        # 2.3  删除redis中的短信验证码,让验证码只能用一次
        redis_conn.delete('sms_%s' % mobile)

        # 2.4 校验短信验证码是否过期
        if sms_code_server is None:
            return http.HttpResponseForbidden('短信验证码过期')
        # 2.5 把bytes类型转换成字符串
        sms_code_server = sms_code_server.decode()
        # 2.6 判断前端和后端的短信验证码是否一致
        if sms_code != sms_code_server:
            return http.HttpResponseForbidden('请输入正确的短信验证码')

        # 3.对openid进行解密
        openid = check_openid_signature(openid)
        if openid is None:
            return http.HttpResponseForbidden("openid无效")

        # 先用手机号查询user表,判断当前手机号是新用户,还是已存在用户
        try:
            user = User.objects.get(mobile=mobile)
        except User.DoesNotExist:
            # 查询不到，说明是新用户，需要创建一个用户
            user = User.objects.create_user(mobile=mobile, password=password, username=mobile)
        else:
            # 校验这个旧用户的密码是否正确
            if user.check_password(password) is False:
                return render(request, 'oauth_callback.html', {'account_errmsg': '用户名或密码错误'})

        # openid和用户绑定
        OAuthQQUser.objects.create(
             openid=openid,
             user=user
         )

        login(request, user)  # 状态保持
        next = request.GET.get('state')  # 获取用户界面来源
        response = redirect(next or '/')  # 创建响应对象及重定向
        # 向cookie中设置username以备在状态栏显示登录用户的用户名
        response.set_cookie('username', user.username, max_age=settings.SESSION_COOKIE_AGE)

        # 在此就做合并购物车
        merge_cart_cookie_to_redis(request, response)

        # 响应
        return response







