from rest_framework import serializers


from goods.models import *


class SPUSpecModelSerializer(serializers.ModelSerializer):
    """商品SPU规格序列化器"""
    spu = serializers.StringRelatedField()
    spu_id = serializers.IntegerField()

    class Meta:
        model = SPUSpecification
        fields = ["id", "name", "spu", "spu_id"]



























