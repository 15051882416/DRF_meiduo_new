from django.contrib.auth.models import Permission, ContentType
from rest_framework import serializers


class PermissionModelSerializer(serializers.ModelSerializer):
    """用户权限列表序列化器"""

    class Meta:

        model = Permission
        fields = "__all__"


class ContentTypeModelSerializer(serializers.ModelSerializer):
    """权限类型列表数据"""

    class Meta:
        model = ContentType
        fields = ["id", "name"]

















