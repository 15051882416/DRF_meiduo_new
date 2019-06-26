from django.contrib.auth.models import Permission, ContentType
from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import ListAPIView
from rest_framework.decorators import action
from rest_framework.response import Response

from meiduo_admin.pagination import MyPagination
from meiduo_admin.serializers.permission_serializers import *


class PermissionViewSet(ModelViewSet):
    """获取用户权限列表数据"""

    queryset = Permission.objects.all().order_by("id")
    serializer_class = PermissionModelSerializer
    pagination_class = MyPagination

    # 获取权限类型列表数据
    @action(methods=["get"], detail=False)
    def content_types(self, request):

        content = ContentType.objects.all()
        serializer = ContentTypeModelSerializer(content, many=True)

        return Response(serializer.data)


# class ContentTypeView(ListAPIView):
#     """获取权限类型列表数据"""
#
#     queryset = ContentType.objects.all()
#     serializer_class = ContentTypeModelSerializer












