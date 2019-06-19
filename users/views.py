from random import randint

from goods.models import SKU
from .utils import generate_email_verify_url, check_verify_token
import re, json
from django import http
from django.conf import settings
from django.contrib.auth import login, authenticate, logout, mixins
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.views import View
from django_redis import get_redis_connection
from django.core.cache import cache
from django_redis import get_redis_connection

from .utils import get_user_by_account
from meiduo_mall.utils.response_code import RETCODE
from users.models import User, Address
from celery_tasks.email.tasks import send_verify_email
from meiduo_mall.utils.Views import LoginRequiredMixin
from . import constants


import logging
from carts.utils import merge_cart_cookie_to_redis
logger = logging.getLogger('django')
from .utils import generate_send_sms_code_token, check_sms_code_token
from orders.models import OrderInfo, OrderGoods


class RegisterView(View):
    """用户注册"""

    def get(self, request):

        return render(request, "register.html")

    def post(self, request):
        '''逻辑功能注册'''
        # 接收前端传入的表单数据
        # 用户名, 密码, 密码2, 手机号, 短信验证码, 同意协议
        query_dict = request.POST
        username = query_dict.get("username")
        password = query_dict.get("password")
        password2 = query_dict.get("password2")
        mobile = query_dict.get("mobile")
        sms_code = query_dict.get('sms_code')
        allow = query_dict.get("allow")

        if all([username, password, password2, mobile, sms_code, allow]) is False:
            return http.HttpResponseForbidden("缺少必传参数")

        if not re.match(r'^[a-zA-Z0-9_-]{5,20}$', username):
            return http.HttpResponseForbidden("请输入5-20个字符的用户名")
        if not re.match(r'^[0-9A-Za-z]{8,20}$', password):
            return http.HttpResponseForbidden("请输入8-20位的密码")
        if password != password2:
            return http.HttpResponseForbidden("两次输入的密码不一致")
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return http.HttpResponseForbidden("请输入正确的手机号码")


        #  短信验证码后期再补充校验逻辑

        redis_conn = get_redis_connection('verify_code')
        # 2.2 获取redis中的短信验证码
        sms_code_server = redis_conn.get('sms_%s' % mobile)
        # 2.3  删除redis中的短信验证码,让验证码只能用一次
        # sms_code_server.delete('sms_code_%s' % mobile)  <<------->>错误代码
        redis_conn.delete("sms_%s" % mobile)

        # 2.4 校验短信验证码是否过期
        if sms_code_server is None:
            return http.HttpResponseForbidden('短信验证码过期')
        # 2.5 把bytes类型转换成字符串
        sms_code_server = sms_code_server.decode()
        # 2.6 判断前端和后端的短信验证码是否一致
        if sms_code_server != sms_code:
            return http.HttpResponseForbidden('请输入正确的短信验证码')


        # 3.保存数据,创建user
        user = User.objects.create_user(username=username, password=password, mobile=mobile)

        # 当用户登录后 将用户的user.id值存储到session   生成sessionid  cookie
        # 状态保持(记录用户的登录状态)
        login(request, user)

        # 向cookie中写用户名，用于客户端显示
        response = redirect('/')
        response.set_cookie('username', username, max_age=constants.USERNAME_COOKIE_EXPIRES)

        # 响应
        return response

        # # 响应:重定向到首页
        # return redirect("/")


class UsernameCountView(View):
    """判断用户名是否重复注册"""
    def get(self, request, username):
        # 获取当前username在数据库中的数量 只会为0, 或1
        count = User.objects.filter(username=username).count()
        response_data = {'count': count, 'code': RETCODE.OK, 'errmsg': 'ok'}
        return http.JsonResponse(response_data)


class MobileCountView(View):
    """判断手机号是否重复注册"""
    def get(self, request, mobile):
        # 获取当前mobile在数据库中的数量 只会为0, 或1
        count = User.objects.filter(mobile=mobile).count()
        response_data = {'count': count, 'code': RETCODE.OK, 'errmsg': 'ok'}
        return http.JsonResponse(response_data)


class LoginView(View):
    """用户登录"""
    # 提供登录界面
    def get(self, request):
        return render(request, 'login.html')

    def post(self, request):
        """用户登录逻辑"""
        # 1.接收表单数据
        username = request.POST.get("username")
        password = request.POST.get("password")
        remembered = request.POST.get("remembered")

        # 2.校验
        # try:
        #     user = User.objects.get(username=username)
        # except User.DoesNotExist:
        #     return
        #
        # if user.check_password(password) is False:
        #     return
        # if re.match(r'^1[3-9]\d{9}$', username):
        #     User.USERNAME_FIELD = 'mobile'

        # 2.校验,认证登录用户
        user = authenticate(request, username=username, password=password)

        if user is None:
            return render(request, 'login.html', {'account_errmsg': '用户名或密码错误'})
        # 3.状态保持
        login(request, user)

        # 如果用户没有点击记住登录( 设置状态保持的周期)
        if remembered != 'on':
            # 没有记住用户：浏览器会话结束就过期, 默认是两周
            request.session.set_expiry(0)

        # # 响应登录结果,重定向到首页
        # return redirect('/')

        # 以下代码实现的功能:(首页用户名展示)

        # session如果会话结束就过期,应该设置过期时间为0,
        # 但是cookie如果设置会话结束就过期不能写0,应该写None
        next = request.GET.get('next')   # 尝试性去获取来源查询参数
        response = redirect('/')
        # 登录时用户名写入到cookie
        response.set_cookie('username', user.username,
                            max_age=settings.SESSION_COOKIE_AGE if remembered else None)

        # 在此就做合并购物车
        merge_cart_cookie_to_redis(request, response)

        # 重定向到首页
        return response


class LogoutView(View):
    """退出登录"""
    def get(self, request):
        # 1.清除状态保持信息,清理session
        logout(request)
        # 2.退出登录,创建响应对象之重定向到登录页
        response = redirect('/login/')
        # 3.退出登录时,清除cookie中的username
        response.delete_cookie('username')
        # 4.响应
        return response


# 判断用户是否登录的3种方法: 展示用户中心界面

# class UserInfoView(View):
#     """展示用户中心界面"""
#     def get(self, request):
#         # return render(request, 'user_center_info.html')
#
#         # 判断用户是否登录,登录后再显示用户中心界面,没登录重定向到登录页
#         if request.user.is_authenticated:
#             return render(request, 'user_center_info.html')
#         else:
#             return redirect('/login/?next=/info/')


# class UserInfoView(View):
#     """展示用户中心界面"""
#     @method_decorator(login_required)
#     def get(self, request):
#         """展示用户中心界面"""
#         return render(request, 'user_center_info.html')


class UserInfoView(mixins.LoginRequiredMixin, View):
    """展示用户中心"""
    def get(self, request):
        """展示用户中心界面"""
        return render(request, 'user_center_info.html')


class EmailView(mixins.LoginRequiredMixin, View):
    """设置用户邮箱"""
    def put(self, request):
        """实现添加邮箱逻辑"""
        # 接收请求体数据参数
        json_dict = json.loads(request.body.decode())
        email = json_dict.get("email")
        # 校验参数
        if not email:
            return http.HttpResponseForbidden({'code': RETCODE.NECESSARYPARAMERR, 'errmsg': '缺少email参数'})
        if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            return http.HttpResponseForbidden({'code': RETCODE.EMAILERR, 'errmsg': '邮箱格式错误'})

        # 修改用户的email字段
        user = request.user
        # user.email = email
        # user.save()
        User.objects.filter(username=user.username, email='').update(email=email)
        # 在此就应该对当前设置的邮箱发一封激活邮件
        # from django.core.mail import send_mail
        # send_mail()

        # 生成邮箱激活url
        verify_url = generate_email_verify_url(user)
        # 使用celery异步发送邮件
        send_verify_email.delay(email, verify_url)
        # 响应
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '添加邮箱成功'})


class VerifyEmailView(View):
    """激活邮箱"""
    def get(self, request):
        # 接收参数中的token
        token = request.GET.get("token")
        if token is None:
            return http.HttpResponseForbidden("缺少token参数")
        # 对token进行解密并获取user
        user = check_verify_token(token)
        if user is None:
            return http.HttpResponseForbidden("token无效")
        user.email_active = True
        user.save()
        return redirect('/info/')


class AddressView(LoginRequiredMixin):
    """用户收货地址"""
    def get(self, request):
        """提供收货地址界面"""
        # 获取用户地址列表
        user = request.user
        address_qs = Address.objects.filter(user=user, is_delete=False)
        address_model_list = []
        for address_model in address_qs:
            address_dict = {
                "id": address_model.id,
                "title": address_model.title,
                "receiver": address_model.receiver,
                "province": address_model.province.name,
                "province_id": address_model.province_id,
                "city": address_model.city.name,
                "city_id": address_model.city_id,
                "district": address_model.district.name,
                "district_id": address_model.district_id,
                "place": address_model.detail_address,
                "mobile": address_model.mobile,
                "tel": address_model.phone,
                "email": address_model.email
            }
            address_model_list.append(address_dict)
        context = {
            "default_address_id": user.default_address_id,
            "addresses": address_model_list
        }

        return render(request, 'user_center_site.html', context)


# class AreasView(View):
#     """省市区数据"""
#     def get(self, request):
#         """提供省市区数据"""
#         area_id = request.GET.get("area_id")
#         if not area_id:
#             # 读取省份缓存数据
#             province_list = cache.get("province_list")
#             if not province_list:
#                 # 提供省份数据
#                 try:
#                     province_qs = Area.objects.filter(parent=None)
#                     province_list = []
#                     for province_model in province_qs:
#                         province_list.append({'id': province_model.id, 'name': province_model.name})
#                 except Exception as e:
#                     logger.error(e)
#                     return http.JsonResponse({"code": RETCODE.DBERR, 'errmsg': '省份数据错误'})
#                 # 存储省份缓存数据
#                 cache.set("province_list", province_list, 3600)
#             # 响应省份数据
#             return http.JsonResponse({"code": RETCODE.OK, "errmsg": "OK", "province_list": province_list})
#
#         else:
#             # 读取市或区缓存数据
#             sub_data = cache.get("sub_model_%s" % area_id)
#             if not sub_data:
#                 # 提供市或区的数据
#                 try:
#                     # 查询市或区的父级数据
#                     parent_model = Area.objects.get(id=area_id)
#                     sub_model_qs = parent_model.subs.all()
#                     sub_model_list = []
#                     for sub_model in sub_model_qs:
#                         sub_model_list.append({"id": sub_model.id, "name": sub_model.name})
#
#                     sub_data = {
#                         "id": parent_model.id,  # 父级pk
#                         "name": parent_model.name,  # 父级name
#                         "subs": sub_model_list  # 父级的子集
#                     }
#                 except Exception as e:
#                     logger.error(e)
#                     return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '城市或区数据错误'})
#                 # 存储市或区缓存数据
#                 cache.set("sub_model_%s" % area_id, sub_data, 3600)
#
#             return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', "sub_data": sub_data})


class CreatAddressView(LoginRequiredMixin):
    """新增地址"""
    def post(self, request):

        # 判断是否超过地址上限：最多20个
        count = request.user.addresses.count()
        if count > 20:
            return http.JsonResponse({"code": RETCODE.THROTTLINGERR, 'errmsg': '超过地址数量上限'})

        # 接收参数
        json_dict = json.loads(request.body.decode())
        receiver = json_dict.get('receiver')
        province_id = json_dict.get('province_id')
        city_id = json_dict.get('city_id')
        district_id = json_dict.get('district_id')
        place = json_dict.get('place')
        mobile = json_dict.get('mobile')
        tel = json_dict.get('tel')
        email = json_dict.get('email')
        # 校验参数
        if not all([receiver, province_id, city_id, district_id, place, mobile]):
            return http.HttpResponseForbidden("缺少必传参数")
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return http.HttpResponseForbidden("参数mobile有误")
        if tel:
            if not re.match(r'^(0[0-9]{2,3}-)?([2-9][0-9]{6,7})+(-[0-9]{1,4})?$', tel):
                return http.HttpResponseForbidden('参数tel有误')
        if email:
            if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
                return http.HttpResponseForbidden('参数email有误')

        try:
            # 保存地址信息
            address = Address.objects.create(
                user=request.user,
                title=receiver,
                receiver=receiver,
                province_id=province_id,
                city_id=city_id,
                district_id=district_id,
                detail_address=place,
                mobile=mobile,
                phone=tel,
                email=email
            )
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '新增地址失败'})
        # 设置默认地址
        if not request.user.default_address:
            request.user.default_address = address
            request.user.save()
        # 新增地址成功，将新增的地址响应给前端实现局部刷新
        address_dict = {
            "id": address.id,
            "title": address.title,
            "receiver": address.receiver,
            "province": address.province.name,
            "province_id": address.province.id,
            "city": address.city.name,
            "city_id": address.city.id,
            "district": address.district.name,
            "district_id": address.district.id,
            "place": address.detail_address,
            "mobile": address.mobile,
            "tel": address.phone,
            "email": address.email
        }
        # 响应保存结果
        return http.JsonResponse({"code": RETCODE.OK, "errmsg": "OK", "address": address_dict})


class UpdateDestroyAddressView(LoginRequiredMixin):
    """修改地址"""
    def put(self, request, address_id):
        # 接收参数
        json_dict = json.loads(request.body.decode())
        receiver = json_dict.get('receiver')
        province_id = json_dict.get('province_id')
        city_id = json_dict.get('city_id')
        district_id = json_dict.get('district_id')
        place = json_dict.get('place')
        mobile = json_dict.get('mobile')
        tel = json_dict.get('tel')
        email = json_dict.get('email')
        # 校验参数
        if not all([receiver, province_id, city_id, district_id, place, mobile]):
            return http.HttpResponseForbidden("缺少必传参数")
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return http.HttpResponseForbidden("参数mobile有误")
        if tel:
            if not re.match(r'^(0[0-9]{2,3}-)?([2-9][0-9]{6,7})+(-[0-9]{1,4})?$', tel):
                return http.HttpResponseForbidden('参数tel有误')
        if email:
            if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
                return http.HttpResponseForbidden('参数email有误')

        # 判断地址是否存在,并更新地址信息
        try:

            Address.objects.filter(id=address_id).update(
                user=request.user,
                title=receiver,
                receiver=receiver,
                province_id=province_id,
                city_id=city_id,
                district_id=district_id,
                detail_address=place,
                mobile=mobile,
                phone=tel,
                email=email
            )
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '新增地址失败'})

        # 构造响应数据
        address = Address.objects.get(id=address_id)
        address_dict = {
            "id": address.id,
            "title": address.title,
            "receiver": address.receiver,
            "province": address.province.name,
            "province_id": address.province_id,
            "city": address.city.name,
            "city_id": address.city_id,
            "district": address.district.name,
            "district_id": address.district_id,
            "place": address.detail_address,
            "mobile": address.mobile,
            "tel": address.phone,
            "email": address.email
        }
        # 响应保存结果
        return http.JsonResponse({"code": RETCODE.OK, "errmsg": "OK", "address": address_dict})

    def delete(self, request, address_id):
        """删除地址"""
        try:
            # 查询要删除的地址
            address = Address.objects.get(id=address_id)
            # address.is_deleted = True
            address.delete()
            # address.save()
        except Exception as e:
            logger.error(e)
            return http.HttpResponseForbidden({'code': RETCODE.DBERR, 'errmsg': '删除地址失败'})

        # 响应删除地址结果
        return http.JsonResponse({"code": RETCODE.OK, "errmsg": "删除地址成功"})


class DefaultAddressView(LoginRequiredMixin):
    """设置默认地址"""
    def put(self, request, address_id):
        # 查询指定id的收货地址
        try:
            address = Address.objects.get(id=address_id)
            user = request.user
            # 把指定的收货地址设置给user的default_address字段
            user.default_address = address
            user.save()
            return http.JsonResponse({"code": RETCODE.OK, "errmsg": "设置默认地址成功"})
        except Address.DoesNotExist:
            return http.JsonResponse({'code': RETCODE.PARAMERR, 'errmsg': '设置默认地址失败'})


class UpdateTitleAddressView(LoginRequiredMixin):
    """设置地址标题"""
    def put(self, request, address_id):
        json_dict = json.loads(request.body.decode())
        title = json_dict.get("title")
        try:
            address = Address.objects.get(id=address_id)
            address.title = title
            address.save()
        except Address.DoesNotExist:
            return http.JsonResponse({'code': RETCODE.PARAMERR, 'errmsg': '设置默认地址标题失败'})

        return http.JsonResponse({"code": RETCODE.OK, "errmsg": "设置默认地址标题成功"})


class ChangePasswordView(LoginRequiredMixin):
    """修改用户登录密码"""
    def get(self, request):
        """提供修改密码界面"""
        return render(request, "user_center_pass.html")

    def post(self, request):
        """获取表单数据"""
        old_password = request.POST.get("old_pwd")
        new_password = request.POST.get("new_pwd")
        new_password2 = request.POST.get("new_cpwd")

        # 校验
        if all([old_password, new_password, new_password2]) is False:
            return http.HttpResponseForbidden('缺少必传参数')
        user = request.user  # 获取当前登录用户
        # 查询旧密码是否正确
        if user.check_password(old_password) is False:
            return render(request, "user_center_pass.html", {'origin_pwd_errmsg': '原密码错误'})
        if not re.match(r'^[0-9A-Za-z]{8,20}$', new_password):
            return http.HttpResponseForbidden('密码最少8位，最长20位')
        if new_password != new_password2:
            return http.HttpResponseForbidden('两次输入的密码不一致')

        # 修改用户的密码 set_password方法
        user.set_password(new_password)
        user.save()
        # 清除状态保持信息
        logout(request)
        # 清除cookie中的username
        response = redirect("/login/")
        response.delete_cookie("username")
        # 重定向到login登录界面
        return response


class UserBrowseHistory(LoginRequiredMixin):
    """商品浏览记录"""

    def post(self, request):
        """保存用户浏览记录"""
        json_dict = json.loads(request.body.decode())
        sku_id = json_dict.get("sku_id")
        # 校验sku_id的真实有效性
        try:
            sku = SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            return http.HttpResponseForbidden("sku_id不存在")

        # 创建redis连接对象
        redis_conn = get_redis_connection("history")
        # 获取当前用户对象
        user = request.user
        # 拼接用户list的key
        key = "history_%s" % user.id

        # # 去重
        # redis_conn.lrem(key, 0, sku_id)
        # # 添加到列表的开头
        # redis_conn.lpush(key, sku_id)
        # # 截取列表中的前五个元素
        # redis_conn.ltrim(key, 0, 4)

        p1 = redis_conn.pipeline()
        # 去重
        p1.lrem(key, 0, sku_id)
        # 添加
        p1.lpush(key, sku_id)
        # 截取列表中的前五个元素
        p1.ltrim(key, 0, 4)
        # 执行管道
        p1.execute()

        return http.JsonResponse({"code": RETCODE.OK, "errmsg": "OK"})

    def get(self, request):
        """查询获取用户商品浏览记录"""
        user = request.user
        # 创建redis连接对象
        redis_conn = get_redis_connection("history")
        # 获取当前用户在redis中的所有浏览记录列表
        sku_ids = redis_conn.lrange("history_%s" % user.id, 0, -1)
        skus = []  # 用来保存sku字典
        # 将通过列表中的sku_id获取到sku模型
        for sku_id in sku_ids:
            sku_model = SKU.objects.get(id=sku_id)
            # 再将sku模型转换成字典
            skus.append({
                'id': sku_model.id,
                'name': sku_model.name,
                'price': sku_model.price,
                'default_image_url': sku_model.default_image.url

            })
        return http.JsonResponse({"code": RETCODE.OK, "errmsg": "OK", "skus": skus})


class FindPasswordView(View):
    """找回密码"""

    def get(self, request):
        """提供找寻密码的界面"""
        return render(request, "find_password.html")


class EnterAccountsView(View):
    """输入用户名"""

    def get(self, request, username):
        """输入用户名"""

        # 提取前端url查询参数传入的image_code, uuid
        image_code = request.GET.get("text")
        uuid = request.GET.get("image_code_id")

        # 校验
        if all([username, image_code, uuid]) is False:
            return http.HttpResponseForbidden("缺少必传参数")
        if not re.match(r'^[a-zA-Z0-9_-]{5,20}$', username):
            return http.HttpResponseForbidden("请输入5-20个字符的用户名")

        # try:
        #     User.objects.get(username=username)
        # except User.DoesNotExist:
        #     return http.HttpResponseForbidden("用户不存在")

        # 通过输入的数据判断用户是否存在，根据用户名或手机号获取user
        user = get_user_by_account(username)

        # 获取redis中的图形验证码
        redis_conn = get_redis_connection("verify_code")
        image_code_server = redis_conn.get("img_%s" % uuid)
        # 2.3 删除redis中图形验证码,让验证码只能用一次
        redis_conn.delete("img_%s" % uuid)
        # 2.4判断redis中存储的图形验证码是否已过期
        if image_code_server is None:
            return http.JsonResponse({'code': RETCODE.IMAGECODEERR, 'errmsg': '图形验证码失效'})

        # 2.5 从redis中取出来的数据都是bytes类型
        image_code_server = image_code_server.decode()

        if image_code.lower() != image_code_server.lower():
            return http.JsonResponse({'code': RETCODE.IMAGECODEERR, 'errmsg': '输入图形验证码有误'})

        access_token = generate_send_sms_code_token(user)

        data = {
            "mobile": user.mobile,
            "access_token": access_token,
        }

        return http.JsonResponse(
            {"code": RETCODE.OK, "errmsg": "ok", "mobile": user.mobile, "access_token": access_token})


class SendSmsCodeView(View):
    """发送短信验证码"""

    def get(self, request):
        # 获取查询参数中的数据
        access_token = request.GET.get("access_token")

        user = check_sms_code_token(access_token)

        if user:

            mobile = user.mobile
            # 创建redis连接对象
            redis_conn = get_redis_connection('verify_code')
            # 0.1 尝试的去redis中获取此手机号有没发送过短信的标记,
            # 如果有,直接响应
            send_flag = redis_conn.get("send_flag_%s" % mobile)

            if send_flag:  # 判断有没有标记
                return http.JsonResponse({'code': RETCODE.THROTTLINGERR, 'errmsg': '频繁发送短信'})

            # 3. 生成一个随机的6位数字, 作为短信验证码
            sms_code = '%06d' % randint(0, 999999)
            logger.info(sms_code)

            # 管道技术
            pl = redis_conn.pipeline()

            # 3.1 把短信验证码存储到redis,以备后期注册时校验
            # redis_conn.setex("sms_%s" % mobile, 60, sms_code)
            pl.setex("sms_%s" % mobile, 300, sms_code)
            # 3.1.2 向redis存储一个此手机号已发送过短信的标记
            # redis_conn.setex('send_flag_%s' % mobile, 60, 1)
            pl.setex('send_flag_%s' % mobile, 60, 1)

            # 执行管道
            pl.execute()

            return http.JsonResponse({"message": "OK"})
        else:
            return http.JsonResponse({"error": "数据错误", "status": 400})


class VerifyMobileView(View):
    """验证手机号"""

    def get(self, request, username):

        # 获取查询参数中的数据sms_code
        sms_code = request.GET.get("sms_code")

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return http.HttpResponseForbidden("用户不存在")

        mobile = user.mobile

        redis_conn = get_redis_connection('verify_code')

        # 2.2 获取redis中的短信验证码
        sms_code_server = redis_conn.get('sms_%s' % mobile)
        # 2.3  删除redis中的短信验证码,让验证码只能用一次
        # sms_code_server.delete('sms_code_%s' % mobile)  <<------->>错误代码
        redis_conn.delete("sms_%s" % mobile)

        # 2.4 校验短信验证码是否过期
        if sms_code_server is None:
            return http.HttpResponseForbidden('短信验证码过期')
        # 2.5 把bytes类型转换成字符串
        sms_code_server = sms_code_server.decode()
        # 2.6 判断前端和后端的短信验证码是否一致
        if sms_code_server != sms_code:
            return http.HttpResponseForbidden('请输入正确的短信验证码')

        access_token = generate_send_sms_code_token(user)

        data = {
            "user_id": user.id,  # 用户id
            "access_token": access_token,  # 用户加密信息
        }

        # return http.JsonResponse({"code": RETCODE.OK, "errmsg": "OK", "data": data})
        return http.JsonResponse({"code": RETCODE.OK, "errmsg": "OK", "user_id": user.id, "access_token": access_token})


class ResetPasswordView(View):
    """重置密码"""

    def post(self, request, user_id):
        # 获取请求表单中的参数
        json_dict = json.loads(request.body.decode())
        password = json_dict.get("password")
        password2 = json_dict.get("password2")
        access_token = json_dict.get("access_token")

        # 校验参数
        if all([password, password2, access_token]) is False:
            return http.HttpResponseForbidden("缺少必传参数")
        if not re.match(r'^[0-9A-Za-z]{8,20}$', password):
            return http.HttpResponseForbidden("请输入8-20位的密码")
        if password != password2:
            return http.HttpResponseForbidden("两次输入的密码不一致")

        user = check_sms_code_token(access_token)

        if user.id == int(user_id):
            # try:
            #     user = User.objects.get(id=user_id)
            # except User.DoesNotExist:
            #     return http.HttpResponseForbidden("用户不存在")

            # user.password = password2  user是个对象，对象属性赋值后，密码并没有真正修改，只是此对象添加了一个同名的属性
            user.set_password(password2)  # 设置密码方法：调用set_password()方法，并save()保存
            user.save()

            return http.JsonResponse({"message": "OK"})
        else:
            # 当前条件不成立时返回的仍然是json数据，而前端代码并没有做判断，直接接收了，导致终端响应的状态码为200（即成功），因此造成成功响应的假象
            return http.JsonResponse({"error": "数据错误", "status": 400}, status=400)

        # if user:
        #     user.password = password
        #     return http.JsonResponse({"message": "OK"})
        # else:
        #     return http.JsonResponse({"error": "数据错误", "status": 400})
