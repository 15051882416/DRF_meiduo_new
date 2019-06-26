from rest_framework.generics import *
from rest_framework.viewsets import ModelViewSet


from goods.models import *
from meiduo_admin.serializers.Specification_serializers import *
from meiduo_admin.pagination import MyPagination


# class SPUSpecView(ListAPIView):
#     queryset = SPUSpecification.objects.all()
#     serializer_class = SPUSpecModelSerializer
#     pagination_class = MyPagination


class SPUSpecificationView(ModelViewSet):
    """商品SPU规格表管理"""
    queryset = SPUSpecification.objects.all()
    serializer_class = SPUSpecModelSerializer
    pagination_class = MyPagination

















