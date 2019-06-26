from rest_framework.generics import *
from rest_framework.viewsets import ModelViewSet


from meiduo_admin.serializers.goods_channel_serializers import *
from goods.models import *
from meiduo_admin.pagination import MyPagination


class GoodsChannelView(ModelViewSet):
    """商品频道信息"""
    queryset = GoodsChannel.objects.all()
    serializer_class = GoodsChannelModelSerializer
    pagination_class = MyPagination


class GoodsChannelGroupView(ListAPIView):
    """获取商品频道组信息"""
    queryset = GoodsChannelGroup.objects.all()
    serializer_class = GoodsChannelGroupModelSerializer


class GetGoodsCategoryView(ListAPIView):
    """获取商品一级分类信息"""
    # queryset = GoodsCategory.objects.filter(parent_id__lte=37)
    queryset = GoodsCategory.objects.filter(parent=None)
    serializer_class = GoodsCategoryModelSerializer


# 还可以在GoodsChannelView(ModelViewSet)视图集中定义两个函数，
# 来分别获得商品频道组信息和商品一级分类信息（注意：使用action动作方式与请求方式进行映射）





