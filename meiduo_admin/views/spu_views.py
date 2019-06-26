from rest_framework.generics import *
from goods.models import *
from rest_framework.viewsets import ModelViewSet

from meiduo_admin.serializers.spu_serializers import *
from meiduo_admin.pagination import MyPagination


class SPUView(ModelViewSet):
    """获取和新增SPU表列表数据"""
    queryset = SPU.objects.all()
    serializer_class = SPUModelSerializer
    pagination_class = MyPagination


class BrandSimpleView(ListAPIView):
    """获取品牌信息"""
    queryset = Brand.objects.all()
    serializer_class = BrandModelSerializer


# GET
# goods/channel/categories/
# 处理获得一二三级分类所有数据的接口
class GoodsView(ListAPIView):
    """获取商品级别分类信息"""
    queryset = GoodsCategory
    serializer_class = GoodsCategoryModelSerializer

    def get_queryset(self):

        # pk = self.kwargs["pk"]    # 直接通过列表方式取pk会报KeyError: 'pk'错误
        pk = self.kwargs.get("pk")    # 而通过.get方式取pk，则不会报错
        # pk = self.request.query_params.get("pk")

        if pk:
            # 如果请求路径中有pk： 处理的是二级或三级分类（跟据pk）
            return GoodsCategory.objects.filter(parent_id=pk)
            # return self.queryset.objects.filter(parent_id=pk)
        # 如果请求的路径中没有pk：处理的一级分类数据集
        return GoodsCategory.objects.filter(parent=None)
        # return self.queryset.objects.filter(parent=None)















































