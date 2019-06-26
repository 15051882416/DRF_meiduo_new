from rest_framework.viewsets import ModelViewSet
from django.contrib.auth.models import Group
from rest_framework.response import Response
from rest_framework.decorators import action
from users.models import User
from meiduo_admin.serializers.admin_serializers import *
from meiduo_admin.pagination import MyPagination


class AdminViewSet(ModelViewSet):
    """获取管理员用户列表数据"""

    # 获取用户列表中的管理员用户数据(is_staff=True)
    queryset = User.objects.filter(is_staff=True)
    serializer_class = AdminSerializer
    pagination_class = MyPagination

    # 获取分组表数据
    @action(methods=["get"], detail=False)
    def groups_simple(self, request):

        group = Group.objects.all()
        ser = GroupSimpleSerializer(group, many=True)
        return Response(ser.data)



















