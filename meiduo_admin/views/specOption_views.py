from rest_framework.generics import *
from rest_framework.viewsets import ModelViewSet


from goods.models import *
from meiduo_admin.serializers.specOption_serializers import *
from meiduo_admin.pagination import MyPagination


class SpecOptionView(ModelViewSet):
    """获取规格选项表列表数据"""
    queryset = SpecificationOption.objects.all()
    serializer_class = SpecOptionModelSerializer
    pagination_class = MyPagination


class GetSPUSpecView(ListAPIView):
    """获取商品SPU规格数据"""
    queryset = SPUSpecification.objects.all()
    serializer_class = GetSPUSpecModelSerializer






















