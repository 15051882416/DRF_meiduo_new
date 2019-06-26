from rest_framework import serializers
from django.contrib.auth.models import Group
from django.contrib.auth.hashers import make_password
from users.models import User


class AdminSerializer(serializers.ModelSerializer):
    """用户列表序列化器"""

    class Meta:
        model = User
        # fields = ["id", "username", "email", "mobile", "password", "user_permissions", "groups"]
        fields = "__all__"

        extra_kwargs = {
            'password': {'write_only': True}
        }

    # 重写父类create方法，在新建管理员时，增加管理员权限属性，并将密码加密
    def create(self, validated_data):
        validated_data["password"] = make_password(validated_data["password"])
        validated_data["is_staff"] = True

        return super().create(validated_data)

    # 重写父类update方法，在修改更新管理员信息时，更新后信息中传入的密码是明文，因此需要进行密码加密
    def update(self, instance, validated_data):

        validated_data["password"] = make_password(validated_data["password"])

        return super().update(instance, validated_data)

    # # 另一种情况：在更新管理员信息时，判断前端是否填入密码（判断有效数据中是否传入密码）
    # def update(self, instance, validated_data):
    #
    #     password = validated_data.get("password")
    #     # 判断有效数据中是否传入密码
    #     if password:
    #         # 如果传入密码，将密码加密
    #         validated_data["password"] = make_password(password)
    #     else:
    #         # 如果没有没有填入密码（即有效数据中没有传入密码），就使用原有的加密密码
    #         validated_data["password"] = instance.password
    #
    #     return super().update(instance, validated_data)


class GroupSimpleSerializer(serializers.ModelSerializer):
    """用户组列表序列化器"""

    class Meta:
        model = Group
        fields = ["id", "name"]















