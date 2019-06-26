from rest_framework.viewsets import ModelViewSet
from django.contrib.auth.models import Group, ContentType, Permission
from rest_framework.decorators import action
from rest_framework.response import Response
from meiduo_admin.serializers.group_serializers import *
from meiduo_admin.pagination import MyPagination


class GroupViewSet(ModelViewSet):
    """获取用户组列表数据"""

    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    pagination_class = MyPagination


    # GET
    # /meiduo_admin/permission/simple/

    # 获取权限表数据
    @action(methods=["get"], detail=False)
    def simple(self, request):
        perm = Permission.objects.all()
        ser = PermissionSerializer(perm, many=True)

        return Response(ser.data)








