from rest_framework import serializers

from orders.models import *
from goods.models import *


class SKUModelSerializer(serializers.ModelSerializer):
    """商品SKU列化器"""

    # default_image_url = serializers.ImageField()  # 前端接收商品图片的key为default_image_url（写错了），实为default_image

    class Meta:
        model = SKU
        fields = ["name", "default_image"]


class OrderGoodsModelSerializer(serializers.ModelSerializer):
    """订单商品序列化器"""

    sku = SKUModelSerializer()

    class Meta:
        model = OrderGoods
        fields = ["count", "price", "sku"]


class OrderInfoModelSerializer(serializers.ModelSerializer):
    """订单信息序列化器"""

    user = serializers.StringRelatedField()
    skus = OrderGoodsModelSerializer(many=True)

    class Meta:
        model = OrderInfo
        fields = "__all__"






















