from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from users.models import User


# 创建一个序列化器，用于序列化User模型类
class UserManageModleSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ["id", "username", "mobile", "email", "password"]
        extra_kwargs = {
            "id": {"read_only": True},
            "password": {"write_only": True}

        }

    # 重写create方法, DRF默认新增用户时，密码为明文，因此需要重写create方法，将密码加密
    def create(self, validated_data):

        # password = validated_data["password"]
        # # 明文密码加密
        # validated_data["password"] = make_password(password)
        # # 并且创建的用户是超级管理员
        # validated_data["is_superuser"] = True
        #
        # return self.Meta.model.objects.create(**validated_data)

        return self.Meta.model.objects.create_superuser(**validated_data)






















