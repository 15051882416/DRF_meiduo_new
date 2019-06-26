from rest_framework import serializers

from goods.models import *


class SpecOptionModelSerializer(serializers.ModelSerializer):
    """规格选项序列化器"""
    spec = serializers.StringRelatedField()
    spec_id = serializers.IntegerField()

    class Meta:
        model = SpecificationOption
        fields = "__all__"


class GetSPUSpecModelSerializer(serializers.ModelSerializer):
    """规商品SPU规格序列化器"""

    class Meta:
        model = SPUSpecification
        fields = ["id", "name"]


























