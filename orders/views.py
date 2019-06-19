from decimal import Decimal
import json
from django.utils import timezone
from django.db import transaction

from django.core.paginator import Paginator, EmptyPage
from django import http
from django.shortcuts import render
from django_redis import get_redis_connection

from meiduo_mall.utils.Views import LoginRequiredMixin
from users.models import Address
from goods.models import SKU
from .models import OrderInfo, OrderGoods
from meiduo_mall.utils.response_code import RETCODE


class OrderSettlementView(LoginRequiredMixin):
    """结算订单界面逻辑"""

    def get(self, request):
        # 获取到当前登录用户
        user = request.user
        #  查询数据(登录用户的收货地址,展示购物车中勾选商品的一些数据)
        addresses = Address.objects.filter(user=user, is_delete=False)
        #  判断是否查询到用户收货,没有 设置变量为None
        addresses = addresses if addresses.exists() else None

        # 创建redis连接对象，获取redis中的数据
        redis_conn = get_redis_connection("carts")
        redis_dict = redis_conn.hgetall("carts_%s" % user.id)
        sku_id_selected = redis_conn.smembers("selected_%s" % user.id)
        cart_dict = {}  # 准备一个字典用来包装勾选到的商品id和count
        # 遍历sku_id_selected以获取到勾选到的商品和count
        for sku_id_bytes in sku_id_selected:
            cart_dict[int(sku_id_bytes)] = int(redis_dict[sku_id_bytes])

        # 获取勾选商品的sku模型
        skus = SKU.objects.filter(id__in=cart_dict.keys())
        total_count = 0  # 统计商品总数量
        total_amount = Decimal("0.00")
        # 遍历sku查询集给sku模型多定义count和小计数据
        for sku in skus:
            # 给sku模型多定义count属性记录数量和amount属性记录商品总价
            sku.count = cart_dict[sku.id]
            sku.amount = sku.count * sku.price

            # 累加商品总量
            total_count += sku.count
            # 累加商品小计得到商品总价
            total_amount += sku.amount
        # 运费
        freight = Decimal("10.00")

        # 构造模板需要渲染的数据
        context = {
            'addresses': addresses,  # 用户收货地址
            'skus': skus,  # 勾选商品的sku查询集
            'total_count': total_count,  # 总数量
            'total_amount': total_amount,  # 商品总价
            'freight': freight,  # 运费
            'payment_amount': total_amount + freight  # 总金额
        }
        return render(request, "place_order.html", context)


# class OrderCommitView(LoginRequiredMixin):
#     """订单提交"""
#
#     def post(self, request):
#         """保存订单信息和订单商品信息"""
#         # 接收请求数据参数
#         json_dict = json.loads(request.body.decode())
#         address_id = json_dict.get("address_id")
#         pay_method = json_dict.get("pay_method")
#
#         # 校验参数
#         if all([address_id, pay_method]) is False:
#             return http.HttpResponseForbidden("缺少必传参数")
#         try:
#             address = Address.objects.get(id=address_id)
#         except Address.DoesNotExist:
#             return http.HttpResponseForbidden("address_id有误")
#         if pay_method not in [OrderInfo.PAY_METHODS_ENUM["CASH"], OrderInfo.PAY_METHODS_ENUM["ALIPAY"]]:
#             return http.HttpResponseForbidden("支付方式不正确")
#         user = request.user
#         # 生成订单编号：获取当前时间 + user.id
#         order_id = timezone.now().strftime("%Y%m%d%H%M%S") + ("%09d" % user.id)
#
#         # 订单状态
#         status = (OrderInfo.ORDER_STATUS_ENUM['UNPAID']
#                   if pay_method == OrderInfo.PAY_METHODS_ENUM['ALIPAY']
#                   else OrderInfo.ORDER_STATUS_ENUM['UNSEND'])
#
#         # 保存订单记录信息
#         order = OrderInfo.objects.create(
#             order_id=order_id,
#             user=user,
#             address=address,
#             total_count=0,
#             total_amount=Decimal(0.00),
#             freight=Decimal('10.00'),
#             pay_method=pay_method,
#             status=status
#         )
#
#         # 二, 修改sku的库存和销量
#         # 创建redis连接对象，获取数据
#         redis_conn = get_redis_connection("carts")
#         redis_cart = redis_conn.hgetall("carts_%s" % user.id)
#         selected = redis_conn.smembers("selected_%s" % user.id)
#         cart_dict = {}  # 准备一个字典用来包装勾选到的商品id和count
#         for sku_id_bytes in selected:
#             redis_cart[int(sku_id_bytes)] = int(redis_cart[sku_id_bytes])
#         # 遍历购物车中被勾选的商品信息
#         for sku_id in cart_dict.keys():
#             # 得到sku模型
#             sku = SKU.objects.get(id=sku_id)
#             buy_count = redis_cart[sku.id]  # 购买的数量
#             origin_stock = sku.stock  # 原有库存
#             origin_sales = sku.sales  # 原有销量
#             # 判断SKU库存
#             if buy_count > origin_stock:
#                 # 如果库存不足,提前响应
#                 return http.JsonResponse({'code': RETCODE.STOCKERR, 'errmsg': '库存不足'})
#             # SKU减少库存量,增加销量
#             new_stock = origin_stock - buy_count
#             new_sales = origin_sales + buy_count
#
#             sku.stock = new_stock
#             sku.sales = new_sales
#             sku.save()
#
#             # 三, 修改spu的销量
#             sku.spu.sales += buy_count
#             sku.spu.save()
#
#             # 四, 保存订单中的商品记录
#             OrderGoods.objects.create(
#                 order=order,
#                 sku=sku,
#                 count=buy_count,
#                 price=sku.price,
#             )
#             # 累加商品总数量和总价
#             order.total_count += buy_count
#             order.total_amount += (sku.price * buy_count)
#         # 累加运费
#         order.total_amount += order.freight
#         order.save()
#
#         # 删除已结算的购物车数据
#         pl = redis_conn.pipeline()
#         pl.hdel("carts_%s" % user.id, *selected)
#         pl.delete("selected_%s" % user.id)
#         pl.execute()
#
#         return http.JsonResponse({"code": RETCODE.OK, "errmsg": "下单成功", "order_id": order_id})


class OrderCommitView(LoginRequiredMixin):
    """订单提交"""

    def post(self, request):
        """保存订单信息和订单商品信息"""

        # 四张表的数据操作看作一个事务，要么一起成功,要么一起失败

        # 接收请求数据参数
        json_dict = json.loads(request.body.decode())
        address_id = json_dict.get("address_id")
        pay_method = json_dict.get("pay_method")

        # 校验参数
        if all([address_id, pay_method]) is False:
            return http.HttpResponseForbidden("缺少必传参数")
        try:
            address = Address.objects.get(id=address_id)
        except Address.DoesNotExist:
            return http.HttpResponseForbidden("address_id有误")
        if pay_method not in [OrderInfo.PAY_METHODS_ENUM["CASH"], OrderInfo.PAY_METHODS_ENUM["ALIPAY"]]:
            return http.HttpResponseForbidden("支付方式不正确")
        user = request.user
        # 生成订单编号：获取当前时间 + user.id
        order_id = timezone.now().strftime("%Y%m%d%H%M%S") + ("%09d" % user.id)

        # 订单状态
        status = (OrderInfo.ORDER_STATUS_ENUM['UNPAID']
                  if pay_method == OrderInfo.PAY_METHODS_ENUM['ALIPAY']
                  else OrderInfo.ORDER_STATUS_ENUM['UNSEND'])

        # 手动开启事务
        with transaction.atomic():
            # 创建事务的保存点
            save_point = transaction.savepoint()

            try:
                # 保存订单记录信息
                order = OrderInfo.objects.create(
                    order_id=order_id,
                    user=user,
                    address=address,
                    total_count=0,
                    total_amount=Decimal('0.00'),
                    freight=Decimal('10.00'),
                    pay_method=pay_method,
                    status=status
                )

                # 二, 修改sku的库存和销量
                # 创建redis连接对象，获取数据
                redis_conn = get_redis_connection("carts")
                redis_cart = redis_conn.hgetall("carts_%s" % user.id)
                selected = redis_conn.smembers("selected_%s" % user.id)
                cart_dict = {}  # 准备一个字典用来包装勾选到的商品id和count
                for sku_id_bytes in selected:
                    cart_dict[int(sku_id_bytes)] = int(redis_cart[sku_id_bytes])

                # 遍历购物车中被勾选的商品信息
                for sku_id in cart_dict.keys():
                    while True:
                        # 得到sku模型,一次只查询出一个sku模型
                        sku = SKU.objects.get(id=sku_id)
                        buy_count = cart_dict[sku.id]  # 购买的数量
                        origin_stock = sku.stock  # 原有库存
                        origin_sales = sku.sales  # 原有销量
                        # 判断SKU库存
                        if buy_count > origin_stock:
                            # 库存不足就回滚
                            transaction.savepoint_rollback(save_point)

                            # 如果库存不足,提前响应
                            return http.JsonResponse({'code': RETCODE.STOCKERR, 'errmsg': '库存不足'})

                        # SKU减少库存量,增加销量
                        new_stock = origin_stock - buy_count
                        new_sales = origin_sales + buy_count
                        # 修改sku模型库存和销量
                        # sku.stock = new_stock
                        # sku.sales = new_sales
                        # sku.save()

                        result = SKU.objects.filter(id=sku_id, stock=origin_stock).update(stock=new_stock,
                                                                                          sales=new_sales)
                        if result == 0:
                            continue

                        # 三, 修改spu的销量
                        sku.spu.sales += buy_count
                        sku.spu.save()

                        # 四, 保存订单中的商品记录
                        OrderGoods.objects.create(
                            order=order,
                            sku=sku,
                            count=buy_count,
                            price=sku.price,
                        )

                        # 累加商品总数量和总价
                        order.total_count += buy_count
                        order.total_amount += (sku.price * buy_count)

                        break  # 当前商品下单成功,继续买下一个
                # 累加运费
                order.total_amount += order.freight
                order.save()
            except Exception:
                # 暴力回滚
                transaction.savepoint_rollback(save_point)
                return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '下单失败'})
            else:
                # 提交事务
                transaction.savepoint_commit(save_point)

        # 删除已结算的购物车数据
        pl = redis_conn.pipeline()
        pl.hdel("carts_%s" % user.id, *selected)
        pl.delete("selected_%s" % user.id)
        pl.execute()

        return http.JsonResponse({"code": RETCODE.OK, "errmsg": "下单成功", "order_id": order_id})


class OrderSuccessView(LoginRequiredMixin):
    """订单提交成功"""

    def get(self, request):
        # 获取查询字符串参数
        order_id = request.GET.get("order_id")
        payment_amount = request.GET.get("payment_amount")
        pay_method = request.GET.get("pay_method")
        # 校验
        try:
            OrderInfo.objects.get(order_id=order_id, total_amount=payment_amount, pay_method=pay_method)
        except OrderInfo.DoesNotExist:
            return http.HttpResponseForbidden("订单有误")
        # 要进行渲染的数据
        context = {
            "order_id": order_id,
            "payment_amount": payment_amount,
            "pay_method": pay_method

        }
        return render(request, "order_success.html", context)


class UserAllOrdersView(LoginRequiredMixin):
    """用户订单展示"""

    def get(self, request, current):
        # 获取当前登录的用户
        user = request.user

        try:
            # 获取当前用户下的所有订单的查询集
            order_qs = OrderInfo.objects.filter(user=user)
        except OrderInfo.DoesNotExist:
            return http.HttpResponseForbidden("订单不存在")

        # 准备一个空列表来包装所有的订单
        page_orders = []
        # 遍历订单的查询集得到每一个订单
        for order in order_qs:
            # 通过订单id查询过滤得到订单商品信息的查询集
            order_goods_qs = OrderGoods.objects.filter(order_id=order.order_id)

            # 准备一个空字典用来包装每个订单下所有的sku
            order.sku_list = []

            # 定义一个变量用来记录商品的总价
            order.total_amount = Decimal("0.00")
            # 遍历订单商品信息的查询集得到每一个订单商品信息
            for order_goods in order_goods_qs:
                # 通过每一个订单商品中的sku_id得到每一个sku
                sku = SKU.objects.get(id=order_goods.sku_id)

                # 给sku模型多定义amount属性记录商品总价
                sku.count = order_goods.count
                sku.amount = sku.count * sku.price

                order.sku_list.append(sku)

                # 累加商品小计得到商品总价
                order.total_amount += sku.amount + order.freight
                # order.total_amount += order.freight

            # 给OrderInfo模型多定义pay_method_name和status_name属性记录订单的支付方式名称和支付状态名称
            order.pay_method_name = OrderInfo.PAY_METHOD_CHOICES[order.pay_method - 1][1]
            order.status_name = OrderInfo.ORDER_STATUS_CHOICES[order.status - 1][1]

            # 将每一个订单追加到空的订单列表中
            page_orders.append(order)

        # 创建分页对象paginator（要分页的所有数据， 每页显示多少个数据）
        paginator = Paginator(page_orders, 3)
        try:
            # 获取当前页的数据
            page_skus = paginator.page(current)
        except EmptyPage:
            return http.HttpResponseForbidden('当前页不存在')

        # 获取总页数据
        total_page = paginator.num_pages

        # 准备要进行渲染的数据
        context = {

            # "page_orders": page_orders, # 未分页时展示的所有数据
            "page_orders": page_skus,  # 分页后展示的每页数据
            "page_num": current,  # 当前页码
            "total_page": total_page  # 总页数
        }

        return render(request, "user_center_order.html", context)


class OrderWaitCommentView(LoginRequiredMixin):
    """订单待评价页面"""

    def get(self, request):

        order_id = request.GET.get("order_id")
        try:
            order_goods = OrderGoods.objects.get(order_id=order_id)
        except OrderInfo.DoesNotExist:
            return http.HttpResponseForbidden("订单不存在")

        return render(request, "goods_judge.html")
