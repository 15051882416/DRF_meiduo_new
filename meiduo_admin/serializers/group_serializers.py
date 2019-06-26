from django.contrib.auth.models import Group, ContentType, Permission
from rest_framework import serializers


class GroupSerializer(serializers.ModelSerializer):
    """用户组列表序列化器"""
    class Meta:
        model = Group
        fields = ["id", "name", "permissions"]


class PermissionSerializer(serializers.ModelSerializer):
    """权限表序列化器"""

    class Meta:
        model = Permission
        fields = ["id", "name"]









