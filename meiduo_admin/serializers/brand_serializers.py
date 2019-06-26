from rest_framework import serializers
from fdfs_client.client import Fdfs_client
from meiduo_mall.settings import dev
from goods.models import *


class BrandModelSerializer(serializers.ModelSerializer):
    """品牌序列化器"""
    class Meta:
        model = Brand
        fields = "__all__"

    # 重写create业务逻辑方法, 完成品牌信息的新增和保存
    def create(self, validated_data):

        # 获取有效数据中的logo图片文件
        # logo = validated_data.get("logo")
        logo = validated_data.pop("logo")

        # 创建Fastdfs连接对象
        # client = Fdfs_client("meiduo_mall/utils/fastdfs/client.conf")
        client = Fdfs_client(dev.FDFS_CONF_PATH)

        # 上传logo图片文件
        result = client.upload_by_buffer(logo.read())

        # 判断logo图片文件是否定上传成功
        if result["Status"] != "Upload successed.":
            raise serializers.ValidationError("图片上传失败，请重新尝试")

        # 如果上传成功，就获取图片文件上传后的路径（唯一标识）
        logo_url = result["Remote file_id"]

        validated_data["logo"] = logo_url
        # 保存新建的数据

        # Brand.objects.create(**validated_data)
        # return validated_data

        return super().create(validated_data)

    # 重写update方法，完成品牌信息的更新
    def update(self, instance, validated_data):

        # 获取有效数据中的logo图片文件
        # logo = validated_data.get("logo")
        logo = validated_data.pop("logo")

        # 创建Fastdfs连接对象
        # client = Fdfs_client("meiduo_mall/utils/fastdfs/client.conf")
        client = Fdfs_client(dev.FDFS_CONF_PATH)

        # 上传logo图片文件
        result = client.upload_by_buffer(logo.read())

        # 判断logo图片文件是否定上传成功
        if result["Status"] != "Upload successed.":
            raise serializers.ValidationError("图片上传失败，请重新尝试")

        # 如果上传成功，就获取图片文件上传后的路径（唯一标识）
        logo_url = result["Remote file_id"]

        # 保存更新结果
        instance.logo = logo_url
        instance.save()

        # return instance  # 直接返回instance对象是错误的，这并没有完整的更新数据

        # validated_data["logo"] = logo_url
        #
        return super().update(instance, validated_data)
























