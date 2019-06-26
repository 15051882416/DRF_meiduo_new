from rest_framework import serializers
from goods.models import GoodsVisitCount


class GoodsVisitSerializer(serializers.ModelSerializer):

    # 指明这个外键在序列化后是以字符串的形式展示（默认是以主表主键的形式展示）
    category = serializers.StringRelatedField(read_only=True)

    class Meta:
        # 指明基于哪个模型类的序列化
        model = GoodsVisitCount
        # 指明要进行映射并序列化的字段
        fields = ("category", "count")














