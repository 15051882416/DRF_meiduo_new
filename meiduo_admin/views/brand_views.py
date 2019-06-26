from rest_framework.generics import *
from rest_framework.viewsets import ModelViewSet
from goods.models import Brand
from meiduo_admin.serializers.brand_serializers import *
from meiduo_admin.pagination import MyPagination

from fdfs_client.client import Fdfs_client
from rest_framework.response import Response


class BrandView(ModelViewSet):
    """获取品牌信息"""
    queryset = Brand.objects.all()
    serializer_class = BrandModelSerializer
    pagination_class = MyPagination

    # # 重写create业务逻辑方法, 完成品牌信息的新增和保存
    # def create(self, request, *args, **kwargs):
    #
    #     # 创建FastDFS客户端连接对象
    #     client = Fdfs_client("meiduo_mall/utils/fastdfs/client.conf")
    #
    #     # 获取前端传入的Logo图片数据
    #     logo = request.FILES.get('logo')
    #     # 上传图片到fastDFS
    #     res = client.upload_by_buffer(logo.read())
    #
    #     # 判断Logo图片是否上传成功
    #     if res['Status'] != 'Upload successed.':
    #         return Response({"errormsg": "图片失败，请重新上传"}, status=403)
    #
    #     # 获取上传后的Logo图片路径
    #     logo_url = res['Remote file_id']
    #
    #     # 获取前端传入的其他数据name,first_letter
    #     name = request.data.get('name')
    #     first_letter = request.data.get("first_letter")
    #
    #     # 保存要新增的品牌信息
    #     Brand.objects.create(name=name, logo=logo_url, first_letter=first_letter)
    #     # 返回新增的品牌信息数据结果
    #     return Response(
    #         {
    #             'name': name,
    #             'logo': logo_url,
    #             'first_letter': first_letter
    #         },
    #         status=201  # 前端需要接受201状态
    #     )
    #
    # # 重写update方法，完成品牌信息的更新
    # def update(self, request, *args, **kwargs):
    #
    #     # 创建FastDFS客户端连接对象
    #     client = Fdfs_client("meiduo_mall/utils/fastdfs/client.conf")
    #
    #     # 获取前端传入的Logo图片数据
    #     logo = request.FILES.get('logo')
    #     # 上传图片到fastDFS
    #     res = client.upload_by_buffer(logo.read())
    #
    #     # 判断Logo图片是否上传成功
    #     if res['Status'] != 'Upload successed.':
    #
    #         return Response({"errormsg": "图片失败，请重新上传"}, status=403)
    #
    #     # 获取上传后的Logo图片路径
    #     logo_url = res['Remote file_id']
    #
    #     # 获取前端传入的其他数据：name,first_letter
    #     name = request.data.get('name')
    #     first_letter = request.data.get("first_letter")
    #
    #     # 获取要进行更新的品牌信息数据对象
    #     brand = Brand.objects.get(id=kwargs["pk"])
    #     # 保存要更新的品牌信息
    #     brand.name = name
    #     brand.first_letter = first_letter
    #     brand.logo = logo_url
    #     brand.save()
    #
    #     # 返回新增的品牌信息数据结果
    #     return Response(
    #         {
    #             'name': name,
    #             'logo': logo_url,
    #             'first_letter': first_letter
    #         },
    #         status=201  # 前端需要接受201状态
    #     )














