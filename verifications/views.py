from random import randint

from django import http

# Create your views here.
from django.views import View
from django_redis import get_redis_connection

from meiduo_mall.libs.captcha.captcha import captcha
from meiduo_mall.utils.response_code import RETCODE
from celery_tasks.sms.yuntongxun.sms import CCP
from celery_tasks.sms.tasks import send_sms_code
from . import constants

import logging


logger = logging.getLogger('django')


class ImageCodeView(View):
    """图形验证码"""
    def get(self, request, uuid):
        name, text, image = captcha.generate_captcha()
        # 2.将图形验证码的文字存储到redis
        # 创建redis连接对象
        redis_conn = get_redis_connection('verify_code')
        # setex(key,过期时间单位秒, 值)
        redis_conn.setex('img_%s' % uuid, 300, text)

        # 3. 响应图片内容给前端
        return http.HttpResponse(image, content_type='image/png')


# class SMSCodeView(View):
#
#     def get(self, request, mobile):
#         # 1. 提取前端url查询参数传入的image_code, uuid
#         image_code = request.GET.get("image_code")
#         uuid = request.GET.get("uuid")
#          # 2. 校验 all()
#         if all([image_code, uuid]) is False:
#             return http.HttpResponseForbidden('缺少必传参数')
#          # 2.2 获取redis中的图形验证码
#         redis_conn = get_redis_connection('verify_code')
#         image_code_server = redis_conn.get("img_%s" % uuid)
#         # 2.3 删除redis中图形验证码,让验证码只能用一次
#         redis_conn.delete("img_%s" % uuid)
#         # 2.4判断redis中存储的图形验证码是否已过期
#         if image_code_server is None:
#
#             return http.JsonResponse({'code': RETCODE.IMAGECODEERR, 'errmsg': '图形验证码失效'})
#         # 2.5 从redis中取出来的数据都是bytes类型
#         image_code_server = image_code_server.decode()
#
#         if image_code.lower() != image_code_server.lower():
#             return http.JsonResponse({'code': RETCODE.IMAGECODEERR, 'errmsg': '输入图形验证码有误'})
#          # 3. 生成一个随机的6位数字, 作为短信验证码
#         sms_code = '%06d' % randint(0, 999999)
#         logger.info(sms_code)
#         # 3.1 把短信验证码存储到redis,以备后期注册时校验
#         redis_conn.setex("sms_%s" % mobile, 60, sms_code)
#           # 3.2 发短信 容联云通讯
#         CCP().send_template_sms(mobile, [sms_code, 300//60], 1)
#           # 4. 响应
#         return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '发送短信成功'})


class SMSCodeView(View):
    """短信验证码"""

    def get(self, request, mobile):

        # 0 创建redis连接对象
        redis_conn = get_redis_connection('verify_code')
        # 0.1 尝试的去redis中获取此手机号有没发送过短信的标记,
        # 如果有,直接响应
        send_flag = redis_conn.get("send_flag_%s" % mobile)

        if send_flag:   # 判断有没有标记
            return http.JsonResponse({'code': RETCODE.THROTTLINGERR, 'errmsg': '频繁发送短信'})



        # 1. 提取前端url查询参数传入的image_code, uuid
        image_code = request.GET.get("image_code")
        uuid = request.GET.get("uuid")


         # 2. 校验 all()
        if all([image_code, uuid]) is False:
            return http.HttpResponseForbidden('缺少必传参数')


         # 2.2 获取redis中的图形验证码

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



        # 3.2 发短信 容联云通讯
        # CCP().send_template_sms(mobile, [sms_code, constants.SMS_CODE_REDIS_EXPIRES//60], 1)
        # 生产任务,把任务外包给celery
        # send_sms_code.delay(mobile, sms_code)

          # 4. 响应
        # return http.JsonResponse({'count': RETCODE.OK, 'errmsg': '发送短信成功'})
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': "发送短信成功"})