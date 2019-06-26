from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from orders.models import *
from meiduo_admin.pagination import MyPagination
from meiduo_admin.serializers.orders_serializers import *
from rest_framework.response import Response


class OrderInfoViewSet(ModelViewSet):
    """订单信息列表数据操作"""

    queryset = OrderInfo.objects.all()
    serializer_class = OrderInfoModelSerializer
    pagination_class = MyPagination

    lookup_field = 'order_id'

    # # 定义一个函数用来修改订单的状态
    # @action(methods=["put"], detail=True)
    # def status(self, request, order_id):
    #
    #     # 获取当前要修改的订单
    #     order = self.get_object()
    #     # 获取要修改的状态
    #     status = request.data.get("status")
    #
    #     # 修改订单状态
    #     order.status = status
    #     order.save()
    #
    #     self.get_serializer(order)
    #
    #     return Response({
    #         "order_id": order.order_id,
    #         "status": status
    #     })

    # 重写get_queryset方法，利用keyword过滤搜索

    def get_queryset(self):

        # 获取前端传入的keyword
        keyword = self.request.query_params.get("keyword")

        # 判断keyword是否传入
        if keyword:
            return self.queryset.filter(order_id__contains=keyword)

        # 如果keyword没有传入，就返回所有数据
        return self.queryset.all()















