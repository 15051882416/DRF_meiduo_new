from alipay import AliPay
from django.shortcuts import render
from django import http
from django.conf import settings
import os

from orders.models import OrderInfo
from meiduo_mall.utils.Views import LoginRequiredMixin
from meiduo_mall.utils.response_code import RETCODE
from .models import Payment

# 测试支付的账号：pqcanx4910@sandbox.com ，密码：111111


class PaymentView(LoginRequiredMixin):
    """发起支付"""

    def get(self, request, order_id):

        user = request.user
        # 查询要支付的订单
        try:
            order = OrderInfo.objects.get(order_id=order_id, user=user, status=OrderInfo.ORDER_STATUS_ENUM["UNPAID"])
        except OrderInfo.DoesNotExist:
            return http.HttpResponseForbidden("订单信息错误")

        # 支付宝---支付宝SDK配置参数
        # ALIPAY_APPID = '2016091900551154'
        # ALIPAY_DEBUG = True  # 表示是沙箱环境还是真实支付环境
        # ALIPAY_URL = 'https://openapi.alipaydev.com/gateway.do'
        # ALIPAY_RETURN_URL = 'http://www.meiduo.site:8000/payment/status/'

        # 创建支付宝支付对象
        alipay = AliPay(
            appid=settings.ALIPAY_APPID,
            app_notify_url=None,  # 默认回调url
            app_private_key_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), "keys/app_private_key.pem"),
            # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
            alipay_public_key_path=os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                "keys/alipay_public_key.pem"),
            sign_type="RSA2",  # RSA 或者 RSA2
            debug=settings.ALIPAY_DEBUG  # 默认False
        )

        # 生成登录支付宝连接
        order_string = alipay.api_alipay_trade_page_pay(
            out_trade_no=order_id,  # 生成的订单号
            total_amount=str(order.total_amount),
            subject="美多商城_%s" % order_id,
            return_url=settings.ALIPAY_RETURN_URL,
            # notify_url="https://example.com/notify"  # 可选, 不填则使用默认notify url
        )

        # 真实环境电脑网站支付网关：https://openapi.alipay.com/gateway.do? + order_string
        # 沙箱环境电脑网站支付网关：https://openapi.alipaydev.com/gateway.do? + order_string

        # 拼接支付宝支付界面url
        alipay_url = settings.ALIPAY_URL + "?" + order_string

        return http.JsonResponse({"code": RETCODE.OK, "errmsg": "OK", "alipay_url": alipay_url})


class PaymentStatusView(LoginRequiredMixin):
    """保存订单支付结果"""

    def get(self, request):
        # 获取前端传入的请求查询参数
        query_dict = request.GET
        # 将查询参数数据转换成字典
        data = query_dict.dict()
        # 获取并从请求参数中剔除signature
        signature = data.pop("sign")

        # 创建支付宝支付对象    创建alipay  SDK对象
        alipay = AliPay(
            appid=settings.ALIPAY_APPID,
            app_notify_url=None,
            app_private_key_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), "keys/app_private_key.pem"),
            alipay_public_key_path=os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                "keys/alipay_public_key.pem"),
            sign_type="RSA2",
            debug=settings.ALIPAY_DEBUG
        )

        # 检验这个重定向是否是alipay重定向过来的,调用aliPay中的verify方法
        success = alipay.verify(data, signature)
        if success:
            # 如果校验通过获取到支付宝交易号和美多订单编号
            order_id = data.get("out_trade_no")
            trade_id = data.get("trade_no")

            try:
                # 在保存支付宝交易号和美多订单编号之前，先查询一下是否已经保存
                Payment.objects.get(order_id=order_id, trade_id=trade_id)
            except Payment.DoesNotExist:
                # 将支付宝交易号和美多订单编号保存起来
                Payment.objects.create(
                    order_id=order_id,
                    trade_id=trade_id
                )
            # 修改已支付成功订单的状态
            OrderInfo.objects.filter(order_id=order_id, status=OrderInfo.ORDER_STATUS_ENUM['UNPAID']).update(
                status=OrderInfo.ORDER_STATUS_ENUM['UNCOMMENT'])
            # 响应  渲染支付结果界面
            return render(request, "pay_success.html", {"trade_id": trade_id})
        else:
            # 如果支付结果校验失败,就响应其它
            return http.HttpResponseForbidden('非法请求')
