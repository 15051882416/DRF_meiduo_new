from rest_framework.generics import *
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response

from fdfs_client.client import Fdfs_client

from goods.models import SKUImage
from meiduo_admin.serializers.sku_image_serializers import *
from meiduo_admin.pagination import MyPagination
from meiduo_mall import settings


class SKUImageView(ModelViewSet):
    """获取SKU图片"""
    queryset = SKUImage.objects.all()
    serializer_class = SKUImageModelSerializer
    pagination_class = MyPagination


    # # 重写create方法，完成图片的上传和保存
    # def create(self, request, *args, **kwargs):
    #
    #     # 创建FastDFS客户端连接对象
    #     client = Fdfs_client("meiduo_mall/utils/fastdfs/client.conf")
    #     # 获取前端传递的image文件
    #     data = request.FILES.get('image')
    #     # 上传图片到fastDFS
    #     res = client.upload_by_buffer(data.read())
    #     # 判断是否上传成功
    #     if res['Status'] != 'Upload successed.':
    #         return Response({"errormsg": "图片上传失败"}, status=403)
    #     # 获取上传后的图片路径
    #     image_url = res['Remote file_id']
    #     # 获取sku_id
    #     sku_id = request.data.get('sku')[0]
    #     # 保存图片
    #     img = SKUImage.objects.create(sku_id=sku_id, image=image_url)
    #     # 返回结果
    #     return Response(
    #         {
    #             'id': img.id,
    #             'sku': sku_id,
    #             'image': image_url
    #         },
    #         status=201  # 前端需要接受201状态
    #     )
    #
    # # 重写update方法，完成商品图片信息的更新
    # def update(self, request, *args, **kwargs):
    #
    #     # 创建FastDFS客户端连接对象
    #     client = Fdfs_client("meiduo_mall/utils/fastdfs/client.conf")
    #     # 获取前端传入的图片文件
    #     image = request.FILES.get("image")
    #     # 将获得的前端传入图片信息文件上传FastDFS
    #     res = client.upload_by_buffer(image.read())
    #
    #     # 判断图片信息文件是否上传成功
    #     if res["Status"] != "Upload successed.":
    #         # 如果图片信息文件没有上传成功，直接响应
    #         return Response({"errormsg": "图片失败，请重新上传"}, status=403)
    #
    #     # 如果图片信息文件上传成功，再执行后续步骤
    #     # 获取图片上传后的路径
    #     image_url = res['Remote file_id']
    #     # 获取前端传入的商品id(sku_id)
    #     sku_id = request.data.get('sku')[0]
    #
    #     # 获取要更新的图片文件数据对象
    #     img = SKUImage.objects.get(id=kwargs["pk"])
    #
    #     # 将新的图片信息保存到要进行更新的图片文件数据对象中
    #     img.image = image_url
    #     img.save()
    #
    #     # 返回更新数据结果
    #     # return Response({"id": img.id, "sku": sku_id, "image": img.image})
    #     return Response(
    #         {
    #             'id': img.id,
    #             'sku': sku_id,
    #             'image': img.image.url
    #         },
    #         status=201  # 前端需要接受201状态码
    #     )


class SKUSimpleView(ListAPIView):
    """获取商品SKU表id、name信息"""
    queryset = SKU.objects.all()
    serializer_class = SKUSimpleModelSerializer














