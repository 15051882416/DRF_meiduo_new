from rest_framework import serializers
from fdfs_client.client import Fdfs_client
from goods.models import SKUImage, SKU
from meiduo_mall.settings import dev


class SKUImageModelSerializer(serializers.ModelSerializer):
    """SKU图片表序列化器"""

    class Meta:
        model = SKUImage
        fields = "__all__"

    # 重写create方法，完成图片的上传和保存
    def create(self, validated_data):

        # 获取有效数据中的Image图片文件
        # image = validated_data.get("image")
        image = validated_data.pop("image")

        # 创建Fastdfs连接对象
        # client = Fdfs_client("meiduo_mall/utils/fastdfs/client.conf")
        client = Fdfs_client(dev.FDFS_CONF_PATH)

        # 上传Image图片文件
        result = client.upload_by_buffer(image.read())

        # 判断Image图片文件是否定上传成功
        if result["Status"] != "Upload successed.":
            raise serializers.ValidationError("图片上传失败，请重新尝试")

        # 如果上传成功，就获取图片文件上传后的路径（唯一标识）
        image_url = result["Remote file_id"]

        validated_data["image"] = image_url
        # 保存新建的数据

        # SKUImage.objects.create(**validated_data)
        # return validated_data

        return super().create(validated_data)

    # 重写update方法，完成商品图片信息的更新
    def update(self, instance, validated_data):

        # 获取有效数据中的Image图片文件
        # image = validated_data.get("image")
        image = validated_data.pop("image")

        # 创建Fastdfs连接对象
        # client = Fdfs_client("meiduo_mall/utils/fastdfs/client.conf")
        client = Fdfs_client(dev.FDFS_CONF_PATH)
        # 上传Image图片文件
        result = client.upload_by_buffer(image.read())

        # 判断Image图片文件是否定上传成功
        if result["Status"] != "Upload successed.":
            raise serializers.ValidationError("图片上传失败，请重新尝试")

        # 如果上传成功，就获取图片文件上传后的路径（唯一标识）
        image_url = result["Remote file_id"]

        validated_data["image"] = image_url

        return super().update(instance, validated_data)


class SKUSimpleModelSerializer(serializers.ModelSerializer):
    """获取商品SKU表id、name信息"""

    class Meta:
        model = SKU
        fields = ["id", "name"]















