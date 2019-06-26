from rest_framework import serializers


from goods.models import *


# 关联嵌套序列化

class SKUSpecificationModelSerializer(serializers.ModelSerializer):
    """SKU具体规格序列化器"""

    spec_id = serializers.IntegerField()
    option_id = serializers.IntegerField()

    class Meta:
        model = SKUSpecification  # SKUSpecification中sku外键关联了SKU表
        fields = ("spec_id", 'option_id')


class SKUModelSerializer(serializers.ModelSerializer):
    """获取sku表信息的序列化器"""

    # 关联嵌套返回
    category = serializers.StringRelatedField()
    # 指定分类信息
    category_id = serializers.IntegerField()
    # 关联嵌套返回
    spu = serializers.StringRelatedField()
    # 指定所关联的spu表信息
    spu_id = serializers.IntegerField()

    # 指定所关联的选项信息-----关联嵌套返回
    # specs代表的是与sku对象关联的所有的从表数据对象SKUSpecification
    specs = SKUSpecificationModelSerializer(many=True)

    class Meta:
        model = SKU  # SKU表中category外键关联了GoodsCategory分类表。spu外键关联了SPU商品表
        fields = '__all__'

    def create(self, validated_data):
        # 目的：创建中间表(SKUSpecification对应的表)数据（从表），主表数据首先必须得有
        spec_option = validated_data.pop("specs")

        # 获得规格及规格选项数据validated_data['specs']
        # [
        #    {spec_id:1,  option_id:10},
        #    {....}
        # ]

        # 新建sku对象
        sku = super().create(validated_data)
        # [
        #   {sku_id: 6, spec_id:1,  option_id:10},
        #   {...}
        # ]

        # 根据spec_option创建中间表数据
        for temp in spec_option:
            # temp: {spec_id:1,  option_id:10}
            temp["sku_id"] = sku.id
            SKUSpecification.objects.create(**temp)

        return sku

    # super().create(validated_data)是ModelSerializer提供的create方法
    # 问题是： 该方法没有能够帮助我们创建中间表数据，意味着规格选项信息丢失
    # return super().create(validated_data)

    def update(self, instance, validated_data):
        """ 更新sku对象的时候，顺带着更新中间表数据"""

        # 1、获得规格及规格选项数据
        spec_option = validated_data.pop('specs')
        # 2、根据这些数据，更新中间表
        for temp in spec_option:
            # temp: {spec_id:4,  option_id:9}
            # 2.1 找到对应的中间表数据：当前更新的sku对象，对应的规格及规格选项
            skuspec = SKUSpecification.objects.get(sku_id=instance.id, spec_id=temp['spec_id'])
            skuspec.option_id = temp['option_id']
            skuspec.save()

        # ModelSerializer提供的update方法无法更新中间表数据
        return super().update(instance, validated_data)















class GoodsCategorySerializer(serializers.ModelSerializer):
    """商品分类序列化器"""
    class Meta:
        model = GoodsCategory
        fields = ["id", "name"]


class SPUModelSerializer(serializers.ModelSerializer):
    """商品SPU表序列化器"""
    class Meta:
        model = SPU
        fields = ["id", "name"]


class SpecOptionModelSerializer(serializers.ModelSerializer):
    """规格选项序列化器"""
    class Meta:
        model = SpecificationOption
        fields = ["id", "value"]


class SPUSpecModelSerializer(serializers.ModelSerializer):
    """SPU商品规格信息序列化器"""
    spu = serializers.StringRelatedField()
    spu_id = serializers.IntegerField()

    options = SpecOptionModelSerializer(many=True)

    class Meta:
        model = SPUSpecification
        fields = ["id", "name", "spu", "spu_id", "options"]

