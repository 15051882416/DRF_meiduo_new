from rest_framework import serializers


from goods.models import *


class GoodsChannelModelSerializer(serializers.ModelSerializer):
    """商品频道序列化器"""
    category = serializers.StringRelatedField()
    category_id = serializers.IntegerField()
    group = serializers.StringRelatedField()
    group_id = serializers.IntegerField()

    class Meta:
        model = GoodsChannel
        fields = "__all__"


class GoodsChannelGroupModelSerializer(serializers.ModelSerializer):
    """商品频道组序列化器"""
    class Meta:
        model = GoodsChannelGroup
        fields = ["id", "name"]


class GoodsCategoryModelSerializer(serializers.ModelSerializer):
    """商品类别序列化器"""
    class Meta:
        model = GoodsCategory
        fields = ["id", "name"]













