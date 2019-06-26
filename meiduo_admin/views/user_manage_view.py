from rest_framework.generics import ListAPIView, GenericAPIView, CreateAPIView
from rest_framework.response import Response


from users.models import User
from meiduo_admin.serializers.user_manage_serializers import *
from meiduo_admin.pagination import MyPagination


# GET
# /users/?keyword=<搜索内容>&page=<页码>&pagesize=<页容量>

# class UserManageView(GenericAPIView):
#
#     queryset = User.objects.all()
#     serializer_class = UserManageModleSerializer
#     # 配置自定义分页器
#     pagination_class = MyPagination
#
#     def get(self, request):
#
#         # user_queryset = self.get_queryset().order_by("id")
#         # user_queryset = User.objects.get_queryset().order_by('id')
#
#         # 获得数据集
#         user_queryset = self.get_queryset()
#
#         # 对该数据进行分页处理，并得到一个子集
#         page = self.paginate_queryset(user_queryset)
#
#         # 对该子集进行序列化处理
#         if page:
#             page_serializer = self.get_serializer(page, many=True)
#
#             # 传入分页子集序列化结果，构建最终序列化返回数据格式, 返回的结果是一个响应对象
#             return self.get_paginated_response(page_serializer.data)
#
#         # 如果分页失败，就当不分页，默认返回所有数据
#         serializer = self.get_serializer(user_queryset, many=True)
#         return Response(serializer.data)

        # return Response({"lists": serializer.data})


class UserManageView(ListAPIView, CreateAPIView):

    queryset = User.objects.all()
    serializer_class = UserManageModleSerializer
    # 配置自定义分页器
    pagination_class = MyPagination

    # 重写get_queryset方法，根据前端是否传入keyword值返回不同的查询结果
    def get_queryset(self):
        keyword = self.request.query_params.get("keyword")

        if keyword:
            # 如果有的话，需要根据keyword过滤，返回过滤后的数据集
            return self.queryset.filter(username__contains=keyword)
        # 如果没有的话，默认返回self.queryset.all()
        return self.queryset.all()  # all() 目的在于使用缓存





































