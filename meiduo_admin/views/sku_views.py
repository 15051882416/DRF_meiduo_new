from rest_framework.generics import ListAPIView, CreateAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from meiduo_admin.serializers.sku_serializers import *
from goods.models import *
from meiduo_admin.pagination import MyPagination


# class SKUView(ListAPIView):
#     """获取SKU商品信息"""
#     queryset = SKU.objects.all()
#     serializer_class = SKUModelSerializer
#
#     pagination_class = MyPagination
#
#     # 页面搜索过滤
#     def get_queryset(self):
#         keyword = self.request.query_params.get("keyword")
#         if keyword:
#             return self.queryset.filter(name__contains=keyword)
#         return self.queryset.all()


class SKUView(ModelViewSet):
    """获取SKU商品信息"""
    queryset = SKU.objects.all()

    serializer_class = SKUModelSerializer

    pagination_class = MyPagination

    # 页面搜索过滤
    def get_queryset(self):
        keyword = self.request.query_params.get("keyword")
        if keyword:
            return self.queryset.filter(name__contains=keyword)
        return self.queryset.all()


class GoodsCategoryView(ListAPIView):
    """获取三级分类信息"""
    # 根据数据存储规律parent_id大于37为三级分类信息，查询条件为parent_id__gt=37
    queryset = GoodsCategory.objects.filter(parent_id__gt=37)
    serializer_class = GoodsCategorySerializer


class SPUSimpleView(ListAPIView):
    """获取spu表名称数据"""
    queryset = SPU.objects.all()
    serializer_class = SPUModelSerializer


# class SPUSpecView(ModelViewSet):
class SPUSpecView(ListAPIView):

    """获取SPU商品规格信息"""
    queryset = SPUSpecification.objects.all()
    serializer_class = SPUSpecModelSerializer

    def get_queryset(self):
        spu_id = self.kwargs.get("pk")
        return self.queryset.filter(spu_id=spu_id)














