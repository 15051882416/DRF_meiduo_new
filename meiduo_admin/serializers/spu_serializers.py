from rest_framework import serializers
from goods.models import *


class SPUModelSerializer(serializers.ModelSerializer):
    """商品SPU序列化器"""
    brand = serializers.StringRelatedField()
    brand_id = serializers.IntegerField()
    category1_id = serializers.IntegerField()
    category2_id = serializers.IntegerField()
    category3_id = serializers.IntegerField()

    class Meta:
        model = SPU
        # fields = "__all__"
        # 新增加SPU时，在前端请求时会报Bad Request，这是因为模型类在序列化时将所有的字段都序列化了，
        # 而在校验返回数据时，category1，category2，category3，前端并不需要
        exclude = ["category1", "category2", "category3"]


class BrandModelSerializer(serializers.ModelSerializer):
    """品牌信息序列化器"""
    class Meta:
        model = Brand
        fields = ["id", "name"]


class GoodsCategoryModelSerializer(serializers.ModelSerializer):
    """商品级别分类信息"""
    class Meta:
        model = GoodsCategory
        fields = ["id", "name"]
















































